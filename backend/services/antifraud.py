# ==========================================
# File: services/antifraud.py
# Description: Anti-fraud detection logic for code submission
# Author: AI Agent
# Created: 2026-08-02
# Changes:
#   - 2026-08-02 (AI Agent): Initial creation
# ==========================================

import time

def check_speedrun(start_time: float, min_required_time: int) -> bool:
    """
    Checks if the user completed the task too quickly (speedrun).
    Returns True if it's a speedrun (fraud), False otherwise.
    """
    time_taken = time.time() - start_time
    if time_taken < min_required_time:
        return True
    return False

def check_code_plagiarism(code: str) -> bool:
    """
    Basic heuristic to check for copy-pasted or highly suspicious code.
    In a real app, this would use AST analysis or external services.
    """
    suspicious_patterns = [
        "import os\nos.system",
        "eval(",
        "exec("
    ]
    for pattern in suspicious_patterns:
        if pattern in code:
            return True
    return False

def evaluate_code_submission(code: str, start_time: float, min_time: int = 10) -> dict:
    """
    Evaluates a submission through the anti-fraud engine.
    """
    if check_code_plagiarism(code):
        return {"status": "rejected", "reason": "Suspicious code detected. Action flagged."}
    
    if check_speedrun(start_time, min_time):
        return {"status": "rejected", "reason": "Speedrun detected. Please spend more time analyzing the problem."}
        
    return {"status": "approved", "points_awarded": 100}
