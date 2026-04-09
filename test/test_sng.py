import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata

class TestSNG(unittest.TestCase):
    """SNG file format."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_sng"])
    
    def _test_totalscore(self, chartname, score):
        chartpath = self.chartfolder + os.sep + chartname
        record = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        )
        
        self.assertEqual(record.best_path().totalscore(), score)
    
    def best_paths(self, chartname):
        result = hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 4
        )
        
        return [p for p in result.all_paths() if p.totalscore() == result.best_path().totalscore()]
    
    def _test_pathstrs(self, chartname, s_pathstrs):
        paths = [p.pathstring() for p in self.best_paths(chartname)]
        for i, s_pathstr in enumerate(s_pathstrs):
            with self.subTest(i=i):
                self.assertTrue(s_pathstr in paths, f"{s_pathstr} not in {paths}")
    
    def test_tapped_out(self):
        self._test_totalscore("tapped_out.sng", 1022200)

    def test_paths_snakeskinboots(self):
        self._test_pathstrs("snakeskinboots.sng", ["1 E2 3+"])
    
    def test_paths_wastingtime(self):
        self._test_pathstrs("wastingtime.sng", ["3 0 0 0"])