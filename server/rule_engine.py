"""
Rule Engine for CodeForge.

Loads per-IP hint levels from the database and enforces them.
Manages Level 5 unlock state with optional time limits.

Includes an in-memory TTL cache to avoid repeated DB queries
for the same IP within a short window.
"""

import time
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session as DBSession

from server.models import Student, Rule

_CACHE_TTL_SECONDS = 10.0

_rule_cache: dict[str, tuple[float, int]] = {}


def _cache_get(ip_address: str) -> int | None:
    """Return cached effective level if still valid, else None."""
    entry = _rule_cache.get(ip_address)
    if entry and (time.time() - entry[0]) < _CACHE_TTL_SECONDS:
        return entry[1]
    return None


def _cache_set(ip_address: str, level: int):
    """Store an effective level in the cache."""
    _rule_cache[ip_address] = (time.time(), level)


def _cache_invalidate(ip_address: str):
    """Remove a specific IP from the cache."""
    _rule_cache.pop(ip_address, None)


def _cache_clear():
    """Clear the entire rule cache."""
    _rule_cache.clear()


def get_or_create_rule(db: DBSession, ip_address: str) -> Rule:
    """Return the rule for a given IP, creating a default rule if none exists."""
    rule = db.query(Rule).filter(Rule.student_ip == ip_address).first()
    if rule is None:
        rule = Rule(student_ip=ip_address, hint_level=2, level_5_unlocked=False)
        db.add(rule)
        db.commit()
        db.refresh(rule)
    return rule


def get_effective_level(db: DBSession, ip_address: str) -> int:
    """
    Return the hint level that should be applied for this IP.

    Uses a short-lived in-memory cache to avoid hitting the DB
    on every request for the same IP.
    """
    cached = _cache_get(ip_address)
    if cached is not None:
        return cached

    rule = get_or_create_rule(db, ip_address)

    if rule.level_5_unlocked and rule.unlock_until:
        if datetime.now(timezone.utc).replace(tzinfo=None) < rule.unlock_until:
            _cache_set(ip_address, 5)
            return 5
        else:
            rule.level_5_unlocked = False
            rule.unlock_until = None
            db.commit()

    if rule.level_5_unlocked and rule.unlock_until is None:
        _cache_set(ip_address, 5)
        return 5

    _cache_set(ip_address, rule.hint_level)
    return rule.hint_level


def set_hint_level(db: DBSession, ip_address: str, level: int) -> Rule:
    """Set a student's hint level (1-5). Returns the updated rule."""
    if level < 1 or level > 5:
        raise ValueError("Level must be between 1 and 5")

    rule = get_or_create_rule(db, ip_address)
    rule.hint_level = level

    if level != 5:
        rule.level_5_unlocked = False
        rule.unlock_until = None

    db.commit()
    db.refresh(rule)
    _cache_invalidate(ip_address)
    return rule


def broadcast_level(db: DBSession, level: int) -> int:
    """Set all students to the same hint level. Returns the count affected."""
    if level < 1 or level > 5:
        raise ValueError("Level must be between 1 and 5")

    rules = db.query(Rule).all()
    count = 0
    for rule in rules:
        rule.hint_level = level
        if level != 5:
            rule.level_5_unlocked = False
            rule.unlock_until = None
        count += 1

    db.commit()
    _cache_clear()
    return count


def unlock_level_5(db: DBSession, ip_address: str, duration_minutes: int | None = None) -> Rule:
    """
    Temporarily unlock Level 5 for a student.

    If duration_minutes is provided, Level 5 will auto-lock after that time.
    Otherwise it stays unlocked until the teacher manually locks it.
    Maximum unlock duration is 60 minutes.
    """
    rule = get_or_create_rule(db, ip_address)
    rule.level_5_unlocked = True
    rule.hint_level = 5

    if duration_minutes and duration_minutes > 0:
        capped = min(duration_minutes, 60)
        rule.unlock_until = datetime.now(timezone.utc).replace(tzinfo=None).replace(
            second=0, microsecond=0
        ) + timedelta(minutes=capped)
    else:
        rule.unlock_until = None

    db.commit()
    db.refresh(rule)
    _cache_invalidate(ip_address)
    return rule
