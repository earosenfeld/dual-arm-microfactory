# Architecture

The project uses a deterministic industrial supervisor with replaceable adapters.

## Layers

- `cell`: domain model for parts, fixture, arms, detections, grasps, and motion plans.
- `perception`: part detection, pose confidence, verification, and active vision.
- `planning`: grasp scoring and collision-aware motion plan interfaces.
- `control`: assembly sequence, bimanual coordination, recovery, and final test.
- `reporting`: event log and acceptance artifacts.
- `dashboard`: static dashboard now, live dashboard later.

## Design Rule

Learning models can propose local actions, but they do not own safety-critical execution.
The supervisor owns state, allowed transitions, recovery, and final acceptance.

## Future Hardware Ports

- ROS 2 topics/actions for detections, planning requests, and trajectory execution.
- MoveIt 2 planning adapter.
- FoundationPose adapter for CAD-guided 6D pose.
- SAM 2 adapter for segmentation/tracking.
- PLC adapter for fixture clamp and functional test.
- Force/contact adapter for insertion and belt seating.
