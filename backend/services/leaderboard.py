# ==========================================
# File: services/leaderboard.py
# Description: Top 5% calculation with tier rewards
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

def calculate_top_tiers(users_sorted: list) -> list:
    """
    Assigns reward tiers to the top 5% of users.
    - Top 2%: "Absolute Top" (30-50% discount)
    - Next 1.5%: "Discipline" (15-25% discount) 
    - Next 1.5%: "Progress" (10-15% discount)
    """
    total = len(users_sorted)
    if total == 0:
        return []
    
    top_2_pct = max(1, int(total * 0.02))
    top_3_5_pct = max(1, int(total * 0.035))
    top_5_pct = max(1, int(total * 0.05))
    
    result = []
    for i, user in enumerate(users_sorted):
        tier = None
        discount = 0
        if i < top_2_pct:
            tier = "Absolute Top"
            discount = 40
        elif i < top_3_5_pct:
            tier = "Discipline"
            discount = 20
        elif i < top_5_pct:
            tier = "Progress"
            discount = 12
        
        result.append({
            "rank": i + 1,
            "user_id": user.get("id"),
            "username": user.get("username"),
            "points": user.get("points"),
            "level": user.get("level", "Junior"),
            "avatar_url": user.get("avatar_url", ""),
            "tier": tier,
            "discount": discount,
            "is_shadowbanned": user.get("is_shadowbanned", False),
        })
    
    # Filter out shadowbanned users from top tiers
    for entry in result:
        if entry["is_shadowbanned"] and entry["tier"]:
            entry["tier"] = None
            entry["discount"] = 0
    
    return result
