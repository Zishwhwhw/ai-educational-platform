"use client";

/**
 * Общая форма входа и регистрации.
 *
 * Ошибки показываются на конкретном поле, а не одной строкой сверху: сервер
 * возвращает `fields` с указанием, что именно не прошло, и терять эту
 * точность ради простоты не стоит — «проверьте данные» никому не помогает.
 */

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { ApiError, API_BASE } from "@/lib/api";
import { storeSession, type Session } from "@/lib/auth";

type Mode = "login" | "register";

interface FieldError {
  loc: (string | number)[];
  msg: string;
}

export default function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const isRegister = mode === "register";

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setPending(true);
    setFormError(null);
    setFieldErrors({});

    try {
      // Запрос идёт мимо общего клиента: тот при 401 пробует обменять refresh
      // и чистит сессию. На странице входа обменивать нечего, а очистка стёрла
      // бы сообщение об ошибке.
      const res = await fetch(`${API_BASE}${isRegister ? "/auth/register" : "/auth/login"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(isRegister ? { username, email, password } : { email, password }),
      });
      const body = await res.json().catch(() => null);

      if (!res.ok) {
        const err = body?.error;
        const fields: FieldError[] | undefined = err?.fields;
        if (Array.isArray(fields)) {
          setFieldErrors(
            Object.fromEntries(fields.map((f) => [String(f.loc[f.loc.length - 1]), f.msg])),
          );
          setFormError("Please check the highlighted fields");
        } else {
          setFormError(err?.message ?? `Request failed with ${res.status}`);
        }
        return;
      }

      storeSession(body as Session);
      router.push("/catalog");
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Could not reach the server");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="text-center">
        <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-sm font-bold text-accent-fg">
          OC
        </div>
        <h1 className="text-xl font-bold text-text">
          {isRegister ? "Create your account" : "Sign in to OverCoding"}
        </h1>
        <p className="mt-1 text-sm text-text-2">
          {isRegister
            ? "Start writing code from the first lesson."
            : "Pick up where you left off."}
        </p>
      </header>

      <form onSubmit={submit} className="space-y-4" noValidate>
        {isRegister && (
          <Input
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            hint="3–32 characters: letters, digits, - and _"
            error={fieldErrors.username}
            required
          />
        )}
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          error={fieldErrors.email}
          required
        />
        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={isRegister ? "new-password" : "current-password"}
          hint={isRegister ? "At least 8 characters" : undefined}
          error={fieldErrors.password}
          required
        />

        {formError && (
          <p role="alert" className="text-xs text-danger">
            {formError}
          </p>
        )}

        <Button type="submit" fullWidth loading={pending}>
          {isRegister ? "Create account" : "Sign in"}
        </Button>
      </form>

      <p className="text-center text-xs text-text-2">
        {isRegister ? "Already have an account? " : "New here? "}
        <Link href={isRegister ? "/login" : "/register"} className="text-accent hover:underline">
          {isRegister ? "Sign in" : "Create an account"}
        </Link>
      </p>
    </div>
  );
}
