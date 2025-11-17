from unittest import TestCase
from unittest import main

import shelve
import pandas as pd
import numpy as np
import glob
import os

from reformatSamples import reformatSamples

class Test_reformatSamples(TestCase):
    def setUp(self):
        # setup for all tests
        with shelve.open('expected_results') as expected_results:
            self.exp = expected_results['reformatSamples']

        self.dat = pd.read_csv("pistonrings.csv")
        rslt = reformatSamples(self.dat)

        self.act = reformatSamples(self.dat)

    def test_shape(self):
        # verify that the result has the expected shape (i.e. rows and columns)

        self.assertEqual(self.exp.shape, self.act.shape)

    def test_bad_samples(self):
        # verify that None is returned if a dataframe without the same number of all samples is passed in the call

        # remove one observation from the last sample so that the dataset represents bad samples
        bad = self.dat.loc[range(self.dat.shape[0] - 1), :]

        # reformatSamples should return None if the number of observations for per sample is not the same
        # for all samples
        actual = reformatSamples(bad)

        self.assertIsNone(actual)

    def test_good_samples(self):
        # verify that the resulting dataframe is correct in all aspects:

        # verify indexes
        self.assertTrue(self.exp.index.equals(self.act.index))

        # verify column labels
        self.assertTrue(self.exp.columns.equals(self.act.columns))

        # verify contents
        # this test superceded due to floating point accuracy errors
        # self.assertTrue(self.exp.equals(self.act))

        nrow, ncol = self.exp.shape

        # verify sample fields one at a time, limiting precision to 5 decimal places
        for i in range(nrow):
            for j in range(ncol):
                with self.subTest(sample=self.exp.iloc[i, 0]):
                    self.assertAlmostEqual(self.exp.iloc[i, j], self.act.iloc[i,j], places=5)



if __name__ == '__main__':
    rslt = main(verbosity=2, exit=False)