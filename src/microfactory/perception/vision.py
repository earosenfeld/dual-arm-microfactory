from __future__ import annotations

from dataclasses import dataclass
from random import Random

from microfactory.cell.models import CellState, Detection, Part, PartKind, Pose
from microfactory.reporting.events import EventLog
from microfactory.cell.models import StepStatus


@dataclass(frozen=True)
class ActiveViewpoint:
    id: str
    camera_pose: Pose
    expected_confidence_gain: float


class SimulatedVisionSystem:
    """Deterministic stand-in for RGB-D segmentation and 6D pose tracking."""

    def __init__(self, seed: int = 7) -> None:
        self.random = Random(seed)
        self.view_counter = 0

    def detect_best_part(
        self,
        state: CellState,
        kind: PartKind,
        log: EventLog,
        allow_active_view: bool = True,
    ) -> Detection:
        candidates = state.loose_parts(kind)
        if not candidates:
            raise RuntimeError(f"No loose part available for {kind.value}")

        part = candidates[0]
        detection = self._detect(part, state)
        log.add(
            "perception",
            f"Detected {kind.value} candidate {part.id}",
            StepStatus.PASS if detection.is_confident else StepStatus.WARN,
            detection=detection.as_dict(),
        )

        if detection.is_confident or not allow_active_view:
            return detection

        viewpoint = self.next_best_view(detection)
        log.add(
            "active_vision",
            "Pose confidence below threshold; planning next-best-view capture",
            StepStatus.WARN,
            viewpoint={
                "id": viewpoint.id,
                "camera_pose": viewpoint.camera_pose.as_dict(),
                "expected_confidence_gain": viewpoint.expected_confidence_gain,
            },
        )
        improved = Detection(
            part_id=detection.part_id,
            kind=detection.kind,
            pose=detection.pose.shifted(dx=-0.002, dy=0.001),
            confidence=min(0.98, detection.confidence + viewpoint.expected_confidence_gain),
            occlusion=max(0.05, detection.occlusion - 0.30),
            view_id=viewpoint.id,
        )
        log.add(
            "active_vision",
            f"Updated pose estimate for {part.id} after active view",
            StepStatus.PASS if improved.is_confident else StepStatus.FAIL,
            detection=improved.as_dict(),
        )
        return improved

    def verify_installed(self, state: CellState, kind: PartKind, log: EventLog) -> bool:
        installed = state.fixture.has(kind)
        log.add(
            "verification",
            f"Verified fixture contains {kind.value}",
            StepStatus.PASS if installed else StepStatus.FAIL,
            fixture=state.fixture.as_dict(),
        )
        return installed

    def verify_belt_seated(self, state: CellState, log: EventLog) -> bool:
        status = StepStatus.PASS if state.fixture.belt_seated else StepStatus.FAIL
        log.add(
            "verification",
            "Checked belt seating on both rollers",
            status,
            belt_seated=state.fixture.belt_seated,
        )
        return state.fixture.belt_seated

    def _detect(self, part: Part, state: CellState) -> Detection:
        self.view_counter += 1
        occlusion = 0.18 + self.random.random() * 0.18
        confidence = 0.82 + self.random.random() * 0.12

        if "low_confidence_vision" in state.active_failures and part.kind in {PartKind.BASE, PartKind.ROLLER}:
            confidence = 0.49
            occlusion = 0.68
            state.active_failures.discard("low_confidence_vision")

        return Detection(
            part_id=part.id,
            kind=part.kind,
            pose=part.pose.shifted(
                dx=(self.random.random() - 0.5) * 0.006,
                dy=(self.random.random() - 0.5) * 0.006,
            ),
            confidence=confidence,
            occlusion=occlusion,
            view_id=f"view-{self.view_counter:03d}",
        )

    def next_best_view(self, detection: Detection) -> ActiveViewpoint:
        self.view_counter += 1
        return ActiveViewpoint(
            id=f"view-{self.view_counter:03d}",
            camera_pose=detection.pose.shifted(dx=-0.08, dy=0.05, dz=0.18),
            expected_confidence_gain=0.34,
        )
