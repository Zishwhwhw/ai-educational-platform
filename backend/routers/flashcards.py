# ==========================================
# File: routers/flashcards.py
# Description: Spaced Repetition (Flashbacks) routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import models, schemas
from database import get_db

router = APIRouter(prefix="/flashcards", tags=["flashcards"])

@router.get("/due/{user_id}", response_model=List[schemas.FlashcardResponse])
def get_due_flashcards(user_id: int, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return db.query(models.Flashcard).filter(
        models.Flashcard.user_id == user_id,
        models.Flashcard.next_review <= now
    ).all()

@router.post("/", response_model=schemas.FlashcardResponse)
def create_flashcard(card: schemas.FlashcardCreate, user_id: int = 1, db: Session = Depends(get_db)):
    new_card = models.Flashcard(
        user_id=user_id,
        question=card.question,
        answer=card.answer,
        next_review=datetime.utcnow()
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.post("/{card_id}/review")
def review_flashcard(card_id: int, review: schemas.FlashcardReview, db: Session = Depends(get_db)):
    card = db.query(models.Flashcard).filter(models.Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
        
    q = review.quality
    if q >= 3:
        if card.repetitions == 0:
            card.interval_days = 1
        elif card.repetitions == 1:
            card.interval_days = 6
        else:
            card.interval_days = int(card.interval_days * card.ease_factor)
        card.repetitions += 1
    else:
        card.repetitions = 0
        card.interval_days = 1
        
    card.ease_factor = max(1.3, card.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    card.next_review = datetime.utcnow() + timedelta(days=card.interval_days)
    db.commit()
    return {"message": "Review recorded", "next_review": card.next_review.isoformat(), "interval_days": card.interval_days}
