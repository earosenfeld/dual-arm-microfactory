from __future__ import annotations

import html
import json
from pathlib import Path

from microfactory.control.assembly import AssemblyResult


def write_static_dashboard(result: AssemblyResult, output_path: Path) -> None:
    payload = {
        "success": result.success,
        "state": result.state.as_dict(),
        "events": result.log.as_list(),
    }
    serialized = json.dumps(payload, indent=2)
    escaped = html.escape(serialized)
    output_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dual-Arm Microfactory Run</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #101418;
      --panel: #171e25;
      --text: #e8edf2;
      --muted: #9aa7b5;
      --pass: #57d68d;
      --warn: #f2c14e;
      --fail: #ff6b6b;
      --recovered: #66b7ff;
    }}
    body {{
      margin: 0;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px;
    }}
    h1 {{ margin-bottom: 4px; }}
    .muted {{ color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid #26313b;
      border-radius: 8px;
      padding: 16px;
    }}
    .status-pass {{ color: var(--pass); }}
    .status-warn {{ color: var(--warn); }}
    .status-fail {{ color: var(--fail); }}
    .status-recovered {{ color: var(--recovered); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border-radius: 8px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #26313b;
      vertical-align: top;
      text-align: left;
    }}
    pre {{
      white-space: pre-wrap;
      background: #0b0f13;
      border: 1px solid #26313b;
      border-radius: 8px;
      padding: 16px;
      overflow: auto;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Dual-Arm Autonomous Microfactory</h1>
    <div class="muted">Run dashboard generated from the simulation event log.</div>
    <section class="grid" id="summary"></section>
    <section>
      <h2>Event Timeline</h2>
      <table>
        <thead>
          <tr><th>Time</th><th>Phase</th><th>Status</th><th>Message</th></tr>
        </thead>
        <tbody id="events"></tbody>
      </table>
    </section>
    <section>
      <h2>Raw Payload</h2>
      <pre>{escaped}</pre>
    </section>
  </main>
  <script>
    const payload = {serialized};
    const counts = payload.events.reduce((acc, event) => {{
      acc[event.status] = (acc[event.status] || 0) + 1;
      return acc;
    }}, {{}});
    document.getElementById("summary").innerHTML = [
      ["Final status", payload.success ? "PASS" : "FAIL"],
      ["Job", payload.state.job_id],
      ["Recoveries", counts.recovered || 0],
      ["Failures", counts.fail || 0],
      ["Cycle time", `${{payload.state.cycle_time_s}}s`],
    ].map(([label, value]) => `<div class="card"><div class="muted">${{label}}</div><h2>${{value}}</h2></div>`).join("");
    document.getElementById("events").innerHTML = payload.events.map((event) => `
      <tr>
        <td>${{event.timestamp}}</td>
        <td>${{event.phase}}</td>
        <td class="status-${{event.status}}">${{event.status}}</td>
        <td>${{event.message}}</td>
      </tr>
    `).join("");
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )
