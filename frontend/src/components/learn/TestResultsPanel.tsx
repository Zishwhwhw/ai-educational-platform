"use client";

import { cn } from "@/lib/cn";
import type { ExecStatus, TestOutcome } from "@/lib/api-types";

/**
 * Результаты прогона по тест-кейсам.
 *
 * Три правила, заданные проектом:
 *
 * 1. Статус несёт значок и текст, а не только цвет — красно-зелёная слепота
 *    самая частая, а здесь цвет иначе нёс бы всю информацию.
 * 2. Скрытый тест показывает имя и статус, но **никогда** вход и ожидаемый
 *    вывод — иначе тесты выносятся из платформы одной отправкой.
 * 3. Ошибка компиляции и таймаут — отдельные состояния, а не «все тесты
 *    провалены»: причина у них разная, и подсказка нужна разная.
 */

const STATUS_META: Record<ExecStatus, { icon: string; label: string; tone: string }> = {
  ok: { icon: "✓", label: "passed", tone: "text-success" },
  runtime_error: { icon: "✗", label: "error", tone: "text-danger" },
  compile_error: { icon: "✗", label: "compile error", tone: "text-danger" },
  timeout: { icon: "⏱", label: "timeout", tone: "text-warning" },
  memory_exceeded: { icon: "▣", label: "out of memory", tone: "text-warning" },
  engine_error: { icon: "⚠", label: "engine unavailable", tone: "text-warning" },
};

/** Оформление строки.
 *
 * Тонкое место: тест мог отработать без единой ошибки и всё равно провалиться —
 * программа просто вывела не то. У такого исхода `status === "ok"` при
 * `passed === false`, и если брать оформление по статусу, провал выглядит
 * как успех. Поэтому решает `passed`, а статус уточняет только причину.
 */
function rowMeta(outcome: TestOutcome) {
  if (outcome.passed) return STATUS_META.ok;
  if (outcome.status === "ok") {
    return { icon: "✗", label: "wrong output", tone: "text-danger" };
  }
  return STATUS_META[outcome.status] ?? STATUS_META.runtime_error;
}

function Row({ outcome, index }: { outcome: TestOutcome; index: number }) {
  const meta = rowMeta(outcome);

  return (
    <li className="border-b border-border last:border-0">
      <div className="flex items-center gap-2 px-3 py-2 font-mono text-xs">
        <span aria-hidden="true" className={cn("w-3 shrink-0", meta.tone)}>
          {meta.icon}
        </span>
        <span className="min-w-0 flex-1 truncate text-text">
          {outcome.name || `test ${index + 1}`}
        </span>
        {outcome.is_hidden && (
          <span className="shrink-0 rounded border border-border px-1.5 py-px text-[10px] text-text-muted">
            hidden
          </span>
        )}
        <span className={cn("shrink-0", meta.tone)}>{meta.label}</span>
        {outcome.time_ms !== null && (
          <span className="w-14 shrink-0 text-right text-text-muted">{outcome.time_ms}ms</span>
        )}
      </div>

      {/* Диф показывается только для видимых тестов и только при провале. */}
      {!outcome.passed && !outcome.is_hidden && outcome.expected_stdout != null && (
        <div className="space-y-1 px-3 pb-2.5 pl-8 font-mono text-xs">
          <div className="flex gap-2">
            <span className="w-16 shrink-0 text-text-muted">expected</span>
            <pre className="min-w-0 flex-1 overflow-x-auto whitespace-pre-wrap text-success">
              {outcome.expected_stdout || "(empty)"}
            </pre>
          </div>
          <div className="flex gap-2">
            <span className="w-16 shrink-0 text-text-muted">got</span>
            <pre className="min-w-0 flex-1 overflow-x-auto whitespace-pre-wrap text-danger">
              {outcome.actual_stdout || "(empty)"}
            </pre>
          </div>
          {outcome.stderr && (
            <div className="flex gap-2">
              <span className="w-16 shrink-0 text-text-muted">stderr</span>
              <pre className="min-w-0 flex-1 overflow-x-auto whitespace-pre-wrap text-danger">
                {outcome.stderr.trim()}
              </pre>
            </div>
          )}
        </div>
      )}
    </li>
  );
}

export default function TestResultsPanel({
  outcomes,
  passedCount,
  totalCount,
  hiddenPending = 0,
  compileOutput = "",
  points,
  maxPoints,
  empty,
}: {
  outcomes: TestOutcome[];
  passedCount: number;
  totalCount: number;
  /** Сколько скрытых тестов ещё не прогонялось — показывается до отправки. */
  hiddenPending?: number;
  compileOutput?: string;
  points?: number;
  maxPoints?: number;
  empty?: React.ReactNode;
}) {
  if (compileOutput) {
    return (
      <div className="p-3">
        <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-danger">
          <span aria-hidden="true">✗</span> Compilation failed
        </p>
        <pre className="overflow-x-auto rounded border border-border bg-bg p-2 font-mono text-xs text-text-2">
          {compileOutput.trim()}
        </pre>
      </div>
    );
  }

  if (outcomes.length === 0) {
    return <div className="p-6 text-center text-xs text-text-muted">{empty ?? "Run your code to see test results"}</div>;
  }

  return (
    <div className="flex min-h-0 flex-col">
      <ul className="min-h-0 flex-1 overflow-y-auto">
        {outcomes.map((o, i) => (
          <Row key={`${o.name}-${i}`} outcome={o} index={i} />
        ))}
        {hiddenPending > 0 && (
          <li className="flex items-center gap-2 px-3 py-2 font-mono text-xs text-text-muted">
            <span aria-hidden="true" className="w-3">
              ●
            </span>
            {hiddenPending} hidden {hiddenPending === 1 ? "test" : "tests"} — press Submit to check
          </li>
        )}
      </ul>

      {/* Итог объявляется вслух: без этого пользователь скринридера не узнает
          результат — он передан только цветом и значками. */}
      <p
        aria-live="polite"
        className="border-t border-border px-3 py-2 text-xs text-text-2"
      >
        {passedCount} of {totalCount} passed
        {points != null && maxPoints != null && (
          <span className="text-text-muted">
            {" · "}
            {points}/{maxPoints} pts
          </span>
        )}
      </p>
    </div>
  );
}
