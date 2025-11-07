from unittest import TestCase
from unittest import main

import shelve
from bbanalyze import bbanalyze

import pandas as pd
import numpy as np
import math

def compFloat(exp, act, atol = 0.00001):
    """
    Compares two floating point values, and returns True if they are equal, False otherwise. Unlike a standard
    numeric comparison math.nan == math.nan = True and math.inf == math.inf = True (these would normally return
    False)
    :param exp: The expected value
    :type exp: float
    :param act: the actual value being tested
    :type act: float
    :param atol: Absolute tolerance used in Numpy.isclose(...) to compare finite floats
    :type atol:
    :return:
    :rtype:
    """

    if not isinstance(exp, float) and not isinstance(act, float):
        # one or the other is not a float, cannot proceed
        return None

    if math.isnan(exp) and math.isnan(act):
        return True
    elif math.isinf(exp) and math.isinf(act):
        return True
    else:
        return np.isclose(exp, act, atol)


def compSeries(exp: pd.Series, act: pd.Series, atol=0.000001):
    """
    Performs a comparison of two Series objects that accounts for nan, inf, and floating point inaccuracies
    :param exp: Object representing expected results
    :type exp: Pandas.Series
    :param act: Object representing actual results
    :type act: Pandas.Series
    :param atol: Absolute tolerance to use with np.isclose function for doing the comparison
    :param atol: float
    :return: True if the Series are equal, False otherwise; None if either of exp or act is not Series object
    :rtype: bool or None
    """

    if isinstance(act, pd.Series) == False or isinstance(exp, pd.Series) == False:
        # one of the arguments is not a series, so this is not a valid call
        return None

    if len(exp) != len(act):
        return False

    if exp.name != act.name:
        return False

    if not exp.index.equals(act.index):
        return False

    if exp.dtype == 'float':
        # the series is a float, so we'll need to do special handling
        # first, create a Series of the index so that we can "apply" over the two Series objects
        idx = pd.Series(exp.index)

        # compare, pairwise, all elements in the two Series
        result = idx.apply(lambda i: compFloat(exp.loc[i], act.loc[i]))

        # return the aggregate result True if all are equal, False otherwise
        return np.all(result)
    else:
        # we should be able to simply compare them with standard operators
        return (exp.equals(act))


def compDataFrame(exp, act, atol=0.000001):
    """
     Performs a comparison of two DataFrame objects that accounts for nan, inf, and floating point inaccuracies
     :param exp: Object representing expected results
     :type exp: Pandas.DataFrame
     :param act: Object representing actual results
     :type act: Pandas.DataFrame
     :param atol: Absolute tolerance to use with np.isclose function for doing the comparison
     :param atol: float
     :return: True if the Series are equal, False otherwise; None if either of exp or act is not Series object
     :rtype: bool or None
     """

    if isinstance(act, pd.DataFrame) == False or isinstance(exp, pd.DataFrame) == False:
        # one of the arguments is not a series, so this is not a valid call
        return None

    if exp.shape != act.shape:
        # exp and act must have the same shape
        return False

    if any(exp.keys() != act.keys()):
        # DataFrames must have the same column names
        return False

    if any(exp.index != act.index):
        # DataFrames must have the same indexes
        return False

    # DataFrames have same shape, indexes, and column names, so we can compare the columns one at a time
    for col in exp.keys():
        if not compSeries(exp[col], act[col]):
            # columns are not equal
            return False

    return True


