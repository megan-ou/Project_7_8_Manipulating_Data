import pandas as pd
import math
import re
import numpy as np

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

    #Read in, sort, drop NaN values + unnecessary columns to the reformatted structure in data set
    # so that it is ready to be reformatted
    sample_dat = pd.read_csv(samples)
    sample_dat.dropna()
    sample_dat.drop('trial', axis=1, inplace=True)
    sample_dat.drop(sample_dat.columns[0],axis=1,inplace=True)
    sample_dat.sort_values(by='sample')

    #Verify that all samples have the same number of observations.
    sample_sizes = sample_dat.groupby(["sample"]).size()
    if not all(sample_sizes[1] == sample_sizes[1:]):
        return None

    #Creating the column listing the observation number needed to create a mutli-index DataFrame
    #Store these values in variables, so that the functions are easier to read.
    num_samples = len(sample_sizes)
    num_obs = sample_sizes[1]
    # tile method in numpy to generate repeated sequences of numbers (from documentation)
    seq = np.tile(range(1,num_obs+1), num_samples)
    #convert the numpy array to a series so that it is easy to concatenate to the Pandas DF with a name
    obs_series = pd.Series(seq, name='obs')
    sample_dat = pd.concat([sample_dat,obs_series],axis=1)

    #Create a multi-index DataFrame based on sample and observation number
    reformat_dat = sample_dat.groupby(['sample', 'obs']).sum()
    reformat_dat.unstack(inplace=True)
    print(reformat_dat)

    return None

reformatSamples("pistonrings.csv")
