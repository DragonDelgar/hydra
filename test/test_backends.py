import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong
import hydra.hypath as hypath

class TestBackends(unittest.TestCase):
    """Test cases for backends.
    """
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_backends"])
    
    def test_maladapted(self):
        input_file = self.chartfolder + os.sep + "maladapted.mid"
        song = hysong.load_songpath_mid(input_file, 'expert', True, True)
        graph = hypath.ScoreGraph(song)
        
        end_nodes = []
        
        to_visit = [graph.start]
        visited = []
        while to_visit:
            visiting = to_visit.pop()
            visited.append(visiting)
            
            if visiting.adv_edge is None and visiting.branch_edge is None:
                end_nodes.append(visiting)
            
            if visiting.is_sp and visiting.branch_edge is not None and visiting.branch_edge.dest.timecode == 301440:
                self.assertEqual(len(visiting.branch_edge.backends), 1)
                self.assertEqual(visiting.branch_edge.backends[0].chord.rowstr(), "[Kick - Red - GreenCym]")
                
            if visiting.adv_edge and visiting.adv_edge.dest not in visited:
                to_visit.append(visiting.adv_edge.dest)
            if visiting.branch_edge and visiting.branch_edge.dest not in visited:
                to_visit.append(visiting.branch_edge.dest)
        
        self.assertEqual(len(end_nodes), 1)
        self.assertFalse(end_nodes[0].is_sp)
