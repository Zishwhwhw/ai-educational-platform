/** Оболочка входа и регистрации: без навигации и без панели наставника. */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4 py-10">
      <div className="w-full max-w-sm">{children}</div>
    </div>
  );
}
