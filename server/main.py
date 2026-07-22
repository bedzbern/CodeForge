"""
CodeForge AI Server — Main FastAPI Application.

Entry point for the server. Sets up CORS, loads AI providers,
initialises the database, and registers all API routers.
"""

import os
import re
import socketio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.database import init_db
from server.routers import student, teacher
from server.websocket_events import sio
from server.providers.groq_provider import GroqProvider
from server.providers.ollama_provider import OllamaProvider

_LAB_IP_PATTERN = re.compile(r"^192\.168\.1\.\d{1,3}$")


def _get_lab_origins() -> list[str]:
    """Build CORS origins for the lab network."""
    origins = ["http://localhost:5173"]
    for i in range(1, 52):
        origins.append(f"http://192.168.1.{i}")
        origins.append(f"http://192.168.1.{i}:5173")
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI app."""
    init_db()
    print("[CodeForge] Database initialised")

    provider_name = os.environ.get("AI_PROVIDER", "groq").lower()
    if provider_name == "ollama":
        app.state.ai_provider = OllamaProvider()
        print("[CodeForge] AI Provider: Ollama (local)")
    else:
        app.state.ai_provider = GroqProvider()
        print("[CodeForge] AI Provider: Groq (cloud)")

    yield

    if hasattr(app.state, "ai_provider"):
        await app.state.ai_provider.close()
    print("[CodeForge] Server shut down")


app = FastAPI(
    title="CodeForge AI Server",
    description="Teacher-controlled AI coding assistant for school computer labs",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_lab_origins(),
    allow_origin_headers=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(student.router)
app.include_router(teacher.router)

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
