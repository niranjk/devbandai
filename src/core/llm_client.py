from __future__ import annotations

import os

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class LLMError(Exception):
    """Raised when the LLM backend is unreachable or returns a malformed response."""


class LocalQwenClient:
    """OpenAI-compatible client targeting a local Ollama / vLLM endpoint."""

    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
        timeout: float = 90.0,
    ):
        self.model_name = model_name or os.environ.get(
            "MODEL_NAME", "qwen2.5-coder"
        )
        self.base_url = base_url or os.environ.get(
            "LOCAL_LLM_URL", "http://localhost:11434/v1/chat/completions"
        )
        self.timeout = timeout

    @retry(
        retry=retry_if_exception_type(LLMError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> str:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.base_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise LLMError(f"LLM request timed out after {self.timeout}s") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"LLM HTTP {exc.response.status_code}: {exc.response.text[:300]}"
            ) from exc
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Malformed LLM response: {exc}") from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM connection error: {exc}") from exc
        except Exception as exc:
            raise LLMError(f"Unexpected LLM error: {exc}") from exc

    def is_available(self) -> bool:
        try:
            self.generate_response("ping", "ping")
            return True
        except LLMError:
            return False
