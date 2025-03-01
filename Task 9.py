## Task 9
"""
1. Take the median of each hour of one sensor
2. Treshold is 0.5
3. Take the same sensor's self imputed values
4. Start with the small amount of days and see where the self imputed data reaches the treshold 
(get the medians each hour of 1 day, 2 days, 4 days... and compare them with real data)
"""

import pandas as pd

sensor_positions = pd.DataFrame(pd.read_csv("data/sensor_positions.csv", header=None, names=['location', 'name']))

def prepare_dataframe(df):
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset=["Time"], keep=False).copy()
    df["hour"] = df["Time"].dt.hour
    return df

def get_medians_of_real_data(name):
    data = prepare_dataframe(pd.DataFrame(pd.read_csv(f'data/data SPL August 2022 all/{name}-data.csv')))
    grouped_by_hour = data.groupby('hour')
    medians = grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians

def get_medians_of_self_imputed_data(name, days):
    data = prepare_dataframe(pd.DataFrame(pd.read_csv(f'imputed_data/self/{name}-self.csv'))).head(days * 1440)
    grouped_by_hour = data.groupby('hour')
    medians = grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians

for location, name in sensor_positions.values:
    real_medians = get_medians_of_real_data(name).set_index("hour")

    for days in range(1, 15):
        imputed_medians = get_medians_of_self_imputed_data(name, days)
        real_medians[f'days_{days}'] = (real_medians['dt_sound_level_dB'] - imputed_medians['dt_sound_level_dB']).between(-0.5, 0.5)
    
    real_medians.to_csv(f'imputed_data/treshold_analysis/{name}-treshold.csv')
