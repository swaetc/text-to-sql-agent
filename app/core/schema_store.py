"""Introspects the SQLite DB and retrieves the tables relevant to a question.

For a schema this small (4-5 tables), we don't need a vector DB — a simple
keyword-overlap score between the question and each table's name/columns/
description is enough, and it's free, fast, and has zero extra dependencies.
Swap in embeddings (sentence-transformers + Chroma) if you grow past ~15 tables.
"""
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "store.db"

# Short human descriptions help both retrieval and the LLM prompt.
TABLE_DESCRIPTIONS = {
    "customers": "People who place orders: name, email, city, signup date.",
    "products": "Items for sale: name, category, unit price.",
    "orders": "An order placed by a customer: date, status "
              "(one of: pending, shipped, delivered, cancelled — no other statuses exist).",
    "order_items": "Line items within an order: product, quantity, price at time of order.",
}


@dataclass
class TableInfo:
    name: str
    columns: list[str] = field(default_factory=list)
    foreign_keys: list[str] = field(default_factory=list)
    description: str = ""

    def as_prompt_block(self) -> str:
        cols = ", ".join(self.columns)
        fk = f"\n  Foreign keys: {'; '.join(self.foreign_keys)}" if self.foreign_keys else ""
        return f"- {self.name}({cols}){fk}\n  {self.description}"


def load_all_tables(db_path: Path = DB_PATH) -> list[TableInfo]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = []
    for (table_name,) in cur.fetchall():
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cur.fetchall()]

        cur.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = [f"{table_name}.{row[3]} -> {row[2]}.{row[4]}" for row in cur.fetchall()]

        tables.append(TableInfo(
            name=table_name,
            columns=columns,
            foreign_keys=fks,
            description=TABLE_DESCRIPTIONS.get(table_name, ""),
        ))
    conn.close()
    return tables


def _score(question: str, table: TableInfo) -> int:
    words = set(re.findall(r"[a-z]+", question.lower()))
    haystack = " ".join([table.name] + table.columns + [table.description]).lower()
    return sum(1 for w in words if w in haystack)


def retrieve_relevant_tables(question: str, top_k: int = 4) -> list[TableInfo]:
    """Returns the top_k most relevant tables for a question, ranked by
    keyword overlap. At this demo's scale (4 tables) top_k=4 means retrieval
    effectively returns the whole schema every time — that's fine, and safer
    than a min_score cutoff silently dropping a table the SQL needs (e.g. a
    'spend' question needing order_items, which has zero keyword overlap
    with 'spend' itself). The scoring still matters once you grow past ~10
    tables and lower top_k to actually trim the prompt."""
    all_tables = load_all_tables()
    scored = sorted(all_tables, key=lambda t: _score(question, t), reverse=True)
    return scored[:top_k]


def schema_prompt_block(tables: list[TableInfo]) -> str:
    return "\n".join(t.as_prompt_block() for t in tables)
