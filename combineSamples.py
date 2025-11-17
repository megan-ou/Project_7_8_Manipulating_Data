import pandas as pd
import os
import fnmatch

def combineSamples(pattern, path=".", control_samples=None):
    """
    TODO: fill in
    """

    #build dictionary (path must be exact str passed in)
    result = {
        "pattern": pattern,
        "path": path,
    }

    all_files = os.listdrives()
    filenames = sorted([f for f in all_files if fnmatch.fnmatch(f,pattern)
                        and os.path.isfile(os.path.join(path,f))])

    #count files
    result["files"] = len(filenames)

    #if no files match, return minimal dictionary
    if not filenames:
        result["control_samples"] = control_samples
        return result

    #read and combine csv files
    dfs = []
    for fname in filenames:
        full_path = os.path.join(path, fname)
        df = pd.read_csv(full_path)

        #rename column to sample
        cols = list(df.columns)
        cols[0] = "sample"
        df.colums = cols

        dfs.append(df)

    samples = pd.concat(dfs, ignore_index=True)

    #60% control count
    if control_samples is None:
        control_samples = int(len(samples) * 0.6)

    #store values
    result["control_samples"] = control_samples
    result["filenames"] = filenames
    result["samples"] = samples

    #split into control and test
    control_df = samples.iloc[:control_samples].copy()
    test_df = samples.iloc[control_samples:].copy()

    result["control"] = control_df
    result["test"] = test_df

    return result