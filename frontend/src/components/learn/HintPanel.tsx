"use client";

/**
 * Лестница подсказок.
 *
 * Ступени необратимы и стоят баллов, поэтому интерфейс подчинён одному правилу:
 * **цена называется до раскрытия, а не после.** Переход требует двух действий —
 * нажать «Reveal» и подтвердить в диалоге, где написан штраф и сказано, что
 * отменить нельзя. Случайный клик не должен стоить ученику награды.
 *
 * Раскрытые ступени остаются на экране: к ним возвращаются.
 */

import { useCallback, useState } from "react";

import Button from "@/components/ui/Button";
import Dialog from "@/components/ui/Dialog";
import { ApiError, api } from "@/lib/api";

interface HintState {
  failed_attempts: number;
  revealed_level: number;
  next_level: number | null;
  next_unlocks_after_failures: number | null;
  next_reward_multiplier: number | null;
}

interface Hint {
  level: number;
  text: string;
  generated: boolean;
  reward_multiplier: number;
  max_level: number;
}

export default function HintPanel({
  submissionId,
  points,
  state,
  onStateChange,
}: {
  /** Подсказки привязаны к отправке: без неё разбирать нечего. */
  submissionId: number | null;
  points: number;
  state: HintState | null;
  onStateChange: () => void;
}) {
  const [revealed, setRevealed] = useState<Hint[]>([]);
  const [pending, setPending] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const next = state?.next_level ?? null;
  const unlocked =
    state != null &&
    next != null &&
    state.next_unlocks_after_failures != null &&
    state.failed_attempts >= state.next_unlocks_after_failures;

  const doReveal = useCallback(async () => {
    if (submissionId == null || next == null) return;
    setConfirming(false);
    setPending(true);
    setError(null);
    try {
      const hint = await api<Hint>("/hints/reveal", {
        method: "POST",
        json: { submission_id: submissionId, level: next },
      });
      setRevealed((prev) => [...prev, hint]);
      onStateChange();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not load the hint");
    } finally {
      setPending(false);
    }
  }, [next, onStateChange, submissionId]);

  if (submissionId == null) {
    return (
      <p className="px-3 py-4 text-center text-xs text-text-muted">
        Submit an attempt first — hints are based on your code.
      </p>
    );
  }

  const currentReward = revealed.length
    ? revealed[revealed.length - 1].reward_multiplier
    : 1;

  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-text-2">Hints</span>
        <span className="font-mono text-[11px] text-text-muted">
          {state?.revealed_level ?? 0} of 5
        </span>
      </div>

      <ol className="divide-y divide-border">
        {revealed.map((h) => (
          <li key={h.level} className="px-3 py-2.5">
            <div className="mb-1 flex items-center gap-2">
              <span className="font-mono text-[11px] text-text-muted">Hint {h.level}</span>
              {h.generated && (
                <span className="rounded border border-border px-1.5 py-px text-[10px] text-text-muted">
                  AI tutor
                </span>
              )}
            </div>
            <p className="whitespace-pre-wrap text-xs text-text">{h.text}</p>
          </li>
        ))}
      </ol>

      {error && (
        <p role="alert" className="px-3 py-2 text-xs text-danger">
          {error}
        </p>
      )}

      <div className="px-3 py-2.5">
        {next == null ? (
          <p className="text-xs text-text-muted">All hints revealed.</p>
        ) : unlocked ? (
          <>
            <Button
              size="sm"
              variant="secondary"
              fullWidth
              loading={pending}
              onClick={() => setConfirming(true)}
            >
              Reveal hint {next} of 5
            </Button>
            {/* Штраф назван до раскрытия, а не после. */}
            <p className="mt-1.5 text-center text-[11px] text-text-muted">
              {state?.next_reward_multiplier === 0
                ? "Shows the full solution — the reward drops to 0"
                : `Reward drops to ${Math.round(
                    points * (state?.next_reward_multiplier ?? 1),
                  )} of ${points} pts`}
            </p>
          </>
        ) : (
          <p className="text-center text-xs text-text-muted">
            Hint {next} unlocks after{" "}
            {(state?.next_unlocks_after_failures ?? 0) - (state?.failed_attempts ?? 0)} more
            failed {(state?.next_unlocks_after_failures ?? 0) - (state?.failed_attempts ?? 0) === 1
              ? "attempt"
              : "attempts"}
          </p>
        )}
      </div>

      <Dialog
        open={confirming}
        title={`Reveal hint ${next} of 5?`}
        description={
          state?.next_reward_multiplier === 0
            ? `This shows the full solution. The reward for this task drops from ${points} to 0 pts. This cannot be undone.`
            : `The reward for this task drops from ${points} to ${Math.round(
                points * (state?.next_reward_multiplier ?? 1),
              )} pts. This cannot be undone.`
        }
        confirmLabel={`Reveal hint ${next}`}
        destructive={state?.next_reward_multiplier === 0}
        onConfirm={doReveal}
        onClose={() => setConfirming(false)}
      />

      {currentReward < 1 && (
        <p className="border-t border-border px-3 py-1.5 text-[11px] text-text-muted">
          Current reward: {Math.round(points * currentReward)} of {points} pts
        </p>
      )}
    </div>
  );
}
