from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    lesson_id: int
    content: str
    parent_id: int | None = None


class CommentResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    content: str
    parent_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClanCreate(BaseModel):
    name: str
    description: str = ""


class ClanResponse(BaseModel):
    id: int
    name: str
    description: str
    max_members: int
    total_points: int

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: int
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)
