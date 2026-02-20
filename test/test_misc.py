import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestMisc(unittest.TestCase):
    """Cement any problem songs as regression tests when their problems get fixed."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_misc"])
    
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
        
    def test_path_hellabove(self):
        self._test_pathstr("hellabove.mid", "1 2")
        
    def test_path_arithmophobia(self):
        self._test_pathstr("arithmophobia.mid", "5 9+ 0")

    def test_score_lune(self):
        self._test_optimal("lune.mid", 434350)
        
    def test_score_deathking(self):
        self._test_optimal("deathking.mid", 261200, geq=True)

    def test_score_flamesbut(self):
        self._test_optimal("flamesbut.mid", 216775, geq=True)