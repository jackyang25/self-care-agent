"""configuration loading for agent."""

import os
from pathlib import Path
from typing import Dict, Any

import yaml

from src.utils.logger import get_logger

logger = get_logger("agent.config")

# configuration paths and defaults
_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "config"
DEFAULT_PROMPT_VERSION = "v1"


def _get_system_prompt_path() -> Path:
    """get path to system prompt yaml file."""
    return _CONFIG_DIR / "system_prompt.yaml"


def _get_agent_config_path() -> Path:
    """get path to agent config yaml file."""
    return _CONFIG_DIR / "agent_config.yaml"


def load_agent_config() -> Dict[str, Any]:
    """load agent configuration from yaml file.

    returns:
        dict with 'llm_model' and 'temperature' keys

    raises:
        FileNotFoundError: if config file not found
        ValueError: if config file missing required fields
    """
    config_path = _get_agent_config_path()

    if not config_path.exists():
        raise FileNotFoundError(
            f"agent config file not found at {config_path}. "
            f"ensure config/agent_config.yaml exists."
        )

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ValueError(f"failed to parse yaml from {config_path}: {exc}") from exc

    llm_model = data.get("llm_model")
    temperature = data.get("temperature")

    if not llm_model:
        raise ValueError(f"missing 'llm_model' field in {config_path}")
    if temperature is None:
        raise ValueError(f"missing 'temperature' field in {config_path}")

    return {
        "llm_model": llm_model,
        "temperature": float(temperature),
    }


def load_system_prompt() -> Dict[str, str]:
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
        else _get_system_prompt_path()
    )

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"system prompt file not found at {prompt_path}. "
            f"ensure config/system_prompt.yaml exists or set SYSTEM_PROMPT_PATH."
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


# load configurations at module initialization
SYSTEM_PROMPT_DATA = load_system_prompt()
AGENT_CONFIG = load_agent_config()

logger.info(
    f"loaded system prompt version={SYSTEM_PROMPT_DATA['version']} from {SYSTEM_PROMPT_DATA['path']}"
)
logger.info(
    f"loaded agent config: model={AGENT_CONFIG['llm_model']}, temperature={AGENT_CONFIG['temperature']}"
)

