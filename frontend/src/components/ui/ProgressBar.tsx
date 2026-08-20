import { cn } from "@/lib/cn";

export default function ProgressBar({
  value,
  max = 100,
  showBall = false,
  label,
  className,
}: {
  value: number;
  max?: number;
  /** Шарик-ползунок на конце полосы — требование спеки для карточек курсов. */
  showBall?: boolean;
  label?: string;
  className?: string;
}) {
  const pct = max > 0 ? Math.min(100, Math.max(0, (value / max) * 100)) : 0;

  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(value)}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-label={label ?? "Progress"}
      className={cn("relative h-1.5 w-full rounded-full bg-border", className)}
    >
      <div
        className="h-full rounded-full bg-accent transition-[width] duration-300 motion-reduce:transition-none"
        style={{ width: `${pct}%` }}
      />
      {showBall && pct > 0 && (
        <span
          aria-hidden="true"
          className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-bg bg-accent transition-[left] duration-300 motion-reduce:transition-none"
          style={{ left: `${pct}%` }}
        />
      )}
    </div>
  );
}
