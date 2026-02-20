import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestActMisalign(unittest.TestCase):
    """Test cases for Clone Hero's activation phrase misalignment fixing:
    An activation phrase typically "falls back" to find its activation chord
    if there isn't a chord exactly at the phrase's end, but it can actually
    also "fall forward" up to 6 ticks.
    
    If both are possible, the closer one is used.
    If there's a tie, the ahead note takes precedence.
    """
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_act_misalign"])
    
    def _test_activation_note(self, chartname, has_green):
        chartpath = self.chartfolder + os.sep + chartname
        record = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        )
        act_chord = record.best_path().get_activation(0).chord
        self.assertEqual(act_chord[hydata.NoteColor.GREEN] is not None, has_green)
    
    
    def test_control(self):
        self._test_activation_note("control.chart", True)
        
    def test_6t(self):
        self._test_activation_note("-6t.chart", True)
    
    def test_7t(self):
        self._test_activation_note("-7t.chart", False)
    
    def test_89t(self):
        self._test_activation_note("+89t.chart", True)
    
    def test_90t(self):
        self._test_activation_note("+90t.chart", False)
    
    def test_fast_6t(self):
        self._test_activation_note("fast -6t.chart", True)
    
    def test_fast_7t(self):
        self._test_activation_note("fast -7t.chart", False)
    
    def test_short_6t(self):
        self._test_activation_note("short -6t.chart", True)
    
    def test_short_7t(self):
        self._test_activation_note("short -7t.chart", False)
    
    def test_timesig_6t(self):
        self._test_activation_note("timesig -6t.chart", True)
    
    def test_timesig_7t(self):
        self._test_activation_note("timesig -7t.chart", False)
    
    def test_tie(self):
        self._test_activation_note("6t tie.chart", True)
    
    def test_pre_closer(self):
        self._test_activation_note("4t pre closer.chart", False)
    
    def test_post_closer(self):
        self._test_activation_note("4t post closer.chart", True)
    
    def test_control_midi(self):
        self._test_activation_note("control.mid", True)
       
    def test_15_480_midi(self):
        self._test_activation_note("-15 480t.mid", True)
        
    def test_16_480_midi(self):
        self._test_activation_note("-16 480t.mid", False)
        
    def test_30_960_midi(self):
        self._test_activation_note("-30 960t.mid", True)
        
    def test_31_960_midi(self):
        self._test_activation_note("-31 960t.mid", False)
