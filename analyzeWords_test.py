import string
from unittest import TestCase
import pandas as pd
from analyzeWords import analyzeWords


class Test(TestCase):
    def setUp(self):
        self.words = pd.read_csv("words_2.csv")['x']
        self.act = analyzeWords(self.words)

        # Populate a dictionary based on words_2.csv, a set of 26 words for expected values.
        # words_2.csv contains words of different sizes starting with each letter with captials thrown in
        # here and there
        # These values are hardcoded in.
        for w in self.words:
            self.words[self.words == w] = w.lower()

        self.alphabet = list(string.ascii_lowercase)
        self.exp = dict.fromkeys(["letter_counts", "max_char", "size_counts", "oo_count", "oo_words", "words_6plus",
                                  "words_6plus_count"])

        self.exp["letter_counts"] = dict.fromkeys(self.alphabet)
        for letter in self.alphabet:
            self.exp["letter_counts"][letter] = 1

        self.exp["max_char"] = 12

        sequence = list(range(1, 13))
        self.exp["size_counts"] = dict.fromkeys(sequence)
        # Based on my counts, they do add up to 26
        self.exp["size_counts"][1] = 1
        self.exp["size_counts"][2] = 1
        self.exp["size_counts"][3] = 1
        self.exp["size_counts"][4] = 0
        self.exp["size_counts"][5] = 9
        self.exp["size_counts"][6] = 5
        self.exp["size_counts"][7] = 5
        self.exp["size_counts"][8] = 1
        self.exp["size_counts"][9] = 1
        self.exp["size_counts"][10] = 0
        self.exp["size_counts"][11] = 1
        self.exp["size_counts"][12] = 1

        self.exp["oo_count"] = 9
        self.oo = self.words.copy()
        self.oo.drop(index=[1, 3, 4, 5, 7, 8, 9, 10, 13, 15, 16, 18, 19, 20, 21, 23, 24], inplace=True)
        self.exp["oo_words"] = self.oo

        self.exp["words_6plus_count"] = 14
        self.six_plus = self.words.copy()
        self.six_plus.drop(index=[0, 3, 7, 9, 10, 12, 13, 15, 16, 20, 22, 24], inplace=True)
        self.exp["words_6plus"] = self.six_plus

    def test_analyze_words(self):
        # Test for wrong data type
        x = "pd.Series"
        self.assertIsNone(analyzeWords(x))

        # Test for valid values from setUp()
        for letter in self.alphabet:
            self.assertEqual(self.exp["letter_counts"][letter], self.act["letter_counts"][letter])

        self.assertEqual(self.exp["max_char"], self.act["max_char"])

        for i in range(1, 13):
            self.assertEqual(self.exp["size_counts"][i], self.act["size_counts"][i])

        self.assertEqual(self.exp["oo_count"], self.act["oo_count"])

        self.assertTrue(self.exp["oo_words"].equals(self.act["oo_words"]))

        self.assertEqual(self.exp["words_6plus_count"], self.act["words_6plus_count"])

        self.assertTrue(self.exp["words_6plus"].equals(self.act["words_6plus"]))



