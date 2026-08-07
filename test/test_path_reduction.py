import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong

class TestPathReduction(unittest.TestCase):
    """Test cases for path reduction update. Test charts have edges cases for
    path comparison logic."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_path_reduction"])
    

    def _test_pathlist(self, input_file, depth, expected_score_tiers):
        testresult = hyutil.analyze_chart_file(self.chartfolder + os.sep + input_file, 'Expert', True, True, 'scores', depth)
        
        test_score_tiers = {}
        
        for p in testresult.all_paths():
            score = p.totalscore()
            if score not in test_score_tiers:
                test_score_tiers[score] = []
                
            test_score_tiers[score].append(p.pathstring())
            
        self.assertEqual(sorted(test_score_tiers.keys()), sorted(expected_score_tiers.keys()))
        
        for k in test_score_tiers.keys():
            self.assertEqual(sorted(test_score_tiers[k]), sorted(expected_score_tiers[k]))
    
    
    def test_0(self):
        self._test_pathlist("test0.chart", 0, {
                45450 : ["1 0 0"],
            })
            
        self._test_pathlist("test0.chart", 1, {
                45450 : ["1 0 0"],
                43150 : ["0 1"],
            })
