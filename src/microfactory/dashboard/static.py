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
      --bg: #0d1117;
      --band: #111922;
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
      width: min(1440px, calc(100vw - 40px));
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
    h3 { font-size: 14px; margin-bottom: 8px; color: var(--muted); font-weight: 600; }
    .subhead {
      color: var(--muted);
      font-size: 16px;
      max-width: 860px;
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
      grid-template-columns: minmax(640px, 1.4fr) minmax(360px, 0.8fr);
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
    .stage {
      background:
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(0deg, rgba(255,255,255,0.03) 1px, transparent 1px),
        #0f151c;
      background-size: 48px 48px;
      min-height: 560px;
      position: relative;
    }
    svg {
      width: 100%;
      height: 560px;
      display: block;
    }
    .controls {
      display: grid;
      grid-template-columns: auto auto minmax(180px, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 12px 16px;
      border-top: 1px solid var(--line);
      background: var(--band);
    }
    button {
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--text);
      border-radius: 8px;
      padding: 9px 12px;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { border-color: var(--blue); }
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
      max-height: 514px;
      overflow: auto;
      padding-right: 4px;
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
    .arm-line { stroke-width: 16; stroke-linecap: round; fill: none; }
    .arm-left { stroke: var(--blue); }
    .arm-right { stroke: var(--violet); }
    .part { transition: transform 360ms ease, opacity 240ms ease; }
    .ghost { opacity: 0.2; }
    .label { fill: var(--muted); font-size: 13px; }
    .small-label { fill: var(--muted); font-size: 11px; }
    .fixture-ok { stroke: var(--green); }
    .fixture-alert { stroke: var(--red); }
    @media (max-width: 1080px) {
      .layout { grid-template-columns: 1fr; }
      .stage, svg { min-height: 460px; height: 460px; }
      .details { grid-template-columns: 1fr; }
    }
    @media (max-width: 680px) {
      main { width: min(100vw - 24px, 1440px); padding-top: 18px; }
      header { grid-template-columns: 1fr; }
      .controls { grid-template-columns: 1fr 1fr; }
      .metric-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Dual-Arm Autonomous Microfactory</h1>
        <p class="subhead">Vision-guided assembly replay: two arms build a mini conveyor, detect failures, recover, run a final functional test, and generate an acceptance log.</p>
      </div>
      <div id="final-pill" class="pill">RUN</div>
    </header>

    <section class="layout">
      <div class="panel">
        <div class="stage">
          <svg viewBox="0 0 900 560" role="img" aria-label="Animated microfactory cell replay">
            <defs>
              <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity="0.35"/>
              </filter>
            </defs>
            <rect x="38" y="42" width="824" height="458" rx="18" fill="#101923" stroke="#314150"/>
            <rect x="70" y="96" width="210" height="322" rx="12" fill="#172330" stroke="#334557"/>
            <rect x="620" y="96" width="210" height="322" rx="12" fill="#172330" stroke="#334557"/>
            <text x="82" y="124" class="label">Loose parts tray</text>
            <text x="632" y="124" class="label">Installed / reject area</text>
            <rect id="fixture" x="345" y="218" width="210" height="124" rx="14" fill="#1b2632" stroke="#4b6175" stroke-width="3" filter="url(#softShadow)"/>
            <text x="386" y="290" class="label">assembly fixture</text>
            <rect id="conveyorBase" class="part ghost" x="372" y="250" width="156" height="36" rx="6" fill="#6ee7e7"/>
            <circle id="rollerA" class="part ghost" cx="398" cy="252" r="14" fill="#f2c14e"/>
            <circle id="rollerB" class="part ghost" cx="502" cy="252" r="14" fill="#f2c14e"/>
            <path id="beltPath" class="part ghost" d="M398 236 C430 220 470 220 502 236 M398 268 C430 284 470 284 502 268" fill="none" stroke="#57d68d" stroke-width="8" stroke-linecap="round"/>
            <rect id="motorPart" class="part ghost" x="520" y="248" width="36" height="38" rx="7" fill="#b99cff"/>
            <rect id="sensorPart" class="part ghost" x="354" y="296" width="34" height="22" rx="4" fill="#62b6ff"/>
            <circle id="puck" class="part ghost" cx="388" cy="270" r="8" fill="#ffffff"/>

            <path id="leftArm" class="arm-line arm-left" d="M190 472 L238 376 L316 316"/>
            <circle cx="190" cy="472" r="28" fill="#163247" stroke="#62b6ff" stroke-width="3"/>
            <circle id="leftTool" cx="316" cy="316" r="14" fill="#62b6ff"/>
            <text x="142" y="520" class="label">left arm</text>
            <path id="rightArm" class="arm-line arm-right" d="M710 472 L662 376 L584 316"/>
            <circle cx="710" cy="472" r="28" fill="#2c2247" stroke="#b99cff" stroke-width="3"/>
            <circle id="rightTool" cx="584" cy="316" r="14" fill="#b99cff"/>
            <text x="668" y="520" class="label">right arm</text>

            <g id="looseParts">
              <rect id="looseBase" class="part" x="110" y="168" width="106" height="30" rx="5" fill="#6ee7e7"/>
              <circle id="looseRoller1" class="part" cx="128" cy="250" r="17" fill="#f2c14e"/>
              <circle id="looseRoller2" class="part" cx="198" cy="250" r="17" fill="#f2c14e"/>
              <path id="looseBelt" class="part" d="M110 326 C136 300 204 300 230 326 C204 352 136 352 110 326" fill="none" stroke="#57d68d" stroke-width="10" stroke-linecap="round"/>
              <rect id="looseMotor" class="part" x="106" y="366" width="44" height="42" rx="7" fill="#b99cff"/>
              <rect id="looseSensor" class="part" x="196" y="370" width="42" height="28" rx="4" fill="#62b6ff"/>
            </g>

            <g id="visionCone">
              <path d="M450 68 L342 214 L558 214 Z" fill="#62b6ff" opacity="0.08" stroke="#62b6ff" stroke-opacity="0.25"/>
              <rect x="410" y="42" width="80" height="34" rx="7" fill="#24384a" stroke="#62b6ff"/>
              <text x="424" y="64" class="small-label">RGB-D</text>
            </g>

            <text id="phaseText" x="70" y="462" class="label">Waiting for replay</text>
            <text id="detailText" x="70" y="484" class="small-label"></text>
          </svg>
        </div>
        <div class="controls">
          <button id="playBtn">Play</button>
          <button id="resetBtn">Reset</button>
          <input id="scrubber" type="range" min="0" max="0" value="0" step="1" aria-label="Replay scrubber">
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
          <div class="event-list" id="eventList"></div>
        </div>
      </aside>
    </section>

    <section class="details">
      <div class="panel">
        <div class="panel-body">
          <h2>What This Proves</h2>
          <div class="callout">
            This is not a happy-path pick-and-place. The cell logs perception confidence,
            motion plans, bimanual fixture stabilization, failure detection, autonomous recovery,
            and a final functional acceptance test.
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
    let index = 0;
    let playing = false;
    let timer = null;

    const el = (id) => document.getElementById(id);
    const statusClass = (status) => `status-${status}`;

    function setText(id, value) {
      el(id).textContent = value;
    }

    function partVisible(id, visible) {
      const node = el(id);
      node.classList.toggle("ghost", !visible);
      node.style.opacity = visible ? "1" : "0.18";
    }

    function moveTool(arm, x, y) {
      const tool = el(arm === "left_arm" ? "leftTool" : "rightTool");
      tool.setAttribute("cx", x);
      tool.setAttribute("cy", y);
      const path = el(arm === "left_arm" ? "leftArm" : "rightArm");
      const base = arm === "left_arm" ? [190, 472] : [710, 472];
      const elbow = arm === "left_arm" ? [238, 376] : [662, 376];
      path.setAttribute("d", `M${base[0]} ${base[1]} L${elbow[0]} ${elbow[1]} L${x} ${y}`);
    }

    function resetScene() {
      ["conveyorBase", "rollerA", "rollerB", "beltPath", "motorPart", "sensorPart", "puck"].forEach((id) => partVisible(id, false));
      ["looseBase", "looseRoller1", "looseRoller2", "looseBelt", "looseMotor", "looseSensor"].forEach((id) => partVisible(id, true));
      moveTool("left_arm", 316, 316);
      moveTool("right_arm", 584, 316);
      el("fixture").setAttribute("stroke", "#4b6175");
      setText("phaseText", "Waiting for replay");
      setText("detailText", "");
    }

    function applyEvent(event) {
      setText("phaseText", `${event.phase} [${event.status}]`);
      setText("detailText", event.message);
      el("fixture").setAttribute("stroke", event.status === "fail" ? "#ff6b6b" : event.status === "recovered" ? "#62b6ff" : "#4b6175");

      const msg = event.message.toLowerCase();
      const phase = event.phase;
      const details = event.details || {};
      const arm = details.arm || details.active_arm || (msg.includes("left_arm") ? "left_arm" : msg.includes("right_arm") ? "right_arm" : null);

      if (phase === "perception" || phase === "active_vision") {
        el("visionCone").style.opacity = event.status === "fail" ? "0.35" : "1";
      }
      if (phase === "motion_planning" && details.plan) {
        moveTool(details.plan.arm, details.plan.arm === "left_arm" ? 356 : 544, 228);
      }
      if (phase === "bimanual_coordination") {
        moveTool(details.assist_arm, details.assist_arm === "left_arm" ? 344 : 556, 308);
      }
      if (phase === "execution" && arm) {
        moveTool(arm, arm === "left_arm" ? 386 : 514, 260);
      }
      if (msg.includes("installed base")) {
        partVisible("looseBase", false);
        partVisible("conveyorBase", true);
      }
      if (msg.includes("installed roller") && el("rollerA").classList.contains("ghost")) {
        partVisible("looseRoller1", false);
        partVisible("rollerA", true);
      } else if (msg.includes("installed roller")) {
        partVisible("looseRoller2", false);
        partVisible("rollerB", true);
      }
      if (msg.includes("belt placed") || msg.includes("belt slip")) {
        partVisible("looseBelt", false);
        partVisible("beltPath", true);
        el("beltPath").setAttribute("stroke", event.status === "fail" ? "#ff6b6b" : "#57d68d");
      }
      if (msg.includes("re-tensioning")) {
        el("beltPath").setAttribute("stroke", "#62b6ff");
      }
      if (msg.includes("installed motor")) {
        partVisible("looseMotor", false);
        partVisible("motorPart", true);
      }
      if (msg.includes("installed sensor")) {
        partVisible("looseSensor", false);
        partVisible("sensorPart", true);
      }
      if (phase === "functional_test" && event.status === "pass") {
        partVisible("puck", true);
        el("puck").style.transform = "translate(102px, 0)";
        el("fixture").setAttribute("stroke", "#57d68d");
      }
    }

    function renderAt(nextIndex) {
      index = Math.max(0, Math.min(nextIndex, events.length - 1));
      resetScene();
      for (let i = 0; i <= index; i += 1) {
        applyEvent(events[i]);
      }
      el("scrubber").value = String(index);
      setText("stepLabel", `${index + 1} / ${events.length}`);
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
      }, 420);
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
      el("eventList").innerHTML = events.map((event, i) => `
        <div class="event" data-event-index="${i}">
          <div class="event-top">
            <span>#${event.sequence} ${event.phase}</span>
            <span class="${statusClass(event.status)}">${event.status}</span>
          </div>
          <div class="event-msg">${event.message}</div>
        </div>
      `).join("");
      document.querySelectorAll(".event").forEach((node) => {
        node.addEventListener("click", () => renderAt(Number(node.dataset.eventIndex)));
      });
      const critical = events.filter((event) => event.status !== "pass" || ["active_vision", "bimanual_coordination", "functional_test"].includes(event.phase));
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
    el("scrubber").max = String(Math.max(0, events.length - 1));
    el("scrubber").addEventListener("input", (event) => renderAt(Number(event.target.value)));

    renderMetrics();
    renderEvents();
    renderAt(0);
  </script>
</body>
</html>
"""
    output_path.write_text(
        template.replace("__PAYLOAD__", serialized).replace("__RAW_PAYLOAD__", escaped),
        encoding="utf-8",
    )
