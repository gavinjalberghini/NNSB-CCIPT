"""
# Author: Gavin Alberghini
# Date: 10/29/19
# File: push.py
# Purpose: The function of this file it to consolidate, convert, and upload data from a local repository to SQLite
"""

import pandas as pd
import sqlite3
from dbfread import DBF

# Set constants for SQL table schema
CONST_LAND_SUB_CSV = "Data/Land_Subsidence.csv"
CONST_SEA_LEVEL_CSV = "Data/Sea_Level.csv"
CONST_TIDES_CSV = "Data/Tides.csv"
CONST_STORM_CSV = "Data/Storm_Surge.csv"
CONST_UID_COL_NAME = "UID"
CONST_UNIT_COL_NAME = "Unit_UID"
CONST_DATA_DUR_COL_NAME = "Data_Duration_UID"
CONST_MMPERYR_INDEX = 0
CONST_FEET_INDEX = 1
base_uid = 0


# Generate a unique identification number
def generate_uid():
    global base_uid
    base_uid = base_uid + 1
    return base_uid


# Conver noise in data to a standard value
def fill(df):
    df = df.fillna("?")
    df = df.replace(" ", "?")
    df = df.replace("~", "?")
    df = df.replace("", "?")
    return df


# Build unit table in SQLite
def build_unit_table(connection):
    df = pd.DataFrame()
    uid_col = [CONST_MMPERYR_INDEX, CONST_FEET_INDEX]
    unit_col = ["mm/yr", "ft"]

    df.insert(0, "Unit", unit_col, True)
    df.insert(0, CONST_UID_COL_NAME, uid_col, True)

    df.to_sql("Unit", connection)


# Build tide table in SQLite
def build_tide_table(df, connection):
    col_len = len(df.index)
    uid_col = []
    unit_uid_col = []
    date_col = []

    hh_time_col = []
    h_time_col = []
    l_time_col = []
    ll_time_col = []
    hh_water_level_col = []
    h_water_level_col = []
    l_water_level_col = []
    ll_water_level_col = []

    for x in range(0, col_len):
        uid_col.append(generate_uid())
        date_col.append(df.iloc[x][0])

        if len(str.split(df.iloc[x][7])) == 2:
            ll_time_col.append(str.split(df.iloc[x][7])[1])
        else:
            ll_time_col.append("?")

        if len(str.split(df.iloc[x][5])) == 2:
            l_time_col.append(str.split(df.iloc[x][5])[1])
        else:
            l_time_col.append("?")

        if len(str.split(df.iloc[x][3])) == 2:
            h_time_col.append(str.split(df.iloc[x][3])[1])
        else:
            h_time_col.append("?")

        if len(str.split(df.iloc[x][1])) == 2:
            hh_time_col.append(str.split(df.iloc[x][1])[1])
        else:
            hh_time_col.append("?")

        hh_water_level_col.append(df.iloc[x][2])
        h_water_level_col.append(df.iloc[x][4])
        l_water_level_col.append(df.iloc[x][6])
        ll_water_level_col.append(df.iloc[x][8])
        unit_uid_col.append(CONST_FEET_INDEX)

    df = pd.DataFrame()

    df.insert(0, CONST_UID_COL_NAME, uid_col, True)
    df.insert(1, "Date", date_col, True)
    df.insert(2, "HH_Time", hh_time_col, True)
    df.insert(3, "HH_Water_Level", hh_water_level_col, True)
    df.insert(4, "H_Time", h_time_col, True)
    df.insert(5, "H_Water_Level", h_water_level_col, True)
    df.insert(6, "L_Time", l_time_col, True)
    df.insert(7, "L_Water_Level", l_water_level_col, True)
    df.insert(8, "LL_Time", ll_time_col, True)
    df.insert(9, "LL_Water_Level", ll_water_level_col, True)
    df.insert(10, CONST_UNIT_COL_NAME, unit_uid_col, True)

    df.to_sql("Tides", connection)


