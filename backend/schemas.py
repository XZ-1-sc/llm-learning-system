from typing import Literal
from pydantic import BaseModel,Field
from datetime import datetime


class LearnerProfileCreate(BaseModel):
    python_level: Literal["beginner","intermediate","advanced"]
    ai_level: Literal["beginner","intermediate","advanced"]
    learning_goal: str = Field(min_length=1,max_length=200)
    weekly_hours: int = Field(ge=1,le=168)

class LearnerProfileRead(LearnerProfileCreate):
    id: int
    created_at: datetime

class DiagnosticSubmission(BaseModel):
    profile_id: int = Field(gt=0)
    answers: dict[str, Literal["A", "B", "C"]]


class DiagnosticResultRead(BaseModel):
    id: int
    profile_id: int
    score: int
    total: int
    incorrect_question_ids: list[str]
    created_at: datetime


class LearningPlanStep(BaseModel):
    task: str
    estimated_minutes: int


class LearningPlanRead(BaseModel):
    diagnostic_id: int
    profile_id: int
    learning_goal: str
    weekly_hours: int
    steps: list[LearningPlanStep]


LearningTopic = Literal["python", "llm", "rag"]


class LearningResourceRead(BaseModel):
    topic: LearningTopic
    title: str
    publisher: str
    source_url: str
    summary: str
