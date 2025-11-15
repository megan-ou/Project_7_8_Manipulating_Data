import re

import pandas as pd
import string

def analyzeWords(words):
    """
    Function that profiles a Pandas Series of words and analyzes the characteristics of the list
    Args:
        words (Pandas Series): Series of words to be analyzed

    Returns: Dictionary containing:
                - letter_counts
                - max_char
                - size_counts
                - oo_count
                - oo_words
                - words_6plus
                - words_6plus_count
    """
    alphabet = list(string.ascii_lowercase)

    word_stats = dict.fromkeys(["letter_counts", "max_char", "size_counts", "oo_count", "oo_words", "words_6plus",
                                "words_6plus_count"])

    word_stats["letter_counts"] = dict.fromkeys(alphabet)

    for letter in alphabet:
        matches = re.findall(f'^{letter}', words)
        word_stats["letter_counts"][letter] = len(matches)

    return word_stats