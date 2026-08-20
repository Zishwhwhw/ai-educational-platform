"use client";

/**
 * Шапка приложения.
 *
 * Все показатели раньше были захардкожены — «450 Pts», «5 Days Streak»,
 * аватар «S» — и не менялись, что бы пользователь ни делал. Теперь они
 * приходят из сессии.
 *
 * Уведомления убраны: раньше это был выпадающий список из двух выдуманных
 * сообщений. Настоящих уведомлений пока нет, а пустой колокольчик обещает
 * функцию, которой не существует.
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSyncExternalStore } from "react";

import ThemeToggle from "@/components/ThemeToggle";
import { API_BASE } from "@/lib/api";
import {
  clearSession,
  getAuthServerSnapshot,
  getAuthSnapshot,
  getRefreshToken,
  subscribeAuth,
} from "@/lib/auth";

function Stat({ icon, value, label }: { icon: string; value: number | string; label: string }) {
  return (
    <div
      title={label}
      className="flex items-center gap-1.5 rounded-lg border border-border bg-raised px-2.5 py-1.5 text-xs font-semibold text-text-2"
    >
      <span aria-hidden="true">{icon}</span>
      <span className="text-text">{value}</span>
      <span className="hidden sm:inline">{label}</span>
    </div>
  );
}

export default function Header() {
  const router = useRouter();
  const user = useSyncExternalStore(subscribeAuth, getAuthSnapshot, getAuthServerSnapshot);

  async function signOut() {
    const token = getRefreshToken();
    // Отзываем сессию на сервере, но выходим в любом случае: если запрос
    // не прошёл, держать человека внутри против его воли неправильно.
    if (token) {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: token }),
      }).catch(() => undefined);
    }
    clearSession();
    router.replace("/login");
  }

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between gap-4 border-b border-border bg-surface px-6">
      <div className="flex min-w-0 items-center gap-3">
        <h1 className="hidden truncate text-lg font-bold text-text xl:block">
          {user ? `Welcome back, ${user.username}` : "OverCoding"}
        </h1>
        {user && (
          <span className="shrink-0 rounded-full border border-accent/20 bg-accent/10 px-2.5 py-0.5 text-xs font-semibold text-accent">
            {user.level}
          </span>
        )}
      </div>

      <div className="flex items-center gap-3">
        {user && (
          <>
            <Stat icon="🔥" value={user.streak_days} label="streak" />
            <Stat icon="💎" value={user.coins} label="coins" />
            <Stat icon="🏆" value={user.points} label="pts" />
          </>
        )}

        <ThemeToggle />

        {user ? (
          <div className="flex items-center gap-2">
            <Link
              href={`/profile`}
              title={user.email}
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-sm font-bold text-accent-fg"
            >
              {user.username.slice(0, 1).toUpperCase()}
            </Link>
            <button
              type="button"
              onClick={signOut}
              className="text-xs text-text-2 hover:text-text"
            >
              Sign out
            </button>
          </div>
        ) : (
          <Link href="/login" className="text-xs text-accent hover:underline">
            Sign in
          </Link>
        )}
      </div>
    </header>
  );
}
