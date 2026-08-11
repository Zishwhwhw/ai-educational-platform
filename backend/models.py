# ==========================================
# File: models.py
# Description: ALL SQLAlchemy models for the platform (30+ features)
# Author: AI Agent
# Created: 2026-08-02
# Changes:
#   - 2026-08-02: Initial creation
#   - 2026-08-02: Expanded with ALL tables for full platform
# ==========================================

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

from database import Base

# === ENUMS ===
class RoleEnum(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    owner = "owner"

class SubscriptionEnum(str, enum.Enum):
    free = "free"
    basic = "basic"
    advanced = "advanced"
    premium = "premium"

class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    correct = "correct"
    incorrect = "incorrect"
    flagged = "flagged"

class TaskDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class ContentType(str, enum.Enum):
    text = "text"
    video = "video"
    quiz = "quiz"
    task = "task"

class ItemType(str, enum.Enum):
    theme = "theme"
    avatar = "avatar"
    badge = "badge"
    background = "background"

# === MODELS ===

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student")
    subscription_tier = Column(String, default="free")
    points = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    xp_multiplier = Column(Float, default=1.0)
    streak_days = Column(Integer, default=0)
    streak_freeze_count = Column(Integer, default=2)
    longest_streak = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_shadowbanned = Column(Boolean, default=False)
    is_in_trial = Column(Boolean, default=True)
    trial_end_date = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    daily_coins_earned = Column(Integer, default=0)
    daily_coin_limit = Column(Integer, default=100)
    avatar_url = Column(String, default="")
    bio = Column(Text, default="")
    github_url = Column(String, default="")
    theme = Column(String, default="dark")
    level = Column(String, default="Junior")
    clan_id = Column(Integer, ForeignKey("clans.id"), nullable=True)
    focus_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    courses_taught = relationship("Course", back_populates="teacher")
    progress = relationship("Progress", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    purchases = relationship("UserPurchase", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")
    sent_messages = relationship("PrivateMessage", foreign_keys="PrivateMessage.sender_id", back_populates="sender")
    received_messages = relationship("PrivateMessage", foreign_keys="PrivateMessage.receiver_id", back_populates="receiver")
    comments = relationship("Comment", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    language = Column(String, default="python")
    difficulty = Column(String, default="beginner")
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_ai_generated = Column(Boolean, default=False)
    is_preinstalled = Column(Boolean, default=False)
    base_price = Column(Float, default=0.0)
    target_points = Column(Integer, default=1700)
    image_url = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="courses_taught")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    order = Column(Integer)
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    title = Column(String)
    content_type = Column(String, default="text")
    content = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    min_read_time = Column(Integer, default=300)
    points_value = Column(Integer, default=5)
    order = Column(Integer, default=0)
    module = relationship("Module", back_populates="lessons")
    tasks = relationship("Task", back_populates="lesson", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="lesson")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    difficulty = Column(String, default="easy")
    prompt = Column(Text)
    expected_output = Column(Text, nullable=True)
    test_cases = Column(Text, nullable=True)
    points_value = Column(Integer, default=25)
    lesson = relationship("Lesson", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    code = Column(Text)
    status = Column(String, default="pending")
    points_awarded = Column(Integer, default=0)
    hint_level = Column(Integer, default=0)
    feedback = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="submissions")
    task = relationship("Task", back_populates="submissions")
    reviews = relationship("PeerReview", back_populates="submission")

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    is_completed = Column(Boolean, default=False)
    points_awarded = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="progress")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    icon = Column(String, default="🏆")
    category = Column(String, default="general")
    required_value = Column(Integer, default=1)

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")

class StoreItem(Base):
    __tablename__ = "store_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    price_coins = Column(Integer)
    item_type = Column(String, default="theme")
    image_url = Column(String, default="")
    rarity = Column(String, default="common")

class UserPurchase(Base):
    __tablename__ = "user_purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("store_items.id"))
    purchased_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="purchases")
    item = relationship("StoreItem")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    content = Column(Text)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="comments")
    lesson = relationship("Lesson", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])

class PeerReview(Base):
    __tablename__ = "peer_reviews"
    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    score = Column(Integer, default=0)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewer = relationship("User")
    submission = relationship("Submission", back_populates="reviews")

class Clan(Base):
    __tablename__ = "clans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text, default="")
    max_members = Column(Integer, default=5)
    total_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    members = relationship("ClanMember", back_populates="clan")

class ClanMember(Base):
    __tablename__ = "clan_members"
    id = Column(Integer, primary_key=True, index=True)
    clan_id = Column(Integer, ForeignKey("clans.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)
    clan = relationship("Clan", back_populates="members")
    user = relationship("User")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    next_review = Column(DateTime, default=datetime.utcnow)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    user = relationship("User", back_populates="flashcards")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    notification_type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="notifications")

class PrivateMessage(Base):
    __tablename__ = "private_messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

class DoubleXPEvent(Base):
    __tablename__ = "double_xp_events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    multiplier = Column(Float, default=2.0)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

class AntiFraudLog(Base):
    __tablename__ = "antifraud_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Appeal(Base):
    __tablename__ = "appeals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    status = Column(String, default="pending")
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
