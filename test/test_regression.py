import os
import unittest
import json

import hydra.hyutil as hyutil
import hydra.hydata as hydata
import hydra.hysong as hysong

class TestRegression(unittest.TestCase):
    """Test cases for existing path results before implementing a change.
    """
    def setUp(self):
        pass
    

    def _test_pathlist(self, input_file, depth, expected_score_tiers):
        testresult = hyutil.analyze_chart_file(input_file, 'Expert', True, True, 'scores', depth)
        
        test_score_tiers = {}
        
        for p in testresult.all_paths():
            score = p.totalscore()
            if score not in test_score_tiers:
                test_score_tiers[score] = []
                
            test_score_tiers[score].append(p.pathstring())
            
        self.assertEqual(sorted(test_score_tiers.keys()), sorted(expected_score_tiers.keys()))
        
        for k in test_score_tiers.keys():
            self.assertEqual(sorted(test_score_tiers[k]), sorted(expected_score_tiers[k]))
    
    
    def test_0(self): # Xane60 - Godzilla (Eminem)
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Xane60 - Godzilla (Eminem)\\notes.chart", 10, {
                558370 : ["(No activations.)"],
            })

    def test_1(self): # Venetian Snares - Epidermis
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Venetian Snares - Epidermis\\notes.mid", 10, {
                717330 : ["0 1 0 2"],
                715510 : ["1 1 0 2"],
                714570 : ["0 1 0 0 2"],
                714090 : ["2 0 0 2"],
                713790 : ["0 1 1 1"],
                713130 : ["0 1 0 0 1"],
                712750 : ["1 1 0 0 2"],
                712730 : ["0 1 0 0 0"],
                712570 : ["0 2 0 2"],
                712450 : ["0 0 0 0 2"],
                712430 : ["0 1 0 0 3"],
            })

    def test_2(self): # Travis Orbin - Dr. Jackle/Dr. Jekyll [Miles Davis]
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Travis Orbin - Dr. Jackle_Dr. Jekyll [Miles Davis]\\notes.mid", 10, {
                1235885 : ["(No activations.)"],
            })

    def test_3(self): # Eric Moore - Get Ur Freak On [Missy Elliot]
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Eric Moore - Get Ur Freak On [Missy Elliot]\\notes.chart", 10, {
                531685 : ["5- 2+ 2- 0 0"],
                530945 : ["5- 3 2- 0 0"],
                530325 : ["5+ 2- 2- 0 0"],
                529925 : ["0 1 2+ 2- 0 0"],
                529905 : ["5+ 2+ 0 0 0"],
                529585 : ["5+ 1 2- 0 0"],
                529345 : ["5- 2- 3 0 0"],
                529185 : ["5+ 0 3 0 0", "0 1 3 2- 0 0"],
                528725 : ["5- 2+ 4 0"],
                528525 : ["5+ 3 0 0 0"],
                528285 : ["5- 4 0 0 0"],
            })

    def test_4(self): # Equipoise - Alchemic Web Of Deceit
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 8\\Equipoise - Alchemic Web Of Deceit\\notes.mid", 10, {
                618425 : ["(No activations.)"],
            })

    def test_5(self): # The Faceless - The Spiraling Void
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\The Faceless - The Spiraling Void\\notes.chart", 10, {
                1145595 : ["0 0 1 3 4+ 0+ 0 0 0 0"],
                1145215 : ["0 0 1 3 4+ 1 0 0 2"],
                1144575 : ["0 0 1 3 4+ 0+ 0 0 0 2"],
                1144175 : ["3 1 3 4+ 0+ 0 0 0 0"],
                1143795 : ["3 1 3 4+ 1 0 0 2"],
                1143475 : ["0 0 1 3 4+ 1 1 0 0"],
                1143435 : ["2 1 3 4+ 0+ 0 0 0 0"],
                1143215 : ["1 3 3 4+ 0+ 0 0 0 0"],
                1143155 : ["3 1 3 4+ 0+ 0 0 0 2"],
                1143055 : ["2 1 3 4+ 1 0 0 2", "0 0 1 3 4+ 1 0 0 0"],
                1142835 : ["1 3 3 4+ 1 0 0 2"],
            })

    def test_6(self): # Synovial - Neibolt
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\Synovial - Neibolt\\notes.mid", 10, {
                903195 : ["2 0 0 2 2 2 0"],
                902515 : ["2 0 0 2 2 2 1"],
                900655 : ["2 3 2 2 2 0"],
                900055 : ["3 1 2 2 2 0"],
                899975 : ["2 3 2 2 2 1"],
                899575 : ["2 0 0 2 1 0 0 0"],
                899555 : ["2 0 0 2 1 4 0"],
                899375 : ["3 1 2 2 2 1"],
                898895 : ["2 0 0 2 1 0 0 1"],
                898875 : ["2 0 0 2 1 4 1"],
                898655 : ["2 0 0 2 1 2+ 1"],
            })

    def test_7(self): # <color=#344ceb>Sound</color>Haven - Focus [Ariana Grande]
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\SoundHaven - Focus [Ariana Grande]\\notes.mid", 10, {
                755530 : ["0 3+ 0 0"],
                754950 : ["0 3- 0 0 0"],
                754310 : ["0 2 0 0 0"],
                754230 : ["0 0 1+ 0 0"],
                753990 : ["0 0 0 0 0 0"],
                753190 : ["0 0 1- 0 0 0"],
                752790 : ["0 3- 1 0"],
                752150 : ["0 2 1 0"],
                751950 : ["1- 1 0 0 0"],
                751830 : ["0 0 0 1 0"],
                751350 : ["1+ 1+ 0 0"],
            })

    def test_8(self): # Kinglet - Blister
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\Kinglet - Blister\\notes.mid", 10, {
                549810 : ["(No activations.)"],
            })

    def test_9(self): # Hella - Hand That Rocks the Cradle
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 7\\Hella - Hand That Rocks the Cradle\\notes.mid", 10, {
                594265 : ["7 4 2"],
                593785 : ["7 4 1"],
                593545 : ["6 4 2"],
                593505 : ["8 4 2"],
                593205 : ["9 4 2"],
                593065 : ["6 4 1"],
                593025 : ["8 4 1"],
                592725 : ["9 4 1"],
                592545 : ["7 4 0"],
                592265 : ["0 3 2 2"],
                592165 : ["2 3 2 2"],
            })

    def test_10(self): # The Agonist - Thank You, Pain
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\The Agonist - Thank You, Pain\\notes.chart", 10, {
                865395 : ["2 0 0 2"],
                864935 : ["2 0 0 1"],
                859195 : ["2 0 3"],
                848195 : ["2 0 0 3"],
                845575 : ["2 0 0 0"],
                839795 : ["2 0 4"],
                838015 : ["2 0 1 1"],
                836455 : ["2 1 1"],
                835855 : ["2 0 1 0"],
                835755 : ["2 0 1 2"],
                830595 : ["2 0 0 4"],
            })

    def test_11(self): # RX Bandits - Bled to Be Free (The Operation)
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\RX Bandits - Bled to Be Free (The Operation)\\notes.chart", 10, {
                663135 : ["2 1 0 5 1"],
                662815 : ["2 1 0 0 1 1"],
                662635 : ["0 5 0 5 1"],
                662615 : ["2 1 0 1 1 1"],
                662455 : ["1 5 0 5 1"],
                662315 : ["2 1 0 0 0 1", "0 5 0 0 1 1"],
                662215 : ["2 1 0 5 2"],
                662135 : ["1 5 0 0 1 1"],
                662115 : ["2 1 0 1 0 1", "0 5 0 1 1 1"],
                662035 : ["2 1 0 2 0 1"],
                661935 : ["1 5 0 1 1 1"],
            })

    def test_12(self): # Polyphia - 87
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\Polyphia - 87\\notes.chart", 10, {
                692550 : ["3 0 2"],
                692150 : ["3 0 1"],
                690210 : ["0 3 0 0 1"],
                688950 : ["4 0 0 1"],
                688170 : ["2 3 0 0 1"],
                688050 : ["3 0 3"],
                687730 : ["0 3 0 0 0"],
                687550 : ["1 3 0 0 1"],
                686670 : ["0 3 1 2"],
                686470 : ["4 0 0 0"],
                686270 : ["0 3 1 1"],
            })

    def test_13(self): # Casiopea - Swallow
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\Casiopea - Swallow\\notes.mid", 10, {
                687100 : ["(No activations.)"],
            })

    def test_14(self): # Between the Buried and Me - (b) The Decade of Statues
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 6\\Between the Buried and Me - (B) The Decade Of Statues\\notes.mid", 10, {
                1058450 : ["0 4 4 0 1 1"],
                1056850 : ["2 3 4 0 1 1", "0 4 4 0 1 2"],
                1056190 : ["0 4 2 3 1 1"],
                1055930 : ["0 4 4 0 1 3"],
                1055610 : ["0 4 4 4 1"],
                1055570 : ["1 3 4 0 1 1"],
                1055250 : ["2 3 4 0 1 2"],
                1054750 : ["0 5 4 0 1 1"],
                1054590 : ["2 3 2 3 1 1", "0 4 2 3 1 2"],
                1054330 : ["2 3 4 0 1 3"],
                1054210 : ["2 2 4 0 1 1"],
            })

    def test_15(self): # Victoria - Grow
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Victoria - Grow\\notes.chart", 10, {
                671195 : ["7- 1 4"],
                670995 : ["7- 1 2"],
                670975 : ["7- 1 1+"],
                670675 : ["7- 1 3"],
                666655 : ["7- 2 1"],
                666535 : ["1 1- 1 4"],
                666335 : ["2- 1- 1 4", "1 1- 1 2"],
                666315 : ["1 1- 1 1+"],
                666135 : ["7- 2 0", "2- 1- 1 2"],
                666115 : ["2- 1- 1 1+"],
                666015 : ["1 1- 1 3"],
            })

    def test_16(self): # Interloper - Pathkeeper
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Interloper - Pathkeeper\\notes.mid", 10, {
                712630 : ["(No activations.)"],
            })

    def test_17(self): # HopH2O - I Am... All Of Me (Crush 40)
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\HopH2O - I Am... All Of Me (Crush 40)\\notes.mid", 10, {
                694985 : ["3 E0 3 2 E0", "0+ 2 0 0- 2 E0"],
                694885 : ["0+ 2 2 2 E0"],
                694265 : ["3 E0 1 0- 2 E0"],
                693905 : ["0- E3 3 2 E0"],
                693645 : ["0+ 1 3 2 E0"],
                693345 : ["3 E3 0- 2 E0"],
                693265 : ["0+ 2 0 0+ 3"],
                693185 : ["0- E3 1 0- 2 E0"],
                692985 : ["0- E1 E0 3 2 E0"],
                692925 : ["0+ 1 1 0- 2 E0"],
                692865 : ["0+ 2 0 0+ 0 E0"],
            })

    def test_18(self): # Gavin Harrison - White Mist [The Pineapple Thief]
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Gavin Harrison - White Mist [The Pineapple Thief]\\notes.mid", 10, {
                830560 : ["3 5+ 0 1"],
                830540 : ["4 4 0 1"],
                830120 : ["3 0 1+ 0 1"],
                829160 : ["3 5+ 3"],
                829140 : ["4 4 3"],
                828720 : ["3 0 1+ 3"],
                828040 : ["3 6 0 1"],
                828000 : ["4 3+ 2- 1"],
                827660 : ["4 1 0 0 1"],
                827480 : ["2 0 1+ 0 1"],
                827160 : ["0 0 1+ 0 1"],
            })

    def test_19(self): # Chaotrope - Senescence (shortened)
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 5\\Chaotrope - Senescence (shortened)\\notes.chart", 10, {
                700090 : ["0 0 0+ 1 0 0+"],
                699970 : ["0 0 0- 3- 0 0+"],
                699630 : ["0 0 0+ 1 3"],
                699510 : ["0 0 0- 3- 3"],
                697990 : ["0 1 0+ 1 0 0+"],
                697870 : ["0 1 0- 3- 0 0+"],
                697790 : ["0 0 0+ 1 2 0"],
                697730 : ["0 0 0+ 1 0 1"],
                697670 : ["0 0 0- 3- 2 0"],
                697610 : ["0 0 0- 3- 0 1"],
                697530 : ["0 1 0+ 1 3"],
            })

    def test_20(self): # Sufferer - Chair
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Sufferer - Chair\\notes.mid", 10, {
                343585 : ["(No activations.)"],
            })

    def test_21(self): # Rush - YYZ
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Rush - YYZ\\notes.mid", 10, {
                732860 : ["0 4 1 4"],
                732160 : ["0 4 1 3"],
                731320 : ["0 2 0 E2 4"],
                730620 : ["0 2 0 E2 3"],
                730400 : ["0 3 0 0 4"],
                730040 : ["0 3 1+ 4"],
                729700 : ["0 3 0 0 3"],
                729620 : ["0 2 0 E1 4"],
                729340 : ["0 3 1+ 3"],
                728920 : ["0 2 0 E1 3"],
                726360 : ["5 0 E2 4"],
            })

    def test_22(self): # Protest the Hero - Limb From Limb
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Protest the Hero - Limb From Limb\\notes.chart", 10, {
                691790 : ["0 2 1 0 E2 0 0"],
                691530 : ["0 2 1 0 E2 0 1"],
                691370 : ["0 2 1 4 1 0"],
                691110 : ["0 2 1 4 1 1"],
                691050 : ["0 2 1 0 E1 1 0"],
                690790 : ["0 2 1 0 E1 1 1"],
                690610 : ["0 2 1 0 E4+ 0"],
                690470 : ["0 2 1 5 0 0"],
                690350 : ["0 2 1 0 E4+ 1"],
                690210 : ["0 2 1 5 0 1"],
                689970 : ["0 2 1 1 0 0 0"],
            })

    def test_23(self): # Green Day - Burnout
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Green Day - Burnout\\notes.mid", 10, {
                378175 : ["0 4 1"],
                378075 : ["2 1 2"],
                377895 : ["3 1 1"],
                377695 : ["2 1 0"],
                377635 : ["3 0 2"],
                377415 : ["2 1 1"],
                377335 : ["0 5 1"],
                377255 : ["3 0 0"],
                377155 : ["4 1 1"],
                377015 : ["2 2 1"],
                376975 : ["3 0 1", "1 1 2"],
            })

    def test_24(self): # Avenged Sevenfold - Unbound (The Wild Ride)
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 4\\Avenged Sevenfold - Unbound (The Wild Ride)\\notes.mid", 10, {
                865320 : ["2 2+ 0 2"],
                864420 : ["2 3 0 2"],
                862000 : ["2 0 0 0 2", "0 0 2+ 0 2"],
                861100 : ["0 0 3 0 2"],
                860220 : ["2 2- 2 2"],
                859580 : ["2 2+ 3 0"],
                859560 : ["3 2+ 0 2"],
                858680 : ["2 3 3 0", "0 0 0 0 0 2"],
                858660 : ["3 3 0 2"],
                857820 : ["2 2+ 1 1"],
                857460 : ["2 2+ 0 1"],
            })

    def test_25(self): # The All-American Rejects - Move Along
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\The All-American Rejects - Move Along\\notes.mid", 10, {
                524750 : ["0 1 0 0"],
                523670 : ["1+ 0 0 0"],
                523550 : ["1- 1 0 0"],
                523510 : ["0 2 0 0"],
                523030 : ["1+ 3 0"],
                522310 : ["1- 2 0 0"],
                522230 : ["0 0 1 0"],
                521030 : ["1- 0 1 0"],
                520210 : ["0 1 2"],
                520090 : ["3 1 0"],
                519830 : ["1+ 1 0- 0"],
            })

    def test_26(self): # Mutemath - Allies
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Mutemath - Allies\\notes.chart", 10, {
                451830 : ["0 1 1 0"],
                447770 : ["0 1 0 0"],
                447690 : ["0 1 4"],
                443190 : ["0 1 1 1"],
                441130 : ["0 1 5"],
                440030 : ["0 2 1"],
                439130 : ["0 1 0 1"],
                438870 : ["3 1 0"],
                438530 : ["0 1 2 1"],
                438490 : ["0 0 1 0"],
                438430 : ["0 1 2 0"],
            })

    def test_27(self): # Jack Wall - Snakeskin Boots
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Jack Wall - Snakeskin Boots [highfine]\\notes.chart", 10, {
                410510 : ["1 E2 3+"],
                410190 : ["1 E2 0- 0 0"],
                410070 : ["1 E2 0- 0 1"],
                409670 : ["1 E1 3+"],
                409390 : ["1 E2 0- 3"],
                409350 : ["1 E1 0- 0 0"],
                409330 : ["1 E2 0+ E1"],
                409230 : ["1 E2 0- 2+", "1 E1 0- 0 1"],
                409050 : ["1 E0 E0 1- 0"],
                409030 : ["0 2 3+"],
                408930 : ["1 E0 E0 1- 1"],
            })

    def test_28(self): # Four Year Strong - Wasting Time (Eternal Summer)
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Four Year Strong - Wasting Time (Eternal Summer)\\notes.mid", 10, {
                510070 : ["3 E0 0 0"],
                507470 : ["2 1 0 0"],
                504370 : ["3 E2 0"],
                501130 : ["1 0 0 0"],
                499850 : ["2 4 0"],
                499290 : ["1 1 0 0"],
                498670 : ["3 E0 3"],
                496070 : ["2 1 3"],
                495010 : ["2 0 0 0"],
                494890 : ["2 3 0"],
                493510 : ["3 E1 1"],
            })

    def test_29(self): # Dream Theater - Overture 1928
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 3\\Dream Theater - Overture 1928\\notes.chart", 10, {
                380330 : ["(No activations.)"],
            })

    def test_30(self): # Thornhill - Limbo
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Thornhill - Limbo\\notes.mid", 10, {
                315350 : ["(No activations.)"],
            })

    def test_31(self): # Moonlight Haze - Lunaris
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Moonlight Haze - Lunaris\\notes.chart", 10, {
                342250 : ["(No activations.)"],
            })

    def test_32(self): # Matt McGuire - Avalanche [Bring Me The Horizon]
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Matt McGuire - Avalanche [Bring Me The Horizon]\\notes.mid", 10, {
                565850 : ["0 0 2+ 4 0"],
                565450 : ["0 0 2+ 4 1"],
                565390 : ["1 3 6 0"],
                565230 : ["0 6+ 4 0"],
                565170 : ["1 4 4 0"],
                565150 : ["0 0 2- 6 0"],
                564990 : ["1 3 6 1", "0 6- 6 0"],
                564830 : ["0 6+ 4 1"],
                564770 : ["1 4 4 1"],
                564750 : ["0 0 2- 6 1"],
                564610 : ["1 2+ 6 0"],
            })

    def test_33(self): # Dance Gavin Dance - Young Robot
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\Dance Gavin Dance - Young Robot\\notes.mid", 10, {
                245800 : ["(No activations.)"],
            })

    def test_34(self): # A Day to Remember - City Of Ocala
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 2\\A Day to Remember - City Of Ocala\\notes.mid", 10, {
                367290 : ["2 2 0"],
                366170 : ["2 0 1"],
                365430 : ["2 1 1"],
                365090 : ["2 3+"],
                364850 : ["2 2 1"],
                361830 : ["2 0 0"],
                361090 : ["2 1 0"],
                359790 : ["2 3-"],
                359650 : ["2 0 2"],
                358910 : ["2 1 2"],
                358630 : ["2 4"],
            })

    def test_35(self): # Nothing - April Ha Ha
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Nothing - April Ha Ha [tomato]\\notes.chart", 10, {
                423230 : ["0 2 1"],
                423170 : ["0 0 4"],
                422770 : ["2 4"],
                422690 : ["0 0 0 1"],
                422490 : ["1 0 2"],
                422450 : ["0 1 2"],
                422430 : ["1 0 0 0"],
                422390 : ["0 1 0 0"],
                422370 : ["0 0 3"],
                422310 : ["0 0 1 0"],
                422290 : ["2 0 1"],
            })

    def test_36(self): # Nickelback - How You Remind Me
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Nickelback - How You Remind Me\\notes.chart", 10, {
                267180 : ["6 0"],
                266880 : ["8- 0"],
                266780 : ["7 0"],
                266280 : ["0 0 0"],
                264240 : ["6 1"],
                263980 : ["5 0"],
                263940 : ["8- 1"],
                263840 : ["7 1"],
                263340 : ["0 0 1"],
                262940 : ["0 1 0"],
                261040 : ["5 1"],
            })

    def test_37(self): # My Chemical Romance - To the End
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\My Chemical Romance - To the End\\notes.mid", 10, {
                341645 : ["2 2 0"],
                341545 : ["0 0- 2 0"],
                340165 : ["3 1 0"],
                339825 : ["0 0+ 1 0"],
                338865 : ["1 3 0"],
                338145 : ["1 0 1 0"],
                335725 : ["0 4 0"],
                334425 : ["0 1 2"],
                334365 : ["0 1 1"],
                334045 : ["3 3"],
                333705 : ["0 0+ 3"],
            })

    def test_38(self): # Jason Paige - Pokemon Theme
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Jason Paige - Pokemon Theme\\notes.chart", 10, {
                298195 : ["(No activations.)"],
            })

    def test_39(self): # Don Broco - Actors
        self._test_pathlist("..\\test\\input\\common\\Summer Blast _25 Setlist\\Tier 1\\Don Broco - Actors\\notes.mid", 10, {
                255960 : ["4 1"],
                254040 : ["0 0 1"],
                252900 : ["1 0 1"],
                250360 : ["0 1 1"],
                249980 : ["2 2"],
                249220 : ["1 1 1"],
                248600 : ["3 1"],
                248100 : ["0 4"],
                247300 : ["4 0"],
                246960 : ["1 4"],
                245380 : ["0 0 0"],
            })

    def test_40(self): # Yoink - Spirit Bomb
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Yoink - Spirit Bomb [GanonMetroid]\\notes.mid", 10, {
                800240 : ["4 0 6"],
                799800 : ["4 4 3", "4 4 1"],
                799600 : ["4 3 3", "4 3 1"],
                799200 : ["0 3 6"],
                798400 : ["3 1 6"],
                797760 : ["3 5 3", "3 5 1"],
                797600 : ["2 1 6"],
                797460 : ["4 4 2"],
                797260 : ["4 3 2"],
                796960 : ["2 5 3", "2 5 1"],
                796780 : ["0 1 0 5", "0 1 0 4"],
            })

    def test_41(self): # Xane60 & SoundHaven - Bug Thief [Iglooghost] (B&X)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Xane60 & SoundHaven - Bug Thief [Iglooghost]\\notes.chart", 10, {
                662620 : ["3- 0 1- 2 1 1+ 0"],
                662100 : ["3- 1+ 3 1 1+ 0", "3- 0 1- 3+ 0 1+ 0"],
                662020 : ["3- 3- 2 1 1+ 0"],
                662000 : ["3- 0 1- 3- 1 1+ 0"],
                661960 : ["3+ 0+ 2 1 1+ 0"],
                661780 : ["1+ 1 4 1 1+ 0"],
                661760 : ["3+ 0- 3 1 1+ 0"],
                661720 : ["3- 0 1+ 1 1 1+ 0"],
                661700 : ["3- 1- 4 1 1+ 0"],
                661520 : ["3- 0 1- 2 0 3+ 0"],
                661500 : ["3- 3- 3+ 0 1+ 0", "3- 0 0 2 1 1+ 0"],
            })

    def test_42(self): # SoundHaven - Snowball Earth [Indistinct]
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\SoundHaven - Snowball Earth [Indistinct]\\notes.mid", 10, {
                768490 : ["(No activations.)"],
            })

    def test_43(self): # Necrophagist - Stabwound
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Necrophagist - Stabwound\\notes.chart", 10, {
                820950 : ["2 0- E2+"],
                820070 : ["3 0- E2+"],
                812810 : ["2 0- E3"],
                811930 : ["3 0- E3"],
                811490 : ["1 0 2 E0"],
                810830 : ["1 0 3+"],
                809930 : ["2 0+ 1"],
                809050 : ["3 0+ 1"],
                803290 : ["2 0- E1 E0"],
                803030 : ["0 1 E2+"],
                802690 : ["1 0 4"],
            })

    def test_44(self): # Ne Obliviscaris - Tapestry of the Starless Abstract (Shortened)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Ne Obliviscaris - Tapestry of the Starless Abstract (Shortened)\\notes.mid", 10, {
                1257810 : ["1 0- 2- 0+ 1 0"],
                1257470 : ["1 0+ 0 0+ 1 0"],
                1256470 : ["1 0- 2- 0+ 2- 0"],
                1256130 : ["1 0+ 0 0+ 2- 0"],
                1255630 : ["1 1 0- 0+ 1 0"],
                1254850 : ["1 2- 0- 0+ 1 0"],
                1254530 : ["1 0- 2- 0- 2 0"],
                1254310 : ["1 0- 2- 1 1 0"],
                1254290 : ["1 1 0- 0+ 2- 0"],
                1254190 : ["1 0+ 0 0- 2 0"],
                1254070 : ["1 2+ 2+ 1 0"],
            })

    def test_45(self): # Mahavishnu Orchestra - Awakening
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Mahavishnu Orchestra - Awakening\\notes.mid", 10, {
                770090 : ["1 0 2 0 0"],
                763810 : ["1 0 3 0 0"],
                763610 : ["1 0 2 1 0"],
                762410 : ["2 2 0 0", "1 0 1 0 0"],
                760730 : ["2 3 0 0"],
                758130 : ["0 1 2 0 0"],
                757030 : ["0 0 2 0 0"],
                756450 : ["1 3 0 0"],
                755930 : ["2 2 1 0", "1 0 1 1 0"],
                755350 : ["0 0 3 0 0"],
                754770 : ["1 4 0 0"],
            })

    def test_46(self): # DOMi & JD Beck - Zildjian LIVE! Performance 2020
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\DOMi & JD Beck - Zildjian LIVE! Performance 2020\\notes.mid", 10, {
                1248495 : ["0 2+ 1 3 0"],
                1248075 : ["0 2- 3 3 0"],
                1247535 : ["2 1+ 1 3 0"],
                1247115 : ["2 1- 3 3 0"],
                1246055 : ["0 2+ 0 3 0"],
                1246035 : ["0 1 3 3 0"],
                1245315 : ["0 2- 2 3 0"],
                1245255 : ["0 2+ 1 1 0 0"],
                1245095 : ["2 1+ 0 3 0"],
                1245075 : ["2 0 3 3 0"],
                1245055 : ["0 2- 0 1 3 0"],
            })

    def test_47(self): # Conquering Dystopia - Prelude to Obliteration
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Conquering Dystopia - Prelude to Obliteration\\notes.chart", 10, {
                809500 : ["(No activations.)"],
            })

    def test_48(self): # Car Bomb - The Sentinel
        self._test_pathlist("..\\test\\input\\common\\IB24\\T7\\Car Bomb - The Sentinel\\notes.mid", 10, {
                694105 : ["0 0 2 E3"],
                691745 : ["1 2 E3"],
                689245 : ["0 0 2 E4"],
                689225 : ["1 0 1 E3"],
                687485 : ["0 1 1 E3"],
                687405 : ["1 3 E3"],
                686885 : ["1 2 E4"],
                686565 : ["0 4 E3"],
                686285 : ["0 2 1 E3"],
                684745 : ["2 1 E3"],
                684365 : ["1 0 1 E4"],
            })

    def test_49(self): # Senri Kawaguchi - Ladies Talk [Kiyo Sen] (Drumeo Performance)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Senri Kawaguchi - Ladies Talk [Kiyo Sen] (Drumeo Performance)\\notes.mid", 10, {
                1229730 : ["0 E1+ E0 E0 0 E0 0 0"],
                1229470 : ["0 E2 4 2+ 0 0"],
                1229410 : ["0 E2 4 2- 1 0"],
                1229070 : ["0 E1+ E0 E1 2+ 0 0"],
                1229010 : ["0 E1+ E0 E1 2- 1 0"],
                1228970 : ["1+ 0- E0 E0 0 E0 0 0"],
                1228690 : ["0 E2 4 3 0 0"],
                1228630 : ["0 E1+ E0 E0 0 E3- 0"],
                1228310 : ["1+ 0- E0 E1 2+ 0 0"],
                1228290 : ["0 E1+ E0 E1 3 0 0", "0 E0 1- 4 2+ 0 0"],
                1228250 : ["1+ 0- E0 E1 2- 1 0", "0 E2 0 E0 0 E0 0 0"],
            })

    def test_50(self): # Pathfinder - When The Sunrise Breaks The Darkness
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Pathfinder - When The Sunrise Breaks The Darkness\\notes.mid", 10, {
                1299450 : ["(No activations.)"],
            })

    def test_51(self): # Lockslip - Bend
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Lockslip - Lockslip - 02 - Bend\\notes.mid", 10, {
                375670 : ["(No activations.)"],
            })

    def test_52(self): # Lightning Bolt - Dream Genie
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Lightning Bolt - Dream Genie\\notes.mid", 10, {
                1174640 : ["5 1 0 0 2 0 6 2 3"],
                1174600 : ["5 1 0 6 0 6 2 3"],
                1174540 : ["5 1 0 0 2 0 6 0 2 0"],
                1174500 : ["5 1 0 6 0 6 0 2 0"],
                1174440 : ["6 1 0 2 0 6 2 3"],
                1174400 : ["6 1 6 0 6 2 3"],
                1174340 : ["6 1 0 2 0 6 0 2 0"],
                1174300 : ["6 1 6 0 6 0 2 0"],
                1174260 : ["5 1 0 0 2 0 6 0 6"],
                1174240 : ["5 1 0 0 2 0 0 1 2 3"],
                1174220 : ["5 1 0 6 0 6 0 6"],
            })

    def test_53(self): # LethalLasagna - Levitating (feat. DaBaby) (Dua Lipa) (L)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Levitating (feat. DaBaby) (Dua Lipa) (L)\\notes.chart", 10, {
                469355 : ["(No activations.)"],
            })

    def test_54(self): # HopH2O - Nasty (Tinashe)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\HopH2O - Nasty (Tinashe)\\notes.mid", 10, {
                593950 : ["0 3 2"],
                590770 : ["1 2 2"],
                582630 : ["0 0 1 2"],
                578950 : ["0 3 0 1"],
                578850 : ["1 3 1"],
                577870 : ["0 0 2 1"],
                575790 : ["0 3 3"],
                575770 : ["1 2 0 1"],
                575230 : ["0 3 1"],
                574710 : ["1 0 0+ 1"],
                573110 : ["1 0 0- 2"],
            })

    def test_55(self): # Hannes Grossmann - Vacant Dreams
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Hannes Grossmann - Vacant Dreams\\notes.mid", 10, {
                938190 : ["1 0 4 2 1"],
                935690 : ["1 0 4 2 0"],
                933910 : ["1 0 0 2 2 1"],
                933670 : ["1 1 3 2 1"],
                931750 : ["1 1 4 0 1"],
                931410 : ["1 0 0 2 2 0"],
                931170 : ["1 1 3 2 0", "1 0 0 1 2 1"],
                930670 : ["1 0 5 2 1"],
                930430 : ["1 0 0 3 0 1"],
                929250 : ["1 1 4 0 0"],
                929210 : ["1 0 1 0 2 1"],
            })

    def test_56(self): # Fallen Monarch - Blight
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\Fallen Monarch - Blight\\notes.chart", 10, {
                742985 : ["(No activations.)"],
            })

    def test_57(self): # black midi - Sugar/Tzu
        self._test_pathlist("..\\test\\input\\common\\IB24\\T6\\black midi - Sugar／Tzu (Smoochums, Vasasasasa)\\notes.mid", 10, {
                655190 : ["0 E3+ E5 E1", "0 E3+ E5 E0"],
                654790 : ["0 E3+ E5 E2"],
                653310 : ["0 E3+ E5 E3"],
                650870 : ["0 E3+ E6 E1", "0 E3+ E6 E0"],
                650470 : ["0 E3+ E6 E2"],
                648990 : ["0 E3+ E6 E3"],
                647110 : ["0 E2 E7 E1", "0 E2 E7 E0"],
                646710 : ["0 E2 E7 E2"],
                645690 : ["0 E3+ E4 E3", "0 E3+ E4 E2"],
                645230 : ["0 E2 E7 E3"],
                644550 : ["0 E3+ E4 E4"],
            })

    def test_58(self): # TEXTURES - Laments Of An Icarus
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\TEXTURES - Laments Of An Icarus\\notes.mid", 10, {
                528610 : ["(No activations.)"],
            })

    def test_59(self): # Symphony X - Set the World on Fire
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Symphony X - Set the World on Fire\\notes.chart", 10, {
                1150660 : ["0 1 1 1 1"],
                1150640 : ["1 0 1 1 1"],
                1149580 : ["0 1 1 1 0"],
                1149560 : ["1 0 1 1 0"],
                1149320 : ["0 1 1 0 0 0"],
                1149300 : ["1 0 1 0 0 0"],
                1145320 : ["0 1 1 2"],
                1145300 : ["1 0 1 2"],
                1143820 : ["0 1 1 0 0 1"],
                1143800 : ["1 0 1 0 0 1"],
                1139380 : ["0 2- 1 1 1"],
            })

    def test_60(self): # Sianvar - Omniphobia
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Sianvar - Omniphobia\\notes.mid", 10, {
                676130 : ["(No activations.)"],
            })

    def test_61(self): # Satyr - Whelmed
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Satyr - Whelmed\\notes.mid", 10, {
                522595 : ["(No activations.)"],
            })

    def test_62(self): # Mike Orlando - Tapped Out
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Mike Orlando - Tapped Out\\notes.mid", 10, {
                1022200 : ["1 0 E0 E0 0 3 6"],
                1022040 : ["1 0 E0 E0 0 3 0 0"],
                1021660 : ["1 2- 2 5 0"],
                1021640 : ["1 0 E4 5 0"],
                1021380 : ["1 1 2 5 0"],
                1021360 : ["1 0 E0 E0 0 3 4"],
                1021180 : ["1 2- 2 5 2"],
                1021160 : ["1 0 E4 5 2"],
                1020900 : ["1 1 2 5 2", "1 0 E0 E0 0 3 1 0"],
                1020540 : ["1 2- 0 0 5 0"],
                1020440 : ["1 2- 2 4 6"],
            })

    def test_63(self): # Meshuggah - Nostrum
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Meshuggah - Nostrum\\notes.mid", 10, {
                1079130 : ["0 2 1 0"],
                1077970 : ["1 2 1 0"],
                1075510 : ["0 0 0 0+ 0"],
                1075370 : ["0 3 0+ 0"],
                1074350 : ["1 0 0 0+ 0"],
                1074210 : ["1 3 0+ 0"],
                1073830 : ["4 0 0+ 0"],
                1072290 : ["0 2 1 2"],
                1072130 : ["0 1- 0 0+ 0"],
                1071490 : ["0 2 0 0 0"],
                1071130 : ["1 2 1 2"],
            })

    def test_64(self): # Mastodon - Megalodon
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Mastodon - Megalodon\\notes.chart", 10, {
                909850 : ["0 3 1 0"],
                908470 : ["0 3 2 0"],
                908410 : ["0 1 1 1 0"],
                907030 : ["0 1 1 2 0"],
                906210 : ["0 1 0 1 0"],
                905510 : ["0 1 4 0"],
                905250 : ["0 1 2 1 0"],
                904830 : ["0 1 0 2 0"],
                904630 : ["0 3 0 0"],
                903190 : ["0 1 1 0 0"],
                902250 : ["0 2 2 0"],
            })

    def test_65(self): # Brandon Burkhalter - Someday
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\Brandon Burkhalter - Someday\\notes.mid", 10, {
                504415 : ["1+ 1 0+ 2"],
                504235 : ["1+ 1 1 1"],
                503755 : ["1+ 0- 2 2"],
                503335 : ["1+ 0+ 1 2"],
                503275 : ["0 0+ 2 2"],
                503015 : ["0 0- 0+ 0+ 2"],
                502835 : ["0 0- 0+ 1 1"],
                502755 : ["1- 0+ 2 2", "0 1 1 2"],
                502595 : ["0 0- 0- 1 2"],
                502495 : ["1- 0- 0+ 0+ 2"],
                502315 : ["1- 0- 0+ 1 1"],
            })

    def test_66(self): # August Burns Red - White Washed
        self._test_pathlist("..\\test\\input\\common\\IB24\\T5\\August Burns Red - White Washed\\notes.mid", 10, {
                706180 : ["0 1 3 0- 0"],
                705640 : ["0 1 0 0 0- 0"],
                693840 : ["0 1 3 2"],
                693300 : ["0 1 0 0 2"],
                692360 : ["0 1 3 0+"],
                691820 : ["0 1 0 0 0+"],
                691800 : ["0 1 2 0- 0"],
                691120 : ["3 3 0- 0"],
                690580 : ["3 0 0 0- 0"],
                689640 : ["0 0 0 2 0- 0"],
                688580 : ["0 0 1 0 0- 0"],
            })

    def test_67(self): # Tesseract - Deception - Concealing Fate, Pt. 2
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\Tesseract - Deception - Concealing Fate, Pt. 2\\notes.mid", 10, {
                1015340 : ["0 1 5 0 4"],
                1014820 : ["0 2 5 0 4"],
                1014680 : ["1 1 5 0 4"],
                1014500 : ["0 1 6 0 4"],
                1014480 : ["2 E0 5 0 4"],
                1014160 : ["1 2 5 0 4"],
                1013980 : ["0 2 6 0 4"],
                1013840 : ["1 1 6 0 4"],
                1013640 : ["2 E0 6 0 4"],
                1013320 : ["1 2 6 0 4"],
                1011960 : ["0 0 6+ 0 4"],
            })

    def test_68(self): # sungazer - All These People
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\sungazer - All These People\\notes.mid", 10, {
                614195 : ["1 1 0- 0+"],
                608415 : ["1 0+ 0+ 0+"],
                607095 : ["1 1 2"],
                606795 : ["1 0- 1 0+"],
                604935 : ["1 0+ 0- 1"],
                604715 : ["0 1 0+ 0+"],
                604595 : ["0 2 0- 0+"],
                603315 : ["1 1 1"],
                603195 : ["1 0+ 2"],
                601235 : ["0 1 0- 1"],
                601035 : ["1 1 0- 0-"],
            })

    def test_69(self): # Phish - Llama
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\Phish - Llama\\notes.mid", 10, {
                794440 : ["0 0 0 4 1"],
                794040 : ["0 0 0 5 0"],
                793900 : ["3 0 4 1"],
                793700 : ["0 0 0 5 1"],
                793500 : ["3 0 5 0"],
                793440 : ["0 3 4 1"],
                793160 : ["3 0 5 1"],
                793120 : ["0 0 0 0 1 1"],
                793040 : ["0 3 5 0", "0 0 0 0 0 1"],
                792980 : ["0 0 0 4 2"],
                792920 : ["1 0 0 4 1"],
            })

    def test_70(self): # Haken - The Good Doctor
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\Haken - The Good Doctor\\notes.mid", 10, {
                413810 : ["(No activations.)"],
            })

    def test_71(self): # Hail The Sun - Missed Injections
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\Hail The Sun - Missed Injections\\notes.mid", 10, {
                530275 : ["3 0"],
                528235 : ["1 2"],
                525315 : ["0 0- 1"],
                522455 : ["0 0+ 0"],
                522195 : ["1 0 0"],
                520115 : ["2 1"],
                518415 : ["3 1"],
                518275 : ["0 3"],
                514875 : ["0 1 0"],
                512215 : ["6"],
                510595 : ["0 0+ 1"],
            })

    def test_72(self): # Foo Fighters - Everlong
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\Foo Fighters - Everlong\\notes.mid", 10, {
                682900 : ["1 2 3"],
                681700 : ["2 2 3"],
                681580 : ["0 3 3"],
                680240 : ["3 0 3"],
                679300 : ["3 2 1"],
                678720 : ["3 1- 3"],
                678420 : ["1 3 2"],
                678380 : ["3 2 0"],
                678180 : ["1 2 0 1"],
                677880 : ["1 4 1"],
                677760 : ["1 3 1"],
            })

    def test_73(self): # Dance Gavin Dance - Chocolate Jackalope
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\Dance Gavin Dance - Chocolate Jackalope\\notes.mid", 10, {
                401785 : ["(No activations.)"],
            })

    def test_74(self): # A Lot Like Birds - Think Dirty out Loud
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\A Lot Like Birds - Think Dirty out Loud\\notes.mid", 10, {
                558135 : ["(No activations.)"],
            })

    def test_75(self): # 1.O.M. - Apex
        self._test_pathlist("..\\test\\input\\common\\IB24\\T4\\1.O.M. - Apex\\notes.chart", 10, {
                480165 : ["(No activations.)"],
            })

    def test_76(self): # Trivium - Feast of Fire
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\Trivium - Feast of Fire\\notes.mid", 10, {
                544080 : ["1 1 E3 0 E1 E2"],
                543880 : ["1 1 E3 0 E1 E3"],
                542760 : ["1 0 E3 0 E1 E2"],
                542560 : ["1 0 E3 0 E1 E3"],
                542120 : ["1 1 E3 0 E1 E0 0"],
                541580 : ["1 4 E3- E1 E2"],
                541380 : ["1 4 E3- E1 E3"],
                541100 : ["1 1 E0 E3- E1 E2"],
                540940 : ["2 1 E3 0 E1 E2"],
                540900 : ["1 1 E2 0 E1 E2", "1 1 E0 E3- E1 E3"],
                540800 : ["1 0 E3 0 E1 E0 0"],
            })

    def test_77(self): # Thrice - Deadbolt
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\Thrice - Deadbolt\\notes.mid", 10, {
                286435 : ["0 2 0"],
                286235 : ["1 0 0"],
                284715 : ["0 2 2"],
                284515 : ["1 0 2"],
                283715 : ["1 2"],
                283435 : ["0 0 1"],
                283135 : ["0 2 1"],
                283035 : ["1 1 0"],
                282975 : ["0 1 1"],
                282935 : ["1 0 1"],
                282735 : ["0 0 0 0"],
            })

    def test_78(self): # The Ghost Inside - Outlive
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\The Ghost Inside - Get What You Give - 02 - Outlive\\notes.mid", 10, {
                271270 : ["(No activations.)"],
            })

    def test_79(self): # Neck Deep - Beautiful Madness
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\Neck Deep - Beautiful Madness\\notes.mid", 10, {
                362120 : ["2 1"],
                359960 : ["3 1"],
                356960 : ["0 0 1"],
                355920 : ["1 0 0"],
                355900 : ["1 3"],
                355200 : ["2 0", "1 2+"],
                355140 : ["1 1 0"],
                353040 : ["3 0"],
                352600 : ["0 1 0"],
                352160 : ["0 3"],
                350040 : ["0 0 0"],
            })

    def test_80(self): # Good Tiger - Where Are the Birds
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\Good Tiger - Where Are the Birds\\notes.chart", 10, {
                365950 : ["(No activations.)"],
            })

    def test_81(self): # CHON - Book (feat. Matt Garstka)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\CHON - Book (feat. Matt Garstka)\\notes.mid", 10, {
                382865 : ["0- 1+ 0+"],
                379285 : ["0- 1- 1"],
                378205 : ["3 0+"],
                375445 : ["0- 1+ 0-"],
                374485 : ["0+ 2"],
                370785 : ["3 0-"],
                369365 : ["0- 0 1"],
                369285 : ["0+ 0- 0+"],
                366245 : ["0- 1- 0 0"],
                365565 : ["0- 4"],
                363325 : ["0- 3"],
            })

    def test_82(self): # Alpha Wolf - Acid Romance
        self._test_pathlist("..\\test\\input\\common\\IB24\\T3\\Alpha Wolf - Acid Romance\\notes.mid", 10, {
                277190 : ["0 2 0 1"],
                276670 : ["0 3+ 1"],
                275650 : ["0 4 1"],
                275290 : ["0 2 1 1"],
                274850 : ["0 1+ 0 1", "0 1- 0 1"],
                273710 : ["0 1- 1 1"],
                273570 : ["1 4 1"],
                273370 : ["1 1 0 1"],
                272970 : ["1 3 1"],
                272950 : ["0 1+ 1 1"],
                272870 : ["0 2 0 0"],
            })

    def test_83(self): # The Fall of Troy - Act One, Scene One
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\The Fall of Troy - Act One, Scene One [highfine]\\notes.chart", 10, {
                508455 : ["1 0+ 4 0 0"],
                507815 : ["1 0+ 4 3"],
                507795 : ["1 0+ 5 0+"],
                507595 : ["0+ 3 4 0 0"],
                506955 : ["0+ 3 4 3"],
                506935 : ["0+ 3 5 0+"],
                506295 : ["0- 0 0+ 4 0 0"],
                505655 : ["0- 0 0+ 4 3"],
                505635 : ["0- 0 0+ 5 0+"],
                504835 : ["0- 4+ 4 0 0"],
                504595 : ["1 0+ 5 1"],
            })

    def test_84(self): # Stone Temple Pilots - Trippin' on a Hole in a Paper Heart
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\Stone Temple Pilots - Trippin on a Hole in a Paper Heart\\notes.chart", 10, {
                377735 : ["2 1 0"],
                377535 : ["2 2 0"],
                377415 : ["0 0 0 0"],
                377395 : ["3 0 0"],
                375915 : ["0 1 0 0"],
                375755 : ["2 0 2"],
                375355 : ["0 3 0"],
                375315 : ["4 0 0"],
                374515 : ["1 2 0"],
                374235 : ["2 1 1"],
                374035 : ["2 2 1"],
            })

    def test_85(self): # Nova Charisma - The Greater Cause
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\Nova Charisma - The Greater Cause\\notes.mid", 10, {
                354150 : ["1 3 0"],
                352870 : ["0 0 1+ 0"],
                351870 : ["2 1+ 0"],
                351530 : ["3 1 0"],
                351450 : ["0 1 1 0"],
                351430 : ["1 0 1 0"],
                351350 : ["0 0 1- 1"],
                351010 : ["3 0 1"],
                350930 : ["0 1 0 1"],
                350910 : ["1 0 0 1"],
                350350 : ["2 1- 1"],
            })

    def test_86(self): # Mayday Parade - Jamie All Over
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\Mayday Parade - Jamie All Over\\notes.mid", 10, {
                335685 : ["0 0 2 0"],
                335465 : ["0 0 0 0"],
                335365 : ["0 1 3"],
                335305 : ["0 2 0 0"],
                335245 : ["0 2 2"],
                335225 : ["0 1 1 0"],
                335105 : ["1 0 3", "0 2 3"],
                335025 : ["2 0 3"],
                334985 : ["0 2 1- 0"],
                334965 : ["1 0 1 0"],
                334885 : ["2 0 1 0"],
            })

    def test_87(self): # Karnivool - Themata
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\Karnivool - Themata\\notes.mid", 10, {
                447835 : ["(No activations.)"],
            })

    def test_88(self): # fanclubwallet - Band Like That
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\fanclubwallet - Band Like That\\notes.mid", 10, {
                334510 : ["1 4"],
                333030 : ["2 4"],
                333010 : ["1 1 0"],
                332990 : ["1 5"],
                331530 : ["2 1 0"],
                331510 : ["2 5"],
                330590 : ["1 0 1"],
                329410 : ["0 3 0"],
                329110 : ["2 0 1"],
                328130 : ["0 0 3"],
                327410 : ["3 3"],
            })

    def test_89(self): # Area 11 - Knightmare/Frame
        self._test_pathlist("..\\test\\input\\common\\IB24\\T2\\Area 11 - Knightmare Frame\\notes.mid", 10, {
                420570 : ["1 1 0 0", "0 4 0 0"],
                419990 : ["1 1 0 1", "0 4 0 1"],
                419750 : ["0 7 0"],
                419570 : ["1 4 0"],
                419170 : ["0 7 1"],
                418990 : ["1 4 1"],
                418130 : ["1 1 3", "0 4 3"],
                417930 : ["0 3 0 0"],
                417450 : ["1 0 0 0"],
                417370 : ["0 2 0 0"],
                417350 : ["1 1 2", "0 4 2", "0 3 0 1"],
            })

    def test_90(self): # Tigran Hamasyan - Entertain Me
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Tigran Hamasyan - Entertain Me [tomato]\\notes.chart", 10, {
                287170 : ["0 0 0 1"],
                286310 : ["2 0 1"],
                286230 : ["3+ 0 1"],
                286110 : ["1 0+ 2", "0 1+ 0 1"],
                286030 : ["3- 0 1"],
                285910 : ["0 1- 0 1"],
                285530 : ["0 2 2"],
                284190 : ["3+ 3"],
                284070 : ["1 0- 0 1", "0 1+ 3"],
                283010 : ["4 0 1"],
                282030 : ["1 0- 3"],
            })

    def test_91(self): # Smash Mouth - I'm A Believer (The Monkees cover)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Smash Mouth - I_m A Believer (The Monkees cover) [highfine]\\notes.chart", 10, {
                354615 : ["1 0+ 0 0"],
                354155 : ["1 0+ 2", "1 0+ 1"],
                352135 : ["1 1 0 0"],
                351935 : ["1 0- 1"],
                351675 : ["1 1 2", "1 1 1"],
                350295 : ["0- 0 0+ 0 0"],
                349835 : ["0- 0 0+ 2", "0- 0 0+ 1"],
                348495 : ["2 1 0 0"],
                348235 : ["1 2 1", "1 2 0+"],
                348035 : ["2 1 2", "2 1 1"],
                347815 : ["0- 0 1 0 0"],
            })

    def test_92(self): # Hawthorne Heights - Saying Sorry
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Hawthorne Heights - Saying Sorry\\notes.mid", 10, {
                313865 : ["0 1 2"],
                313405 : ["0 1 0 1"],
                313005 : ["0 1 0 2"],
                311365 : ["0 1 1"],
                310525 : ["0 1 3"],
                309325 : ["0 1 0 0"],
                301765 : ["4 2"],
                301305 : ["4 0 1"],
                300905 : ["4 0 2"],
                300705 : ["0 1 0"],
                299265 : ["4 1"],
            })

    def test_93(self): # Evans Blue - Beg
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Evans Blue - Beg [highfine]\\notes.chart", 10, {
                328150 : ["1- 0 0 E0"],
                327670 : ["3 0- E0"],
                327350 : ["3 2"],
                323730 : ["1- 0 2+"],
                323610 : ["1+ 1+"],
                323050 : ["0 0 1+"],
                322850 : ["2 1+"],
                322510 : ["1+ 2"],
                321950 : ["0 0 2"],
                321750 : ["2 2"],
                320450 : ["1+ 0"],
            })

    def test_94(self): # Earth, Wind & Fire - September
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Earth, Wind & Fire - September\\notes.mid", 10, {
                337470 : ["(No activations.)"],
            })

    def test_95(self): # Deftones - My Own Summer (Shove It)
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Deftones - My Own Summer (Shove It) [highfine]\\notes.chart", 10, {
                352470 : ["3 3 1"],
                351910 : ["3 0 5"],
                351890 : ["2 0 1 1"],
                351850 : ["2 1 3"],
                351430 : ["3 1 3"],
                351390 : ["2 1 4"],
                351290 : ["3 2 3"],
                351090 : ["1 0 1 1"],
                351050 : ["1 1 3"],
                350970 : ["3 1 4"],
                350830 : ["3 2 4"],
            })

    def test_96(self): # Allister - Overrated
        self._test_pathlist("..\\test\\input\\common\\IB24\\T1\\Allister - Overrated\\notes.mid", 10, {
                228710 : ["1 2"],
                227990 : ["2 1"],
                227070 : ["2 0 0"],
                223570 : ["1 0 0"],
                221710 : ["0 0 1"],
                221530 : ["0 3"],
                221510 : ["0 0 0"],
                221470 : ["1 1"],
                221450 : ["0 1 0"],
                220490 : ["3 1"],
                220290 : ["3 0"],
            })