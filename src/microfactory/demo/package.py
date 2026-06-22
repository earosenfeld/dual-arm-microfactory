from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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
    (output_dir / "index.html").write_text(render_index(runs), encoding="utf-8")
    return runs


def render_demo_readme(runs: list[DemoRun]) -> str:
    lines = [
        "# Dual-Arm Microfactory Demo Package",
        "",
        "Open `index.html` first. Each scenario includes a replay dashboard, raw event log,",
        "cell state, and acceptance report.",
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
    cards = []
    for run in runs:
        metrics = summarize_run(run.result)
        cards.append(
            f"""
      <a class="card" href="{run.scenario}/dashboard.html">
        <div class="eyebrow">{run.scenario.replace("_", " ")}</div>
        <h2>{metrics.final_status}</h2>
        <p>{metrics.recovered_events} recoveries, {metrics.active_vision_events} active-vision events, {metrics.bimanual_events} bimanual assists</p>
      </a>
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
      --panel: #151d27;
      --line: #2a3948;
      --text: #eef4fa;
      --muted: #9dadbd;
      --blue: #62b6ff;
      --green: #57d68d;
    }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px 24px;
    }}
    h1 {{
      max-width: 860px;
      font-size: clamp(34px, 5vw, 64px);
      line-height: 1;
      margin: 0 0 14px;
      letter-spacing: 0;
    }}
    .subhead {{
      color: var(--muted);
      max-width: 760px;
      line-height: 1.5;
      margin-bottom: 28px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
    }}
    .card {{
      color: inherit;
      text-decoration: none;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      min-height: 156px;
      transition: border-color 160ms ease, transform 160ms ease;
    }}
    .card:hover {{
      border-color: var(--blue);
      transform: translateY(-2px);
    }}
    .eyebrow {{
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 12px;
    }}
    h2 {{
      color: var(--green);
      margin: 18px 0 8px;
      font-size: 34px;
    }}
    p {{ color: var(--muted); line-height: 1.45; }}
  </style>
</head>
<body>
  <main>
    <h1>Dual-Arm Autonomous Microfactory Demo Package</h1>
    <p class="subhead">Replayable simulation runs for a two-arm robotic cell that assembles a mini conveyor, injects failures, recovers, and produces acceptance evidence.</p>
    <section class="grid">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
"""
