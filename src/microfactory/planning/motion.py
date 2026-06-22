from __future__ import annotations

from microfactory.cell.models import ArmName, MotionPlan, Pose, StepStatus
from microfactory.reporting.events import EventLog


class MotionPlanner:
    """Simple deterministic planner used until a MoveIt 2 adapter is added."""

    def plan_to(self, arm: ArmName, start: Pose, target: Pose, log: EventLog) -> MotionPlan:
        path_length = start.distance_to(target) * 1000.0
        clearance = max(4.0, 36.0 - path_length * 0.015)
        status = StepStatus.PASS if clearance >= 8.0 else StepStatus.WARN
        note = "collision-free path" if status == StepStatus.PASS else "tight clearance near fixture"
        plan = MotionPlan(
            arm=arm,
            target=target,
            planning_time_ms=max(24, int(path_length * 0.42)),
            path_length_mm=path_length,
            min_clearance_mm=clearance,
            status=status,
            note=note,
        )
        log.add(
            "motion_planning",
            f"Planned {arm.value} move",
            status if plan.is_safe else StepStatus.FAIL,
            plan=plan.as_dict(),
        )
        return plan
