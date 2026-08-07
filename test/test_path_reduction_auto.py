import os
import sys
import unittest
import json

from itertools import combinations

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong

@unittest.skipIf('fast' in sys.argv, "Skipping slow tests.")
class TestPathReductionAuto(unittest.TestCase):
    """Test cases for path reduction in general. Runs charts with ms filter /
    depth settings and checks that the results match what would happen if you
    took the full path list at the end and applied the path reduction then."""
    def setUp(self):
        pass
    
    
    def _test_single(self, notespath, record_fullpaths, depth_mode, depth_value, ms_filter):
        record_reducedpaths = hyutil.analyze_chart_file(notespath, 'Expert', True, True, depth_mode, depth_value, ms_filter)
        
        # Apply path reduction to fullpaths after the fact
        expected_reducedpaths = [p for p in record_fullpaths.all_paths() if p.passes_ms_filter(ms_filter) or p.totalscore() == record_fullpaths.best_path().totalscore()]
        
        if depth_mode == 'scores':
            current_score_tier = record_reducedpaths.best_path().totalscore()
            extra_tiers_so_far = 0
            saved_paths = []
            for p in expected_reducedpaths:
                if p.totalscore() != current_score_tier:
                    current_score_tier = p.totalscore()
                    extra_tiers_so_far += 1
                    if extra_tiers_so_far > depth_value:
                        break
                saved_paths.append(p)
            
            expected_reducedpaths = saved_paths
        else:
            expected_reducedpaths = [p for p in expected_reducedpaths if p.totalscore() + depth_value >= record_reducedpaths.best_path().totalscore()]
        
        observed_reducedpaths = list(record_reducedpaths.all_paths())
        
        # Check that this matches the result of in-progress path reduction
        self.assertEqual(len(observed_reducedpaths), len(expected_reducedpaths))
        
        for i, p in enumerate(observed_reducedpaths):
            self.assertEqual(p.totalscore(), expected_reducedpaths[i].totalscore())
            self.assertEqual(p.pathstring(), expected_reducedpaths[i].pathstring())
    
    
    # test space: ['points'/'scores'] x [depth value increments] x [ms_filter increments or None]
    def _test_notespath(self, notespath, fulldepth=200):
        self._check_all(notespath, fulldepth)
    
    
    def _check_all(self, notespath, fulldepth):
        record_fullpaths = hyutil.analyze_chart_file(notespath, 'Expert', True, True, 'scores', fulldepth, None)
        for (depth_mode, depth_value_increment, depth_value_totalsteps) in [('scores', 1, 20), ('points', 100, 5)]:
            for depth_value_step in range(depth_value_totalsteps):
                depth_value = depth_value_increment * depth_value_step
                
                with self.subTest(f"{notespath} | {depth_value} {depth_mode}"):
                    self._test_single(notespath, record_fullpaths, depth_mode, depth_value, None)
                
                for ms_filter in range(-50, 110, 25):
                    with self.subTest(f"{notespath} | {depth_value} {depth_mode} | {ms_filter} ms"):
                        self._test_single(notespath, record_fullpaths, depth_mode, depth_value, ms_filter)
    
    def test_Xane60(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Xane60 - Godzilla (Eminem)\\notes.chart")
    def test_Venetian(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Venetian Snares - Epidermis\\notes.mid")
    def test_Travis(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Travis Orbin - Dr. Jackle_Dr. Jekyll [Miles Davis]\\notes.mid")
    def test_Eric(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Eric Moore - Get Ur Freak On [Missy Elliot]\\notes.chart")
    def test_Equipoise(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Equipoise - Alchemic Web Of Deceit\\notes.mid")
    def test_The(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\The Faceless - The Spiraling Void\\notes.chart")
    def test_Synovial(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\Synovial - Neibolt\\notes.mid")
    def test_SoundHaven(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\SoundHaven - Focus [Ariana Grande]\\notes.mid")
    def test_Kinglet(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\Kinglet - Blister\\notes.mid")
    def test_Hella(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\Hella - Hand That Rocks the Cradle\\notes.mid")
    def test_The(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\The Agonist - Thank You, Pain\\notes.chart")
    def test_RX(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\RX Bandits - Bled to Be Free (The Operation)\\notes.chart")
    def test_Polyphia(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\Polyphia - 87\\notes.chart")
    def test_Casiopea(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\Casiopea - Swallow\\notes.mid")
    def test_Between(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\Between the Buried and Me - (B) The Decade Of Statues\\notes.mid")
    def test_Victoria(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Victoria - Grow\\notes.chart")
    def test_Interloper(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Interloper - Pathkeeper\\notes.mid")
    def test_HopH2O(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\HopH2O - I Am... All Of Me (Crush 40)\\notes.mid")
    def test_Gavin(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Gavin Harrison - White Mist [The Pineapple Thief]\\notes.mid")
    def test_Chaotrope(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Chaotrope - Senescence (shortened)\\notes.chart")
    def test_Sufferer(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Sufferer - Chair\\notes.mid")
    def test_Rush(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Rush - YYZ\\notes.mid")
    def test_Protest(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Protest the Hero - Limb From Limb\\notes.chart")
    def test_Green(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Green Day - Burnout\\notes.mid")
    def test_Avenged(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Avenged Sevenfold - Unbound (The Wild Ride)\\notes.mid")
    def test_The(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\The All-American Rejects - Move Along\\notes.mid")
    def test_Mutemath(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Mutemath - Allies\\notes.chart")
    def test_Jack(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Jack Wall - Snakeskin Boots [highfine]\\notes.chart")
    def test_Four(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Four Year Strong - Wasting Time (Eternal Summer)\\notes.mid")
    def test_Dream(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Dream Theater - Overture 1928\\notes.chart")
    def test_Thornhill(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Thornhill - Limbo\\notes.mid")
    def test_Moonlight(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Moonlight Haze - Lunaris\\notes.chart")
    def test_Matt(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Matt McGuire - Avalanche [Bring Me The Horizon]\\notes.mid")
    def test_Dance(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Dance Gavin Dance - Young Robot\\notes.mid")
    def test_A(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\A Day to Remember - City Of Ocala\\notes.mid")
    def test_Nothing(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Nothing - April Ha Ha [tomato]\\notes.chart")
    def test_Nickelback(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Nickelback - How You Remind Me\\notes.chart")
    def test_My(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\My Chemical Romance - To the End\\notes.mid")
    def test_Jason(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Jason Paige - Pokemon Theme\\notes.chart")
    def test_Don(self):
        self._test_notespath("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Don Broco - Actors\\notes.mid")
    def test_Yoink(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Yoink - Spirit Bomb [GanonMetroid]\\notes.mid")
    def test_Xane60(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Xane60 & SoundHaven - Bug Thief [Iglooghost]\\notes.chart")
    def test_SoundHaven(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\SoundHaven - Snowball Earth [Indistinct]\\notes.mid")
    def test_Necrophagist(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Necrophagist - Stabwound\\notes.chart")
    def test_Ne(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Ne Obliviscaris - Tapestry of the Starless Abstract (Shortened)\\notes.mid")
    def test_Mahavishnu(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Mahavishnu Orchestra - Awakening\\notes.mid")
    def test_DOMi(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\DOMi & JD Beck - Zildjian LIVE! Performance 2020\\notes.mid")
    def test_Conquering(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Conquering Dystopia - Prelude to Obliteration\\notes.chart")
    def test_Car(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T7\\Car Bomb - The Sentinel\\notes.mid")
    def test_Senri(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Senri Kawaguchi - Ladies Talk [Kiyo Sen] (Drumeo Performance)\\notes.mid")
    def test_Pathfinder(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Pathfinder - When The Sunrise Breaks The Darkness\\notes.mid")
    def test_Lockslip(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Lockslip - Lockslip - 02 - Bend\\notes.mid")
    def test_Lightning(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Lightning Bolt - Dream Genie\\notes.mid")
    def test_Levitating(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Levitating (feat. DaBaby) (Dua Lipa) (L)\\notes.chart")
    def test_HopH2O(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\HopH2O - Nasty (Tinashe)\\notes.mid")
    def test_Hannes(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Hannes Grossmann - Vacant Dreams\\notes.mid")
    def test_Fallen(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\Fallen Monarch - Blight\\notes.chart")
    def test_black(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T6\\black midi - Sugar／Tzu (Smoochums, Vasasasasa)\\notes.mid")
    def test_TEXTURES(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\TEXTURES - Laments Of An Icarus\\notes.mid")
    def test_Symphony(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Symphony X - Set the World on Fire\\notes.chart")
    def test_Sianvar(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Sianvar - Omniphobia\\notes.mid")
    def test_Satyr(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Satyr - Whelmed\\notes.mid")
    def test_Mike(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Mike Orlando - Tapped Out\\notes.mid")
    def test_Meshuggah(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Meshuggah - Nostrum\\notes.mid")
    def test_Mastodon(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Mastodon - Megalodon\\notes.chart")
    def test_Brandon(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\Brandon Burkhalter - Someday\\notes.mid")
    def test_August(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T5\\August Burns Red - White Washed\\notes.mid")
    def test_Tesseract(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\Tesseract - Deception - Concealing Fate, Pt. 2\\notes.mid")
    def test_sungazer(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\sungazer - All These People\\notes.mid")
    def test_Phish(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\Phish - Llama\\notes.mid")
    def test_Haken(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\Haken - The Good Doctor\\notes.mid")
    def test_Hail(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\Hail The Sun - Missed Injections\\notes.mid")
    def test_Foo(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\Foo Fighters - Everlong\\notes.mid")
    def test_Dance(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\Dance Gavin Dance - Chocolate Jackalope\\notes.mid")
    def test_A(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\A Lot Like Birds - Think Dirty out Loud\\notes.mid")
    def test_1OM(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T4\\1.O.M. - Apex\\notes.chart")
    def test_Trivium(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\Trivium - Feast of Fire\\notes.mid")
    def test_Thrice(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\Thrice - Deadbolt\\notes.mid")
    def test_The(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\The Ghost Inside - Get What You Give - 02 - Outlive\\notes.mid")
    def test_Neck(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\Neck Deep - Beautiful Madness\\notes.mid")
    def test_Good(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\Good Tiger - Where Are the Birds\\notes.chart")
    def test_CHON(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\CHON - Book (feat. Matt Garstka)\\notes.mid")
    def test_Alpha(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T3\\Alpha Wolf - Acid Romance\\notes.mid")
    def test_The(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\The Fall of Troy - Act One, Scene One [highfine]\\notes.chart", fulldepth=400)
    def test_Stone(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\Stone Temple Pilots - Trippin on a Hole in a Paper Heart\\notes.chart")
    def test_Nova(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\Nova Charisma - The Greater Cause\\notes.mid")
    def test_Mayday(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\Mayday Parade - Jamie All Over\\notes.mid")
    def test_Karnivool(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\Karnivool - Themata\\notes.mid")
    def test_fanclubwallet(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\fanclubwallet - Band Like That\\notes.mid")
    def test_Area(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T2\\Area 11 - Knightmare Frame\\notes.mid")
    def test_Tigran(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Tigran Hamasyan - Entertain Me [tomato]\\notes.chart")
    def test_Smash(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Smash Mouth - I_m A Believer (The Monkees cover) [highfine]\\notes.chart")
    def test_Hawthorne(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Hawthorne Heights - Saying Sorry\\notes.mid")
    def test_Evans(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Evans Blue - Beg [highfine]\\notes.chart")
    def test_Earth(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Earth, Wind & Fire - September\\notes.mid")
    def test_Deftones(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Deftones - My Own Summer (Shove It) [highfine]\\notes.chart")
    def test_Allister(self):
        self._test_notespath("..\\test\\input\\common\\IB24\\T1\\Allister - Overrated\\notes.mid")