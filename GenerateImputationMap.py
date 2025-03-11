## Task 11
# Create map of previous days for 5 random sensors

import pandas as pd

sensors = pd.DataFrame(pd.read_csv("data/sensor_positions.csv", header=None, names=['location', 'name']))['name'].values

def prepare_dataframe(df):
    df["Time"] = pd.to_datetime(df["Time"])
    df["date"] = df["Time"].dt.date
    df["hour"] = df["Time"].dt.hour
    return df

def add_sensor_previous_days(name):
    sensor_data = prepare_dataframe(pd.DataFrame(pd.read_csv(f'data/data SPL August 2022 all/{name}-data.csv')))

    # Each day has only max 24 values
    reduced_data = sensor_data.groupby(['hour', 'date'])['dt_sound_level_dB'].median().round().reset_index()
    values_for_each_hour = []

    for hour in range(0, 24):
        current_hour_data = reduced_data[reduced_data['hour'] == hour].copy() # Also add 30 days time limit
        max_previous_days = len(current_hour_data)
        median_to_compare = 0
        for previous_days_count in range(1, max_previous_days):
            current_hour_data[f"median_prev_days_{previous_days_count}"] = current_hour_data["dt_sound_level_dB"].rolling(window=previous_days_count+1).median()
            current_hour_total_median = current_hour_data[f"median_prev_days_{previous_days_count}"].median()
            is_valid_estimation = -0.5 <= (current_hour_total_median - median_to_compare) <= 0.5
            if is_valid_estimation:
                values_for_each_hour.append(previous_days_count - 1) # If the difference between 2 and 1 previous are lower than treshold, use 1 previous days 
                break

        
            if (previous_days_count == max_previous_days - 1):
                values_for_each_hour.append("NaN")
            
            median_to_compare = current_hour_total_median

    pd.DataFrame([[sensor] + values_for_each_hour]).to_csv('imputation-maps/test_imputation_map.csv', mode='a', index=False, header=False)

for sensor in sensors:
    add_sensor_previous_days(sensor)