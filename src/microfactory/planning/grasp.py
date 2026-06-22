from __future__ import annotations

from microfactory.cell.models import ArmName, Detection, GraspCandidate, PartKind, Pose, StepStatus
from microfactory.reporting.events import EventLog


class GraspPlanner:
    def plan(self, detection: Detection, preferred_arm: ArmName, log: EventLog) -> GraspCandidate:
        base_score = detection.confidence
        clearance = 22.0
        reason = "top-side pinch grasp"

        if detection.kind == PartKind.BELT:
            base_score -= 0.08
            clearance = 15.0
            reason = "edge pinch with belt stretch allowance"
        elif detection.kind == PartKind.MOTOR:
            base_score -= 0.03
            clearance = 18.0
            reason = "side grasp avoiding shaft"
        elif detection.kind == PartKind.FASTENER:
            base_score -= 0.12
            clearance = 10.0
            reason = "small part precision grasp"

        candidate = GraspCandidate(
            part_id=detection.part_id,
            arm=preferred_arm,
            pose=Pose(
                detection.pose.x,
                detection.pose.y,
                detection.pose.z + 0.09,
                detection.pose.roll,
                detection.pose.pitch,
                detection.pose.yaw,
            ),
            score=max(0.0, min(1.0, base_score)),
            clearance_mm=clearance,
            reason=reason,
        )
        log.add(
            "grasp_planning",
            f"Selected grasp for {detection.part_id}",
            StepStatus.PASS if candidate.is_usable else StepStatus.FAIL,
            grasp=candidate.as_dict(),
        )
        return candidate
