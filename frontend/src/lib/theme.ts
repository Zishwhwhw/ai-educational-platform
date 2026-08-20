"use client";

/** Тема: три состояния, а не два. `system` — значение по умолчанию. */
export type ThemeSetting = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

export const THEME_STORAGE_KEY = "oc-theme";

export function resolveTheme(setting: ThemeSetting): ResolvedTheme {
  if (setting !== "system") return setting;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function readThemeSetting(): ThemeSetting {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "light" || stored === "dark" || stored === "system") return stored;
  } catch {
    // localStorage недоступен (приватный режим, отключённые куки) — не повод падать.
  }
  return "system";
}

export function applyTheme(setting: ThemeSetting): void {
  const root = document.documentElement;

  // Гасим переходы на один кадр, иначе переключение выглядит как долгий перелив.
  root.classList.add("theme-switching");
  root.setAttribute("data-theme", resolveTheme(setting));
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => root.classList.remove("theme-switching"));
  });

  try {
    localStorage.setItem(THEME_STORAGE_KEY, setting);
  } catch {
    // см. выше
  }
}

/**
 * Скрипт, встраиваемый в <head> до первой отрисовки.
 * Без него страница на мгновение показывает светлую тему перед тёмной.
 * Обязан быть синхронным и без defer.
 */
export const THEME_INIT_SCRIPT = `
(function(){
  try {
    var s = localStorage.getItem('${THEME_STORAGE_KEY}');
    if (s !== 'light' && s !== 'dark') {
      s = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', s);
  } catch (e) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
})();
`.trim();

/* ---------------------------------------------------------------------------
   Внешнее хранилище для useSyncExternalStore.

   localStorage — внешняя по отношению к React система, поэтому читать её
   через useState + useEffect неверно: это вызывает каскадный ререндер и
   расхождение при гидратации. useSyncExternalStore решает оба вопроса.
   --------------------------------------------------------------------------- */

const listeners = new Set<() => void>();

function emit(): void {
  for (const l of listeners) l();
}

export function subscribeTheme(onChange: () => void): () => void {
  listeners.add(onChange);
  // storage-событие приходит, когда тему сменили в другой вкладке.
  window.addEventListener("storage", onChange);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener("storage", onChange);
  };
}

export function getThemeSnapshot(): ThemeSetting {
  return readThemeSetting();
}

/** На сервере выбора пользователя нет — всегда `system`. */
export function getThemeServerSnapshot(): ThemeSetting {
  return "system";
}

export function setTheme(setting: ThemeSetting): void {
  applyTheme(setting);
  emit();
}
