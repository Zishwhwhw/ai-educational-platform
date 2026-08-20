"use client";

/**
 * Простые типы шагов: теория, видео, выбор, ввод.
 *
 * Каждый компонент отвечает только за сбор ответа и отдаёт его наверх
 * в том виде, какой ждёт сервер. Проверкой они не занимаются — правильные
 * ответы на клиент не приходят и приходить не должны.
 */

import { useId, useState } from "react";

import Input from "@/components/ui/Input";
import type { StepContent } from "@/lib/api-types";
import { cn } from "@/lib/cn";

export type Answer = Record<string, unknown>;

export interface StepInputProps {
  content: StepContent;
  disabled?: boolean;
  onChange: (answer: Answer | null) => void;
}

export function TextStep({ content }: { content: StepContent }) {
  return (
    <div className="prose-measure whitespace-pre-wrap text-sm text-text">
      {content.markdown ?? ""}
    </div>
  );
}

export function VideoStep({ content }: { content: StepContent }) {
  if (!content.url) {
    return <p className="text-sm text-text-muted">No video attached to this step.</p>;
  }
  return (
    <div className="space-y-2">
      <div className="aspect-video w-full overflow-hidden rounded-lg border border-border">
        <iframe
          src={content.url}
          title="Lesson video"
          className="h-full w-full"
          allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture"
          allowFullScreen
        />
      </div>
      {/* Урок обязан быть проходим без видео: ролик может быть удалён,
          заблокирован в стране или просто не грузиться. */}
      <p className="text-xs text-text-muted">
        The video is supporting material — you can complete this step without it.
      </p>
    </div>
  );
}

export function ChoiceStep({
  content,
  multiple,
  disabled,
  onChange,
}: StepInputProps & { multiple: boolean }) {
  const [selected, setSelected] = useState<string[]>([]);
  const name = useId();
  const options = content.options ?? [];

  function toggle(id: string) {
    const next = multiple
      ? selected.includes(id)
        ? selected.filter((x) => x !== id)
        : [...selected, id]
      : [id];
    setSelected(next);
    onChange(next.length ? (multiple ? { choices: next } : { choice: next[0] }) : null);
  }

  return (
    <fieldset disabled={disabled} className="space-y-2">
      {content.question && (
        <legend className="mb-2 text-sm text-text">{content.question}</legend>
      )}
      {multiple && (
        <p className="text-xs text-text-muted">
          Select all that apply — extra selections reduce the score.
        </p>
      )}
      {options.map((o) => {
        const on = selected.includes(o.id);
        return (
          <label
            key={o.id}
            className={cn(
              "flex cursor-pointer items-center gap-2.5 rounded-md border px-3 py-2 text-sm transition-colors",
              on ? "border-accent bg-accent/10 text-text" : "border-border text-text-2 hover:text-text",
              disabled && "cursor-not-allowed opacity-60",
            )}
          >
            <input
              type={multiple ? "checkbox" : "radio"}
              name={name}
              checked={on}
              onChange={() => toggle(o.id)}
              className="accent-[var(--accent)]"
            />
            {o.text}
          </label>
        );
      })}
    </fieldset>
  );
}

export function InputStep({
  content,
  numeric,
  disabled,
  onChange,
}: StepInputProps & { numeric: boolean }) {
  const [value, setValue] = useState("");

  return (
    <div className="space-y-2">
      {content.question && <p className="text-sm text-text">{content.question}</p>}
      <div className="flex items-end gap-2">
        <div className="w-64">
          <Input
            // inputMode="decimal", а не type="number": числовое поле в браузерах
            // отбрасывает запятую как разделитель, а сервер её принимает.
            inputMode={numeric ? "decimal" : "text"}
            value={value}
            disabled={disabled}
            placeholder={content.placeholder ?? (numeric ? "42" : "your answer")}
            onChange={(e) => {
              setValue(e.target.value);
              onChange(
                e.target.value.trim()
                  ? numeric
                    ? { value: e.target.value }
                    : { text: e.target.value }
                  : null,
              );
            }}
          />
        </div>
        {content.unit && <span className="pb-2.5 text-sm text-text-2">{content.unit}</span>}
      </div>
    </div>
  );
}
