"""Studio UI — single-page app with sidebar navigation.

Pages: Welcome (project picker), Dashboard (audit results), Dimensions
(config), Baseline (manual grades), Export (reports).
"""

from __future__ import annotations


def render_studio() -> str:
    return _HTML


_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Two-Brain Studio</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0f1117; --surface: #1a1d27; --card: #222632; --border: #2e3345;
  --text: #e2e8f0; --muted: #64748b; --accent: #818cf8; --accent-dim: #6366f1;
  --green: #34d399; --yellow: #fbbf24; --red: #f87171;
  --radius: 10px;
  --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --mono: 'SF Mono', 'Cascadia Code', 'Fira Code', monospace;
  --sidebar-w: 220px;
}
body { font-family: var(--font); background: var(--bg); color: var(--text); line-height: 1.5; height: 100vh; overflow: hidden; }

/* ── Layout ──────────────────────────────────────────────────── */
.app { display: flex; height: 100vh; }
.sidebar {
  width: var(--sidebar-w); background: var(--surface); border-right: 1px solid var(--border);
  display: flex; flex-direction: column; flex-shrink: 0;
}
.sidebar-brand { padding: 20px 16px 12px; font-size: 15px; font-weight: 700; }
.sidebar-brand span { color: var(--accent); }
.sidebar-nav { flex: 1; padding: 8px; }
.nav-item {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px;
  border-radius: 8px; cursor: pointer; font-size: 13px; color: var(--muted);
  transition: all 0.15s; margin-bottom: 2px;
}
.nav-item:hover { background: rgba(129,140,248,0.08); color: var(--text); }
.nav-item.active { background: rgba(129,140,248,0.12); color: var(--accent); font-weight: 600; }
.nav-icon { font-size: 16px; width: 20px; text-align: center; }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid var(--border); font-size: 11px; color: var(--muted); }
.sidebar-footer .project-path {
  font-family: var(--mono); font-size: 10px; margin-top: 4px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 190px;
}

.main { flex: 1; overflow-y: auto; padding: 28px 32px; }
.page { display: none; }
.page.active { display: block; }

/* ── Welcome ─────────────────────────────────────────────────── */
.welcome-hero { text-align: center; padding: 60px 20px 40px; }
.welcome-hero h1 { font-size: 28px; font-weight: 800; margin-bottom: 8px; }
.welcome-hero h1 span { color: var(--accent); }
.welcome-hero p { color: var(--muted); font-size: 14px; max-width: 500px; margin: 0 auto; }
.welcome-actions { display: flex; gap: 16px; justify-content: center; margin: 32px 0; flex-wrap: wrap; }
.welcome-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 24px; width: 260px; cursor: pointer; transition: all 0.15s; text-align: left;
}
.welcome-card:hover { border-color: var(--accent-dim); transform: translateY(-2px); }
.welcome-card h3 { font-size: 15px; margin-bottom: 6px; }
.welcome-card p { font-size: 12px; color: var(--muted); }
.recent-list { max-width: 560px; margin: 0 auto; }
.recent-title { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.recent-item {
  padding: 10px 14px; background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; margin-bottom: 6px; cursor: pointer; font-family: var(--mono);
  font-size: 12px; color: var(--muted); transition: all 0.15s;
}
.recent-item:hover { border-color: var(--accent-dim); color: var(--text); }

/* ── Setup Wizard ────────────────────────────────────────────── */
.wizard { max-width: 600px; margin: 0 auto; padding-top: 40px; }
.wizard h2 { font-size: 20px; margin-bottom: 20px; }
.wizard-step { margin-bottom: 24px; }
.wizard-label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.path-picker { display: flex; gap: 8px; }
.path-input {
  flex: 1; padding: 10px 14px; background: var(--card); border: 1px solid var(--border);
  border-radius: 8px; color: var(--text); font-family: var(--mono); font-size: 13px;
}
.path-input:focus { outline: none; border-color: var(--accent-dim); }
.preset-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px; }
.preset-card {
  padding: 14px; background: var(--card); border: 2px solid var(--border);
  border-radius: 8px; cursor: pointer; transition: all 0.15s;
}
.preset-card:hover { border-color: var(--accent-dim); }
.preset-card.selected { border-color: var(--accent); background: rgba(129,140,248,0.08); }
.preset-card h4 { font-size: 13px; margin-bottom: 4px; }
.preset-card .preset-desc { font-size: 11px; color: var(--muted); }
.preset-card .preset-dims { font-size: 11px; color: var(--accent); margin-top: 4px; }

