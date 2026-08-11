# ==========================================
# File: database.py
# Description: SQLAlchemy database connection and session setup
# Author: AI Agent
# Created: 2026-08-02
# Changes:
#   - 2026-08-02 (AI Agent): Initial creation
# ==========================================

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
