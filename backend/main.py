from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(title="NidhiFlow AI Backend")
app.include_router(health_router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
