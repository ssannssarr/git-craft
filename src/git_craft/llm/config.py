"""Load Git Craft settings from JSONC and environment variables."""

import json
import os
from pathlib import Path

HOME = Path.home()
CONFIG_DIR = HOME / ".config" / "gitCraft"
CONFIG_FILE = CONFIG_DIR / "config.jsonc"


def _strip_jsonc_comments(source: str) -> str:
    """Remove line and block comments while preserving quoted strings."""
    output = []
    in_string = escaped = False
    index = 0
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            output.append(char)
            index += 1
        elif char == "/" and next_char == "/":
            while index < len(source) and source[index] not in "\r\n":
                index += 1
        elif char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(source) and source[index:index + 2] != "*/":
                index += 1
            index = min(index + 2, len(source))
        else:
            output.append(char)
            index += 1
    return "".join(output)


def load_config() -> dict[str, str]:
    """Load user configuration, with environment variables taking precedence."""
    config = {}

    if CONFIG_FILE.exists():
        try:
            data = json.loads(_strip_jsonc_comments(CONFIG_FILE.read_text()))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not read configuration at {CONFIG_FILE}: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"Configuration at {CONFIG_FILE} must contain a JSON object.")
        config.update(data)

    env_mapping = {
        "api_key": "APIKEY",
        "model_id": "MODELID",
        "base_url": "BASEURL",
    }
    env_prefix = "GITCRAFT"
    for key, env_suffix in env_mapping.items():
        env_var = f"{env_prefix}_{env_suffix}"
        value = os.environ.get(env_var)
        if value:
            config[key] = value

    return config
