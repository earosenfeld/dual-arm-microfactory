# Architecture

The project uses a deterministic industrial supervisor with replaceable adapters.

## Layers

- `cell`: domain model for parts, fixture, arms, detections, grasps, and motion plans.
- `ports`: protocol interfaces for vision, grasp planning, motion planning, and recovery.
- `perception`: part detection, pose confidence, verification, and active vision.
- `planning`: grasp scoring and collision-aware motion plan interfaces.
- `control`: assembly sequence, bimanual coordination, recovery, and final test.
- `reporting`: event log and acceptance artifacts.
- `dashboard`: static dashboard now, live dashboard later.

## Design Rule

Learning models can propose local actions, but they do not own safety-critical execution.
The supervisor owns state, allowed transitions, recovery, and final acceptance.

## Current Simulation Boundary

The checked-in implementation uses simulation adapters behind the ports. The supervisor,
event log, metrics, reports, and dashboard are the reusable core. Hardware work should
replace the port implementations without moving safety-critical state ownership out of
`control`.

## Future Hardware Ports

- ROS 2 topics/actions for detections, planning requests, and trajectory execution.
- MoveIt 2 planning adapter.
- FoundationPose adapter for CAD-guided 6D pose.
- SAM 2 adapter for segmentation/tracking.
- PLC adapter for fixture clamp and functional test.
- Force/contact adapter for insertion and belt seating.
