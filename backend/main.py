from fastapi import FastAPI

app = FastAPI(title="RAG个性化学习系统")

@app.get("/health")
def health_check() ->dict[str, str]:
    return {"status": "ok"}