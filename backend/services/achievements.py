# ==========================================
# File: services/achievements.py
# Description: Achievement unlock checker
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

ACHIEVEMENT_DEFINITIONS = [
    {"name": "First Steps", "description": "Complete your first lesson", "icon": "👣", "category": "learning", "check": lambda stats: stats.get("lessons_completed", 0) >= 1, "required_value": 1},
    {"name": "Code Warrior", "description": "Submit 10 correct solutions", "icon": "⚔️", "category": "coding", "check": lambda stats: stats.get("correct_submissions", 0) >= 10, "required_value": 10},
    {"name": "Streak Master", "description": "Maintain a 7-day streak", "icon": "🔥", "category": "consistency", "check": lambda stats: stats.get("streak_days", 0) >= 7, "required_value": 7},
    {"name": "Course Completer", "description": "Complete an entire course", "icon": "🎓", "category": "learning", "check": lambda stats: stats.get("courses_completed", 0) >= 1, "required_value": 1},
    {"name": "Perfect Code", "description": "Get a perfect score on a hard task", "icon": "💎", "category": "coding", "check": lambda stats: stats.get("perfect_hard_tasks", 0) >= 1, "required_value": 1},
    {"name": "Social Butterfly", "description": "Post 5 comments", "icon": "🦋", "category": "social", "check": lambda stats: stats.get("comments_posted", 0) >= 5, "required_value": 5},
    {"name": "Clan Leader", "description": "Create or lead a clan", "icon": "👑", "category": "social", "check": lambda stats: stats.get("clans_created", 0) >= 1, "required_value": 1},
    {"name": "Speed Demon", "description": "Complete 5 tasks in one day", "icon": "⚡", "category": "coding", "check": lambda stats: stats.get("daily_tasks", 0) >= 5, "required_value": 5},
    {"name": "Reviewer", "description": "Complete 3 peer reviews", "icon": "🔍", "category": "social", "check": lambda stats: stats.get("reviews_given", 0) >= 3, "required_value": 3},
    {"name": "Wealthy", "description": "Earn 1000 coins total", "icon": "💰", "category": "economy", "check": lambda stats: stats.get("total_coins_earned", 0) >= 1000, "required_value": 1000},
    {"name": "Marathon Runner", "description": "30-day streak", "icon": "🏃", "category": "consistency", "check": lambda stats: stats.get("streak_days", 0) >= 30, "required_value": 30},
    {"name": "Polyglot", "description": "Complete courses in 3 different languages", "icon": "🌍", "category": "learning", "check": lambda stats: stats.get("languages_completed", 0) >= 3, "required_value": 3},
]

def check_achievements(user_stats: dict) -> list:
    unlocked = []
    for achievement in ACHIEVEMENT_DEFINITIONS:
        if achievement["check"](user_stats):
            unlocked.append({
                "name": achievement["name"],
                "description": achievement["description"],
                "icon": achievement["icon"],
                "category": achievement["category"],
                "required_value": achievement["required_value"],
            })
    return unlocked
