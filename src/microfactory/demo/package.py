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
    metrics_list = [scenario["metrics"] for scenario in manifest["scenarios"]]
    pass_count = sum(1 for metrics in metrics_list if metrics["final_status"] == "PASS")
    total_recoveries = sum(metrics["recovered_events"] for metrics in metrics_list)
    total_bimanual = sum(metrics["bimanual_events"] for metrics in metrics_list)
    total_motion_plans = sum(metrics["motion_plan_count"] for metrics in metrics_list)
    minimum_clearance = min(metrics["minimum_clearance_mm"] for metrics in metrics_list)
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
  <link rel="icon" href="data:,">
  <title>Dual-Arm Microfactory Demo Package</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #090a0c;
      --band: #111317;
      --panel: #15181d;
      --panel-2: #1c2128;
      --panel-3: #242a33;
      --line: #303844;
      --line-strong: #4b5563;
      --text: #f5f7fa;
      --muted: #a7b0be;
      --blue: #38a3ff;
      --green: #43e07f;
      --yellow: #ffd166;
      --red: #ff5f7a;
      --cyan: #2ee6d6;
      --violet: #ad8cff;
      --orange: #ff9f1c;
      --steel: #cad3de;
      --shadow: 0 18px 50px rgba(0,0,0,0.28);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      font-variant-numeric: tabular-nums;
    }}
    main {{
      width: min(1780px, calc(100vw - 20px));
      margin: 0 auto;
      padding: 10px 0 34px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(360px, 1fr) auto auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 8px;
      min-height: 64px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #15181d, #101216);
      box-shadow: var(--shadow);
    }}
    .icon-sprite {{ display: none; }}
    .icon {{
      width: 16px;
      height: 16px;
      flex: 0 0 auto;
      stroke: currentColor;
      fill: none;
      stroke-width: 1.9;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .brand-lockup {{
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr);
      gap: 11px;
      align-items: center;
      min-width: 0;
    }}
    .brand-mark {{
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(46,230,214,0.48);
      border-radius: 8px;
      background: linear-gradient(135deg, rgba(46,230,214,0.22), rgba(255,159,28,0.10)), #101317;
      color: var(--cyan);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04), 0 0 24px rgba(46,230,214,0.18);
    }}
    .brand-mark .icon {{ width: 27px; height: 27px; stroke-width: 1.65; }}
    h1 {{
      font-size: 22px;
      line-height: 1.1;
      margin: 0 0 3px;
      letter-spacing: 0;
      font-weight: 900;
    }}
    .subhead {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.25;
    }}
    .menu-strip {{
      display: flex;
      gap: 4px;
      justify-content: center;
      flex-wrap: wrap;
      min-width: 0;
    }}
    .menu-item,
    .repo-pill {{
      height: 32px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: linear-gradient(180deg, var(--panel-3), var(--panel-2));
      color: var(--steel);
      padding: 0 10px;
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}
    .menu-item.active {{
      border-color: rgba(46,230,214,0.55);
      color: #ffffff;
      background: linear-gradient(180deg, #26333a, #172026);
    }}
    .menu-item .icon {{ color: var(--cyan); width: 15px; height: 15px; }}
    .menu-item:nth-child(2) .icon {{ color: var(--orange); }}
    .menu-item:nth-child(3) .icon {{ color: var(--blue); }}
    .repo-pill {{
      color: var(--green);
      border-color: rgba(67,224,127,0.48);
      background: rgba(67,224,127,0.08);
      min-width: 120px;
      justify-content: center;
    }}
    .overview {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 8px;
    }}
    .status-card {{
      min-height: 56px;
      padding: 10px 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #15191f, #101318);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
    }}
    .status-label {{
      display: flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }}
    .status-label .icon {{ width: 14px; height: 14px; color: var(--orange); }}
    .status-value {{
      font-size: 15px;
      font-weight: 900;
      overflow-wrap: anywhere;
    }}
    .workbench {{
      display: grid;
      grid-template-columns: minmax(760px, 1fr) 360px;
      gap: 8px;
      align-items: start;
    }}
    .panel {{
      background: linear-gradient(180deg, #161a20, #12151a);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }}
    .panel-body {{ padding: 12px; }}
    .panel-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 44px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #1c2128, #14181e);
    }}
    .panel-title {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 850;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #eef3f8;
    }}
    .panel-title .icon {{ width: 15px; height: 15px; color: var(--cyan); }}
    .scenario-bar {{
      display: grid;
      grid-template-columns: repeat(5, minmax(150px, 1fr));
      gap: 8px;
      padding: 12px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #181c22, #111418);
    }}
    button {{
      border: 1px solid var(--line);
      background: linear-gradient(180deg, var(--panel-3), var(--panel-2));
      color: inherit;
      border-radius: 8px;
      padding: 9px 10px;
      cursor: pointer;
      font-weight: 800;
      min-height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}
    button:hover {{ border-color: var(--cyan); color: #fff; }}
    button.active {{
      border-color: var(--cyan);
      color: var(--cyan);
      background: linear-gradient(180deg, #203039, #162025);
    }}
    .scenario-button {{
      min-height: 86px;
      display: grid;
      grid-template-columns: 28px minmax(0, 1fr);
      gap: 8px;
      align-items: start;
      justify-content: stretch;
      text-align: left;
      padding: 10px;
    }}
    .scenario-icon {{
      width: 28px;
      height: 28px;
      display: grid;
      place-items: center;
      border-radius: 7px;
      background: rgba(46,230,214,0.10);
      color: var(--cyan);
      border: 1px solid rgba(46,230,214,0.30);
    }}
    .scenario-icon .icon {{ width: 16px; height: 16px; }}
    .scenario-meta {{
      display: grid;
      gap: 5px;
      min-width: 0;
    }}
    .scenario-name {{
      color: #fff;
      font-size: 13px;
      line-height: 1.15;
      overflow-wrap: anywhere;
    }}
    .scenario-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 750;
    }}
    .scenario-stats span {{
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 999px;
      padding: 2px 6px;
      background: rgba(255,255,255,0.035);
    }}
    iframe {{
      width: 100%;
      height: 790px;
      border: 0;
      display: block;
      background: #07080a;
    }}
    .frame-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 42px;
      padding: 9px 12px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #171b21, #111418);
    }}
    .frame-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .frame-kicker .icon {{ color: var(--orange); }}
    .frame-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .metric {{
      position: relative;
      background: linear-gradient(180deg, #20262e, #181d24);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 82px;
      overflow: hidden;
    }}
    .metric::before {{
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 3px;
      background: var(--cyan);
    }}
    .metric-label {{
      display: flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }}
    .metric-label .icon {{ width: 14px; height: 14px; color: var(--cyan); }}
    .metric-value {{
      font-size: 24px;
      font-weight: 900;
      line-height: 1;
    }}
    .eyebrow {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 12px;
    }}
    h2 {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 12px;
      font-size: 20px;
    }}
    h2 .icon {{ color: var(--cyan); }}
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
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--text);
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: linear-gradient(180deg, #20262e, #171c23);
      font-size: 13px;
      font-weight: 800;
    }}
    a.tool-link .icon {{ color: var(--orange); width: 15px; height: 15px; }}
    a.tool-link:hover {{ border-color: var(--cyan); }}
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
      background: linear-gradient(180deg, #20262e, #171c23);
    }}
    .arch-step strong {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--cyan);
      font-size: 13px;
    }}
    .arch-step strong .icon {{ width: 14px; height: 14px; }}
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
      margin-top: 8px;
    }}
    .recording-mode iframe {{ height: 880px; }}
    .recording-mode .comparison,
    .recording-mode .side-lower {{ display: none; }}
    .recording-mode .workbench {{ grid-template-columns: 1fr; }}
    @media (max-width: 1180px) {{
      .workbench {{ grid-template-columns: 1fr; }}
      .overview {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      iframe {{ height: 680px; }}
      header {{ grid-template-columns: 1fr; }}
      .menu-strip {{ justify-content: flex-start; }}
    }}
    @media (max-width: 720px) {{
      main {{ width: min(100vw - 20px, 1560px); }}
      header {{ grid-template-columns: 1fr; }}
      .brand-lockup {{ grid-template-columns: 1fr; }}
      .overview {{ grid-template-columns: 1fr; }}
      .scenario-bar {{ grid-template-columns: 1fr; }}
      .metric-grid, .link-grid {{ grid-template-columns: 1fr; }}
      iframe {{ height: 620px; }}
    }}
  </style>
</head>
<body>
  <svg class="icon-sprite" aria-hidden="true" focusable="false">
    <symbol id="icon-logo" viewBox="0 0 24 24"><path d="M5 7.5 12 3l7 4.5v9L12 21l-7-4.5z"></path><path d="M12 3v8.8m7-4.3-7 4.3-7-4.3"></path><path d="M8.2 14.2h7.6M9.5 16.5h5"></path></symbol>
    <symbol id="icon-cube" viewBox="0 0 24 24"><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"></path><path d="M12 12 4 7.5m8 4.5 8-4.5M12 12v9"></path></symbol>
    <symbol id="icon-route" viewBox="0 0 24 24"><path d="M5 18c5 0 4-12 9-12h5"></path><circle cx="5" cy="18" r="2"></circle><circle cx="19" cy="6" r="2"></circle></symbol>
    <symbol id="icon-camera" viewBox="0 0 24 24"><path d="M4 8h4l1.4-2h5.2L16 8h4v10H4z"></path><circle cx="12" cy="13" r="3.2"></circle></symbol>
    <symbol id="icon-clipboard" viewBox="0 0 24 24"><path d="M9 5h6l1 2h3v14H5V7h3z"></path><path d="M9 12h6M9 16h4"></path></symbol>
    <symbol id="icon-target" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"></circle><circle cx="12" cy="12" r="3"></circle><path d="M12 2v4M12 18v4M2 12h4M18 12h4"></path></symbol>
    <symbol id="icon-gauge" viewBox="0 0 24 24"><path d="M4 15a8 8 0 0 1 16 0"></path><path d="m12 15 4-5"></path><path d="M7 19h10"></path></symbol>
    <symbol id="icon-eye" viewBox="0 0 24 24"><path d="M3 12s3.5-6 9-6 9 6 9 6-3.5 6-9 6-9-6-9-6z"></path><circle cx="12" cy="12" r="2.5"></circle></symbol>
    <symbol id="icon-robot" viewBox="0 0 24 24"><path d="M7 10h10v8H7z"></path><path d="M9 10V7h6v3M12 7V4"></path><circle cx="10" cy="14" r="1"></circle><circle cx="14" cy="14" r="1"></circle><path d="M5 13H3m18 0h-2M9 18v2m6-2v2"></path></symbol>
    <symbol id="icon-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"></path></symbol>
    <symbol id="icon-record" viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="3"></rect><circle cx="12" cy="12" r="3"></circle></symbol>
    <symbol id="icon-open" viewBox="0 0 24 24"><path d="M14 4h6v6"></path><path d="m10 14 10-10"></path><path d="M20 14v5H5V4h5"></path></symbol>
  </svg>
  <main>
    <header>
      <div class="brand-lockup">
        <div class="brand-mark"><svg class="icon"><use href="#icon-logo"></use></svg></div>
        <div>
          <div class="eyebrow">Scenario Workbench</div>
          <h1>Dual-Arm Autonomous Microfactory</h1>
          <p class="subhead">Replayable two-arm assembly: perception, planning, recovery, functional test, and acceptance evidence.</p>
        </div>
      </div>
      <nav class="menu-strip" aria-label="Workbench toolbar">
        <span class="menu-item active"><svg class="icon"><use href="#icon-cube"></use></svg>Replay</span>
        <span class="menu-item"><svg class="icon"><use href="#icon-route"></use></svg>Scenarios</span>
        <span class="menu-item"><svg class="icon"><use href="#icon-clipboard"></use></svg>Evidence</span>
      </nav>
      <div class="repo-pill"><svg class="icon"><use href="#icon-check"></use></svg>{pass_count}/{len(manifest["scenarios"])} PASS</div>
    </header>

    <section class="overview" aria-label="Demo package overview">
      <div class="status-card">
        <div class="status-label"><svg class="icon"><use href="#icon-cube"></use></svg>Scenarios</div>
        <div class="status-value">{len(manifest["scenarios"])} replays</div>
      </div>
      <div class="status-card">
        <div class="status-label"><svg class="icon"><use href="#icon-check"></use></svg>Recoveries</div>
        <div class="status-value">{total_recoveries}</div>
      </div>
      <div class="status-card">
        <div class="status-label"><svg class="icon"><use href="#icon-robot"></use></svg>Bimanual</div>
        <div class="status-value">{total_bimanual} assists</div>
      </div>
      <div class="status-card">
        <div class="status-label"><svg class="icon"><use href="#icon-route"></use></svg>Motion Plans</div>
        <div class="status-value">{total_motion_plans}</div>
      </div>
      <div class="status-card">
        <div class="status-label"><svg class="icon"><use href="#icon-target"></use></svg>Min Clearance</div>
        <div class="status-value">{minimum_clearance} mm</div>
      </div>
    </section>

    <section class="workbench">
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-route"></use></svg>Mission Replays</div>
          <div class="frame-actions">
            <a class="tool-link" id="dashboardTopLink" href="{first["dashboard"]}"><svg class="icon"><use href="#icon-open"></use></svg>Open Dashboard</a>
          </div>
        </div>
        <div class="scenario-bar" id="scenarioButtons"></div>
        <div class="frame-top">
          <div class="frame-kicker"><svg class="icon"><use href="#icon-cube"></use></svg><span id="frameTitle">{first["title"]}</span></div>
          <div class="frame-kicker"><svg class="icon"><use href="#icon-gauge"></use></svg><span id="frameStatus">{first["metrics"]["final_status"]}</span></div>
        </div>
        <iframe id="replayFrame" src="{first["dashboard"]}?embed=1" title="Scenario replay dashboard"></iframe>
      </div>

      <aside class="panel">
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-gauge"></use></svg>Mission Control</div>
        </div>
        <div class="panel-body">
          <div class="scenario-title">
            <div>
              <div class="eyebrow" id="scenarioName">{first["name"]}</div>
              <h2 id="scenarioTitle">{first["title"]}</h2>
            </div>
            <button id="recordingModeButton"><svg class="icon"><use href="#icon-record"></use></svg>Recording</button>
          </div>
          <p id="scenarioDescription">{first["description"]}</p>
          <div class="metric-grid" id="metricGrid"></div>
          <div class="link-grid">
            <a class="tool-link" id="dashboardLink" href="{first["dashboard"]}"><svg class="icon"><use href="#icon-open"></use></svg>Open dashboard</a>
            <a class="tool-link" id="reportLink" href="{first["acceptance_report"]}"><svg class="icon"><use href="#icon-clipboard"></use></svg>Acceptance report</a>
            <a class="tool-link" id="eventsLink" href="{first["events"]}"><svg class="icon"><use href="#icon-gauge"></use></svg>Event log JSON</a>
            <a class="tool-link" href="linkedin-post.md"><svg class="icon"><use href="#icon-open"></use></svg>LinkedIn draft</a>
          </div>
        </div>
        <div class="panel-body side-lower" style="border-top: 1px solid var(--line);">
          <h2><svg class="icon"><use href="#icon-robot"></use></svg>System Spine</h2>
          <div class="architecture">
            <div class="arch-step"><strong><svg class="icon"><use href="#icon-camera"></use></svg>Perception</strong><span>RGB-D pose confidence, active re-observe, installation verification.</span></div>
            <div class="arch-step"><strong><svg class="icon"><use href="#icon-route"></use></svg>Planning</strong><span>Grasp scoring, clearance checks, bimanual assist poses.</span></div>
            <div class="arch-step"><strong><svg class="icon"><use href="#icon-robot"></use></svg>Supervisor</strong><span>Deterministic state machine owns sequence, recovery, and acceptance.</span></div>
            <div class="arch-step"><strong><svg class="icon"><use href="#icon-clipboard"></use></svg>Evidence</strong><span>Every run exports metrics, events, reports, and replay dashboard.</span></div>
          </div>
        </div>
      </aside>
    </section>

    <section class="panel comparison">
      <div class="panel-header">
        <div class="panel-title"><svg class="icon"><use href="#icon-target"></use></svg>Scenario Comparison</div>
      </div>
      <div class="panel-body">
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
    const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#icon-${{name}}"></use></svg>`;

    function renderScenarioButtons() {{
      el("scenarioButtons").innerHTML = manifest.scenarios.map((scenario, index) => `
        <button class="scenario-button" data-scenario-index="${{index}}">
          <span class="scenario-icon">${{icon(index === 0 ? "target" : index === 4 ? "check" : "route")}}</span>
          <span class="scenario-meta">
            <span class="scenario-name">${{scenario.title}}</span>
            <span class="scenario-stats">
              <span>${{scenario.metrics.final_status}}</span>
              <span>${{scenario.metrics.recovered_events}} rec</span>
              <span>${{scenario.metrics.minimum_clearance_mm}} mm</span>
            </span>
          </span>
        </button>
      `).join("");
      document.querySelectorAll("[data-scenario-index]").forEach((button) => {{
        button.addEventListener("click", () => selectScenario(Number(button.dataset.scenarioIndex)));
      }});
    }}

    function metric(label, value) {{
      const iconName = {{
        "Final status": "check",
        "Recoveries": "target",
        "Active vision": "camera",
        "Bimanual assists": "robot",
        "Motion plans": "route",
        "Min clearance": "target",
        "Avg plan time": "gauge",
        "Elapsed": "gauge",
      }}[label] || "gauge";
      return `<div class="metric"><div class="metric-label">${{icon(iconName)}}${{label}}</div><div class="metric-value">${{value}}</div></div>`;
    }}

    function selectScenario(index) {{
      current = manifest.scenarios[index];
      el("scenarioName").textContent = current.name;
      el("scenarioTitle").textContent = current.title;
      el("scenarioDescription").textContent = current.description;
      el("replayFrame").src = `${{current.dashboard}}?embed=1`;
      el("dashboardLink").href = current.dashboard;
      el("dashboardTopLink").href = current.dashboard;
      el("reportLink").href = current.acceptance_report;
      el("eventsLink").href = current.events;
      el("frameTitle").textContent = current.title;
      el("frameStatus").textContent = current.metrics.final_status;

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
      el("recordingModeButton").innerHTML = document.body.classList.contains("recording-mode")
        ? `${{icon("record")}}Exit Recording`
        : `${{icon("record")}}Recording`;
    }});

    renderScenarioButtons();
    selectScenario(0);
  </script>
</body>
</html>
"""
