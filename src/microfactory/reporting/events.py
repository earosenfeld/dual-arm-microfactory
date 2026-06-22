from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from microfactory.cell.models import StepStatus


@dataclass(frozen=True)
class CellEvent:
    timestamp: str
    phase: str
    message: str
    status: StepStatus
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "phase": self.phase,
            "message": self.message,
            "status": self.status.value,
            "details": self.details,
        }


class EventLog:
    def __init__(self) -> None:
        self.events: list[CellEvent] = []

    def add(
        self,
        phase: str,
        message: str,
        status: StepStatus = StepStatus.PASS,
        **details: Any,
    ) -> None:
        self.events.append(
            CellEvent(
                timestamp=datetime.now(UTC).isoformat(timespec="milliseconds"),
                phase=phase,
                message=message,
                status=status,
                details=details,
            )
        )

    def count(self, status: StepStatus) -> int:
        return sum(1 for event in self.events if event.status == status)

    def as_list(self) -> list[dict[str, Any]]:
        return [event.as_dict() for event in self.events]

    def has_failures(self) -> bool:
        return any(event.status == StepStatus.FAIL for event in self.events)
