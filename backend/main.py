from fastapi import FastAPI
from backend.schemas import LearnerProfileCreate

app = FastAPI(title="RAG个性化学习系统")

@app.get("/health")
def health_check() ->dict[str, str]:
    return {"status": "ok"}

@app.post("/profiles")
def create_profile(profile: LearnerProfileCreate) -> LearnerProfileCreate:
    return profile