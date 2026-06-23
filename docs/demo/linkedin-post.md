I started building a dual-arm autonomous microfactory demo.

The goal is not another happy-path pick-and-place. The cell assembles a mini conveyor module from loose parts, injects real failure modes, recovers, runs a final functional test, and generates an acceptance log.

Current simulation-first version includes:
- active vision retry when pose confidence is low
- grasp scoring and collision-aware motion-plan events
- bimanual fixture stabilization during assembly
- autonomous recovery for belt slip, clamp failure, wrong-part detection, and low-confidence perception
- replayable run dashboard with event timeline and acceptance metrics

Demo package: 5 scenarios, 3 recovery scenarios, 3 recovery events, 20 bimanual coordination events.

Next step: connect the same supervisor to ROS 2, MoveIt 2, RGB-D perception, and a tabletop physical cell.

The architecture rule: learning models can propose local subskills, but the deterministic supervisor owns state, recovery, and final acceptance.
