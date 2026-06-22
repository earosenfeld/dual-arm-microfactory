from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from microfactory.cell.models import StepStatus


@dataclass(frozen=True)
class CellEvent:
    sequence: int
    timestamp: str
    sim_time_s: float
    phase: str
    message: str
    status: StepStatus
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "sim_time_s": round(self.sim_time_s, 2),
            "phase": self.phase,
            "message": self.message,
            "status": self.status.value,
            "details": self.details,
        }


class EventLog:
    def __init__(self) -> None:
        self.events: list[CellEvent] = []
        self._sim_time_s = 0.0

    def add(
        self,
        phase: str,
        message: str,
        status: StepStatus = StepStatus.PASS,
        duration_s: float = 0.8,
        **details: Any,
    ) -> None:
        sequence = len(self.events) + 1
        self.events.append(
            CellEvent(
                sequence=sequence,
                timestamp=datetime.now(UTC).isoformat(timespec="milliseconds"),
                sim_time_s=self._sim_time_s,
                phase=phase,
                message=message,
                status=status,
                details=details,
            )
        )
        self._sim_time_s += duration_s

    def count(self, status: StepStatus) -> int:
        return sum(1 for event in self.events if event.status == status)

    def as_list(self) -> list[dict[str, Any]]:
        return [event.as_dict() for event in self.events]

    def has_failures(self) -> bool:
        return any(event.status == StepStatus.FAIL for event in self.events)
