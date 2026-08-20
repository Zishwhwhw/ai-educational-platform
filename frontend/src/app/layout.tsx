import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";

import { THEME_INIT_SCRIPT } from "@/lib/theme";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });

// Моноширинный нужен не только редактору: панель тестов, вывод программы
// и инлайн-фрагменты кода в теории используют тот же шрифт.
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "OverCoding",
  description: "Learn programming by writing code, not by watching videos",
};

/**
 * Корневой layout намеренно минимален: только тема и шрифты.
 *
 * Оболочки живут в группах маршрутов — `(app)` с навигацией и `(learn)` без неё.
 * Учебному экрану нужно всё место под работу, и раньше он не мог его получить,
 * потому что боковые панели были прибиты к корню.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // suppressHydrationWarning: data-theme проставляется скриптом ниже
    // до гидратации, поэтому разметка сервера и клиента расходятся намеренно.
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} bg-bg text-text`}>
        {/* Первым элементом body, а не в <head>: документация Next запрещает
            добавлять <head> в корневой layout вручную. Браузер выполняет такой
            скрипт синхронно при разборе HTML — до первой отрисовки, поэтому
            вспышки светлой темы не будет.
            node_modules/next/dist/docs/01-app/02-guides/preventing-flash-before-hydration.md */}
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
        {children}
      </body>
    </html>
  );
}
