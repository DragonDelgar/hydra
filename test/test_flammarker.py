import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong

class TestFlamMarker(unittest.TestCase):
    """Test cases for MIDI flam marker, which in CH converts
    one-handed notes into two-handed chords using a specific mapping.
    """
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_flammarker"])
    
    def test_flammarkers(self):
        input_file = self.chartfolder + os.sep + "flammarker_authored.mid"
        expected_pro_file = self.chartfolder + os.sep + "flammarker_expected_prodrums.mid"
        expected_reg_file = self.chartfolder + os.sep + "flammarker_expected_regdrums.mid"
        
        outcome_pro = hysong.load_songpath_mid(input_file, 'expert', True, True)
        outcome_reg = hysong.load_songpath_mid(input_file, 'expert', False, True)
        
        expected_pro = hysong.load_songpath_mid(expected_pro_file, 'expert', True, True)
        expected_reg = hysong.load_songpath_mid(expected_reg_file, 'expert', False, True)
        
        # Pro
        self.assertEqual(len(outcome_pro._sequence), len(expected_pro._sequence))
        for i in range(len(outcome_pro._sequence)):
            self.assertEqual(outcome_pro._sequence[i].chord, expected_pro._sequence[i].chord, f"Pro flam conversion #{i} ({outcome_pro._sequence[i].timecode.measurestr()}).")
        
        # Reg
        self.assertEqual(len(outcome_reg._sequence), len(expected_reg._sequence))
        for i in range(len(outcome_reg._sequence)):
            self.assertEqual(outcome_reg._sequence[i].chord, expected_reg._sequence[i].chord, f"Reg flam conversion #{i} ({outcome_reg._sequence[i].timecode.measurestr()}).")

