"""Desktop app entry point — PyWebView window hosting the Flask server."""

from __future__ import annotations

import logging
import sys
import threading
import time
import urllib.request

log = logging.getLogger("two_brain_studio")

PORT = 18484
_window = None


def select_folder():
    """Open native folder picker dialog. Exposed to JS as window.pywebview.api.select_folder()."""
    if _window is None:
        return None
    result = _window.create_file_dialog(dialog_type=20)  # FOLDER_DIALOG
    if result and len(result) > 0:
        return result[0]
    return None


def main() -> None:
    """Launch Two-Brain Studio."""
    try:
        import webview
    except ImportError:
        print("PyWebView required: pip install pywebview", file=sys.stderr)
        sys.exit(1)

    from two_brain_studio.server import create_app

    app = create_app()
    url = f"http://127.0.0.1:{PORT}/"

    # Start Flask in daemon thread
    server = threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False),
        daemon=True,
    )
    server.start()
    _wait_for_server(url)

    global _window
    _window = webview.create_window(
        "Two-Brain Studio",
        url,
        width=1200,
        height=800,
        min_size=(900, 600),
        background_color="#0f1117",
    )
    _window.expose(select_folder)

    try:
        for gui in ("qt", None):
            try:
                webview.start(gui=gui)
                break
            except Exception as exc:
                if gui is not None:
                    log.debug("gui=%s failed: %s", gui, exc)
                    continue
                raise
    finally:
        # Cleanup on window close
        from two_brain_studio import engine_manager
        engine_manager.unload_project()
        log.info("Studio closed")


def _wait_for_server(url: str, timeout: int = 10) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)  # noqa: S310
            return
        except Exception:
            time.sleep(0.2)


if __name__ == "__main__":
    main()