class Test_bbanalyze(TestCase):

    def setUp(self):
        # initialize expected results
        with shelve.open('expected_results', flag='r') as expected_results:
            self.exp = expected_results['bbanalyze']
            self.exp2005 = expected_results['bbanalyze.2005']

            # call bbanalyze with default file
            self.act = bbanalyze()

    def test_bbanalyze_no_default(self):
        # verify the bb subset

        bb = self.exp['bb']
        bb2005 = bb.loc[bb['year'] == 2005, :].drop(columns=['obp', 'pab'])

        bb2005.to_csv('bb2005.csv')

        act = bbanalyze('bb2005.csv')

        for k,v in self.exp2005.items():
            with self.subTest(Item=k):
                if k in {'al', 'nl'}:
                    # evaluate the AL or NL dictionaries
                    with self.subTest(League=k):
                        self.assertTrue(compDataFrame(v['dat'], act[k]['dat']))
                        self.assertEqual(v['players'], act[k]['players'])
                        self.assertEqual(v['teams'], act[k]['teams'])
                elif isinstance(v, pd.DataFrame):# or isinstance(v, pd.Series):
                    self.assertTrue(compDataFrame(v, act[k]))
                elif isinstance(v, pd.Series):
                    self.assertTrue(compSeries(v, act[k]))
                else:
                    # if k == 'records':
                    #     for key in v.keys():
                    #         if key == 'career':
                    #             self.assertEqual(v[key], act[k][key])
                    # else:
                    self.assertEqual(v, act[k])


    def test_bb(self):
        # verify the bb subset
        bbexp = self.exp['bb']

        bbact = self.act['bb']

        for col in bbexp.columns:
            with self.subTest(column=col):
                self.assertTrue(compSeries(bbexp[col], bbact[col]))

    def test_nl(self):
        # verify the NL subset
        bbexp = self.exp['nl']

        bbact = self.act['nl']

        # test data frame contents
        for col in bbexp['dat'].columns:
            with self.subTest(column=col):
                self.assertTrue(bbexp['dat'][col].equals(bbact['dat'][col]))

        # test player and team counts
        self.assertEqual(bbexp['teams'], bbact['teams'])
        self.assertEqual(bbexp['players'], bbact['players'])

    def test_al(self):
        # verify the AL subset
        bbexp = self.exp['al']

        bbact = self.act['al']

        # test data frame contents
        for col in bbexp['dat'].columns:
            with self.subTest(column=col):
                self.assertTrue(bbexp['dat'][col].equals(bbact['dat'][col]))

        # test player and team counts
        self.assertEqual(bbexp['teams'], bbact['teams'])
        self.assertEqual(bbexp['players'], bbact['players'])

    def test_record_count(self):
        # verify the record count

        self.assertEqual(self.exp['record.count'], self.act['record.count'])

    def test_complete_cases(self):
        # verify complete cases count

        self.assertEqual(self.exp['complete.cases'], self.act['complete.cases'])

    def test_years(self):
        # verify complete cases count

        self.assertEqual(self.exp['years'], self.act['years'])

    def test_complete_player_count(self):
        # verify complete cases count

        self.assertEqual(self.exp['player.count'], self.act['player.count'])

    def test_complete_team_count(self):
        # verify complete cases count

        self.assertEqual(self.exp['team.count'], self.act['team.count'])

    def test_records(self):
        for record in self.exp['records']:
            # TODO remove the conditional processing for next year (Fall 2022)
            #  the following accounts for spec error, which stated to include players with >= 50 ab in a stint
            #  but it was supposed to be >= 50 career at bats (which was stated in class and office hours).
            #  exp_stint50 contains records based on removing all rows with fewer than 50 at bats. After the
            #  correction, keep the comparison against self.exp

            with self.subTest(Record=record):
                # if self.exp_stint50['records'][record]['value'] == self.act['records'][record]['value']:
                #     self.assertAlmostEqual(self.exp_stint50['records'][record], self.act['records'][record], places=5)
                # else:
                #     self.assertAlmostEqual(self.exp['records'][record], self.act['records'][record], places=5)
                self.assertAlmostEqual(self.exp['records'][record], self.act['records'][record], places=5)



if __name__ == '__main__':
    rslt = main(verbosity=2, exit=False)

    # db = shelve.open('expected_results')
    # exp = db['bbanalyze']['bb']
    # act = db['bbanalyze']['bb']
    #
    # print(compDataFrame(exp, act))