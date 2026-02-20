import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestAverageMultiplier(unittest.TestCase):
    """Test cases for average multiplier."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_avg_mult"])
    
    def _test_avg_mult(self, chartname, avgmult):
        chartpath = self.chartfolder + os.sep + chartname
        path = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        ).best_path()
        
        self.assertEqual(str(path.avg_mult())[:5], avgmult)
    
    def test_last(self):
        self._test_avg_mult('last.mid', "3.921")
        
    def test_wtd(self):
        self._test_avg_mult('wtd.chart', "4.937")
        
    def test_disappointed(self):
        self._test_avg_mult('disappointed.mid', "5.622")
        
    def test_nephele(self):
        self._test_avg_mult('nephele.mid', "3.963")
    
    def test_vicarious(self):
        self._test_avg_mult('vicarious.mid', "5.054")
        
    def test_sws(self):
        self._test_avg_mult('sws.chart', "2.666")
