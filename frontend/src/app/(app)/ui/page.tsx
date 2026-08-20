"use client";

/**
 * Витрина дизайн-системы.
 *
 * Нужна, чтобы примитивы можно было увидеть во всех состояниях сразу и в обеих
 * темах — иначе состояния вроде loading, error и disabled проверяются только
 * случайно, когда до них доберётся реальный сценарий.
 *
 * Служебная страница: из навигации не ведёт ссылок, перед публичным запуском
 * либо убирается, либо закрывается для роли, отличной от admin.
 */

import { useState } from "react";

import {
  Badge,
  Button,
  Card,
  Dialog,
  EmptyState,
  ErrorState,
  Input,
  ProgressBar,
  Skeleton,
  Tabs,
} from "@/components/ui";

function Section({ title, note, children }: { title: string; note?: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-3">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-text-2">{title}</h2>
        {note && <p className="mt-0.5 text-xs text-text-muted">{note}</p>}
      </div>
      <div className="flex flex-wrap items-start gap-3">{children}</div>
    </section>
  );
}

export default function UiShowcase() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tab, setTab] = useState("task");

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-10 py-4">
      <header>
        <h1 className="text-2xl font-bold text-text">OverCoding UI</h1>
        <p className="mt-1 text-sm text-text-2">
          Design system primitives. Switch the theme in the header — every element must stay
          legible in both.
        </p>
      </header>

      <Section title="Buttons">
        <Button>Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="danger">Danger</Button>
        <Button loading>Loading</Button>
        <Button disabled>Disabled</Button>
        <Button size="sm">Small</Button>
        <Button size="lg">Large</Button>
      </Section>

      <Section title="Run and Submit" note="Разный вид намеренно: Submit расходует попытку, Run — нет">
        <Button variant="secondary" iconLeft="▸">
          Run
        </Button>
        <Button>Submit</Button>
      </Section>

      <Section title="Inputs">
        <div className="w-64">
          <Input label="Email" placeholder="you@example.com" />
        </div>
        <div className="w-64">
          <Input label="Username" hint="3–32 characters, letters and digits" />
        </div>
        <div className="w-64">
          <Input label="Password" type="password" error="Password is too short" />
        </div>
        <div className="w-64">
          <Input label="Disabled" disabled placeholder="Not editable" />
        </div>
      </Section>

      <Section title="Test result badges" note="Статус дублируется значком и текстом, не только цветом">
        <Badge tone="success" icon="✓">
          passed
        </Badge>
        <Badge tone="danger" icon="✗">
          failed
        </Badge>
        <Badge tone="neutral" icon="●">
          hidden
        </Badge>
        <Badge tone="warning" icon="⏱">
          timeout
        </Badge>
        <Badge tone="accent">Python</Badge>
      </Section>

      <Section title="Progress">
        <div className="w-72">
          <ProgressBar value={430} max={1700} label="Course progress" showBall />
          <p className="mt-2 text-xs text-text-2">430 / 1700 pts</p>
        </div>
        <div className="w-72">
          <ProgressBar value={100} max={100} label="Complete" />
        </div>
      </Section>

      <Section title="Cards">
        <Card className="w-64 p-4">
          <p className="text-sm font-medium text-text">Static card</p>
          <p className="mt-1 text-xs text-text-2">Flat surface</p>
        </Card>
        <Card interactive elevation="raised" className="w-64 p-4">
          <p className="text-sm font-medium text-text">Interactive card</p>
          <p className="mt-1 text-xs text-text-2">Lifts on hover</p>
        </Card>
      </Section>

      <Section title="Tabs" note="Стрелки, Home и End работают с клавиатуры">
        <Tabs
          items={[
            { id: "task", label: "Task", icon: "📖" },
            { id: "code", label: "Code", icon: "💻" },
            { id: "tests", label: "Tests", icon: "✓" },
          ]}
          activeId={tab}
          onChange={setTab}
        />
      </Section>

      <Section title="Loading">
        <div className="flex w-72 flex-col gap-2">
          <Skeleton variant="text" className="w-2/3" />
          <Skeleton variant="text" className="w-full" />
          <Skeleton variant="rect" className="h-20 w-full" />
        </div>
      </Section>

      <Section title="Empty and error states">
        <div className="w-full">
          <EmptyState
            icon="📚"
            title="No courses yet"
            description="Browse the catalog to enroll in your first course."
            actionLabel="Browse catalog"
            onAction={() => undefined}
          />
        </div>
        <div className="w-full">
          <ErrorState
            description="Could not load your progress."
            onRetry={() => undefined}
          />
        </div>
      </Section>

      <Section title="Dialog" note="Необратимое действие — подтверждение обязательно">
        <Button variant="secondary" onClick={() => setDialogOpen(true)}>
          Reveal hint 3 of 5
        </Button>
        <Dialog
          open={dialogOpen}
          title="Reveal hint 3 of 5?"
          description="Shows where the error is. Final reward drops 40 → 32 pts. This cannot be undone."
          confirmLabel="Reveal hint 3"
          onConfirm={() => setDialogOpen(false)}
          onClose={() => setDialogOpen(false)}
        />
      </Section>
    </div>
  );
}
