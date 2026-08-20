"use client";

import { useRouter } from "next/navigation";
import { useEffect, useSyncExternalStore } from "react";

import Skeleton from "@/components/ui/Skeleton";
import {
  getAuthServerSnapshot,
  getAuthSnapshot,
  getAccessToken,
  subscribeAuth,
} from "@/lib/auth";

/**
 * Пускает дальше только с сессией.
 *
 * Проверка на клиенте, а не на сервере: токен лежит в `localStorage`, до
 * которого серверный рендер не дотягивается. Пока состояние не прочитано,
 * показывается скелетон — мигнуть формой входа залогиненному пользователю
 * хуже, чем подождать кадр.
 */
export default function RequireAuth({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const user = useSyncExternalStore(subscribeAuth, getAuthSnapshot, getAuthServerSnapshot);

  // Токен без сохранённого пользователя тоже считается сессией: профиль мог
  // не сохраниться, но работать это не мешает.
  const hasSession = user !== null || getAccessToken() !== null;

  useEffect(() => {
    if (!hasSession) router.replace("/login");
  }, [hasSession, router]);

  if (!hasSession) {
    return (
      <div className="space-y-3 p-6">
        <Skeleton variant="text" className="w-40" />
        <Skeleton variant="rect" className="h-32 w-full" />
      </div>
    );
  }
  return <>{children}</>;
}
