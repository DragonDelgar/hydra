import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestLeftoverSP(unittest.TestCase):
    """Tests the leftover SP of paths."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_leftover_sp"])
    
    def best_path(self, chartname):
        return hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 4
        ).best_path()
    
    def _test_leftover_sp(
        self, chartname, s_leftover_sp
    ):
        path = self.best_path(chartname)
        
        self.assertEqual(path.leftover_sp, s_leftover_sp)
    
    def test_bend(self):
        self._test_leftover_sp("bend.mid", 1)
        
    def test_tapped_out(self):
        self._test_leftover_sp("tappedout.mid", 0)