"""
Tests for the CodeForge Rule Engine.

Covers:
- Default rule creation for unknown IPs
- Effective level retrieval with caching
- Level setting and validation
- Broadcast level changes
- Level 5 unlock with duration cap
- Cache invalidation on writes
"""

import time
import pytest
from datetime import datetime, timedelta

from server.rule_engine import (
    get_or_create_rule,
    get_effective_level,
    set_hint_level,
    broadcast_level,
    unlock_level_5,
    _cache_clear,
)
from server.models import Rule


class TestGetOrCreateRule:
    def test_returns_existing_rule(self, db_session):
        rule = get_or_create_rule(db_session, "192.168.1.2")
        assert rule.student_ip == "192.168.1.2"
        assert rule.hint_level == 1

    def test_creates_default_rule_for_unknown_ip(self, db_session):
        rule = get_or_create_rule(db_session, "192.168.1.99")
        assert rule.student_ip == "192.168.1.99"
        assert rule.hint_level == 2
        assert rule.level_5_unlocked is False

    def test_default_rule_persists(self, db_session):
        get_or_create_rule(db_session, "192.168.1.99")
        rule = db_session.query(Rule).filter(Rule.student_ip == "192.168.1.99").first()
        assert rule is not None
        assert rule.hint_level == 2


class TestGetEffectiveLevel:
    def test_returns_configured_level(self, db_session):
        _cache_clear()
        level = get_effective_level(db_session, "192.168.1.2")
        assert level == 1

    def test_returns_2_for_unknown_ip(self, db_session):
        _cache_clear()
        level = get_effective_level(db_session, "192.168.1.99")
        assert level == 2

    def test_returns_5_when_unlocked_with_valid_time(self, db_session):
        _cache_clear()
        rule = get_or_create_rule(db_session, "192.168.1.2")
        rule.level_5_unlocked = True
        rule.unlock_until = datetime.utcnow() + timedelta(hours=1)
        db_session.commit()

        level = get_effective_level(db_session, "192.168.1.2")
        assert level == 5

    def test_returns_configured_level_when_unlock_expired(self, db_session):
        _cache_clear()
        rule = get_or_create_rule(db_session, "192.168.1.2")
        rule.level_5_unlocked = True
        rule.unlock_until = datetime.utcnow() - timedelta(minutes=1)
        db_session.commit()

        level = get_effective_level(db_session, "192.168.1.2")
        assert level == 1

    def test_returns_5_when_permanently_unlocked(self, db_session):
        _cache_clear()
        rule = get_or_create_rule(db_session, "192.168.1.2")
        rule.level_5_unlocked = True
        rule.unlock_until = None
        db_session.commit()

        level = get_effective_level(db_session, "192.168.1.2")
        assert level == 5


class TestSetHintLevel:
    def test_sets_level(self, db_session):
        _cache_clear()
        rule = set_hint_level(db_session, "192.168.1.2", 4)
        assert rule.hint_level == 4

    def test_validates_level_range(self, db_session):
        _cache_clear()
        with pytest.raises(ValueError):
            set_hint_level(db_session, "192.168.1.2", 0)
        with pytest.raises(ValueError):
            set_hint_level(db_session, "192.168.1.2", 6)

    def test_clears_unlock_when_setting_below_5(self, db_session):
        _cache_clear()
        rule = get_or_create_rule(db_session, "192.168.1.2")
        rule.level_5_unlocked = True
        rule.unlock_until = datetime.utcnow() + timedelta(hours=1)
        db_session.commit()

        rule = set_hint_level(db_session, "192.168.1.2", 3)
        assert rule.level_5_unlocked is False
        assert rule.unlock_until is None


class TestBroadcastLevel:
    def test_broadcasts_to_all_rules(self, db_session):
        _cache_clear()
        count = broadcast_level(db_session, 3)
        assert count >= 3

        for ip in ["192.168.1.2", "192.168.1.3", "192.168.1.4"]:
            level = get_effective_level(db_session, ip)
            assert level == 3

    def test_broadcast_validates_level(self, db_session):
        _cache_clear()
        with pytest.raises(ValueError):
            broadcast_level(db_session, 0)


class TestUnlockLevel5:
    def test_unlocks_with_duration(self, db_session):
        _cache_clear()
        rule = unlock_level_5(db_session, "192.168.1.2", duration_minutes=10)
        assert rule.level_5_unlocked is True
        assert rule.hint_level == 5
        assert rule.unlock_until is not None

    def test_unlock_caps_at_60_minutes(self, db_session):
        _cache_clear()
        rule = unlock_level_5(db_session, "192.168.1.2", duration_minutes=120)
        assert rule.unlock_until is not None
        diff = rule.unlock_until - datetime.utcnow()
        assert diff.total_seconds() <= 61 * 60

    def test_permanent_unlock(self, db_session):
        _cache_clear()
        rule = unlock_level_5(db_session, "192.168.1.2")
        assert rule.level_5_unlocked is True
        assert rule.unlock_until is None
