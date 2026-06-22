# Hardware Plan

The first physical version should stay small, inexpensive, and credible.

## Minimum Viable Cell

- Two low-cost 6-DOF arms or one stronger arm plus one helper positioner.
- Parallel grippers with replaceable fingertips.
- RGB-D camera mounted overhead.
- Optional wrist camera on the primary arm.
- 3D-printed mini conveyor parts.
- 3D-printed fixture with datums and simple compliance.
- AprilTags or ArUco markers for calibration.
- Clamp sensor, belt seating sensor, and test-puck sensor.
- Small PLC or PLC simulator with Modbus TCP / OPC UA bridge.

## Conveyor Module

The conveyor module is intentionally visual:

- Base plate.
- Two rollers.
- Belt.
- Motor/coupler.
- Sensor.
- Clips or fasteners.

The final test should move a small puck through the sensor window. That gives the demo a
clear payoff instead of ending with a static assembled object.

## Failure Injection

- Belt slipped off roller.
- Fixture clamp fails to close.
- Wrong revision sensor in the tray.
- Low confidence pose estimate from occlusion.
- Missing fastener.
- Part moves after first pose estimate.
