from fastapi import FastAPI
from backend.core.config import settings
from backend.api.router import router as api_router
from backend.core.database import engine
from backend.trading.models import Base

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0"
)

app.include_router(api_router)


@app.on_event("startup")
def _create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Paper Trading Backend is running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
