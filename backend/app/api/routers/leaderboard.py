# ==========================================
# File: routers/leaderboard.py
# Description: Leaderboard and Top 5% calculations
# Author: AI Agent
# Created: 2026-08-02
# ==========================================


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.session import get_db
from app.services.leaderboard import calculate_top_tiers

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/", response_model=list[schemas.LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.points.desc()).all()
    user_dicts = [
        {
            "id": u.id,
            "username": u.username,
            "points": u.points,
            "level": u.level,
            "avatar_url": u.avatar_url,
            "is_shadowbanned": u.is_shadowbanned,
        }
        for u in users
    ]
    return calculate_top_tiers(user_dicts)
