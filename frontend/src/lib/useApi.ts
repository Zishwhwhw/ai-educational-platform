"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, api } from "@/lib/api";

export interface AsyncState<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
  reload: () => void;
}

/**
 * Загрузка данных с четырьмя состояниями вместо одного.
 *
 * Отдельный хук, потому что «данные есть» — лишь одно из состояний экрана,
 * а на всех девяти унаследованных страницах было нарисовано только оно.
 */
export function useApi<T>(path: string | null): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(path !== null);
  const [nonce, setNonce] = useState(0);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    if (path === null) return;
    let cancelled = false;

    api<T>(path)
      .then((d) => {
        if (cancelled) return;
        setData(d);
        setError(null);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof ApiError || e instanceof Error ? e : new Error("Request failed"));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [path, nonce]);

  return { data, error, loading, reload };
}
