"use client";

/**
 * Состояние авторизации.
 *
 * Токены лежат в `localStorage`, а это внешняя по отношению к React система,
 * поэтому читаются через `useSyncExternalStore`, как тема. Через `useState`
 * с эффектом получился бы каскадный ререндер и расхождение при гидратации.
 *
 * Access-токен живёт 15 минут, поэтому здесь же обновление сессии: при 401
 * делается ровно одна попытка обменять refresh, и только если она не удалась —
 * выход. Без этого пользователя выбрасывало бы каждые четверть часа.
 */

const ACCESS_KEY = "oc-access-token";
const REFRESH_KEY = "oc-refresh-token";
const USER_KEY = "oc-user";

export interface CurrentUser {
  id: number;
  username: string;
  email: string;
  roles: string[];
  points: number;
  coins: number;
  streak_days: number;
  level: string;
}

export interface Session {
  access_token: string;
  refresh_token: string;
  user: CurrentUser;
}

const listeners = new Set<() => void>();

function emit(): void {
  for (const l of listeners) l();
}

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // приватный режим — не повод падать
  }
}

export function getAccessToken(): string | null {
  return read(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  return read(REFRESH_KEY);
}

export function storeSession(session: Session): void {
  write(ACCESS_KEY, session.access_token);
  write(REFRESH_KEY, session.refresh_token);
  write(USER_KEY, JSON.stringify(session.user));
  emit();
}

export function clearSession(): void {
  write(ACCESS_KEY, null);
  write(REFRESH_KEY, null);
  write(USER_KEY, null);
  emit();
}

// --- внешнее хранилище для useSyncExternalStore --------------------------------

export function subscribeAuth(onChange: () => void): () => void {
  listeners.add(onChange);
  // Выход в одной вкладке должен выкидывать и в остальных.
  window.addEventListener("storage", onChange);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener("storage", onChange);
  };
}

let cachedRaw: string | null = null;
let cachedUser: CurrentUser | null = null;

export function getAuthSnapshot(): CurrentUser | null {
  const raw = read(USER_KEY);
  // Снимок обязан быть стабильным по ссылке, иначе useSyncExternalStore
  // уходит в бесконечный ререндер: новый объект на каждый вызов выглядит
  // как изменение состояния.
  if (raw !== cachedRaw) {
    cachedRaw = raw;
    try {
      cachedUser = raw ? (JSON.parse(raw) as CurrentUser) : null;
    } catch {
      cachedUser = null;
    }
  }
  return cachedUser;
}

export function getAuthServerSnapshot(): CurrentUser | null {
  return null;
}

// --- обновление сессии ----------------------------------------------------------

let refreshing: Promise<boolean> | null = null;

/**
 * Обменять refresh на новую пару. Параллельные вызовы разделяют один запрос:
 * иначе несколько одновременных 401 обменяли бы токен несколько раз, а сервер
 * считает повторное использование кражей и обрывает всю сессию.
 */
export async function refreshSession(baseUrl: string): Promise<boolean> {
  if (refreshing) return refreshing;

  const token = getRefreshToken();
  if (!token) return false;

  refreshing = (async () => {
    try {
      const res = await fetch(`${baseUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: token }),
      });
      if (!res.ok) {
        clearSession();
        return false;
      }
      storeSession((await res.json()) as Session);
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();

  return refreshing;
}