/* ── Shared ──────────────────────────────────────────────────── */
.btn {
  padding: 8px 18px; border-radius: 8px; border: 1px solid var(--border);
  background: var(--card); color: var(--text); font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.btn:hover { background: var(--surface); border-color: var(--accent-dim); }
.btn.primary { background: var(--accent-dim); border-color: var(--accent); color: #fff; }
.btn.primary:hover { background: var(--accent); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.section-title {
  font-size: 14px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; color: var(--muted); margin-bottom: 12px;
}
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h2 { font-size: 20px; font-weight: 700; }

/* ── Score table (reused from audit dashboard) ───────────────── */
.health-badge {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px;
  border-radius: 20px; font-weight: 600; font-size: 14px;
}
.health-badge.ok { background: rgba(52,211,153,0.12); color: var(--green); }
.health-badge.warn { background: rgba(251,191,36,0.12); color: var(--yellow); }
.health-badge.fail { background: rgba(248,113,113,0.12); color: var(--red); }
.health-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

.grade-ring { width: 100px; height: 100px; position: relative; margin: 0 auto 8px; }
.grade-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.grade-ring circle { fill: none; stroke-width: 7; stroke-linecap: round; }
.grade-ring .track { stroke: var(--border); }
.grade-ring .fill { stroke: var(--accent); transition: stroke-dashoffset 0.8s ease; }
.grade-ring .label {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.grade-ring .grade-letter { font-size: 26px; font-weight: 800; color: var(--accent); }
.grade-ring .grade-score { font-size: 11px; color: var(--muted); font-family: var(--mono); }

.stats-row { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 110px; background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px; text-align: center;
}
.stat-card .stat-value { font-size: 24px; font-weight: 700; font-family: var(--mono); }
.stat-card .stat-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }

.score-table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden;
}
.score-table th, .score-table td { padding: 10px 14px; text-align: left; font-size: 13px; border-bottom: 1px solid var(--border); }
.score-table th { background: var(--surface); color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
.score-table tr:last-child td { border-bottom: none; }
.score-table tr:hover td { background: rgba(129,140,248,0.04); }
.score-bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; min-width: 120px; }
.score-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }
.status-badge { display: inline-flex; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.status-badge.ok { background: rgba(52,211,153,0.12); color: var(--green); }
.status-badge.warn { background: rgba(251,191,36,0.12); color: var(--yellow); }
.status-badge.fail { background: rgba(248,113,113,0.12); color: var(--red); }

/* ── Baseline Editor ─────────────────────────────────────────── */
.baseline-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }
.baseline-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px;
}
.baseline-card h4 { font-size: 14px; margin-bottom: 8px; }
.baseline-row { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.baseline-row label { font-size: 11px; color: var(--muted); min-width: 60px; }
.baseline-select, .baseline-input {
  padding: 5px 8px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); font-size: 12px; flex: 1;
}
.baseline-select:focus, .baseline-input:focus { outline: none; border-color: var(--accent-dim); }

/* ── Action bar ──────────────────────────────────────────────── */
.action-bar { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }

