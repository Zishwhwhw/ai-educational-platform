# ==========================================
# File: routers/lessons.py
# Description: Lesson and Task CRUD routes
# Author: AI Agent
# Created: 2026-08-02
# ==========================================


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.session import get_db

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("/module/{module_id}", response_model=schemas.LessonResponse)
def create_lesson(module_id: int, lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    new = models.Lesson(**lesson.dict(), module_id=module_id)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.get("/{lesson_id}", response_model=schemas.LessonResponse)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get("/{lesson_id}/tasks", response_model=list[schemas.TaskResponse])
def get_lesson_tasks(lesson_id: int, db: Session = Depends(get_db)):
    return db.query(models.Task).filter(models.Task.lesson_id == lesson_id).all()


@router.post("/{lesson_id}/tasks", response_model=schemas.TaskResponse)
def create_task(lesson_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    new = models.Task(**task.dict(), lesson_id=lesson_id)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new
