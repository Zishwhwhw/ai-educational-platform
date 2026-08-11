# ==========================================
# File: schemas.py
# Description: ALL Pydantic schemas for API requests/responses
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# === AUTH ===
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str

# === USER ===
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    subscription_tier: str
    points: int
    coins: int
    streak_days: int
    longest_streak: int
    level: str
    avatar_url: str
    bio: str
    github_url: str
    theme: str
    is_shadowbanned: bool
    is_in_trial: bool
    daily_coins_earned: int
    daily_coin_limit: int
    xp_multiplier: float
    focus_mode: bool
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None
    theme: Optional[str] = None
    focus_mode: Optional[bool] = None

# === COURSE ===
class CourseCreate(BaseModel):
    title: str
    description: str
    language: str = "python"
    difficulty: str = "beginner"
    base_price: float = 0.0

class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    language: str
    difficulty: str
    teacher_id: Optional[int]
    is_ai_generated: bool
    is_preinstalled: bool
    base_price: float
    target_points: int
    image_url: str
    class Config:
        from_attributes = True

# === MODULE ===
class ModuleCreate(BaseModel):
    title: str
    order: int = 0

class ModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    order: int
    class Config:
        from_attributes = True

# === LESSON ===
class LessonCreate(BaseModel):
    title: str
    content_type: str = "text"
    content: Optional[str] = None
    video_url: Optional[str] = None
    min_read_time: int = 300
    points_value: int = 5
    order: int = 0

class LessonResponse(BaseModel):
    id: int
    module_id: int
    title: str
    content_type: str
    content: Optional[str]
    video_url: Optional[str]
    min_read_time: int
    points_value: int
    order: int
    class Config:
        from_attributes = True

# === TASK ===
class TaskCreate(BaseModel):
    prompt: str
    difficulty: str = "easy"
    expected_output: Optional[str] = None
    test_cases: Optional[str] = None
    points_value: int = 25

class TaskResponse(BaseModel):
    id: int
    lesson_id: int
    difficulty: str
    prompt: str
    points_value: int
    class Config:
        from_attributes = True

# === SUBMISSION ===
class SubmissionCreate(BaseModel):
    task_id: int
    code: str

class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    code: str
    status: str
    points_awarded: int
    hint_level: int
    feedback: Optional[str]
    class Config:
        from_attributes = True

class HintRequest(BaseModel):
    submission_id: int

class HintResponse(BaseModel):
    hint_level: int
    hint_text: str

# === PROGRESS ===
class ProgressCreate(BaseModel):
    lesson_id: int
    course_id: Optional[int] = None
    time_spent: int = 0

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    is_completed: bool
    points_awarded: int
    time_spent: int
    class Config:
        from_attributes = True

# === ACHIEVEMENT ===
class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    category: str
    required_value: int
    class Config:
        from_attributes = True

class UserAchievementResponse(BaseModel):
    achievement: AchievementResponse
    unlocked_at: datetime
    class Config:
        from_attributes = True

# === STORE ===
class StoreItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price_coins: int
    item_type: str
    image_url: str
    rarity: str
    class Config:
        from_attributes = True

class PurchaseRequest(BaseModel):
    item_id: int

# === COMMENT ===
class CommentCreate(BaseModel):
    lesson_id: int
    content: str
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    content: str
    parent_id: Optional[int]
    created_at: datetime
    class Config:
        from_attributes = True

# === PEER REVIEW ===
class PeerReviewCreate(BaseModel):
    submission_id: int
    score: int
    feedback: str

class PeerReviewResponse(BaseModel):
    id: int
    reviewer_id: int
    submission_id: int
    score: int
    feedback: str
    created_at: datetime
    class Config:
        from_attributes = True

# === CLAN ===
class ClanCreate(BaseModel):
    name: str
    description: str = ""

class ClanResponse(BaseModel):
    id: int
    name: str
    description: str
    max_members: int
    total_points: int
    class Config:
        from_attributes = True

# === FLASHCARD ===
class FlashcardCreate(BaseModel):
    question: str
    answer: str

class FlashcardResponse(BaseModel):
    id: int
    question: str
    answer: str
    next_review: datetime
    interval_days: int
    repetitions: int
    class Config:
        from_attributes = True

class FlashcardReview(BaseModel):
    quality: int  # 0-5 how well the user remembered

# === NOTIFICATION ===
class NotificationResponse(BaseModel):
    id: int
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# === PRIVATE MESSAGE ===
class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

# === LEADERBOARD ===
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    points: int
    level: str
    avatar_url: str
    tier: Optional[str] = None

# === AI ===
class AIPromptRequest(BaseModel):
    prompt: str
    context: str = ""

class AIPromptResponse(BaseModel):
    response: str

class AICourseGenerateRequest(BaseModel):
    topic: str
    language: str = "python"
    difficulty: str = "beginner"
    num_modules: int = 5

class AIResumeCheckRequest(BaseModel):
    resume_text: str

# === APPEAL ===
class AppealCreate(BaseModel):
    reason: str

class AppealResponse(BaseModel):
    id: int
    user_id: int
    reason: str
    status: str
    response: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# === STREAK ===
class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    freeze_remaining: int
    last_activity: Optional[datetime]