# Build sea table in SQLite
def build_sea_table(df, connection):
    col_len = len(df.index)
    uid_col = []
    unit_uid_col = []
    date_col = []
    time_col = []

    for x in range(0, col_len):
        date_time = df.iloc[x][0]
        tmp = date_time.split(' ')
        date_col.append(tmp[0])
        time_col.append(tmp[1])
        uid_col.append(generate_uid())
        unit_uid_col.append(CONST_FEET_INDEX)

    df = df.drop(columns=["date_time"])

    df.rename(columns={'water_level': 'Water_Level'}, inplace=True)
    df.rename(columns={'sigma': 'Sigma'}, inplace=True)
    df.rename(columns={'flags': 'Flags'}, inplace=True)
    df.insert(4, CONST_UNIT_COL_NAME, unit_uid_col, True)
    df.insert(0, "Collection_Time", time_col, True)
    df.insert(0, "Collection_Dates", date_col, True)
    df.insert(0, CONST_UID_COL_NAME, uid_col, True)

    df.to_sql("Sea_Level", connection)


# Prepare land data for SQL schema format
def transform_land(df):
    col_len = len(df.index)
    uid_col = []
    unit_uid_col = []

    for x in range(0, col_len):
        uid_col.append(generate_uid())
        unit_uid_col.append(CONST_MMPERYR_INDEX)

    col_order = ["Name", "Status", "Decommission Date", "lat", "long", "Lat_Long Update Date", "Time Period",
                 "VertVel(mm/yr)", "UncertVertVel(mm/yr)", "Website"]
    df = df.reindex(columns=col_order)

    df.insert(0, CONST_UID_COL_NAME, uid_col, True)
    df.insert(10, CONST_UNIT_COL_NAME, unit_uid_col, True)

    df.columns = [CONST_UID_COL_NAME, "Name", "Status", "Decommission_Date", "Latitude", "Longitude",
                  "Position_Update_Date", CONST_DATA_DUR_COL_NAME, "Vertical_Vel", "Uncertainty", CONST_UNIT_COL_NAME,
                  "Website"]

    return df


# Build land table in SQLite
def build_land_tables(df, connection):
    data_dur_df = pd.DataFrame(columns=["UID", "Begin_Date", "End_Date"])

    for x in range(0, len(df.index)):
        y = generate_uid()
        time_dur = df.iloc[x][CONST_DATA_DUR_COL_NAME]
        times = time_dur.split('–')
        temp = pd.Series([y, times[0], times[1]], index=data_dur_df.columns)
        data_dur_df = data_dur_df.append(temp, ignore_index=True)
        df.at[x, CONST_DATA_DUR_COL_NAME] = y

    df.to_sql("Land_Subsidence", connection)
    data_dur_df.to_sql("Data_Duration", connection)


# Establish SQLite connection
conn = sqlite3.connect('Data/NNSB_CLIMATE_IMPACT.db')
cur = conn.cursor()

# Clear any tables that exist
cur.execute("DROP TABLE IF EXISTS Land_Subsidence;")
cur.execute("DROP TABLE IF EXISTS Tides;")
cur.execute("DROP TABLE IF EXISTS Sea_Level;")
cur.execute("DROP TABLE IF EXISTS Unit;")
cur.execute("DROP TABLE IF EXISTS Data_Duration;")

# Get data from csv files in Data folder
land_data = pd.read_csv(CONST_LAND_SUB_CSV)
sea_level_data = pd.read_csv(CONST_SEA_LEVEL_CSV)
tide_data = pd.read_csv(CONST_TIDES_CSV)
## storm_data = pd.read_csv(CONST_STORM_CSV)

# Filter noisy values out of tables
land_data = fill(land_data.copy())
sea_level_data = fill(sea_level_data.copy())
tide_data = fill(tide_data.copy())
## storm_data = fill(storm_data.copy())

land_data = transform_land(land_data.copy())

# Build SQL schema
build_unit_table(conn)
print("Building Unit Table")

build_land_tables(land_data.copy(), conn)
print("Building Land Subsidence Table")

build_sea_table(sea_level_data.copy(), conn)
print("Building Sea Level Table")

build_tide_table(tide_data.copy(), conn)
print("Building Tide Table")

## build_storm_table(storm_data.copy(), conn)

# Write out SQL schema to a .sql file and close the connection
with open('Data/NNSB_CLIMATE_IMPACT.sql', 'w') as f:
    for line in conn.iterdump():
        f.write('%s\n' % line)
conn.close()
