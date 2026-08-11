# ==========================================
# File: routers/submissions.py
# Description: Code submission, hints, and peer review routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models, schemas
from database import get_db
from services.hints import get_hint
from services.points import calculate_points, apply_fifty_percent_rule, get_level
from services.antifraud import evaluate_code_submission
import time

router = APIRouter(prefix="/submissions", tags=["submissions"])

@router.post("/", response_model=schemas.SubmissionResponse)
def submit_code(sub: schemas.SubmissionCreate, user_id: int = 1, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == sub.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Anti-fraud check
    fraud_result = evaluate_code_submission(sub.code, time.time() - 60, 5)
    
    # Count previous attempts for hint level
    prev_attempts = db.query(models.Submission).filter(
        models.Submission.user_id == user_id,
        models.Submission.task_id == sub.task_id,
        models.Submission.status == "incorrect"
    ).count()
    
    # Determine correctness (simplified: check if expected output matches)
    is_correct = False
    if task.expected_output and task.expected_output.strip() in sub.code:
        is_correct = True
    
    status = "correct" if is_correct else "incorrect"
    if fraud_result["status"] == "rejected":
        status = "flagged"
    
    points = 0
    if is_correct and status != "flagged":
        points = calculate_points("task", task.difficulty, user.xp_multiplier)
        user.points += points
        user.level = get_level(user.points)
    
    feedback = fraud_result.get("reason", "") if status == "flagged" else ("Correct! Well done!" if is_correct else get_hint(prev_attempts)["hint_text"])
    
    submission = models.Submission(
        user_id=user_id,
        task_id=sub.task_id,
        code=sub.code,
        status=status,
        points_awarded=points,
        hint_level=prev_attempts,
        feedback=feedback,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

@router.get("/user/{user_id}", response_model=List[schemas.SubmissionResponse])
def get_user_submissions(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Submission).filter(models.Submission.user_id == user_id).all()

@router.post("/hint", response_model=schemas.HintResponse)
def request_hint(req: schemas.HintRequest, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == req.submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    hint = get_hint(sub.hint_level)
    sub.hint_level += 1
    db.commit()
    return {"hint_level": hint["hint_level"], "hint_text": hint["hint_text"]}

@router.post("/peer-review", response_model=schemas.PeerReviewResponse)
def create_peer_review(review: schemas.PeerReviewCreate, reviewer_id: int = 1, db: Session = Depends(get_db)):
    new = models.PeerReview(reviewer_id=reviewer_id, **review.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new
