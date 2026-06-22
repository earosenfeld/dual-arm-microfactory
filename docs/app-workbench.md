# Scenario Workbench

The generated `index.html` is the main application surface for a public demo.

Generate it:

```bash
PYTHONPATH=src python3 -m microfactory demo
```

Open the generated `runs/<timestamp>-linkedin-demo/index.html`.

## What It Shows

- Scenario switching across nominal and recovery cases.
- Embedded animated replay dashboard for the selected scenario.
- Metrics cards for recovery events, active vision, bimanual assists, motion plans,
  minimum clearance, and simulated elapsed time.
- Scenario comparison table.
- Direct links to the acceptance report, event log, metrics JSON, and LinkedIn post draft.
- Recording mode that hides nonessential panels and enlarges the replay for screen capture.

## Why This Matters

The workbench makes the project look like an integrated robotics application, not a pile of
scripts. It is also honest: every visualization is driven by generated run artifacts rather
than hard-coded screenshots.
