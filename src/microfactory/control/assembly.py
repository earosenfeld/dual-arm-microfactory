from __future__ import annotations

from dataclasses import dataclass

from microfactory.cell.models import ArmName, CellState, PartKind, PartState, Pose, StepStatus
from microfactory.control.recovery import RecoveryPolicy
from microfactory.perception.vision import SimulatedVisionSystem
from microfactory.planning.grasp import GraspPlanner
from microfactory.planning.motion import MotionPlanner
from microfactory.ports import GraspPlannerPort, MotionPlannerPort, RecoveryPort, VisionPort
from microfactory.reporting.events import EventLog


@dataclass(frozen=True)
class AssemblyResult:
    success: bool
    state: CellState
    log: EventLog


class ConveyorAssemblyController:
    def __init__(
        self,
        vision: VisionPort | None = None,
        grasp_planner: GraspPlannerPort | None = None,
        motion_planner: MotionPlannerPort | None = None,
        recovery: RecoveryPort | None = None,
    ) -> None:
        self.vision = vision or SimulatedVisionSystem()
        self.grasp_planner = grasp_planner or GraspPlanner()
        self.motion_planner = motion_planner or MotionPlanner()
        self.recovery = recovery or RecoveryPolicy()
        self.arm_home = {
            ArmName.LEFT: Pose(-0.36, 0.08, 0.34),
            ArmName.RIGHT: Pose(0.36, 0.08, 0.34),
        }

    def run(self, state: CellState) -> AssemblyResult:
        log = EventLog()
        log.add("job", f"Started autonomous assembly for {state.job_id}", StepStatus.PASS)

        if "wrong_part" in state.active_failures:
            self.recovery.handle_wrong_part(state, log)

        sequence = [
            (PartKind.BASE, ArmName.LEFT),
            (PartKind.ROLLER, ArmName.RIGHT),
            (PartKind.ROLLER, ArmName.RIGHT),
            (PartKind.BELT, ArmName.LEFT),
            (PartKind.MOTOR, ArmName.RIGHT),
            (PartKind.SENSOR, ArmName.LEFT),
        ]

        for kind, arm in sequence:
            if not self._install_next(state, kind, arm, log):
                self.recovery.recover_missing_kind(kind, log)
                return AssemblyResult(False, state, log)

        self._close_clamp(state, log)
        self._verify_belt(state, log)
        self._functional_test(state, log)

        success = state.fixture.functional_test_passed
        final_status = StepStatus.PASS if success else StepStatus.FAIL
        log.add(
            "job",
            "Assembly cycle completed" if success else "Assembly cycle completed with failures",
            final_status,
            cell=state.as_dict(),
        )
        return AssemblyResult(success, state, log)

    def _install_next(
        self,
        state: CellState,
        kind: PartKind,
        arm: ArmName,
        log: EventLog,
    ) -> bool:
        if not state.loose_parts(kind):
            return False

        detection = self.vision.detect_best_part(state, kind, log)
        if not detection.is_confident:
            return False

        grasp = self.grasp_planner.plan(detection, arm, log)
        if not grasp.is_usable:
            return False

        plan = self.motion_planner.plan_to(arm, self.arm_home[arm], grasp.pose, log)
        if not plan.is_safe:
            return False

        self._coordinate_assist_arm(kind, arm, state, log)

        part = state.parts[detection.part_id]
        part.state = PartState.PICKED
        log.add("execution", f"{arm.value} picked {part.id}", StepStatus.PASS, part=part.as_dict())

        insertion_pose = state.fixture.pose.shifted(dz=0.12)
        place_plan = self.motion_planner.plan_to(arm, grasp.pose, insertion_pose, log)
        if not place_plan.is_safe:
            return False

        if kind == PartKind.BELT and "belt_slip" in state.active_failures:
            state.fixture.install(part)
            state.fixture.belt_seated = False
            log.add(
                "execution",
                "Belt placed but visual verification detected slip",
                StepStatus.FAIL,
                part=part.as_dict(),
            )
            return self.recovery.recover_belt_slip(state, log)

        state.fixture.install(part)
        if kind == PartKind.BELT:
            state.fixture.belt_seated = True
        log.add("execution", f"Installed {part.kind.value} {part.id}", StepStatus.PASS, part=part.as_dict())
        self.vision.verify_installed(state, kind, log)
        state.cycle_time_s += 6.5
        return True

    def _coordinate_assist_arm(
        self,
        kind: PartKind,
        active_arm: ArmName,
        state: CellState,
        log: EventLog,
    ) -> None:
        if kind not in {PartKind.ROLLER, PartKind.BELT, PartKind.MOTOR}:
            return

        assist_arm = ArmName.RIGHT if active_arm == ArmName.LEFT else ArmName.LEFT
        target = state.fixture.pose.shifted(dy=-0.08, dz=0.18)
        plan = self.motion_planner.plan_to(assist_arm, self.arm_home[assist_arm], target, log)
        if plan.is_safe:
            log.add(
                "bimanual_coordination",
                f"{assist_arm.value} stabilizes fixture while {active_arm.value} installs {kind.value}",
                StepStatus.PASS,
                assist_arm=assist_arm.value,
                active_arm=active_arm.value,
                part_kind=kind.value,
            )
        else:
            log.add(
                "bimanual_coordination",
                "Assist arm could not reach stabilization pose; continuing with fixture-only support",
                StepStatus.WARN,
                assist_arm=assist_arm.value,
                active_arm=active_arm.value,
                part_kind=kind.value,
            )

    def _close_clamp(self, state: CellState, log: EventLog) -> None:
        if "clamp_fail" in state.active_failures:
            state.fixture.clamp_closed = False
            log.add(
                "fixture",
                "Clamp command did not reach closed sensor before timeout",
                StepStatus.FAIL,
                fixture=state.fixture.as_dict(),
            )
            self.recovery.recover_clamp_failure(state, log)
            return

        state.fixture.clamp_closed = True
        log.add("fixture", "Fixture clamp closed", StepStatus.PASS, fixture=state.fixture.as_dict())

    def _verify_belt(self, state: CellState, log: EventLog) -> None:
        if not self.vision.verify_belt_seated(state, log):
            self.recovery.recover_belt_slip(state, log)
            self.vision.verify_belt_seated(state, log)

    def _functional_test(self, state: CellState, log: EventLog) -> None:
        required = (
            state.fixture.has(PartKind.BASE)
            and state.fixture.has(PartKind.ROLLER, count=2)
            and state.fixture.has(PartKind.BELT)
            and state.fixture.has(PartKind.MOTOR)
            and state.fixture.clamp_closed
            and state.fixture.belt_seated
        )
        state.fixture.functional_test_passed = required
        log.add(
            "functional_test",
            "Mini conveyor moved test puck through sensor window"
            if required
            else "Functional test blocked by incomplete assembly",
            StepStatus.PASS if required else StepStatus.FAIL,
            fixture=state.fixture.as_dict(),
        )
