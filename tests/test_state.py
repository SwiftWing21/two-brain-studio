"""Tests for app state persistence."""

import json
from unittest.mock import patch

import pytest

from scorerift_studio import state


class TestAppConfig:
    def test_load_missing_config(self, tmp_path):
        with patch.object(state, "CONFIG_FILE", tmp_path / "nonexistent.json"):
            config = state.load_app_config()
            assert "recent_projects" in config
            assert config["theme"] == "dark"

    def test_save_and_load(self, tmp_path):
        config_file = tmp_path / "config.json"
        with patch.object(state, "CONFIG_FILE", config_file), \
             patch.object(state, "CONFIG_DIR", tmp_path):
            state.save_app_config({"recent_projects": ["/a"], "theme": "light"})
            loaded = state.load_app_config()
            assert loaded["recent_projects"] == ["/a"]
            assert loaded["theme"] == "light"


class TestRecentProjects:
    def test_add_recent(self, tmp_path):
        config_file = tmp_path / "config.json"
        with patch.object(state, "CONFIG_FILE", config_file), \
             patch.object(state, "CONFIG_DIR", tmp_path):
            state.add_recent_project("/path/a")
            state.add_recent_project("/path/b")
            config = state.load_app_config()
            assert config["recent_projects"][0] == "/path/b"
            assert config["recent_projects"][1] == "/path/a"

    def test_dedup(self, tmp_path):
        config_file = tmp_path / "config.json"
        with patch.object(state, "CONFIG_FILE", config_file), \
             patch.object(state, "CONFIG_DIR", tmp_path):
            state.add_recent_project("/path/a")
            state.add_recent_project("/path/a")
            config = state.load_app_config()
            assert config["recent_projects"].count("/path/a") == 1

    def test_max_10(self, tmp_path):
        config_file = tmp_path / "config.json"
        with patch.object(state, "CONFIG_FILE", config_file), \
             patch.object(state, "CONFIG_DIR", tmp_path):
            for i in range(15):
                state.add_recent_project(f"/path/{i}")
            config = state.load_app_config()
            assert len(config["recent_projects"]) == 10
            assert config["recent_projects"][0] == "/path/14"
