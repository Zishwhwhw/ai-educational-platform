import AuthForm from "@/components/auth/AuthForm";

export const metadata = { title: "Sign in — OverCoding" };

export default function LoginPage() {
  return <AuthForm mode="login" />;
}
