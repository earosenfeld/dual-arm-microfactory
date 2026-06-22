from __future__ import annotations

import html
import json
from pathlib import Path

from microfactory.control.assembly import AssemblyResult
from microfactory.reporting.metrics import summarize_run


def write_static_dashboard(result: AssemblyResult, output_path: Path) -> None:
    payload = {
        "success": result.success,
        "metrics": summarize_run(result).as_dict(),
        "state": result.state.as_dict(),
        "events": result.log.as_list(),
    }
    serialized = json.dumps(payload, indent=2)
    escaped = html.escape(serialized)
    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dual-Arm Microfactory Replay</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0c1016;
      --band: #101821;
      --panel: #151d27;
      --panel-2: #1b2632;
      --line: #2a3948;
      --text: #eef4fa;
      --muted: #9dadbd;
      --blue: #62b6ff;
      --green: #57d68d;
      --yellow: #f2c14e;
      --red: #ff6b6b;
      --cyan: #6ee7e7;
      --violet: #b99cff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    main {
      width: min(1480px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }
    header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 20px;
      align-items: end;
      margin-bottom: 18px;
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 {
      margin-bottom: 8px;
      font-size: clamp(30px, 4vw, 56px);
      letter-spacing: 0;
      line-height: 1;
    }
    h2 { font-size: 18px; margin-bottom: 12px; }
    .subhead {
      color: var(--muted);
      font-size: 16px;
      max-width: 900px;
      line-height: 1.45;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 104px;
      height: 38px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--panel);
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .pill.pass { color: var(--green); border-color: rgba(87, 214, 141, 0.45); }
    .pill.fail { color: var(--red); border-color: rgba(255, 107, 107, 0.45); }
    .layout {
      display: grid;
      grid-template-columns: minmax(720px, 1.5fr) minmax(360px, 0.75fr);
      gap: 16px;
      align-items: start;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    .panel-body { padding: 16px; }
    .viewport-shell {
      position: relative;
      min-height: 620px;
      background:
        radial-gradient(circle at 42% 22%, rgba(98, 182, 255, 0.10), transparent 34%),
        linear-gradient(180deg, #101923 0%, #0d131a 100%);
    }
    canvas {
      display: block;
      width: 100%;
      height: 620px;
    }
    .viewport-toolbar {
      position: absolute;
      top: 12px;
      left: 12px;
      right: 12px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      pointer-events: none;
    }
    .viewport-toolbar > div {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      pointer-events: auto;
    }
    .hud {
      position: absolute;
      left: 12px;
      bottom: 12px;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      width: calc(100% - 24px);
      pointer-events: none;
    }
    .hud-chip,
    .legend-chip {
      border: 1px solid rgba(121, 147, 170, 0.32);
      background: rgba(16, 24, 33, 0.88);
      border-radius: 8px;
      padding: 10px;
      backdrop-filter: blur(10px);
    }
    .hud-label {
      color: var(--muted);
      font-size: 11px;
      margin-bottom: 7px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    .hud-value {
      font-size: 15px;
      font-weight: 800;
      overflow-wrap: anywhere;
    }
    .controls {
      display: grid;
      grid-template-columns: auto auto auto auto minmax(180px, 1fr) auto auto;
      gap: 10px;
      align-items: center;
      padding: 12px 16px;
      border-top: 1px solid var(--line);
      background: var(--band);
    }
    button,
    select {
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--text);
      border-radius: 8px;
      padding: 9px 12px;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { border-color: var(--blue); }
    button.active { border-color: var(--blue); color: var(--blue); background: #17293a; }
    input[type="range"] { width: 100%; accent-color: var(--blue); }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .metric {
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 82px;
    }
    .metric-label {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }
    .metric-value {
      font-size: 24px;
      font-weight: 800;
      line-height: 1;
    }
    .event-list {
      display: grid;
      gap: 8px;
      max-height: 500px;
      overflow: auto;
      padding-right: 4px;
    }
    .filter-bar {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 12px;
    }
    .filter-bar button {
      padding: 8px 10px;
      color: var(--muted);
    }
    .filter-bar button.active {
      border-color: var(--blue);
      color: var(--blue);
      background: #17293a;
    }
    .event {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
      padding: 10px;
      cursor: pointer;
    }
    .event.active { border-color: var(--blue); background: #1b2d3d; }
    .event-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 4px;
      color: var(--muted);
      font-size: 12px;
    }
    .event-msg {
      font-size: 13px;
      line-height: 1.35;
    }
    .status-pass { color: var(--green); }
    .status-warn { color: var(--yellow); }
    .status-fail { color: var(--red); }
    .status-recovered { color: var(--blue); }
    .details {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 16px;
    }
    .log-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .log-table th, .log-table td {
      padding: 9px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    .log-table th { color: var(--muted); font-weight: 600; }
    pre {
      white-space: pre-wrap;
      background: #090d12;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      max-height: 420px;
      overflow: auto;
      font-size: 12px;
      color: #cbd7e3;
    }
    .callout {
      background: #112437;
      border: 1px solid rgba(98, 182, 255, 0.35);
      border-radius: 8px;
      padding: 14px;
      line-height: 1.45;
      color: #dcecff;
    }
    .legend {
      position: absolute;
      right: 12px;
      bottom: 112px;
      display: grid;
      gap: 6px;
      width: 178px;
      pointer-events: none;
    }
    .legend-row {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
    }
    .swatch {
      width: 13px;
      height: 13px;
      border-radius: 3px;
      border: 1px solid rgba(255,255,255,0.25);
    }
    .recording-mode main {
      width: min(1320px, calc(100vw - 24px));
      padding-top: 12px;
    }
    .recording-mode header,
    .recording-mode .details,
    .recording-mode aside {
      display: none;
    }
    .recording-mode .layout {
      grid-template-columns: 1fr;
    }
    .recording-mode canvas {
      height: 780px;
    }
    .recording-mode .viewport-shell {
      min-height: 780px;
    }
    @media (max-width: 1120px) {
      .layout { grid-template-columns: 1fr; }
      .viewport-shell { min-height: 520px; }
      canvas { height: 520px; }
      .details { grid-template-columns: 1fr; }
      .hud { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 720px) {
      main { width: min(100vw - 24px, 1480px); padding-top: 18px; }
      header { grid-template-columns: 1fr; }
      .controls { grid-template-columns: 1fr 1fr; }
      .metric-grid { grid-template-columns: 1fr; }
      .hud { grid-template-columns: 1fr; }
      .legend { display: none; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Dual-Arm Autonomous Microfactory</h1>
        <p class="subhead">RoboDK/RViz-style replay: two arms assemble a mini conveyor, visualize planned motion, detect failures, recover, and produce acceptance evidence.</p>
      </div>
      <div id="final-pill" class="pill">RUN</div>
    </header>

    <section class="layout">
      <div class="panel">
        <div class="viewport-shell">
          <canvas id="robotViewport" width="1400" height="860" aria-label="Robotics workcell viewport"></canvas>
          <div class="viewport-toolbar">
            <div>
              <button class="active" data-view="iso">Iso</button>
              <button data-view="top">Top</button>
              <button data-view="side">Side</button>
            </div>
            <div>
              <button id="fitViewBtn">Fit View</button>
            </div>
          </div>
          <div class="legend legend-chip">
            <div class="legend-row"><span class="swatch" style="background:#62b6ff"></span>left arm</div>
            <div class="legend-row"><span class="swatch" style="background:#b99cff"></span>right arm</div>
            <div class="legend-row"><span class="swatch" style="background:#57d68d"></span>accepted</div>
            <div class="legend-row"><span class="swatch" style="background:#ff6b6b"></span>fault</div>
          </div>
          <div class="hud">
            <div class="hud-chip">
              <div class="hud-label">Sim Time</div>
              <div class="hud-value" id="currentTime">0.0s</div>
            </div>
            <div class="hud-chip">
              <div class="hud-label">Phase</div>
              <div class="hud-value" id="currentPhase">idle</div>
            </div>
            <div class="hud-chip">
              <div class="hud-label">Status</div>
              <div class="hud-value" id="currentStatus">pending</div>
            </div>
            <div class="hud-chip">
              <div class="hud-label">Focus</div>
              <div class="hud-value" id="currentFocus">full sequence</div>
            </div>
          </div>
        </div>
        <div class="controls">
          <button id="playBtn">Play</button>
          <button id="resetBtn">Reset</button>
          <button id="prevCriticalBtn">Prev Critical</button>
          <button id="nextCriticalBtn">Next Critical</button>
          <input id="scrubber" type="range" min="0" max="0" value="0" step="1" aria-label="Replay scrubber">
          <select id="speedSelect" aria-label="Playback speed">
            <option value="700">0.6x</option>
            <option value="420" selected>1x</option>
            <option value="240">1.75x</option>
            <option value="120">3.5x</option>
          </select>
          <button id="recordingModeBtn">Recording</button>
          <span id="stepLabel" class="muted">0 / 0</span>
        </div>
      </div>

      <aside class="panel">
        <div class="panel-body">
          <h2>Run Metrics</h2>
          <div class="metric-grid" id="metrics"></div>
        </div>
        <div class="panel-body" style="border-top: 1px solid var(--line);">
          <h2>Replay Timeline</h2>
          <div class="filter-bar" id="filterBar">
            <button class="active" data-filter="all">All</button>
            <button data-filter="critical">Critical</button>
            <button data-filter="recovery">Recovery</button>
            <button data-filter="planning">Planning</button>
          </div>
          <div class="event-list" id="eventList"></div>
        </div>
      </aside>
    </section>

    <section class="details">
      <div class="panel">
        <div class="panel-body">
          <h2>What This Proves</h2>
          <div class="callout">
            This is not a happy-path pick-and-place. The replay visualizes tool motion,
            planned paths, perception confidence, bimanual stabilization, autonomous recovery,
            and the final functional test from generated event data.
          </div>
          <div style="margin-top: 12px;">
            <button id="copySummaryBtn">Copy Run Summary</button>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-body">
          <h2>Critical Events</h2>
          <table class="log-table">
            <thead><tr><th>#</th><th>Phase</th><th>Status</th><th>Message</th></tr></thead>
            <tbody id="criticalRows"></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-body">
          <h2>Raw Run Payload</h2>
          <pre>__RAW_PAYLOAD__</pre>
        </div>
      </div>
    </section>
  </main>

  <script>
    const payload = __PAYLOAD__;
    const events = payload.events;
    const canvas = document.getElementById("robotViewport");
    const ctx = canvas.getContext("2d");
    let index = 0;
    let playing = false;
    let timer = null;
    let playbackMs = 420;
    let eventFilter = "all";
    let viewMode = "iso";
    let animationFrame = null;

    const el = (id) => document.getElementById(id);
    const statusClass = (status) => `status-${status}`;
    const criticalPhases = new Set(["active_vision", "bimanual_coordination", "functional_test"]);
    const colors = {
      left: "#62b6ff",
      right: "#b99cff",
      accepted: "#57d68d",
      warning: "#f2c14e",
      fault: "#ff6b6b",
      grid: "rgba(128, 159, 184, 0.22)",
      text: "#dce7f2",
      muted: "#8da0b2",
      base: "#6ee7e7",
      roller: "#f2c14e",
      belt: "#57d68d",
      motor: "#b99cff",
      sensor: "#62b6ff",
    };

    const world = {
      leftBase: { x: -2.7, y: 1.35, z: 0 },
      rightBase: { x: 2.7, y: 1.35, z: 0 },
      tray: { x: -2.45, y: -0.75, z: 0 },
      reject: { x: 2.45, y: -0.75, z: 0 },
      fixture: { x: 0, y: 0, z: 0 },
      camera: { x: 0, y: -2.1, z: 2.9 },
    };

    function resizeCanvas() {
      const rect = canvas.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.max(900, Math.floor(rect.width * ratio));
      canvas.height = Math.max(520, Math.floor(rect.height * ratio));
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      drawScene();
    }

    function setText(id, value) {
      el(id).textContent = value;
    }

    function isCritical(event) {
      return event.status !== "pass" || criticalPhases.has(event.phase);
    }

    function isPlanning(event) {
      return event.phase === "motion_planning" || event.phase === "grasp_planning";
    }

    function filteredEvents() {
      if (eventFilter === "critical") {
        return events.map((event, i) => [event, i]).filter(([event]) => isCritical(event));
      }
      if (eventFilter === "recovery") {
        return events.map((event, i) => [event, i]).filter(([event]) => event.status === "recovered" || event.phase === "recovery");
      }
      if (eventFilter === "planning") {
        return events.map((event, i) => [event, i]).filter(([event]) => isPlanning(event));
      }
      return events.map((event, i) => [event, i]);
    }

    function currentEvent() {
      return events[Math.max(0, Math.min(index, events.length - 1))];
    }

    function project(point) {
      const rect = canvas.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;
      const scale = Math.min(w / 7.2, h / 5.1);
      const cx = w * 0.5;
      const cy = h * 0.61;
      if (viewMode === "top") {
        return { x: cx + point.x * scale, y: cy + point.y * scale, z: point.z };
      }
      if (viewMode === "side") {
        return { x: cx + point.x * scale, y: cy - point.z * scale * 0.9 + point.y * scale * 0.12, z: point.z };
      }
      return {
        x: cx + (point.x - point.y) * scale * 0.78,
        y: cy + (point.x + point.y) * scale * 0.36 - point.z * scale * 0.9,
        z: point.z,
      };
    }

    function sceneState(eventIndex = index) {
      const state = {
        installed: new Set(),
        hiddenLoose: new Set(),
        beltColor: colors.belt,
        fixtureColor: "#526b7f",
        leftTool: { x: -1.25, y: 0.25, z: 1.35 },
        rightTool: { x: 1.25, y: 0.25, z: 1.35 },
        leftTarget: null,
        rightTarget: null,
        plannedPath: null,
        cameraPulse: false,
        activePose: null,
        puckProgress: 0,
        status: "idle",
      };

      for (let i = 0; i <= eventIndex; i += 1) {
        const event = events[i];
        const msg = event.message.toLowerCase();
        const details = event.details || {};
        state.status = event.status;
        if (event.status === "fail") {
          state.fixtureColor = colors.fault;
        } else if (event.status === "recovered") {
          state.fixtureColor = colors.left;
        }
        if (event.phase === "perception" || event.phase === "active_vision") {
          state.cameraPulse = true;
          const detection = details.detection;
          if (detection) {
            state.activePose = poseToWorld(detection.pose, detection.kind);
          }
        }
        if (event.phase === "motion_planning" && details.plan) {
          const target = planTargetToWorld(details.plan);
          state.plannedPath = {
            arm: details.plan.arm,
            start: details.plan.arm === "left_arm" ? state.leftTool : state.rightTool,
            target,
            clearance: details.plan.min_clearance_mm,
            status: details.plan.status,
          };
          if (details.plan.arm === "left_arm") {
            state.leftTarget = target;
            state.leftTool = target;
          } else {
            state.rightTarget = target;
            state.rightTool = target;
          }
        }
        if (event.phase === "bimanual_coordination") {
          if (details.assist_arm === "left_arm") {
            state.leftTool = { x: -0.42, y: 0.05, z: 0.75 };
          }
          if (details.assist_arm === "right_arm") {
            state.rightTool = { x: 0.42, y: 0.05, z: 0.75 };
          }
        }
        if (event.phase === "execution") {
          if (msg.includes("left_arm")) {
            state.leftTool = { x: -0.28, y: -0.02, z: 0.62 };
          }
          if (msg.includes("right_arm")) {
            state.rightTool = { x: 0.28, y: -0.02, z: 0.62 };
          }
        }
        if (msg.includes("installed base")) {
          state.hiddenLoose.add("base");
          state.installed.add("base");
        }
        if (msg.includes("installed roller")) {
          if (!state.installed.has("rollerA")) {
            state.hiddenLoose.add("rollerA");
            state.installed.add("rollerA");
          } else {
            state.hiddenLoose.add("rollerB");
            state.installed.add("rollerB");
          }
        }
        if (msg.includes("belt placed") || msg.includes("belt slip")) {
          state.hiddenLoose.add("belt");
          state.installed.add("belt");
          state.beltColor = event.status === "fail" ? colors.fault : colors.belt;
        }
        if (msg.includes("re-tensioning")) {
          state.beltColor = colors.left;
        }
        if (msg.includes("installed motor")) {
          state.hiddenLoose.add("motor");
          state.installed.add("motor");
        }
        if (msg.includes("installed sensor")) {
          state.hiddenLoose.add("sensor");
          state.installed.add("sensor");
        }
        if (event.phase === "functional_test" && event.status === "pass") {
          state.fixtureColor = colors.accepted;
          state.puckProgress = 1;
        }
      }
      return state;
    }

    function lerp(a, b, t) {
      return a + (b - a) * t;
    }

    function easeInOut(t) {
      return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }

    function lerpPoint(a, b, t) {
      return {
        x: lerp(a.x, b.x, t),
        y: lerp(a.y, b.y, t),
        z: lerp(a.z, b.z, t),
      };
    }

    function lerpScene(from, to, t) {
      const eased = easeInOut(t);
      return {
        ...to,
        leftTool: lerpPoint(from.leftTool, to.leftTool, eased),
        rightTool: lerpPoint(from.rightTool, to.rightTool, eased),
        puckProgress: lerp(from.puckProgress, to.puckProgress, eased),
      };
    }

    function poseToWorld(pose, kind) {
      const kindOffsets = {
        base_plate: { x: -2.45, y: -0.95, z: 0.1 },
        roller: { x: -2.55, y: -0.45, z: 0.16 },
        belt: { x: -2.35, y: 0.08, z: 0.14 },
        motor: { x: -2.75, y: 0.65, z: 0.18 },
        sensor: { x: -2.08, y: 0.68, z: 0.16 },
      };
      return kindOffsets[kind] || { x: -2.35, y: -0.5, z: 0.2 };
    }

    function planTargetToWorld(plan) {
      const target = plan.target || {};
      const x = Number(target.x ?? 0);
      const y = Number(target.y ?? 0);
      const z = Number(target.z ?? 0.2);
      if (Math.abs(x) < 0.03 && Math.abs(y) < 0.03) {
        return { x: plan.arm === "left_arm" ? -0.18 : 0.18, y: 0.0, z: 0.76 };
      }
      return {
        x: Math.max(-2.85, Math.min(2.85, (x - 0.35) * 6.0)),
        y: Math.max(-1.3, Math.min(1.35, (y - 0.42) * 5.0)),
        z: Math.max(0.22, Math.min(1.5, z * 6.0)),
      };
    }

    function clearCanvas() {
      const rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      const gradient = ctx.createLinearGradient(0, 0, 0, rect.height);
      gradient.addColorStop(0, "#111b25");
      gradient.addColorStop(1, "#0c1118");
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, rect.width, rect.height);
    }

    function line3(a, b, color, width = 1.5, dash = []) {
      const pa = project(a);
      const pb = project(b);
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.setLineDash(dash);
      ctx.beginPath();
      ctx.moveTo(pa.x, pa.y);
      ctx.lineTo(pb.x, pb.y);
      ctx.stroke();
      ctx.restore();
    }

    function fillEllipse3(center, rx, ry, color, stroke = "rgba(255,255,255,0.18)") {
      const p = project(center);
      ctx.save();
      ctx.fillStyle = color;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(p.x, p.y, rx, ry, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }

    function drawLabel(text, point, color = colors.muted) {
      const p = project(point);
      ctx.save();
      ctx.fillStyle = color;
      ctx.font = "12px Inter, Segoe UI, sans-serif";
      ctx.fillText(text, p.x + 8, p.y - 8);
      ctx.restore();
    }

    function drawBox(center, size, color, stroke = "rgba(255,255,255,0.22)") {
      const p = project({ x: center.x, y: center.y, z: center.z + size.z });
      const base = project(center);
      const w = size.x * 72;
      const d = size.y * 32;
      const h = Math.max(8, (base.y - p.y));
      ctx.save();
      ctx.fillStyle = color;
      ctx.strokeStyle = stroke;
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.roundRect(p.x - w / 2, p.y - h / 2, w, Math.max(10, h), 4);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "rgba(255,255,255,0.08)";
      ctx.fillRect(p.x - w / 2, p.y - h / 2, w, 5);
      if (d > 0) {
        ctx.strokeStyle = "rgba(0,0,0,0.28)";
        ctx.strokeRect(p.x - w / 2 + 4, p.y - h / 2 + 4, w, Math.max(10, h));
      }
      ctx.restore();
    }

    function drawGrid() {
      for (let i = -4; i <= 4; i += 0.5) {
        const major = Math.abs(i % 1) < 0.01;
        line3({ x: -4, y: i, z: 0 }, { x: 4, y: i, z: 0 }, major ? "rgba(128,159,184,0.26)" : "rgba(128,159,184,0.12)", major ? 1.3 : 0.8);
        line3({ x: i, y: -2.4, z: 0 }, { x: i, y: 2.3, z: 0 }, major ? "rgba(128,159,184,0.26)" : "rgba(128,159,184,0.12)", major ? 1.3 : 0.8);
      }
      line3({ x: 0, y: 0, z: 0 }, { x: 1.2, y: 0, z: 0 }, "#ff6b6b", 3);
      line3({ x: 0, y: 0, z: 0 }, { x: 0, y: 1.2, z: 0 }, "#57d68d", 3);
      line3({ x: 0, y: 0, z: 0 }, { x: 0, y: 0, z: 1.2 }, "#62b6ff", 3);
      drawLabel("X", { x: 1.25, y: 0, z: 0 }, "#ff8f8f");
      drawLabel("Y", { x: 0, y: 1.25, z: 0 }, "#8ff0b5");
      drawLabel("Z", { x: 0, y: 0, z: 1.25 }, "#9ed0ff");
    }

    function drawCamera(state) {
      drawBox(world.camera, { x: 0.6, y: 0.32, z: 0.18 }, "rgba(36,56,74,0.95)", colors.left);
      const targetA = { x: -0.95, y: -0.35, z: 0 };
      const targetB = { x: 0.95, y: -0.35, z: 0 };
      const targetC = { x: 0.95, y: 0.95, z: 0 };
      const targetD = { x: -0.95, y: 0.95, z: 0 };
      const pulse = state.cameraPulse ? "rgba(98,182,255,0.36)" : "rgba(98,182,255,0.16)";
      [targetA, targetB, targetC, targetD].forEach((target) => line3(world.camera, target, pulse, 1.2, [5, 5]));
      line3(targetA, targetB, pulse, 1);
      line3(targetB, targetC, pulse, 1);
      line3(targetC, targetD, pulse, 1);
      line3(targetD, targetA, pulse, 1);
      drawLabel("RGB-D camera", { x: world.camera.x + 0.25, y: world.camera.y, z: world.camera.z + 0.2 }, colors.left);
    }

    function drawWorkcell(state) {
      drawBox({ x: world.tray.x, y: world.tray.y, z: 0.02 }, { x: 1.45, y: 1.25, z: 0.10 }, "rgba(23,35,48,0.92)", "#334557");
      drawLabel("loose parts", { x: world.tray.x - 0.58, y: world.tray.y - 0.56, z: 0.18 });
      drawBox({ x: world.reject.x, y: world.reject.y, z: 0.02 }, { x: 1.45, y: 1.25, z: 0.10 }, "rgba(23,35,48,0.92)", "#334557");
      drawLabel("installed / reject", { x: world.reject.x - 0.58, y: world.reject.y - 0.56, z: 0.18 });
      drawBox({ x: 0, y: 0, z: 0.05 }, { x: 1.55, y: 1.0, z: 0.24 }, "rgba(27,38,50,0.96)", state.fixtureColor);
      drawLabel("assembly fixture", { x: -0.52, y: -0.48, z: 0.4 }, state.fixtureColor);

      if (!state.hiddenLoose.has("base")) drawBox({ x: -2.7, y: -1.0, z: 0.18 }, { x: 0.85, y: 0.28, z: 0.12 }, colors.base);
      if (!state.hiddenLoose.has("rollerA")) fillEllipse3({ x: -2.85, y: -0.45, z: 0.26 }, 16, 10, colors.roller);
      if (!state.hiddenLoose.has("rollerB")) fillEllipse3({ x: -2.35, y: -0.42, z: 0.26 }, 16, 10, colors.roller);
      if (!state.hiddenLoose.has("belt")) drawBelt({ x: -2.58, y: 0.18, z: 0.22 }, 0.75, 0.26, colors.belt);
      if (!state.hiddenLoose.has("motor")) drawBox({ x: -2.92, y: 0.75, z: 0.22 }, { x: 0.32, y: 0.32, z: 0.26 }, colors.motor);
      if (!state.hiddenLoose.has("sensor")) drawBox({ x: -2.16, y: 0.76, z: 0.18 }, { x: 0.34, y: 0.22, z: 0.14 }, colors.sensor);

      if (state.installed.has("base")) drawBox({ x: 0, y: 0, z: 0.28 }, { x: 1.18, y: 0.36, z: 0.12 }, colors.base);
      if (state.installed.has("rollerA")) fillEllipse3({ x: -0.42, y: 0, z: 0.48 }, 18, 10, colors.roller);
      if (state.installed.has("rollerB")) fillEllipse3({ x: 0.42, y: 0, z: 0.48 }, 18, 10, colors.roller);
      if (state.installed.has("belt")) drawBelt({ x: 0, y: 0, z: 0.52 }, 1.0, 0.26, state.beltColor);
      if (state.installed.has("motor")) drawBox({ x: 0.78, y: 0.02, z: 0.45 }, { x: 0.28, y: 0.3, z: 0.24 }, colors.motor);
      if (state.installed.has("sensor")) drawBox({ x: -0.72, y: 0.32, z: 0.42 }, { x: 0.32, y: 0.18, z: 0.14 }, colors.sensor);
      if (state.puckProgress > 0) {
        fillEllipse3({ x: -0.42 + state.puckProgress * 0.86, y: 0.04, z: 0.68 }, 9, 6, "#ffffff", "rgba(255,255,255,0.55)");
      }
    }

    function drawBelt(center, width, depth, color) {
      const a = project({ x: center.x - width / 2, y: center.y - depth / 2, z: center.z });
      const b = project({ x: center.x + width / 2, y: center.y - depth / 2, z: center.z });
      const c = project({ x: center.x + width / 2, y: center.y + depth / 2, z: center.z });
      const d = project({ x: center.x - width / 2, y: center.y + depth / 2, z: center.z });
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = 7;
      ctx.lineJoin = "round";
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.lineTo(c.x, c.y);
      ctx.lineTo(d.x, d.y);
      ctx.closePath();
      ctx.stroke();
      ctx.restore();
    }

    function drawRobotArm(base, tool, color, label) {
      const shoulder = { x: base.x, y: base.y, z: 0.62 };
      const elbow = {
        x: base.x * 0.58 + tool.x * 0.42,
        y: base.y * 0.58 + tool.y * 0.42,
        z: Math.max(0.95, tool.z + 0.35),
      };
      drawBox({ x: base.x, y: base.y, z: 0.08 }, { x: 0.42, y: 0.42, z: 0.18 }, "rgba(27,38,50,0.98)", color);
      line3(shoulder, elbow, color, 8);
      line3(elbow, tool, color, 8);
      fillEllipse3(shoulder, 12, 8, color);
      fillEllipse3(elbow, 10, 7, color);
      fillEllipse3(tool, 9, 6, color);
      drawLabel(label, { x: base.x - 0.2, y: base.y + 0.18, z: 0.32 }, color);
    }

    function drawPlannedPath(state) {
      if (!state.plannedPath) return;
      const path = state.plannedPath;
      const color = path.status === "warn" ? colors.warning : colors.left;
      line3(path.start, path.target, color, 2.5, [8, 6]);
      fillEllipse3(path.target, 12, 8, color, "rgba(255,255,255,0.35)");
      drawLabel(`${path.arm.replace("_arm", "")} target / ${path.clearance}mm clearance`, { x: path.target.x + 0.1, y: path.target.y, z: path.target.z + 0.2 }, color);
    }

    function drawActivePose(state) {
      if (!state.activePose) return;
      const p = state.activePose;
      line3({ x: p.x - 0.18, y: p.y, z: p.z }, { x: p.x + 0.18, y: p.y, z: p.z }, colors.yellow, 2);
      line3({ x: p.x, y: p.y - 0.18, z: p.z }, { x: p.x, y: p.y + 0.18, z: p.z }, colors.yellow, 2);
      line3({ x: p.x, y: p.y, z: p.z - 0.12 }, { x: p.x, y: p.y, z: p.z + 0.18 }, colors.yellow, 2);
      drawLabel("pose estimate", { x: p.x + 0.08, y: p.y + 0.08, z: p.z + 0.16 }, colors.yellow);
    }

    function drawScene(state = sceneState()) {
      clearCanvas();
      drawGrid();
      drawCamera(state);
      drawWorkcell(state);
      drawPlannedPath(state);
      drawActivePose(state);
      drawRobotArm(world.leftBase, state.leftTool, colors.left, "left arm");
      drawRobotArm(world.rightBase, state.rightTool, colors.right, "right arm");
      drawViewportText(state);
    }

    function animateScene(from, to) {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
      const durationMs = Math.min(380, Math.max(180, playbackMs * 0.72));
      const started = performance.now();
      const frame = (now) => {
        const t = Math.min(1, (now - started) / durationMs);
        drawScene(lerpScene(from, to, t));
        if (t < 1) {
          animationFrame = requestAnimationFrame(frame);
        } else {
          animationFrame = null;
          drawScene(to);
        }
      };
      animationFrame = requestAnimationFrame(frame);
    }

    function drawViewportText(state) {
      const rect = canvas.getBoundingClientRect();
      const event = currentEvent();
      ctx.save();
      ctx.fillStyle = "rgba(12, 16, 22, 0.70)";
      ctx.strokeStyle = "rgba(128, 159, 184, 0.24)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(18, rect.height - 96, Math.min(720, rect.width - 36), 72, 8);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = statusToColor(event.status);
      ctx.font = "700 14px Inter, Segoe UI, sans-serif";
      ctx.fillText(`${event.phase} [${event.status}]`, 34, rect.height - 64);
      ctx.fillStyle = colors.text;
      ctx.font = "13px Inter, Segoe UI, sans-serif";
      wrapText(event.message, 34, rect.height - 40, Math.min(680, rect.width - 76), 17);
      ctx.restore();
    }

    function wrapText(text, x, y, maxWidth, lineHeight) {
      const words = text.split(" ");
      let line = "";
      for (const word of words) {
        const test = line ? `${line} ${word}` : word;
        if (ctx.measureText(test).width > maxWidth && line) {
          ctx.fillText(line, x, y);
          line = word;
          y += lineHeight;
        } else {
          line = test;
        }
      }
      ctx.fillText(line, x, y);
    }

    function statusToColor(status) {
      if (status === "fail") return colors.fault;
      if (status === "warn") return colors.warning;
      if (status === "recovered") return colors.left;
      return colors.accepted;
    }

    function renderAt(nextIndex) {
      const oldIndex = index;
      const from = sceneState(oldIndex);
      index = Math.max(0, Math.min(nextIndex, events.length - 1));
      const target = sceneState(index);
      const current = currentEvent();
      setText("currentTime", `${current.sim_time_s.toFixed(1)}s`);
      setText("currentPhase", current.phase);
      setText("currentStatus", current.status);
      setText("currentFocus", isCritical(current) ? "critical event" : "normal sequence");
      el("scrubber").value = String(index);
      setText("stepLabel", `${index + 1} / ${events.length}`);
      if (Math.abs(index - oldIndex) === 1) {
        animateScene(from, target);
      } else {
        if (animationFrame) {
          cancelAnimationFrame(animationFrame);
          animationFrame = null;
        }
        drawScene(target);
      }
      document.querySelectorAll(".event").forEach((node) => node.classList.remove("active"));
      const active = document.querySelector(`[data-event-index="${index}"]`);
      if (active) {
        active.classList.add("active");
        active.scrollIntoView({ block: "nearest" });
      }
    }

    function play() {
      if (playing) {
        playing = false;
        clearInterval(timer);
        el("playBtn").textContent = "Play";
        return;
      }
      playing = true;
      el("playBtn").textContent = "Pause";
      timer = setInterval(() => {
        if (index >= events.length - 1) {
          playing = false;
          clearInterval(timer);
          el("playBtn").textContent = "Replay";
          return;
        }
        renderAt(index + 1);
      }, playbackMs);
    }

    function restartPlaybackIfNeeded() {
      if (!playing) return;
      clearInterval(timer);
      playing = false;
      play();
    }

    function jumpCritical(direction) {
      const start = index + direction;
      for (let i = start; i >= 0 && i < events.length; i += direction) {
        if (isCritical(events[i])) {
          renderAt(i);
          return;
        }
      }
    }

    function runSummaryText() {
      const m = payload.metrics;
      return [
        "Dual-Arm Autonomous Microfactory replay",
        `Final status: ${m.final_status}`,
        `Recoveries: ${m.recovered_events}`,
        `Active vision events: ${m.active_vision_events}`,
        `Bimanual assists: ${m.bimanual_events}`,
        `Motion plans: ${m.motion_plan_count}`,
        `Minimum clearance: ${m.minimum_clearance_mm} mm`,
        `Average planning time: ${m.average_planning_time_ms} ms`,
        `Simulated elapsed time: ${m.simulated_elapsed_s}s`,
      ].join("\\n");
    }

    async function copyRunSummary() {
      const text = runSummaryText();
      try {
        await navigator.clipboard.writeText(text);
        el("copySummaryBtn").textContent = "Copied";
      } catch {
        const area = document.createElement("textarea");
        area.value = text;
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        area.remove();
        el("copySummaryBtn").textContent = "Copied";
      }
      setTimeout(() => {
        el("copySummaryBtn").textContent = "Copy Run Summary";
      }, 1400);
    }

    function renderMetrics() {
      const metrics = payload.metrics;
      const items = [
        ["Final status", metrics.final_status],
        ["Recovery events", metrics.recovered_events],
        ["Active vision events", metrics.active_vision_events],
        ["Bimanual assists", metrics.bimanual_events],
        ["Motion plans", metrics.motion_plan_count],
        ["Min clearance", `${metrics.minimum_clearance_mm} mm`],
        ["Avg plan time", `${metrics.average_planning_time_ms} ms`],
        ["Sim elapsed", `${metrics.simulated_elapsed_s}s`],
      ];
      el("metrics").innerHTML = items.map(([label, value]) => `
        <div class="metric">
          <div class="metric-label">${label}</div>
          <div class="metric-value">${value}</div>
        </div>
      `).join("");
      const pill = el("final-pill");
      pill.textContent = metrics.final_status;
      pill.classList.add(metrics.final_status === "PASS" ? "pass" : "fail");
    }

    function renderEvents() {
      const rows = filteredEvents();
      el("eventList").innerHTML = rows.map(([event, i]) => `
        <div class="event" data-event-index="${i}">
          <div class="event-top">
            <span>#${event.sequence} ${event.phase}</span>
            <span class="${statusClass(event.status)}">${event.status}</span>
          </div>
          <div class="event-msg">${event.message}</div>
        </div>
      `).join("") || `<div class="event"><div class="event-msg">No events match this filter.</div></div>`;
      document.querySelectorAll(".event").forEach((node) => {
        if (!node.dataset.eventIndex) return;
        node.addEventListener("click", () => renderAt(Number(node.dataset.eventIndex)));
      });
      const critical = events.filter((event) => isCritical(event));
      el("criticalRows").innerHTML = critical.map((event) => `
        <tr>
          <td>${event.sequence}</td>
          <td>${event.phase}</td>
          <td class="${statusClass(event.status)}">${event.status}</td>
          <td>${event.message}</td>
        </tr>
      `).join("");
    }

    el("playBtn").addEventListener("click", play);
    el("resetBtn").addEventListener("click", () => {
      playing = false;
      clearInterval(timer);
      el("playBtn").textContent = "Play";
      renderAt(0);
    });
    el("prevCriticalBtn").addEventListener("click", () => jumpCritical(-1));
    el("nextCriticalBtn").addEventListener("click", () => jumpCritical(1));
    el("speedSelect").addEventListener("change", (event) => {
      playbackMs = Number(event.target.value);
      restartPlaybackIfNeeded();
    });
    el("recordingModeBtn").addEventListener("click", () => {
      document.body.classList.toggle("recording-mode");
      el("recordingModeBtn").textContent = document.body.classList.contains("recording-mode")
        ? "Exit Recording"
        : "Recording";
      requestAnimationFrame(resizeCanvas);
    });
    el("copySummaryBtn").addEventListener("click", copyRunSummary);
    el("fitViewBtn").addEventListener("click", resizeCanvas);
    document.querySelectorAll("[data-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        eventFilter = button.dataset.filter;
        document.querySelectorAll("[data-filter]").forEach((node) => node.classList.remove("active"));
        button.classList.add("active");
        renderEvents();
        renderAt(index);
      });
    });
    document.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => {
        viewMode = button.dataset.view;
        document.querySelectorAll("[data-view]").forEach((node) => node.classList.remove("active"));
        button.classList.add("active");
        drawScene();
      });
    });
    el("scrubber").max = String(Math.max(0, events.length - 1));
    el("scrubber").addEventListener("input", (event) => renderAt(Number(event.target.value)));
    window.addEventListener("resize", resizeCanvas);

    renderMetrics();
    renderEvents();
    resizeCanvas();
    renderAt(0);
  </script>
</body>
</html>
"""
    output_path.write_text(
        template.replace("__PAYLOAD__", serialized).replace("__RAW_PAYLOAD__", escaped),
        encoding="utf-8",
    )
