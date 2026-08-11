# ==========================================
# File: main.py
# Description: FastAPI entry point and complete app configuration
# Author: AI Agent (Orchestrator)
# Created: 2026-08-02
# Changes:
#   - 2026-08-02 (AI Agent): Registered all 16 routers for complete platform
# ==========================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Educational Platform API",
    description="Backend API for the gamified AI-powered educational platform",
    version="1.0.0",
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AI-Code Backend API",
        "status": "online",
        "version": "1.0.0"
    }

from routers import (
    auth,
    users,
    courses,
    lessons,
    submissions,
    progress,
    achievements,
    ai,
    ws,
    store,
    clans,
    streaks,
    flashcards,
    notifications,
    messages,
    leaderboard
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(submissions.router)
app.include_router(progress.router)
app.include_router(achievements.router)
app.include_router(ai.router)
app.include_router(ws.router)
app.include_router(store.router)
app.include_router(clans.router)
app.include_router(streaks.router)
app.include_router(flashcards.router)
app.include_router(notifications.router)
app.include_router(messages.router)
app.include_router(leaderboard.router)
