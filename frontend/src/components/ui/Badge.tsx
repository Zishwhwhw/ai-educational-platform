import { cn } from "@/lib/cn";

type Tone = "neutral" | "success" | "danger" | "warning" | "accent";

const TONES: Record<Tone, string> = {
  neutral: "border-border text-text-2",
  success: "border-success/40 text-success",
  danger: "border-danger/40 text-danger",
  warning: "border-warning/40 text-warning",
  accent: "border-accent/40 text-accent",
};

export default function Badge({
  tone = "neutral",
  icon,
  children,
  className,
}: {
  tone?: Tone;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
        TONES[tone],
        className,
      )}
    >
      {/* Значок декоративен: смысл несёт текст. Цвет не должен быть
          единственным носителем информации — важно для дальтоников. */}
      {icon && <span aria-hidden="true">{icon}</span>}
      {children}
    </span>
  );
}
