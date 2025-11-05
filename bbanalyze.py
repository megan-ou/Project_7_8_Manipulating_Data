import pandas as pd

def bbanalyze(filename = "baseball.csv"):
    """
    Function that analyzes, calculates, and reports the relative statistics for a given baseball
    dataset, national league, and American League baseball.
    TODO: add more info?
    Returns: dictionary with records for the following
        record.count
        complete.cases
        player.count
        team.count
        league.count
        bb
        nl
        al
        records
    """
    bbdat = pd.read_csv(filename)
