# ==========================================
# File: routers/messages.py
# Description: Private messaging system routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=schemas.MessageResponse)
def send_message(msg: schemas.MessageCreate, sender_id: int = 1, db: Session = Depends(get_db)):
    new_msg = models.PrivateMessage(
        sender_id=sender_id,
        receiver_id=msg.receiver_id,
        content=msg.content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@router.get("/conversation/{user2_id}", response_model=List[schemas.MessageResponse])
def get_conversation(user2_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    return db.query(models.PrivateMessage).filter(
        ((models.PrivateMessage.sender_id == user_id) & (models.PrivateMessage.receiver_id == user2_id)) |
        ((models.PrivateMessage.sender_id == user2_id) & (models.PrivateMessage.receiver_id == user_id))
    ).order_by(models.PrivateMessage.created_at.asc()).all()
