from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    category: str
    required_value: int

    model_config = ConfigDict(from_attributes=True)


class UserAchievementResponse(BaseModel):
    achievement: AchievementResponse
    unlocked_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoreItemResponse(BaseModel):
    id: int
    name: str
    description: str
    price_coins: int
    item_type: str
    image_url: str
    rarity: str

    model_config = ConfigDict(from_attributes=True)


class PurchaseRequest(BaseModel):
    item_id: int


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

    model_config = ConfigDict(from_attributes=True)


class FlashcardReview(BaseModel):
    quality: int


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    points: int
    level: str
    avatar_url: str
    tier: str | None = None


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    freeze_remaining: int
    last_activity: datetime | None
