import { cn } from "@/lib/cn";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  elevation?: "flat" | "raised";
  interactive?: boolean;
}

export default function Card({
  elevation = "flat",
  interactive = false,
  className,
  children,
  ...rest
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-surface",
        elevation === "raised" && "bg-raised shadow-e1",
        interactive &&
          // Приподнятие при наведении включено по умолчанию (см. §6 дизайн-документа),
          // но гасится при prefers-reduced-motion.
          "cursor-pointer transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-e2 motion-reduce:transform-none motion-reduce:transition-none",
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}
