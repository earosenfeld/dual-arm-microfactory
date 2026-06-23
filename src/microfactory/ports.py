from __future__ import annotations

from typing import Protocol

from microfactory.cell.models import ArmName, CellState, Detection, GraspCandidate, MotionPlan, PartKind, Pose
from microfactory.reporting.events import EventLog


class VisionPort(Protocol):
    def detect_best_part(
        self,
        state: CellState,
        kind: PartKind,
        log: EventLog,
        allow_active_view: bool = True,
    ) -> Detection:
        """Return the best current pose estimate for the requested loose part kind."""

    def verify_installed(self, state: CellState, kind: PartKind, log: EventLog) -> bool:
        """Verify that a part kind is present in the fixture after placement."""

    def verify_belt_seated(self, state: CellState, log: EventLog) -> bool:
        """Verify the final belt seating state before functional test."""


class GraspPlannerPort(Protocol):
    def plan(self, detection: Detection, preferred_arm: ArmName, log: EventLog) -> GraspCandidate:
        """Select a feasible grasp for the detected part."""


class MotionPlannerPort(Protocol):
    def plan_to(self, arm: ArmName, start: Pose, target: Pose, log: EventLog) -> MotionPlan:
        """Plan a collision-aware motion from the current pose to a target pose."""


class RecoveryPort(Protocol):
    def recover_belt_slip(self, state: CellState, log: EventLog) -> bool:
        """Recover from a belt seating failure."""

    def recover_clamp_failure(self, state: CellState, log: EventLog) -> bool:
        """Recover from a fixture clamp timeout."""

    def handle_wrong_part(self, state: CellState, log: EventLog) -> bool:
        """Reject incorrect parts before assembly begins."""

    def recover_missing_kind(self, kind: PartKind, log: EventLog) -> None:
        """Record a terminal recovery request when no valid part remains."""
