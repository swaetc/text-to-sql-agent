"""Validates generated SQL before it ever touches the database.

Two layers of defense:
1. This validator (parse + allow-list check) — catches obviously bad SQL cheaply.
2. The read-only DB connection in executor.py — catches anything that slips through.
Never rely on either alone.
"""
import sqlglot
from sqlglot import exp

ALLOWED_STATEMENT = exp.Select
DISALLOWED_KEYWORDS = {
    "insert", "update", "delete", "drop", "alter", "create",
    "attach", "detach", "pragma", "replace", "truncate",
}
DEFAULT_ROW_LIMIT = 200


class ValidationError(Exception):
    pass


def validate_and_normalize(sql: str, known_tables: set[str]) -> str:
    """Raises ValidationError with a human-readable reason on any problem.
    Returns a normalized SQL string (with a LIMIT injected if missing)."""
    sql = sql.strip().rstrip(";")

    lowered = sql.lower()
    for kw in DISALLOWED_KEYWORDS:
        if kw in lowered.split():
            raise ValidationError(f"Disallowed keyword detected: '{kw}'. Only SELECT is permitted.")

    try:
        parsed = sqlglot.parse_one(sql, read="sqlite")
    except Exception as e:
        raise ValidationError(f"SQL failed to parse: {e}")

    if not isinstance(parsed, ALLOWED_STATEMENT):
        raise ValidationError("Only SELECT statements are permitted.")

    referenced_tables = {t.name.lower() for t in parsed.find_all(exp.Table)}
    unknown = referenced_tables - known_tables
    if unknown:
        raise ValidationError(f"Query references unknown table(s): {', '.join(unknown)}")

    if parsed.args.get("limit") is None:
        parsed = parsed.limit(DEFAULT_ROW_LIMIT)

    return parsed.sql(dialect="sqlite")
