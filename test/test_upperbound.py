import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong
import hydra.hypath as hypath

class TestUpperbound(unittest.TestCase):
    """Test cases for songs where the optimal path is only visible with a >140
        upper bound.
    """
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_upperbound"])
    
    def _test_optimals(self, filename, upperbound, expected_score, expected_ms):
        input_file = self.chartfolder + os.sep + filename
        default_record = hyutil.analyze_chart_file(input_file, 'Expert', True, True, 'scores', 0, None, None)
        upperbound_record = hyutil.analyze_chart_file(input_file, 'Expert', True, True, 'scores', 0, None, upperbound)
        
        self.assertLess(default_record.best_path().totalscore(), upperbound_record.best_path().totalscore())
        self.assertEqual(upperbound_record.best_path().totalscore(), expected_score)
        self.assertAlmostEqual(upperbound_record.best_path().difficulty(), expected_ms, places=2)        

    def test_dumpweed(self):
        self._test_optimals('dumpweed.mid', 190, 422940, 143.129)

    def test_maladapted(self):
        self._test_optimals('maladapted.mid', 190, 444435, 184.048)

    def test_burnout(self):
        self._test_optimals('burnout.mid', 190, 378315, 163.043)

    def test_poyw(self):
        self._test_optimals('poyw.mid', 190, 312590, 178.571)