/* ── Toast ───────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 24px; right: 24px; padding: 10px 20px;
  background: var(--card); border: 1px solid var(--border); border-radius: 8px;
  font-size: 13px; opacity: 0; transform: translateY(10px); transition: all 0.3s; z-index: 100;
}
.toast.show { opacity: 1; transform: translateY(0); }
.toast.success { border-color: var(--green); color: var(--green); }
.toast.error { border-color: var(--red); color: var(--red); }
</style>
</head>
<body>
<div class="app">

<!-- ── Sidebar ────────────────────────────────────────────────── -->
<div class="sidebar">
  <div class="sidebar-brand"><span>Two-Brain</span> Studio</div>
  <div class="sidebar-nav">
    <div class="nav-item active" data-page="welcome" onclick="showPage('welcome')">
      <span class="nav-icon">&#9776;</span> Home
    </div>
    <div class="nav-item" data-page="dashboard" onclick="showPage('dashboard')">
      <span class="nav-icon">&#9673;</span> Dashboard
    </div>
    <div class="nav-item" data-page="dimensions" onclick="showPage('dimensions')">
      <span class="nav-icon">&#9881;</span> Dimensions
    </div>
    <div class="nav-item" data-page="baseline" onclick="showPage('baseline')">
      <span class="nav-icon">&#9998;</span> Baseline
    </div>
    <div class="nav-item" data-page="export" onclick="showPage('export')">
      <span class="nav-icon">&#8681;</span> Export
    </div>
  </div>
  <div class="sidebar-footer">
    <div id="sidebar-status">No project loaded</div>
    <div class="project-path" id="sidebar-path"></div>
  </div>
</div>

<!-- ── Main Content ──────────────────────────────────────────── -->
<div class="main">

  <!-- Welcome / Home -->
  <div class="page active" id="page-welcome">
    <div class="welcome-hero">
      <h1><span>Two-Brain</span> Studio</h1>
      <p>Configure, run, and review audits — no CLI required.</p>
    </div>
    <div class="welcome-actions">
      <div class="welcome-card" onclick="showPage('setup')">
        <h3>+ New Project</h3>
        <p>Initialize a new audit on any folder. Pick a preset to get started fast.</p>
      </div>
      <div class="welcome-card" onclick="openExisting()">
        <h3>Open Existing</h3>
        <p>Open a folder that already has audit.db and audit_baseline.json.</p>
      </div>
    </div>
    <div class="recent-list" id="recent-list"></div>
  </div>

  <!-- Setup Wizard -->
  <div class="page" id="page-setup">
    <div class="wizard">
      <h2>New Project</h2>
      <div class="wizard-step">
        <div class="wizard-label">Project Folder</div>
        <div class="path-picker">
          <input class="path-input" id="setup-path" placeholder="/path/to/your/project" />
          <button class="btn" onclick="browseFolder()">Browse</button>
        </div>
      </div>
      <div class="wizard-step">
        <div class="wizard-label">Preset (optional)</div>
        <div class="preset-grid" id="preset-grid"></div>
      </div>
      <div class="action-bar">
        <button class="btn" onclick="showPage('welcome')">Cancel</button>
        <button class="btn primary" onclick="initProject()">Create Project</button>
      </div>
    </div>
  </div>

  <!-- Dashboard -->
  <div class="page" id="page-dashboard">
    <div class="page-header">
      <h2>Dashboard</h2>
      <div id="dash-health" class="health-badge ok"><div class="dot"></div><span id="dash-health-text">--</span></div>
    </div>
    <div style="display:flex;gap:24px;margin-bottom:24px;align-items:flex-start;">
      <div>
        <div class="grade-ring">
          <svg viewBox="0 0 100 100">
            <circle class="track" cx="50" cy="50" r="43"></circle>
            <circle class="fill" id="dash-arc" cx="50" cy="50" r="43" stroke-dasharray="270.18" stroke-dashoffset="270.18"></circle>
          </svg>
          <div class="label">
            <div class="grade-letter" id="dash-grade">--</div>
            <div class="grade-score" id="dash-score">--</div>
          </div>
        </div>
      </div>
      <div class="stats-row" style="flex:1;">
        <div class="stat-card"><div class="stat-value" id="d-dims">--</div><div class="stat-label">Dimensions</div></div>
        <div class="stat-card"><div class="stat-value" style="color:var(--green)" id="d-pass">--</div><div class="stat-label">Passing</div></div>
        <div class="stat-card"><div class="stat-value" style="color:var(--yellow)" id="d-divs">--</div><div class="stat-label">Divergences</div></div>
        <div class="stat-card"><div class="stat-value" style="color:var(--red)" id="d-fail">--</div><div class="stat-label">Failing</div></div>
        <div class="stat-card"><div class="stat-value" style="color:var(--accent)" id="d-reviewed">--</div><div class="stat-label">Reviewed</div></div>
      </div>
    </div>
    <table class="score-table">
      <thead><tr><th>Dimension</th><th>Score</th><th>Grade</th><th>Manual</th><th>Status</th><th>Confidence</th></tr></thead>
      <tbody id="dash-tbody"><tr><td colspan="6" style="text-align:center;color:var(--muted);padding:20px;">Run an audit to see results</td></tr></tbody>
    </table>
    <div class="action-bar">
      <button class="btn primary" onclick="runAudit('light')">Run Light</button>
      <button class="btn" onclick="runAudit('medium')">Run Medium</button>
      <button class="btn" onclick="runAudit('daily')">Run Daily</button>
      <button class="btn" onclick="runAudit('weekly')">Run Weekly</button>
    </div>
  </div>

  <!-- Dimensions -->
  <div class="page" id="page-dimensions">
    <div class="page-header"><h2>Dimensions</h2></div>
    <p style="color:var(--muted);margin-bottom:16px;font-size:13px;">Registered check functions. To add custom dimensions, use the Python API.</p>
    <table class="score-table">
      <thead><tr><th>Name</th><th>Tier</th><th>Confidence</th><th>Description</th></tr></thead>
      <tbody id="dim-tbody"><tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px;">No project loaded</td></tr></tbody>
    </table>
  </div>

  <!-- Baseline Editor -->
  <div class="page" id="page-baseline">
    <div class="page-header"><h2>Manual Grades</h2></div>
    <p style="color:var(--muted);margin-bottom:16px;font-size:13px;">Set manual grades for each dimension. These are the "right brain" — your human assessment.</p>
    <div class="baseline-grid" id="baseline-grid"></div>
  </div>

  <!-- Export -->
  <div class="page" id="page-export">
    <div class="page-header"><h2>Export</h2></div>
    <p style="color:var(--muted);margin-bottom:16px;font-size:13px;">Generate audit reports in various formats.</p>
    <div class="action-bar">
      <button class="btn" onclick="exportReport('markdown')">Markdown</button>
      <button class="btn" onclick="exportReport('json')">JSON</button>
      <button class="btn" onclick="exportReport('csv')">CSV</button>
    </div>
    <pre id="export-output" style="margin-top:16px;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);font-family:var(--mono);font-size:12px;white-space:pre-wrap;max-height:500px;overflow:auto;display:none;"></pre>
  </div>

</div><!-- /.main -->
</div><!-- /.app -->

<div class="toast" id="toast"></div>

<script>
var selectedPreset = null;
var GRADES = ['S','A+','A','A-','B+','B','B-','C+','C','D','F'];
function scoreToGrade(s) {
  var G = {S:1,'A+':.95,A:.9,'A-':.85,'B+':.8,B:.75,'B-':.7,'C+':.65,C:.6,D:.5,F:.3};
  var entries = Object.entries(G).sort(function(a,b){return b[1]-a[1];});
  for (var i=0;i<entries.length;i++) { if (s >= entries[i][1]-0.035) return entries[i][0]; }
  return 'F';
}
function scoreColor(s) {
  if (s >= 0.85) return 'var(--green)';
  if (s >= 0.70) return 'var(--accent)';
  if (s >= 0.55) return 'var(--yellow)';
  return 'var(--red)';
}
function el(tag, attrs, children) {
  var e = document.createElement(tag);
  if (attrs) Object.entries(attrs).forEach(function(kv) {
    if (kv[0]==='style'&&typeof kv[1]==='object') Object.assign(e.style,kv[1]);
    else if (kv[0]==='className') e.className=kv[1];
    else if (kv[0]==='onclick') e.addEventListener('click',kv[1]);
    else e.setAttribute(kv[0],kv[1]);
  });
  if (children) {
    if (typeof children==='string') e.textContent=children;
    else if (Array.isArray(children)) children.forEach(function(c){if(c)e.appendChild(c);});
    else e.appendChild(children);
  }
  return e;
}
async function api(path,opts){var r=await fetch(path,opts);return r.json();}
function toast(msg,type){var t=document.getElementById('toast');t.textContent=msg;t.className='toast '+(type||'')+' show';clearTimeout(t._t);t._t=setTimeout(function(){t.className='toast';},3000);}

/* ── Navigation ──────────────────────────────────────────────── */
function showPage(id) {
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');});
  document.querySelectorAll('.nav-item').forEach(function(n){n.classList.remove('active');});
  var page = document.getElementById('page-'+id);
  if (page) page.classList.add('active');
  var nav = document.querySelector('.nav-item[data-page="'+id+'"]');
  if (nav) nav.classList.add('active');
  if (id==='dashboard') refreshDashboard();
  if (id==='dimensions') refreshDimensions();
  if (id==='baseline') refreshBaseline();
}

