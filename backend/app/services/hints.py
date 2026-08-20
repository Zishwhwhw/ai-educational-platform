# ==========================================
# File: services/hints.py
# Description: 5-step hint system logic
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

HINT_MESSAGES = {
    0: {"text": "Incorrect. Try again!", "detail_level": "none"},
    1: {
        "text": "Incorrect. Light hint: Think about the data type you're using and the loop structure.",
        "detail_level": "light",
    },
    2: {
        "text": "Incorrect. Stronger hint: The error is likely in your loop condition or the way you're accumulating the result. Check lines around your main logic.",
        "detail_level": "medium",
    },
    3: {
        "text": "Here's exactly where the error is: Look at how you're filtering/checking values. You need to use the modulo operator (%) to check for even/odd, and make sure your return statement is inside the function but outside the loop.",
        "detail_level": "exact",
    },
    4: {
        "text": "Here is the full working solution:\n\ndef sum_even(numbers):\n    total = 0\n    for num in numbers:\n        if num % 2 == 0:\n            total += num\n    return total\n\nStudy this carefully and understand each line before moving on.",
        "detail_level": "solution",
    },
}


def get_hint(hint_level: int, task_prompt: str = "") -> dict:
    if hint_level > 4:
        hint_level = 4
    hint = HINT_MESSAGES.get(hint_level, HINT_MESSAGES[0])
    return {
        "hint_level": hint_level,
        "hint_text": hint["text"],
        "detail_level": hint["detail_level"],
    }


def should_give_hint(current_level: int) -> bool:
    return current_level <= 4
