from unittest import TestCase

import pandas as pd
from reformatSamples import reformatSamples

class Test(TestCase):
    def setUp(self):
        self.exp = pd.read_csv("pistonrings_2.csv")
        self.exp.index = [1,2,3]
        self.db = pd.read_csv("pistonrings_3.csv")
        self.act = reformatSamples(self.db)
        self.bad_db = pd.read_csv("pistonrings_4.csv")

    def test_reformat_samples(self):
        #Invalid values
        self.assertIsNone(reformatSamples(self.bad_db))
        self.assertIsNone(reformatSamples("database"))

        #Valid values
        #Shape and index labels
        self.assertEqual(self.exp.shape, self.act.shape)
        self.assertTrue(self.exp.index.equals(self.act.index))
        self.assertTrue(self.exp.columns.equals(self.act.columns))

        #Contents
        for i in range(1,4):
            self.assertAlmostEqual(self.exp.loc[i,'sample'],self.act.loc[i,'sample'])
            self.assertAlmostEqual(self.exp.loc[i,'obs.1'],self.act.loc[i,'obs.1'])
            self.assertAlmostEqual(self.exp.loc[i,'obs.2'],self.act.loc[i,'obs.2'])