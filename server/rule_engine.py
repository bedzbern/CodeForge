"""
Rule Engine for CodeForge.

Loads per-IP hint levels from the database and enforces them.
Manages Level 5 unlock state with optional time limits.
"""

from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from server.models import Student, Rule


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

    If Level 5 is unlocked and the unlock window has not expired, returns 5.
    Otherwise returns the student's configured hint_level.
    """
    rule = get_or_create_rule(db, ip_address)

    if rule.level_5_unlocked and rule.unlock_until:
        if datetime.utcnow() < rule.unlock_until:
            return 5
        else:
            rule.level_5_unlocked = False
            rule.unlock_until = None
            db.commit()

    if rule.level_5_unlocked and rule.unlock_until is None:
        return 5

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
    return count


def unlock_level_5(db: DBSession, ip_address: str, duration_minutes: int | None = None) -> Rule:
    """
    Temporarily unlock Level 5 for a student.

    If duration_minutes is provided, Level 5 will auto-lock after that time.
    Otherwise it stays unlocked until the teacher manually locks it.
    """
    rule = get_or_create_rule(db, ip_address)
    rule.level_5_unlocked = True
    rule.hint_level = 5

    if duration_minutes and duration_minutes > 0:
        rule.unlock_until = datetime.utcnow().replace(
            second=0, microsecond=0
        ) + __import__("datetime").timedelta(minutes=duration_minutes)
    else:
        rule.unlock_until = None

    db.commit()
    db.refresh(rule)
    return rule
