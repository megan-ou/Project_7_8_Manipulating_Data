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

    #Execution test data does not have a rowid column (first column), dropping that column so they are equal. (This helped us
    # pass more tests?) I don't like this as a solution, but it is a bit of a brute-force to get things to equal up.
    # Could I get an explanation of what went wrong here?
    bbdat.drop(bbdat.columns[0],axis=1,inplace=True)
    #This code below doesn't work because for some reason it cannot find rowid?
    #keys = bbdat.keys()
    #if [key == "rowid" for key in keys]:
        #bbdat.drop('rowid', axis=1, inplace=True)

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
    obp_ser = calc_obp(bbstats["bb"])
    pab_ser = calc_pab(bbstats["bb"])
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
    # Find all records in bb DataFrame with >= 50 career at bats
    bbrecords = get_dat_subset(bbstats["bb"], "ab", "50", ">=")
    #Aggregate by id and get a list of all players with >= 50 career at bats.
    bbrecords = bbrecords.groupby(["id"]).sum()
    record_players = pd.Series(bbrecords.index.tolist(), name="id")

    #Aggregate bb DataFrame using groupby to calculate total career stats per player id. Do NOT use bbrecords yet
    # because it will drop career stats for players in years before they have 50 career at bats, we will be missing
    # some numbers.
    # Drop obp and pab because we want to recalculate it based on aggregated stats.
    bbrecords_agg = bbstats["bb"].drop('obp',axis=1).drop('pab',axis=1).groupby(["id"]).sum()
    #Recalculate the aggregate obp and pab
    obp_ser = calc_obp(bbrecords_agg)
    pab_ser = calc_pab(bbrecords_agg)
    bbrecords_agg = pd.concat([bbrecords_agg, obp_ser, pab_ser], axis=1)

    #Now we need to compare the list of players to the indexes of bbrecords_agg and drop any row that does not match.
    # This way we have only players with at least 50 career at bats with an aggregate value of their entire career stats.
    merge_df = pd.merge(record_players, bbrecords_agg, left_on="id", right_index=True, how="inner")

    #separate the keys in bbrecords into keys for metrics already existing in the dataset and keys that
    # need further calculations. Calculated keys is a tuple containing the metric that is given as a percentage
    # and the metric name.
    existing_keys = ["obp","pab","hr","h","sb","so","bb","g"]
    calculated_keys = [("hr","hrp"), ("h","hp"), ("sb","sbp"), ("so","sop"), ("so","sopa"), ("bb","bbp")]

    for key in existing_keys:
        #Iterate through all records and call helper method to find the max value and corresponding player id.
        max_val = get_highest_record(merge_df, key)
        #further debugging: prnt key values
        bbstats["records"][key]["id"] = max_val[0]
        bbstats["records"][key]["value"] = max_val[1]

    for key in calculated_keys:
        calc_series = calc_percentage_ab_stats(merge_df, key)
        merge_df = pd.concat([merge_df, calc_series], axis=1)
        max_val = get_highest_record(merge_df, key[1])
        bbstats["records"][key[1]]["id"] = max_val[0]
        bbstats["records"][key[1]]["value"] = max_val[1]

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
    Finds the index of the highest value in a specified column of a DataFrame. D
    Args:
        df (Pandas DataFrame or Pandas Series): DataFrame that contains the records
        col (str): column in which you find the max value in

    Returns: index of row containing max value
    """
    if not isinstance(col, str) or not isinstance(df, pd.DataFrame):
        return math.nan

    value = df[col].max()
    id = df[col].idxmax()
    name = df.at[id,"id"]

    return (name, value)
    # Call idxmax on only one column, so that only 1 index value is returned
    # Use axis=0 because we want the row index for max value within a column
    #return df[col].idxmax()

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

def calc_obp(df):
    """
    Method to calculate on base percentage based on a given DataFrame
    Args:
        df (Pandas DataFrame): DataFrame that contains the stats

    Returns: Series containing all obp

    """
    if not isinstance(df, pd.DataFrame):
        return math.nan

    obp = pd.Series((df["h"] + df["bb"] + df["hbp"]) / (df["ab"] + df["bb"] + df["hbp"]), name='obp')
    return obp

def calc_pab(df):
    """
    Method to calculate productive at bats based on a given DataFrame
    Args:
        df (Pandas DataFrame): DataFrame that contains the stats

    Returns: Series containing all pab

    """
    if not isinstance(df, pd.DataFrame):
        return math.nan

    pab = pd.Series((df["h"] + df["bb"] + df["hbp"] + df["sf"] + df["sh"]) /
              (df["ab"] + df["bb"] + df["hbp"] + df["sf"] + df["sh"]), name='pab')

    return pab
