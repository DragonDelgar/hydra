import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata


class TestPathCount(unittest.TestCase):
    """Test cases for path counts."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_pathcount"])
    
    def _test_pathcount(self, chartname, depth, pathcount):
        chartpath = self.chartfolder + os.sep + chartname
        r = hyutil.analyze_chart_file(
            chartpath,
            'expert', True, True,
            'scores', depth
        )
        
        self.assertEqual(sum(1 for p in r.all_paths()), pathcount)
    
    def test_album(self):
        self._test_pathcount('album.mid', 10, 704)
