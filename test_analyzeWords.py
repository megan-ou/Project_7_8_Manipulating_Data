from unittest import TestCase
from unittest import main

import shelve
import pandas as pd
import glob
import os

from analyzeWords import analyzeWords

class Test_analyzeWords(TestCase):
    def setUp(self):
        # setup for all tests
        with shelve.open('expected_results') as expected_results:
            self.exp = expected_results['analyzeWords']

        self.words = pd.read_csv("words.csv")['x']
        self.act = analyzeWords(self.words)

    def test_letter_counts(self):
        # validate the counts for each letter of the alphabet

        for k,v in self.exp['letter_counts'].items():
            with self.subTest(letter=k):
                self.assertEqual(v, self.act['letter_counts'][k])

    def test_letter_max_char(self):
        # validate the maximum character count

        self.assertEqual(self.exp['max_char'], self.act['max_char'])

    def test_size_counts(self):
        # validate counts of words by

        for k,v in self.exp['size_counts'].items():
            with self.subTest(letter=k):
                self.assertEqual(v, self.act['size_counts'][k])

    def test_oo_count(self):
        # validate the count of 'oo' words

        self.assertEqual(self.exp['oo_count'], self.act['oo_count'])

    def test_oo_words(self):
        # verify that all 'oo' words were identified

        self.assertTrue(self.exp['oo_words'].equals(self.act['oo_words']))

    def test_6plus_count(self):
        # validate the count of 'oo' words

        self.assertEqual(self.exp['words_6plus_count'], self.act['words_6plus_count'])

    def test_6plus_words(self):
        # verify that all 'oo' words were identified

        self.assertTrue(self.exp['words_6plus'].equals(self.act['words_6plus']))


if __name__ == '__main__':
    rslt = main(verbosity=2, exit=False)
