from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import sqrt
from typing import Any


class PartKind(str, Enum):
    BASE = "base_plate"
    ROLLER = "roller"
    BELT = "belt"
    MOTOR = "motor"
    SENSOR = "sensor"
    FASTENER = "fastener"


class PartState(str, Enum):
    LOOSE = "loose"
    PICKED = "picked"
    INSTALLED = "installed"
    REJECTED = "rejected"


class ArmName(str, Enum):
    LEFT = "left_arm"
    RIGHT = "right_arm"


class StepStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    RECOVERED = "recovered"


@dataclass(frozen=True)
class Pose:
    x: float
    y: float
    z: float
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    def distance_to(self, other: "Pose") -> float:
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

    def shifted(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> "Pose":
        return Pose(
            x=self.x + dx,
            y=self.y + dy,
            z=self.z + dz,
            roll=self.roll,
            pitch=self.pitch,
            yaw=self.yaw,
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
        }


@dataclass
class Part:
    id: str
    kind: PartKind
    pose: Pose
    state: PartState = PartState.LOOSE
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "pose": self.pose.as_dict(),
            "state": self.state.value,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Detection:
    part_id: str
    kind: PartKind
    pose: Pose
    confidence: float
    occlusion: float
    view_id: str

    @property
    def is_confident(self) -> bool:
        return self.confidence >= 0.72 and self.occlusion <= 0.45

    def as_dict(self) -> dict[str, Any]:
        return {
            "part_id": self.part_id,
            "kind": self.kind.value,
            "pose": self.pose.as_dict(),
            "confidence": round(self.confidence, 3),
            "occlusion": round(self.occlusion, 3),
            "view_id": self.view_id,
        }


@dataclass(frozen=True)
class GraspCandidate:
    part_id: str
    arm: ArmName
    pose: Pose
    score: float
    clearance_mm: float
    reason: str

    @property
    def is_usable(self) -> bool:
        return self.score >= 0.62 and self.clearance_mm >= 8.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "part_id": self.part_id,
            "arm": self.arm.value,
            "pose": self.pose.as_dict(),
            "score": round(self.score, 3),
            "clearance_mm": round(self.clearance_mm, 2),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class MotionPlan:
    arm: ArmName
    target: Pose
    planning_time_ms: int
    path_length_mm: float
    min_clearance_mm: float
    status: StepStatus
    note: str

    @property
    def is_safe(self) -> bool:
        return self.status in {StepStatus.PASS, StepStatus.WARN} and self.min_clearance_mm >= 5.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm.value,
            "target": self.target.as_dict(),
            "planning_time_ms": self.planning_time_ms,
            "path_length_mm": round(self.path_length_mm, 2),
            "min_clearance_mm": round(self.min_clearance_mm, 2),
            "status": self.status.value,
            "note": self.note,
        }


@dataclass
class Fixture:
    id: str
    pose: Pose
    installed: dict[PartKind, list[str]] = field(default_factory=dict)
    belt_seated: bool = False
    clamp_closed: bool = False
    functional_test_passed: bool = False

    def install(self, part: Part) -> None:
        self.installed.setdefault(part.kind, []).append(part.id)
        part.state = PartState.INSTALLED

    def has(self, kind: PartKind, count: int = 1) -> bool:
        return len(self.installed.get(kind, [])) >= count

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "pose": self.pose.as_dict(),
            "installed": {kind.value: ids for kind, ids in self.installed.items()},
            "belt_seated": self.belt_seated,
            "clamp_closed": self.clamp_closed,
            "functional_test_passed": self.functional_test_passed,
        }


@dataclass
class CellState:
    job_id: str
    fixture: Fixture
    parts: dict[str, Part]
    active_failures: set[str] = field(default_factory=set)
    cycle_time_s: float = 0.0

    def loose_parts(self, kind: PartKind | None = None) -> list[Part]:
        parts = [part for part in self.parts.values() if part.state == PartState.LOOSE]
        if kind is not None:
            return [part for part in parts if part.kind == kind]
        return parts

    def as_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "fixture": self.fixture.as_dict(),
            "parts": {part_id: part.as_dict() for part_id, part in self.parts.items()},
            "active_failures": sorted(self.active_failures),
            "cycle_time_s": round(self.cycle_time_s, 2),
        }
