import sys
import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata

class TestSB25Filter(unittest.TestCase):
    """Regression tests for active tourney setlist. For ms filter."""
    def setUp(self):
        self.chartfolder = os.sep.join(["..","test","input","test_sb25"])
    
    def _path_passes_filter(self, path, ms_filter):
        # ms_filter is the hardest allowed ms.
        # The higher the ms_filter, the more is allowed.
        # "ms_filter == infinity" is equivalent to ms_filter is None.
        for act in path.all_activations():
            # e offset: negative is harder
            if act.is_E0() and -act.e_offset > ms_filter:
                return False
            
            for sqinout in act.sqinouts:
                if sqinout.difficulty > ms_filter:
                    return False
                
        return True
        
    def _record_contains_path(self, record, path):
        # Path strings are sufficient in this context (known to be same chart)
        return any(p.pathstring() == path.pathstring() for p in record.all_paths())
    
    def _test_filter(self, chartname):
        
        full_record = hyutil.analyze_chart_file(
            self.chartfolder + os.sep + chartname,
            'expert', True, True,
            'scores', 500,
            None
        )
        
        for i, ms_filter in enumerate(range(-200, 205, 50)):
            with self.subTest(i=i):
                filter_depth = 5
                
                filter_record = hyutil.analyze_chart_file(
                    self.chartfolder + os.sep + chartname,
                    'expert', True, True,
                    'scores', filter_depth,
                    ms_filter
                )
                
                # First path (top score) is unchanged by filtering
                best_score = full_record.best_path().totalscore()
                full_opts = list(filter(lambda x: x.totalscore() == best_score, full_record.all_paths()))
                filt_opts = list(filter(lambda x: x.totalscore() == best_score, filter_record.all_paths()))
                self.assertEqual(len(full_opts), len(filt_opts))
                for i in range(len(full_opts)):
                    self.assertEqual(full_opts[i].pathstring(), filt_opts[i].pathstring())
                
                # Tracing through the full record in order and collecting paths
                # that pass the filter recreates the filter record
                filter_paths = list(filter_record.all_paths())
                filter_i = len(full_opts)
                lastscore = filter_record.best_path().totalscore()
                scorelevel = 0
                for p in list(full_record.all_paths())[len(full_opts):]:
                    if p.passes_ms_filter(ms_filter):
                        if p.totalscore() != lastscore:
                            self.assertLess(p.totalscore(), lastscore)
                            scorelevel += 1
                            lastscore = p.totalscore()
                        if filter_i == len(filter_paths):
                            # Done with filter list. Check that further
                            # paths that pass the filter aren't supposed to be
                            # in the filter record's depth range
                            self.assertLess(filter_depth, scorelevel)
                        else:
                            if p.pathstring() != filter_paths[filter_i].pathstring():
                                print(f"Records:")
                                fps = list(full_record.all_paths())
                                flps = list(filter_record.all_paths())
                                for i in range(len(fps)):
                                    fp = fps[i]
                                    sout = f"\t{fp.totalscore()}, {fp.difficulty()} ms: {fp.pathstring()}"
                                    
                                    if i < len(flps):
                                        flp = flps[i]
                                        sout += f"\t\t\t{flp.totalscore()}, {flp.difficulty()} ms: {flp.pathstring()}"
                                        
                                    print(sout)
                            self.assertEqual(p.pathstring(), filter_paths[filter_i].pathstring())
                            filter_i += 1

                
                # Verify the filter record was traced through fully
                self.assertEqual(filter_i, len(filter_paths))


    # T1
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_howyouremindme(self):
        self._test_filter("howyouremindme.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_actors(self):
        self._test_filter("actors.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_pokemontheme(self):
        self._test_filter("pokemontheme.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_totheend(self):
        self._test_filter("totheend.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_aprilhaha(self):
        self._test_filter("aprilhaha.chart")
        
    # T2
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_lunaris(self):
        self._test_filter("lunaris.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_cityofocala(self):
        self._test_filter("cityofocala.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_youngrobot(self):
        self._test_filter("youngrobot.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_limbo(self):
        self._test_filter("limbo.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_avalanche(self):
        self._test_filter("avalanche.mid")
        
    # T3
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_snakeskinboots(self):
        self._test_filter("snakeskinboots.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_movealong(self):
        self._test_filter("movealong.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_wastingtime(self):
        self._test_filter("wastingtime.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_overture1928(self):
        self._test_filter("overture1928.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_allies(self):
        self._test_filter("allies.chart")
        
    # T4
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_yyz(self):
        self._test_filter("yyz.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_burnout(self):
        self._test_filter("burnout.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_limbfromlimb(self):
        self._test_filter("limbfromlimb.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_chair(self):
        self._test_filter("chair.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_unbound(self):
        self._test_filter("unbound.mid")
        
    # T5
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_iamallofme(self):
        self._test_filter("iamallofme.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_pathkeeper(self):
        self._test_filter("pathkeeper.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_whitemist(self):
        self._test_filter("whitemist.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_senescence(self):
        self._test_filter("senescence.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_grow(self):
        self._test_filter("grow.chart")
        
    # T6
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_thankyoupain(self):
        self._test_filter("thankyoupain.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_87(self):
        self._test_filter("87.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_bledtobefree(self):
        self._test_filter("bledtobefree.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_swallow(self):
        self._test_filter("swallow.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_b(self):
        self._test_filter("b.mid")
        
    # T7
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_blister(self):
        self._test_filter("blister.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_focus(self):
        self._test_filter("focus.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_thespiralingvoid(self):
        self._test_filter("thespiralingvoid.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_neibolt(self):
        self._test_filter("neibolt.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_handthatrocksthecradle(self):
        self._test_filter("handthatrocksthecradle.mid")
        
    # T8
        @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_epidermis(self):
        self._test_filter("epidermis.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_godzilla(self):
        self._test_filter("godzilla.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_geturfreakon(self):
        self._test_filter("geturfreakon.chart")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_drjekyll(self):
        self._test_filter("drjekyll.mid")
            @unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
    def testpaths_alchemicwebofdeceit(self):
        self._test_filter("alchemicwebofdeceit.mid")
