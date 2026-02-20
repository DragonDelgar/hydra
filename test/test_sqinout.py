import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestSqinout(unittest.TestCase):
    """Tests for sqinout mechanics i.e. various sp backend situations."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_sqinout"])
    
    def best_path(self, chartname):
        return hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 4
        ).best_path()
    
    def _test_scoring(
        self, chartname,
        s_base, s_combo, s_sp, s_solo, s_accents, s_ghosts, s_total,
    ):
        path = self.best_path(chartname)
        
        self.assertEqual(path.score_base, s_base)
        self.assertEqual(path.score_combo, s_combo)
        self.assertEqual(path.score_sp, s_sp)
        self.assertEqual(path.score_solo, s_solo)
        self.assertEqual(path.score_accents, s_accents)
        self.assertEqual(path.score_ghosts, s_ghosts)
        
        self.assertEqual(path.totalscore(), s_total)
        
    def _test_activations(
        self, chartname,
        s_acts
    ):
        path = self.best_path(chartname)
        self.assertEqual(len(path), len(s_acts))
        for i, (skip, mbt) in enumerate(s_acts):
            self.assertEqual(path.get_activation(i).skips, skip)
            self.assertEqual(path.get_activation(i).timecode.measurestr(), mbt)
        
    def _test_pathstr(self, chartname, s_pathstr):
        path = self.best_path(chartname)
        self.assertEqual(path.pathstring(), s_pathstr)
        
    def test_sqin_0ms(self):
        self._test_scoring(
            "sqin_0ms.chart",
            1900, 2850, 3200, 0, 0, 0, 7950
        )
        
    def test_sqin_early(self):
        self._test_scoring(
            "sqin_early.chart",
            2200, 3750, 3950, 0, 0, 0, 9900
        )
        
    def test_sqin_late(self):
        self._test_scoring(
            "sqin_late.chart",
            2200, 3750, 3950, 0, 0, 0, 9900
        )
    
    def test_sqout_0ms(self):
        self._test_scoring(
            "sqout_0ms.chart",
            2150, 3600, 4200, 0, 0, 0, 9950
        )

    @unittest.expectedFailure
    def test_sqout_early(self):
        """If a SqOut requires the SP window to be fudged early, it becomes
        more complicated to figure out which backends are possible. This test
        is failing because even though the SP note is being squeezed out, the
        regular backend right after it is still POSSIBLY capable of being
        squeezed in.
        
        There is a whole class of "plus or minus 1 backend" accuracy errors
        related to complex backend setups, so this test is disabled for now
        until that topic is tackled as a whole...
        """
        self._test_scoring(
            "sqout_early.chart",
            2200, 3750, 4500, 0, 0, 0, 10450
        )
        
    def test_sqout_early_emptydeact(self):
        self._test_scoring(
            "sqout_early_emptydeact.chart",
            2150, 3600, 4350, 0, 0, 0, 10100
        )
        
    def test_sqout_late(self):
        self._test_scoring(
            "sqout_late.chart",
            2200, 3750, 4500, 0, 0, 0, 10450
        )

    def test_sqout_late_chopsuey(self):
        self._test_activations(
            "sqout_late_chopsuey.mid",
            [
                (5, "m43.1.0"),
                (0, "m73.1.0"),
                (2, "m105.1.0")
            ]
        )

    def test_path_wtd(self):
        self._test_pathstr("wtd.chart", "1 1 E5")
        
    def test_path_chopsuey(self):
        self._test_pathstr("sqout_late_chopsuey.mid", "5 0 2")
