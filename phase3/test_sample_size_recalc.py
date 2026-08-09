import unittest

from phase3.sample_size_recalc import required_teams_per_arm


class Phase3SampleSizeTest(unittest.TestCase):
    def test_phase2_reference_icc_015(self):
        out = required_teams_per_arm(nbar=6, icc=0.15, r=0.65, cluster_loss=0.10)
        self.assertEqual(out["required_teams_per_arm"], 12)

    def test_phase2_reference_icc_040(self):
        out = required_teams_per_arm(nbar=6, icc=0.40, r=0.65, cluster_loss=0.10)
        self.assertEqual(out["required_teams_per_arm"], 21)

    def test_floor(self):
        out = required_teams_per_arm(nbar=20, icc=0.01, r=0.90, cluster_loss=0.0)
        self.assertGreaterEqual(out["required_teams_per_arm"], 6)


if __name__ == "__main__":
    unittest.main()
