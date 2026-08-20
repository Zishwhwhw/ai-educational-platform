from pydantic import BaseModel


class AIPromptRequest(BaseModel):
    prompt: str
    context: str = ""


class AIPromptResponse(BaseModel):
    response: str


class AICourseGenerateRequest(BaseModel):
    topic: str
    language: str = "python"
    difficulty: str = "beginner"
    num_modules: int = 5


class AIResumeCheckRequest(BaseModel):
    resume_text: str
