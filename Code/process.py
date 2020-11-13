"""
# Author: Gavin Alberghini
# Date: 10/29/19
# File: process.py
# Purpose: The function of this file is to filter data, calculate regressions, and find weighted averages to
#          use for predictions
"""

import pandas as pd
import numpy as np
import sqlite3
import dbfread
import geopy.distance as geo
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import time

# Set the lat lon location for NNSB
CONST_NNSB_LOC = (36.977711, -76.430351)


# Plot x/y data and make a polynomial regression on it
def regress_data(data):
    x = []
    y = []

    for tup in data:
        x.append(tup[0])
        y.append(tup[1])

    x = np.asarray(x)
    x = np.reshape(x, (-1, 1))

    poly = PolynomialFeatures(degree=4)
    x_poly = poly.fit_transform(x)

    poly.fit(x_poly, y)
    lin2 = LinearRegression()
    lin2.fit(x_poly, y)

    plt.scatter(x, y, color='blue')

    plt.plot(x, lin2.predict(poly.fit_transform(x)), color='red')
    plt.title('Polynomial Regression')

    plt.show()


# Given an x value predict the associated y value
def make_prediction(data, guess):
    x = []
    y = []

    for tup in data:
        x.append(tup[0])
        y.append(tup[1])

    x = np.asarray(x)
    x = np.reshape(x, (-1, 1))

    poly = PolynomialFeatures(degree=4)
    x_poly = poly.fit_transform(x)
    lin = LinearRegression()
    lin.fit(x_poly, y)

    guess = guess * 10000000000 + x[0]

    guess = np.asarray(guess)
    guess = np.reshape(guess, (-1, 1))

    return lin.predict(poly.fit_transform(guess))


# Calculate a weighted average between land subsidence rates
def calculate_weighted_avg(data):
    dist_sum = sum(i for i, j, k in data)
    weighted_vals = []
    uncertanty = []

    for x in data:
        weight = float(x[0])/float(dist_sum)
        weight = 1 - weight
        weighted_vals.append(weight * x[1])
        uncertanty.append(x[2])

    uncert = sum(uncertanty)
    res = (sum(weighted_vals) - uncert, sum(weighted_vals), sum(weighted_vals) + uncert)

    return res


# Fetch land data from SQLite db
def get_land_data(cursor):
    cursor.execute("SELECT Latitude, Longitude, Vertical_Vel, Uncertainty FROM Land_Subsidence")
    qry_res = cursor.fetchall()
    res = []

    for x in qry_res:
        station_cord = (x[0], x[1])
        dist = geo.distance(CONST_NNSB_LOC, station_cord).km
        res.append((dist, x[2], x[3]))

    return res


# Fetch sea data from SQLite db
def get_sea_data(cursor):
    cursor.execute("SELECT Collection_Dates, Collection_Time, Water_Level FROM Sea_Level")
    qry_res = cursor.fetchall()
    res = []

    for x in qry_res:
        x_val = x[0].replace("-", "")
        x_val += x[1].replace(":", "")

        y_val = str(x[2])
        if "e" in y_val:
            degree = int(y_val[-1])
            if y_val[0] == "-":
                y_val = float(y_val[:5])
            else:
                y_val = float(y_val[:4])
            y_val = y_val * (10 ** -degree)

        res.append((int(x_val), float(y_val)))

    return res


# Fetch tide data from SQLite db
def get_tide_data(cursor, tide):

    if tide == "LOW":
        cursor.execute("SELECT Date, LL_Time, LL_Water_Level FROM Tides")
        qry_res = cursor.fetchall()
        res = []
    else:
        cursor.execute("SELECT Date, HH_Time, HH_Water_Level FROM Tides")
        qry_res = cursor.fetchall()
        res = []

    for x in qry_res:

        if x[0] == "?" or x[1] == "?":
            pass
        else:
            date = x[0].replace("-", "")
            t = x[1].replace(":", "")
            wl = x[2]
            res.append((int(date + t), float(wl)))

    return res


def apply(year, tide):
    # Connect to SQLite database
    conn = sqlite3.connect('Data/NNSB_CLIMATE_IMPACT.db')
    cur = conn.cursor()

    # Process land subsidence data
    land_data = get_land_data(cur)
    print("Grabbed Land Subsidence Data...")

    land_sub = calculate_weighted_avg(land_data)
    print("Made Land Subsidance Calculation...")

    # Process sea level data
    sea_data = get_sea_data(cur)
    print("Grabbed Sea Level Data...")

    # Process tide level data
    tide_data = get_tide_data(cur, tide)
    print("Grabbed Tide Data...")

    if tide == "HIGH" or tide == "LOW":
        temp = make_prediction(tide_data, year)
    else:
        temp = make_prediction(sea_data, year)
    print("Made Prediction...")

    water_change = temp[0] + (-1 * land_sub[1] * year / 1000 * 3.28)
    print("Water Elevation Change: " + str(water_change))

    res_str = "{0:.3f}".format(water_change)

    # Close SQLite connection
    conn.close()
    return "Water Level Displacement " + res_str + "ft"
