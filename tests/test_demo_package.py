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
                self.assertTrue((output_dir / scenario / "dashboard.html").exists())
                self.assertTrue((output_dir / scenario / "acceptance_report.md").exists())
                self.assertTrue((output_dir / scenario / "metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
