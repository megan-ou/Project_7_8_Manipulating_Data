import unittest
from unittest import TestCase
import pandas as pd
from bbanalyze import bbanalyze

class Test_bbanalyze(TestCase):
    def setUp(self):
        #test environment, 101 rows of data from baseball.csv
        self.test_file = 'BBAnalyze_Test.csv'
        self.result = bbanalyze(self.test_file)

    def test_bbanalyze_no_default(self):
        """
        Verify bbanalyze runs correct with provided filename
        """
        result = bbanalyze(self.test_file)
        self.assertIsInstance(result, dict)
        self.assertIn("record.count", result)
        self.assertEqual(result["record.count"], 101)

    #verify bb subset structure
    def test_bb(self):
        df = self.result["bb"]
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("obp", df.columns)
        self.assertIn("pab", df.columns)

    #verify al subset
    def test_al(self):
        al = self.result["al"]
        self.assertTrue((al["dat"]["lg"] == "AL").all())
        self.assertEqual(al["players"], 13)
        self.assertEqual(al["teams"], 10)

    #verify nl subset
    def test_nl(self):
        nl = self.result["nl"]
        self.assertTrue((nl["dat"]["lg"] == "NL").all())
        self.assertEqual(nl["players"], 33)
        self.assertEqual(nl["teams"], 13)

    #record count test
    def test_record_count(self):
        self.assertEqual(self.result["record.count"], 101)

    #complete cases test
    def test_complete_cases(self):
        self.assertEqual(self.result["complete.cases"], 51)

    #test years
    def test_years(self):
        self.assertEqual(self.result["years"], (1871, 2007))

    #unique play count test
    def test_complete_player_count(self):
        self.assertEqual(self.result["player.count"], 58)

    #unique team count test
    def test_complete_team_count(self):
        self.assertEqual(self.result["team.count"], 40)

    #league count test
    def test_league_count(self):
        self.assertEqual(self.result["league.count"], 2)

    #test obp and pab
    #hardcoded obp and pad for data containing all relevant variables
    def test_obp_pab_calc(self):
        df = self.result["bb"]

        #test for loftoke01 (CLE)
        self.assertAlmostEqual(df.loc[df["id"] == "loftoke01"].iloc[0]["obp"], 66/190)
        self.assertAlmostEqual(df.loc[df["id"] == "loftoke01"].iloc[0]["pab"], 72/196)

        #test for loftoke01 (TEX)
        self.assertAlmostEqual(df.loc[df["id"] == "loftoke01"].iloc[1]["obp"], 137/358)
        self.assertAlmostEqual(df.loc[df["id"] == "loftoke01"].iloc[1]["pab"], 142/363)


