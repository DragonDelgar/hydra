import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong
import hydra.hypath as hypath

class TestSongFeatures(unittest.TestCase):
    """Test cases for song features (analysis stuff found when parsing the song,
    not when optimizing paths).
    """
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_songfeatures"])
    
    def test_wgfa(self):
        input_file = self.chartfolder + os.sep + "wgfa.mid"
        record = hyutil.analyze_chart_file(input_file, 'Expert', True, True, 'scores', 0)
        
        self.assertTrue('Ghost kicks' in record.songfeatures)
        self.assertEqual(record.songfeatures['Ghost kicks'], 36)
