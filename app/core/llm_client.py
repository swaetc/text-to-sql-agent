"""Thin LLM client with Groq as primary and Gemini as fallback.

Both are free-tier. Keeping this behind one interface means the rest of the
agent doesn't care which provider actually answered — useful since free
tiers get rate-limited, and providers occasionally retire models.

Env vars expected:
  GROQ_API_KEY
  GEMINI_API_KEY   (optional but recommended as a fallback)
"""
import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    text: str
    provider: str


class LLMClient:
    def __init__(
        self,
        groq_model: str | None = None,
        gemini_model: str | None = None,
    ):
        self.groq_model = groq_model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.gemini_model = gemini_model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._groq = None
        self._gemini = None

    def _groq_client(self):
        if self._groq is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")
            from groq import Groq
            self._groq = Groq(api_key=api_key)
        return self._groq

    def _gemini_client(self):
        if self._gemini is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._gemini = genai.GenerativeModel(self.gemini_model)
        return self._gemini

    @staticmethod
    def _parse_json_response(raw_text: str) -> dict:
        text = raw_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def complete_json(self, system_prompt: str, user_prompt: str) -> tuple[dict, str]:
        """Calls the LLM and parses a JSON object from the response.
        Tries Groq first if available, falls back to Gemini on any failure
        (rate limit, network error, missing key). Returns (parsed_json, provider_name)."""
        groq_error = None
        has_groq_key = bool(os.getenv("GROQ_API_KEY"))
        has_gemini_key = bool(os.getenv("GEMINI_API_KEY"))

        if not has_groq_key and not has_gemini_key:
            raise RuntimeError(
                "No LLM API keys configured. Please set GROQ_API_KEY or GEMINI_API_KEY environment variable."
            )

        if has_groq_key:
            try:
                return self._complete_groq(system_prompt, user_prompt), "groq"
            except Exception as e:
                groq_error = e

        if has_gemini_key:
            try:
                return self._complete_gemini(system_prompt, user_prompt), "gemini"
            except Exception as gemini_error:
                if groq_error:
                    raise RuntimeError(
                        f"Both Groq and Gemini failed. Groq: {groq_error} | Gemini: {gemini_error}"
                    ) from gemini_error
                raise RuntimeError(f"Gemini failed: {gemini_error}") from gemini_error

        raise RuntimeError(
            f"Groq request failed and GEMINI_API_KEY is not configured: {groq_error}"
        )

    def _complete_groq(self, system_prompt: str, user_prompt: str) -> dict:
        client = self._groq_client()
        resp = client.chat.completions.create(
            model=self.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content or "{}"
        return self._parse_json_response(content)

    def _complete_gemini(self, system_prompt: str, user_prompt: str) -> dict:
        client = self._gemini_client()
        resp = client.generate_content(
            f"{system_prompt}\n\n{user_prompt}\n\nRespond with JSON only, no markdown fences.",
            generation_config={"temperature": 0, "response_mime_type": "application/json"},
        )
        return self._parse_json_response(resp.text or "{}")
