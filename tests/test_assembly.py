from __future__ import annotations

import unittest

from microfactory.cell.scenarios import build_conveyor_cell
from microfactory.control.assembly import ConveyorAssemblyController
from microfactory.cell.models import PartState, StepStatus


class ConveyorAssemblyControllerTests(unittest.TestCase):
    def test_nominal_assembly_passes(self) -> None:
        result = ConveyorAssemblyController().run(build_conveyor_cell("nominal"))

        self.assertTrue(result.success)
        self.assertTrue(result.state.fixture.functional_test_passed)
        self.assertEqual(result.log.count(StepStatus.FAIL), 0)

    def test_belt_slip_recovers_and_passes(self) -> None:
        result = ConveyorAssemblyController().run(build_conveyor_cell("belt_slip"))

        self.assertTrue(result.success)
        self.assertTrue(result.state.fixture.belt_seated)
        self.assertGreaterEqual(result.log.count(StepStatus.RECOVERED), 1)

    def test_low_confidence_vision_triggers_active_view(self) -> None:
        result = ConveyorAssemblyController().run(build_conveyor_cell("low_confidence_vision"))
        phases = [event.phase for event in result.log.events]

        self.assertTrue(result.success)
        self.assertIn("active_vision", phases)

    def test_wrong_part_is_rejected_and_spare_part_is_used(self) -> None:
        result = ConveyorAssemblyController().run(build_conveyor_cell("wrong_part"))

        self.assertTrue(result.success)
        self.assertEqual(result.state.parts["sensor-001"].state, PartState.REJECTED)
        self.assertEqual(result.state.parts["sensor-002"].state, PartState.INSTALLED)
        self.assertGreaterEqual(result.log.count(StepStatus.RECOVERED), 1)


if __name__ == "__main__":
    unittest.main()
