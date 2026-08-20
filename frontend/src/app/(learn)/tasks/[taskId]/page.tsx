"use client";

/**
 * Экран задания — центральный экран продукта.
 *
 * Раскладка: слева условие, справа редактор с результатами тестов. На узких
 * экранах разделение физически не помещается, поэтому переключение вкладками,
 * а кнопки Run и Submit остаются закреплёнными над таб-баром — без этого
 * пришлось бы уходить с вкладки кода, чтобы запустить код.
 *
 * Полный путь `/courses/[id]/lessons/[id]/steps/[id]` появится, когда будет
 * переписан API курсов; сейчас экран открывается по идентификатору задания.
 */

import Link from "next/link";
import { use, useEffect, useState, useSyncExternalStore } from "react";

import CodeWorkspace from "@/components/learn/CodeWorkspace";
import Badge from "@/components/ui/Badge";
import Skeleton from "@/components/ui/Skeleton";
import Tabs from "@/components/ui/Tabs";
import { ErrorState } from "@/components/ui/States";
import { ApiError, api } from "@/lib/api";
import { cn } from "@/lib/cn";
import {
  getThemeServerSnapshot,
  getThemeSnapshot,
  resolveTheme,
  subscribeTheme,
} from "@/lib/theme";

interface TaskLanguage {
  language: string;
  starter_code: string;
  time_limit_ms: number;
  memory_limit_mb: number;
}

interface VisibleTest {
  name: string;
  stdin: string;
  expected_stdout: string;
}

interface TaskDetail {
  id: number;
  prompt: string;
  difficulty: string;
  points_value: number;
  languages: TaskLanguage[];
  visible_tests: VisibleTest[];
  hidden_test_count: number;
}

const MOBILE_TABS = [
  { id: "task", label: "Task", icon: "📖" },
  { id: "code", label: "Code", icon: "💻" },
];

export default function TaskPage({ params }: { params: Promise<{ taskId: string }> }) {
  const { taskId } = use(params);
  const id = Number(taskId);

  const [task, setTask] = useState<TaskDetail | null>(null);
  const [error, setError] = useState<ApiError | Error | null>(null);
  const [tab, setTab] = useState("task");

  // Тема читается из того же внешнего хранилища, что и переключатель:
  // localStorage — внешняя по отношению к React система, и useState с эффектом
  // здесь дал бы каскадный ререндер и расхождение при гидратации.
  const themeSetting = useSyncExternalStore(
    subscribeTheme,
    getThemeSnapshot,
    getThemeServerSnapshot,
  );
  const theme = themeSetting === "system" ? "dark" : resolveTheme(themeSetting);

  useEffect(() => {
    let cancelled = false;
    api<TaskDetail>(`/tasks/${id}`)
      .then((t) => {
        if (!cancelled) setTask(t);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e : new Error("Failed to load"));
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (error) {
    return (
      <div className="mx-auto max-w-md p-8">
        <ErrorState
          title={error instanceof ApiError && error.status === 401 ? "Sign in required" : "Could not load the task"}
          description={error.message}
          onRetry={() => location.reload()}
        />
      </div>
    );
  }

  if (!task) return <LoadingSkeleton />;

  const spec = task.languages[0];
  if (!spec) {
    return (
      <div className="mx-auto max-w-md p-8">
        <ErrorState
          title="Task has no languages configured"
          description="This task cannot be solved yet. Its author needs to add at least one language."
        />
      </div>
    );
  }

  return (
    <>
      <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border px-4">
        <Link href="/catalog" className="text-sm text-text-2 hover:text-text">
          ← Back
        </Link>
        <span className="truncate text-sm font-medium text-text">Task #{task.id}</span>
        <Badge tone="neutral">{task.difficulty}</Badge>
        <Badge tone="accent">{spec.language}</Badge>
        <span className="ml-auto text-xs text-text-2">{task.points_value} pts</span>
      </header>

      {/* Планшет и телефон: вкладки вместо разделённого экрана. */}
      <div className="border-b border-border px-3 py-1.5 lg:hidden">
        <Tabs items={MOBILE_TABS} activeId={tab} onChange={setTab} />
      </div>

      <div className="flex min-h-0 flex-1 lg:divide-x lg:divide-border">
        <section
          className={cn(
            "min-h-0 overflow-y-auto p-4 lg:block lg:w-[42%]",
            tab === "task" ? "block w-full" : "hidden",
          )}
        >
          <TaskBrief task={task} />
        </section>

        <section
          className={cn(
            "flex min-h-0 flex-col lg:flex lg:w-[58%]",
            tab === "code" ? "flex w-full" : "hidden",
          )}
        >
          <CodeWorkspace
            taskId={task.id}
            language={spec.language}
            starterCode={spec.starter_code || ""}
            points={task.points_value}
            visibleTestCount={task.visible_tests.length}
            hiddenTestCount={task.hidden_test_count}
            theme={theme}
          />
        </section>
      </div>
    </>
  );
}

function TaskBrief({ task }: { task: TaskDetail }) {
  return (
    <div className="prose-measure space-y-4">
      <h1 className="text-sm font-semibold uppercase tracking-wide text-text-2">Task</h1>
      <p className="whitespace-pre-wrap text-sm text-text">{task.prompt}</p>

      {task.visible_tests.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-text-2">Examples</h2>
          {task.visible_tests.map((t) => (
            <div key={t.name} className="overflow-hidden rounded-md border border-border">
              <div className="border-b border-border px-2.5 py-1 font-mono text-[11px] text-text-muted">
                {t.name}
              </div>
              <div className="grid grid-cols-2 divide-x divide-border font-mono text-xs">
                <div className="p-2.5">
                  <div className="mb-1 text-[10px] uppercase text-text-muted">input</div>
                  <pre className="overflow-x-auto whitespace-pre-wrap text-text">{t.stdin || "(none)"}</pre>
                </div>
                <div className="p-2.5">
                  <div className="mb-1 text-[10px] uppercase text-text-muted">output</div>
                  <pre className="overflow-x-auto whitespace-pre-wrap text-text">{t.expected_stdout}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {task.hidden_test_count > 0 && (
        <p className="text-xs text-text-muted">
          Plus {task.hidden_test_count} hidden{" "}
          {task.hidden_test_count === 1 ? "test" : "tests"} — checked on Submit.
        </p>
      )}
    </div>
  );
}

/** Скелетон повторяет форму будущего экрана: так нет сдвига, когда данные придут. */
function LoadingSkeleton() {
  return (
    <>
      <div className="flex h-14 shrink-0 items-center gap-3 border-b border-border px-4">
        <Skeleton variant="text" className="w-24" />
      </div>
      <div className="flex min-h-0 flex-1 lg:divide-x lg:divide-border">
        <div className="w-full space-y-3 p-4 lg:w-[42%]">
          <Skeleton variant="text" className="w-1/3" />
          <Skeleton variant="text" className="w-full" />
          <Skeleton variant="text" className="w-5/6" />
          <Skeleton variant="rect" className="h-24 w-full" />
        </div>
        <div className="hidden p-4 lg:block lg:w-[58%]">
          <Skeleton variant="rect" className="h-full min-h-[300px] w-full" />
        </div>
      </div>
    </>
  );
}
