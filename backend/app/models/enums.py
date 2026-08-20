import enum


class RoleEnum(enum.StrEnum):
    """Роли аддитивны: преподаватель обязан быть и учеником.

    Поэтому связь пользователь↔роль — many-to-many (таблица `user_roles`),
    а не одна колонка. Решение B4 от 2026-08-20.
    """

    student = "student"
    teacher = "teacher"
    moderator = "moderator"
    admin = "admin"
    owner = "owner"


class SubscriptionEnum(enum.StrEnum):
    free = "free"
    basic = "basic"
    advanced = "advanced"
    premium = "premium"


class SubmissionStatus(enum.StrEnum):
    pending = "pending"
    correct = "correct"
    incorrect = "incorrect"
    flagged = "flagged"


class TaskDifficulty(enum.StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ContentType(enum.StrEnum):
    text = "text"
    video = "video"
    quiz = "quiz"
    task = "task"


class ItemType(enum.StrEnum):
    theme = "theme"
    avatar = "avatar"
    badge = "badge"
    background = "background"
