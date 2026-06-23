# Acceptance Report: JOB-CONVEYOR-WRONG_PART

Final status: **PASS**

## Summary

- Pass events: 55
- Warning events: 0
- Recovery events: 1
- Failure events: 0
- Active vision events: 0
- Bimanual coordination events: 4
- Motion plans: 16
- Minimum clearance: 20.1 mm
- Average planning time: 237.5 ms
- Cycle time: 39.0s

## Fixture Result

- Base installed: True
- Rollers installed: True
- Belt seated: True
- Clamp closed: True
- Functional test passed: True

## Timeline

- `000.0s` **job** [pass] Started autonomous assembly for JOB-CONVEYOR-WRONG_PART
- `000.8s` **recovery** [recovered] Rejected sensor-001; part number does not match job requirement
- `001.6s` **perception** [pass] Detected base_plate candidate base-001
- `002.4s` **grasp_planning** [pass] Selected grasp for base-001
- `003.2s` **motion_planning** [pass] Planned left_arm move
- `004.0s` **execution** [pass] left_arm picked base-001
- `004.8s` **motion_planning** [pass] Planned left_arm move
- `005.6s` **execution** [pass] Installed base_plate base-001
- `006.4s` **verification** [pass] Verified fixture contains base_plate
- `007.2s` **perception** [pass] Detected roller candidate roller-001
- `008.0s` **grasp_planning** [pass] Selected grasp for roller-001
- `008.8s` **motion_planning** [pass] Planned right_arm move
- `009.6s` **motion_planning** [pass] Planned left_arm move
- `010.4s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs roller
- `011.2s` **execution** [pass] right_arm picked roller-001
- `012.0s` **motion_planning** [pass] Planned right_arm move
- `012.8s` **execution** [pass] Installed roller roller-001
- `013.6s` **verification** [pass] Verified fixture contains roller
- `014.4s` **perception** [pass] Detected roller candidate roller-002
- `015.2s` **grasp_planning** [pass] Selected grasp for roller-002
- `016.0s` **motion_planning** [pass] Planned right_arm move
- `016.8s` **motion_planning** [pass] Planned left_arm move
- `017.6s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs roller
- `018.4s` **execution** [pass] right_arm picked roller-002
- `019.2s` **motion_planning** [pass] Planned right_arm move
- `020.0s` **execution** [pass] Installed roller roller-002
- `020.8s` **verification** [pass] Verified fixture contains roller
- `021.6s` **perception** [pass] Detected belt candidate belt-001
- `022.4s` **grasp_planning** [pass] Selected grasp for belt-001
- `023.2s` **motion_planning** [pass] Planned left_arm move
- `024.0s` **motion_planning** [pass] Planned right_arm move
- `024.8s` **bimanual_coordination** [pass] right_arm stabilizes fixture while left_arm installs belt
- `025.6s` **execution** [pass] left_arm picked belt-001
- `026.4s` **motion_planning** [pass] Planned left_arm move
- `027.2s` **execution** [pass] Installed belt belt-001
- `028.0s` **verification** [pass] Verified fixture contains belt
- `028.8s` **perception** [pass] Detected motor candidate motor-001
- `029.6s` **grasp_planning** [pass] Selected grasp for motor-001
- `030.4s` **motion_planning** [pass] Planned right_arm move
- `031.2s` **motion_planning** [pass] Planned left_arm move
- `032.0s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs motor
- `032.8s` **execution** [pass] right_arm picked motor-001
- `033.6s` **motion_planning** [pass] Planned right_arm move
- `034.4s` **execution** [pass] Installed motor motor-001
- `035.2s` **verification** [pass] Verified fixture contains motor
- `036.0s` **perception** [pass] Detected sensor candidate sensor-002
- `036.8s` **grasp_planning** [pass] Selected grasp for sensor-002
- `037.6s` **motion_planning** [pass] Planned left_arm move
- `038.4s` **execution** [pass] left_arm picked sensor-002
- `039.2s` **motion_planning** [pass] Planned left_arm move
- `040.0s` **execution** [pass] Installed sensor sensor-002
- `040.8s` **verification** [pass] Verified fixture contains sensor
- `041.6s` **fixture** [pass] Fixture clamp closed
- `042.4s` **verification** [pass] Checked belt seating on both rollers
- `043.2s` **functional_test** [pass] Mini conveyor moved test puck through sensor window
- `044.0s` **job** [pass] Assembly cycle completed
