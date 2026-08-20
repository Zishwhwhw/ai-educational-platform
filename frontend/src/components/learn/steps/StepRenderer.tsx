"use client";

/**
 * Отрисовка одного шага урока.
 *
 * Диспетчер по строковому типу. Неизвестный тип не роняет страницу и не
 * показывает пустоту: клиент может встретить тип, которого не знает его
 * версия сборки, и должен честно сказать об этом.
 */

import { useCallback, useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { ApiError, api } from "@/lib/api";
import type { LessonStep, StepAnswerResponse } from "@/lib/api-types";

import { ChoiceStep, InputStep, TextStep, VideoStep, type Answer } from "./inputs";
import { MatchingStep, OrderingStep } from "./interactive";

const PASSIVE = new Set(["text", "video"]);

export default function StepRenderer({
  step,
  onCompleted,
}: {
  step: LessonStep;
  onCompleted?: (result: StepAnswerResponse) => void;
}) {
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [result, setResult] = useState<StepAnswerResponse | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const passive = PASSIVE.has(step.type);

  const submit = useCallback(async () => {
    setPending(true);
    setError(null);
    try {
      const res = await api<StepAnswerResponse>(`/steps/${step.id}/answer`, {
        method: "POST",
        json: { answer: answer ?? {} },
      });
      setResult(res);
      onCompleted?.(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not submit the answer");
    } finally {
      setPending(false);
    }
  }, [answer, onCompleted, step.id]);

  const props = { content: step.content, disabled: pending, onChange: setAnswer };

  let body: React.ReactNode;
  switch (step.type) {
    case "text":
      body = <TextStep content={step.content} />;
      break;
    case "video":
      body = <VideoStep content={step.content} />;
      break;
    case "choice_single":
      body = <ChoiceStep {...props} multiple={false} />;
      break;
    case "choice_multiple":
      body = <ChoiceStep {...props} multiple />;
      break;
    case "input_string":
      body = <InputStep {...props} numeric={false} />;
      break;
    case "input_number":
      body = <InputStep {...props} numeric />;
      break;
    case "matching":
      body = <MatchingStep {...props} />;
      break;
    case "ordering":
      body = <OrderingStep {...props} />;
      break;
    case "code":
      // Задание на код живёт на своём экране: там нужен редактор,
      // песочница и панель тестов.
      body = (
        <p className="text-sm text-text-2">
          This step is a coding task —{" "}
          <a href={`/tasks/${step.content.task_id}`} className="text-accent hover:underline">
            open the editor
          </a>
          .
        </p>
      );
      break;
    default:
      body = (
        <p className="rounded-md border border-warning/40 px-3 py-2 text-sm text-text-2">
          This step type is not supported by your version of the app. Reload the page
          to get the latest version.
        </p>
      );
  }

  const canSubmit = passive || answer !== null;

  return (
    <section className="space-y-3 rounded-lg border border-border bg-surface p-4">
      <header className="flex items-center gap-2">
        <span className="font-mono text-[11px] uppercase text-text-muted">
          {step.type.replace("_", " ")}
        </span>
        {step.is_completed && <Badge tone="success" icon="✓">completed</Badge>}
        <span className="ml-auto text-[11px] text-text-muted">{step.points_value} pts</span>
      </header>

      {body}

      {error && (
        <p role="alert" className="text-xs text-danger">
          {error}
        </p>
      )}

      {step.type !== "code" && step.type in STEP_LABELS && (
        <div className="flex items-center gap-3">
          <Button size="sm" onClick={submit} loading={pending} disabled={!canSubmit}>
            {STEP_LABELS[step.type]}
          </Button>

          {result && (
            // Итог объявляется вслух: цвет и значок скринридер не передаёт.
            <p aria-live="polite" className="text-xs">
              <span className={result.is_correct ? "text-success" : "text-danger"}>
                {result.is_correct ? "✓ correct" : "✗ not correct"}
              </span>
              <span className="text-text-muted">
                {" · "}
                {result.points_awarded} of {step.points_value} pts
                {result.detail?.matched != null &&
                  ` · ${result.detail.matched}/${result.detail.total} matched`}
                {result.detail?.in_place != null &&
                  ` · ${result.detail.in_place}/${result.detail.total} in place`}
              </span>
            </p>
          )}
        </div>
      )}
    </section>
  );
}

const STEP_LABELS: Record<string, string> = {
  text: "Mark as read",
  video: "Mark as watched",
  choice_single: "Check answer",
  choice_multiple: "Check answer",
  input_string: "Check answer",
  input_number: "Check answer",
  matching: "Check answer",
  ordering: "Check answer",
};
