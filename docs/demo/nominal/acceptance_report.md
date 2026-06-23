# Acceptance Report: JOB-CONVEYOR-NOMINAL

Final status: **PASS**

## Summary

- Pass events: 55
- Warning events: 0
- Recovery events: 0
- Failure events: 0
- Active vision events: 0
- Bimanual coordination events: 4
- Motion plans: 16
- Minimum clearance: 21.2 mm
- Average planning time: 234.0 ms
- Cycle time: 39.0s

## Fixture Result

- Base installed: True
- Rollers installed: True
- Belt seated: True
- Clamp closed: True
- Functional test passed: True

## Timeline

- `000.0s` **job** [pass] Started autonomous assembly for JOB-CONVEYOR-NOMINAL
- `000.8s` **perception** [pass] Detected base_plate candidate base-001
- `001.6s` **grasp_planning** [pass] Selected grasp for base-001
- `002.4s` **motion_planning** [pass] Planned left_arm move
- `003.2s` **execution** [pass] left_arm picked base-001
- `004.0s` **motion_planning** [pass] Planned left_arm move
- `004.8s` **execution** [pass] Installed base_plate base-001
- `005.6s` **verification** [pass] Verified fixture contains base_plate
- `006.4s` **perception** [pass] Detected roller candidate roller-001
- `007.2s` **grasp_planning** [pass] Selected grasp for roller-001
- `008.0s` **motion_planning** [pass] Planned right_arm move
- `008.8s` **motion_planning** [pass] Planned left_arm move
- `009.6s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs roller
- `010.4s` **execution** [pass] right_arm picked roller-001
- `011.2s` **motion_planning** [pass] Planned right_arm move
- `012.0s` **execution** [pass] Installed roller roller-001
- `012.8s` **verification** [pass] Verified fixture contains roller
- `013.6s` **perception** [pass] Detected roller candidate roller-002
- `014.4s` **grasp_planning** [pass] Selected grasp for roller-002
- `015.2s` **motion_planning** [pass] Planned right_arm move
- `016.0s` **motion_planning** [pass] Planned left_arm move
- `016.8s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs roller
- `017.6s` **execution** [pass] right_arm picked roller-002
- `018.4s` **motion_planning** [pass] Planned right_arm move
- `019.2s` **execution** [pass] Installed roller roller-002
- `020.0s` **verification** [pass] Verified fixture contains roller
- `020.8s` **perception** [pass] Detected belt candidate belt-001
- `021.6s` **grasp_planning** [pass] Selected grasp for belt-001
- `022.4s` **motion_planning** [pass] Planned left_arm move
- `023.2s` **motion_planning** [pass] Planned right_arm move
- `024.0s` **bimanual_coordination** [pass] right_arm stabilizes fixture while left_arm installs belt
- `024.8s` **execution** [pass] left_arm picked belt-001
- `025.6s` **motion_planning** [pass] Planned left_arm move
- `026.4s` **execution** [pass] Installed belt belt-001
- `027.2s` **verification** [pass] Verified fixture contains belt
- `028.0s` **perception** [pass] Detected motor candidate motor-001
- `028.8s` **grasp_planning** [pass] Selected grasp for motor-001
- `029.6s` **motion_planning** [pass] Planned right_arm move
- `030.4s` **motion_planning** [pass] Planned left_arm move
- `031.2s` **bimanual_coordination** [pass] left_arm stabilizes fixture while right_arm installs motor
- `032.0s` **execution** [pass] right_arm picked motor-001
- `032.8s` **motion_planning** [pass] Planned right_arm move
- `033.6s` **execution** [pass] Installed motor motor-001
- `034.4s` **verification** [pass] Verified fixture contains motor
- `035.2s` **perception** [pass] Detected sensor candidate sensor-001
- `036.0s` **grasp_planning** [pass] Selected grasp for sensor-001
- `036.8s` **motion_planning** [pass] Planned left_arm move
- `037.6s` **execution** [pass] left_arm picked sensor-001
- `038.4s` **motion_planning** [pass] Planned left_arm move
- `039.2s` **execution** [pass] Installed sensor sensor-001
- `040.0s` **verification** [pass] Verified fixture contains sensor
- `040.8s` **fixture** [pass] Fixture clamp closed
- `041.6s` **verification** [pass] Checked belt seating on both rollers
- `042.4s` **functional_test** [pass] Mini conveyor moved test puck through sensor window
- `043.2s` **job** [pass] Assembly cycle completed
