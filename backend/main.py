from fastapi import FastAPI
from backend.core.config import settings
from backend.api.router import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0"
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Paper Trading Backend is running"
    }
