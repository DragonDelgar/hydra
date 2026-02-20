import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestE(unittest.TestCase):
    """Tests for E."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_e"])
    
    def best_path(self, chartname):
        return hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 4
        ).best_path()
    
    def _test_e_value(self, chartname, s_ms, act_index=0):
        path = self.best_path(chartname)
        self.assertAlmostEqual(path.get_activation(act_index).e_offset, s_ms, places=5)
        
    def _test_no_e(self, chartname, act_index=0):
        path = self.best_path(chartname)
        self.assertFalse(path.get_activation(act_index).is_e_critical())
    
    def test_e_70bpm(self):
        self._test_e_value("70bpm.chart", -3750/70)
        
    def test_e_100bpm(self):
        self._test_e_value("100bpm.chart", -37.5)
        
    def test_e_140bpm(self):
        self._test_e_value("140bpm.chart", -3750/140)
        
    def test_e_240bpm(self):
        self._test_e_value("240bpm.chart", -15.625)
        
    def test_e_400bpm(self):
        self._test_e_value("400bpm.chart", -9.375)

    def test_e_obfuscation(self):
        self._test_e_value("obfuscation.mid", -25.0, act_index=1)
        
    def test_e_oppressor(self):
        self._test_no_e("oppressor.mid")