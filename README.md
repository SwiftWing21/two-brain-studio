# ScoreRift Studio

Desktop GUI for [scorerift](https://github.com/SwiftWing21/scorerift) — configure, run, and review audits without touching the CLI.

## What It Does

- **Open any folder** as an audit project (or create a new one)
- **Pick a preset** (Python, API, Database, Infrastructure, ML) or register custom dimensions
- **Run audits** at any tier (light/medium/daily/weekly) with one click
- **View results** — grade ring, score bars, divergence alerts, confidence levels
- **Edit manual grades** — the "right brain" baseline editor with grade dropdowns and notes
- **Export reports** — Markdown, JSON, CSV with one click
- **Recent projects** — quick access to your last 10 projects

## Install

```bash
pip install scorerift-studio
```

## Launch

```bash
scorerift-studio
```

Or on Windows, double-click `launch.bat` (uses `pythonw.exe` — no console flash).

## Screenshots

*Coming soon — the app is a dark-mode native window with sidebar navigation.*

## Requirements

- Python 3.10+
- [scorerift](https://pypi.org/project/scorerift/) >= 0.1.2
- Flask >= 3.0
- PyWebView >= 5.0 (falls back to browser if unavailable)

## How It Works

Studio is a PyWebView native window hosting a Flask server. The UI is a single-page app with sidebar navigation — all rendering happens client-side via safe DOM construction. The Flask backend wraps `scorerift`'s Python API for project management, dimension configuration, baseline editing, and audit execution.

```
┌─────────────────────────────────────┐
│  PyWebView (native window)          │
│  ┌───────────────────────────────┐  │
│  │  Flask Server (localhost)     │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │  scorerift engine │  │  │
│  │  │  (scores, baseline, DB) │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Development

```bash
git clone https://github.com/SwiftWing21/scorerift-studio.git
cd scorerift-studio
pip install -e ".[dev]"
python -m scorerift_studio.app
```

## License

MIT
