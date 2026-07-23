"""
CodeForge AI Server — Main FastAPI Application.

Entry point for the server. Sets up CORS, loads AI providers,
initialises the database, caches prompts, and registers all API routers.

Performance features:
- Prompts loaded into memory at startup (no disk I/O per request).
- Rule engine uses 10s in-memory TTL cache.
- Rate limiter auto-cleans stale entries every 10 minutes.
- Request timing logged for performance monitoring.
"""

import os
import re
import time
import socketio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from server.database import init_db
from server.routers import student, teacher
from server.websocket_events import sio
from server.providers.groq_provider import GroqProvider
from server.providers.ollama_provider import OllamaProvider
from server.prompt_cache import load_prompts


def _get_lab_origins() -> list[str]:
    """Build CORS origins for the lab network."""
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    for i in range(1, 52):
        origins.append(f"http://192.168.1.{i}")
        origins.append(f"http://192.168.1.{i}:5173")
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI app."""
    init_db()
    print("[CodeForge] Database initialised")

    load_prompts()

    provider_name = os.environ.get("AI_PROVIDER", "groq").lower()
    if provider_name == "ollama":
        app.state.ai_provider = OllamaProvider()
        print("[CodeForge] AI Provider: Ollama (local)")
    else:
        app.state.ai_provider = GroqProvider()
        print("[CodeForge] AI Provider: Groq (cloud)")

    app.state.active_session_id = None

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


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    """Log request path and duration for performance monitoring."""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    if duration_ms > 1000:
        print(f"[PERF] SLOW {request.method} {request.url.path} — {duration_ms:.0f}ms")

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_lab_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(student.router)
app.include_router(teacher.router)

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

app = socket_app
