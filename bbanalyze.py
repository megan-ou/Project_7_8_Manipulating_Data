import math
import pandas as pd
import re

def bbanalyze(filename = "baseball.csv"):
    """
    Function that analyzes, calculates, and reports the relative statistics for a given baseball
    dataset, national league, and American League baseball.

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

    #Execution test data does not have a rowid column, dropping that column so they are equal. (This helped us
    # pass more tests?)
    keys = bbdat.keys()
    if [key == "rowid" for key in keys]:
        bbdat.drop('rowid', axis=1, inplace=True)

    #Construct empty dictionaries with null values to be populated later; basically initializing
    # all values to keep track of the dictionaries within dictionaries. This is for my own sanity;
    # I am unsure if it would be better to create them later on.
    bbstats = dict.fromkeys(["record.count", "complete.cases", "player.count", "team.count",
                             "league.count", "bb", "nl", "al", "records"])
    bbstats["nl"] = dict.fromkeys(["dat", "players", "teams"])
    bbstats["al"] = dict.fromkeys(["dat", "players", "teams"])
    bbstats["records"] = dict.fromkeys(["obp", "pab", "hr", "hrp", "h", "hp", "sb", "sbp", "so",
                                        "sop", "sopa", "bb", "bbp", "g"])
    #I didn't want to use a for loop and instead use a list comprehension, but I was not sure
    # how to structure it as bbstats["records"][key] = [list comprehension]
    for key in bbstats["records"].keys():
        bbstats["records"][key] = dict.fromkeys(["id", "value"])

    # count number of records
    bbstats["record.count"] = len(bbdat)

    #tuple form of min year, max year
    bbstats["years"] = (int(bbdat["year"].min()), int(bbdat["year"].max()))

    #unique player count - no double-count
    bbstats["player.count"] = get_count(bbdat,"id")

    #unique team count - no double-count
    bbstats["team.count"] = get_count(bbdat, "team")

    #unique league count - no double-count
    bbstats["league.count"] = get_count(bbdat, "lg")

    # count number of complete cases
    bbstats["bb"] = bbdat.dropna()
    #Could also use .shape[0] here
    bbstats["complete.cases"] = len(bbstats["bb"])

    # Adding columns to bb DataFrame for obp and pab by creating new Series to concatenate to the bb DataFrame.
    # Is it okay to do the calculations inside the .Series() function call because it might be a little hard to read.
    obp_ser = pd.Series((bbstats["bb"]["h"] + bbstats["bb"]["bb"] + bbstats["bb"]["hbp"]) /
                        (bbstats["bb"]["ab"] + bbstats["bb"]["bb"] + bbstats["bb"]["hbp"]),
                        name='obp')
    pab_ser = pd.Series((bbstats["bb"]["h"] + bbstats["bb"]["bb"] + bbstats["bb"]["hbp"] + bbstats["bb"]["sf"]
                         + bbstats["bb"]["sh"]) / (bbstats["bb"]["ab"] + bbstats["bb"]["bb"] + bbstats["bb"]["hbp"] +
                                                   bbstats["bb"]["sf"] + bbstats["bb"]["sh"]), name='pab')
    bbstats["bb"] = pd.concat([bbstats["bb"], obp_ser, pab_ser], axis=1)

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

    #separate the keys in bbrecords into keys for metrics already existing in the dataset and keys that
    # need further calculations. Calculated keys is a tuple containing the metric that is given as a percentage
    # and the metric name.
    existing_keys = ["obp","pab","hr","h","sb","so","bb","g"]
    calculated_keys = [("hr","hrp"), ("h","hp"), ("sb","sbp"), ("so","sop"), ("so","sopa"), ("bb","bbp")]

    for key in existing_keys:
        #Iterate through all records and call helper method to find index with the largest value
        #Using that index, locate player ID and record value and populate the dictionary with them.
        index = get_highest_record(bbrecords, key)
        bbstats["records"][key]["id"] = bbrecords["id"][index]
        bbstats["records"][key]["value"] = bbrecords[key][index]

    for key in calculated_keys:
        #TODO: The problem is here where the program is not locating the correct max value. I think I'm going to try
        #   a new approach where instead of finding the index, i'm going to find the actual max value and then find
        #   player ID based on that max value? Idk if idxmax() is the easiest way to find values. The code runs just
        #   fine and populates the dictionary with actual values. It is the values themselves that are not the maximum.
        #   I know that I am calculating the statistics correctly because they calculations pass the execution test. The
        #   problem is purely locating that maximum value.
        calc_series = calc_percentage_ab_stats(bbrecords, key)
        bbrecords = pd.concat([bbrecords, calc_series], axis=1)
        index = get_highest_record(bbrecords, key[1])
        bbstats["records"][key[1]]["id"] = bbrecords["id"][index]
        bbstats["records"][key[1]]["value"] = bbrecords[key[1]][index]


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

def get_highest_record(df, col=""):
    """
    Finds the index of the highest value in a specified column of a DataFrame. D
    Args:
        df (Pandas DataFrame or Pandas Series): DataFrame that contains the records
        col (str): column in which you find the max value in

    Returns: index of row containing max value
    """
    if not isinstance(col, str) or not isinstance(df, pd.DataFrame):
        return math.nan

    # Call idxmax on only one column, so that only 1 index value is returned
    # Use axis=0 because we want the row index for max value within a column
    return df[col].idxmax()

def calc_percentage_ab_stats(df, metric):
    """
    Method that calculates a metric as a percentage at bat and returns a series containing
    the new calculations. Special calculations for sopa
    Args:
        df (Pandas DataFrame): DataFrame that contains the records
        metric (tuple of str): tuple containing the metric that is given as a percentage and the metric name
            tuple SHOULD be in the format of (column name of given metric, name of new metric)

    Returns: Series containing the new metric calculates
    """
    #if not isinstance(df, pd.DataFrame):
        #return math.nan
   # elif not any([isinstance(val, str) for val in metric]):
        #return math.nan

    #Split the tuple into a key and column
    col = metric[0]
    key = metric[1]

    if key == "sopa":
        return pd.Series(df[col] / (df["ab"] + df["bb"] + df["hbp"] + df["sh"] + df["sf"]), name=key)
    else:
        return pd.Series(df[col] / df["ab"], name=key)



