"""Anthropic Claude client wrapper with retry and structured response parsing."""

from __future__ import annotations

import re
import time
from typing import Any

import anthropic

from assume_break.config import get_settings

_client: anthropic.Anthropic | None = None
_async_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.Anthropic:
    """Create or return a singleton Anthropic client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def get_async_client() -> anthropic.AsyncAnthropic:
    """Create or return a singleton async Anthropic client."""
    global _async_client
    if _async_client is None:
        settings = get_settings()
        _async_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _async_client


class NoAPIKeyError(Exception):
    """Raised when no Anthropic API key is configured."""


def call_claude(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    max_retries: int = 3,
) -> str:
    """Synchronous call to Claude with exponential backoff retry.

    Returns the text content of Claude's response.
    Raises NoAPIKeyError if no API key is configured.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise NoAPIKeyError("No ANTHROPIC_API_KEY configured. Using rule-based fallback.")
    client = get_client()
    model = model or settings.claude_model

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except anthropic.RateLimitError as e:
            last_error = e
            wait = 2 ** (attempt + 1)
            time.sleep(wait)
        except anthropic.APIError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise

    raise last_error  # type: ignore[misc]


async def call_claude_async(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    max_retries: int = 3,
) -> str:
    """Async call to Claude with exponential backoff retry."""
    import asyncio

    settings = get_settings()
    client = get_async_client()
    model = model or settings.claude_model

    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text
        except anthropic.RateLimitError as e:
            last_error = e
            wait = 2 ** (attempt + 1)
            await asyncio.sleep(wait)
        except anthropic.APIError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                await asyncio.sleep(wait)
            else:
                raise

    raise last_error  # type: ignore[misc]


def parse_structured_response(response: str, expected_fields: list[str]) -> list[dict[str, Any]]:
    """Parse structured FRACTURE/REALITY/CITATION/VERDICT/IMPACT blocks from Claude's response.

    Extracts blocks where each field appears as 'FIELD: value' on its own line.
    Returns a list of dicts, one per block.
    """
    blocks: list[dict[str, Any]] = []

    # Split on the first expected field to find block boundaries
    primary_field = expected_fields[0]
    pattern = rf"(?:^|\n)\s*{re.escape(primary_field)}\s*:"
    parts = re.split(pattern, response, flags=re.IGNORECASE)

    for part in parts[1:]:  # Skip text before first block
        block: dict[str, Any] = {}
        # Re-add the primary field marker for parsing
        text = f"{primary_field}: {part}"

        for field_name in expected_fields:
            field_pattern = rf"{re.escape(field_name)}\s*:\s*(.+?)(?=\n\s*(?:{'|'.join(re.escape(f) for f in expected_fields)})\s*:|\Z)"
            match = re.search(field_pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                block[field_name.lower()] = match.group(1).strip()

        if block:
            blocks.append(block)

    return blocks
