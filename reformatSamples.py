import pandas as pd
import math
import re

def reformatSamples(samples):
    """
    Function that reformats a set of data from observations indicating sample number to neat rows per sample
    containing observations per sample. All samples must have the same number of observations.

    Args:
        samples (str): name of file containing samples.

    Returns: data frame containing the restructured data

    """
    #Ensure that samples is in the correct format to be then read into a pd Data Frame
    if not isinstance(samples, str):
        return math.nan

    match = re.search(r".+\.csv$", samples)
    if not match:
        return math.nan

    sampledat = pd.read_csv(samples)

    #make sure there are no rows with NaN values
    sampledat.dropna()

    #Verify that all samples have the same number of observations. First use groupby to sort/aggregate the data frame
    # Used pandas documentation to find .size() and it's functions. It returns a Series with the size of each category.
    # Go through the Series to ensure that all values are the same
    sample_sizes = sampledat.groupby(["sample"]).size()
    #Use .diff() to compare each consecutive row in the Series. This way, if there are any differences between two rows,
    # then the program knows that at least one sample has too many or too little observations and returns None.
    #Originally didn't realize that another Series is returned, so I summed the differences in entries. If there are no
    # differences, sum should be 0.
    diff_rows = sample_sizes.diff().sum()
    if diff_rows != 0:
        return None



    return None

reformatSamples("pistonrings.csv")
