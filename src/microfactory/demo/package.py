from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from microfactory.cell.scenarios import build_conveyor_cell
from microfactory.control.assembly import ConveyorAssemblyController, AssemblyResult
from microfactory.dashboard.static import write_static_dashboard
from microfactory.reporting.metrics import summarize_run
from microfactory.reporting.report import write_run_artifacts


DEMO_SCENARIOS = ("belt_slip", "low_confidence_vision", "clamp_fail", "wrong_part", "nominal")


@dataclass(frozen=True)
class DemoRun:
    scenario: str
    output_dir: Path
    result: AssemblyResult


def build_demo_package(output_dir: Path) -> list[DemoRun]:
    output_dir.mkdir(parents=True, exist_ok=True)
    runs: list[DemoRun] = []

    for scenario in DEMO_SCENARIOS:
        state = build_conveyor_cell(scenario)
        result = ConveyorAssemblyController().run(state)
        scenario_dir = output_dir / scenario
        write_run_artifacts(result, scenario_dir)
        write_static_dashboard(result, scenario_dir / "dashboard.html")
        runs.append(DemoRun(scenario=scenario, output_dir=scenario_dir, result=result))

    (output_dir / "README.md").write_text(render_demo_readme(runs), encoding="utf-8")
    (output_dir / "linkedin-post.md").write_text(render_linkedin_post(runs), encoding="utf-8")
    (output_dir / "manifest.json").write_text(
        json.dumps(render_manifest(runs), indent=2),
        encoding="utf-8",
    )
    (output_dir / "index.html").write_text(render_index(runs), encoding="utf-8")
    return runs


def render_manifest(runs: list[DemoRun]) -> dict[str, Any]:
    return {
        "project": "Dual-Arm Autonomous Microfactory",
        "description": (
            "Replayable simulation package for dual-arm robotic assembly, failure recovery, "
            "functional test, and acceptance evidence."
        ),
        "scenarios": [
            {
                "name": run.scenario,
                "title": scenario_title(run.scenario),
                "description": scenario_description(run.scenario),
                "dashboard": f"{run.scenario}/dashboard.html",
                "acceptance_report": f"{run.scenario}/acceptance_report.md",
                "events": f"{run.scenario}/events.json",
                "metrics": summarize_run(run.result).as_dict(),
            }
            for run in runs
        ],
    }


def scenario_title(scenario: str) -> str:
    return {
        "belt_slip": "Belt Slip Recovery",
        "low_confidence_vision": "Active Vision Re-Observe",
        "clamp_fail": "Clamp Timeout Recovery",
        "wrong_part": "Wrong Revision Rejection",
        "nominal": "Nominal Assembly",
    }.get(scenario, scenario.replace("_", " ").title())


def scenario_description(scenario: str) -> str:
    return {
        "belt_slip": "The belt is intentionally mis-seated, detected visually, re-tensioned, and accepted after final functional test.",
        "low_confidence_vision": "The first pose estimate is uncertain, so the cell plans a next-best-view capture before picking.",
        "clamp_fail": "The fixture clamp misses its closed sensor, then the supervisor cycles the clamp and verifies recovery.",
        "wrong_part": "A wrong-revision sensor is rejected and the correct spare part is installed instead.",
        "nominal": "Clean happy-path assembly used as a baseline for timing, planning, and event counts.",
    }.get(scenario, "Replayable assembly scenario.")


