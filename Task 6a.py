# Task 6a: Create bland-altman plot for self and nearest and compare

import pandas as pd

sensor_positions = pd.DataFrame(pd.read_csv("data/sensor_positions.csv", header=None, names=['location', 'name']))

def get_clean_dataframe(path):
    data = pd.read_csv(path)
    df = pd.DataFrame(data)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset=["Time"], keep=False) 
    df["hour"] = df["Time"].dt.hour
    return df

def get_combined_real_data():
    full_df = pd.DataFrame()
    for _, name in sensor_positions.values:
        df = get_clean_dataframe(f'data/data SPL August 2022 all/{name}-data.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df

def get_combined_self_imputed_data():
    full_df = pd.DataFrame()
    for _, name in sensor_positions.values:
        df = get_clean_dataframe(f'imputed_data/self/{name}-self.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df

def get_combined_nearest_imputed_data():
    full_df = pd.DataFrame()
    for _, name in sensor_positions.values:
        df = get_clean_dataframe(f'imputed_data/nearest/{name}-nearest.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df


real = get_combined_real_data()
self_imputed = get_combined_self_imputed_data()
nearest_imputed = get_combined_self_imputed_data()

print(len(real))
print(len(self_imputed))
print(len(nearest_imputed))