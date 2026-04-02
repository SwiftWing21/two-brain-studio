"""Tests for the Studio Flask server."""

import json

import pytest

from two_brain_studio.server import create_app


@pytest.fixture(autouse=True)
def _clean_engine():
    """Ensure no project is loaded between tests."""
    from two_brain_studio import engine_manager
    engine_manager.unload_project()
    yield
    engine_manager.unload_project()


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestProjectLifecycle:
    def test_status_no_project(self, client):
        resp = client.get("/api/project/status")
        assert resp.status_code == 200
        assert resp.get_json()["loaded"] is False

    def test_init_project(self, client, tmp_path):
        resp = client.post("/api/project/init", json={
            "path": str(tmp_path / "test_proj"),
            "preset": "python",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "path" in data
        assert data["preset"] == "python"

    def test_open_project(self, client, tmp_path):
        # Init first
        proj = tmp_path / "proj"
        proj.mkdir()
        client.post("/api/project/init", json={"path": str(proj)})
        # Close
        client.post("/api/project/close")
        # Re-open
        resp = client.post("/api/project/open", json={"path": str(proj)})
        assert resp.status_code == 200

    def test_open_nonexistent(self, client):
        resp = client.post("/api/project/open", json={"path": "/nonexistent/path"})
        assert resp.status_code == 400

    def test_close_project(self, client, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        client.post("/api/project/init", json={"path": str(proj)})
        resp = client.post("/api/project/close")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True
        # Status should show not loaded
        status = client.get("/api/project/status").get_json()
        assert status["loaded"] is False


class TestValidation:
    def test_init_no_path(self, client):
        resp = client.post("/api/project/init", json={"preset": "python"})
        assert resp.status_code == 400

    def test_set_grade_missing_fields(self, client, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        client.post("/api/project/init", json={"path": str(proj)})
        resp = client.post("/api/baseline/grade", json={"dimension": "test"})
        assert resp.status_code == 400

    def test_set_ratchet_missing_dimension(self, client, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        client.post("/api/project/init", json={"path": str(proj)})
        resp = client.post("/api/baseline/ratchet", json={"grade": "A"})
        assert resp.status_code == 400

    def test_run_invalid_tier(self, client, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        client.post("/api/project/init", json={"path": str(proj)})
        resp = client.post("/api/run/bogus")
        assert resp.status_code == 400

    def test_run_no_project(self, client):
        resp = client.post("/api/run/light")
        assert resp.status_code == 400


class TestDataEndpoints:
    def test_presets(self, client):
        resp = client.get("/api/presets")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 5
        assert all("id" in p for p in data)

    def test_recent(self, client):
        resp = client.get("/api/recent")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_dimensions_no_project(self, client):
        resp = client.get("/api/dimensions")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_scores_no_project(self, client):
        resp = client.get("/api/scores")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_health_no_project(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is False

    def test_export_no_project(self, client):
        resp = client.get("/api/export/json")
        assert resp.status_code == 400

    def test_index_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Two-Brain" in resp.data
