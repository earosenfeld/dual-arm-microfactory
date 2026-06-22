from __future__ import annotations

from microfactory.cell.models import CellState, Fixture, Part, PartKind, Pose


SUPPORTED_SCENARIOS = {
    "nominal",
    "belt_slip",
    "clamp_fail",
    "low_confidence_vision",
    "wrong_part",
}


def build_conveyor_cell(scenario: str = "nominal") -> CellState:
    if scenario not in SUPPORTED_SCENARIOS:
        supported = ", ".join(sorted(SUPPORTED_SCENARIOS))
        raise ValueError(f"Unknown scenario '{scenario}'. Supported scenarios: {supported}")

    parts = {
        "base-001": Part("base-001", PartKind.BASE, Pose(0.18, 0.42, 0.03, yaw=0.04)),
        "roller-001": Part("roller-001", PartKind.ROLLER, Pose(0.32, 0.37, 0.04, yaw=1.48)),
        "roller-002": Part("roller-002", PartKind.ROLLER, Pose(0.28, 0.49, 0.04, yaw=1.61)),
        "belt-001": Part("belt-001", PartKind.BELT, Pose(0.43, 0.45, 0.02, yaw=0.12)),
        "motor-001": Part("motor-001", PartKind.MOTOR, Pose(0.51, 0.36, 0.05, yaw=-0.2)),
        "sensor-001": Part("sensor-001", PartKind.SENSOR, Pose(0.49, 0.53, 0.03, yaw=0.03)),
        "fastener-001": Part("fastener-001", PartKind.FASTENER, Pose(0.60, 0.39, 0.01)),
        "fastener-002": Part("fastener-002", PartKind.FASTENER, Pose(0.62, 0.43, 0.01)),
    }

    if scenario == "wrong_part":
        parts["sensor-001"].metadata["part_number"] = "SENSOR-REV-B"
        parts["sensor-001"].metadata["expected_part_number"] = "SENSOR-REV-C"

    fixture = Fixture(id="fixture-conveyor-a", pose=Pose(0.0, 0.0, 0.0))
    failures = set()
    if scenario != "nominal":
        failures.add(scenario)

    return CellState(
        job_id=f"JOB-CONVEYOR-{scenario.upper()}",
        fixture=fixture,
        parts=parts,
        active_failures=failures,
    )
