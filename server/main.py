"""
CodeForge AI Server — Main FastAPI Application.

Entry point for the server. Sets up CORS, loads AI providers,
initialises the database, and registers all API routers.
"""

import os
import socketio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.database import init_db
from server.routers import student, teacher
from server.websocket_events import sio
from server.providers.groq_provider import GroqProvider
from server.providers.ollama_provider import OllamaProvider


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
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.1.1:5173",
        "http://192.168.1.*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student.router)
app.include_router(teacher.router)

socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
