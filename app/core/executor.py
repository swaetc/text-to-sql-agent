"""Executes validated SQL against a read-only SQLite connection.

SQLite doesn't have DB-level user roles like Postgres, so read-only is
enforced by opening the file in URI mode=ro (the OS-level file handle
literally cannot write) plus a busy timeout so a runaway query can't hang
the process. If you swap in Postgres, do this with a dedicated read-only
role (`GRANT SELECT ONLY`) instead.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "store.db"
QUERY_TIMEOUT_SECONDS = 5


class ExecutionError(Exception):
    pass


def run_query(sql: str) -> tuple[list[str], list[tuple]]:
    uri = f"file:{DB_PATH}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=QUERY_TIMEOUT_SECONDS)
        cur = conn.cursor()
        cur.execute(sql)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        conn.close()
        return columns, rows
    except sqlite3.Error as e:
        raise ExecutionError(str(e))
