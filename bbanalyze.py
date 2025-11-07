import math
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

    #Construct empty dictionaries with null values to be populated later; basically initializing
    # all values to keep track of the dictionaries within dictionaries. This is for my own sanity;
    # I am unsure if it would be better to create them later on.
    bbstats = dict.fromkeys(["record.count", "complete.cases", "player.count", "team.count",
                             "league.count", "bb", "nl", "al", "records"])
    bbstats["nl"] = dict.fromkeys(["dat", "players", "teams"])
    bbstats["al"] = dict.fromkeys(["dat", "players", "teams"])
    bbstats["records"] = dict.fromkeys(["odp", "pab", "hr", "hrp", "h", "hp", "sb", "sbp", "so",
                                        "sop", "sopa", "bb", "bbp", "g"])
    #I didn't want to use a for loop and instead use a list comprehension, but I was not sure
    # how to structure it as bbstats["records"][key] = [list comprehension]
    for i in bbstats["records"].keys:
        bbstats["records"][i] = dict.fromkeys(["id", "value"])

    #TODO: record.count -> league.count calculations here

    #TODO: bb calculated here

    #TODO: nl calculated here; can use get_dat_subset

    bbstats["al"]["dat"] = get_dat_subset(bbdat,"lg", "AL")

def get_dat_subset(df, col, value):
    """
    Helper method that takes a subset of data based on a specific ID value (ex: taking a
    subset of all National League Baseball players)
    Args:
        df (Pandas DataFrame): DataFrame that we are taking the subset out of
        col (string): column name of the data subset we are extracting
        value (string): what specific value from the subset that we are looking for

    Returns: subset of database based on the id and value
    """
    if not isinstance(id, str) or not isinstance(value, str) or not isinstance(df, pd.DataFrame):
        return math.nan

    return df.query(f'{col} == "{value}"')

