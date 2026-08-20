"use client";

import { useEffect, useRef } from "react";

import Button from "@/components/ui/Button";

/**
 * Модальное окно на нативном `<dialog>`.
 *
 * Нативный элемент даёт ловушку фокуса, закрытие по Esc и слой поверх всего
 * без ручной реализации — то, что чаще всего делают неправильно в самописных
 * модалках. Используется, в частности, для подтверждения необратимого
 * раскрытия подсказки на экране урока.
 */
export default function Dialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  destructive = false,
  onConfirm,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  onConfirm?: () => void;
  onClose: () => void;
  children?: React.ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);

  // Esc закрывает окно средствами браузера — сообщаем об этом наверх.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onCancel = (e: Event) => {
      e.preventDefault();
      onClose();
    };
    el.addEventListener("cancel", onCancel);
    return () => el.removeEventListener("cancel", onCancel);
  }, [onClose]);

  return (
    <dialog
      ref={ref}
      className="max-w-md rounded-lg border border-border bg-raised p-0 text-text shadow-e2 backdrop:bg-black/50"
    >
      <div className="flex flex-col gap-3 p-5">
        <h2 className="text-base font-semibold">{title}</h2>
        {description && <p className="text-sm text-text-2">{description}</p>}
        {children}
        <div className="mt-2 flex justify-end gap-2">
          <Button size="sm" variant="ghost" onClick={onClose}>
            {cancelLabel}
          </Button>
          {onConfirm && (
            <Button size="sm" variant={destructive ? "danger" : "primary"} onClick={onConfirm}>
              {confirmLabel}
            </Button>
          )}
        </div>
      </div>
    </dialog>
  );
}