/* ── Welcome ─────────────────────────────────────────────────── */
async function loadRecents() {
  var recents = await api('/api/recent');
  var list = document.getElementById('recent-list');
  while (list.firstChild) list.removeChild(list.firstChild);
  if (!recents.length) return;
  list.appendChild(el('div',{className:'recent-title'},'Recent Projects'));
  recents.forEach(function(p) {
    list.appendChild(el('div',{className:'recent-item',onclick:function(){openProject(p);}},p));
  });
}

async function openExisting() {
  if (window.pywebview && window.pywebview.api) {
    var folder = await window.pywebview.api.select_folder();
    if (folder) openProject(folder);
  } else {
    var path = prompt('Enter project folder path:');
    if (path) openProject(path);
  }
}

async function openProject(path) {
  try {
    var result = await api('/api/project/open',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:path})});
    if (result.error) { toast(result.error,'error'); return; }
    updateSidebar(path, result.dimensions);
    toast('Project loaded','success');
    showPage('dashboard');
  } catch(e) { toast('Failed: '+e.message,'error'); }
}

/* ── Setup ───────────────────────────────────────────────────── */
async function loadPresets() {
  var presets = await api('/api/presets');
  var grid = document.getElementById('preset-grid');
  while (grid.firstChild) grid.removeChild(grid.firstChild);
  presets.forEach(function(p) {
    var card = el('div',{className:'preset-card',onclick:function(){
      selectedPreset = (selectedPreset===p.id) ? null : p.id;
      document.querySelectorAll('.preset-card').forEach(function(c){c.classList.remove('selected');});
      if (selectedPreset) card.classList.add('selected');
    }},[
      el('h4',null,p.name),
      el('div',{className:'preset-desc'},p.description),
      el('div',{className:'preset-dims'},p.dims+' dimensions'),
    ]);
    grid.appendChild(card);
  });
}

