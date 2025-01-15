### Fill the missing data based on 3 nearest sensors.

import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

# ============== PREPARE SENSOR POSITIONS ===================
# location = [longitude, latitude] NB! usually other way around

def set_correct_type(loc):
    # change datatype and shape to [lat, lon]
    return np.array(loc.strip('()').split(), dtype=float)[::-1]

sensor_positions = pd.DataFrame(pd.read_csv("data/sensor_positions.csv", header=None, names=['location', 'name']))
sensor_positions["location"] = sensor_positions["location"].apply(set_correct_type)

# ============== PREPARE SENSOR POSITIONS ===================


def get_data_with_nans(df):
    full_time_range = pd.date_range(start=df["Time"].min(), end=df["Time"].max(), freq="min")
    df = df.set_index("Time").reindex(full_time_range)
    df = df.rename_axis("Time").reset_index()
    df["time_diff"] = df["Time"].diff().dt.total_seconds()
    df["dt_sound_level_dB"] = np.where((df["time_diff"] == 60) | (df.index == 0), df["dt_sound_level_dB"], np.nan)
    df = df.drop(columns=["time_diff"])
    return df

def get_dataframe_without_duplicates(df):
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset=["Time"], keep=False) 
    return df

def set_time_as_index(df):
    return df.set_index('Time')

def get_sensor_data(name):
    return pd.DataFrame(pd.read_csv(f'data/data SPL August 2022 all/{name}-data.csv'))

def get_nearest_indices(query_point):
    coordinates_in_radians = np.radians(sensor_positions['location'].tolist())
    query_point_in_radians = np.array(np.radians(query_point)).reshape(1, -1) 

    sensor_positions_tree = BallTree(coordinates_in_radians, metric='haversine')
    _, indices = sensor_positions_tree.query(query_point_in_radians, k=4)

    return indices[0]

def get_nearest_name(index):
    location, name = sensor_positions.iloc[index]
    print(location, name)
    return name

def get_main_df(name):
    return set_time_as_index(get_data_with_nans(get_dataframe_without_duplicates(get_sensor_data(name))))

def get_nearest_df(name):
    return set_time_as_index(get_dataframe_without_duplicates(get_sensor_data(name)))


# What should I do with the ones that have no values in three nearest ones?
# Should I save the values in some other csv file?

# used https://latitude.to/ to check the distances

# Create 5 tables of randomly picked locations and their nearest neighbor db values
for i in [10, 47, 68, 150, 241]:
    location, name = sensor_positions.iloc[i]
    print("==================================")
    print(location, name, "<= MAIN")
    nearest_indices = get_nearest_indices(location)

    main_df = get_main_df(name)

    # 0th index is itself
    first_nearest_df = get_nearest_df(get_nearest_name(nearest_indices[1]))
    second_nearest_df = get_nearest_df(get_nearest_name(nearest_indices[2]))
    third_nearest_df = get_nearest_df(get_nearest_name(nearest_indices[3]))

    main_df['db_first_nearest'] = first_nearest_df['dt_sound_level_dB']
    main_df['db_second_nearest'] = second_nearest_df['dt_sound_level_dB']
    main_df['db_third_nearest'] = third_nearest_df['dt_sound_level_dB']

    main_df.to_csv(f'nearest/{name}-nearest.csv')
    
    
