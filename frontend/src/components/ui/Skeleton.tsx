import { cn } from "@/lib/cn";

/** Скелетон повторяет форму будущего содержимого, а не крутится по центру:
 *  так меньше сдвига макета, когда данные приедут. */
export default function Skeleton({
  variant = "text",
  className,
}: {
  variant?: "text" | "rect" | "circle";
  className?: string;
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "block animate-pulse bg-border motion-reduce:animate-none",
        variant === "text" && "h-4 rounded",
        variant === "rect" && "rounded-md",
        variant === "circle" && "rounded-full",
        className,
      )}
    />
  );
}
