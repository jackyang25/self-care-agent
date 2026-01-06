"""configuration and prompt building for agent."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pytz
import yaml

from src.shared.logger import get_logger

logger = get_logger("agent.config")

# agent configuration (can be overridden via environment variables)
LLM_MODEL = os.getenv("AGENT_MODEL", "gpt-4o")
TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.0"))

# prompt configuration
DEFAULT_PROMPT_VERSION = "v1"
_AGENT_DIR = Path(__file__).resolve().parent


def _get_prompt_path() -> Path:
    """get path to system prompt yaml file."""
    return _AGENT_DIR / "system_prompt.yaml"


def load_prompt() -> Dict[str, str]:
    """load system prompt from yaml file.

    supports environment variable overrides:
    - SYSTEM_PROMPT_PATH: custom path to prompt yaml file
    - SYSTEM_PROMPT_VERSION: override version metadata

    returns:
        dict with 'prompt', 'version', and 'path' keys

    raises:
        FileNotFoundError: if prompt file not found
        ValueError: if prompt file missing 'prompt' field
    """
    prompt_path_env = os.getenv("SYSTEM_PROMPT_PATH")
    prompt_path = (
        Path(prompt_path_env).expanduser()
        if prompt_path_env
        else _get_prompt_path()
    )

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"system prompt file not found at {prompt_path}. "
            f"ensure src/application/agent/system_prompt.yaml exists or set SYSTEM_PROMPT_PATH."
        )

    try:
        data = yaml.safe_load(prompt_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ValueError(f"failed to parse yaml from {prompt_path}: {exc}") from exc

    prompt_text = data.get("prompt")
    if not prompt_text:
        raise ValueError(f"missing 'prompt' field in {prompt_path}")

    prompt_version = str(data.get("version", DEFAULT_PROMPT_VERSION))

    # allow env override for version metadata
    env_version = os.getenv("SYSTEM_PROMPT_VERSION")
    if env_version:
        prompt_version = env_version

    return {
        "prompt": prompt_text,
        "version": prompt_version,
        "path": str(prompt_path),
    }


# load prompt at module initialization
PROMPT_DATA = load_prompt()

# agent configuration dict (for backward compatibility)
AGENT_CONFIG = {
    "llm_model": LLM_MODEL,
    "temperature": TEMPERATURE,
}

logger.info(
    f"loaded prompt version={PROMPT_DATA['version']} from {PROMPT_DATA['path']}"
)
logger.info(
    f"agent config: model={LLM_MODEL}, temperature={TEMPERATURE}"
)


def build_patient_context(
    age: Optional[int],
    gender: Optional[str],
    timezone: str,
    country: Optional[str] = None,
) -> str:
    """build patient context section for system prompt.

    args:
        age: patient age
        gender: patient gender
        timezone: patient timezone (e.g., "America/New_York")
        country: patient country context (e.g., "za", "ke", "us")

    returns:
        formatted context string to append to system prompt
    """
    context_parts = []

    # add current time in user's timezone
    try:
        tz = pytz.timezone(timezone) if timezone else pytz.UTC
        current_time = datetime.now(tz)
        time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p %Z")
    except Exception:
        current_time = datetime.now(pytz.UTC)
        time_str = current_time.strftime("%A, %B %d, %Y at %I:%M %p UTC")

    context_parts.append(f"Current time: {time_str}")

    if age is not None:
        context_parts.append(f"Age: {age}")
    if gender is not None:
        context_parts.append(f"Gender: {gender}")
    if country is not None:
        context_parts.append(f"Country: {country}")

    if not context_parts:
        return ""

    context_lines = "\n".join(f"- {part}" for part in context_parts)
    return (
        f"\n\n## current patient context\n\n{context_lines}\n\n"
        f"use this information to provide appropriate, personalized care. "
        f"use the current time to schedule appointments appropriately "
        f"(e.g., 'tomorrow' means the next day from current time). "
        f"when using rag_retrieval, country-specific clinical guidelines will be prioritized."
    )
