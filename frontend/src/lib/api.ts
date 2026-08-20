"use client";

import type { ApiErrorBody } from "@/lib/api-types";
import { clearSession, getAccessToken, refreshSession } from "@/lib/auth";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }

  /** Сбой песочницы или сервера — не вина пользователя, повтор осмыслен. */
  get isRetryable(): boolean {
    return this.code === "execution_unavailable" || this.status >= 500;
  }

  get isUnauthorized(): boolean {
    return this.status === 401;
  }
}

export const API_BASE = BASE;

async function request(path: string, init: RequestInit & { json?: unknown }): Promise<Response> {
  const { json, headers, ...rest } = init;
  const token = getAccessToken();

  return fetch(`${BASE}${path}`, {
    ...rest,
    headers: {
      ...(json !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
}

export async function api<T>(
  path: string,
  init: RequestInit & { json?: unknown; skipRefresh?: boolean } = {},
): Promise<T> {
  const { skipRefresh, ...rest } = init;
  let res = await request(path, rest);

  // Access-токен живёт 15 минут. Одна попытка обменять refresh, и только
  // если она не удалась — считаем сессию законченной. Иначе пользователя
  // выбрасывало бы каждые четверть часа посреди задачи.
  if (res.status === 401 && !skipRefresh && (await refreshSession(BASE))) {
    res = await request(path, rest);
  }

  if (res.status === 204) return undefined as T;

  const body = await res.json().catch(() => null);

  if (!res.ok) {
    const err = (body as ApiErrorBody | null)?.error;
    if (res.status === 401 && !skipRefresh) clearSession();
    throw new ApiError(
      res.status,
      err?.code ?? "unknown",
      err?.message ?? `Request failed with ${res.status}`,
      err?.request_id,
    );
  }
  return body as T;
}
