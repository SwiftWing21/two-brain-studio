"""Tests for the engine manager."""

import pytest

from scorerift_studio import engine_manager


class TestEngineManager:
    def setup_method(self):
        engine_manager.unload_project()

    def test_no_engine_initially(self):
        assert engine_manager.get_engine() is None
        assert engine_manager.get_project_path() is None

    def test_init_project(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        result = engine_manager.init_project(str(proj))
        assert engine_manager.get_engine() is not None
        assert engine_manager.get_project_path() is not None
        # Baseline and config created (DB is created lazily on first write)
        assert (proj / "audit_baseline.json").exists()
        assert (proj / ".scorerift.json").exists()

    def test_load_project(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        engine_manager.init_project(str(proj))
        engine_manager.unload_project()
        result = engine_manager.load_project(str(proj))
        assert result["path"] == str(proj)
        assert engine_manager.get_engine() is not None

    def test_unload_project(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        engine_manager.init_project(str(proj))
        engine_manager.unload_project()
        assert engine_manager.get_engine() is None
        assert engine_manager.get_project_path() is None

    def test_switch_project(self, tmp_path):
        p1 = tmp_path / "p1"
        p2 = tmp_path / "p2"
        p1.mkdir()
        p2.mkdir()
        engine_manager.init_project(str(p1))
        assert engine_manager.get_project_path() == str(p1)
        engine_manager.init_project(str(p2))
        assert engine_manager.get_project_path() == str(p2)

    def test_init_with_preset(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        result = engine_manager.init_project(str(proj), preset="python")
        # Dimensions may or may not load depending on install state
        assert result["preset"] == "python"
