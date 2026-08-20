"use client";

import { useRef } from "react";

import { cn } from "@/lib/cn";

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

/** Вкладки с клавиатурной навигацией по образцу WAI-ARIA:
 *  стрелки перемещают, Home и End прыгают к краям. Без этого вкладки
 *  недоступны тем, кто не пользуется мышью. */
export default function Tabs({
  items,
  activeId,
  onChange,
  className,
}: {
  items: TabItem[];
  activeId: string;
  onChange: (id: string) => void;
  className?: string;
}) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});

  function onKeyDown(e: React.KeyboardEvent) {
    const i = items.findIndex((t) => t.id === activeId);
    let next = i;
    if (e.key === "ArrowRight") next = (i + 1) % items.length;
    else if (e.key === "ArrowLeft") next = (i - 1 + items.length) % items.length;
    else if (e.key === "Home") next = 0;
    else if (e.key === "End") next = items.length - 1;
    else return;
    e.preventDefault();
    const id = items[next].id;
    onChange(id);
    refs.current[id]?.focus();
  }

  return (
    <div role="tablist" onKeyDown={onKeyDown} className={cn("flex gap-1", className)}>
      {items.map((t) => {
        const active = t.id === activeId;
        return (
          <button
            key={t.id}
            ref={(el) => {
              refs.current[t.id] = el;
            }}
            role="tab"
            type="button"
            aria-selected={active}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(t.id)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors",
              active ? "bg-surface font-medium text-text" : "text-text-2 hover:text-text",
            )}
          >
            {t.icon && <span aria-hidden="true">{t.icon}</span>}
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
