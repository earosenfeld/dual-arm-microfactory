# Technical Roadmap

## Phase 0: Simulation Spine

- Deterministic conveyor assembly scenario.
- Simulated perception confidence and active viewpoint retry.
- Grasp and motion planning interfaces.
- Recovery-aware assembly controller.
- Acceptance report and static dashboard.

## Phase 1: Visualization

- Real-time browser dashboard.
- Planning-scene visualization.
- Pose, grasp, and event overlays.
- Run replay from event logs.

## Phase 2: ROS 2 Integration

- ROS 2 messages for detections, grasps, plans, and cell events.
- MoveIt 2 planner adapter.
- Joint trajectory execution adapter.
- RViz scene export.

## Phase 3: Perception

- RGB-D camera adapter.
- AprilTag calibration workflow.
- SAM 2 segmentation adapter.
- FoundationPose or CAD-based 6D pose adapter.
- Confidence-driven next-best-view routine.

## Phase 4: Physical Cell

- Two affordable arms or one arm plus a helper positioner.
- 3D-printed conveyor module and fixture.
- Part-presence sensors.
- Clamp and motor control through a small PLC or PLC simulator.
- Final functional test with sensor feedback.

## Phase 5: Learned Subskills

- Collect demonstrations for belt seating or peg insertion.
- Train a small Diffusion Policy / ACT / LeRobot-compatible subskill.
- Keep learned subskill inside a deterministic supervisor.
- Compare learned local policy against scripted recovery.
