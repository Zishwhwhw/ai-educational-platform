from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppealCreate(BaseModel):
    reason: str


class AppealResponse(BaseModel):
    id: int
    user_id: int
    reason: str
    status: str
    response: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
