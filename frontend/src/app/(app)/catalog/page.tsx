"use client";

/**
 * Каталог курсов.
 *
 * Заменяет `library`, где список из шести курсов был захардкожен прямо в файле,
 * а фильтрация работала по этому массиву. Здесь данные приходят из API,
 * и экран нарисован во всех четырёх состояниях, а не только в «данные есть».
 */

import Link from "next/link";
import { useMemo, useState } from "react";

import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import ProgressBar from "@/components/ui/ProgressBar";
import Skeleton from "@/components/ui/Skeleton";
import { EmptyState, ErrorState } from "@/components/ui/States";
import type { CourseCard as Course } from "@/lib/api-types";
import { useApi } from "@/lib/useApi";

export default function CatalogPage() {
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState<string>("all");

  const { data, error, loading, reload } = useApi<Course[]>("/courses/");

  const languages = useMemo(
    () => ["all", ...Array.from(new Set((data ?? []).map((c) => c.language))).sort()],
    [data],
  );

  // Фильтрация на клиенте оправдана, пока курсов десятки: сервер поддерживает
  // те же параметры, и при росте каталога фильтры переезжают в запрос.
  const shown = (data ?? []).filter(
    (c) =>
      (language === "all" || c.language === language) &&
      (search === "" ||
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        c.description.toLowerCase().includes(search.toLowerCase())),
  );

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-text">Catalog</h1>
        <p className="mt-1 text-sm text-text-2">
          Pick a course and start writing code. Progress is saved automatically.
        </p>
      </header>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="sm:w-80">
          <Input
            label="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Course name or topic"
          />
        </div>
        {languages.length > 2 && (
          <div className="flex flex-wrap gap-1.5 pb-1">
            {languages.map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => setLanguage(l)}
                aria-pressed={language === l}
                className={
                  language === l
                    ? "rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-fg"
                    : "rounded-md border border-border px-2.5 py-1 text-xs text-text-2 hover:text-text"
                }
              >
                {l}
              </button>
            ))}
          </div>
        )}
      </div>

      {loading && <CardGridSkeleton />}

      {error && (
        <ErrorState
          title="Could not load the catalog"
          description={error.message}
          onRetry={reload}
        />
      )}

      {!loading && !error && shown.length === 0 && (
        <EmptyState
          icon="📚"
          title={data?.length ? "Nothing matches your search" : "No courses yet"}
          description={
            data?.length
              ? "Try a different keyword or clear the language filter."
              : "Courses will appear here once they are published."
          }
          actionLabel={data?.length ? "Clear search" : undefined}
          onAction={
            data?.length
              ? () => {
                  setSearch("");
                  setLanguage("all");
                }
              : undefined
          }
        />
      )}

      {shown.length > 0 && (
        <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {shown.map((c) => (
            <li key={c.id}>
              <CourseTile course={c} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CourseTile({ course }: { course: Course }) {
  const started = course.earned_points > 0;
  return (
    <Link href={`/courses/${course.id}`} className="block">
      <Card interactive elevation="raised" className="flex h-full flex-col gap-3 p-4">
        <div className="flex items-start gap-2">
          <h2 className="min-w-0 flex-1 text-sm font-semibold text-text">{course.title}</h2>
          {course.is_preinstalled && <Badge tone="neutral">official</Badge>}
        </div>

        <p className="line-clamp-2 flex-1 text-xs text-text-2">{course.description}</p>

        <div className="flex flex-wrap items-center gap-1.5">
          <Badge tone="accent">{course.language}</Badge>
          <Badge tone="neutral">{course.difficulty}</Badge>
          <span className="ml-auto text-[11px] text-text-muted">
            {course.lesson_count} {course.lesson_count === 1 ? "lesson" : "lessons"}
          </span>
        </div>

        <div className="space-y-1.5">
          <ProgressBar
            value={course.earned_points}
            max={course.target_points}
            showBall={started}
            label={`${course.title} progress`}
          />
          <p className="text-[11px] text-text-muted">
            {started
              ? `${course.earned_points} / ${course.target_points} pts`
              : `${course.target_points} pts to complete`}
          </p>
        </div>
      </Card>
    </Link>
  );
}

/** Скелетон повторяет сетку карточек, чтобы макет не прыгнул при загрузке. */
function CardGridSkeleton() {
  return (
    <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <li key={i}>
          <Card className="space-y-3 p-4">
            <Skeleton variant="text" className="w-2/3" />
            <Skeleton variant="text" className="w-full" />
            <Skeleton variant="text" className="w-1/2" />
            <Skeleton variant="rect" className="h-1.5 w-full" />
          </Card>
        </li>
      ))}
    </ul>
  );
}
