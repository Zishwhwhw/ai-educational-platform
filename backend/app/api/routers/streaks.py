# ==========================================
# File: routers/streaks.py
# Description: Streak status and freeze usage routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.session import get_db
from app.services.streaks import can_use_freeze, check_streak

router = APIRouter(prefix="/streaks", tags=["streaks"])


@router.get("/user/{user_id}", response_model=schemas.StreakResponse)
def get_user_streak(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    check_streak(user.last_activity, user.streak_days, user.streak_freeze_count)
    return {
        "current_streak": user.streak_days,
        "longest_streak": user.longest_streak,
        "freeze_remaining": user.streak_freeze_count,
        "last_activity": user.last_activity,
    }


@router.post("/user/{user_id}/freeze")
def use_streak_freeze(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not can_use_freeze(user.streak_freeze_count):
        raise HTTPException(status_code=400, detail="No freeze charges left")

    user.streak_freeze_count -= 1
    db.commit()
    return {"message": "Streak freeze applied successfully", "remaining": user.streak_freeze_count}
