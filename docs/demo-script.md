# Demo Script

## Opening Shot

Show the cell with two robot arms, loose parts in trays, a fixture in the center, and the live
dashboard on a monitor.

Narration:

> This is a dual-arm autonomous microfactory. It assembles a working mini conveyor from loose
> parts, verifies the build, recovers from failures, and generates an acceptance log.

## Sequence

1. Start `JOB-CONVEYOR-BELT-SLIP`.
2. Camera detects the base plate and rollers.
3. The robot shows grasp candidates and planned paths.
4. Arm A holds/alines the base while Arm B installs rollers.
5. Arm A stretches or places the belt.
6. Inject belt slip.
7. The system detects the belt is mis-seated.
8. Recovery backs out, re-tensions, and retries.
9. Motor and sensor are installed.
10. The fixture clamp closes.
11. The final functional test runs the conveyor.
12. Dashboard shows the pass result, recovery event, timing, and report.

## Money Shot

The best video moment is not the first successful assembly. It is the recovery:

> The belt slipped. The robot saw it, changed state, corrected the physical problem, and still
> shipped a passing acceptance report.

## Expert Talking Points

- 6D pose estimation and tracking are isolated behind the perception port.
- Motion planning is isolated behind the planner port and will be backed by MoveIt 2.
- Recovery is state-machine driven, not a prompt.
- The event log is the acceptance artifact and debugging trace.
- Learning models are optional subskills, supervised by deterministic safety logic.

## LinkedIn Caption Hook

> I am building a dual-arm autonomous microfactory demo. The goal is not another
> happy-path pick-and-place; it is a robotic cell that can detect failure, recover,
> run a functional test, and produce acceptance evidence.
