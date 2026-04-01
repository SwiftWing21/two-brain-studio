"""Flask server powering the studio UI.

Serves the single-page app shell and API endpoints for project management,
dimension configuration, baseline editing, and audit execution. The audit
dashboard itself is mounted from two-brain-audit's blueprint.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify, request

from two_brain_studio import engine_manager
from two_brain_studio.ui import render_studio


def create_app() -> Flask:
    app = Flask("two_brain_studio")

    # ── Studio UI ────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_studio()

    # ── Project Management ───────────────────────────────────────────
    @app.route("/api/project/open", methods=["POST"])
    def open_project():
        data = request.get_json(force=True)
        path = data.get("path", "")
        if not path or not Path(path).is_dir():
            return jsonify({"error": "Invalid directory path"}), 400
        try:
            result = engine_manager.load_project(path)
            _mount_audit_blueprint(app)
            return jsonify(result)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/project/init", methods=["POST"])
    def init_project():
        data = request.get_json(force=True)
        path = data.get("path", "")
        preset = data.get("preset")
        if not path:
            return jsonify({"error": "Path required"}), 400
        try:
            result = engine_manager.init_project(path, preset=preset)
            _mount_audit_blueprint(app)
            return jsonify(result)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/project/status")
    def project_status():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"loaded": False})
        return jsonify({
            "loaded": True,
            "path": engine_manager.get_project_path(),
            "db_path": os.path.abspath(engine.db_path),
            "baseline_path": os.path.abspath(engine.baseline_path),
            "dimensions": len(engine.dimensions),
        })

    @app.route("/api/project/browse", methods=["POST"])
    def browse_folder():
        """Trigger native folder picker via pywebview."""
        # This is handled client-side via webview.api — just a placeholder
        return jsonify({"note": "Use window.pywebview.api.select_folder() instead"})

    # ── Recent Projects ──────────────────────────────────────────────
    @app.route("/api/recent")
    def recent_projects():
        from two_brain_studio.state import load_app_config
        config = load_app_config()
        recents = config.get("recent_projects", [])
        # Validate paths still exist
        valid = [p for p in recents if Path(p).is_dir()]
        return jsonify(valid)

    # ── Presets ──────────────────────────────────────────────────────
    @app.route("/api/presets")
    def list_presets():
        return jsonify([
            {"id": "python", "name": "Python Project", "dims": 8,
             "description": "Tests, lint, types, deps, docs, security, complexity, imports"},
            {"id": "api", "name": "REST API", "dims": 8,
             "description": "Endpoints, latency, errors, auth, schema, rate limits, CORS, TLS"},
            {"id": "database", "name": "Database", "dims": 7,
             "description": "Schema, indexes, queries, backups, replication, pool, migrations"},
            {"id": "infrastructure", "name": "Infrastructure", "dims": 8,
             "description": "Uptime, certs, resources, config drift, secrets, DNS, CDN, containers"},
            {"id": "ml_pipeline", "name": "ML Pipeline", "dims": 7,
             "description": "Model freshness, data drift, latency, accuracy, features, GPU, experiments"},
        ])

    # ── Dimensions ───────────────────────────────────────────────────
    @app.route("/api/dimensions")
    def list_dimensions():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify([])
        return jsonify([
            {
                "name": d.name,
                "confidence": d.confidence,
                "tier": d.tier.value,
                "description": d.description,
            }
            for d in engine.dimensions.values()
        ])

    # ── Baseline Editor ──────────────────────────────────────────────
    @app.route("/api/baseline")
    def get_baseline():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({})
        return jsonify(engine.sidecar.load())

    @app.route("/api/baseline/grade", methods=["POST"])
    def set_grade():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"error": "No project loaded"}), 400
        data = request.get_json(force=True)
        engine.sidecar.set_grade(
            dimension=data["dimension"],
            grade=data["grade"],
            source=data.get("source", "human"),
            notes=data.get("notes", ""),
        )
        return jsonify({"ok": True})

    @app.route("/api/baseline/ratchet", methods=["POST"])
    def set_ratchet():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"error": "No project loaded"}), 400
        data = request.get_json(force=True)
        if data.get("remove"):
            engine.sidecar.remove_ratchet(data["dimension"])
        else:
            engine.sidecar.set_ratchet(data["dimension"], data["grade"])
        return jsonify({"ok": True})

    # ── Run Audit ────────────────────────────────────────────────────
    @app.route("/api/run/<tier>", methods=["POST"])
    def run_audit(tier: str):
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"error": "No project loaded"}), 400
        results = engine.run_tier(tier)
        baseline = engine.sidecar.load()
        dims = baseline.get("dimensions", {})
        out = []
        for r in results:
            meta = dims.get(r.name, {})
            out.append({
                "name": r.name,
                "auto_score": r.auto_score,
                "auto_detail": r.auto_detail,
                "auto_confidence": r.auto_confidence,
                "manual_grade": r.manual_grade,
                "manual_score": r.manual_score,
                "manual_source": meta.get("source"),
                "manual_updated": meta.get("updated"),
                "manual_notes": meta.get("notes"),
                "divergent": r.divergent,
                "acknowledged": r.acknowledged,
                "tier": r.tier,
                "timestamp": r.timestamp,
            })
        return jsonify(out)

    @app.route("/api/health")
    def health():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"ok": False, "grade": "--", "score": 0, "divergences": 0, "failing": []})
        return jsonify(engine.health_check())

    @app.route("/api/scores")
    def scores():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify([])
        results = engine.latest_scores()
        baseline = engine.sidecar.load()
        dims = baseline.get("dimensions", {})
        out = []
        for r in results:
            meta = dims.get(r.name, {})
            out.append({
                "name": r.name,
                "auto_score": r.auto_score,
                "auto_detail": r.auto_detail,
                "auto_confidence": r.auto_confidence,
                "manual_grade": r.manual_grade,
                "manual_score": r.manual_score,
                "manual_source": meta.get("source"),
                "manual_updated": meta.get("updated"),
                "manual_notes": meta.get("notes"),
                "divergent": r.divergent,
                "acknowledged": r.acknowledged,
                "tier": r.tier,
                "timestamp": r.timestamp,
            })
        return jsonify(out)

    @app.route("/api/feedback/summary")
    def feedback_summary():
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"count": 0, "avg_score": None})
        return jsonify(engine.feedback_summary())

    @app.route("/api/acknowledge/<dimension>", methods=["POST"])
    def acknowledge(dimension: str):
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"error": "No project loaded"}), 400
        engine.acknowledge(dimension)
        return jsonify({"ok": True})

    @app.route("/api/export/<fmt>")
    def export(fmt: str):
        engine = engine_manager.get_engine()
        if not engine:
            return jsonify({"error": "No project loaded"}), 400
        from two_brain_audit.exporters import export_csv, export_json, export_markdown
        exporters = {"json": export_json, "csv": export_csv, "markdown": export_markdown}
        fn = exporters.get(fmt)
        if not fn:
            return jsonify({"error": f"Unknown format: {fmt}"}), 400
        return fn(engine), 200, {"Content-Type": "text/plain"}

    return app


def _mount_audit_blueprint(app: Flask) -> None:
    """Mount the two-brain-audit dashboard blueprint if not already mounted."""
    if "two_brain_audit" in app.blueprints:
        return
    engine = engine_manager.get_engine()
    if engine:
        from two_brain_audit.dashboard import create_blueprint
        app.register_blueprint(create_blueprint(engine), url_prefix="/audit")
