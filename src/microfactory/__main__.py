from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from microfactory.cell.scenarios import SUPPORTED_SCENARIOS, build_conveyor_cell
from microfactory.control.assembly import ConveyorAssemblyController
from microfactory.dashboard.static import write_static_dashboard
from microfactory.demo.package import build_demo_package
from microfactory.reporting.report import write_run_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(prog="microfactory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the conveyor assembly simulation")
    run_parser.add_argument(
        "--scenario",
        choices=sorted(SUPPORTED_SCENARIOS),
        default="nominal",
        help="Failure scenario to inject into the simulated cell",
    )
    run_parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for run artifacts. Defaults to runs/<timestamp>-<scenario>",
    )

    demo_parser = subparsers.add_parser("demo", help="Generate a LinkedIn-ready demo package")
    demo_parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for demo artifacts. Defaults to runs/<timestamp>-linkedin-demo",
    )

    args = parser.parse_args()
    if args.command == "run":
        run_scenario(args.scenario, args.output_dir)
    elif args.command == "demo":
        run_demo(args.output_dir)


def run_scenario(scenario: str, output_dir: str | None) -> None:
    state = build_conveyor_cell(scenario)
    controller = ConveyorAssemblyController()
    result = controller.run(state)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(output_dir) if output_dir else Path("runs") / f"{timestamp}-{scenario}"
    write_run_artifacts(result, out_dir)
    write_static_dashboard(result, out_dir / "dashboard.html")
    status = "PASS" if result.success else "FAIL"
    print(f"{status}: wrote run artifacts to {out_dir}")
    print(f"Open dashboard: {out_dir / 'dashboard.html'}")


def run_demo(output_dir: str | None) -> None:
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(output_dir) if output_dir else Path("runs") / f"{timestamp}-linkedin-demo"
    runs = build_demo_package(out_dir)
    pass_count = sum(1 for run in runs if run.result.success)
    print(f"Generated demo package with {pass_count}/{len(runs)} passing scenarios: {out_dir}")
    print(f"Open index: {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
