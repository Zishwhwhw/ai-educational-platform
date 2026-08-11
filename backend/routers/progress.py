# ==========================================
# File: routers/progress.py
# Description: Progress tracking routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models, schemas
from database import get_db
from services.points import calculate_points, apply_fifty_percent_rule, get_level
from services.coins import calculate_coins_earned, can_earn_coins

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/complete", response_model=schemas.ProgressResponse)
def complete_lesson(prog: schemas.ProgressCreate, user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    lesson = db.query(models.Lesson).filter(models.Lesson.id == prog.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if already completed
    existing = db.query(models.Progress).filter(
        models.Progress.user_id == user_id,
        models.Progress.lesson_id == prog.lesson_id,
        models.Progress.is_completed == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already completed")
    
    # Apply 50% rule
    base_points = lesson.points_value
    final_points = apply_fifty_percent_rule(base_points, prog.time_spent, lesson.min_read_time)
    final_points = int(final_points * user.xp_multiplier)
    
    # Award coins
    coin_reward = max(1, final_points // 5)
    if can_earn_coins(user.daily_coins_earned, user.subscription_tier):
        earned = calculate_coins_earned(coin_reward, user.subscription_tier)
        user.coins += earned
        user.daily_coins_earned += earned
    
    user.points += final_points
    user.level = get_level(user.points)
    
    progress = models.Progress(
        user_id=user_id,
        lesson_id=prog.lesson_id,
        course_id=prog.course_id,
        is_completed=True,
        points_awarded=final_points,
        time_spent=prog.time_spent,
        completed_at=datetime.utcnow(),
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress

@router.get("/user/{user_id}", response_model=List[schemas.ProgressResponse])
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Progress).filter(models.Progress.user_id == user_id).all()

@router.get("/user/{user_id}/course/{course_id}")
def get_course_progress(user_id: int, course_id: int, db: Session = Depends(get_db)):
    total_lessons = db.query(models.Lesson).join(models.Module).filter(models.Module.course_id == course_id).count()
    completed = db.query(models.Progress).filter(
        models.Progress.user_id == user_id,
        models.Progress.course_id == course_id,
        models.Progress.is_completed == True
    ).count()
    return {"total_lessons": total_lessons, "completed": completed, "percentage": round((completed / max(total_lessons, 1)) * 100, 1)}
