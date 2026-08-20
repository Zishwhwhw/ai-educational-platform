"""Реэкспорт: `from app.models import User` продолжает работать."""

from app.models.auth import (
    RefreshToken,
    Role,
    user_roles,
)
from app.models.course import (
    Course,
    Lesson,
    Module,
    Task,
    TaskLanguage,
    TestCase,
)
from app.models.enums import (
    ContentType,
    ItemType,
    RoleEnum,
    SubmissionStatus,
    SubscriptionEnum,
    TaskDifficulty,
)
from app.models.gamification import (
    Achievement,
    DoubleXPEvent,
    Flashcard,
    StoreItem,
    UserAchievement,
    UserPurchase,
)
from app.models.integrity import (
    AntiFraudLog,
    Appeal,
)
from app.models.learning import (
    PeerReview,
    Progress,
    Submission,
    SubmissionResult,
)
from app.models.social import (
    Clan,
    ClanMember,
    Comment,
    Notification,
    PrivateMessage,
)
from app.models.user import (
    User,
)

__all__ = [
    "Achievement",
    "AntiFraudLog",
    "Appeal",
    "Clan",
    "ClanMember",
    "Comment",
    "ContentType",
    "Course",
    "DoubleXPEvent",
    "Flashcard",
    "ItemType",
    "Lesson",
    "Module",
    "Notification",
    "PeerReview",
    "PrivateMessage",
    "Progress",
    "RefreshToken",
    "Role",
    "RoleEnum",
    "StoreItem",
    "Submission",
    "SubmissionResult",
    "SubmissionStatus",
    "SubscriptionEnum",
    "Task",
    "TaskDifficulty",
    "TaskLanguage",
    "TestCase",
    "User",
    "UserAchievement",
    "UserPurchase",
    "user_roles",
]
