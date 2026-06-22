from __future__ import annotations

from microfactory.cell.models import CellState, PartKind, PartState, StepStatus
from microfactory.reporting.events import EventLog


class RecoveryPolicy:
    def recover_belt_slip(self, state: CellState, log: EventLog) -> bool:
        log.add(
            "recovery",
            "Belt slip detected; backing out, re-tensioning, and retrying seating",
            StepStatus.RECOVERED,
            recovery="belt_reseat",
        )
        state.fixture.belt_seated = True
        state.active_failures.discard("belt_slip")
        return True

    def recover_clamp_failure(self, state: CellState, log: EventLog) -> bool:
        log.add(
            "recovery",
            "Fixture clamp failed; cycling clamp and rechecking part presence",
            StepStatus.RECOVERED,
            recovery="clamp_cycle",
        )
        state.fixture.clamp_closed = True
        state.active_failures.discard("clamp_fail")
        return True

    def handle_wrong_part(self, state: CellState, log: EventLog) -> bool:
        bad_parts = [
            part
            for part in state.parts.values()
            if part.metadata.get("expected_part_number")
            and part.metadata.get("part_number") != part.metadata.get("expected_part_number")
        ]
        if not bad_parts:
            return False

        for part in bad_parts:
            part.state = PartState.REJECTED
            log.add(
                "recovery",
                f"Rejected {part.id}; part number does not match job requirement",
                StepStatus.RECOVERED,
                part=part.as_dict(),
            )
        state.active_failures.discard("wrong_part")
        return True

    def recover_missing_kind(self, kind: PartKind, log: EventLog) -> None:
        log.add(
            "recovery",
            f"No valid {kind.value} remains; requesting operator replenishment",
            StepStatus.FAIL,
            required_part=kind.value,
        )
