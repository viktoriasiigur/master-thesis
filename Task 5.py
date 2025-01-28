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
    df["minute"] = df["Time"].dt.minute
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

def bland_altman_plot(method1, method2):
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
    plt.title("Bland-Altman plot - Actual vs 10 (20D6 sensor)")
    plt.xlabel('Hour')
    plt.ylabel('dB differences')
    plt.xticks(np.arange(0, 24, 1))
    plt.grid(alpha=0.5)
    plt.savefig("bland-altman-test.png")


df = get_clean_dataframe(paths[0])

actual_medians = get_actual_median(df)
samples_median_10 = get_samples_median(df, 10)
print(paths[0])

bland_altman_plot(actual_medians, samples_median_10)