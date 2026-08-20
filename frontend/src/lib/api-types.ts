/** Типы ответов бэкенда. Держатся в одном месте, чтобы расхождение
 *  с сервером ловилось компилятором, а не в браузере. */

export type ExecStatus =
  | "ok"
  | "runtime_error"
  | "compile_error"
  | "timeout"
  | "memory_exceeded"
  | "engine_error";

export interface TestOutcome {
  name: string;
  is_hidden: boolean;
  passed: boolean;
  status: ExecStatus;
  time_ms: number | null;
  /** Для скрытых тестов сервер не присылает содержимое — и после отправки тоже. */
  stdin?: string | null;
  expected_stdout?: string | null;
  actual_stdout?: string | null;
  stderr?: string | null;
}

export interface RunResponse {
  passed_count: number;
  total_count: number;
  outcomes: TestOutcome[];
  compile_output: string;
  engine_available: boolean;
}

export interface SubmissionResponse {
  id: number;
  task_id: number;
  language: string;
  status: "correct" | "incorrect" | "flagged";
  tests_passed: number;
  tests_total: number;
  score: number;
  points_awarded: number;
  attempt_number: number;
  submitted_at: string;
  outcomes: TestOutcome[];
  compile_output: string;
}

export interface ApiErrorBody {
  error: { code: string; message: string; request_id?: string };
}

export interface CourseCard {
  id: number;
  title: string;
  description: string;
  language: string;
  difficulty: string;
  is_preinstalled: boolean;
  target_points: number;
  image_url: string;
  lesson_count: number;
  earned_points: number;
}

export interface TaskOutline {
  id: number;
  difficulty: string;
  points_value: number;
  is_solved: boolean;
}

export interface LessonOutline {
  id: number;
  title: string;
  content_type: string;
  points_value: number;
  order: number;
  is_completed: boolean;
  tasks: TaskOutline[];
}

export interface CourseOutline {
  id: number;
  title: string;
  description: string;
  language: string;
  difficulty: string;
  target_points: number;
  earned_points: number;
  modules: { id: number; title: string; order: number; lessons: LessonOutline[] }[];
  /** Первое нерешённое задание — цель кнопки Continue. */
  next_task_id: number | null;
}

export interface HintState {
  failed_attempts: number;
  revealed_level: number;
  next_level: number | null;
  next_unlocks_after_failures: number | null;
  next_reward_multiplier: number | null;
}
