from fastapi import FastAPI
from backend.schemas import LearnerProfileCreate, LearnerProfileRead
from psycopg.rows import dict_row
from backend.database import get_connection

app = FastAPI(title="RAG个性化学习系统")

@app.get("/health")
def health_check() ->dict[str, str]:
    return {"status": "ok"}

@app.post("/profiles",status_code=201)
def create_profile(profile: LearnerProfileCreate) -> LearnerProfileRead:
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO learner_profiles (
                    python_level, ai_level, learning_goal, weekly_hours
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id, python_level, ai_level, learning_goal,
                          weekly_hours, created_at
                """,
                (
                    profile.python_level,
                    profile.ai_level,
                    profile.learning_goal,
                    profile.weekly_hours,
                ),
            )
            return LearnerProfileRead.model_validate(cursor.fetchone())