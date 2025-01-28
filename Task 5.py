### Random samples medians
# Task is to get median of each hour.
# Then take 1000 random values of each hour and get the median of those
# Then take 10000 random values of each hour and get the median of those
# Make bland-altman plot of all the files and all the hours

import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

paths = []

for root, dirs, files in os.walk("data/data SPL August 2022 all", topdown=False):
    for name in files:
        paths.append(os.path.join(root, name))

def get_clean_dataframe(path):
    data = pd.read_csv(path)
    df = pd.DataFrame(data)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset=["Time"], keep=False) 
    df["hour"] = df["Time"].dt.hour
    return df

def get_actual_median(df):
    grouped_by_hour = df.groupby('hour')
    medians = grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians

def get_samples_median(df, count):
    grouped_by_hour = df.groupby('hour')
    sampled_data = grouped_by_hour.sample(n=count, random_state=42)
    samples_grouped_by_hour = sampled_data.groupby('hour')
    medians = samples_grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians

def bland_altman_plot(method1, method2, amount_1, amount_2):
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
    plt.title(f"Bland-Altman plot - {amount_1} vs {amount_2} (all sensors)")
    plt.xlabel('Hour')
    plt.ylabel('dB differences')
    plt.xticks(np.arange(0, 24, 1))
    plt.grid(alpha=0.5)
    plt.savefig(f"bland-altman-{amount_1}-vs-{amount_2}.png")
    
def get_all_sensors_df():
    full_df = pd.DataFrame()
    for path in paths:
        df = get_clean_dataframe(path)
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df


df = get_all_sensors_df()

def get_plot_by_values(amount_1, amount_2):
    if (amount_1 == 'actual'):
        samples_1 = get_actual_median(df)
    else:
        samples_1 = get_samples_median(df, amount_1)
    samples_2 = get_samples_median(df, amount_2)
    bland_altman_plot(samples_1, samples_2, amount_1, amount_2)

get_plot_by_values(10, 100)
get_plot_by_values(100, 1000)
get_plot_by_values(1000, 10000)
get_plot_by_values('actual', 10)
get_plot_by_values('actual', 100)
get_plot_by_values('actual', 1000)
get_plot_by_values('actual', 2500)
get_plot_by_values('actual', 3634)
get_plot_by_values('actual', 3635)
get_plot_by_values('actual', 5000)
get_plot_by_values('actual', 10000)