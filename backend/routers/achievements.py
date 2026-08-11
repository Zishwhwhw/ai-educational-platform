# ==========================================
# File: routers/achievements.py
# Description: Achievement listing and unlock routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models, schemas
from database import get_db
from services.achievements import ACHIEVEMENT_DEFINITIONS

router = APIRouter(prefix="/achievements", tags=["achievements"])

@router.get("/")
def list_all_achievements():
    return [{"name": a["name"], "description": a["description"], "icon": a["icon"], "category": a["category"], "required_value": a["required_value"]} for a in ACHIEVEMENT_DEFINITIONS]

@router.get("/user/{user_id}")
def get_user_achievements(user_id: int, db: Session = Depends(get_db)):
    unlocked = db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user_id).all()
    result = []
    for ua in unlocked:
        ach = db.query(models.Achievement).filter(models.Achievement.id == ua.achievement_id).first()
        if ach:
            result.append({"name": ach.name, "description": ach.description, "icon": ach.icon, "category": ach.category, "unlocked_at": ua.unlocked_at.isoformat()})
    return result

@router.post("/check/{user_id}")
def check_and_unlock(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"unlocked": []}
    
    stats = {
        "lessons_completed": db.query(models.Progress).filter(models.Progress.user_id == user_id, models.Progress.is_completed == True).count(),
        "correct_submissions": db.query(models.Submission).filter(models.Submission.user_id == user_id, models.Submission.status == "correct").count(),
        "streak_days": user.streak_days,
        "comments_posted": db.query(models.Comment).filter(models.Comment.user_id == user_id).count(),
        "reviews_given": db.query(models.PeerReview).filter(models.PeerReview.reviewer_id == user_id).count(),
        "total_coins_earned": user.coins,
    }
    
    newly_unlocked = []
    for ach_def in ACHIEVEMENT_DEFINITIONS:
        if ach_def["check"](stats):
            existing_ach = db.query(models.Achievement).filter(models.Achievement.name == ach_def["name"]).first()
            if not existing_ach:
                existing_ach = models.Achievement(name=ach_def["name"], description=ach_def["description"], icon=ach_def["icon"], category=ach_def["category"], required_value=ach_def["required_value"])
                db.add(existing_ach)
                db.commit()
                db.refresh(existing_ach)
            
            already_has = db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user_id, models.UserAchievement.achievement_id == existing_ach.id).first()
            if not already_has:
                ua = models.UserAchievement(user_id=user_id, achievement_id=existing_ach.id)
                db.add(ua)
                db.commit()
                newly_unlocked.append(ach_def["name"])
    
    return {"unlocked": newly_unlocked}
