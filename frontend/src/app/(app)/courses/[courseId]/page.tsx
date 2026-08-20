"use client";

/**
 * Страница курса: модули, уроки, задания и прогресс.
 *
 * Замыкает цикл с двух сторон. До неё в задание было неоткуда попасть
 * и некуда идти после решения: экран задания открывался только по прямой ссылке.
 */

import Link from "next/link";
import { use } from "react";

import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import ProgressBar from "@/components/ui/ProgressBar";
import Skeleton from "@/components/ui/Skeleton";
import { EmptyState, ErrorState } from "@/components/ui/States";
import type { CourseOutline, LessonOutline } from "@/lib/api-types";
import { useApi } from "@/lib/useApi";

export default function CoursePage({ params }: { params: Promise<{ courseId: string }> }) {
  const { courseId } = use(params);
  const { data: course, error, loading, reload } = useApi<CourseOutline>(`/courses/${courseId}`);

  if (loading) return <OutlineSkeleton />;

  if (error) {
    return (
      <ErrorState title="Could not load the course" description={error.message} onRetry={reload} />
    );
  }
  if (!course) return null;

  const lessonCount = course.modules.reduce((n, m) => n + m.lessons.length, 0);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header className="space-y-3">
        <Link href="/catalog" className="text-sm text-text-2 hover:text-text">
          ← Catalog
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-text">{course.title}</h1>
          <p className="mt-1 text-sm text-text-2">{course.description}</p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <Badge tone="accent">{course.language}</Badge>
          <Badge tone="neutral">{course.difficulty}</Badge>
          <span className="text-xs text-text-muted">
            {lessonCount} {lessonCount === 1 ? "lesson" : "lessons"}
          </span>
        </div>
      </header>

      <Card className="space-y-3 p-4">
        <div className="flex items-center justify-between gap-4">
          <div className="min-w-0">
            <p className="text-sm font-medium text-text">
              {course.earned_points} / {course.target_points} pts
            </p>
            <p className="text-xs text-text-2">
              {course.next_task_id
                ? "Pick up where you left off"
                : lessonCount === 0
                  ? "This course has no content yet"
                  : "Everything solved — nice work"}
            </p>
          </div>
          {course.next_task_id && (
            // Ссылка, стилизованная под кнопку, а не <Button> с <Link> внутри:
            // интерактивный элемент внутри интерактивного — недопустимая
            // разметка, и клавиатурная навигация по ней ломается.
            <Link
              href={`/tasks/${course.next_task_id}`}
              className="inline-flex h-8 shrink-0 items-center rounded-md bg-accent px-3 text-xs font-medium text-accent-fg transition-opacity hover:opacity-90"
            >
              Continue
            </Link>
          )}
        </div>
        <ProgressBar
          value={course.earned_points}
          max={course.target_points}
          showBall={course.earned_points > 0}
          label="Course progress"
        />
      </Card>

      {course.modules.length === 0 ? (
        <EmptyState
          icon="📭"
          title="No modules yet"
          description="The author has not added any content to this course."
        />
      ) : (
        <ol className="space-y-5">
          {course.modules.map((m, i) => (
            <li key={m.id} className="space-y-2">
              <h2 className="text-xs font-semibold uppercase tracking-wide text-text-2">
                Module {i + 1} · {m.title}
              </h2>
              {m.lessons.length === 0 ? (
                <p className="rounded-md border border-dashed border-border px-3 py-4 text-center text-xs text-text-muted">
                  No lessons in this module yet
                </p>
              ) : (
                <ul className="overflow-hidden rounded-lg border border-border">
                  {m.lessons.map((l) => (
                    <LessonRow key={l.id} lesson={l} />
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function LessonRow({ lesson }: { lesson: LessonOutline }) {
  const solved = lesson.tasks.filter((t) => t.is_solved).length;

  // Урок считается пройденным по разным признакам в зависимости от того,
  // есть ли в нём задания. `is_completed` пишется только при отметке
  // теоретического урока прочитанным и решением задания не обновляется —
  // если смотреть на него всегда, урок с решёнными заданиями выглядит
  // непройденным, что противоречит счётчику рядом.
  const done = lesson.tasks.length > 0 ? solved === lesson.tasks.length : lesson.is_completed;

  return (
    <li className="border-b border-border last:border-0">
      <div className="flex items-center gap-3 px-3 py-2.5">
        {/* Состояние передано значком и текстом рядом, а не только цветом. */}
        <span
          aria-hidden="true"
          className={done ? "text-success" : "text-text-muted"}
        >
          {done ? "✓" : "○"}
        </span>
        <span className="min-w-0 flex-1 truncate text-sm text-text">{lesson.title}</span>

        {lesson.tasks.length > 0 && (
          <span className="shrink-0 font-mono text-[11px] text-text-muted">
            {solved}/{lesson.tasks.length} tasks
          </span>
        )}

        {lesson.tasks.length > 0 ? (
          <Link
            href={`/tasks/${lesson.tasks.find((t) => !t.is_solved)?.id ?? lesson.tasks[0].id}`}
            className="shrink-0 text-xs text-accent hover:underline"
          >
            {solved === lesson.tasks.length ? "Review" : "Solve"}
          </Link>
        ) : (
          <span className="shrink-0 text-xs text-text-muted">no tasks</span>
        )}
      </div>
    </li>
  );
}

function OutlineSkeleton() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-3">
        <Skeleton variant="text" className="w-24" />
        <Skeleton variant="text" className="h-7 w-1/2" />
        <Skeleton variant="text" className="w-3/4" />
      </div>
      <Skeleton variant="rect" className="h-24 w-full" />
      <Skeleton variant="rect" className="h-40 w-full" />
    </div>
  );
}
