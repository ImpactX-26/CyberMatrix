
"""
Minimal LLM wrapper for the LandRegistry agent.

The agent expects:

    llm.complete(messages)

This module deliberately keeps provider-specific code outside agent.py.

Supported modes:
- groq / any OpenAI-compatible remote endpoint
- gemini / Gemini OpenAI-compatible endpoint
- ollama / local Ollama

Environment variables:

Remote OpenAI-compatible:
    LANDREG_LLM_PROVIDER=groq
    LANDREG_LLM_API_KEY=...
    LANDREG_LLM_BASE_URL=https://api.groq.com/openai/v1
    LANDREG_LLM_MODEL=...

Gemini:
    LANDREG_LLM_PROVIDER=gemini
    LANDREG_LLM_API_KEY=...
    LANDREG_LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
    LANDREG_LLM_MODEL=...

Ollama:
    LANDREG_LLM_PROVIDER=ollama
    LANDREG_LLM_BASE_URL=http://localhost:11434/v1
    LANDREG_LLM_MODEL=...

No API key is required for Ollama.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class LLMError(Exception):
    """Base error for LLM wrapper failures."""


class LLMTimeoutError(LLMError):
    """Raised when the provider request times out."""


class LLMRateLimitError(LLMError):
    """Raised when the provider returns HTTP 429."""


class LLMProviderError(LLMError):
    """Raised for other provider/API errors."""


DEFAULT_BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "ollama": "http://localhost:11434/v1",
}


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _provider() -> str:
    return _env("LANDREG_LLM_PROVIDER", "").lower()


def _base_url(provider: str) -> str:
    value = _env("LANDREG_LLM_BASE_URL")

    if value:
        return value.rstrip("/")

    return DEFAULT_BASE_URLS.get(provider, "").rstrip("/")


def _model() -> str:
    return _env("LANDREG_LLM_MODEL")


def _api_key(provider: str) -> str:
    if provider == "ollama":
        return _env("LANDREG_LLM_API_KEY", "ollama")

    return _env("LANDREG_LLM_API_KEY")


def _request_payload(
    messages: list[dict[str, str]],
    model: str,
) -> dict[str, Any]:
    return {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 300,
    }


def _extract_content(payload: dict[str, Any]) -> Any:
    choices = payload.get("choices")

    if not isinstance(choices, list) or not choices:
        raise LLMProviderError(
            "LLM response did not contain choices"
        )

    first = choices[0]

    if not isinstance(first, dict):
        raise LLMProviderError(
            "LLM response choice is invalid"
        )

    message = first.get("message")

    if isinstance(message, dict):
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, dict):
            return content

    text = first.get("text")

    if isinstance(text, str):
        return text

    raise LLMProviderError(
        "LLM response did not contain text content"
    )


class LLMClient:
    """Small provider-neutral client implementing complete()."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.provider = (
            provider.strip().lower()
            if provider
            else _provider()
        )

        self.model = (
            model.strip()
            if model
            else _model()
        )

        self.base_url = (
            base_url.rstrip("/")
            if base_url
            else _base_url(self.provider)
        )

        self.api_key = (
            api_key
            if api_key is not None
            else _api_key(self.provider)
        )

        self.timeout = float(timeout)

    def complete(
        self,
        messages: list[dict[str, str]],
    ) -> Any:
        """Return the provider's generated content."""

        if not self.provider:
            raise LLMProviderError(
                "LANDREG_LLM_PROVIDER is not configured"
            )

        if not self.model:
            raise LLMProviderError(
                "LANDREG_LLM_MODEL is not configured"
            )

        if not self.base_url:
            raise LLMProviderError(
                f"no base URL configured for provider: {self.provider}"
            )

        if not isinstance(messages, list) or not messages:
            raise LLMProviderError(
                "messages must be a non-empty list"
            )

        endpoint = self.base_url + "/chat/completions"

        payload = _request_payload(
            messages,
            self.model,
        )

        body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw = response.read().decode("utf-8")

        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise LLMRateLimitError(
                    "LLM provider returned HTTP 429"
                ) from exc

            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = ""

            raise LLMProviderError(
                f"LLM provider returned HTTP {exc.code}: {detail[:500]}"
            ) from exc

        except TimeoutError as exc:
            raise LLMTimeoutError(
                "LLM request timed out"
            ) from exc

        except urllib.error.URLError as exc:
            reason = str(exc.reason)

            if "timed out" in reason.lower():
                raise LLMTimeoutError(
                    "LLM request timed out"
                ) from exc

            raise LLMProviderError(
                f"LLM connection failed: {reason}"
            ) from exc

        try:
            response_payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(
                "LLM provider returned invalid JSON"
            ) from exc

        if not isinstance(response_payload, dict):
            raise LLMProviderError(
                "LLM provider response must be a JSON object"
            )

        return _extract_content(response_payload)


def get_client() -> LLMClient:
    """Return a client configured from environment variables."""
    return LLMClient()


def complete(
    messages: list[dict[str, str]],
) -> Any:
    """Module-level convenience function."""
    return get_client().complete(messages)


if __name__ == "__main__":
    client = get_client()

    print(
        json.dumps(
            {
                "provider": client.provider,
                "model": client.model,
                "base_url": client.base_url,
                "configured": bool(
                    client.provider
                    and client.model
                    and client.base_url
                ),
            },
            indent=2,
        )
    )