async function browseFolder() {
  if (window.pywebview && window.pywebview.api) {
    var folder = await window.pywebview.api.select_folder();
    if (folder) document.getElementById('setup-path').value = folder;
  }
}

async function initProject() {
  var path = document.getElementById('setup-path').value.trim();
  if (!path) { toast('Select a folder first','error'); return; }
  try {
    var result = await api('/api/project/init',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:path,preset:selectedPreset})});
    if (result.error) { toast(result.error,'error'); return; }
    updateSidebar(path, result.dimensions);
    toast('Project created','success');
    showPage('dashboard');
  } catch(e) { toast('Failed: '+e.message,'error'); }
}

function updateSidebar(path, dims) {
  document.getElementById('sidebar-status').textContent = (dims||0)+' dimensions';
  document.getElementById('sidebar-path').textContent = path;
  document.getElementById('sidebar-path').title = path;
}

/* ── Dashboard ───────────────────────────────────────────────── */
async function refreshDashboard() {
  try {
    var scores = await api('/api/scores');
    var health = await api('/api/health');
    var fb = await api('/api/feedback/summary');

    var badge = document.getElementById('dash-health');
    badge.className = 'health-badge '+(health.ok?'ok':(health.failing.length?'fail':'warn'));
    document.getElementById('dash-health-text').textContent = health.ok?'Healthy':(health.failing.length?'Failing':'Diverged');

    var pct = health.score;
    var circ = 2*Math.PI*43;
    document.getElementById('dash-arc').style.strokeDashoffset = String(circ*(1-pct));
    document.getElementById('dash-arc').style.stroke = scoreColor(pct);
    document.getElementById('dash-grade').textContent = health.grade;
    document.getElementById('dash-grade').style.color = scoreColor(pct);
    document.getElementById('dash-score').textContent = pct.toFixed(3);

    var passing = scores.filter(function(s){return s.auto_score>0.5&&!s.divergent;}).length;
    var failing = scores.filter(function(s){return s.auto_score<=0.5;}).length;
    var divs = scores.filter(function(s){return s.divergent&&!s.acknowledged;}).length;
    var reviewed = scores.filter(function(s){return s.manual_grade;}).length;
    document.getElementById('d-dims').textContent = String(scores.length);
    document.getElementById('d-pass').textContent = String(passing);
    document.getElementById('d-divs').textContent = String(divs);
    document.getElementById('d-fail').textContent = String(failing);
    document.getElementById('d-reviewed').textContent = reviewed+'/'+scores.length;

    var tbody = document.getElementById('dash-tbody');
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
    if (!scores.length) {
      var emptyTr = el('tr'); emptyTr.appendChild(el('td',{colspan:'6',style:{textAlign:'center',color:'var(--muted)',padding:'20px'}},'Run an audit to see results'));
      tbody.appendChild(emptyTr); return;
    }
    scores.forEach(function(s) {
      var grade = scoreToGrade(s.auto_score);
      var color = scoreColor(s.auto_score);
      var status = 'ok', statusLabel = 'OK';
      if (s.auto_score<=0.5){status='fail';statusLabel='FAIL';}
      else if (s.divergent&&!s.acknowledged){status='warn';statusLabel='DIVERGED';}
      var tr = el('tr');
      tr.appendChild(el('td',{style:{fontWeight:'600'}},s.name));
      var barFill = el('div',{className:'score-bar-fill',style:{width:Math.round(s.auto_score*100)+'%',background:color}});
      tr.appendChild(el('td',null,[el('div',{className:'score-bar'},[barFill])]));
      tr.appendChild(el('td',{style:{fontWeight:'700',color:color}},grade));
      tr.appendChild(el('td',null,s.manual_grade||'\\u2014'));
      tr.appendChild(el('td',null,[el('span',{className:'status-badge '+status},statusLabel)]));
      tr.appendChild(el('td',{style:{fontFamily:'var(--mono)',fontSize:'12px'}},Math.round((s.auto_confidence||0)*100)+'%'));
      tbody.appendChild(tr);
    });
  } catch(e) { console.error(e); }
}

