"use client";

import { useEffect, useSyncExternalStore } from "react";

import {
  applyTheme,
  getThemeServerSnapshot,
  getThemeSnapshot,
  setTheme,
  subscribeTheme,
  type ThemeSetting,
} from "@/lib/theme";

const OPTIONS: { value: ThemeSetting; label: string; icon: string }[] = [
  { value: "light", label: "Light", icon: "☀" },
  { value: "dark", label: "Dark", icon: "☾" },
  { value: "system", label: "System", icon: "◐" },
];

export default function ThemeToggle() {
  // localStorage — внешняя система, поэтому useSyncExternalStore, а не
  // useState + useEffect: не даёт каскадного ререндера и корректно
  // расходится между сервером ("system") и клиентом.
  const setting = useSyncExternalStore(
    subscribeTheme,
    getThemeSnapshot,
    getThemeServerSnapshot,
  );

  // Пока выбран "system", тема следует за настройкой ОС.
  useEffect(() => {
    if (setting !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => applyTheme("system");
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [setting]);

  return (
    <div
      role="radiogroup"
      aria-label="Color theme"
      className="inline-flex items-center gap-0.5 rounded-md border border-border bg-surface p-0.5"
    >
      {OPTIONS.map((o) => {
        const active = setting === o.value;
        return (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={o.label}
            title={o.label}
            onClick={() => setTheme(o.value)}
            className={[
              "flex h-7 w-7 items-center justify-center rounded text-sm transition-colors",
              active
                ? "bg-accent text-accent-fg"
                : "text-text-2 hover:bg-raised hover:text-text",
            ].join(" ")}
          >
            <span aria-hidden="true">{o.icon}</span>
          </button>
        );
      })}
    </div>
  );
}
