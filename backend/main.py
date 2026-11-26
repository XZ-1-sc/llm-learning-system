from fastapi import FastAPI, HTTPException, Path, Query
from backend.schemas import LearnerProfileCreate, LearnerProfileRead
from psycopg.rows import dict_row
from backend.database import get_connection
from backend.diagnostics import QUESTIONS
from backend.diagnostics import QUESTIONS, grade_diagnostic, recommend_study, recommend_study_tasks
from backend.knowledge import build_rag_context, find_knowledge_passages
from backend.learning_resources import LEARNING_RESOURCES, find_learning_resources
from backend.schemas import (
    DiagnosticResultRead,
    DiagnosticSubmission,
    KnowledgePassageRead,
    LearningPlanRead,
    LearningPlanStep,
    LearningResourceRead,
    LearningTopic,
    LearnerProfileCreate,
    LearnerProfileRead,
    RagContextRead,
    RagContextRequest,
)

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

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO diagnostic_results (
                    profile_id, score, total, incorrect_question_ids
                )
                SELECT id, %s, %s, %s::text[]
                FROM learner_profiles
                WHERE id = %s
                RETURNING id
                """,
                (
                    result["score"],
                    result["total"],
                    result["incorrect_question_ids"],
                    submission.profile_id,
                ),
            )
            saved = cursor.fetchone()

    if saved is None:
        raise HTTPException(status_code=404, detail="Learner profile not found")

    return {"id": saved["id"], "profile_id": submission.profile_id, **result}


@app.get("/diagnostics/{diagnostic_id}")
def read_diagnostic(diagnostic_id: int = Path(gt=0)) -> DiagnosticResultRead:
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, profile_id, score, total, incorrect_question_ids, created_at
                FROM diagnostic_results
                WHERE id = %s
                """,
                (diagnostic_id,),
            )
            row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Diagnostic result not found")

    return DiagnosticResultRead.model_validate(row)


@app.get("/diagnostics/{diagnostic_id}/recommendations")
def read_study_recommendations(diagnostic_id: int = Path(gt=0)) -> list[str]:
    result = read_diagnostic(diagnostic_id)
    return recommend_study(result.incorrect_question_ids)


@app.get("/diagnostics/{diagnostic_id}/learning-plan")
def read_learning_plan(diagnostic_id: int = Path(gt=0)) -> LearningPlanRead:
    result = read_diagnostic(diagnostic_id)
    profile = read_profile(result.profile_id)
    tasks = recommend_study_tasks(result.incorrect_question_ids)
    minutes_per_step = min(30, profile.weekly_hours * 60 // len(tasks))

    return LearningPlanRead(
        diagnostic_id=result.id,
        profile_id=profile.id,
        learning_goal=profile.learning_goal,
        weekly_hours=profile.weekly_hours,
        steps=[
            LearningPlanStep(
                task=task,
                estimated_minutes=minutes_per_step,
                resources=[resource for resource in LEARNING_RESOURCES if resource.topic in topics],
            )
            for task, topics in tasks
        ],
    )


@app.get("/learning-resources")
def list_learning_resources(topic: LearningTopic | None = None) -> list[LearningResourceRead]:
    return [
        resource
        for resource in LEARNING_RESOURCES
        if topic is None or resource.topic == topic
    ]


@app.get("/learning-resources/search")
def search_learning_resources(
    search_query: str = Query(alias="q", min_length=1, max_length=100, pattern=r"\S"),
) -> list[LearningResourceRead]:
    return find_learning_resources(search_query)


@app.get("/knowledge/search")
def search_knowledge(
    search_query: str = Query(alias="q", min_length=1, max_length=100, pattern=r"\S"),
) -> list[KnowledgePassageRead]:
    return find_knowledge_passages(search_query)


@app.post("/rag/context")
def preview_rag_context(request: RagContextRequest) -> RagContextRead:
    return build_rag_context(request.question, request.search_query)
