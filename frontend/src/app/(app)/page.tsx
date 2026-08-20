import { redirect } from "next/navigation";

/** Корень ведёт в каталог: своей задачи у него нет, а дашборд ещё не написан. */
export default function Home() {
  redirect("/catalog");
}
