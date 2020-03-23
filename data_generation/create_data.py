import pandas as pd
import numpy as np
import os
import pathlib
import ijson
from datetime import datetime, timedelta
from collections import namedtuple
import json
import geopandas
import matplotlib.pyplot as plt
import time
import random



def str_time_prop(start, end, format):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + random.random() * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def random_date(x, start, end):
    """
    Function to apply to date column of a pandas df generating random timestamps
    :return:
    :rtype:
    """
    return str_time_prop(start, end, '%d/%m/%Y %I:%M:%S')


def generate_random_coordinate(center_lat, center_lon, radius):
    """
    Generate a random coordinate in a circle with given radius around the given center
    """
    # radius in degrees
    r = radius/ 111300
    u = np.random.random()
    v = np.random.random()
    w = r * np.sqrt(u)
    t = 2 * np.pi * v
    x = w * np.cos(t)
    x1 = x / np.cos(center_lon)
    y = w * np.sin(t)
    return (center_lat+x1, center_lon +y)


def create_locations(n, center_lat=52.520659 , center_lon=13.411305, radius= 20000):
    """
    Create n sample locations in a circle around the given center coordinate, with a given radius
    :param n: number of examples
    :param center_lat:
    :param center_lon:
    :param radius:
    :type radius:
    :return: two lists containing latitudes and longitudes
    """
    new_coords = []
    for i in range(n):
        new_coords.append(generate_random_coordinate(center_lat, center_lon, radius))
    new_coords_lat, new_cords_lon = zip(*new_coords)
    return new_coords_lat, new_cords_lon


def create_data_set(n, n_per_id, center_lat=52.520659, center_lon=13.411305, r=20000, start_date="09/03/2020 12:00:00",
                    end_date="23/03/2020 12:00:00", save=True):
    """
    Creates dataset simulating gps movement profiles of infected people
    :param n: number of samples to generate, one sample corresponds to one infected person
    :param n_per_id: number of samples per unique id
    :param center_lat: latitude of central coordinate
    :param center_lon: longitude of central coordinate
    :return:
    """
    columns = ['id', 'time', 'lat', 'lon', 'accuracy', 'IN_VEHICLE', 'STILL',
               'ON_BICYCLE', 'ON_FOOT', 'UNKNOWN', 'TILTING', 'EXITING_VEHICLE',
               'infection_risk']

    ids = range(int(n))

    df = pd.DataFrame(columns=columns)
    for id in ids:
        id_df = pd.DataFrame(columns=columns)
        lats, lons = create_locations(n_per_id, center_lat, center_lon, r)
        id_df["lat"] = lats
        id_df["lon"] = lons
        id_df["id"] = id
        id_df["time"] = id_df["time"].apply(random_date, args=(start_date, end_date))
        # Sampling of accuracy and activies based on distributions of my own data, which i wont make publicly available,
        # can be set as desired
        # Number missing data also based on my personal data can be set
        id_df["accuracy"] = id_df["accuracy"].apply(lambda x: np.random.normal(loc=51.48, scale=32.90))
        id_df["IN_VEHICLE"] = id_df["IN_VEHICLE"].apply(
            lambda x: np.random.normal(loc=26.75, scale=24.38) if np.random.random()
                                                                  < 0.149 else "NaN")
        id_df["STILL"] = id_df["STILL"].apply(lambda x: np.random.normal(loc=64.08, scale=37.27) if np.random.random()
                                                                                                    < 0.24 else "NaN")
        id_df["ON_BICYCLE"] = id_df["ON_BICYCLE"].apply(
            lambda x: np.random.normal(loc=8.24, scale=8.62) if np.random.random()
                                                                < 0.102 else "NaN")
        id_df["ON_FOOT"] = id_df["ON_FOOT"].apply(
            lambda x: np.random.normal(loc=24.30, scale=29.94) if np.random.random()
                                                                  < 0.11 else "NaN")
        id_df["UNKNOWN"] = id_df["UNKNOWN"].apply(
            lambda x: np.random.normal(loc=16.87, scale=22.21) if np.random.random()
                                                                  < 0.146 else "NaN")
        id_df["TILTING"] = id_df["TILTING"].apply(lambda x: np.random.normal(loc=100, scale=0.0) if np.random.random()
                                                                                                    < 0.125 else "NaN")
        id_df["EXITING_VEHICLE"] = id_df["EXITING_VEHICLE"].apply(
            lambda x: np.random.normal(loc=100, scale=0) if np.random.random()
                                                            < 0.005 else "NaN")

        df = pd.concat([df, id_df], ignore_index=True)
    if save:
        df.to_csv("berlin_data.csv")
    return df



if __name__ == '__main__':
    create_data_set(300, 10000)
