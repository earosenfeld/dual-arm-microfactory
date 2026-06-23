from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from microfactory.control.assembly import AssemblyResult
from microfactory.reporting.metrics import summarize_run


def write_static_dashboard(result: AssemblyResult, output_path: Path) -> None:
    payload = {
        "success": result.success,
        "metrics": summarize_run(result).as_dict(),
        "state": result.state.as_dict(),
        "events": result.log.as_list(),
    }
    _copy_three_vendor(output_path.parent)
    serialized = json.dumps(payload, indent=2)
    escaped = html.escape(serialized)
    template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Dual-Arm Microfactory Replay</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #090a0c;
      --band: #111317;
      --panel: #15181d;
      --panel-2: #1c2128;
      --panel-3: #242a33;
      --panel-4: #2b313b;
      --line: #303844;
      --line-strong: #4b5563;
      --text: #f5f7fa;
      --muted: #a7b0be;
      --blue: #38a3ff;
      --green: #43e07f;
      --yellow: #ffd166;
      --red: #ff5f7a;
      --cyan: #2ee6d6;
      --violet: #ad8cff;
      --orange: #ff9f1c;
      --steel: #cad3de;
      --shadow: 0 18px 50px rgba(0,0,0,0.28);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      font-variant-numeric: tabular-nums;
    }
    main {
      width: min(1800px, calc(100vw - 20px));
      margin: 0 auto;
      padding: 10px 0 28px;
    }
    header {
      display: grid;
      grid-template-columns: minmax(330px, 1fr) auto auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 8px;
      min-height: 58px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #15181d, #101216);
      box-shadow: var(--shadow);
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 {
      margin-bottom: 3px;
      font-size: 21px;
      font-weight: 900;
      letter-spacing: 0;
      line-height: 1.12;
    }
    .icon-sprite { display: none; }
    .icon {
      width: 16px;
      height: 16px;
      flex: 0 0 auto;
      stroke: currentColor;
      fill: none;
      stroke-width: 1.9;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .icon.fill {
      fill: currentColor;
      stroke: none;
    }
    .brand-lockup {
      display: grid;
      grid-template-columns: 42px minmax(0, 1fr);
      gap: 11px;
      align-items: center;
      min-width: 0;
    }
    .brand-mark {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(46,230,214,0.48);
      border-radius: 8px;
      background:
        linear-gradient(135deg, rgba(46,230,214,0.22), rgba(255,159,28,0.10)),
        #101317;
      color: var(--cyan);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04), 0 0 24px rgba(46,230,214,0.18);
    }
    .brand-mark .icon {
      width: 27px;
      height: 27px;
      stroke-width: 1.65;
    }
    .app-caption {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.25;
    }
    .menu-strip {
      display: flex;
      gap: 4px;
      justify-content: center;
      flex-wrap: wrap;
      min-width: 0;
    }
    .menu-item {
      height: 32px;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: linear-gradient(180deg, var(--panel-3), var(--panel-2));
      color: var(--steel);
      font-size: 12px;
      font-weight: 750;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .menu-item .icon { color: var(--cyan); width: 15px; height: 15px; }
    .menu-item:nth-child(2) .icon { color: var(--orange); }
    .menu-item:nth-child(3) .icon { color: var(--blue); }
    .menu-item:nth-child(4) .icon { color: var(--green); }
    .menu-item.active {
      border-color: rgba(46,230,214,0.55);
      color: #ffffff;
      background: linear-gradient(180deg, #26333a, #172026);
    }
    h2 {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 18px;
      margin-bottom: 12px;
    }
    h2 .icon { color: var(--cyan); }
    .subhead {
      color: var(--muted);
      font-size: 15px;
      max-width: 940px;
      line-height: 1.45;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-width: 104px;
      height: 38px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--panel);
      font-weight: 800;
      letter-spacing: 0.02em;
    }
    .pill.pass { color: var(--green); border-color: rgba(67, 224, 127, 0.5); background: rgba(67,224,127,0.08); }
    .pill.fail { color: var(--red); border-color: rgba(255, 95, 122, 0.52); background: rgba(255,95,122,0.08); }
    .status-strip {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 8px;
    }
    .status-cell {
      min-height: 48px;
      padding: 10px 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #15191f, #101318);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
    }
    .status-head {
      display: flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      margin-bottom: 5px;
    }
    .status-k {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 0;
    }
    .status-head .icon {
      width: 14px;
      height: 14px;
      color: var(--orange);
    }
    .status-v {
      font-size: 14px;
      font-weight: 850;
      overflow-wrap: anywhere;
    }
    .sim-shell {
      display: grid;
      grid-template-columns: 280px minmax(640px, 1fr) 340px;
      gap: 8px;
      align-items: stretch;
    }
    .panel {
      background: linear-gradient(180deg, #161a20, #12151a);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      min-width: 0;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      min-height: 44px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #1c2128, #14181e);
    }
    .panel-title {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #eef3f8;
    }
    .panel-title .icon {
      width: 15px;
      height: 15px;
      color: var(--cyan);
    }
    .panel-body { padding: 12px; }
    .display-list,
    .stack-list,
    .inspector-list {
      display: grid;
      gap: 8px;
      font-size: 12px;
    }
    .display-row,
    .stack-row,
    .inspector-row {
      display: grid;
      grid-template-columns: auto 1fr auto;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      padding: 7px 8px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: linear-gradient(180deg, #20262e, #1a2027);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
    }
    button.display-row {
      width: 100%;
      color: var(--text);
      text-align: left;
      cursor: pointer;
      min-height: 38px;
      padding: 7px 8px;
      justify-content: stretch;
    }
    button.display-row:hover {
      border-color: rgba(46,230,214,0.45);
    }
    button.display-row.off {
      color: var(--muted);
      background: #15191e;
    }
    button.display-row.off .display-check {
      color: var(--muted);
      border-color: rgba(167,176,190,0.24);
      background: rgba(167,176,190,0.06);
      box-shadow: none;
    }
    .display-check {
      width: 22px;
      height: 22px;
      display: grid;
      place-items: center;
      border-radius: 6px;
      border: 1px solid rgba(46,230,214,0.36);
      background: rgba(46,230,214,0.10);
      color: var(--cyan);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 0 16px rgba(46,230,214,0.10);
    }
    .display-check .icon {
      width: 14px;
      height: 14px;
    }
    .stack-row {
      grid-template-columns: 74px 1fr auto;
      font-variant-numeric: tabular-nums;
    }
    .stack-bar {
      height: 8px;
      border-radius: 999px;
      background: #0d0f12;
      overflow: hidden;
      border: 1px solid #333b46;
    }
    .stack-fill {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--orange), var(--cyan), var(--green));
    }
    .inspector-row {
      grid-template-columns: minmax(92px, auto) minmax(0, 1fr);
    }
    .inspector-key {
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 10px;
    }
    .inspector-value {
      color: #e9f2fb;
      font-weight: 750;
      overflow-wrap: anywhere;
    }
    .scene-tree {
      display: grid;
      gap: 8px;
      font-size: 13px;
    }
    .tree-row {
      display: grid;
      grid-template-columns: 28px 1fr auto;
      align-items: center;
      gap: 8px;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #20262e, #1a2027);
    }
    .tree-icon {
      width: 24px;
      height: 24px;
      display: grid;
      place-items: center;
      border-radius: 7px;
      background: rgba(255,255,255,0.045);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 0 14px rgba(46,230,214,0.10);
    }
    .tree-icon .icon {
      width: 15px;
      height: 15px;
    }
    .tree-status {
      color: var(--muted);
      font-size: 11px;
    }
    .viewport-panel {
      position: relative;
      min-height: 760px;
      background: #07080a;
    }
    #robotViewport {
      position: relative;
      min-height: 760px;
      height: min(76vh, 820px);
      background:
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(0deg, rgba(255,255,255,0.022) 1px, transparent 1px),
        radial-gradient(circle at 50% 34%, rgba(46,230,214,0.07), transparent 30%),
        #07080a;
      background-size: 32px 32px, 32px 32px, auto, auto;
    }
    #robotViewport canvas {
      display: block;
      width: 100%;
      height: 100%;
      outline: none;
    }
    .viewport-toolbar {
      position: absolute;
      top: 12px;
      left: 12px;
      right: 12px;
      z-index: 5;
      display: flex;
      justify-content: space-between;
      gap: 10px;
      pointer-events: none;
    }
    .toolbar-group {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      pointer-events: auto;
    }
    .viewport-badge {
      position: absolute;
      top: 62px;
      left: 12px;
      z-index: 6;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      border: 1px solid rgba(121, 147, 170, 0.32);
      border-radius: 8px;
      background: rgba(13, 15, 18, 0.84);
      backdrop-filter: blur(12px);
      color: #dcecff;
      font-size: 12px;
      font-weight: 850;
      pointer-events: none;
    }
    .viewport-badge span {
      color: var(--cyan);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 10px;
    }
    .viewport-readout {
      position: absolute;
      top: 106px;
      left: 12px;
      z-index: 6;
      display: grid;
      gap: 5px;
      min-width: 186px;
      padding: 9px 10px;
      border: 1px solid rgba(121, 147, 170, 0.32);
      border-radius: 8px;
      background: rgba(13, 15, 18, 0.84);
      backdrop-filter: blur(12px);
      color: var(--muted);
      font-size: 11px;
      font-variant-numeric: tabular-nums;
      pointer-events: none;
    }
    .readout-line {
      display: flex;
      justify-content: space-between;
      gap: 14px;
    }
    .readout-line strong {
      color: #e9f2fb;
      font-weight: 800;
    }
    .view-cube {
      position: absolute;
      top: 72px;
      right: 18px;
      z-index: 6;
      width: 88px;
      height: 88px;
      border: 1px solid rgba(140,165,190,0.34);
      border-radius: 8px;
      background: rgba(13, 15, 18, 0.82);
      backdrop-filter: blur(10px);
    }
    .view-cube::before {
      content: "Z";
      position: absolute;
      top: 10px;
      left: 38px;
      color: var(--blue);
      font-weight: 900;
    }
    .view-cube::after {
      content: "X  Y";
      position: absolute;
      bottom: 12px;
      left: 24px;
      color: var(--muted);
      font-size: 12px;
      word-spacing: 10px;
    }
    .hud {
      position: absolute;
      left: 12px;
      right: 12px;
      bottom: 12px;
      z-index: 5;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      pointer-events: none;
    }
    .hud-chip,
    .legend-chip {
      border: 1px solid rgba(121, 147, 170, 0.32);
      background: rgba(15, 17, 20, 0.88);
      border-radius: 8px;
      padding: 10px;
      backdrop-filter: blur(12px);
    }
    .hud-label {
      color: var(--muted);
      font-size: 10px;
      margin-bottom: 7px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .hud-value {
      font-size: 15px;
      font-weight: 850;
      overflow-wrap: anywhere;
    }
    .legend {
      position: absolute;
      right: 18px;
      bottom: 122px;
      z-index: 5;
      display: grid;
      gap: 6px;
      width: 186px;
      pointer-events: none;
    }
    .legend-row {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
    }
    .swatch {
      width: 13px;
      height: 13px;
      border-radius: 3px;
      border: 1px solid rgba(255,255,255,0.25);
    }
    .camera-inset {
      position: absolute;
      left: 12px;
      bottom: 122px;
      z-index: 5;
      width: 238px;
      border: 1px solid rgba(121, 147, 170, 0.32);
      border-radius: 8px;
      background: rgba(13, 15, 18, 0.88);
      overflow: hidden;
      backdrop-filter: blur(12px);
      pointer-events: none;
    }
    .camera-head {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      padding: 8px 10px;
      border-bottom: 1px solid rgba(121, 147, 170, 0.24);
      color: #dcecff;
      font-size: 11px;
      font-weight: 850;
    }
    .camera-feed {
      position: relative;
      height: 118px;
      background:
        linear-gradient(90deg, rgba(98,182,255,0.14) 1px, transparent 1px),
        linear-gradient(0deg, rgba(98,182,255,0.12) 1px, transparent 1px),
        radial-gradient(circle at 34% 56%, rgba(87,214,141,0.38), transparent 10%),
        radial-gradient(circle at 64% 45%, rgba(242,193,78,0.28), transparent 12%),
        #0b1118;
      background-size: 18px 18px, 18px 18px, auto, auto, auto;
    }
    .camera-feed::before {
      content: "";
      position: absolute;
      inset: 18px 52px 22px 42px;
      border: 2px solid var(--green);
      border-radius: 4px;
      box-shadow: 0 0 18px rgba(87,214,141,0.32);
    }
    .camera-feed::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      top: 46%;
      height: 2px;
      background: rgba(98,182,255,0.72);
      box-shadow: 0 0 16px rgba(98,182,255,0.72);
    }
    .camera-foot {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      padding: 8px 10px;
      color: var(--muted);
      font-size: 11px;
      border-top: 1px solid rgba(121, 147, 170, 0.24);
    }
    .controls {
      display: grid;
      grid-template-columns: auto auto auto auto minmax(90px, 1fr) 82px auto;
      gap: 8px;
      align-items: center;
      padding: 10px 12px;
      border-top: 1px solid var(--line);
      background: linear-gradient(180deg, #181c22, #111418);
    }
    button,
    select {
      border: 1px solid var(--line);
      background: linear-gradient(180deg, var(--panel-3), var(--panel-2));
      color: var(--text);
      border-radius: 8px;
      padding: 8px 10px;
      font-weight: 750;
      cursor: pointer;
      min-height: 36px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }
    button:hover { border-color: var(--cyan); color: #ffffff; }
    button.active {
      border-color: var(--cyan);
      color: var(--cyan);
      background: linear-gradient(180deg, #203039, #162025);
    }
    button .icon { width: 15px; height: 15px; }
    .view-btn {
      min-width: 48px;
      padding-inline: 10px;
    }
    .command-btn {
      min-width: 78px;
    }
    #prevCriticalBtn,
    #nextCriticalBtn {
      min-width: 92px;
      line-height: 1.05;
    }
    #recordingModeBtn {
      min-width: 86px;
    }
    select { width: 82px; }
    input[type="range"] { width: 100%; accent-color: var(--orange); }
    .timeline-mini {
      position: relative;
      height: 54px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c0e11;
      margin-bottom: 10px;
      overflow: hidden;
    }
    .timeline-mini::before {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, transparent 0, rgba(98,182,255,0.12) 50%, transparent 100%);
    }
    .timeline-marker {
      position: absolute;
      top: 9px;
      bottom: 9px;
      width: 3px;
      border-radius: 999px;
      background: var(--blue);
      box-shadow: 0 0 14px var(--blue);
    }
    .timeline-marker.fail {
      background: var(--red);
      box-shadow: 0 0 14px var(--red);
    }
    .timeline-cursor {
      position: absolute;
      top: 4px;
      bottom: 4px;
      width: 2px;
      background: #fff;
      box-shadow: 0 0 12px rgba(255,255,255,0.65);
    }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .metric {
      background: linear-gradient(180deg, #20262e, #181d24);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 78px;
      position: relative;
      overflow: hidden;
    }
    .metric::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background: var(--cyan);
    }
    .metric-label {
      display: flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 8px;
    }
    .metric-label .icon {
      width: 14px;
      height: 14px;
      color: var(--cyan);
    }
    .metric-value {
      font-size: 22px;
      font-weight: 850;
      line-height: 1;
      color: #ffffff;
    }
    .filter-bar {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 12px;
    }
    .filter-bar button {
      padding: 8px 10px;
      color: var(--muted);
    }
    .filter-bar button.active {
      border-color: var(--cyan);
      color: var(--cyan);
      background: #172526;
    }
    .event-list {
      display: grid;
      gap: 8px;
      max-height: 450px;
      overflow: auto;
      padding-right: 4px;
    }
    .event {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #20262e, #171c23);
      padding: 10px;
      cursor: pointer;
    }
    .event.active { border-color: var(--orange); background: #2b251b; }
    .event-top {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 4px;
      color: var(--muted);
      font-size: 12px;
    }
    .event-phase {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-width: 0;
    }
    .event-phase .icon {
      width: 14px;
      height: 14px;
      color: var(--orange);
    }
    .event-msg {
      font-size: 13px;
      line-height: 1.35;
    }
    .status-pass { color: var(--green); }
    .status-warn { color: var(--yellow); }
    .status-fail { color: var(--red); }
    .status-recovered { color: var(--blue); }
    .details {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
    }
    .log-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .log-table th, .log-table td {
      padding: 9px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    .log-table th { color: var(--muted); font-weight: 600; }
    pre {
      white-space: pre-wrap;
      background: #090d12;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      max-height: 360px;
      overflow: auto;
      font-size: 12px;
      color: #cbd7e3;
    }
    .callout {
      background: #112437;
      border: 1px solid rgba(98, 182, 255, 0.35);
      border-radius: 8px;
      padding: 14px;
      line-height: 1.45;
      color: #dcecff;
    }
    .statusbar {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
    }
    .statusbar span {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--band);
      padding: 8px 10px;
      overflow-wrap: anywhere;
    }
    .statusbar .icon { color: var(--orange); }
    .recording-mode main {
      width: min(1440px, calc(100vw - 24px));
      padding-top: 10px;
    }
    .recording-mode header,
    .recording-mode .details,
    .recording-mode .status-strip,
    .recording-mode .statusbar,
    .recording-mode .left-panel,
    .recording-mode .right-panel {
      display: none;
    }
    .recording-mode .sim-shell { grid-template-columns: 1fr; }
    .recording-mode #robotViewport { height: 86vh; }
    .recording-mode .viewport-panel { min-height: 86vh; }
    .embed-mode main {
      width: 100%;
      padding: 0;
    }
    .embed-mode header,
    .embed-mode .details,
    .embed-mode .status-strip,
    .embed-mode .statusbar,
    .embed-mode .left-panel,
    .embed-mode .right-panel {
      display: none;
    }
    .embed-mode .sim-shell {
      grid-template-columns: 1fr;
      gap: 0;
    }
    .embed-mode .viewport-panel {
      min-height: 760px;
      border: 0;
      border-radius: 0;
    }
    .embed-mode #robotViewport {
      height: 720px;
      min-height: 720px;
    }
    .cinematic-overlay {
      display: none;
      position: absolute;
      inset: 0;
      z-index: 9;
      pointer-events: none;
    }
    .cinematic-mode main {
      width: 100vw;
      padding: 0;
    }
    .cinematic-mode header,
    .cinematic-mode .details,
    .cinematic-mode .status-strip,
    .cinematic-mode .statusbar,
    .cinematic-mode .left-panel,
    .cinematic-mode .right-panel,
    .cinematic-mode .controls,
    .cinematic-mode .viewport-toolbar,
    .cinematic-mode .viewport-badge,
    .cinematic-mode .viewport-readout,
    .cinematic-mode .view-cube,
    .cinematic-mode .legend,
    .cinematic-mode .hud {
      display: none;
    }
    .cinematic-mode .sim-shell {
      grid-template-columns: 1fr;
      gap: 0;
    }
    .cinematic-mode .viewport-panel {
      min-height: 100vh;
      border: 0;
      border-radius: 0;
    }
    .cinematic-mode #robotViewport {
      height: 100vh;
      min-height: 100vh;
      cursor: none;
    }
    .cinematic-mode .camera-inset {
      left: 24px;
      bottom: 132px;
      width: 280px;
    }
    .cinematic-mode .cinematic-overlay {
      display: block;
    }
    .cinematic-titlebar,
    .cinematic-card,
    .cinematic-rail {
      position: absolute;
      border: 1px solid rgba(121,147,170,0.34);
      border-radius: 8px;
      background: rgba(9,12,16,0.91);
      backdrop-filter: blur(14px);
      box-shadow: 0 18px 50px rgba(0,0,0,0.34);
    }
    .cinematic-titlebar {
      top: 22px;
      left: 22px;
      right: 22px;
      min-height: 68px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 13px 16px;
    }
    .cinematic-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }
    .cinematic-brand .brand-mark {
      width: 40px;
      height: 40px;
    }
    .cinematic-kicker {
      color: var(--cyan);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0;
      font-weight: 900;
      margin-bottom: 3px;
    }
    .cinematic-heading {
      color: #fff;
      font-size: 30px;
      font-weight: 950;
      line-height: 1.05;
      overflow-wrap: anywhere;
    }
    .cinematic-status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-width: 112px;
      justify-content: center;
      border: 1px solid rgba(67,224,127,0.48);
      border-radius: 8px;
      background: rgba(67,224,127,0.08);
      color: var(--green);
      padding: 10px 12px;
      font-weight: 950;
      letter-spacing: 0;
    }
    .cinematic-card {
      right: 24px;
      bottom: 132px;
      width: min(430px, calc(100vw - 48px));
      padding: 16px;
      border-left: 4px solid var(--orange);
    }
    .cinematic-badge {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--orange);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0;
      font-weight: 950;
      margin-bottom: 10px;
    }
    .cinematic-card h2 {
      font-size: 38px;
      line-height: 1.02;
      margin: 0 0 10px;
      display: block;
    }
    .cinematic-card p {
      color: #dbe4ee;
      margin: 0;
      font-size: 18px;
      line-height: 1.42;
    }
    .cinematic-rail {
      left: 24px;
      right: 24px;
      bottom: 22px;
      min-height: 82px;
      display: grid;
      grid-template-columns: minmax(180px, 240px) 1fr;
      gap: 14px;
      align-items: center;
      padding: 12px 14px;
    }
    .cinematic-time {
      color: var(--muted);
      font-size: 12px;
    }
    .cinematic-time strong {
      display: block;
      color: #fff;
      font-size: 24px;
      margin-top: 3px;
    }
    .cinematic-chapters {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 8px;
    }
    .chapter-pill {
      position: relative;
      display: grid;
      grid-template-columns: 18px minmax(0, 1fr);
      align-items: center;
      gap: 7px;
      min-height: 46px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.035);
      padding: 8px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 850;
      overflow: hidden;
    }
    .chapter-pill::after {
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 3px;
      background: transparent;
    }
    .chapter-pill .icon {
      width: 16px;
      height: 16px;
    }
    .chapter-pill.active {
      border-color: var(--orange);
      background: rgba(255,159,28,0.12);
      color: #fff;
    }
    .chapter-pill.active::after {
      background: linear-gradient(90deg, var(--orange), #fff2b0);
    }
    .chapter-pill.done {
      border-color: rgba(46,230,214,0.36);
      color: var(--cyan);
    }
    .chapter-pill.done::after {
      background: var(--cyan);
    }
    @media (max-width: 900px) {
      .cinematic-mode .camera-inset { display: none; }
      .cinematic-titlebar {
        left: 12px;
        right: 12px;
        top: 12px;
      }
      .cinematic-heading { font-size: 22px; }
      .cinematic-card h2 { font-size: 28px; }
      .cinematic-card p { font-size: 15px; }
      .cinematic-card {
        left: 12px;
        right: 12px;
        bottom: 118px;
        width: auto;
      }
      .cinematic-rail {
        left: 12px;
        right: 12px;
        grid-template-columns: 1fr;
      }
      .cinematic-chapters {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
    }
    @media (max-width: 1280px) {
      .sim-shell { grid-template-columns: 1fr; }
      .left-panel { order: 2; }
      .right-panel { order: 3; }
      .hud { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .status-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      header { grid-template-columns: 1fr; }
    }
    @media (max-width: 760px) {
      main { width: min(100vw - 20px, 1580px); }
      header { grid-template-columns: 1fr; }
      .menu-strip { justify-content: flex-start; }
      .status-strip, .statusbar { grid-template-columns: 1fr; }
      .viewport-toolbar {
        flex-direction: column;
        align-items: flex-start;
        right: auto;
        max-width: calc(100% - 24px);
      }
      .toolbar-group { max-width: 100%; }
      .viewport-badge { top: 112px; max-width: calc(100% - 24px); }
      .controls { grid-template-columns: 1fr 1fr; }
      .metric-grid { grid-template-columns: 1fr; }
      .hud { grid-template-columns: 1fr; }
      .legend, .view-cube, .camera-inset, .viewport-readout { display: none; }
      #robotViewport { height: 560px; }
    }
  </style>
</head>
<body>
  <svg class="icon-sprite" aria-hidden="true" focusable="false">
    <symbol id="icon-logo" viewBox="0 0 24 24">
      <path d="M5 7.5 12 3l7 4.5v9L12 21l-7-4.5z"></path>
      <path d="M12 3v8.8m7-4.3-7 4.3-7-4.3"></path>
      <path d="M8.2 14.2h7.6M9.5 16.5h5"></path>
    </symbol>
    <symbol id="icon-cube" viewBox="0 0 24 24">
      <path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"></path>
      <path d="M12 12 4 7.5m8 4.5 8-4.5M12 12v9"></path>
    </symbol>
    <symbol id="icon-route" viewBox="0 0 24 24">
      <path d="M5 18c5 0 4-12 9-12h5"></path>
      <circle cx="5" cy="18" r="2"></circle>
      <circle cx="19" cy="6" r="2"></circle>
    </symbol>
    <symbol id="icon-camera" viewBox="0 0 24 24">
      <path d="M4 8h4l1.4-2h5.2L16 8h4v10H4z"></path>
      <circle cx="12" cy="13" r="3.2"></circle>
    </symbol>
    <symbol id="icon-clipboard" viewBox="0 0 24 24">
      <path d="M9 5h6l1 2h3v14H5V7h3z"></path>
      <path d="M9 12h6M9 16h4"></path>
    </symbol>
    <symbol id="icon-target" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="8"></circle>
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4"></path>
    </symbol>
    <symbol id="icon-gauge" viewBox="0 0 24 24">
      <path d="M4 15a8 8 0 0 1 16 0"></path>
      <path d="m12 15 4-5"></path>
      <path d="M7 19h10"></path>
    </symbol>
    <symbol id="icon-eye" viewBox="0 0 24 24">
      <path d="M3 12s3.5-6 9-6 9 6 9 6-3.5 6-9 6-9-6-9-6z"></path>
      <circle cx="12" cy="12" r="2.5"></circle>
    </symbol>
    <symbol id="icon-robot" viewBox="0 0 24 24">
      <path d="M7 10h10v8H7z"></path>
      <path d="M9 10V7h6v3M12 7V4"></path>
      <circle cx="10" cy="14" r="1"></circle>
      <circle cx="14" cy="14" r="1"></circle>
      <path d="M5 13H3m18 0h-2M9 18v2m6-2v2"></path>
    </symbol>
    <symbol id="icon-displays" viewBox="0 0 24 24">
      <rect x="4" y="5" width="16" height="11" rx="2"></rect>
      <path d="M8 20h8M12 16v4"></path>
    </symbol>
    <symbol id="icon-layers" viewBox="0 0 24 24">
      <path d="m12 4 9 5-9 5-9-5z"></path>
      <path d="m3 13 9 5 9-5"></path>
    </symbol>
    <symbol id="icon-stack" viewBox="0 0 24 24">
      <path d="M5 7h14M5 12h14M5 17h14"></path>
      <path d="M8 7v10"></path>
    </symbol>
    <symbol id="icon-metrics" viewBox="0 0 24 24">
      <path d="M5 19V9m7 10V5m7 14v-7"></path>
    </symbol>
    <symbol id="icon-fit" viewBox="0 0 24 24">
      <path d="M8 4H4v4m12-4h4v4M8 20H4v-4m16 0v4h-4"></path>
      <path d="M9 9h6v6H9z"></path>
    </symbol>
    <symbol id="icon-ghost" viewBox="0 0 24 24">
      <path d="M6 20V9a6 6 0 0 1 12 0v11l-3-2-3 2-3-2z"></path>
      <circle cx="10" cy="11" r="1"></circle>
      <circle cx="14" cy="11" r="1"></circle>
    </symbol>
    <symbol id="icon-play" viewBox="0 0 24 24">
      <path d="M8 5v14l11-7z"></path>
    </symbol>
    <symbol id="icon-pause" viewBox="0 0 24 24">
      <path d="M8 5v14M16 5v14"></path>
    </symbol>
    <symbol id="icon-reset" viewBox="0 0 24 24">
      <path d="M5 12a7 7 0 1 0 2-5"></path>
      <path d="M5 5v5h5"></path>
    </symbol>
    <symbol id="icon-prev" viewBox="0 0 24 24">
      <path d="M11 7 6 12l5 5M18 7l-5 5 5 5"></path>
    </symbol>
    <symbol id="icon-next" viewBox="0 0 24 24">
      <path d="m6 7 5 5-5 5M13 7l5 5-5 5"></path>
    </symbol>
    <symbol id="icon-record" viewBox="0 0 24 24">
      <rect x="5" y="5" width="14" height="14" rx="3"></rect>
      <circle cx="12" cy="12" r="3"></circle>
    </symbol>
    <symbol id="icon-check" viewBox="0 0 24 24">
      <path d="m5 12 4 4L19 6"></path>
    </symbol>
    <symbol id="icon-timeline" viewBox="0 0 24 24">
      <path d="M4 12h16"></path>
      <circle cx="7" cy="12" r="2"></circle>
      <circle cx="14" cy="12" r="2"></circle>
      <path d="M19 8v8"></path>
    </symbol>
    <symbol id="icon-inspector" viewBox="0 0 24 24">
      <path d="M5 4h10l4 4v12H5z"></path>
      <path d="M15 4v4h4M8 12h8M8 16h5"></path>
    </symbol>
    <symbol id="icon-filter" viewBox="0 0 24 24">
      <path d="M4 6h16M7 12h10M10 18h4"></path>
    </symbol>
    <symbol id="icon-axis" viewBox="0 0 24 24">
      <path d="M12 19V5m0 0-3 3m3-3 3 3M5 16l7-4 7 4"></path>
    </symbol>
  </svg>
  <main>
    <header>
      <div class="brand-lockup">
        <div class="brand-mark"><svg class="icon"><use href="#icon-logo"></use></svg></div>
        <div>
          <h1>Dual-Arm Autonomous Microfactory</h1>
          <div class="app-caption">RoboDK/RViz-style Three.js workcell replay</div>
        </div>
      </div>
      <nav class="menu-strip" aria-label="Application toolbar">
        <span class="menu-item active"><svg class="icon"><use href="#icon-cube"></use></svg>Planning Scene</span>
        <span class="menu-item"><svg class="icon"><use href="#icon-route"></use></svg>Motion Replay</span>
        <span class="menu-item"><svg class="icon"><use href="#icon-camera"></use></svg>Perception</span>
        <span class="menu-item"><svg class="icon"><use href="#icon-clipboard"></use></svg>Evidence</span>
      </nav>
      <div id="final-pill" class="pill"><svg class="icon"><use href="#icon-gauge"></use></svg>RUN</div>
    </header>

    <section class="status-strip" aria-label="Run status">
      <div class="status-cell">
        <div class="status-head"><svg class="icon"><use href="#icon-cube"></use></svg><div class="status-k">Scenario</div></div>
        <div class="status-v" id="scenarioName">conveyor recovery</div>
      </div>
      <div class="status-cell">
        <div class="status-head"><svg class="icon"><use href="#icon-route"></use></svg><div class="status-k">Planner</div></div>
        <div class="status-v" id="plannerHealth">deterministic</div>
      </div>
      <div class="status-cell">
        <div class="status-head"><svg class="icon"><use href="#icon-target"></use></svg><div class="status-k">Clearance</div></div>
        <div class="status-v" id="clearanceReadout">-- mm</div>
      </div>
      <div class="status-cell">
        <div class="status-head"><svg class="icon"><use href="#icon-eye"></use></svg><div class="status-k">Vision Confidence</div></div>
        <div class="status-v" id="confidenceReadout">--</div>
      </div>
      <div class="status-cell">
        <div class="status-head"><svg class="icon"><use href="#icon-robot"></use></svg><div class="status-k">Robot Mode</div></div>
        <div class="status-v" id="robotMode">ready</div>
      </div>
    </section>

    <section class="sim-shell">
      <aside class="panel left-panel">
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-displays"></use></svg>Displays</div>
        </div>
        <div class="panel-body">
          <div class="display-list">
            <button class="display-row active" data-display="scene"><span class="display-check"><svg class="icon"><use href="#icon-cube"></use></svg></span><span>Planning scene</span><span class="display-state">on</span></button>
            <button class="display-row active" data-display="robots"><span class="display-check"><svg class="icon"><use href="#icon-robot"></use></svg></span><span>Robot links</span><span class="display-state">on</span></button>
            <button class="display-row active" data-display="envelopes"><span class="display-check"><svg class="icon"><use href="#icon-target"></use></svg></span><span>Safety envelopes</span><span class="display-state">on</span></button>
            <button class="display-row active" data-display="camera"><span class="display-check"><svg class="icon"><use href="#icon-camera"></use></svg></span><span>Camera frustum</span><span class="display-state">on</span></button>
            <button class="display-row active" data-display="paths"><span class="display-check"><svg class="icon"><use href="#icon-route"></use></svg></span><span>Toolpath waypoints</span><span class="display-state">on</span></button>
          </div>
        </div>
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-layers"></use></svg>Scene Tree</div>
        </div>
        <div class="panel-body">
          <div class="scene-tree" id="sceneTree"></div>
        </div>
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-stack"></use></svg>Planning Stack</div>
        </div>
        <div class="panel-body">
          <div class="stack-list" id="planningStack"></div>
        </div>
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-metrics"></use></svg>Run Metrics</div>
        </div>
        <div class="panel-body">
          <div class="metric-grid" id="metrics"></div>
        </div>
      </aside>

      <section class="panel viewport-panel">
        <div id="robotViewport" aria-label="Three.js robotics workcell viewport">
          <div class="viewport-toolbar">
            <div class="toolbar-group">
              <button class="view-btn active" data-view="iso"><svg class="icon"><use href="#icon-cube"></use></svg>Iso</button>
              <button class="view-btn" data-view="top"><svg class="icon"><use href="#icon-axis"></use></svg>Top</button>
              <button class="view-btn" data-view="side"><svg class="icon"><use href="#icon-axis"></use></svg>Side</button>
              <button class="view-btn" data-view="front"><svg class="icon"><use href="#icon-axis"></use></svg>Front</button>
            </div>
            <div class="toolbar-group">
              <button id="fitViewBtn"><svg class="icon"><use href="#icon-fit"></use></svg>Fit View</button>
              <button id="ghostBtn" class="active"><svg class="icon"><use href="#icon-ghost"></use></svg>Ghosts</button>
            </div>
          </div>
          <div class="viewport-badge"><span>World</span> MoveIt-style planning scene</div>
          <div class="viewport-readout">
            <div class="readout-line"><span>left TCP</span><strong id="leftTcpReadout">--</strong></div>
            <div class="readout-line"><span>right TCP</span><strong id="rightTcpReadout">--</strong></div>
            <div class="readout-line"><span>target</span><strong id="targetReadout">none</strong></div>
          </div>
          <div class="view-cube"></div>
          <div class="legend legend-chip">
            <div class="legend-row"><span class="swatch" style="background:#62b6ff"></span>left arm</div>
            <div class="legend-row"><span class="swatch" style="background:#b99cff"></span>right arm</div>
            <div class="legend-row"><span class="swatch" style="background:#57d68d"></span>accepted state</div>
            <div class="legend-row"><span class="swatch" style="background:#ff6b6b"></span>fault state</div>
          </div>
          <div class="camera-inset">
            <div class="camera-head"><span>RGB-D / pose estimate</span><span id="cameraState">idle</span></div>
            <div class="camera-feed"></div>
            <div class="camera-foot"><span id="visionMode">waiting for detection</span><strong id="visionConfidence">--</strong></div>
          </div>
          <div class="cinematic-overlay" aria-hidden="true">
            <div class="cinematic-titlebar">
              <div class="cinematic-brand">
                <div class="brand-mark"><svg class="icon"><use href="#icon-logo"></use></svg></div>
                <div>
                  <div class="cinematic-kicker">Autonomous Recovery Demo</div>
                  <div class="cinematic-heading">Dual-Arm Microfactory Replay</div>
                </div>
              </div>
              <div class="cinematic-status"><svg class="icon"><use href="#icon-check"></use></svg><span id="cinematicStatus">RUN</span></div>
            </div>
            <div class="cinematic-card">
              <div class="cinematic-badge" id="cinematicBadge"><svg class="icon"><use href="#icon-cube"></use></svg>Opening</div>
              <h2 id="cinematicTitle">Starting autonomous assembly</h2>
              <p id="cinematicBody">The cell begins from loose parts and builds a conveyor module with perception, planning, bimanual coordination, recovery, and final acceptance.</p>
            </div>
            <div class="cinematic-rail">
              <div class="cinematic-time">
                Replay Time
                <strong id="cinematicTime">0.0s</strong>
              </div>
              <div class="cinematic-chapters" id="cinematicChapters"></div>
            </div>
          </div>
          <div class="hud">
            <div class="hud-chip">
              <div class="hud-label">Sim Time</div>
              <div class="hud-value" id="currentTime">0.0s</div>
            </div>
            <div class="hud-chip">
              <div class="hud-label">Phase</div>
              <div class="hud-value" id="currentPhase">idle</div>
            </div>
            <div class="hud-chip">
              <div class="hud-label">Status</div>
              <div class="hud-value" id="currentStatus">pending</div>
            </div>
            <div class="hud-chip">
              <div class="hud-label">Focus</div>
              <div class="hud-value" id="currentFocus">full sequence</div>
            </div>
          </div>
        </div>
        <div class="controls">
          <button id="playBtn" class="command-btn"><svg class="icon"><use href="#icon-play"></use></svg>Play</button>
          <button id="resetBtn" class="command-btn"><svg class="icon"><use href="#icon-reset"></use></svg>Reset</button>
          <button id="prevCriticalBtn" class="command-btn"><svg class="icon"><use href="#icon-prev"></use></svg>Prev Critical</button>
          <button id="nextCriticalBtn" class="command-btn"><svg class="icon"><use href="#icon-next"></use></svg>Next Critical</button>
          <input id="scrubber" type="range" min="0" max="0" value="0" step="1" aria-label="Replay scrubber">
          <select id="speedSelect" aria-label="Playback speed">
            <option value="700">0.6x</option>
            <option value="420" selected>1x</option>
            <option value="240">1.75x</option>
            <option value="120">3.5x</option>
          </select>
          <button id="recordingModeBtn" class="command-btn"><svg class="icon"><use href="#icon-record"></use></svg>Recording</button>
          <span id="stepLabel" class="muted">0 / 0</span>
        </div>
      </section>

      <aside class="panel right-panel">
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-inspector"></use></svg>Live Inspector</div>
        </div>
        <div class="panel-body">
          <div class="inspector-list" id="eventInspector"></div>
        </div>
        <div class="panel-header">
          <div class="panel-title"><svg class="icon"><use href="#icon-timeline"></use></svg>Replay Timeline</div>
        </div>
        <div class="panel-body">
          <div class="timeline-mini" id="timelineMini"></div>
          <div class="filter-bar" id="filterBar">
            <button class="active" data-filter="all"><svg class="icon"><use href="#icon-filter"></use></svg>All</button>
            <button data-filter="critical"><svg class="icon"><use href="#icon-target"></use></svg>Critical</button>
            <button data-filter="recovery"><svg class="icon"><use href="#icon-reset"></use></svg>Recovery</button>
            <button data-filter="planning"><svg class="icon"><use href="#icon-route"></use></svg>Planning</button>
          </div>
          <div class="event-list" id="eventList"></div>
        </div>
      </aside>
    </section>

    <section class="details">
      <div class="panel">
        <div class="panel-body">
          <h2><svg class="icon"><use href="#icon-check"></use></svg>What This Proves</h2>
          <div class="callout">
            The replay is rendered from generated event data: planned paths, pose estimates,
            bimanual stabilization, robot-link motion, failure detection, recovery, and final
            functional acceptance.
          </div>
          <div style="margin-top: 12px;">
            <button id="copySummaryBtn"><svg class="icon"><use href="#icon-clipboard"></use></svg>Copy Run Summary</button>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-body">
          <h2><svg class="icon"><use href="#icon-target"></use></svg>Critical Events</h2>
          <table class="log-table">
            <thead><tr><th>#</th><th>Phase</th><th>Status</th><th>Message</th></tr></thead>
            <tbody id="criticalRows"></tbody>
          </table>
        </div>
      </div>
      <div class="panel">
        <div class="panel-body">
          <h2><svg class="icon"><use href="#icon-inspector"></use></svg>Raw Run Payload</h2>
          <pre>__RAW_PAYLOAD__</pre>
        </div>
      </div>
    </section>
    <footer class="statusbar">
      <span><svg class="icon"><use href="#icon-cube"></use></svg>Renderer: Three.js WebGL, local vendor bundle</span>
      <span><svg class="icon"><use href="#icon-layers"></use></svg>Scene: generated from deterministic event log</span>
      <span><svg class="icon"><use href="#icon-route"></use></svg>Control: scrub, replay, jump critical, orbit, zoom</span>
      <span><svg class="icon"><use href="#icon-clipboard"></use></svg>Artifacts: metrics, event JSON, acceptance report</span>
    </footer>
  </main>

  <script type="module">
    import * as THREE from "./assets/vendor/three/three.module.min.js";

    const payload = __PAYLOAD__;
    const events = payload.events;
    const viewport = document.getElementById("robotViewport");
    const query = new URLSearchParams(window.location.search);
    const cinematicEnabled = query.get("cinematic") === "1";
    if (query.get("embed") === "1" || cinematicEnabled) {
      document.body.classList.add("embed-mode");
    }
    if (cinematicEnabled) {
      document.body.classList.add("cinematic-mode");
    }
    let index = 0;
    let playing = false;
    let timer = null;
    let playbackMs = cinematicEnabled ? 620 : 420;
    let eventFilter = "all";
    let showGhosts = true;
    const displayState = {
      scene: true,
      robots: true,
      envelopes: true,
      camera: true,
      paths: true,
    };
    let tween = null;
    let cameraTarget = new THREE.Vector3(0, 0.18, 0.35);
    let orbit = cinematicEnabled
      ? { yaw: -0.68, pitch: 0.52, radius: 6.45 }
      : { yaw: -0.78, pitch: 0.58, radius: 6.2 };
    let dragging = false;
    let lastPointer = { x: 0, y: 0 };
    let cinematicAutoStarted = false;

    const el = (id) => document.getElementById(id);
    const statusClass = (status) => `status-${status}`;
    const svgIcon = (name) => `<svg class="icon" aria-hidden="true"><use href="#icon-${name}"></use></svg>`;
    const criticalPhases = new Set(["active_vision", "bimanual_coordination", "functional_test"]);
    const cinematicChapters = buildCinematicChapters();
    const colors = {
      blue: 0x62b6ff,
      left: 0x62b6ff,
      right: 0xb99cff,
      accepted: 0x57d68d,
      warning: 0xf2c14e,
      fault: 0xff6b6b,
      orange: 0xff9f43,
      cyan: 0x6ee7e7,
      motor: 0xb99cff,
      sensor: 0x62b6ff,
      steel: 0x9fb3c6,
      dark: 0x151f2a,
      floor: 0x0f151d,
    };

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x080c11);
    scene.fog = new THREE.Fog(0x080c11, 6, 14);

    const camera = new THREE.PerspectiveCamera(48, 1, 0.05, 80);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.08;
    viewport.prepend(renderer.domElement);

    const ambient = new THREE.HemisphereLight(0xeaf6ff, 0x17202a, 1.4);
    scene.add(ambient);
    const keyLight = new THREE.DirectionalLight(0xffffff, 2.7);
    keyLight.position.set(-3.8, -4.5, 7.5);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.set(2048, 2048);
    scene.add(keyLight);
    const rim = new THREE.DirectionalLight(0x62b6ff, 1.2);
    rim.position.set(4, 2, 5);
    scene.add(rim);

    const materials = {
      floor: new THREE.MeshStandardMaterial({ color: colors.floor, roughness: 0.78, metalness: 0.12 }),
      tray: new THREE.MeshStandardMaterial({ color: 0x172330, roughness: 0.64, metalness: 0.22 }),
      fixture: new THREE.MeshStandardMaterial({ color: 0x22303e, roughness: 0.58, metalness: 0.35 }),
      fixtureOk: new THREE.MeshStandardMaterial({ color: colors.accepted, roughness: 0.45, metalness: 0.25 }),
      fixtureFault: new THREE.MeshStandardMaterial({ color: colors.fault, roughness: 0.55, metalness: 0.18 }),
      left: new THREE.MeshStandardMaterial({ color: colors.left, roughness: 0.42, metalness: 0.48 }),
      right: new THREE.MeshStandardMaterial({ color: colors.right, roughness: 0.42, metalness: 0.48 }),
      cyan: new THREE.MeshStandardMaterial({ color: colors.cyan, roughness: 0.38, metalness: 0.18 }),
      roller: new THREE.MeshStandardMaterial({ color: colors.warning, roughness: 0.32, metalness: 0.35 }),
      belt: new THREE.MeshStandardMaterial({ color: colors.accepted, roughness: 0.7, metalness: 0.06 }),
      beltFault: new THREE.MeshStandardMaterial({ color: colors.fault, roughness: 0.65, metalness: 0.06 }),
      motor: new THREE.MeshStandardMaterial({ color: colors.motor, roughness: 0.5, metalness: 0.38 }),
      sensor: new THREE.MeshStandardMaterial({ color: colors.sensor, roughness: 0.48, metalness: 0.2 }),
      ghost: new THREE.MeshStandardMaterial({ color: 0x8aa1b5, roughness: 0.62, metalness: 0.1, transparent: true, opacity: 0.22 }),
      rail: new THREE.MeshStandardMaterial({ color: 0x5f7080, roughness: 0.38, metalness: 0.55 }),
      clamp: new THREE.MeshStandardMaterial({ color: colors.orange, roughness: 0.42, metalness: 0.32 }),
      glass: new THREE.MeshStandardMaterial({ color: colors.blue, roughness: 0.18, metalness: 0.05, transparent: true, opacity: 0.14, side: THREE.DoubleSide }),
      envelopeLeft: new THREE.MeshBasicMaterial({ color: colors.left, transparent: true, opacity: 0.075, wireframe: true }),
      envelopeRight: new THREE.MeshBasicMaterial({ color: colors.right, transparent: true, opacity: 0.075, wireframe: true }),
      waypoint: new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.95 }),
      target: new THREE.MeshStandardMaterial({ color: colors.orange, emissive: colors.orange, emissiveIntensity: 0.55, roughness: 0.35, metalness: 0.08 }),
      towerGreen: new THREE.MeshStandardMaterial({ color: colors.accepted, emissive: colors.accepted, emissiveIntensity: 0.55, roughness: 0.28 }),
      towerYellow: new THREE.MeshStandardMaterial({ color: colors.warning, emissive: colors.warning, emissiveIntensity: 0.35, roughness: 0.28 }),
      towerRed: new THREE.MeshStandardMaterial({ color: colors.fault, emissive: colors.fault, emissiveIntensity: 0.35, roughness: 0.28 }),
      path: new THREE.LineBasicMaterial({ color: colors.left, transparent: true, opacity: 0.95 }),
      faultLine: new THREE.LineBasicMaterial({ color: colors.fault, transparent: true, opacity: 0.95 }),
      pose: new THREE.LineBasicMaterial({ color: colors.warning }),
      camera: new THREE.LineBasicMaterial({ color: colors.left, transparent: true, opacity: 0.42 }),
    };

    const objects = {};
    const groups = {
      cell: new THREE.Group(),
      parts: new THREE.Group(),
      robots: new THREE.Group(),
      overlays: new THREE.Group(),
      ghosts: new THREE.Group(),
    };
    Object.values(groups).forEach((group) => scene.add(group));

    initScene();
    initInteraction();

    function initScene() {
      const floor = new THREE.Mesh(new THREE.PlaneGeometry(8.8, 5.4), materials.floor);
      floor.rotation.x = -Math.PI / 2;
      floor.receiveShadow = true;
      groups.cell.add(floor);

      const grid = new THREE.GridHelper(8.8, 22, 0x4d647a, 0x233240);
      grid.material.transparent = true;
      grid.material.opacity = 0.68;
      groups.cell.add(grid);
      groups.cell.add(new THREE.AxesHelper(1.25));

      objects.tray = addBox(groups.cell, [-2.6, 0.06, -0.72], [1.5, 0.16, 1.25], materials.tray);
      objects.reject = addBox(groups.cell, [2.6, 0.06, -0.72], [1.5, 0.16, 1.25], materials.tray);
      objects.fixture = addBox(groups.cell, [0, 0.18, 0], [1.45, 0.34, 1.0], materials.fixture);
      createWorkcellHardware();

      addLabel("loose parts", [-3.23, 0.24, -1.34]);
      addLabel("installed / reject", [1.95, 0.24, -1.34]);
      addLabel("fixture", [-0.38, 0.62, -0.68]);

      createLooseParts();
      createInstalledParts();
      createRobots();
      createCameraFrustum();
      createOverlayObjects();
      setGhostVisibility(true);
    }

    function addBox(parent, position, scale, material) {
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(scale[0], scale[1], scale[2]), material);
      mesh.position.set(position[0], position[1], position[2]);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      parent.add(mesh);
      return mesh;
    }

    function addCylinder(parent, position, radius, depth, material, axis = "x") {
      const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, depth, 32), material);
      mesh.position.set(position[0], position[1], position[2]);
      if (axis === "x") mesh.rotation.z = Math.PI / 2;
      if (axis === "z") mesh.rotation.x = Math.PI / 2;
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      parent.add(mesh);
      return mesh;
    }

    function createWorkcellHardware() {
      addBox(groups.cell, [0, 0.09, 0], [2.24, 0.08, 1.52], materials.rail);
      addBox(groups.cell, [-0.74, 0.43, -0.58], [0.12, 0.22, 0.18], materials.clamp);
      addBox(groups.cell, [0.74, 0.43, -0.58], [0.12, 0.22, 0.18], materials.clamp);
      addBox(groups.cell, [-0.74, 0.43, 0.58], [0.12, 0.22, 0.18], materials.clamp);
      addBox(groups.cell, [0.74, 0.43, 0.58], [0.12, 0.22, 0.18], materials.clamp);
      addCylinder(groups.cell, [0, 0.7, -0.58], 0.035, 1.42, materials.rail, "x");
      addCylinder(groups.cell, [0, 0.7, 0.58], 0.035, 1.42, materials.rail, "x");

      const fence = addBox(groups.overlays, [0, 0.74, 1.88], [5.8, 1.24, 0.04], materials.glass);
      fence.castShadow = false;
      fence.receiveShadow = false;
      addBox(groups.cell, [3.42, 0.62, 1.16], [0.08, 1.24, 0.08], materials.rail);
      addBox(groups.cell, [-3.42, 0.62, 1.16], [0.08, 1.24, 0.08], materials.rail);

      addCylinder(groups.cell, [3.32, 0.82, -1.58], 0.035, 1.28, materials.rail, "y");
      objects.towerRed = addCylinder(groups.cell, [3.32, 1.54, -1.58], 0.095, 0.12, materials.towerRed, "y");
      objects.towerYellow = addCylinder(groups.cell, [3.32, 1.39, -1.58], 0.095, 0.12, materials.towerYellow, "y");
      objects.towerGreen = addCylinder(groups.cell, [3.32, 1.24, -1.58], 0.095, 0.12, materials.towerGreen, "y");

      objects.leftEnvelope = createEnvelope([-2.65, 0.22, 1.28], materials.envelopeLeft);
      objects.rightEnvelope = createEnvelope([2.65, 0.22, 1.28], materials.envelopeRight);
    }

    function createEnvelope(position, material) {
      const envelope = new THREE.Mesh(new THREE.SphereGeometry(1.72, 32, 18, 0, Math.PI * 2, 0, Math.PI * 0.72), material);
      envelope.position.set(position[0], position[1], position[2]);
      envelope.scale.set(1.08, 0.72, 1.08);
      groups.overlays.add(envelope);
      return envelope;
    }

    function createLooseParts() {
      objects.looseBase = addBox(groups.parts, [-2.88, 0.25, -1.02], [0.82, 0.13, 0.28], materials.cyan);
      objects.looseRollerA = addCylinder(groups.parts, [-3.03, 0.28, -0.5], 0.12, 0.34, materials.roller, "x");
      objects.looseRollerB = addCylinder(groups.parts, [-2.35, 0.28, -0.48], 0.12, 0.34, materials.roller, "x");
      objects.looseBelt = createBelt(groups.parts, [-2.67, 0.28, 0.08], 0.72, 0.34, materials.belt);
      objects.looseMotor = addBox(groups.parts, [-3.06, 0.32, 0.7], [0.34, 0.36, 0.34], materials.motor);
      objects.looseSensor = addBox(groups.parts, [-2.2, 0.27, 0.72], [0.34, 0.18, 0.26], materials.sensor);
    }

    function createInstalledParts() {
      objects.base = addBox(groups.parts, [0, 0.46, 0], [1.15, 0.12, 0.36], materials.cyan);
      objects.rollerA = addCylinder(groups.parts, [-0.42, 0.62, 0], 0.11, 0.42, materials.roller, "x");
      objects.rollerB = addCylinder(groups.parts, [0.42, 0.62, 0], 0.11, 0.42, materials.roller, "x");
      objects.belt = createBelt(groups.parts, [0, 0.65, 0], 1.02, 0.36, materials.belt);
      objects.motor = addBox(groups.parts, [0.78, 0.57, 0.02], [0.28, 0.28, 0.3], materials.motor);
      objects.sensor = addBox(groups.parts, [-0.72, 0.54, 0.36], [0.28, 0.14, 0.22], materials.sensor);
      objects.puck = new THREE.Mesh(new THREE.SphereGeometry(0.075, 24, 16), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.28, metalness: 0.08 }));
      objects.puck.castShadow = true;
      groups.parts.add(objects.puck);
      ["base", "rollerA", "rollerB", "belt", "motor", "sensor", "puck"].forEach((key) => objects[key].visible = false);

      objects.baseGhost = addBox(groups.ghosts, [0, 0.46, 0], [1.15, 0.12, 0.36], materials.ghost);
      objects.rollerAGhost = addCylinder(groups.ghosts, [-0.42, 0.62, 0], 0.11, 0.42, materials.ghost, "x");
      objects.rollerBGhost = addCylinder(groups.ghosts, [0.42, 0.62, 0], 0.11, 0.42, materials.ghost, "x");
      objects.beltGhost = createBelt(groups.ghosts, [0, 0.65, 0], 1.02, 0.36, materials.ghost);
      objects.motorGhost = addBox(groups.ghosts, [0.78, 0.57, 0.02], [0.28, 0.28, 0.3], materials.ghost);
      objects.sensorGhost = addBox(groups.ghosts, [-0.72, 0.54, 0.36], [0.28, 0.14, 0.22], materials.ghost);
    }

    function createBelt(parent, position, width, depth, material) {
      const group = new THREE.Group();
      group.position.set(position[0], position[1], position[2]);
      const front = addBox(group, [0, 0, -depth / 2], [width, 0.035, 0.045], material);
      const back = addBox(group, [0, 0, depth / 2], [width, 0.035, 0.045], material);
      const left = addCylinder(group, [-width / 2, 0, 0], 0.06, depth, material, "z");
      const right = addCylinder(group, [width / 2, 0, 0], 0.06, depth, material, "z");
      parent.add(group);
      return group;
    }

    function createRobots() {
      objects.leftRobot = createRobot("left", [-2.65, 0, 1.28], materials.left);
      objects.rightRobot = createRobot("right", [2.65, 0, 1.28], materials.right);
      groups.robots.add(objects.leftRobot.group);
      groups.robots.add(objects.rightRobot.group);
    }

    function createRobot(name, basePosition, material) {
      const group = new THREE.Group();
      const base = addCylinder(group, basePosition, 0.28, 0.18, material, "y");
      const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.16, 24, 16), material);
      shoulder.castShadow = true;
      group.add(shoulder);
      const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.13, 24, 16), material);
      elbow.castShadow = true;
      group.add(elbow);
      const wrist = new THREE.Mesh(new THREE.SphereGeometry(0.105, 24, 16), material);
      wrist.castShadow = true;
      group.add(wrist);
      const upper = createLink(material);
      const forearm = createLink(material);
      const tool = addBox(group, [0, 0, 0], [0.22, 0.09, 0.14], material);
      return { group, base, shoulder, elbow, wrist, upper, forearm, tool, basePosition: new THREE.Vector3(...basePosition) };
    }

    function createLink(material) {
      const mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.065, 1, 24), material);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      groups.robots.add(mesh);
      return mesh;
    }

    function createCameraFrustum() {
      const points = [
        new THREE.Vector3(0, 2.75, -1.95),
        new THREE.Vector3(-1.25, 0.02, -0.78),
        new THREE.Vector3(1.25, 0.02, -0.78),
        new THREE.Vector3(1.25, 0.02, 0.92),
        new THREE.Vector3(-1.25, 0.02, 0.92),
      ];
      const edges = [0,1, 0,2, 0,3, 0,4, 1,2, 2,3, 3,4, 4,1];
      const vertices = [];
      for (let i = 0; i < edges.length; i += 1) vertices.push(points[edges[i]]);
      const geometry = new THREE.BufferGeometry().setFromPoints(vertices);
      objects.cameraFrustum = new THREE.LineSegments(geometry, materials.camera);
      groups.overlays.add(objects.cameraFrustum);
      objects.cameraBody = addBox(groups.overlays, [0, 2.75, -1.95], [0.55, 0.26, 0.22], materials.sensor);
      objects.cameraBody.rotation.x = -0.25;
      addLabel("RGB-D", [0.28, 2.62, -1.95]);
    }

    function createOverlayObjects() {
      objects.pathLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]), materials.path);
      groups.overlays.add(objects.pathLine);
      objects.pathLine.visible = false;
      objects.waypoints = new THREE.Group();
      groups.overlays.add(objects.waypoints);
      objects.targetMarker = new THREE.Mesh(new THREE.SphereGeometry(0.095, 24, 16), materials.target);
      objects.targetMarker.visible = false;
      groups.overlays.add(objects.targetMarker);

      objects.poseCrosshair = new THREE.Group();
      const axes = [
        [new THREE.Vector3(-0.16, 0, 0), new THREE.Vector3(0.16, 0, 0)],
        [new THREE.Vector3(0, -0.16, 0), new THREE.Vector3(0, 0.16, 0)],
        [new THREE.Vector3(0, 0, -0.16), new THREE.Vector3(0, 0, 0.16)],
      ];
      axes.forEach(([a, b]) => {
        const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]), materials.pose);
        objects.poseCrosshair.add(line);
      });
      objects.poseCrosshair.visible = false;
      groups.overlays.add(objects.poseCrosshair);
    }

    function addLabel(text, position) {
      const canvas = document.createElement("canvas");
      canvas.width = 256;
      canvas.height = 64;
      const c = canvas.getContext("2d");
      c.fillStyle = "rgba(12,18,26,0.76)";
      c.roundRect(0, 0, 256, 64, 10);
      c.fill();
      c.fillStyle = "#d9e6f2";
      c.font = "700 24px Segoe UI, Arial";
      c.fillText(text, 18, 40);
      const texture = new THREE.CanvasTexture(canvas);
      const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
      const sprite = new THREE.Sprite(material);
      sprite.position.set(position[0], position[1], position[2]);
      sprite.scale.set(0.62, 0.16, 1);
      groups.overlays.add(sprite);
      return sprite;
    }

    function updateRobot(robot, toolPoint) {
      const base = robot.basePosition;
      const shoulder = new THREE.Vector3(base.x, 0.42, base.z);
      const target = new THREE.Vector3(toolPoint.x, toolPoint.y, toolPoint.z);
      const elbow = new THREE.Vector3().lerpVectors(shoulder, target, 0.48);
      elbow.y += 0.82;
      robot.shoulder.position.copy(shoulder);
      robot.elbow.position.copy(elbow);
      robot.wrist.position.copy(target);
      robot.tool.position.copy(target);
      alignCylinder(robot.upper, shoulder, elbow);
      alignCylinder(robot.forearm, elbow, target);
      robot.tool.lookAt(elbow);
    }

    function alignCylinder(mesh, a, b) {
      const midpoint = new THREE.Vector3().addVectors(a, b).multiplyScalar(0.5);
      const direction = new THREE.Vector3().subVectors(b, a);
      mesh.position.copy(midpoint);
      mesh.scale.set(1, direction.length(), 1);
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
    }

    function sceneState(eventIndex = index) {
      const state = {
        installed: new Set(),
        hiddenLoose: new Set(),
        beltFault: false,
        fixtureMode: "normal",
        leftTool: { x: -1.2, y: 0.95, z: 0.78 },
        rightTool: { x: 1.2, y: 0.95, z: 0.78 },
        plannedPath: null,
        cameraPulse: false,
        activePose: null,
        puckProgress: 0,
        status: "idle",
        lastDetection: null,
        lastPlan: null,
        lastGrasp: null,
        lastAssist: null,
      };

      for (let i = 0; i <= eventIndex; i += 1) {
        const event = events[i];
        const msg = event.message.toLowerCase();
        const details = event.details || {};
        state.status = event.status;
        if (event.status === "fail") state.fixtureMode = "fault";
        if (event.status === "recovered") state.fixtureMode = "recovered";
        if (event.phase === "perception" || event.phase === "active_vision") {
          state.cameraPulse = true;
          if (details.detection) {
            state.lastDetection = details.detection;
            state.activePose = poseToWorld(details.detection.kind);
          }
        }
        if (event.phase === "grasp_planning" && details.grasp) {
          state.lastGrasp = details.grasp;
        }
        if (event.phase === "motion_planning" && details.plan) {
          const target = planTargetToWorld(details.plan);
          state.lastPlan = details.plan;
          state.plannedPath = {
            arm: details.plan.arm,
            start: details.plan.arm === "left_arm" ? state.leftTool : state.rightTool,
            target,
            status: details.plan.status,
            clearance: details.plan.min_clearance_mm,
          };
          if (details.plan.arm === "left_arm") state.leftTool = target;
          if (details.plan.arm === "right_arm") state.rightTool = target;
        }
        if (event.phase === "bimanual_coordination") {
          if (details.assist_arm) state.lastAssist = details.assist_arm;
          if (details.assist_arm === "left_arm") state.leftTool = { x: -0.42, y: 0.8, z: -0.18 };
          if (details.assist_arm === "right_arm") state.rightTool = { x: 0.42, y: 0.8, z: -0.18 };
        }
        if (event.phase === "execution") {
          if (msg.includes("left_arm")) state.leftTool = { x: -0.25, y: 0.78, z: 0.0 };
          if (msg.includes("right_arm")) state.rightTool = { x: 0.25, y: 0.78, z: 0.0 };
        }
        if (msg.includes("installed base")) {
          state.hiddenLoose.add("base");
          state.installed.add("base");
        }
        if (msg.includes("installed roller")) {
          if (!state.installed.has("rollerA")) {
            state.hiddenLoose.add("rollerA");
            state.installed.add("rollerA");
          } else {
            state.hiddenLoose.add("rollerB");
            state.installed.add("rollerB");
          }
        }
        if (msg.includes("belt placed") || msg.includes("belt slip")) {
          state.hiddenLoose.add("belt");
          state.installed.add("belt");
          state.beltFault = event.status === "fail";
        }
        if (msg.includes("re-tensioning")) {
          state.beltFault = false;
        }
        if (msg.includes("installed motor")) {
          state.hiddenLoose.add("motor");
          state.installed.add("motor");
        }
        if (msg.includes("installed sensor")) {
          state.hiddenLoose.add("sensor");
          state.installed.add("sensor");
        }
        if (event.phase === "functional_test" && event.status === "pass") {
          state.fixtureMode = "accepted";
          state.puckProgress = 1;
        }
      }
      return state;
    }

    function poseToWorld(kind) {
      return {
        base_plate: new THREE.Vector3(-2.88, 0.58, -1.02),
        roller: new THREE.Vector3(-2.68, 0.58, -0.49),
        belt: new THREE.Vector3(-2.67, 0.58, 0.08),
        motor: new THREE.Vector3(-3.06, 0.62, 0.7),
        sensor: new THREE.Vector3(-2.2, 0.58, 0.72),
      }[kind] || new THREE.Vector3(-2.5, 0.58, -0.3);
    }

    function planTargetToWorld(plan) {
      const target = plan.target || {};
      const x = Number(target.x ?? 0);
      const y = Number(target.y ?? 0);
      const z = Number(target.z ?? 0.2);
      if (Math.abs(x) < 0.03 && Math.abs(y) < 0.03) {
        return { x: plan.arm === "left_arm" ? -0.18 : 0.18, y: 0.9, z: 0.05 };
      }
      return {
        x: Math.max(-3.05, Math.min(3.05, (x - 0.35) * 6.0)),
        y: Math.max(0.45, Math.min(1.4, z * 5.2)),
        z: Math.max(-1.25, Math.min(1.25, (y - 0.42) * 4.8)),
      };
    }

    function setGhostVisibility(visible) {
      groups.ghosts.visible = visible && displayState.scene;
    }

    function applyDisplayState() {
      groups.cell.visible = displayState.scene;
      groups.parts.visible = displayState.scene;
      groups.ghosts.visible = displayState.scene && showGhosts;
      groups.robots.visible = displayState.robots;
      if (objects.leftEnvelope) objects.leftEnvelope.visible = displayState.envelopes;
      if (objects.rightEnvelope) objects.rightEnvelope.visible = displayState.envelopes;
      if (objects.cameraFrustum) objects.cameraFrustum.visible = displayState.camera;
      if (objects.cameraBody) objects.cameraBody.visible = displayState.camera;
      if (objects.pathLine) objects.pathLine.visible = displayState.paths && Boolean(objects.pathLine.userData.active);
      if (objects.waypoints) objects.waypoints.visible = displayState.paths;
      if (objects.targetMarker) objects.targetMarker.visible = displayState.paths && Boolean(objects.targetMarker.userData.active);
      if (objects.poseCrosshair) objects.poseCrosshair.visible = displayState.paths && Boolean(objects.poseCrosshair.userData.active);
    }

    function applySceneState(state) {
      objects.fixture.material = state.fixtureMode === "accepted"
        ? materials.fixtureOk
        : state.fixtureMode === "fault"
          ? materials.fixtureFault
          : materials.fixture;

      objects.looseBase.visible = !state.hiddenLoose.has("base");
      objects.looseRollerA.visible = !state.hiddenLoose.has("rollerA");
      objects.looseRollerB.visible = !state.hiddenLoose.has("rollerB");
      objects.looseBelt.visible = !state.hiddenLoose.has("belt");
      objects.looseMotor.visible = !state.hiddenLoose.has("motor");
      objects.looseSensor.visible = !state.hiddenLoose.has("sensor");

      objects.base.visible = state.installed.has("base");
      objects.rollerA.visible = state.installed.has("rollerA");
      objects.rollerB.visible = state.installed.has("rollerB");
      objects.belt.visible = state.installed.has("belt");
      objects.belt.children.forEach((child) => child.material = state.beltFault ? materials.beltFault : materials.belt);
      objects.motor.visible = state.installed.has("motor");
      objects.sensor.visible = state.installed.has("sensor");
      objects.puck.visible = state.puckProgress > 0;
      objects.puck.position.set(-0.42 + state.puckProgress * 0.84, 0.78, 0.12);
      objects.towerRed.visible = state.fixtureMode === "fault";
      objects.towerYellow.visible = state.fixtureMode === "recovered";
      objects.towerGreen.visible = state.fixtureMode === "accepted" || state.fixtureMode === "normal";

      objects.cameraFrustum.material.opacity = state.cameraPulse ? 0.78 : 0.32;
      updateRobot(objects.leftRobot, state.leftTool);
      updateRobot(objects.rightRobot, state.rightTool);
      updatePath(state);
      updatePoseCrosshair(state);
      applyDisplayState();
      renderSceneTree(state);
      renderPlanningStack(state);
      updateToolReadouts(state);
    }

    function updatePath(state) {
      if (!state.plannedPath) {
        objects.pathLine.userData.active = false;
        objects.pathLine.visible = false;
        objects.targetMarker.userData.active = false;
        objects.targetMarker.visible = false;
        clearGroup(objects.waypoints);
        return;
      }
      const path = state.plannedPath;
      const points = [
        new THREE.Vector3(path.start.x, path.start.y, path.start.z),
        new THREE.Vector3((path.start.x + path.target.x) / 2, Math.max(path.start.y, path.target.y) + 0.45, (path.start.z + path.target.z) / 2),
        new THREE.Vector3(path.target.x, path.target.y, path.target.z),
      ];
      objects.pathLine.geometry.dispose();
      objects.pathLine.geometry = new THREE.BufferGeometry().setFromPoints(points);
      objects.pathLine.material = path.status === "warn" ? materials.faultLine : materials.path;
      objects.pathLine.userData.active = true;
      objects.pathLine.visible = displayState.paths;
      objects.targetMarker.userData.active = true;
      objects.targetMarker.visible = displayState.paths;
      objects.targetMarker.position.copy(points[2]);
      clearGroup(objects.waypoints);
      points.forEach((point, i) => {
        const marker = new THREE.Mesh(new THREE.SphereGeometry(i === 2 ? 0.052 : 0.038, 16, 10), materials.waypoint);
        marker.position.copy(point);
        objects.waypoints.add(marker);
      });
    }

    function clearGroup(group) {
      while (group.children.length > 0) {
        const child = group.children[0];
        group.remove(child);
        if (child.geometry) child.geometry.dispose();
      }
    }

    function updatePoseCrosshair(state) {
      if (!state.activePose) {
        objects.poseCrosshair.userData.active = false;
        objects.poseCrosshair.visible = false;
        return;
      }
      objects.poseCrosshair.userData.active = true;
      objects.poseCrosshair.visible = displayState.paths;
      objects.poseCrosshair.position.copy(state.activePose);
    }

    function lerp(a, b, t) {
      return a + (b - a) * t;
    }

    function easeInOut(t) {
      return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }

    function lerpPoint(a, b, t) {
      return {
        x: lerp(a.x, b.x, t),
        y: lerp(a.y, b.y, t),
        z: lerp(a.z, b.z, t),
      };
    }

    function lerpState(from, to, t) {
      const eased = easeInOut(t);
      return {
        ...to,
        leftTool: lerpPoint(from.leftTool, to.leftTool, eased),
        rightTool: lerpPoint(from.rightTool, to.rightTool, eased),
        puckProgress: lerp(from.puckProgress, to.puckProgress, eased),
      };
    }

    function animateTo(from, to) {
      const durationMs = Math.min(380, Math.max(180, playbackMs * 0.72));
      tween = { from, to, start: performance.now(), durationMs };
    }

    function currentEvent() {
      return events[Math.max(0, Math.min(index, events.length - 1))];
    }

    function renderLoop(now) {
      if (tween) {
        const t = Math.min(1, (now - tween.start) / tween.durationMs);
        applySceneState(lerpState(tween.from, tween.to, t));
        if (t >= 1) tween = null;
      }
      if (cinematicEnabled && !dragging) {
        orbit.yaw -= 0.00018;
        updateOrbitCamera();
      }
      renderer.render(scene, camera);
      requestAnimationFrame(renderLoop);
    }

    function renderAt(nextIndex) {
      const oldIndex = index;
      const from = sceneState(oldIndex);
      index = Math.max(0, Math.min(nextIndex, events.length - 1));
      const target = sceneState(index);
      const current = currentEvent();
      setText("currentTime", `${current.sim_time_s.toFixed(1)}s`);
      setText("currentPhase", current.phase);
      setText("currentStatus", current.status);
      setText("currentFocus", isCritical(current) ? "critical event" : "normal sequence");
      el("scrubber").value = String(index);
      setText("stepLabel", `${index + 1} / ${events.length}`);
      renderTopStatus(current, target);
      renderEventInspector(current, target);
      renderTimelineMini();
      updateCinematicOverlay(current);
      if (Math.abs(index - oldIndex) === 1) {
        animateTo(from, target);
      } else {
        tween = null;
        applySceneState(target);
      }
      document.querySelectorAll(".event").forEach((node) => node.classList.remove("active"));
      const active = document.querySelector(`[data-event-index="${index}"]`);
      if (active) {
        active.classList.add("active");
        keepEventVisible(active);
      }
    }

    function keepEventVisible(active) {
      const list = el("eventList");
      const top = active.offsetTop;
      const bottom = top + active.offsetHeight;
      if (top < list.scrollTop) list.scrollTop = top;
      if (bottom > list.scrollTop + list.clientHeight) list.scrollTop = bottom - list.clientHeight;
    }

    function setText(id, value) {
      el(id).textContent = value;
    }

    function setButtonContent(id, icon, label) {
      el(id).innerHTML = `${svgIcon(icon)}${label}`;
    }

    function phaseIcon(phase, status = "pass") {
      if (status === "fail") return "target";
      if (status === "recovered") return "reset";
      if (phase.includes("vision") || phase === "perception") return "camera";
      if (phase.includes("planning")) return "route";
      if (phase === "bimanual_coordination" || phase === "execution") return "robot";
      if (phase === "functional_test" || phase === "verification") return "check";
      return "timeline";
    }

    function isCritical(event) {
      return event.status !== "pass" || criticalPhases.has(event.phase);
    }

    function isPlanning(event) {
      return event.phase === "motion_planning" || event.phase === "grasp_planning";
    }

    function filteredEvents() {
      if (eventFilter === "critical") return events.map((event, i) => [event, i]).filter(([event]) => isCritical(event));
      if (eventFilter === "recovery") return events.map((event, i) => [event, i]).filter(([event]) => event.status === "recovered" || event.phase === "recovery");
      if (eventFilter === "planning") return events.map((event, i) => [event, i]).filter(([event]) => isPlanning(event));
      return events.map((event, i) => [event, i]);
    }

    function play() {
      if (playing) {
        playing = false;
        clearInterval(timer);
        setButtonContent("playBtn", "play", "Play");
        return;
      }
      playing = true;
      setButtonContent("playBtn", "pause", "Pause");
      timer = setInterval(() => {
        if (index >= events.length - 1) {
          playing = false;
          clearInterval(timer);
          setButtonContent("playBtn", "reset", "Replay");
          return;
        }
        renderAt(index + 1);
      }, playbackMs);
    }

    function restartPlaybackIfNeeded() {
      if (!playing) return;
      clearInterval(timer);
      playing = false;
      play();
    }

    function jumpCritical(direction) {
      const start = index + direction;
      for (let i = start; i >= 0 && i < events.length; i += direction) {
        if (isCritical(events[i])) {
          renderAt(i);
          return;
        }
      }
    }

    function setView(mode) {
      if (mode === "top") {
        camera.position.set(0, 7.8, 0.01);
        camera.up.set(0, 0, -1);
      } else if (mode === "side") {
        camera.position.set(6.5, 2.2, 0);
        camera.up.set(0, 1, 0);
      } else if (mode === "front") {
        camera.position.set(0, 2.4, 6.5);
        camera.up.set(0, 1, 0);
      } else {
        updateOrbitCamera();
        return;
      }
      camera.lookAt(cameraTarget);
    }

    function updateOrbitCamera() {
      const x = cameraTarget.x + orbit.radius * Math.cos(orbit.pitch) * Math.sin(orbit.yaw);
      const y = cameraTarget.y + orbit.radius * Math.sin(orbit.pitch);
      const z = cameraTarget.z + orbit.radius * Math.cos(orbit.pitch) * Math.cos(orbit.yaw);
      camera.position.set(x, y, z);
      camera.up.set(0, 1, 0);
      camera.lookAt(cameraTarget);
    }

    function resizeRenderer() {
      const rect = viewport.getBoundingClientRect();
      renderer.setSize(rect.width, rect.height, false);
      camera.aspect = rect.width / Math.max(1, rect.height);
      camera.updateProjectionMatrix();
      if (document.querySelector("[data-view].active")?.dataset.view === "iso") updateOrbitCamera();
    }

    function initInteraction() {
      viewport.addEventListener("pointerdown", (event) => {
        dragging = true;
        lastPointer = { x: event.clientX, y: event.clientY };
        viewport.setPointerCapture(event.pointerId);
      });
      viewport.addEventListener("pointermove", (event) => {
        if (!dragging) return;
        const activeView = document.querySelector("[data-view].active")?.dataset.view;
        if (activeView !== "iso") return;
        const dx = event.clientX - lastPointer.x;
        const dy = event.clientY - lastPointer.y;
        lastPointer = { x: event.clientX, y: event.clientY };
        orbit.yaw -= dx * 0.006;
        orbit.pitch = Math.max(0.18, Math.min(1.25, orbit.pitch + dy * 0.004));
        updateOrbitCamera();
      });
      viewport.addEventListener("pointerup", () => dragging = false);
      viewport.addEventListener("wheel", (event) => {
        const activeView = document.querySelector("[data-view].active")?.dataset.view;
        if (activeView !== "iso") return;
        event.preventDefault();
        orbit.radius = Math.max(3.2, Math.min(10, orbit.radius + event.deltaY * 0.006));
        updateOrbitCamera();
      }, { passive: false });
    }

    function renderMetrics() {
      const metrics = payload.metrics;
      const items = [
        ["check", "Final status", metrics.final_status],
        ["reset", "Recovery events", metrics.recovered_events],
        ["camera", "Active vision events", metrics.active_vision_events],
        ["robot", "Bimanual assists", metrics.bimanual_events],
        ["route", "Motion plans", metrics.motion_plan_count],
        ["target", "Min clearance", `${metrics.minimum_clearance_mm} mm`],
        ["gauge", "Avg plan time", `${metrics.average_planning_time_ms} ms`],
        ["timeline", "Sim elapsed", `${metrics.simulated_elapsed_s}s`],
      ];
      el("metrics").innerHTML = items.map(([icon, label, value]) => `
        <div class="metric">
          <div class="metric-label">${svgIcon(icon)}${label}</div>
          <div class="metric-value">${value}</div>
        </div>
      `).join("");
      const pill = el("final-pill");
      pill.innerHTML = `${svgIcon(metrics.final_status === "PASS" ? "check" : "target")}${metrics.final_status}`;
      pill.classList.add(metrics.final_status === "PASS" ? "pass" : "fail");
    }

    function renderSceneTree(state) {
      const rows = [
        ["robot", "left arm", "#38a3ff", "active"],
        ["robot", "right arm", "#ad8cff", "active"],
        ["camera", "RGB-D camera", "#38a3ff", state.cameraPulse ? "observing" : "ready"],
        ["cube", "fixture", state.fixtureMode === "fault" ? "#ff5f7a" : state.fixtureMode === "accepted" ? "#43e07f" : "#cad3de", state.fixtureMode],
        ["cube", "base", "#2ee6d6", state.installed.has("base") ? "installed" : "pending"],
        ["axis", "rollers", "#ffd166", `${Number(state.installed.has("rollerA")) + Number(state.installed.has("rollerB"))}/2`],
        ["route", "belt", state.beltFault ? "#ff5f7a" : "#43e07f", state.installed.has("belt") ? "seated" : "pending"],
        ["gauge", "motor", "#ad8cff", state.installed.has("motor") ? "installed" : "pending"],
        ["target", "sensor", "#38a3ff", state.installed.has("sensor") ? "installed" : "pending"],
      ];
      el("sceneTree").innerHTML = rows.map(([icon, label, color, status]) => `
        <div class="tree-row">
          <span class="tree-icon" style="color:${color};">${svgIcon(icon)}</span>
          <span>${label}</span>
          <span class="tree-status">${status}</span>
        </div>
      `).join("");
    }

    function renderPlanningStack(state) {
      const confidence = state.lastDetection ? state.lastDetection.confidence * 100 : 0;
      const graspScore = state.lastGrasp ? state.lastGrasp.score * 100 : 0;
      const planTime = state.lastPlan ? state.lastPlan.planning_time_ms : 0;
      const clearance = state.lastPlan ? state.lastPlan.min_clearance_mm : 0;
      const rows = [
        ["Vision", confidence ? `${confidence.toFixed(1)}%` : "--", confidence],
        ["Grasp", graspScore ? `${graspScore.toFixed(1)}%` : "--", graspScore],
        ["Planner", planTime ? `${planTime}ms` : "--", Math.max(0, 100 - Math.min(100, planTime / 5))],
        ["Clearance", clearance ? `${clearance.toFixed(1)}mm` : "--", Math.min(100, clearance * 3.2)],
        ["Bimanual", state.lastAssist ? state.lastAssist.replace("_", " ") : "standby", state.lastAssist ? 100 : 18],
      ];
      el("planningStack").innerHTML = rows.map(([label, value, pct]) => `
        <div class="stack-row">
          <span>${label}</span>
          <span class="stack-bar"><span class="stack-fill" style="width:${Math.max(4, Math.min(100, pct))}%"></span></span>
          <span>${value}</span>
        </div>
      `).join("");
    }

    function updateToolReadouts(state) {
      setText("leftTcpReadout", formatPoint(state.leftTool));
      setText("rightTcpReadout", formatPoint(state.rightTool));
      setText("targetReadout", state.plannedPath ? formatPoint(state.plannedPath.target) : "none");
    }

    function renderTopStatus(event, state) {
      const plan = state.lastPlan;
      const detection = state.lastDetection;
      setText("scenarioName", payload.state.job_id.replace("JOB-", "").toLowerCase());
      setText("clearanceReadout", plan ? `${plan.min_clearance_mm.toFixed(1)} mm` : "-- mm");
      setText("confidenceReadout", detection ? `${(detection.confidence * 100).toFixed(1)}%` : "--");
      setText("robotMode", event.status === "fail" ? "fault hold" : event.status === "recovered" ? "recovering" : event.phase.replace("_", " "));
      setText("plannerHealth", plan ? `${plan.status} / ${plan.planning_time_ms}ms` : "deterministic");
      setText("cameraState", state.cameraPulse ? "tracking" : "ready");
      setText("visionMode", detection ? `${detection.kind} / ${detection.view_id}` : "waiting for detection");
      setText("visionConfidence", detection ? `${(detection.confidence * 100).toFixed(1)}%` : "--");
    }

    function renderEventInspector(event, state) {
      const details = event.details || {};
      const plan = details.plan || state.lastPlan;
      const detection = details.detection || state.lastDetection;
      const grasp = details.grasp || state.lastGrasp;
      const rows = [
        ["sequence", `#${event.sequence}`],
        ["phase", event.phase],
        ["status", event.status],
        ["message", event.message],
        ["arm", plan?.arm || grasp?.arm || details.assist_arm || "--"],
        ["target", plan ? formatPose(plan.target) : state.plannedPath ? formatPoint(state.plannedPath.target) : "--"],
        ["clearance", plan ? `${plan.min_clearance_mm.toFixed(2)} mm` : grasp ? `${grasp.clearance_mm.toFixed(2)} mm` : "--"],
        ["planning", plan ? `${plan.planning_time_ms} ms / ${plan.path_length_mm.toFixed(1)} mm` : "--"],
        ["detection", detection ? `${detection.kind} ${Math.round(detection.confidence * 100)}%` : "--"],
        ["fixture", state.fixtureMode],
      ];
      el("eventInspector").innerHTML = rows.map(([key, value]) => `
        <div class="inspector-row">
          <span class="inspector-key">${safeHtml(key)}</span>
          <span class="inspector-value">${safeHtml(value)}</span>
        </div>
      `).join("");
    }

    function renderTimelineMini() {
      const max = Math.max(1, events.length - 1);
      const markers = events.map((event, i) => {
        if (!isCritical(event)) return "";
        const left = (i / max) * 100;
        const cls = event.status === "fail" ? "timeline-marker fail" : "timeline-marker";
        return `<span class="${cls}" style="left:${left}%"></span>`;
      }).join("");
      const cursor = `<span class="timeline-cursor" style="left:${(index / max) * 100}%"></span>`;
      el("timelineMini").innerHTML = markers + cursor;
    }

    function formatPoint(point) {
      return `${point.x.toFixed(2)}, ${point.y.toFixed(2)}, ${point.z.toFixed(2)}`;
    }

    function formatPose(pose) {
      return `${Number(pose.x).toFixed(2)}, ${Number(pose.y).toFixed(2)}, ${Number(pose.z).toFixed(2)}`;
    }

    function safeHtml(value) {
      return String(value ?? "--")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function firstEventIndex(predicate, fallback = 0) {
      const found = events.findIndex(predicate);
      return found >= 0 ? found : fallback;
    }

    function buildCinematicChapters() {
      const failIndex = firstEventIndex((event) => event.status === "fail", Math.floor(events.length * 0.62));
      const recoveryIndex = firstEventIndex((event) => event.status === "recovered" || event.phase === "recovery", failIndex + 1);
      const bimanualIndex = firstEventIndex((event) => event.phase === "bimanual_coordination", Math.floor(events.length * 0.38));
      const functionalIndex = firstEventIndex((event) => event.phase === "functional_test" && event.status === "pass", events.length - 1);
      const chapters = [
        {
          index: 0,
          label: "Setup",
          badge: "Autonomous start",
          icon: "cube",
          title: "From loose parts to accepted assembly",
          body: "The supervisor owns the sequence while perception, planning, and robot execution produce a replayable evidence trail.",
        },
        {
          index: firstEventIndex((event) => event.phase === "perception", 1),
          label: "Perceive",
          badge: "RGB-D perception",
          icon: "camera",
          title: "Vision estimates part pose",
          body: "The cell detects parts, tracks pose confidence, and records the evidence needed to explain every downstream motion.",
        },
        {
          index: firstEventIndex((event) => event.phase === "motion_planning", 2),
          label: "Plan",
          badge: "Collision-aware motion",
          icon: "route",
          title: "Planner clears the workcell",
          body: "Each move includes path length, planning time, and minimum clearance instead of hiding behind a black-box animation.",
        },
        {
          index: bimanualIndex,
          label: "Coordinate",
          badge: "Bimanual assist",
          icon: "robot",
          title: "Two arms stabilize the assembly",
          body: "One arm supports or stabilizes while the other installs the part, matching the real constraints of physical automation.",
        },
        {
          index: failIndex,
          label: "Fault",
          badge: "Fault detected",
          icon: "target",
          title: "The happy path breaks",
          body: "A failure is injected and surfaced in the replay, turning the demo into a recovery story instead of a simple pick-and-place.",
        },
        {
          index: recoveryIndex,
          label: "Recover",
          badge: "Supervisor recovery",
          icon: "reset",
          title: "Recovery is explicit and auditable",
          body: "The deterministic supervisor backs out, retries the physical step, and records the successful recovery transition.",
        },
        {
          index: functionalIndex,
          label: "Accept",
          badge: "Functional acceptance",
          icon: "check",
          title: "Final test closes the loop",
          body: "The conveyor is functionally tested and the run exports metrics, event JSON, and an acceptance report.",
        },
      ];
      return chapters
        .filter((chapter, position, all) => all.findIndex((other) => other.index === chapter.index && other.label === chapter.label) === position)
        .sort((a, b) => a.index - b.index);
    }

    function renderCinematicChapters() {
      el("cinematicChapters").innerHTML = cinematicChapters.map((chapter) => `
        <div class="chapter-pill" data-cinematic-index="${chapter.index}">
          ${svgIcon(chapter.icon)}
          <div>${safeHtml(chapter.label)}</div>
        </div>
      `).join("");
    }

    function currentCinematicChapter() {
      let active = cinematicChapters[0];
      for (const chapter of cinematicChapters) {
        if (chapter.index <= index) active = chapter;
      }
      return active;
    }

    function updateCinematicOverlay(event) {
      if (!cinematicEnabled) return;
      const chapter = currentCinematicChapter();
      el("cinematicBadge").innerHTML = `${svgIcon(chapter.icon)}${safeHtml(chapter.badge)}`;
      setText("cinematicTitle", chapter.title);
      setText("cinematicBody", chapter.body);
      setText("cinematicTime", `${event.sim_time_s.toFixed(1)}s`);
      setText("cinematicStatus", event.status === "fail" ? "FAULT" : event.status === "recovered" ? "RECOVERED" : payload.metrics.final_status);
      document.querySelectorAll(".chapter-pill").forEach((node) => {
        const chapterIndex = Number(node.dataset.cinematicIndex);
        node.classList.toggle("active", chapterIndex === chapter.index);
        node.classList.toggle("done", chapterIndex < chapter.index);
      });
    }

    function renderEvents() {
      const rows = filteredEvents();
      el("eventList").innerHTML = rows.map(([event, i]) => `
        <div class="event" data-event-index="${i}">
          <div class="event-top">
            <span class="event-phase">${svgIcon(phaseIcon(event.phase, event.status))}#${event.sequence} ${event.phase}</span>
            <span class="${statusClass(event.status)}">${event.status}</span>
          </div>
          <div class="event-msg">${event.message}</div>
        </div>
      `).join("") || `<div class="event"><div class="event-msg">No events match this filter.</div></div>`;
      document.querySelectorAll(".event").forEach((node) => {
        if (!node.dataset.eventIndex) return;
        node.addEventListener("click", () => renderAt(Number(node.dataset.eventIndex)));
      });
      const critical = events.filter((event) => isCritical(event));
      el("criticalRows").innerHTML = critical.map((event) => `
        <tr>
          <td>${event.sequence}</td>
          <td>${event.phase}</td>
          <td class="${statusClass(event.status)}">${event.status}</td>
          <td>${event.message}</td>
        </tr>
      `).join("");
    }

    function runSummaryText() {
      const m = payload.metrics;
      return [
        "Dual-Arm Autonomous Microfactory replay",
        `Final status: ${m.final_status}`,
        `Recoveries: ${m.recovered_events}`,
        `Active vision events: ${m.active_vision_events}`,
        `Bimanual assists: ${m.bimanual_events}`,
        `Motion plans: ${m.motion_plan_count}`,
        `Minimum clearance: ${m.minimum_clearance_mm} mm`,
        `Average planning time: ${m.average_planning_time_ms} ms`,
        `Simulated elapsed time: ${m.simulated_elapsed_s}s`,
      ].join("\\n");
    }

    async function copyRunSummary() {
      const text = runSummaryText();
      try {
        await navigator.clipboard.writeText(text);
        setButtonContent("copySummaryBtn", "check", "Copied");
      } catch {
        const area = document.createElement("textarea");
        area.value = text;
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        area.remove();
        setButtonContent("copySummaryBtn", "check", "Copied");
      }
      setTimeout(() => {
        setButtonContent("copySummaryBtn", "clipboard", "Copy Run Summary");
      }, 1400);
    }

    function syncDisplayButtons() {
      document.querySelectorAll("[data-display]").forEach((button) => {
        const key = button.dataset.display;
        const active = Boolean(displayState[key]);
        button.classList.toggle("off", !active);
        button.classList.toggle("active", active);
        const label = button.querySelector(".display-state");
        if (label) label.textContent = active ? "on" : "off";
      });
    }

    el("playBtn").addEventListener("click", play);
    el("resetBtn").addEventListener("click", () => {
      playing = false;
      clearInterval(timer);
      setButtonContent("playBtn", "play", "Play");
      renderAt(0);
    });
    el("prevCriticalBtn").addEventListener("click", () => jumpCritical(-1));
    el("nextCriticalBtn").addEventListener("click", () => jumpCritical(1));
    el("speedSelect").addEventListener("change", (event) => {
      playbackMs = Number(event.target.value);
      restartPlaybackIfNeeded();
    });
    el("recordingModeBtn").addEventListener("click", () => {
      document.body.classList.toggle("recording-mode");
      if (document.body.classList.contains("recording-mode")) {
        setButtonContent("recordingModeBtn", "record", "Exit Recording");
      } else {
        setButtonContent("recordingModeBtn", "record", "Recording");
      }
      requestAnimationFrame(resizeRenderer);
    });
    el("copySummaryBtn").addEventListener("click", copyRunSummary);
    el("fitViewBtn").addEventListener("click", () => {
      orbit = { yaw: -0.78, pitch: 0.58, radius: 6.2 };
      updateOrbitCamera();
    });
    el("ghostBtn").addEventListener("click", () => {
      showGhosts = !showGhosts;
      el("ghostBtn").classList.toggle("active", showGhosts);
      setGhostVisibility(showGhosts);
    });
    document.querySelectorAll("[data-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        eventFilter = button.dataset.filter;
        document.querySelectorAll("[data-filter]").forEach((node) => node.classList.remove("active"));
        button.classList.add("active");
        renderEvents();
        renderAt(index);
      });
    });
    document.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll("[data-view]").forEach((node) => node.classList.remove("active"));
        button.classList.add("active");
        setView(button.dataset.view);
      });
    });
    document.querySelectorAll("[data-display]").forEach((button) => {
      button.addEventListener("click", () => {
        const key = button.dataset.display;
        displayState[key] = !displayState[key];
        syncDisplayButtons();
        applyDisplayState();
      });
    });
    el("scrubber").max = String(Math.max(0, events.length - 1));
    el("scrubber").addEventListener("input", (event) => renderAt(Number(event.target.value)));
    window.addEventListener("resize", resizeRenderer);

    if (cinematicEnabled) {
      el("speedSelect").value = String(playbackMs);
    }
    renderMetrics();
    renderEvents();
    renderCinematicChapters();
    syncDisplayButtons();
    resizeRenderer();
    setView("iso");
    renderAt(0);
    if (cinematicEnabled) {
      window.setTimeout(() => {
        if (cinematicAutoStarted || playing) return;
        cinematicAutoStarted = true;
        play();
      }, 650);
    }
    requestAnimationFrame(renderLoop);
  </script>
</body>
</html>
"""
    output_path.write_text(
        template.replace("__PAYLOAD__", serialized).replace("__RAW_PAYLOAD__", escaped),
        encoding="utf-8",
    )


def _copy_three_vendor(output_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    source_dir = repo_root / "assets" / "vendor" / "three"
    target_dir = output_dir / "assets" / "vendor" / "three"
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("three.module.min.js", "three.core.min.js", "LICENSE"):
        shutil.copyfile(source_dir / filename, target_dir / filename)
