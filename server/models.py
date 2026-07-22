"""
SQLAlchemy models for CodeForge.

Tables: students, rules, queries, sessions, audit_log
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Text, Boolean, Date, DateTime,
    ForeignKey, CheckConstraint, func,
)
from server.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seat_number = Column(Integer, nullable=False, unique=True)
    ip_address = Column(Text, nullable=False, unique=True)
    label = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_active = Column(DateTime, nullable=True)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_ip = Column(Text, ForeignKey("students.ip_address"), nullable=False, unique=True)
    hint_level = Column(Integer, default=2)
    level_5_unlocked = Column(Boolean, default=False)
    unlock_until = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("hint_level BETWEEN 1 AND 5", name="ck_hint_level"),
    )


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_ip = Column(Text, ForeignKey("students.ip_address"), nullable=False)
    session_id = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    code_snapshot = Column(Text, nullable=True)
    file_name = Column(Text, nullable=True)
    line_number = Column(Integer, nullable=True)
    hint_level = Column(Integer, nullable=False)
    ai_response = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Text, primary_key=True)
    date = Column(Date, nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    total_queries = Column(Integer, default=0)
    summary_text = Column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(Text, nullable=False)
    actor = Column(Text, nullable=False)
    target_ip = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
