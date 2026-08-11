# ==========================================
# File: services/points.py
# Description: Points calculator per activity type
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

POINTS_MAP = {
    "text": 5,        # Text lecture (5-10m): 5 pts
    "video": 10,      # Video lesson (10-20m): 10 pts
    "quiz": 15,       # Quiz (5m): 15 pts
    "easy": 25,       # Easy code (15-20m): 25 pts
    "medium": 50,     # Medium code (30-45m): 50 pts
    "hard": 100,      # Hard code/project (1-2h): 100 pts
    "exam": 200,      # Final exam (3h+): 200 pts
}

LEVEL_THRESHOLDS = {
    "Junior": 0,
    "Regular": 500,
    "Middle": 1500,
    "Middle Plus": 3000,
    "Senior": 5000,
}

def calculate_points(content_type: str, difficulty: str = None, xp_multiplier: float = 1.0) -> int:
    if difficulty and difficulty in POINTS_MAP:
        base = POINTS_MAP[difficulty]
    elif content_type in POINTS_MAP:
        base = POINTS_MAP[content_type]
    else:
        base = 5
    return int(base * xp_multiplier)

def get_level(total_points: int) -> str:
    level = "Junior"
    for lvl, threshold in LEVEL_THRESHOLDS.items():
        if total_points >= threshold:
            level = lvl
    return level

def apply_fifty_percent_rule(points: int, time_spent: int, min_time: int) -> int:
    if time_spent < min_time * 0.5:
        return 0
    elif time_spent < min_time:
        return int(points * 0.5)
    return points
