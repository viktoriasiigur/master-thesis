# Task 6a: Create bland-altman plot for self and nearest and compare

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

sensor_positions = pd.DataFrame(pd.read_csv("data/sensor_positions.csv", header=None, names=['location', 'name']))

# ============== PREPARE BIG DATAFRAMES ===================

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
        df = get_clean_dataframe(f'imputed_data/nearest-k-1/{name}-nearest.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df


real_df = get_combined_real_data()
self_imputed_df = get_combined_self_imputed_data()
nearest_imputed_df = get_combined_nearest_imputed_data()

# ============== PREPARE BIG DATAFRAMES ===================


def get_samples_median(df, count):
    grouped_by_hour = df.groupby('hour')
    sampled_data = grouped_by_hour.sample(n=count, random_state=42)
    samples_grouped_by_hour = sampled_data.groupby('hour')
    medians = samples_grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians


def bland_altman_plot(method1, method2, description_1, description_2):
    merged = pd.merge(method1, method2, on='hour', suffixes=('_1', '_2'))
    method1_db_as_array = np.asarray(merged['dt_sound_level_dB_1'])
    method2_db_as_array = np.asarray(merged['dt_sound_level_dB_2'])

    difference = method1_db_as_array - method2_db_as_array
    mean_difference = np.mean(difference)
    standard_deviation = np.std(difference, axis=0)

    plt.figure(figsize=(10, 4))
    plt.scatter(merged['hour'], difference, label='Differences')
    plt.axhline(mean_difference, color='blue', linestyle='-', label='Mean')
    plt.axhline(mean_difference + 1.96 * standard_deviation, color='red', linestyle='--', label='(+/-)1.96*SD')
    plt.axhline(mean_difference - 1.96 * standard_deviation, color='red', linestyle='--')
    plt.legend(loc='upper right')
    plt.title(f"Bland-Altman plot - {description_1} vs {description_2} (all sensors)")
    plt.xlabel('Hour')
    plt.ylabel('dB differences')
    plt.xticks(np.arange(0, 24, 1))
    plt.grid(alpha=0.5)
    plt.savefig(f"imputed_data/bland-altman-{description_1}-vs-{description_2}.png")


real_samples = get_samples_median(real_df, 100)
self_samples = get_samples_median(self_imputed_df, 100)
nearest_samples = get_samples_median(nearest_imputed_df, 100)

bland_altman_plot(real_samples, self_samples, "real", "self_imputed")
bland_altman_plot(real_samples, nearest_samples, "real", "nearest_k_1_imputed")
bland_altman_plot(self_samples, nearest_samples, "self_imputed", "nearest_k_1_imputed")
