from __future__ import annotations

import json
from pathlib import Path

from microfactory.cell.models import StepStatus
from microfactory.control.assembly import AssemblyResult


def write_run_artifacts(result: AssemblyResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "events.json").write_text(
        json.dumps(result.log.as_list(), indent=2),
        encoding="utf-8",
    )
    (output_dir / "cell_state.json").write_text(
        json.dumps(result.state.as_dict(), indent=2),
        encoding="utf-8",
    )
    (output_dir / "acceptance_report.md").write_text(
        render_markdown_report(result),
        encoding="utf-8",
    )


def render_markdown_report(result: AssemblyResult) -> str:
    pass_count = result.log.count(StepStatus.PASS)
    warn_count = result.log.count(StepStatus.WARN)
    recovered_count = result.log.count(StepStatus.RECOVERED)
    fail_count = result.log.count(StepStatus.FAIL)
    status = "PASS" if result.success else "FAIL"
    lines = [
        f"# Acceptance Report: {result.state.job_id}",
        "",
        f"Final status: **{status}**",
        "",
        "## Summary",
        "",
        f"- Pass events: {pass_count}",
        f"- Warning events: {warn_count}",
        f"- Recovery events: {recovered_count}",
        f"- Failure events: {fail_count}",
        f"- Cycle time: {result.state.cycle_time_s:.1f}s",
        "",
        "## Fixture Result",
        "",
        f"- Base installed: {result.state.fixture.has(result.state.parts['base-001'].kind)}",
        f"- Rollers installed: {result.state.fixture.has(result.state.parts['roller-001'].kind, 2)}",
        f"- Belt seated: {result.state.fixture.belt_seated}",
        f"- Clamp closed: {result.state.fixture.clamp_closed}",
        f"- Functional test passed: {result.state.fixture.functional_test_passed}",
        "",
        "## Timeline",
        "",
    ]
    for event in result.log.events:
        lines.append(f"- `{event.timestamp}` **{event.phase}** [{event.status.value}] {event.message}")
    lines.append("")
    return "\n".join(lines)
