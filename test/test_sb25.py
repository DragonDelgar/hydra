import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata

class TestSB25(unittest.TestCase):
    """Regression tests for active tourney setlist."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_sb25"])
    
    def best_paths(self, chartname):
        result = hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 4
        )
        
        return [p for p in result.all_paths() if p.totalscore() == result.best_path().totalscore()]
    
    def _test_pathstrs(self, chartname, s_pathstrs):
        paths = [p.pathstring() for p in self.best_paths(chartname)]
        for i, s_pathstr in enumerate(s_pathstrs):
            with self.subTest(i=i):
                self.assertTrue(s_pathstr in paths, f"{s_pathstr} not in {paths}")
    
    # T1
    
    def test_paths_howyouremindme(self):
        self._test_pathstrs("howyouremindme.chart", ["0 1 1"])
        
    def test_paths_actors(self):
        self._test_pathstrs("actors.mid", ["4 1"])
        
    def test_paths_pokemontheme(self):
        self._test_pathstrs("pokemontheme.chart", ["(No activations.)"])
        
    def test_paths_totheend(self):
        self._test_pathstrs("totheend.mid", ["E2 2 0"])
        
    def test_paths_aprilhaha(self):
        self._test_pathstrs("aprilhaha.chart", ["0 2 1"])
        
    # T2
    
    def test_paths_lunaris(self):
        self._test_pathstrs("lunaris.chart", ["(No activations.)"])
        
    def test_paths_cityofocala(self):
        self._test_pathstrs("cityofocala.mid", ["2 2 0"])
        
    def test_paths_youngrobot(self):
        self._test_pathstrs("youngrobot.mid", ["(No activations.)"])
        
    def test_paths_limbo(self):
        self._test_pathstrs("limbo.mid", ["(No activations.)"])
        
    def test_paths_avalanche(self):
        self._test_pathstrs("avalanche.mid", ["0 0 2+ 4 0"])
        
    # T3
    
    def test_paths_snakeskinboots(self):
        self._test_pathstrs("snakeskinboots.chart", ["1 E2 3+"])
        
    def test_paths_movealong(self):
        self._test_pathstrs("movealong.mid", ["0 1 0 0"])
        
    def test_paths_wastingtime(self):
        self._test_pathstrs("wastingtime.mid", ["3 0 0 0"])
        
    def test_paths_overture1928(self):
        self._test_pathstrs("overture1928.chart", ["(No activations.)"])
        
    def test_paths_allies(self):
        self._test_pathstrs("allies.chart", ["0 1 1 0"])
        
    # T4
    
    def test_paths_yyz(self):
        self._test_pathstrs("yyz.mid", ["0 4 1 4"])
        
    def test_paths_burnout(self):
        self._test_pathstrs("burnout.mid", ["0 4 0"])
        
    def test_paths_limbfromlimb(self):
        self._test_pathstrs("limbfromlimb.chart", ["0 2 1 0 E2 0 0"])
        
    def test_paths_chair(self):
        self._test_pathstrs("chair.mid", ["(No activations.)"])
        
    def test_paths_unbound(self):
        self._test_pathstrs("unbound.mid", ["2 2+ 0 2"])
        
    # T5
    
    def test_paths_iamallofme(self):
        self._test_pathstrs("iamallofme.mid", ["0+ 2 0 0- 2 E0", "3 E0 3 2 E0"])
        
    def test_paths_pathkeeper(self):
        self._test_pathstrs("pathkeeper.mid", ["(No activations.)"])
        
    def test_paths_whitemist(self):
        self._test_pathstrs("whitemist.mid", ["3 5+ 0 1"])
        
    def test_paths_senescence(self):
        self._test_pathstrs("senescence.chart", ["0 0 0 3- 0 0+"])
        
    def test_paths_grow(self):
        self._test_pathstrs("grow.chart", ["7- 1 4"])
        
    # T6
    
    def test_paths_thankyoupain(self):
        self._test_pathstrs("thankyoupain.chart", ["2 0 0 2"])
        
    def test_paths_87(self):
        self._test_pathstrs("87.chart", ["E3 0 E2"])
        
    def test_paths_bledtobefree(self):
        self._test_pathstrs("bledtobefree.mid", ["2 1 0 5 1"])
        
    def test_paths_swallow(self):
        self._test_pathstrs("swallow.mid", ["(No activations.)"])
        
    def test_paths_b(self):
        self._test_pathstrs("b.mid", ["0 4 4 0 E2 1"])
        
    # T7
    
    def test_paths_blister(self):
        self._test_pathstrs("blister.mid", ["(No activations.)"])
        
    def test_paths_focus(self):
        self._test_pathstrs("focus.mid", ["0 E3+ E0 0"])
        
    def test_paths_thespiralingvoid(self):
        self._test_pathstrs("thespiralingvoid.chart", ["0 0 1 3 E4+ 0+ 0 0 0 0"])
        
    def test_paths_neibolt(self):
        self._test_pathstrs("neibolt.mid", ["2 0 0 2 2 2 0"])
        
    def test_paths_handthatrocksthecradle(self):
        self._test_pathstrs("handthatrocksthecradle.mid", ["7 4 E3"])
        
    # T8
    
    def test_paths_epidermis(self):
        self._test_pathstrs("epidermis.mid", ["0 1 0 2"])
        
    def test_paths_godzilla(self):
        self._test_pathstrs("godzilla.chart", ["(No activations.)"])
        
    def test_paths_geturfreakon(self):
        self._test_pathstrs("geturfreakon.chart", ["5- 2+ E2- E0 E0"])
        
    def test_paths_drjekyll(self):
        self._test_pathstrs("drjekyll.mid", ["(No activations.)"])
        
    def test_paths_alchemicwebofdeceit(self):
        self._test_pathstrs("alchemicwebofdeceit.mid", ["(No activations.)"])
