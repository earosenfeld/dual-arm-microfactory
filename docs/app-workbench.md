# Scenario Workbench

The generated `index.html` is the main application surface for a public demo.

Generate it:

```bash
PYTHONPATH=src python3 -m microfactory demo
```

Open the generated `runs/<timestamp>-linkedin-demo/index.html` through a local HTTP
server so the browser can load the vendored Three.js module.

## What It Shows

- Scenario switching across nominal and recovery cases.
- Embedded animated replay dashboard for the selected scenario.
- Metrics cards for recovery events, active vision, bimanual assists, motion plans,
  minimum clearance, and simulated elapsed time.
- Scenario comparison table.
- Direct links to the acceptance report, event log, metrics JSON, and LinkedIn post draft.
- Video Mode that hides nonessential panels and switches the replay into a capture-ready
  cinematic surface.

Each scenario dashboard also includes playback speed, jump-to-critical controls, event
filters, live state chips, a copyable run summary, and its own video view. The
main replay is a Three.js/WebGL robotics viewport with floor grid, coordinate axes,
camera frustum, trays, fixture, robot links, tool poses, planned paths, and installed
parts rendered from the event log.

## Why This Matters

The workbench makes the project look like an integrated robotics application, not a pile of
scripts. It is also honest: every visualization is driven by generated run artifacts rather
than hard-coded screenshots.
