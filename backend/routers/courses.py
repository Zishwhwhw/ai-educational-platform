# ==========================================
# File: routers/courses.py
# Description: Course CRUD with search and filters
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, teacher_id: Optional[int] = None, db: Session = Depends(get_db)):
    new = models.Course(**course.dict(), teacher_id=teacher_id)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get("/", response_model=List[schemas.CourseResponse])
def list_courses(
    language: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    q = db.query(models.Course)
    if language:
        q = q.filter(models.Course.language == language)
    if difficulty:
        q = q.filter(models.Course.difficulty == difficulty)
    if search:
        q = q.filter(models.Course.title.ilike(f"%{search}%"))
    return q.offset(skip).limit(limit).all()

@router.get("/{course_id}", response_model=schemas.CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/{course_id}/modules", response_model=List[schemas.ModuleResponse])
def get_course_modules(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Module).filter(models.Module.course_id == course_id).order_by(models.Module.order).all()

@router.post("/{course_id}/modules", response_model=schemas.ModuleResponse)
def create_module(course_id: int, module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    new = models.Module(**module.dict(), course_id=course_id)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new
