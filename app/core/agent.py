"""The orchestrator: question -> schema retrieval -> SQL generation ->
validate -> execute -> (retry on failure) -> result + NL summary.
"""
from dataclasses import dataclass, field

from app.core import prompts
from app.core.executor import ExecutionError, run_query
from app.core.llm_client import LLMClient
from app.core.schema_store import retrieve_relevant_tables, schema_prompt_block
from app.core.validator import ValidationError, validate_and_normalize

MAX_RETRIES = 3


@dataclass
class AgentResult:
    question: str
    sql: str | None = None
    columns: list[str] = field(default_factory=list)
    rows: list[tuple] = field(default_factory=list)
    summary: str | None = None
    provider: str | None = None
    attempts: int = 0
    error: str | None = None


def answer_question(question: str, llm: LLMClient | None = None) -> AgentResult:
    llm = llm or LLMClient()
    result = AgentResult(question=question)

    tables = retrieve_relevant_tables(question)
    schema_block = schema_prompt_block(tables)
    known_table_names = {t.name.lower() for t in tables}

    system_prompt = prompts.SQL_SYSTEM_PROMPT
    user_prompt = prompts.build_sql_user_prompt(question, schema_block)

    last_sql, last_error = None, None
    candidate_sql = None

    for attempt in range(1, MAX_RETRIES + 1):
        result.attempts = attempt
        try:
            parsed, provider = llm.complete_json(system_prompt, user_prompt)
            result.provider = provider
            candidate_sql = parsed.get("sql", "")

            if not candidate_sql:
                result.error = parsed.get("assumptions") or "Model declined to generate SQL."
                return result

            normalized_sql = validate_and_normalize(candidate_sql, known_table_names)
            columns, rows = run_query(normalized_sql)

            result.sql = normalized_sql
            result.columns = columns
            result.rows = rows
            result.summary = _summarize(llm, question, columns, rows)
            return result

        except (ValidationError, ExecutionError) as e:
            last_sql, last_error = candidate_sql, str(e)
            system_prompt = prompts.SQL_RETRY_SYSTEM_PROMPT
            user_prompt = prompts.build_retry_user_prompt(question, schema_block, last_sql or "", last_error)

    result.error = f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    result.sql = last_sql
    return result


def _summarize(llm: LLMClient, question: str, columns: list[str], rows: list[tuple]) -> str:
    try:
        user_prompt = prompts.build_summary_user_prompt(question, columns, rows)
        parsed, _ = llm.complete_json(prompts.SUMMARY_SYSTEM_PROMPT, user_prompt)
        return parsed.get("summary", "")
    except Exception:
        return ""  # summary is a nice-to-have; never fail the whole request over it