def render_demo_readme(runs: list[DemoRun]) -> str:
    lines = [
        "# Dual-Arm Microfactory Demo Package",
        "",
        "Open `index.html` first. It is an interactive scenario workbench with embedded",
        "dashboards, comparison metrics, raw event logs, cell state, and acceptance reports.",
        "",
        "## Runs",
        "",
        "| Scenario | Status | Recoveries | Active Vision | Bimanual Events | Dashboard |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for run in runs:
        metrics = summarize_run(run.result)
        lines.append(
            "| "
            f"{run.scenario} | "
            f"{metrics.final_status} | "
            f"{metrics.recovered_events} | "
            f"{metrics.active_vision_events} | "
            f"{metrics.bimanual_events} | "
            f"[dashboard]({run.scenario}/dashboard.html) |"
        )
    lines.append("")
    return "\n".join(lines)


def render_linkedin_post(runs: list[DemoRun]) -> str:
    recovery_runs = sum(1 for run in runs if summarize_run(run.result).recovered_events > 0)
    total_recoveries = sum(summarize_run(run.result).recovered_events for run in runs)
    total_bimanual = sum(summarize_run(run.result).bimanual_events for run in runs)
    lines = [
        "I started building a dual-arm autonomous microfactory demo.",
        "",
        "The goal is not another happy-path pick-and-place. The cell assembles a mini conveyor module from loose parts, injects real failure modes, recovers, runs a final functional test, and generates an acceptance log.",
        "",
        "Current simulation-first version includes:",
        "- active vision retry when pose confidence is low",
        "- grasp scoring and collision-aware motion-plan events",
        "- bimanual fixture stabilization during assembly",
        "- autonomous recovery for belt slip, clamp failure, wrong-part detection, and low-confidence perception",
        "- replayable run dashboard with event timeline and acceptance metrics",
        "",
        f"Demo package: {len(runs)} scenarios, {recovery_runs} recovery scenarios, {total_recoveries} recovery events, {total_bimanual} bimanual coordination events.",
        "",
        "Next step: connect the same supervisor to ROS 2, MoveIt 2, RGB-D perception, and a tabletop physical cell.",
        "",
        "The architecture rule: learning models can propose local subskills, but the deterministic supervisor owns state, recovery, and final acceptance.",
    ]
    return "\n".join(lines) + "\n"


def render_index(runs: list[DemoRun]) -> str:
    manifest = render_manifest(runs)
    serialized = json.dumps(manifest, indent=2)
    first = manifest["scenarios"][0]
    rows = []
    for scenario in manifest["scenarios"]:
        metrics = scenario["metrics"]
        rows.append(
            f"""
          <tr>
            <td>{scenario["title"]}</td>
            <td class="pass">{metrics["final_status"]}</td>
            <td>{metrics["recovered_events"]}</td>
            <td>{metrics["active_vision_events"]}</td>
            <td>{metrics["bimanual_events"]}</td>
            <td>{metrics["motion_plan_count"]}</td>
            <td>{metrics["minimum_clearance_mm"]} mm</td>
          </tr>
"""
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dual-Arm Microfactory Demo Package</title>
  <style>
    :root {{
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
      --violet: #b99cff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    main {{
      width: min(1560px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 30px 0 42px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 24px;
      align-items: end;
      margin-bottom: 18px;
    }}
    h1 {{
      font-size: clamp(34px, 5vw, 64px);
      line-height: 1;
      margin: 0 0 14px;
      letter-spacing: 0;
    }}
    .subhead {{
      color: var(--muted);
      max-width: 880px;
      line-height: 1.5;
    }}
    .repo-pill {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 999px;
      padding: 10px 14px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}
    .workbench {{
      display: grid;
      grid-template-columns: minmax(760px, 1.6fr) minmax(360px, 0.8fr);
      gap: 16px;
      align-items: start;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .panel-body {{ padding: 16px; }}
    .scenario-bar {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      padding: 12px;
      border-bottom: 1px solid var(--line);
      background: var(--band);
    }}
    button {{
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: inherit;
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      font-weight: 700;
    }}
    button.active {{ border-color: var(--blue); color: var(--blue); background: #17293a; }}
    iframe {{
      width: 100%;
      height: 760px;
      border: 0;
      display: block;
      background: #0d1117;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .metric {{
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 82px;
    }}
    .metric-label {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }}
    .metric-value {{
      font-size: 24px;
      font-weight: 800;
      line-height: 1;
    }}
    .eyebrow {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 12px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 20px;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 15px;
      color: var(--muted);
    }}
    p {{ color: var(--muted); line-height: 1.45; }}
    .scenario-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 10px;
    }}
    .pass {{ color: var(--green); }}
    .link-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-top: 12px;
    }}
    a.tool-link {{
      color: var(--text);
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: var(--panel-2);
    }}
    a.tool-link:hover {{ border-color: var(--blue); }}
    .architecture {{
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }}
    .arch-step {{
      display: grid;
      grid-template-columns: 90px 1fr;
      gap: 10px;
      align-items: start;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-2);
    }}
    .arch-step strong {{ color: var(--blue); font-size: 13px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    .comparison {{
      margin-top: 16px;
    }}
    .recording-mode iframe {{ height: 880px; }}
    .recording-mode .comparison,
    .recording-mode .side-lower {{ display: none; }}
    .recording-mode .workbench {{ grid-template-columns: 1fr; }}
    @media (max-width: 1180px) {{
      .workbench {{ grid-template-columns: 1fr; }}
      iframe {{ height: 680px; }}
    }}
    @media (max-width: 720px) {{
      main {{ width: min(100vw - 24px, 1560px); }}
      header {{ grid-template-columns: 1fr; }}
      .metric-grid, .link-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <div class="eyebrow">Scenario Workbench</div>
        <h1>Dual-Arm Autonomous Microfactory</h1>
        <p class="subhead">A replayable simulation app for two-arm assembly: active vision, grasp planning, collision-aware motion, bimanual stabilization, recovery, functional test, and acceptance evidence.</p>
      </div>
      <div class="repo-pill">simulation-first robotics demo</div>
    </header>

    <section class="workbench">
      <div class="panel">
        <div class="scenario-bar" id="scenarioButtons"></div>
        <iframe id="replayFrame" src="{first["dashboard"]}" title="Scenario replay dashboard"></iframe>
      </div>

      <aside class="panel">
        <div class="panel-body">
          <div class="scenario-title">
            <div>
              <div class="eyebrow" id="scenarioName">{first["name"]}</div>
              <h2 id="scenarioTitle">{first["title"]}</h2>
            </div>
            <button id="recordingModeButton">Recording Mode</button>
          </div>
          <p id="scenarioDescription">{first["description"]}</p>
          <div class="metric-grid" id="metricGrid"></div>
          <div class="link-grid">
            <a class="tool-link" id="dashboardLink" href="{first["dashboard"]}">Open dashboard</a>
            <a class="tool-link" id="reportLink" href="{first["acceptance_report"]}">Acceptance report</a>
            <a class="tool-link" id="eventsLink" href="{first["events"]}">Event log JSON</a>
            <a class="tool-link" href="linkedin-post.md">LinkedIn post draft</a>
          </div>
        </div>
        <div class="panel-body side-lower" style="border-top: 1px solid var(--line);">
          <h2>System Spine</h2>
          <div class="architecture">
            <div class="arch-step"><strong>Perception</strong><span>RGB-D pose confidence, active re-observe, installation verification.</span></div>
            <div class="arch-step"><strong>Planning</strong><span>Grasp scoring, clearance checks, bimanual assist poses.</span></div>
            <div class="arch-step"><strong>Supervisor</strong><span>Deterministic state machine owns sequence, recovery, and acceptance.</span></div>
            <div class="arch-step"><strong>Evidence</strong><span>Every run exports metrics, events, reports, and replay dashboard.</span></div>
          </div>
        </div>
      </aside>
    </section>

    <section class="panel comparison">
      <div class="panel-body">
        <h2>Scenario Comparison</h2>
        <table>
          <thead>
            <tr>
              <th>Scenario</th>
              <th>Status</th>
              <th>Recoveries</th>
              <th>Active Vision</th>
              <th>Bimanual</th>
              <th>Motion Plans</th>
              <th>Min Clearance</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>
  </main>
  <script>
    const manifest = {serialized};
    let current = manifest.scenarios[0];

    const el = (id) => document.getElementById(id);

    function renderScenarioButtons() {{
      el("scenarioButtons").innerHTML = manifest.scenarios.map((scenario, index) => `
        <button data-scenario-index="${{index}}">${{scenario.title}}</button>
      `).join("");
      document.querySelectorAll("[data-scenario-index]").forEach((button) => {{
        button.addEventListener("click", () => selectScenario(Number(button.dataset.scenarioIndex)));
      }});
    }}

    function metric(label, value) {{
      return `<div class="metric"><div class="metric-label">${{label}}</div><div class="metric-value">${{value}}</div></div>`;
    }}

    function selectScenario(index) {{
      current = manifest.scenarios[index];
      el("scenarioName").textContent = current.name;
      el("scenarioTitle").textContent = current.title;
      el("scenarioDescription").textContent = current.description;
      el("replayFrame").src = current.dashboard;
      el("dashboardLink").href = current.dashboard;
      el("reportLink").href = current.acceptance_report;
      el("eventsLink").href = current.events;

      const m = current.metrics;
      el("metricGrid").innerHTML = [
        metric("Final status", m.final_status),
        metric("Recoveries", m.recovered_events),
        metric("Active vision", m.active_vision_events),
        metric("Bimanual assists", m.bimanual_events),
        metric("Motion plans", m.motion_plan_count),
        metric("Min clearance", `${{m.minimum_clearance_mm}} mm`),
        metric("Avg plan time", `${{m.average_planning_time_ms}} ms`),
        metric("Elapsed", `${{m.simulated_elapsed_s}}s`),
      ].join("");

      document.querySelectorAll("[data-scenario-index]").forEach((button) => {{
        button.classList.toggle("active", Number(button.dataset.scenarioIndex) === index);
      }});
    }}

    el("recordingModeButton").addEventListener("click", () => {{
      document.body.classList.toggle("recording-mode");
      el("recordingModeButton").textContent = document.body.classList.contains("recording-mode")
        ? "Exit Recording"
        : "Recording Mode";
    }});

    renderScenarioButtons();
    selectScenario(0);
  </script>
</body>
</html>
"""
