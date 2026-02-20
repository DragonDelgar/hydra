import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestScoring(unittest.TestCase):
    """Test that the score breakdowns match between the test solution and
    the test input freshly analyzed.
    
    Any chart + score can be added as a test as long as the score is pretty
    confidently optimal AND the Clone Hero score breakdown for that optimal
    run is known.
    
    """
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_scoring"])
    
    def _test_scoring(
        self, chartname,
        s_base, s_combo, s_sp, s_solo, s_accents, s_ghosts, s_total
    ):
        chartpath = self.chartfolder + os.sep + chartname
        path = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        ).best_path()
        
        self.assertEqual(path.score_base, s_base)
        self.assertEqual(path.score_combo, s_combo)
        self.assertEqual(path.score_sp, s_sp)
        self.assertEqual(path.score_solo, s_solo)
        self.assertEqual(path.score_accents, s_accents)
        self.assertEqual(path.score_ghosts, s_ghosts)
        
        self.assertEqual(path.totalscore(), s_total)
        
    def test_missed_injections(self):
        self._test_scoring(
            "mi.mid",
            111235, 350730, 61360, 0, 3250, 3500, 530075
        )
    
    def test_entertain_me(self):
        self._test_scoring(
            "em.chart",
            55390, 168600, 61280, 0, 250, 1650, 287170
        )
        
    def test_think_dirty_out_loud(self):
        self._test_scoring(
            "tdol.mid",
            122130, 417855, 0, 0, 3250, 14900, 558135
        )

    def test_book(self):
        self._test_scoring(
            "book.mid",
            64790, 223075, 84300, 0, 0, 10700, 382865
        )
        
    def test_all_these_people(self):
        self._test_scoring(
            "atp.mid",
            101845, 344510, 153540, 0, 2550, 11750, 614195
        )
