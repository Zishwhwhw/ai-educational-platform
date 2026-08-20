import type { Metadata } from "next";

import RequireAuth from "@/components/auth/RequireAuth";

export const metadata: Metadata = { title: "OverCoding — Lesson" };

/**
 * Оболочка учебного экрана: без боковой навигации и без панели наставника.
 *
 * На экране, где пишут код, всё место отдаётся работе. Ради этого учебные
 * маршруты вынесены в отдельную группу — раньше панели были прибиты к корню
 * и занимали почти 600 пикселей на любой странице.
 */
export default function LearnLayout({ children }: { children: React.ReactNode }) {
  return (
    <RequireAuth>
      <div className="flex h-screen flex-col overflow-hidden">{children}</div>
    </RequireAuth>
  );
}
