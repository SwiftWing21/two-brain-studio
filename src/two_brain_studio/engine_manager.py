"""Manages the active AuditEngine instance for the current project."""

from __future__ import annotations

import importlib
import json
import logging
import threading
from pathlib import Path
from typing import Any

log = logging.getLogger("two_brain_studio")

_engine = None
_project_path = None
_lock = threading.Lock()


def get_engine():
    """Return the active AuditEngine, or None if no project is loaded."""
    with _lock:
        return _engine


def get_project_path() -> str | None:
    """Return the active project directory path."""
    with _lock:
        return _project_path


def unload_project() -> None:
    """Close the current project and release resources."""
    global _engine, _project_path
    with _lock:
        if _engine is not None:
            if hasattr(_engine, "close"):
                try:
                    _engine.close()
                except Exception:
                    log.warning("Error closing engine", exc_info=True)
            _engine = None
        _project_path = None


def load_project(project_dir: str) -> dict[str, Any]:
    """Load or initialize a two-brain-audit project in the given directory."""
    global _engine, _project_path
    from two_brain_audit import AuditEngine

    with _lock:
        # Close previous project if open
        if _engine is not None and hasattr(_engine, "close"):
            try:
                _engine.close()
            except Exception:
                log.warning("Error closing previous engine", exc_info=True)

        project = Path(project_dir)
        db_path = str(project / "audit.db")
        baseline_path = str(project / "audit_baseline.json")

        _engine = AuditEngine(db_path=db_path, baseline_path=baseline_path)
        _project_path = str(project)

        baseline_exists = (project / "audit_baseline.json").exists()

        config_path = project / ".two-brain-audit.json"
        dim_config = None
        if config_path.exists():
            try:
                dim_config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                log.warning("Failed to load dimension config", exc_info=True)

        if dim_config and dim_config.get("preset"):
            _register_preset(dim_config["preset"])

    from two_brain_studio.state import add_recent_project
    add_recent_project(str(project))

    return {
        "path": str(project),
        "db_path": db_path,
        "baseline_exists": baseline_exists,
        "dimensions": len(_engine.dimensions),
        "config": dim_config,
    }


def init_project(project_dir: str, preset: str | None = None) -> dict[str, Any]:
    """Initialize a new two-brain-audit project."""
    global _engine, _project_path
    from two_brain_audit import AuditEngine

    with _lock:
        if _engine is not None and hasattr(_engine, "close"):
            try:
                _engine.close()
            except Exception:
                log.warning("Error closing previous engine", exc_info=True)

        project = Path(project_dir)
        project.mkdir(parents=True, exist_ok=True)

        db_path = str(project / "audit.db")
        baseline_path = str(project / "audit_baseline.json")

        _engine = AuditEngine(db_path=db_path, baseline_path=baseline_path)
        _engine.sidecar.init()
        _project_path = str(project)

        config = {"preset": preset, "created": True}
        (project / ".two-brain-audit.json").write_text(
            json.dumps(config, indent=2) + "\n", encoding="utf-8"
        )

        if preset:
            _register_preset(preset)

    from two_brain_studio.state import add_recent_project
    add_recent_project(str(project))

    return {
        "path": str(project),
        "preset": preset,
        "dimensions": len(_engine.dimensions),
    }


def _register_preset(preset_name: str) -> None:
    """Register dimensions from a named preset."""
    if _engine is None:
        return
    try:
        mod = importlib.import_module("two_brain_audit.presets")
        presets_map = getattr(mod, "PRESETS", None)
        if presets_map is None:
            log.info("Presets not available — register dimensions via Python API.")
            return
        dims = presets_map.get(preset_name, [])
        if dims:
            _engine.register_many(dims)
    except Exception:
        log.warning("Failed to load preset %s", preset_name, exc_info=True)
