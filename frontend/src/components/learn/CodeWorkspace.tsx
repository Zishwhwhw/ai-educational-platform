"use client";

import Editor, { type Monaco } from "@monaco-editor/react";
import { useCallback, useEffect, useRef, useState } from "react";

import Button from "@/components/ui/Button";
import HintPanel from "@/components/learn/HintPanel";
import TestResultsPanel from "@/components/learn/TestResultsPanel";
import Tabs from "@/components/ui/Tabs";
import { ApiError, api } from "@/lib/api";
import type { HintState, RunResponse, SubmissionResponse, TestOutcome } from "@/lib/api-types";
import { cn } from "@/lib/cn";

/**
 * Рабочая область задания: редактор, запуск, отправка, результаты тестов.
 *
 * Ключевое различие, которое обязано читаться в интерфейсе:
 *   Run    — черновой прогон, только видимые тесты, попытка не расходуется.
 *   Submit — зачёт, все тесты включая скрытые, расходует попытку и даёт баллы.
 * Поэтому Run вторичная кнопка, Submit основная, и у Submit есть подтверждение.
 */

const DRAFT_TTL_MS = 1000 * 60 * 60 * 24 * 30;

function draftKey(taskId: number, language: string) {
  return `oc-draft:${taskId}:${language}`;
}

function loadDraft(taskId: number, language: string): string | null {
  try {
    const raw = localStorage.getItem(draftKey(taskId, language));
    if (!raw) return null;
    const { code, at } = JSON.parse(raw) as { code: string; at: number };
    return Date.now() - at > DRAFT_TTL_MS ? null : code;
  } catch {
    return null;
  }
}

export interface CodeWorkspaceProps {
  taskId: number;
  language: string;
  starterCode: string;
  points: number;
  visibleTestCount: number;
  hiddenTestCount: number;
  theme?: "light" | "dark";
  onSolved?: (submission: SubmissionResponse) => void;
}

type Phase = "idle" | "running" | "submitting";

