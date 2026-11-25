from fastapi import FastAPI,HTTPException,Path
from backend.schemas import LearnerProfileCreate, LearnerProfileRead
from psycopg.rows import dict_row
from backend.database import get_connection
from backend.diagnostics import QUESTIONS
from backend.diagnostics import QUESTIONS, grade_diagnostic
from backend.schemas import DiagnosticSubmission, LearnerProfileCreate, LearnerProfileRead

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

@app.get("/profiles/{profile_id}")
def read_profile(profile_id: int = Path(gt=0)) -> LearnerProfileRead:
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, python_level, ai_level, learning_goal,
                       weekly_hours, created_at
                FROM learner_profiles
                WHERE id = %s
                """,
                (profile_id,),
            )
            row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    return LearnerProfileRead.model_validate(row)

@app.get("/diagnostics/questions")
def list_diagnostic_questions():
    return [
        {
            "id": question_id,
            "topic": question_data["topic"],
            "prompt": question_data["prompt"],
            "options": question_data["options"],
        }
        for question_id, question_data in QUESTIONS.items()
    ]

@app.post("/diagnostics")
def submit_diagnostic(submission: DiagnosticSubmission):
    try:
        result = grade_diagnostic(submission.answers)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    read_profile(submission.profile_id)
    return {"profile_id": submission.profile_id, **result}