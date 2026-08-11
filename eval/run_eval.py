"""Runs the agent against eval/questions.json and scores it by execution match:
does the agent's query return the same result set as the hand-written expected
SQL? This is more robust than comparing SQL text, since there are many valid
ways to write the same query.

Run: python -m eval.run_eval
"""
import json
from pathlib import Path

from app.core.agent import answer_question
from app.core.executor import ExecutionError, run_query

QUESTIONS_PATH = Path(__file__).parent / "questions.json"


def rows_match(
    got_columns: list[str], got_rows: list[tuple],
    exp_columns: list[str], exp_rows: list[tuple],
) -> bool:
    """Compares result sets by execution match, not by exact column set: the
    agent is free to choose a different (but overlapping) set of columns than
    the hand-written expected SQL — e.g. dropping a column that's constant
    across all rows because it was already the WHERE filter. We project both
    sides onto whatever columns they share by name and compare those. If the
    two queries share no column names at all, fall back to a raw comparison,
    since there's no shared basis to project onto."""
    got_lower = [c.lower() for c in got_columns]
    exp_lower = [c.lower() for c in exp_columns]
    shared = [c for c in exp_lower if c in got_lower]

    if not shared:
        return sorted(map(str, got_rows)) == sorted(map(str, exp_rows))

    got_idx = [got_lower.index(c) for c in shared]
    exp_idx = [exp_lower.index(c) for c in shared]

    got_projected = [tuple(row[i] for i in got_idx) for row in got_rows]
    exp_projected = [tuple(row[i] for i in exp_idx) for row in exp_rows]
    return sorted(map(str, got_projected)) == sorted(map(str, exp_projected))


def run():
    questions = json.loads(QUESTIONS_PATH.read_text())
    passed, failed = 0, []

    for q in questions:
        result = answer_question(q["question"])

        if q["expected_sql"] == "":
            # This question should NOT get a confident SQL answer.
            ok = result.sql is None or result.error is not None
            outcome = "correctly declined" if ok else "incorrectly answered"
        else:
            try:
                expected_columns, expected_rows = run_query(q["expected_sql"])
            except ExecutionError as e:
                outcome = f"expected_sql itself is broken: {e}"
                ok = False
            else:
                ok = bool(result.rows) and rows_match(
                    result.columns, result.rows, expected_columns, expected_rows
                )
                outcome = "match" if ok else "mismatch"

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {q['id']:16s} ({q['category']:24s}) - {outcome}")
        if ok:
            passed += 1
        else:
            failed.append(q["id"])

    total = len(questions)
    print(f"\n{passed}/{total} passed ({passed / total:.0%})")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    run()
