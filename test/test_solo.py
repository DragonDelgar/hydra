import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestSolo(unittest.TestCase):
    """Test the solo points category."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_solo"])
    
    def _test_solo(self, chartname, s_solo):
        chartpath = self.chartfolder + os.sep + chartname
        path = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        ).best_path()
        
        self.assertEqual(path.score_solo, s_solo)
    
    def test_as_I_am(self):
        self._test_solo("asiam.mid", 14700)
        
    def test_lalala(self):
        self._test_solo("lalala.mid", 15100)
        
    def test_burnout(self):
        self._test_solo("burnout.mid", 11800)
        
    def test_the_good_doctor(self):
        self._test_solo("thegooddoctor.mid", 8600)
        
    def test_in_three_ways(self):
        self._test_solo("inthreeways.mid", 50100)
        
    def test_tapped_out(self):
        self._test_solo("tappedout.mid", 14000)
        
    def test_solo_both_edges(self):
        self._test_solo("both_edges.chart", 500)
        
    def test_solo_ending_edge(self):
        self._test_solo("ending_edge.chart", 400)
        
    def test_solo_no_edges(self):
        self._test_solo("no_edges.chart", 300)
        
    def test_solo_no_notes(self):
        self._test_solo("no_notes.chart", 0)
        
    def test_solo_starting_edge(self):
        self._test_solo("starting_edge.chart", 400)