export default function CodeWorkspace({
  taskId,
  language,
  starterCode,
  points,
  visibleTestCount,
  hiddenTestCount,
  theme = "dark",
  onSolved,
}: CodeWorkspaceProps) {
  const [code, setCode] = useState(starterCode);
  // Ключ, для которого черновик уже подхвачен. Состояние правится во время
  // рендера — это документированный React-приём «подстроить состояние под
  // изменившиеся пропсы». Через эффект пришлось бы отрисовать сначала
  // стартовый код, а потом заменить его черновиком, то есть мигнуть.
  const [draftLoadedFor, setDraftLoadedFor] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [outcomes, setOutcomes] = useState<TestOutcome[]>([]);
  const [passed, setPassed] = useState(0);
  const [total, setTotal] = useState(0);
  const [compileOutput, setCompileOutput] = useState("");
  const [awarded, setAwarded] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submittedOnce, setSubmittedOnce] = useState(false);
  const [lastSubmissionId, setLastSubmissionId] = useState<number | null>(null);
  const [bottomTab, setBottomTab] = useState("tests");
  const [hintState, setHintState] = useState<HintState | null>(null);

  // Состояние лестницы перезапрашивается после каждой отправки и после
  // раскрытия: от него зависит, какая ступень доступна и сколько она стоит.
  const refreshHints = useCallback(() => {
    api<HintState>(`/hints/task/${taskId}`)
      .then(setHintState)
      .catch(() => setHintState(null));
  }, [taskId]);

  // Автосохранение с задержкой: сохранять на каждое нажатие клавиши незачем,
  // а потерять написанное — самое болезненное, что может сделать учебный продукт.
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      try {
        localStorage.setItem(draftKey(taskId, language), JSON.stringify({ code, at: Date.now() }));
      } catch {
        // приватный режим
      }
    }, 500);
    return () => {
      if (saveTimer.current) clearTimeout(saveTimer.current);
    };
  }, [code, taskId, language]);

  const draftKeyForTask = `${taskId}:${language}`;
  if (typeof window !== "undefined" && draftLoadedFor !== draftKeyForTask) {
    setDraftLoadedFor(draftKeyForTask);
    const draft = loadDraft(taskId, language);
    if (draft != null && draft !== code) setCode(draft);
  }

  const busy = phase !== "idle";

  const run = useCallback(async () => {
    setPhase("running");
    setError(null);
    setCompileOutput("");
    setAwarded(null);
    try {
      const res = await api<RunResponse>("/submissions/run", {
        method: "POST",
        json: { task_id: taskId, language, source: code },
      });
      setOutcomes(res.outcomes);
      setPassed(res.passed_count);
      setTotal(res.total_count);
      setCompileOutput(res.compile_output);
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.isRetryable
            ? `${e.message} You can try again.`
            : e.message
          : "Network error",
      );
    } finally {
      setPhase("idle");
    }
  }, [code, language, taskId]);

  const submit = useCallback(async () => {
    setPhase("submitting");
    setError(null);
    setCompileOutput("");
    try {
      const res = await api<SubmissionResponse>("/submissions/", {
        method: "POST",
        json: { task_id: taskId, language, source: code },
      });
      setOutcomes(res.outcomes);
      setPassed(res.tests_passed);
      setTotal(res.tests_total);
      setCompileOutput(res.compile_output);
      setAwarded(res.points_awarded);
      setSubmittedOnce(true);
      setLastSubmissionId(res.id);
      refreshHints();
      if (res.status === "correct") onSolved?.(res);
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.isRetryable
            ? `${e.message} Your attempt was not counted.`
            : e.message
          : "Network error",
      );
    } finally {
      setPhase("idle");
    }
  }, [code, language, onSolved, refreshHints, taskId]);

  // Горячие клавиши регистрируются в Monaco, а не на документе: иначе они
  // срабатывали бы и когда фокус вне редактора.
  const onMount = useCallback(
    (editor: Parameters<NonNullable<React.ComponentProps<typeof Editor>["onMount"]>>[0], monaco: Monaco) => {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => void run());
      editor.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter,
        () => void submit(),
      );
    },
    [run, submit],
  );

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="font-mono text-xs text-text-2">
          main.{language === "python" ? "py" : language}
        </span>
        <button
          type="button"
          onClick={() => setCode(starterCode)}
          className="text-xs text-text-muted hover:text-text"
        >
          Reset to starter
        </button>
      </div>

      <div className="min-h-[220px] flex-1">
        <Editor
          height="100%"
          language={language}
          theme={theme === "dark" ? "vs-dark" : "light"}
          value={code}
          onChange={(v) => setCode(v ?? "")}
          onMount={onMount}
          loading={<div className="p-4 text-xs text-text-muted">Loading editor…</div>}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: "var(--font-jetbrains-mono), ui-monospace, monospace",
            padding: { top: 12 },
            scrollBeyondLastLine: false,
            tabSize: 4,
            renderLineHighlight: "line",
            automaticLayout: true,
          }}
        />
      </div>

      <div className="flex items-center gap-2 border-y border-border px-3 py-2">
        <Button variant="secondary" size="sm" iconLeft="▸" onClick={run} loading={phase === "running"} disabled={busy}>
          Run
        </Button>
        <Button size="sm" onClick={submit} loading={phase === "submitting"} disabled={busy}>
          Submit
        </Button>
        <span className="ml-auto hidden text-xs text-text-muted sm:block">
          ⌘↵ run · ⌘⇧↵ submit
        </span>
      </div>

      {error && (
        <p role="alert" className="border-b border-danger/40 bg-danger/5 px-3 py-2 text-xs text-danger">
          {error}
        </p>
      )}

      <div className="border-b border-border px-2 py-1">
        <Tabs
          items={[
            { id: "tests", label: "Tests", icon: "✓" },
            { id: "hints", label: "Hints", icon: "💡" },
          ]}
          activeId={bottomTab}
          onChange={setBottomTab}
        />
      </div>

      <div
        className={cn(
          "min-h-0 flex-1 overflow-y-auto",
          bottomTab === "hints" && "hidden",
          outcomes.length === 0 && "flex-none",
        )}
      >
        <TestResultsPanel
          outcomes={outcomes}
          passedCount={passed}
          totalCount={total}
          hiddenPending={submittedOnce ? 0 : hiddenTestCount}
          compileOutput={compileOutput}
          points={awarded ?? undefined}
          maxPoints={awarded != null ? points : undefined}
          empty={
            visibleTestCount > 0
              ? `Run to check ${visibleTestCount} visible ${visibleTestCount === 1 ? "test" : "tests"}`
              : "Submit to check the hidden tests"
          }
        />
      </div>

      <div className={cn("min-h-0 flex-1 overflow-y-auto", bottomTab === "tests" && "hidden")}>
        <HintPanel
          submissionId={lastSubmissionId}
          points={points}
          state={hintState}
          onStateChange={refreshHints}
        />
      </div>
    </div>
  );
}
