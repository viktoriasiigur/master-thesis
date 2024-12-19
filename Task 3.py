import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import time

paths = []

for root, dirs, files in os.walk("data/data SPL August 2022 all", topdown=False):
    for name in files:
        paths.append(os.path.join(root, name))

def get_data_with_nans(df):
    full_time_range = pd.date_range(start=df["Time"].min(), end=df["Time"].max(), freq="min")
    df = df.set_index("Time").reindex(full_time_range)
    df = df.rename_axis("Time").reset_index()
    df["time_diff"] = df["Time"].diff().dt.total_seconds()
    df["dt_sound_level_dB"] = np.where((df["time_diff"] == 60) | (df.index == 0), df["dt_sound_level_dB"], np.nan)
    df = df.drop(columns=["time_diff"])
    return df

def get_clean_dataframe(path):
    data = pd.read_csv(path)
    df = pd.DataFrame(data)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset=["Time"], keep=False) 
    df = get_data_with_nans(df)
    df["hour"] = df["Time"].dt.hour
    df["minute"] = df["Time"].dt.minute
    return df

def get_samples(df, random_state):
    # Extract 10 random values per 24-hour period
    df["date"] = df["Time"].dt.date
    grouped = df[df["dt_sound_level_dB"].notna()].groupby("date")

    sampled_data = grouped.sample(n=10, random_state=random_state)
    remaining_data = df.copy()
    remaining_data.loc[sampled_data.index, "dt_sound_level_dB"] = np.nan
    return sampled_data, remaining_data

def get_medians(group):
    if (group.notna().any()):
        return np.ceil(group.median())

def get_imputed_data(df):
    group = df.groupby(["hour", "minute"])["dt_sound_level_dB"]
    nan_groups = group.apply(lambda x: x.isna().all())
    groups_with_all_nans = nan_groups[nan_groups].index
    count_of_no_values_groups = len(groups_with_all_nans) # Amount of hour minute groups that have no values in any day.
    imputed_values = group.transform(get_medians)
    if imputed_values.isna().any():
        imputed_values = imputed_values.interpolate(method="linear", limit_direction="both")
        
    df["dt_sound_level_dB"] = df["dt_sound_level_dB"].fillna(imputed_values)
    return df, count_of_no_values_groups

def get_error_stats(path):
    dataframe = get_clean_dataframe(path)
    error_data = []
    no_values_counts = []
    
    for iteration in range(1000):
        sampled_data, remaining_data = get_samples(dataframe, random_state=iteration)
        imputed_data, count_of_no_values_groups = get_imputed_data(remaining_data)
        sampled_data_indices = sampled_data.index.to_numpy()
        imputed_subset = imputed_data.loc[sampled_data_indices]
        error = pd.DataFrame()
        error['error_db_level'] = np.abs(sampled_data["dt_sound_level_dB"] - imputed_subset["dt_sound_level_dB"])
        error['hour'] = imputed_subset['hour']
        error_data.append(error)
        no_values_counts.append(count_of_no_values_groups)
        print(iteration)
        
    mean_amount_of_no_values_groups = np.ceil(pd.Series(no_values_counts).median()).astype(int)
    errors = pd.concat(error_data, ignore_index=True)
    error_stats = errors.groupby('hour')['error_db_level'].agg(list)
    return error_stats, mean_amount_of_no_values_groups

def create_box_plot(path):
    error_stats, mean_amount_of_no_values_groups = get_error_stats(path)
    plt.figure(figsize=(12, 6))
    plt.boxplot(error_stats)
    
    plt.title(path)
    plt.xlabel("Hour of the Day")
    plt.ylabel("Error (dB)")
    plt.text(-3, -2.5, 'Amount of times of the day (hour:minute) with no not-nan values: ' + str(mean_amount_of_no_values_groups), fontsize=6)
    
    filename = path.replace("data/data SPL August 2022 all/", "").replace(".csv", "")
    plt.savefig(f"box_plots/{filename}-1000.png")

def create_plots_for_all_sensors():
    for path in paths[219:]: 
        start_time = np.floor(time.time() * 1000)
        create_box_plot(path)
        print("Total duration for 1 plot: ", np.floor(time.time() * 1000) - start_time)

create_plots_for_all_sensors()
