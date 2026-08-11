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
        groq_model: str = "llama-3.3-70b-versatile",
        gemini_model: str = "gemini-flash-latest",
    ):
        self.groq_model = groq_model
        self.gemini_model = gemini_model
        self._groq = None
        self._gemini = None

    def _groq_client(self):
        if self._groq is None:
            from groq import Groq
            self._groq = Groq(api_key=os.environ["GROQ_API_KEY"])
        return self._groq

    def _gemini_client(self):
        if self._gemini is None:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            self._gemini = genai.GenerativeModel(self.gemini_model)
        return self._gemini

    def complete_json(self, system_prompt: str, user_prompt: str) -> tuple[dict, str]:
        """Calls the LLM and parses a JSON object from the response.
        Tries Groq first, falls back to Gemini on any failure (rate limit,
        network error, missing key). Returns (parsed_json, provider_name)."""
        try:
            return self._complete_groq(system_prompt, user_prompt), "groq"
        except Exception as groq_err:
            if "GEMINI_API_KEY" not in os.environ:
                raise RuntimeError(f"Groq failed and no Gemini fallback configured: {groq_err}")
            return self._complete_gemini(system_prompt, user_prompt), "gemini"

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
        return json.loads(resp.choices[0].message.content)

    def _complete_gemini(self, system_prompt: str, user_prompt: str) -> dict:
        client = self._gemini_client()
        resp = client.generate_content(
            f"{system_prompt}\n\n{user_prompt}\n\nRespond with JSON only, no markdown fences.",
            generation_config={"temperature": 0, "response_mime_type": "application/json"},
        )
        return json.loads(resp.text)
