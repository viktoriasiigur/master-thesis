"""
## Task 6 
1. Find a treshold (110m)
2. Impute all the sensor in this circle
3. Switch main sensors imputation with the median value of all of these. (round median values up)
4. Do bland altman plot of one sensor imputation vs nearest sensor imputation
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree

EARTH_RADIUS_METERS = 6378137
MAX_RADIUS_IN_RADIANS = 110 / EARTH_RADIUS_METERS # Treshold

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

def set_hour_minute_columns(df):
    df["hour"] = df["Time"].dt.hour
    df["minute"] = df["Time"].dt.minute
    return df

def get_sensor_data(name):
    return pd.DataFrame(pd.read_csv(f'data/data SPL August 2022 all/{name}-data.csv'))

def get_nearest_indices(query_point):
    coordinates_in_radians = np.radians(sensor_positions['location'].tolist())
    query_point_in_radians = np.array(np.radians(query_point)).reshape(1, -1) 

    sensor_positions_tree = BallTree(coordinates_in_radians, metric='haversine')
    nearest_indices = sensor_positions_tree.query_radius(query_point_in_radians, r=MAX_RADIUS_IN_RADIANS)[0]
    return nearest_indices

def get_nearest_name(index):
    location, name = sensor_positions.iloc[index]
    print(location, name)
    return name

def get_main_df(name):
    return set_time_as_index(set_hour_minute_columns(get_data_with_nans(get_dataframe_without_duplicates(get_sensor_data(name)))))

def get_nearest_df(name):
    return set_time_as_index(get_dataframe_without_duplicates(get_sensor_data(name)))



# ============== IMPUTE DATA ===================
def get_medians(group):
    if (group.notna().any()):
        return np.ceil(group.median())

def get_imputed_data(df, column="dt_sound_level_dB"):
    group = df.groupby(["hour", "minute"])[column]
    imputed_values = group.transform(get_medians)
    if imputed_values.isna().any():
        imputed_values = imputed_values.interpolate(method="linear", limit_direction="both").round()
        
    df[column] = df[column].fillna(imputed_values)
    return df

# ============== IMPUTE DATA ===================


# Create 5 tables of randomly picked locations and their nearest neighbor db values
# for i in [10, 47, 68, 150, 241]:
#     location, name = sensor_positions.iloc[i]
#     print("==================================")
#     print(location, name, "<= MAIN")
#     nearest_indices = get_nearest_indices(location)

#     main_df = get_main_df(name)

#     print(main_df.index)

#     for nearest_index in nearest_indices:
#         sensor_name = get_nearest_name(nearest_index)
#         df_of_nearest = get_nearest_df(get_nearest_name(nearest_index))
#         main_df[sensor_name] = get_imputed_data(df_of_nearest)

    
#     print(main_df)

    # 0th index is itself
    # first_nearest_df = get_nearest_df(get_nearest_name(nearest_indices[1]))
    # second_nearest_df = get_nearest_df(get_nearest_name(nearest_indices[2]))
    # third_nearest_df = get_nearest_df(get_nearest_name(nearest_indices[3]))

    # main_df['db_first_nearest'] = first_nearest_df['dt_sound_level_dB']
    # main_df['db_second_nearest'] = second_nearest_df['dt_sound_level_dB']
    # main_df['db_third_nearest'] = third_nearest_df['dt_sound_level_dB']

    # main_df.to_csv(f'nearest/{name}-nearest.csv')
    
    
# ============== GENERATE SELF IMPUTED DATA ===================

def generate_self_imputed_data():
    for _, name in sensor_positions.values:
        main_df = get_main_df(name) 
        imputed_df = get_imputed_data(main_df)
        imputed_df = imputed_df.drop(columns=["hour", "minute"])
        imputed_df.to_csv(f'imputed_data/self/{name}-self.csv')

generate_self_imputed_data()

# ============== GENERATE SELF IMPUTED DATA ===================


# ============== GENERATE NEAREST IMPUTED DATA ===================

# def generate_nearest_imputed_data():
#     for location, name in sensor_positions.values[:2]:
#         main_df = get_main_df(name) 
#         nearest_indices = get_nearest_indices(location)
#         for nearest_index in nearest_indices:
#             nearest_name = get_nearest_name(nearest_index)
#             df_of_nearest = get_nearest_df(nearest_name)
#             main_df[f"{nearest_name}_nearest"] = df_of_nearest

#         for col in main_df.filter(like="_nearest").columns:
#             main_df = get_imputed_data(main_df, col)


#         print(main_df)
#         # imputed_df = imputed_df.drop(columns=["hour", "minute"])
#         # imputed_df.to_csv(f'imputed_data/nearest/{name}-nearest.csv')

# # ============== GENERATE NEAREST IMPUTED DATA ===================

# generate_nearest_imputed_data()