from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from microfactory.cell.models import StepStatus
from microfactory.control.assembly import AssemblyResult


@dataclass(frozen=True)
class RunMetrics:
    final_status: str
    event_count: int
    pass_events: int
    warn_events: int
    fail_events: int
    recovered_events: int
    active_vision_events: int
    bimanual_events: int
    motion_plan_count: int
    average_planning_time_ms: float
    minimum_clearance_mm: float
    cycle_time_s: float
    simulated_elapsed_s: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "final_status": self.final_status,
            "event_count": self.event_count,
            "pass_events": self.pass_events,
            "warn_events": self.warn_events,
            "fail_events": self.fail_events,
            "recovered_events": self.recovered_events,
            "active_vision_events": self.active_vision_events,
            "bimanual_events": self.bimanual_events,
            "motion_plan_count": self.motion_plan_count,
            "average_planning_time_ms": round(self.average_planning_time_ms, 1),
            "minimum_clearance_mm": round(self.minimum_clearance_mm, 1),
            "cycle_time_s": round(self.cycle_time_s, 1),
            "simulated_elapsed_s": round(self.simulated_elapsed_s, 1),
        }


def summarize_run(result: AssemblyResult) -> RunMetrics:
    events = result.log.events
    planning_times: list[int] = []
    clearances: list[float] = []

    for event in events:
        plan = event.details.get("plan")
        if isinstance(plan, dict):
            planning_time = plan.get("planning_time_ms")
            clearance = plan.get("min_clearance_mm")
            if isinstance(planning_time, (int, float)):
                planning_times.append(int(planning_time))
            if isinstance(clearance, (int, float)):
                clearances.append(float(clearance))

    return RunMetrics(
        final_status="PASS" if result.success else "FAIL",
        event_count=len(events),
        pass_events=result.log.count(StepStatus.PASS),
        warn_events=result.log.count(StepStatus.WARN),
        fail_events=result.log.count(StepStatus.FAIL),
        recovered_events=result.log.count(StepStatus.RECOVERED),
        active_vision_events=sum(1 for event in events if event.phase == "active_vision"),
        bimanual_events=sum(1 for event in events if event.phase == "bimanual_coordination"),
        motion_plan_count=len(planning_times),
        average_planning_time_ms=mean(planning_times) if planning_times else 0.0,
        minimum_clearance_mm=min(clearances) if clearances else 0.0,
        cycle_time_s=result.state.cycle_time_s,
        simulated_elapsed_s=events[-1].sim_time_s if events else 0.0,
    )
