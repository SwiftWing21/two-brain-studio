"""Application state — persisted project config + active engine."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger("scorerift_studio")

CONFIG_DIR = Path.home() / ".scorerift-studio"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_app_config() -> dict[str, Any]:
    """Load studio config (recent projects, preferences)."""
    _ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            log.warning("Failed to parse config", exc_info=True)
    return {"recent_projects": [], "theme": "dark", "window": {"width": 1200, "height": 800}}


def save_app_config(config: dict[str, Any]) -> None:
    """Persist studio config."""
    _ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def add_recent_project(project_path: str) -> None:
    """Add a project to the recent list (dedup, max 10)."""
    config = load_app_config()
    recents = config.get("recent_projects", [])
    # Remove if already present, then prepend
    recents = [p for p in recents if p != project_path]
    recents.insert(0, project_path)
    config["recent_projects"] = recents[:10]
    save_app_config(config)
