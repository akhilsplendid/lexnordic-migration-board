from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.legal import router as legal_router
from app.routes.matters import router as matters_router
from app.routes.permits import router as permits_router
from app.routes.sessions import router as sessions_router
from app.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.app_public_url,
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(legal_router)
    app.include_router(matters_router)
    app.include_router(permits_router)
    app.include_router(sessions_router)
    return app


app = create_app()
