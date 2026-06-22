from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from microfactory.demo.package import DEMO_SCENARIOS, build_demo_package


class DemoPackageTests(unittest.TestCase):
    def test_demo_package_generates_postable_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "demo"
            runs = build_demo_package(output_dir)

            self.assertEqual(len(runs), len(DEMO_SCENARIOS))
            self.assertTrue((output_dir / "index.html").exists())
            self.assertTrue((output_dir / "manifest.json").exists())
            self.assertTrue((output_dir / "linkedin-post.md").exists())
            self.assertTrue((output_dir / "README.md").exists())
            index = (output_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("Scenario Workbench", index)
            self.assertIn("recordingModeButton", index)
            for scenario in DEMO_SCENARIOS:
                dashboard = output_dir / scenario / "dashboard.html"
                self.assertTrue(dashboard.exists())
                dashboard_html = dashboard.read_text(encoding="utf-8")
                self.assertIn("robotViewport", dashboard_html)
                self.assertIn("RoboDK/RViz-style", dashboard_html)
                self.assertIn("three.module.min.js", dashboard_html)
                self.assertIn("MoveIt-style planning scene", dashboard_html)
                self.assertIn("Planning Stack", dashboard_html)
                self.assertIn("Live Inspector", dashboard_html)
                self.assertIn("camera-inset", dashboard_html)
                self.assertIn("icon-logo", dashboard_html)
                self.assertIn("icon-robot", dashboard_html)
                self.assertIn("timelineMini", dashboard_html)
                self.assertIn("data-view=\"iso\"", dashboard_html)
                self.assertIn("speedSelect", dashboard_html)
                self.assertIn("nextCriticalBtn", dashboard_html)
                self.assertIn("filterBar", dashboard_html)
                self.assertIn("copySummaryBtn", dashboard_html)
                self.assertTrue(
                    (
                        output_dir
                        / scenario
                        / "assets"
                        / "vendor"
                        / "three"
                        / "three.module.min.js"
                    ).exists()
                )
                self.assertTrue(
                    (
                        output_dir
                        / scenario
                        / "assets"
                        / "vendor"
                        / "three"
                        / "three.core.min.js"
                    ).exists()
                )
                self.assertTrue((output_dir / scenario / "acceptance_report.md").exists())
                self.assertTrue((output_dir / scenario / "metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
