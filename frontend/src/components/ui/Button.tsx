"use client";

import { forwardRef } from "react";

import { cn } from "@/lib/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

const VARIANTS: Record<Variant, string> = {
  // Только токены. Сырые цвета Tailwind запрещены: именно они раньше
  // перекрывали тему и делали светлую нерабочей.
  primary: "bg-accent text-accent-fg hover:opacity-90 active:opacity-80",
  secondary:
    "border border-border-strong bg-surface text-text hover:bg-raised active:bg-raised",
  ghost: "text-text-2 hover:bg-surface hover:text-text",
  danger: "bg-danger text-bg hover:opacity-90 active:opacity-80",
};

const SIZES: Record<Size, string> = {
  sm: "h-8 gap-1.5 px-3 text-xs",
  md: "h-10 gap-2 px-4 text-sm",
  lg: "h-12 gap-2 px-6 text-base",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = "primary",
    size = "md",
    loading = false,
    iconLeft,
    iconRight,
    fullWidth,
    disabled,
    className,
    children,
    ...rest
  },
  ref,
) {
  return (
    <button
      ref={ref}
      // Во время загрузки кнопка остаётся в потоке фокуса, но не срабатывает:
      // disabled убрал бы её из навигации с клавиатуры прямо под пальцами.
      aria-busy={loading || undefined}
      aria-disabled={disabled || loading || undefined}
      disabled={disabled}
      onClick={loading ? (e) => e.preventDefault() : rest.onClick}
      className={cn(
        "inline-flex select-none items-center justify-center rounded-md font-medium",
        "transition-[background-color,opacity,border-color] duration-150",
        "disabled:pointer-events-none disabled:opacity-50",
        loading && "cursor-progress",
        fullWidth && "w-full",
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...rest}
    >
      {loading ? <Spinner /> : iconLeft}
      {children}
      {!loading && iconRight}
    </button>
  );
});

function Spinner() {
  return (
    <span
      aria-hidden="true"
      className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent motion-reduce:animate-none"
    />
  );
}

export default Button;
