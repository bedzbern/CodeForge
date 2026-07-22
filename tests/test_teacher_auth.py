"""
Tests for teacher-facing endpoints.

Covers:
- Teacher IP auth enforcement
- Status endpoint access control
- Level change access control
- Broadcast access control
- Unlock access control
- Summary access control
- Health endpoint (public)
"""

import os
import pytest


class TestTeacherAuth:
    def test_health_endpoint_public(self, client):
        """Health endpoint is accessible to anyone."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_status_requires_teacher_ip(self, client):
        """Status endpoint rejects non-teacher IPs."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.get(
            "/api/status",
            headers={"X-Forwarded-For": "192.168.1.2"},
        )
        assert response.status_code == 403

    def test_status_allows_teacher_ip(self, client):
        """Status endpoint accepts teacher IP."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.get(
            "/api/status",
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 200

    def test_level_change_requires_teacher(self, client):
        """Level change rejects non-teacher IPs."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/level",
            json={"student_ip": "192.168.1.2", "new_level": 3},
            headers={"X-Forwarded-For": "192.168.1.2"},
        )
        assert response.status_code == 403

    def test_broadcast_requires_teacher(self, client):
        """Broadcast rejects non-teacher IPs."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/broadcast",
            json={"new_level": 2},
            headers={"X-Forwarded-For": "192.168.1.3"},
        )
        assert response.status_code == 403

    def test_unlock_requires_teacher(self, client):
        """Unlock rejects non-teacher IPs."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/unlock",
            json={"student_ip": "192.168.1.2", "duration_minutes": 5},
            headers={"X-Forwarded-For": "192.168.1.4"},
        )
        assert response.status_code == 403

    def test_summary_requires_teacher(self, client):
        """Summary rejects non-teacher IPs."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.get(
            "/api/summary",
            headers={"X-Forwarded-For": "192.168.1.5"},
        )
        assert response.status_code == 403

    def test_level_validation(self, client):
        """Level change rejects invalid levels."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/level",
            json={"student_ip": "192.168.1.2", "new_level": 6},
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 422

    def test_teacher_can_change_level(self, client, db_session):
        """Teacher can successfully change a student's level."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/level",
            json={"student_ip": "192.168.1.2", "new_level": 4},
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["new_level"] == 4

    def test_teacher_can_broadcast(self, client, db_session):
        """Teacher can broadcast a level to all students."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/broadcast",
            json={"new_level": 2},
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["affected_students"] >= 3

    def test_unknown_student_ip_for_level(self, client, db_session):
        """Level change for unknown IP returns 404."""
        os.environ["TEACHER_IP"] = "192.168.1.1"
        response = client.post(
            "/api/teacher/level",
            json={"student_ip": "192.168.1.99", "new_level": 3},
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 404
