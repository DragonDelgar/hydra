import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hymisc as hymisc


class TestSkippedDyn(unittest.TestCase):
    """Test for skipped dynamic activation notes (which do not get hit for
    their bonus points when they get skip-autoplayed)."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_skipped_dyn"])
    
    def best_path(self, chartname):
        return hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 4
        ).best_path()
    
    def _test_pathstr(self, chartname, s_pathstr):
        path = self.best_path(chartname)
        self.assertEqual(path.pathstring(), s_pathstr)
        
    def _test_optimal(self, chartname, s_score, geq=False):
        """geq: Test passes if Hydra's optimal score is greater or equal than
        the test value. Useful if there's a best known score, but it isn't
        confirmed to be optimal."""
        path = self.best_path(chartname)
        if geq:
            self.assertGreaterEqual(path.totalscore(), s_score)
        else:
            self.assertEqual(path.totalscore(), s_score)
    
    def test_score_basic(self):
        # Erroneously counting the skipped accent: 1300
        # Correct: 1250
        if hymisc.FLAG_SKIPPED_DYNAMICS:
            self._test_optimal("basic.chart", 1250)
        else:
            self.skipTest("Feature disabled")