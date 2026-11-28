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


LearningTopic = Literal["python", "llm", "rag"]


class LearningResourceRead(BaseModel):
    topic: LearningTopic
    title: str
    publisher: str
    source_url: str
    summary: str


class KnowledgePassageRead(BaseModel):
    id: str
    text: str
    source: LearningResourceRead


class RagContextRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500, pattern=r"\S")
    search_query: str = Field(min_length=1, max_length=100, pattern=r"\S")


class RagCitation(BaseModel):
    passage_id: str
    source: LearningResourceRead


class RagContextRead(BaseModel):
    status: Literal["ready", "insufficient_evidence"]
    question: str
    context: str
    citations: list[RagCitation]


class RagAnswerRead(BaseModel):
    status: Literal["answered", "insufficient_evidence"]
    answer: str
    citations: list[RagCitation]


class LearningPlanStep(BaseModel):
    task: str
    estimated_minutes: int
    resources: list[LearningResourceRead]


class LearningPlanRead(BaseModel):
    diagnostic_id: int
    profile_id: int
    learning_goal: str
    weekly_hours: int
    steps: list[LearningPlanStep]