async function runAudit(tier) {
  toast('Running '+tier+'...','');
  try {
    await api('/api/run/'+encodeURIComponent(tier),{method:'POST'});
    toast('Completed '+tier+' tier','success');
    refreshDashboard();
  } catch(e) { toast('Failed: '+e.message,'error'); }
}

/* ── Dimensions ──────────────────────────────────────────────── */
async function refreshDimensions() {
  var dims = await api('/api/dimensions');
  var tbody = document.getElementById('dim-tbody');
  while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
  if (!dims.length) {
    var emptyTr = el('tr'); emptyTr.appendChild(el('td',{colspan:'4',style:{textAlign:'center',color:'var(--muted)',padding:'20px'}},'No dimensions registered'));
    tbody.appendChild(emptyTr); return;
  }
  dims.forEach(function(d) {
    var tr = el('tr');
    tr.appendChild(el('td',{style:{fontWeight:'600'}},d.name));
    tr.appendChild(el('td',null,d.tier));
    tr.appendChild(el('td',{style:{fontFamily:'var(--mono)'}},Math.round(d.confidence*100)+'%'));
    tr.appendChild(el('td',{style:{color:'var(--muted)',fontSize:'12px'}},d.description||''));
    tbody.appendChild(tr);
  });
}

/* ── Baseline Editor ─────────────────────────────────────────── */
async function refreshBaseline() {
  var dims = await api('/api/dimensions');
  var baseline = await api('/api/baseline');
  var bdims = baseline.dimensions || {};
  var ratchets = baseline.ratchets || {};
  var grid = document.getElementById('baseline-grid');
  while (grid.firstChild) grid.removeChild(grid.firstChild);
  if (!dims.length) { grid.appendChild(el('p',{style:{color:'var(--muted)'}},'No dimensions registered')); return; }

  dims.forEach(function(d) {
    var entry = bdims[d.name] || {};
    var card = el('div',{className:'baseline-card'});
    card.appendChild(el('h4',null,d.name));

    // Grade selector
    var gradeRow = el('div',{className:'baseline-row'});
    gradeRow.appendChild(el('label',null,'Grade'));
    var select = el('select',{className:'baseline-select','data-dim':d.name});
    select.appendChild(el('option',{value:''},'\\u2014 not set'));
    GRADES.forEach(function(g) {
      var opt = el('option',{value:g},g);
      if (entry.grade===g) opt.selected = true;
      select.appendChild(opt);
    });
    select.addEventListener('change',function(){saveGrade(d.name,select.value);});
    gradeRow.appendChild(select);
    card.appendChild(gradeRow);

    // Notes
    var notesRow = el('div',{className:'baseline-row'});
    notesRow.appendChild(el('label',null,'Notes'));
    var input = el('input',{className:'baseline-input',type:'text',value:entry.notes||'',placeholder:'Optional notes...'});
    input.addEventListener('change',function(){saveGrade(d.name,select.value,input.value);});
    notesRow.appendChild(input);
    card.appendChild(notesRow);

    // Source + updated
    if (entry.source) {
      card.appendChild(el('div',{style:{fontSize:'11px',color:'var(--muted)',marginTop:'6px'}},
        entry.source+' \\u00b7 '+(entry.updated||'unknown')));
    }

    grid.appendChild(card);
  });
}

async function saveGrade(dim, grade, notes) {
  if (!grade) return;
  await api('/api/baseline/grade',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({dimension:dim,grade:grade,notes:notes||''})});
  toast('Saved '+dim+' = '+grade,'success');
}

/* ── Export ───────────────────────────────────────────────────── */
async function exportReport(fmt) {
  try {
    var r = await fetch('/api/export/'+fmt);
    var text = await r.text();
    var pre = document.getElementById('export-output');
    pre.textContent = text;
    pre.style.display = 'block';
  } catch(e) { toast('Export failed','error'); }
}

/* ── Init ────────────────────────────────────────────────────── */
loadRecents();
loadPresets();

// Check if project already loaded (e.g., from URL param)
api('/api/project/status').then(function(s) {
  if (s.loaded) {
    updateSidebar(s.path, s.dimensions);
  }
});
</script>
</body>
</html>"""
