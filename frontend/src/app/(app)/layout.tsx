import AISidebar from "@/components/AISidebar";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";

/** Оболочка основного приложения: навигация, шапка, панель наставника. */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex min-w-0 flex-1 flex-col">
        <Header />
        <div className="flex-1 overflow-y-auto p-6">{children}</div>
      </main>
      <AISidebar />
    </div>
  );
}
