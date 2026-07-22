"""
Analytics engine for CodeForge.

Generates end-of-session summaries by analysing query logs.
"""

from collections import Counter
from datetime import date
from sqlalchemy.orm import Session as DBSession

from server.models import Query, Session


def get_session_queries(db: DBSession, session_id: str) -> list[Query]:
    """Return all queries for a given session."""
    return db.query(Query).filter(Query.session_id == session_id).all()


def compute_session_stats(db: DBSession, session_id: str) -> dict:
    """
    Compute raw statistics for a session:
    - total questions
    - unique students who asked
    - common topics (extracted from questions)
    - common errors
    - students who may need follow-up
    """
    queries = get_session_queries(db, session_id)

    total_questions = len(queries)
    unique_students = list(set(q.student_ip for q in queries))

    question_texts = [q.question.lower() for q in queries]
    error_keywords = ["error", "exception", "traceback", "typeerror", "indexerror",
                      "nameerror", "valueerror", "keyerror", "syntaxerror"]

    error_counter = Counter()
    topic_counter = Counter()

    topic_keywords = [
        "for-loop", "for loop", "while loop", "loop", "array", "list",
        "function", "parameter", "argument", "return", "dictionary", "dict",
        "string", "integer", "boolean", "class", "object", "method",
        "index", "slice", "file", "import", "exception", "try",
    ]

    for text in question_texts:
        for keyword in error_keywords:
            if keyword in text:
                error_counter[keyword] += 1
        for keyword in topic_keywords:
            if keyword in text:
                topic_counter[keyword] += 1

    query_counts = Counter(q.student_ip for q in queries)
    high_volume_ips = [ip for ip, count in query_counts.items() if count >= 5]

    low_hint_students = []
    for q in queries:
        if q.hint_level <= 2 and q.student_ip not in low_hint_students:
            low_hint_students.append(q.student_ip)

    return {
        "total_questions": total_questions,
        "unique_students": len(unique_students),
        "unique_student_ips": unique_students,
        "common_topics": topic_counter.most_common(5),
        "common_errors": error_counter.most_common(5),
        "students_needing_followup": list(set(high_volume_ips + low_hint_students)),
    }


def generate_summary_text(db: DBSession, session_id: str) -> str:
    """
    Generate a human-readable summary for the teacher.

    Uses the computed stats to build a natural-language paragraph.
    """
    stats = compute_session_stats(db, session_id)

    if stats["total_questions"] == 0:
        return "No questions were asked during this session."

    parts = []

    parts.append(
        f"During this session, {stats['unique_students']} student(s) "
        f"asked a total of {stats['total_questions']} question(s)."
    )

    if stats["common_topics"]:
        topic_strs = [f"{t[0]} ({t[1]} times)" for t in stats["common_topics"][:3]]
        parts.append("Most common topics: " + ", ".join(topic_strs) + ".")

    if stats["common_errors"]:
        error_strs = [f"{e[0]} ({e[1]} times)" for e in stats["common_errors"][:3]]
        parts.append("Common errors: " + ", ".join(error_strs) + ".")

    if stats["students_needing_followup"]:
        parts.append(
            f"{len(stats['students_needing_followup'])} student(s) may benefit "
            f"from follow-up: {', '.join(stats['students_needing_followup'][:5])}."
        )

    return " ".join(parts)


def create_session_summary(db: DBSession, session_id: str) -> str:
    """
    Generate and persist the session summary.

    Returns the summary text.
    """
    summary = generate_summary_text(db, session_id)

    session = db.query(Session).filter(Session.id == session_id).first()
    if session:
        session.summary_text = summary
        from datetime import datetime
        session.ended_at = datetime.utcnow()
        db.commit()

    return summary
