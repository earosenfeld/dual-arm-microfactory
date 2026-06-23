# Acceptance Report: JOB-CONVEYOR-LOW_CONFIDENCE_VISION

Final status: **PASS**

## Summary

- Pass events: 55
- Warning events: 2
- Recovery events: 0
- Failure events: 0
- Active vision events: 2
- Bimanual coordination events: 4
- Motion plans: 16
- Minimum clearance: 21.2 mm
- Average planning time: 233.9 ms
- Cycle time: 39.0s

## Fixture Result

- Base installed: True
- Rollers installed: True
- Belt seated: True
- Clamp closed: True
- Functional test passed: True

## Timeline

- `000.0s` **job** [pass] Started autonomous assembly for JOB-CONVEYOR-LOW_CONFIDENCE_VISION
- `000.8s` **perception** [warn] Detected base_plate candidate base-001
- `001.6s` **active_vision** [warn] Pose confidence below threshold; planning next-best-view capture
- `002.4s` **active_vision** [pass] Updated pose estimate for base-001 after active view
- `003.2s` **grasp_planning** [pass] Selected grasp for base-001
- `004.0s` **motion_planning** [pass] Planned left_arm move
- `004.8s` **execution** [pass] left_arm picked base-001
- `005.6s` **motion_planning** [pass] Planned left_arm move
- `006.4s` **execution** [pass] Installed base_plate base-001
- `007.2s` **verification** [pass] Verified fixture contains base_plate
- `008.0s` **perception** [pass] Detected roller candidate roller-001
- `008.8s` **grasp_planning** [pass] Selected grasp for roller-001
- `009.6s` **motion_planning** [pass] Planned right_arm move
- `010.4s` **motion_planning** [pass] Planned left_arm move
- `011.2s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs roller
- `012.0s` **execution** [pass] right_arm picked roller-001
- `012.8s` **motion_planning** [pass] Planned right_arm move
- `013.6s` **execution** [pass] Installed roller roller-001
- `014.4s` **verification** [pass] Verified fixture contains roller
- `015.2s` **perception** [pass] Detected roller candidate roller-002
- `016.0s` **grasp_planning** [pass] Selected grasp for roller-002
- `016.8s` **motion_planning** [pass] Planned right_arm move
- `017.6s` **motion_planning** [pass] Planned left_arm move
- `018.4s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs roller
- `019.2s` **execution** [pass] right_arm picked roller-002
- `020.0s` **motion_planning** [pass] Planned right_arm move
- `020.8s` **execution** [pass] Installed roller roller-002
- `021.6s` **verification** [pass] Verified fixture contains roller
- `022.4s` **perception** [pass] Detected belt candidate belt-001
- `023.2s` **grasp_planning** [pass] Selected grasp for belt-001
- `024.0s` **motion_planning** [pass] Planned left_arm move
- `024.8s` **motion_planning** [pass] Planned right_arm move
- `025.6s` **bimanual_coordination** [pass] right_arm stabilizes fixture while left_arm installs belt
- `026.4s` **execution** [pass] left_arm picked belt-001
- `027.2s` **motion_planning** [pass] Planned left_arm move
- `028.0s` **execution** [pass] Installed belt belt-001
- `028.8s` **verification** [pass] Verified fixture contains belt
- `029.6s` **perception** [pass] Detected motor candidate motor-001
- `030.4s` **grasp_planning** [pass] Selected grasp for motor-001
- `031.2s` **motion_planning** [pass] Planned right_arm move
- `032.0s` **motion_planning** [pass] Planned left_arm move
- `032.8s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs motor
- `033.6s` **execution** [pass] right_arm picked motor-001
- `034.4s` **motion_planning** [pass] Planned right_arm move
- `035.2s` **execution** [pass] Installed motor motor-001
- `036.0s` **verification** [pass] Verified fixture contains motor
- `036.8s` **perception** [pass] Detected sensor candidate sensor-001
- `037.6s` **grasp_planning** [pass] Selected grasp for sensor-001
- `038.4s` **motion_planning** [pass] Planned left_arm move
- `039.2s` **execution** [pass] left_arm picked sensor-001
- `040.0s` **motion_planning** [pass] Planned left_arm move
- `040.8s` **execution** [pass] Installed sensor sensor-001
- `041.6s` **verification** [pass] Verified fixture contains sensor
- `042.4s` **fixture** [pass] Fixture clamp closed
- `043.2s` **verification** [pass] Checked belt seating on both rollers
- `044.0s` **functional_test** [pass] Mini conveyor moved test puck through sensor window
- `044.8s` **job** [pass] Assembly cycle completed
