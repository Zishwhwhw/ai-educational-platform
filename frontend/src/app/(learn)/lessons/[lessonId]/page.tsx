"use client";

/**
 * Урок: последовательность шагов.
 *
 * Шаги показываются по одному, а не списком. Причина не в экономии места:
 * список сразу показывает, сколько ещё осталось, и человек начинает
 * пролистывать вместо того, чтобы читать. Один шаг за раз — та же логика,
 * по которой Duolingo не показывает весь урок разом.
 *
 * Прогресс по шагам виден сверху, вернуться назад можно всегда.
 */

import Link from "next/link";
import { use, useCallback, useState } from "react";

import StepRenderer from "@/components/learn/steps/StepRenderer";
import Button from "@/components/ui/Button";
import Skeleton from "@/components/ui/Skeleton";
import { EmptyState, ErrorState } from "@/components/ui/States";
import type { LessonStep, StepAnswerResponse } from "@/lib/api-types";
import { cn } from "@/lib/cn";
import { useApi } from "@/lib/useApi";

export default function LessonPage({ params }: { params: Promise<{ lessonId: string }> }) {
  const { lessonId } = use(params);
  const { data, error, loading, reload } = useApi<LessonStep[]>(`/lessons/${lessonId}/steps`);

  const [index, setIndex] = useState(0);
  const [done, setDone] = useState<Record<number, boolean>>({});

  const onCompleted = useCallback(
    (stepId: number) => (res: StepAnswerResponse) => {
      if (res.is_correct) setDone((d) => ({ ...d, [stepId]: true }));
    },
    [],
  );

  if (loading) return <LessonSkeleton />;
  if (error) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <ErrorState title="Could not load the lesson" description={error.message} onRetry={reload} />
      </div>
    );
  }

  const steps = data ?? [];
  if (steps.length === 0) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <EmptyState
          icon="📭"
          title="This lesson has no steps yet"
          description="Its author has not added any content."
        />
      </div>
    );
  }

  const step = steps[Math.min(index, steps.length - 1)];
  const completed = (s: LessonStep) => s.is_completed || done[s.id];
  const isLast = index === steps.length - 1;

  return (
    <>
      <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border px-4">
        <Link href="/catalog" className="text-sm text-text-2 hover:text-text">
          ← Catalog
        </Link>
        <span className="text-sm font-medium text-text">
          Step {index + 1} of {steps.length}
        </span>

        {/* Точки прогресса: путь и остаток видны сразу, это удерживает. */}
        <ol className="ml-2 flex items-center gap-1" aria-label="Lesson progress">
          {steps.map((s, i) => (
            <li key={s.id}>
              <button
                type="button"
                aria-label={`Step ${i + 1}${completed(s) ? ", completed" : ""}`}
                aria-current={i === index ? "step" : undefined}
                onClick={() => setIndex(i)}
                className={cn(
                  "h-2 w-2 rounded-full transition-colors",
                  completed(s) ? "bg-success" : i === index ? "bg-accent" : "bg-border",
                )}
              />
            </li>
          ))}
        </ol>
      </header>

      <div className="mx-auto w-full max-w-2xl flex-1 overflow-y-auto p-4">
        <StepRenderer key={step.id} step={step} onCompleted={onCompleted(step.id)} />

        <nav className="mt-4 flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            disabled={index === 0}
            onClick={() => setIndex((i) => i - 1)}
          >
            ← Previous
          </Button>
          {!isLast ? (
            <Button size="sm" onClick={() => setIndex((i) => i + 1)}>
              Next →
            </Button>
          ) : (
            <Link
              href="/catalog"
              className="inline-flex h-8 items-center rounded-md bg-accent px-3 text-xs font-medium text-accent-fg hover:opacity-90"
            >
              Finish lesson
            </Link>
          )}
        </nav>
      </div>
    </>
  );
}

function LessonSkeleton() {
  return (
    <>
      <div className="flex h-14 shrink-0 items-center gap-3 border-b border-border px-4">
        <Skeleton variant="text" className="w-32" />
      </div>
      <div className="mx-auto w-full max-w-2xl space-y-3 p-4">
        <Skeleton variant="rect" className="h-40 w-full" />
        <Skeleton variant="text" className="w-1/3" />
      </div>
    </>
  );
}
