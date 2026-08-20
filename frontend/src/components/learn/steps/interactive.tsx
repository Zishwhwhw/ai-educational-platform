"use client";

/**
 * Сопоставление и сортировка.
 *
 * Оба типа обычно делают перетаскиванием — и обычно делают недоступными
 * с клавиатуры. Здесь перетаскивания нет вовсе:
 *
 * * **Сопоставление** — выбрать слева, выбрать справа. Два клика вместо
 *   тянущего жеста; работает пальцем, мышью и с клавиатуры одинаково.
 * * **Сортировка** — кнопки «вверх/вниз» у каждого элемента.
 *
 * Это не компромисс ради доступности: на телефоне перетаскивание внутри
 * прокручиваемой страницы работает плохо у всех.
 */

import { useState } from "react";

import Button from "@/components/ui/Button";
import type { StepOption } from "@/lib/api-types";
import { cn } from "@/lib/cn";

import type { StepInputProps } from "./inputs";

export function MatchingStep({ content, disabled, onChange }: StepInputProps) {
  const left = content.left ?? [];
  const right = content.right ?? [];
  const [pairs, setPairs] = useState<Record<string, string>>({});
  const [activeLeft, setActiveLeft] = useState<string | null>(null);

  function pick(side: "left" | "right", id: string) {
    if (side === "left") {
      setActiveLeft((cur) => (cur === id ? null : id));
      return;
    }
    if (activeLeft == null) return;
    const next = { ...pairs, [activeLeft]: id };
    setPairs(next);
    setActiveLeft(null);
    onChange(Object.keys(next).length ? { pairs: next } : null);
  }

  function clear(leftId: string) {
    const next = { ...pairs };
    delete next[leftId];
    setPairs(next);
    onChange(Object.keys(next).length ? { pairs: next } : null);
  }

  const rightById = Object.fromEntries(right.map((r) => [r.id, r.text]));
  const takenRight = new Set(Object.values(pairs));

  return (
    <div className="space-y-3">
      {content.question && <p className="text-sm text-text">{content.question}</p>}
      <p className="text-xs text-text-muted">
        {activeLeft ? "Now pick its match on the right" : "Pick an item on the left, then its match"}
      </p>

      <div className="grid gap-3 sm:grid-cols-2">
        <ul className="space-y-1.5">
          {left.map((item) => {
            const matched = pairs[item.id];
            return (
              <li key={item.id}>
                <button
                  type="button"
                  disabled={disabled}
                  aria-pressed={activeLeft === item.id}
                  onClick={() => pick("left", item.id)}
                  className={cn(
                    "w-full rounded-md border px-3 py-2 text-left text-sm transition-colors",
                    activeLeft === item.id
                      ? "border-accent bg-accent/10 text-text"
                      : matched
                        ? "border-success/40 text-text"
                        : "border-border text-text-2 hover:text-text",
                  )}
                >
                  <span>{item.text}</span>
                  {matched && (
                    <span className="mt-0.5 block text-xs text-text-muted">
                      → {rightById[matched]}
                      <span
                        role="button"
                        tabIndex={0}
                        onClick={(e) => {
                          e.stopPropagation();
                          clear(item.id);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            e.stopPropagation();
                            clear(item.id);
                          }
                        }}
                        className="ml-2 cursor-pointer text-danger hover:underline"
                      >
                        clear
                      </span>
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>

        <ul className="space-y-1.5">
          {right.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                disabled={disabled || activeLeft == null}
                onClick={() => pick("right", item.id)}
                className={cn(
                  "w-full rounded-md border px-3 py-2 text-left text-sm transition-colors",
                  takenRight.has(item.id)
                    ? "border-border text-text-muted"
                    : activeLeft
                      ? "border-accent/50 text-text hover:bg-accent/10"
                      : "border-border text-text-2",
                  (disabled || activeLeft == null) && "cursor-not-allowed",
                )}
              >
                {item.text}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export function OrderingStep({ content, disabled, onChange }: StepInputProps) {
  const initial: StepOption[] = content.items ?? [];
  const [items, setItems] = useState<StepOption[]>(initial);

  function move(index: number, delta: number) {
    const target = index + delta;
    if (target < 0 || target >= items.length) return;
    const next = [...items];
    [next[index], next[target]] = [next[target], next[index]];
    setItems(next);
    onChange({ order: next.map((i) => i.id) });
  }

  return (
    <div className="space-y-3">
      {content.question && <p className="text-sm text-text">{content.question}</p>}
      <p className="text-xs text-text-muted">
        Use the arrows to reorder. Each item in the right place earns part of the score.
      </p>
      <ol className="space-y-1.5">
        {items.map((item, i) => (
          <li
            key={item.id}
            className="flex items-center gap-2 rounded-md border border-border px-3 py-2"
          >
            <span className="w-5 shrink-0 font-mono text-xs text-text-muted">{i + 1}</span>
            <span className="min-w-0 flex-1 text-sm text-text">{item.text}</span>
            <div className="flex shrink-0 gap-1">
              <Button
                size="sm"
                variant="ghost"
                disabled={disabled || i === 0}
                aria-label={`Move "${item.text}" up`}
                onClick={() => move(i, -1)}
              >
                ↑
              </Button>
              <Button
                size="sm"
                variant="ghost"
                disabled={disabled || i === items.length - 1}
                aria-label={`Move "${item.text}" down`}
                onClick={() => move(i, 1)}
              >
                ↓
              </Button>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
