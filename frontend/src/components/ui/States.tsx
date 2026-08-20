import Button from "@/components/ui/Button";

/** Пустое состояние: объяснение и ровно одно целевое действие.
 *  Ни на одной из девяти унаследованных страниц такого состояния нет —
 *  они нарисованы только для случая «данные есть». */
export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-border px-6 py-12 text-center">
      {icon && (
        <span aria-hidden="true" className="text-2xl opacity-60">
          {icon}
        </span>
      )}
      <p className="text-base font-medium text-text">{title}</p>
      {description && <p className="max-w-sm text-sm text-text-2">{description}</p>}
      {actionLabel && onAction && (
        <Button size="sm" variant="secondary" onClick={onAction} className="mt-1">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

/** Ошибка: что случилось и кнопка повтора. Пустой экран вместо ошибки —
 *  худший вариант: пользователь не понимает, ждать ему или обновлять. */
export function ErrorState({
  title = "Something went wrong",
  description,
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-3 rounded-lg border border-danger/40 px-6 py-12 text-center"
    >
      <span aria-hidden="true" className="text-2xl">
        ⚠
      </span>
      <p className="text-base font-medium text-text">{title}</p>
      {description && <p className="max-w-sm text-sm text-text-2">{description}</p>}
      {onRetry && (
        <Button size="sm" variant="secondary" onClick={onRetry} className="mt-1">
          Try again
        </Button>
      )}
    </div>
  );
}
