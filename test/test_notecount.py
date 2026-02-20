import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestNoteCount(unittest.TestCase):
    """Test cases for average multiplier."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_notecount"])
    
    def _test_notecount(self, chartname, notecount):
        chartpath = self.chartfolder + os.sep + chartname
        path = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        ).best_path()
        
        self.assertEqual(path.notecount, notecount)
    
    def test_last(self):
        self._test_notecount('last.mid', 1081)
        
    def test_wtd(self):
        self._test_notecount('wtd.chart', 2543)
        
    def test_disappointed(self):
        self._test_notecount('disappointed.mid', 2359)
        
    def test_nephele(self):
        self._test_notecount('nephele.mid', 1430)
    
    def test_vicarious(self):
        self._test_notecount('vicarious.mid', 3145)
        
    def test_sws(self):
        self._test_notecount('sws.chart', 21)
