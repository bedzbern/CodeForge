"""
Student-facing API router for CodeForge.

Handles POST /api/ask — the main endpoint students use to ask questions.
"""

import os
from datetime import date, datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from server.database import get_db
from server.models import Student, Query, Session
from server.rule_engine import get_effective_level, get_or_create_rule
from server.rate_limiter import rate_limiter
from server.providers.base import AIProvider

router = APIRouter(prefix="/api")

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server", "prompts")


def _load_prompt(level: int) -> str:
    """Load the system prompt for a given hint level."""
    filename = f"level{level}_socratic.txt" if level == 1 else f"level{level}_"
    name_map = {
        1: "level1_socratic.txt",
        2: "level2_hint_giver.txt",
        3: "level3_error_translator.txt",
        4: "level4_logic_explainer.txt",
        5: "level5_full_answer.txt",
    }
    filepath = os.path.join(PROMPTS_DIR, name_map[level])
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _load_base_prompt() -> str:
    """Load the shared base system prompt."""
    filepath = os.path.join(PROMPTS_DIR, "base_system.txt")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


class AskRequest(BaseModel):
    student_ip: str
    code_snapshot: str = ""
    question: str
    file_name: str = ""
    line_number: int = 0


class AskResponse(BaseModel):
    level: int
    level_name: str
    response: str
    ip: str
    timestamp: str


LEVEL_NAMES = {
    1: "Socratic Mirror",
    2: "Hint Giver",
    3: "Error Translator",
    4: "Logic Explainer",
    5: "Full Answer",
}


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    body: AskRequest,
    request: Request,
    db: DBSession = Depends(get_db),
):
    """
    Handle a student question.

    Validates the student IP, enforces rate limits, determines the hint level,
    builds the AI prompt, and returns the response.
    """
    client_ip = body.student_ip

    if not rate_limiter.is_allowed(client_ip):
        wait = rate_limiter.time_until_allowed(client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Please wait {int(wait)} seconds.",
        )

    student = db.query(Student).filter(Student.ip_address == client_ip).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Unknown student IP")

    student.last_active = datetime.utcnow()
    db.commit()

    level = get_effective_level(db, client_ip)
    level_name = LEVEL_NAMES.get(level, "Hint Giver")

    base_prompt = _load_base_prompt()
    level_prompt = _load_prompt(level)

    messages = [
        {"role": "system", "content": base_prompt},
        {"role": "system", "content": level_prompt},
    ]

    user_content = f"Question: {body.question}"
    if body.code_snapshot:
        user_content += f"\n\nCode:\n```\n{body.code_snapshot}\n```"
    if body.file_name:
        user_content += f"\n\nFile: {body.file_name}"
    if body.line_number:
        user_content += f"\nLine: {body.line_number}"

    messages.append({"role": "user", "content": user_content})

    provider: AIProvider = request.app.state.ai_provider
    try:
        ai_response = await provider.generate(messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI provider error: {str(e)}")

    active_session = db.query(Session).filter(Session.ended_at.is_(None)).first()
    if active_session is None:
        today = date.today()
        session_id = f"sess_{today.strftime('%Y%m%d')}_1"
        active_session = Session(id=session_id, date=today)
        db.add(active_session)
        db.commit()

    query_log = Query(
        student_ip=client_ip,
        session_id=active_session.id,
        question=body.question,
        code_snapshot=body.code_snapshot,
        file_name=body.file_name,
        line_number=body.line_number,
        hint_level=level,
        ai_response=ai_response,
    )
    db.add(query_log)
    active_session.total_queries = (active_session.total_queries or 0) + 1
    db.commit()

    return AskResponse(
        level=level,
        level_name=level_name,
        response=ai_response,
        ip=client_ip,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
