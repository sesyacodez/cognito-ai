"""
Agent runner — loads skill specs, calls OpenRouter with them as tools,
and executes the skill the model selects.
"""

import importlib
import json
import os

import httpx
from pydantic import ValidationError

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen3-coder:free"


class AgentError(Exception):
    """Raised when the agent runner cannot produce a valid result after retries."""


def _get_skill(skill_name: str):
    """Dynamically import a skill module from backend/skills/<skill_name>.py."""
    try:
        return importlib.import_module(f"skills.{skill_name}")
    except ModuleNotFoundError:
        raise AgentError(f"Unknown skill: '{skill_name}'")


def _call_openrouter(messages: list, tools: list, api_key: str, model: str) -> dict:
    """
    POST to OpenRouter's chat completions endpoint.
    Returns the parsed response dict or raises AgentError on HTTP/network failure.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cognito.ai",
        "X-Title": "Cognito AI",
    }
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": "required",
    }
    try:
        response = httpx.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise AgentError(
            f"OpenRouter returned {exc.response.status_code}: {exc.response.text}"
        ) from exc
    except httpx.RequestError as exc:
        raise AgentError(f"Network error calling OpenRouter: {exc}") from exc


def _extract_tool_args(response: dict, skill_name: str) -> dict:
    """
    Extract the tool call arguments from the model response.
    Returns parsed dict or raises AgentError if the shape is unexpected.
    """
    try:
        choices = response["choices"]
        message = choices[0]["message"]
        tool_calls = message.get("tool_calls", [])
        if not tool_calls:
            raise AgentError("Model did not return a tool call.")
        # Find the tool call matching our skill (there should only be one)
        for call in tool_calls:
            if call["function"]["name"] == skill_name:
                return json.loads(call["function"]["arguments"])
        raise AgentError(
            f"Model did not call the '{skill_name}' tool. Got: "
            + str([c["function"]["name"] for c in tool_calls])
        )
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise AgentError(f"Unexpected response shape from OpenRouter: {exc}") from exc


def run_skill(skill_name: str, mode: str = "learn", **kwargs) -> dict:
    """
    Run a named skill via OpenRouter tool-calling.

    1. Load the skill module from backend/skills/<skill_name>.py
    2. Read the skill's SPEC and SYSTEM_PROMPTS
    3. Send to OpenRouter; model calls the tool with structured arguments
    4. Execute skill.run(params, mode) and return the result
    5. Retry once on malformed output; raise AgentError on repeated failure

    Raises:
        AgentError: if the API key is missing, the model fails twice,
                    or the skill output is invalid.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise AgentError(
            "OPENROUTER_API_KEY is not set. Cannot call the skill runner."
        )

    model = os.environ.get("DECOMPOSER_MODEL", DEFAULT_MODEL)
    skill = _get_skill(skill_name)

    topic = kwargs.get("topic", "")
    system_prompt = skill.SYSTEM_PROMPTS.get(mode, skill.SYSTEM_PROMPTS.get("learn"))
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Topic: {topic}"},
    ]
    tools = [skill.SPEC]

    last_error: AgentError | None = None

    for attempt in range(2):
        retry_messages = messages
        if attempt == 1:
            # On retry, add an explicit reminder to follow the schema strictly
            retry_messages = messages + [
                {
                    "role": "user",
                    "content": (
                        "Your previous response was not valid. "
                        "Please call the tool again and return ONLY valid JSON "
                        "matching the schema exactly."
                    ),
                }
            ]
        try:
            response = _call_openrouter(retry_messages, tools, api_key, model)
            params = _extract_tool_args(response, skill_name)
            result = skill.run(params, mode=mode)
            return result
        except (AgentError, ValidationError) as exc:
            last_error = AgentError(str(exc))
            continue

    raise last_error or AgentError("Unknown error in skill runner.")
