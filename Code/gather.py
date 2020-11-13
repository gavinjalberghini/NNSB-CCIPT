"""
# Author: Gavin Alberghini
# Date: 10/29/19
# File: gather.py
# Purpose: The function of this file is to collect data from swells point and convert it into csv files
# API Source: https://tidesandcurrents.noaa.gov/api/
"""

import csv
import sys
import os.path
import noaa_coops as nc
import pandas
import pprint

# Constant data used to hit NOAA API
CONST_SWELL_ID = 8638610
CONST_PRODUCTS = ["water_level", "high_low"]
CONST_BEGIN_YEAR = 2000
CONST_END_YEAR = 2019
CONST_DATUM = "MTL"
CONST_UNIT = "english"
CONST_TIME_ZONE = "lst"

# Create data folder if it does not exist in the project directory
if os.path.exists("Data"):
    pass
else:
    os.mkdir("Data")

# Initialize connection to Swells_Point and water/tide DataFrames
swells_point = nc.Station(CONST_SWELL_ID)
df_water_levels = pandas.DataFrame()
df_tide_levels = pandas.DataFrame()

# Hit Swells_Point for tide data using NOAA API and push the data to a csv
print("Collecting tide data from Swells Point: ")
for i in range(CONST_BEGIN_YEAR, CONST_END_YEAR):
    percent = 100 * float((i - CONST_BEGIN_YEAR)) / float((CONST_END_YEAR - CONST_BEGIN_YEAR))
    if i == CONST_END_YEAR - 1:
        percent = 100
    sys.stdout.write("\r%d%%" % percent)
    sys.stdout.flush()
    begin_date = str(i) + "0101"
    end_date = str(i+1) + "0101"
    temp = swells_point.get_data(begin_date, end_date, CONST_PRODUCTS[1], CONST_DATUM, CONST_UNIT, CONST_TIME_ZONE)
    df_tide_levels = pandas.concat([temp, df_tide_levels], axis=0)
df_tide_levels.to_csv("Data/Tides.csv")

# Hit Swells_Point for water level data using NOAA API and push the data to a csv
print()
print("Collecting water level data from Swells Point: ")
for i in range(CONST_BEGIN_YEAR, CONST_END_YEAR):
    percent = 100 * float((i - CONST_BEGIN_YEAR)) / float((CONST_END_YEAR - CONST_BEGIN_YEAR))
    if i == CONST_END_YEAR - 1:
        percent = 100
    sys.stdout.write("\r%d%%" % percent)
    sys.stdout.flush()
    begin_date = str(i) + "0101"
    end_date = str(i+1) + "0101"
    temp = swells_point.get_data(begin_date, end_date, CONST_PRODUCTS[0], CONST_DATUM, CONST_UNIT, CONST_TIME_ZONE)
    df_water_levels = pandas.concat([temp, df_water_levels], axis=0)
df_water_levels.to_csv("Data/Sea_Level.csv")

