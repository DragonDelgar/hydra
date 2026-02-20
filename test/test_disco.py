import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestDisco(unittest.TestCase):
    """Disco flip stuff."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_disco"])
    
    def _test_totalscore(self, chartname, score):
        chartpath = self.chartfolder + os.sep + chartname
        record = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', 4
        )
        
        self.assertEqual(record.best_path().totalscore(), score)
    
    
    def test_disco_cymbals_chart(self):
        self._test_totalscore("disco_cymbals.chart", 490)
        
    def test_disco_toms_chart(self):
        self._test_totalscore("disco_toms.chart", 490)
        
    def test_disco_cymbals_mid(self):
        self._test_totalscore("disco_cymbals.mid", 490)
        
    def test_disco_toms_mid(self):
        self._test_totalscore("disco_toms.mid", 490)