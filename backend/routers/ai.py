# ==========================================
# File: routers/ai.py
# Description: API routes for AI Mentor interactions
# Author: AI Agent
# Created: 2026-08-02
# Changes:
#   - 2026-08-02 (AI Agent): Initial creation
# ==========================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

class PromptRequest(BaseModel):
    prompt: str
    context: str = ""

class PromptResponse(BaseModel):
    response: str

@router.post("/chat", response_model=PromptResponse)
async def ai_chat(request: PromptRequest):
    """
    Simulates a response from the AI Mentor.
    In production, this would call the Gemini or OpenAI API.
    """
    # Mock processing delay
    await asyncio.sleep(1)
    
    user_prompt = request.prompt.lower()
    
    if "course" in user_prompt:
        reply = "I can help you generate a course! Tell me the topic you are interested in (e.g., 'Advanced Python' or 'React Basics')."
    elif "help" in user_prompt or "error" in user_prompt:
        reply = "I see you need help. Paste your code or error message, and I'll analyze it step-by-step."
    else:
        reply = f"That's an interesting point! As your AI Mentor, I'm here to help you master coding. You said: '{request.prompt}'. How can we explore this further?"
        
    return {"response": reply}
