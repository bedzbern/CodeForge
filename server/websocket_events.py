"""
Socket.IO event handlers for CodeForge.

Manages real-time communication between the server and teacher dashboard.
"""

import socketio

from server.database import SessionLocal
from server.models import Student, Query
from server.rule_engine import get_effective_level, set_hint_level, broadcast_level


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.event
async def connect(sid, environ):
    """Handle a new dashboard connection."""
    print(f"[Socket.IO] Dashboard connected: {sid}")


@sio.event
async def disconnect(sid):
    """Handle a dashboard disconnection."""
    print(f"[Socket.IO] Dashboard disconnected: {sid}")


@sio.event
async def request_full_status(sid, data):
    """
    Dashboard requests the full current state.
    Returns all student statuses.
    """
    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.seat_number).all()
        student_list = []
        for s in students:
            level = get_effective_level(db, s.ip_address)
            query_count = db.query(Query).filter(
                Query.student_ip == s.ip_address
            ).count()
            student_list.append({
                "ip": s.ip_address,
                "seat_number": s.seat_number,
                "hint_level": level,
                "total_queries": query_count,
            })
        await sio.emit("full_status", {"students": student_list}, room=sid)
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
        student_ip = data.get("student_ip")
        new_level = data.get("new_level")

        if not student_ip or not new_level:
            await sio.emit("error", {"message": "Missing student_ip or new_level"}, room=sid)
            return

        rule = set_hint_level(db, student_ip, new_level)

        await sio.emit("level_changed", {
            "ip": student_ip,
            "old_level": rule.hint_level,
            "new_level": new_level,
            "by": "teacher_dashboard",
        })
    except Exception as e:
        await sio.emit("error", {"message": str(e)}, room=sid)
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
        if not new_level:
            await sio.emit("error", {"message": "Missing new_level"}, room=sid)
            return

        count = broadcast_level(db, new_level)

        await sio.emit("level_changed", {
            "new_level": new_level,
            "affected_students": count,
            "by": "teacher_broadcast",
        })
    except Exception as e:
        await sio.emit("error", {"message": str(e)}, room=sid)
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
