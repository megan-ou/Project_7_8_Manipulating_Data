from unittest import TestCase
from unittest import main

import shelve
import pandas as pd
import glob
import os

from extractCoordinates import extractCoordinates

class Test_extractCoordinates(TestCase):
    def setUp(self):
        # setup for all tests
        with shelve.open('expected_results') as expected_results:
            self.exp = expected_results['extractCoordinates']

        self.dat = pd.read_csv("coordinates.csv")
        self.act = extractCoordinates(self.dat)

    def test_station_missing(self):
        # The input data must have a 'station' column

        # rename the station column so that it will be missing
        dat = self.dat

        dat.rename(columns={'station': 'bad'}, inplace=True)

        self.assertEqual(-1, extractCoordinates(dat))

    def test_coordinates_missing(self):
        # The input data must have a 'coordinates' column

        # rename the station column so that it will be missing
        dat = self.dat

        dat.rename(columns={'coordinates': 'bad'}, inplace=True)

        self.assertEqual(-2, extractCoordinates(dat))

    def test_verify_result(self):
        # verify the resulting dataframe
        # the following test was superseded due to floating point inaccuracies
        self.assertTrue(self.exp.equals(self.act))

        # verify sample fields one at a time, limiting precision to 5 decimal places
        nrow, ncol = self.exp.shape

        for i in self.exp.index:
            for j in self.exp.keys()[1:]:
                with self.subTest(station=self.exp.loc[i, 'station'], col=j):
                    self.assertAlmostEqual(self.exp.loc[i, j], self.act.loc[i,j], places=5)



if __name__ == '__main__':
    rslt = main(verbosity=2, exit=False)
