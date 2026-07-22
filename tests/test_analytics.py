"""
Tests for the analytics engine.

Covers:
- Session stats computation
- Summary text generation
- Empty session handling
- Summary persistence
"""

from datetime import date, datetime

from server.analytics import compute_session_stats, generate_summary_text, create_session_summary
from server.models import Query, Session


class TestComputeSessionStats:
    def test_empty_session(self, db_session):
        stats = compute_session_stats(db_session, "sess_20260722_1")
        assert stats["total_questions"] == 0
        assert stats["unique_students"] == 0

    def test_counts_questions(self, db_session):
        db_session.add(Query(
            student_ip="192.168.1.2", session_id="sess_20260722_1",
            question="How do loops work?", hint_level=1, ai_response="Think about iteration.",
        ))
        db_session.add(Query(
            student_ip="192.168.1.3", session_id="sess_20260722_1",
            question="What is a list?", hint_level=2, ai_response="A list is a collection.",
        ))
        db_session.commit()

        stats = compute_session_stats(db_session, "sess_20260722_1")
        assert stats["total_questions"] == 2
        assert stats["unique_students"] == 2

    def test_detects_common_topics(self, db_session):
        for i in range(5):
            db_session.add(Query(
                student_ip="192.168.1.2", session_id="sess_20260722_1",
                question=f"Help with for-loop {i}", hint_level=1, ai_response="Think.",
            ))
        db_session.add(Query(
            student_ip="192.168.1.3", session_id="sess_20260722_1",
            question="What is a function?", hint_level=2, ai_response="A function is.",
        ))
        db_session.commit()

        stats = compute_session_stats(db_session, "sess_20260722_1")
        topics = dict(stats["common_topics"])
        assert "loop" in topics
        assert topics["loop"] >= 5

    def test_detects_errors(self, db_session):
        db_session.add(Query(
            student_ip="192.168.1.2", session_id="sess_20260722_1",
            question="I got an IndexError", hint_level=1, ai_response="Check your index.",
        ))
        db_session.add(Query(
            student_ip="192.168.1.3", session_id="sess_20260722_1",
            question="TypeError at line 5", hint_level=2, ai_response="Check types.",
        ))
        db_session.commit()

        stats = compute_session_stats(db_session, "sess_20260722_1")
        errors = dict(stats["common_errors"])
        assert "indexerror" in errors or "typeerror" in errors


class TestGenerateSummaryText:
    def test_empty_session_summary(self, db_session):
        text = generate_summary_text(db_session, "sess_empty")
        assert "No questions" in text

    def test_includes_student_count(self, db_session):
        db_session.add(Query(
            student_ip="192.168.1.2", session_id="sess_test",
            question="Hello", hint_level=1, ai_response="Hi",
        ))
        db_session.commit()

        text = generate_summary_text(db_session, "sess_test")
        assert "1 student(s)" in text
        assert "1 question(s)" in text


class TestCreateSessionSummary:
    def test_persists_summary(self, db_session):
        db_session.add(Session(id="sess_persist", date=date.today()))
        db_session.add(Query(
            student_ip="192.168.1.2", session_id="sess_persist",
            question="Test", hint_level=1, ai_response="Response",
        ))
        db_session.commit()

        summary = create_session_summary(db_session, "sess_persist")
        assert len(summary) > 0

        session = db_session.query(Session).filter(Session.id == "sess_persist").first()
        assert session.summary_text == summary
        assert session.ended_at is not None
