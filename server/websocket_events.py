"""
Socket.IO event handlers for CodeForge.

Manages real-time communication between the server and teacher dashboard.
"""

import os
import re
import socketio

from server.database import SessionLocal
from server.models import Student, Rule, Query
from server.rule_engine import get_effective_level, set_hint_level, broadcast_level

_TEACHER_IP = os.environ.get("TEACHER_IP", "192.168.1.1")

_LAB_IPS = [f"192.168.1.{i}" for i in range(1, 52)]

_cors_origins = (
    [f"http://{ip}" for ip in _LAB_IPS]
    + [f"http://{ip}:5173" for ip in _LAB_IPS]
    + ["http://localhost:5173", "http://127.0.0.1:5173"]
)

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=_cors_origins,
)


@sio.event
async def connect(sid, environ):
    """Handle a new dashboard connection. Only teacher PC is allowed."""
    source_ip = environ.get("HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR", ""))

    if source_ip != _TEACHER_IP:
        raise socketio.exceptions.ConnectionRefusedError("Teacher access only")

    print(f"[Socket.IO] Dashboard connected: {sid}")


@sio.event
async def disconnect(sid):
    """Handle a dashboard disconnection."""
    print(f"[Socket.IO] Dashboard disconnected: {sid}")


@sio.event
async def request_full_status(sid, data=None):
    """
    Dashboard requests the full current state.
    Returns all student statuses.
    """
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.seat_number).all()
        ips = [s.ip_address for s in students]

        rules = {}
        if ips:
            for r in db.query(Rule).filter(Rule.student_ip.in_(ips)).all():
                rules[r.student_ip] = r

        query_counts = {}
        if ips:
            from sqlalchemy import func
            rows = (
                db.query(Query.student_ip, func.count(Query.id))
                .group_by(Query.student_ip)
                .all()
            )
            query_counts = {row[0]: row[1] for row in rows}

        student_list = []
        for s in students:
            rule = rules.get(s.ip_address)
            if rule:
                level = 5 if rule.level_5_unlocked else rule.hint_level
            else:
                level = 2
            student_list.append({
                "ip": s.ip_address,
                "seat_number": s.seat_number,
                "hint_level": level,
                "total_queries": query_counts.get(s.ip_address, 0),
            })
        await sio.emit("full_status", {"students": student_list}, room=sid)
    except Exception as e:
        print(f"[Socket.IO] Error in request_full_status: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@sio.event
async def teacher_level_change(sid, data):
    """
    Quick level change via WebSocket.
    Expects: { student_ip, new_level, session_id }
    """
    db = SessionLocal()
    try:
        student_ip = data.get("student_ip", "")
        new_level = data.get("new_level")

        if not student_ip or not isinstance(new_level, int) or new_level < 1 or new_level > 5:
            await sio.emit("error", {"message": "Invalid student_ip or new_level (must be 1-5)"}, room=sid)
            return

        rule = set_hint_level(db, student_ip, new_level)

        await sio.emit("level_changed", {
            "ip": student_ip,
            "old_level": rule.hint_level,
            "new_level": new_level,
            "by": "teacher_dashboard",
        })
    except Exception as e:
        await sio.emit("error", {"message": "Failed to update level"}, room=sid)
    finally:
        db.close()


@sio.event
async def teacher_broadcast(sid, data):
    """
    Global level change via WebSocket.
    Expects: { new_level, session_id }
    """
    db = SessionLocal()
    try:
        new_level = data.get("new_level")
        if not isinstance(new_level, int) or new_level < 1 or new_level > 5:
            await sio.emit("error", {"message": "Invalid new_level (must be 1-5)"}, room=sid)
            return

        count = broadcast_level(db, new_level)

        await sio.emit("level_changed", {
            "new_level": new_level,
            "affected_students": count,
            "by": "teacher_broadcast",
        })
    except Exception as e:
        await sio.emit("error", {"message": "Failed to broadcast level"}, room=sid)
    finally:
        db.close()


async def emit_student_query(student_ip: str, question: str, level: int, timestamp: str):
    """Emit a student_query event to all connected dashboards."""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.ip_address == student_ip).first()
        seat = student.seat_number if student else 0
        await sio.emit("student_query", {
            "ip": student_ip,
            "seat": seat,
            "question": question,
            "level": level,
            "timestamp": timestamp,
        })
    finally:
        db.close()


async def emit_student_active(student_ip: str, total_queries: int):
    """Emit a student_active event when a student first queries."""
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.ip_address == student_ip).first()
        seat = student.seat_number if student else 0
        await sio.emit("student_active", {
            "ip": student_ip,
            "seat": seat,
            "total_queries": total_queries,
        })
    finally:
        db.close()


async def emit_summary_ready(session_id: str):
    """Emit a summary_ready event when the session summary is generated."""
    await sio.emit("summary_ready", {
        "session_id": session_id,
        "summary_url": f"/api/summary?session_id={session_id}",
    })
