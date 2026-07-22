"""
Teacher-facing API router for CodeForge.

Handles:
- GET  /api/status          — live student status for dashboard
- POST /api/teacher/level   — change one student's hint level
- POST /api/teacher/broadcast — set global hint level
- POST /api/teacher/unlock  — temporarily unlock Level 5
- GET  /api/summary         — end-of-session analytics
- GET  /api/health          — server health check
"""

import time
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from server.database import get_db
from server.models import Student, Rule, Query, Session, AuditLog
from server.rule_engine import (
    get_effective_level,
    set_hint_level,
    broadcast_level,
    unlock_level_5,
)
from server.analytics import create_session_summary, compute_session_stats

router = APIRouter(prefix="/api")

_start_time = time.time()


class LevelChangeRequest(BaseModel):
    student_ip: str
    new_level: int
    session_id: str = ""


class BroadcastRequest(BaseModel):
    new_level: int
    session_id: str = ""


class UnlockRequest(BaseModel):
    student_ip: str
    duration_minutes: int | None = None
    reason: str = ""


def _get_active_session_id(db: DBSession) -> str:
    """Return the current active session ID, creating one if needed."""
    session = db.query(Session).filter(Session.ended_at.is_(None)).first()
    if session:
        return session.id
    today = date.today()
    sid = f"sess_{today.strftime('%Y%m%d')}_1"
    new_session = Session(id=sid, date=today)
    db.add(new_session)
    db.commit()
    return sid


@router.get("/status")
def get_status(db: DBSession = Depends(get_db)):
    """Return live status of all students for the teacher dashboard."""
    students = db.query(Student).order_by(Student.seat_number).all()
    session_id = _get_active_session_id(db)

    student_list = []
    active_count = 0
    idle_count = 0

    for s in students:
        level = get_effective_level(db, s.ip_address)
        rule = db.query(Rule).filter(Rule.student_ip == s.ip_address).first()

        is_active = (
            s.last_active is not None
            and (datetime.utcnow() - s.last_active).total_seconds() < 300
        )

        query_count = (
            db.query(Query)
            .filter(Query.session_id == session_id, Query.student_ip == s.ip_address)
            .count()
        )

        student_list.append({
            "ip": s.ip_address,
            "seat_number": s.seat_number,
            "current_hint_level": level,
            "total_queries_today": query_count,
            "last_query_time": s.last_active.isoformat() + "Z" if s.last_active else None,
            "status": "active" if is_active else "idle",
        })

        if is_active:
            active_count += 1
        else:
            idle_count += 1

    return {
        "students": student_list,
        "session_id": session_id,
        "total_active": active_count,
        "total_idle": idle_count,
    }


@router.post("/teacher/level")
def change_level(body: LevelChangeRequest, db: DBSession = Depends(get_db)):
    """Change a single student's hint level."""
    student = db.query(Student).filter(Student.ip_address == body.student_ip).first()
    if not student:
        raise HTTPException(status_code=404, detail="Unknown student IP")

    if body.new_level < 1 or body.new_level > 5:
        raise HTTPException(status_code=400, detail="Level must be between 1 and 5")

    rule = set_hint_level(db, body.student_ip, body.new_level)

    db.add(AuditLog(
        action="level_change",
        actor="teacher_dashboard",
        target_ip=body.student_ip,
        details=f'{{"new_level": {body.new_level}}}',
    ))
    db.commit()

    return {
        "success": True,
        "student_ip": body.student_ip,
        "new_level": body.new_level,
        "message": "Hint level updated",
    }


@router.post("/teacher/broadcast")
def broadcast_hint_level(body: BroadcastRequest, db: DBSession = Depends(get_db)):
    """Set all students to the same hint level."""
    if body.new_level < 1 or body.new_level > 5:
        raise HTTPException(status_code=400, detail="Level must be between 1 and 5")

    count = broadcast_level(db, body.new_level)

    db.add(AuditLog(
        action="broadcast",
        actor="teacher_dashboard",
        details=f'{{"new_level": {body.new_level}, "affected": {count}}}',
    ))
    db.commit()

    return {
        "success": True,
        "affected_students": count,
        "new_level": body.new_level,
    }


@router.post("/teacher/unlock")
def unlock_level5(body: UnlockRequest, db: DBSession = Depends(get_db)):
    """Temporarily unlock Level 5 for a specific student."""
    student = db.query(Student).filter(Student.ip_address == body.student_ip).first()
    if not student:
        raise HTTPException(status_code=404, detail="Unknown student IP")

    rule = unlock_level_5(db, body.student_ip, body.duration_minutes)

    db.add(AuditLog(
        action="unlock",
        actor="teacher_dashboard",
        target_ip=body.student_ip,
        details=f'{{"duration_minutes": {body.duration_minutes}, "reason": "{body.reason}"}}',
    ))
    db.commit()

    return {
        "success": True,
        "student_ip": body.student_ip,
        "unlocked_until": rule.unlock_until.isoformat() + "Z" if rule.unlock_until else None,
        "message": f"Level 5 unlocked{f' for {body.duration_minutes} minutes' if body.duration_minutes else ''}",
    }


@router.get("/summary")
def get_summary(session_id: str = "", db: DBSession = Depends(get_db)):
    """Return end-of-session analytics summary."""
    if not session_id:
        session_id = _get_active_session_id(db)

    stats = compute_session_stats(db, session_id)
    summary = create_session_summary(db, session_id)

    return {
        "session_id": session_id,
        "date": date.today().isoformat(),
        "total_questions": stats["total_questions"],
        "total_students_who Asked": stats["unique_students"],
        "common_topics": [{"topic": t[0], "count": t[1]} for t in stats["common_topics"]],
        "common_errors": [{"error": e[0], "count": e[1]} for e in stats["common_errors"]],
        "ai_summary": summary,
        "students_needing_followup": stats["students_needing_followup"],
    }


@router.get("/health")
def health_check(request: Request, db: DBSession = Depends(get_db)):
    """Return server health status."""
    provider = getattr(request.app.state, "ai_provider", None)

    return {
        "status": "healthy",
        "ai_provider": type(provider).__name__ if provider else "none",
        "ai_online": "configured" if provider else "none",
        "database": "connected",
        "uptime_seconds": int(time.time() - _start_time),
    }
