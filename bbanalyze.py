import math
import pandas as pd
import re

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
    if not isinstance(filename, str):
        return math.nan
    #Make sure that the given filename is a .csv file with a name using regular expressions. Not sure if this was
    # required, but this was honestly for fun to see if I can do it. Also makes sure that the .csv file has a name.
    # In other words, the file cannot just be .csv because files should have names?
    match = re.search(r".+\.csv$", filename)
    if not match:
        return math.nan

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
    for key in bbstats["records"].keys():
        bbstats["records"][key] = dict.fromkeys(["id", "value"])

    #TODO: record.count -> league.count calculations here

    #TODO: bb calculated here, need this to test nl and al since nl and al are bb subsets

    #TODO: nl calculated here; can use get_dat_subset and get_count methods; can probably copy format
    # from "al"

    #Calculate al information
    bbstats["al"]["dat"] = get_dat_subset(bbstats["bb"],"lg", "AL")
    bbstats["al"]["players"] = get_count(bbstats["al"]["dat"],"id")
    bbstats["al"]["teams"] = get_count(bbstats["al"]["dat"],"team")

    #Calculate records

    return bbstats

def get_dat_subset(df, col, val):
    """
    Helper method that takes a subset of data based on a specific value (ex: taking a
    subset of all National League Baseball players)
    Args:
        df (Pandas DataFrame): DataFrame that we are taking the subset out of
        col (string): column name of the data subset we are extracting
        val (string): what specific value from the subset that we are looking for

    Returns: subset of database based on the id and value
    """
    if not isinstance(col, str) or not isinstance(val, str) or not isinstance(df, pd.DataFrame):
        return math.nan

    return df.query(f'{col} == "{val}"')

def get_count(df, col):
    """
    Helper method that counts the number of unique rows in a DataFrame; can be used for player count
    and team count.

    Args:
        df (Pandas DataFrame): DataFrame that you want to take count of contents
        col (string): column name of the data we want a count of

    Returns: count of rows
    """
    if not isinstance(df, pd.DataFrame) or not isinstance(col,str):
        return math.nan

    #Originally used .shape(), but realized that shape will count all rows, even the duplicates of same player
    # playing multiple years.
    return df[col].nunique()

bbanalyze()

