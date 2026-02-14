from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.events import router as events_router
from app.api.health import router as health_router
from app.api.items import router as items_router
from app.api.jobs import router as jobs_router
from app.api.orders import router as orders_router
from app.core.config import settings

app = FastAPI(title="Crosslist API")
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(items_router)
app.include_router(jobs_router)
app.include_router(orders_router)
app.include_router(events_router)
