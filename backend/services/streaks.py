# ==========================================
# File: services/streaks.py
# Description: Streak tracking, freeze logic
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from datetime import datetime, timedelta

MAX_FREEZES_PER_MONTH = 2

def check_streak(last_activity: datetime, current_streak: int, freeze_count: int) -> dict:
    now = datetime.utcnow()
    if last_activity is None:
        return {"streak": 1, "freeze_used": False, "broken": False}
    
    diff = (now.date() - last_activity.date()).days
    
    if diff == 0:
        return {"streak": current_streak, "freeze_used": False, "broken": False}
    elif diff == 1:
        return {"streak": current_streak + 1, "freeze_used": False, "broken": False}
    elif diff == 2 and freeze_count > 0:
        return {"streak": current_streak, "freeze_used": True, "broken": False}
    else:
        return {"streak": 1, "freeze_used": False, "broken": True}

def can_use_freeze(freeze_count: int) -> bool:
    return freeze_count > 0
