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
    if not isinstance(words, pd.Series):
        return None

    #Reformat entire series to be all lowercase
    for w in words:
        words[words == w] = w.lower()

    #Have list of uppercase and lowercase alphabet to make creating dictionaries/using alphabet easier
    alphabet = list(string.ascii_lowercase)

    word_stats = dict.fromkeys(["letter_counts", "max_char", "size_counts", "oo_count", "oo_words", "words_6plus",
                                "words_6plus_count"])

    word_stats["letter_counts"] = dict.fromkeys(alphabet)

    for letter in alphabet:
        #Sum the number of matches as each word is searched per letter, this seems a bit inefficient, but
        # it is the easiest way that I can think of and understand.
        count = sum([bool(re.search(f'^{letter}', w)) for w in words])
        word_stats["letter_counts"][letter] = count

    # Create a list containing the length of each string, so it can be searched for longest word
    word_lengths = [len(word) for word in words]
    word_stats["max_char"] = max(word_lengths)

    #Initialize size_counts dictionary
    sequence = list(range(1,word_stats["max_char"] + 1))
    word_stats["size_counts"] = dict.fromkeys(sequence)

    for num in sequence:
        #Re-use the word_lengths list to count up the number of words with num character lengths
        word_stats["size_counts"][num] = word_lengths.count(num)

    # oo section
    #Initialize counter variable outside the loop because it is incremented
    oo_count = 0
    #Create a deep copy of the series because we will be altering the Series and the original Series is needed
    # for the 6plus section; do not do shallow copy or else the data and indexes are shared between the original
    # and the copy.
    oo_words = words.copy()
    for w in oo_words:
        match = re.search("oo", w)
        if match:
            #Increment the counter if there is a match, so there is a running count
            oo_count += 1
        else:
            #If there is no match, find the index of the non-matching word and drop the index from the Series.
            # That way original indexes for the matches are preserved + pass the execution test.
            index = oo_words[oo_words == w].index
            oo_words.drop(index, inplace=True)

    #assign values after entire Series is evaluated
    word_stats["oo_count"] = oo_count
    word_stats["oo_words"] = oo_words

    #6plus section
    if word_stats["max_char"] < 6:
        #If the list's longest word is less than 6 characters long, then you don't need to check the entire
        # Series.
        word_stats["words_6plus_count"] = 0
        word_stats["words_6plus"] = None

    else:
        #Re-use the previously created word_lengths list to sum up the counts
        word_stats["words_6plus_count"] = sum([bool(length >= 6) for length in word_lengths])

        six_plus_words = words.copy()
        for w in six_plus_words:
            #Was going to add words_6plus_count to the loop as well, but I liked the list comprehension, so I kept it
            # Unsure if there is a more efficient way to do both at once
            if len(w) < 6:
                index = six_plus_words[six_plus_words == w].index
                six_plus_words.drop(index, inplace=True)

        word_stats["words_6plus"] = six_plus_words

    return word_stats