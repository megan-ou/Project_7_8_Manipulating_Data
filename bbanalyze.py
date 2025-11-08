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

    # count number of records
    bbstats["record.count"] = len(bbdat)

    # count number of complete cases
    bb = bbdat.dropna()
    bbstats["complete.cases"] = len(bb)

    #tuple form of min year, max year
    bbstats["years"] = (int(bb["year"].min()), int(bb["year"].max()))

    #unique player count - no double-count
    bbstats["player.count"] = bb["id"].nunique()

    #unique team count - no double-count
    bbstats["team.count"] = bb["id"].nunique()

    #unique league count - no double-count
    bbstats["league.count"] = bb["lg"].nunique()

    #calculate obp
    obp_num = bb["h"] + bb["bb"] + bb["hbp"]
    obp_den = bb["ab"] + bb["bb"] + bb["hbp"]
    bb["obp"] = obp_num / obp_den

    #calculate pab
    pab_num = obp_num + bb["sf"] + bb["sh"]
    pab_den = obp_num + bb["sf"] + bb["sh"]
    bb["pab"] = pab_num / pab_den

    #replace inf, -inf, NaN with NaN
    bb[["obp", "pab"]] = bb[["obp", "pab"]].replace([math.inf, -math.inf], math.nan)

    # Calculate nl information
    bbstats["nl"]["dat"] = get_dat_subset(bbstats["bb"], "lg", '"NL"')
    bbstats["nl"]["players"] = get_count(bbstats["nl"]["dat"], "id")
    bbstats["nl"]["teams"] = get_count(bbstats["nl"]["dat"], "team")

    #Calculate al information
    bbstats["al"]["dat"] = get_dat_subset(bbstats["bb"],"lg", '"AL"')
    bbstats["al"]["players"] = get_count(bbstats["al"]["dat"],"id")
    bbstats["al"]["teams"] = get_count(bbstats["al"]["dat"],"team")

    #Calculate records
    #Isolate players with at least 50 career at bats. This ensures that when scanning the dataset for records,
    # program searches through fewer players. (Or you don't have to search for >= 50 career at bats each time)
    bbrecords = get_dat_subset(bbstats["bb"], "ab", "50", ">=")
    for key in bbstats["records"].keys():
        #Iterate through all records and call helper method to find index with the largest value
        #Using that index, locate player ID and record value and populate the dictionary with them.
        index = get_highest_record(bbrecords, key)
        bbstats["records"][key]["id"] = bbrecords["id"][index]
        bbstats["records"][key]["value"] = bbrecords[key][index]

    return bbstats

def get_dat_subset(df, col, val, com = "=="):
    """
    Helper method that takes a subset of data based on a specific value (ex: taking a
    subset of all National League Baseball players)
    Args:
        df (Pandas DataFrame): DataFrame that we are taking the subset out of
        col (string): column name of the data subset we are extracting
        val (string): what specific value from the subset that we are looking for
        com (string): what comparison are we dealing with (==, >=, <=, etc.) Default is ==

    Returns: subset of database based on the id and value
    """
    if (not isinstance(col, str) or not isinstance(val, str) or not isinstance(com,str)
            or not isinstance(df, pd.DataFrame)):
        return math.nan

    #was originally df.query(f'{col} == "{val}"), but I wanted to be able to include value > int and
    # in the class example, there is no "" around the number, so I got rid of the "" in the statement
    # and instead included it in the val string argument (ex: '"AL"').
    return df.query(f'{col} {com} {val}')

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

def get_highest_record(df, col):
    """
    Finds the index of the highest value in a specified column of a DataFrame.
    Args:
        df (Pandas DataFrame): DataFrame that contains the records
        col (str): column in which you find the max value in

    Returns: index of row containing max value
    """
    if not isinstance(df, pd.DataFrame) or not isinstance(col,str):
        return math.nan

    #Call idxmax on only one column, so that only 1 index value is returned
    #Use axis=0 because we want the row index for max value within a column
    return df[col].idxmax(axis=0)

bbanalyze()

