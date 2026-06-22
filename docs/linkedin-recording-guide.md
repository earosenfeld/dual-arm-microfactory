# LinkedIn Recording Guide

## Generate The Demo

```bash
PYTHONPATH=src python3 -m microfactory demo
```

Open the generated `index.html` through a local HTTP server, then open the `belt_slip`
dashboard first.

## 60-Second Recording

1. Start on the demo package index.
2. Open `belt_slip/dashboard.html`.
3. Press `Play`.
4. Pause when the belt slip failure appears.
5. Use `Next Critical` to jump through the failure, recovery, and final functional test.
6. Show the metrics cards and live state chips.
7. Orbit the Three.js viewport, then switch from `Iso` to `Top` briefly to show the
   robotics-workbench feel.
8. Toggle the `Critical` filter in the timeline.
9. End on the final `PASS` status.

## Narration

> I am building a dual-arm autonomous microfactory demo. The point is not a happy-path
> pick-and-place; it is perception, planning, bimanual coordination, recovery, and
> acceptance evidence in one system.

## What To Emphasize

- The cell detects a physical failure and recovers.
- The supervisor owns state and safety-critical transitions.
- The dashboard replays the event log instead of hiding behind a black-box demo.
- The simulation ports are designed to be replaced by ROS 2, MoveIt 2, RGB-D perception,
  and a physical tabletop cell.

## Avoid Saying

- "The robot is fully autonomous" before hardware exists.
- "AI controls the robot."
- "Production ready."

Say "simulation-first architecture" and "next step is physical integration."
