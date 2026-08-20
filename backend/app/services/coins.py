# ==========================================
# File: services/coins.py
# Description: Coin earning logic with daily limits and multipliers
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

SUBSCRIPTION_MULTIPLIERS = {
    "free": 1.0,
    "basic": 1.0,
    "advanced": 1.75,
    "premium": 4.0,
}

DAILY_LIMITS = {
    "free": 50,
    "basic": 100,
    "advanced": 200,
    "premium": 500,
}


def calculate_coins_earned(base_coins: int, subscription_tier: str) -> int:
    multiplier = SUBSCRIPTION_MULTIPLIERS.get(subscription_tier, 1.0)
    return int(base_coins * multiplier)


def can_earn_coins(daily_earned: int, subscription_tier: str) -> bool:
    limit = DAILY_LIMITS.get(subscription_tier, 50)
    return daily_earned < limit


def get_daily_limit(subscription_tier: str) -> int:
    return DAILY_LIMITS.get(subscription_tier, 50)
