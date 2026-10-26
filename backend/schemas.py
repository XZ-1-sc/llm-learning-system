from typing import Literal
from pydantic import BaseModel,Field


class LearnerProfileCreate(BaseModel):
    python_level: Literal["beginner","intermediate","advanced"]
    ai_level: Literal["beginner","intermediate","advanced"]
    learning_goal: str = Field(min_length=1,max_length=200)
    weekly_hours: int = Field(ge=1,le=168)