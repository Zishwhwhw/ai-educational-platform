"use client";

import { forwardRef, useId } from "react";

import { cn } from "@/lib/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, hint, error, id, className, ...rest },
  ref,
) {
  const auto = useId();
  const inputId = id ?? auto;
  const describedBy = error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined;

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-text">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className={cn(
          "h-10 rounded-md border bg-bg px-3 text-sm text-text",
          "placeholder:text-text-muted",
          "disabled:cursor-not-allowed disabled:opacity-50",
          // border-strong, а не border: границе поля ввода нужен контраст 3:1
          // к фону по WCAG 1.4.11, декоративному разделителю — нет.
          error ? "border-danger" : "border-border-strong",
          className,
        )}
        {...rest}
      />
      {/* Ошибка объявляется вслух: изменение цвета рамки скринридер не передаёт. */}
      {error ? (
        <p id={`${inputId}-error`} role="alert" className="text-xs text-danger">
          {error}
        </p>
      ) : hint ? (
        <p id={`${inputId}-hint`} className="text-xs text-text-2">
          {hint}
        </p>
      ) : null}
    </div>
  );
});

export default Input;
