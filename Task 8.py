### Make histogram of real vs self and real vs nearest imputation 

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

names = ['2013', '2015', '2018', '201B', '201C', '201E', '201F', '2024', '2025', '2026', '2027', '2029', '202A', '202D', '202E', '202F', '2030', '2032', '2035', '2037', '203C', '203D', '203F', '2042', '2043', '2044', '2045', '204C', '204E', '2051', '2052', '2054', '2056', '2057', '2058', '205C', '205F', '2063', '2068', '206B', '2072', '2074', '2078', '207B', '207E', '2085', '2086', '2088', '208D', '2091', '2092', '2093', '209C', '20A5', '20A6', '20A9', '20CF', '20D0', '20D6', '2109', '2130', '2133', '2135', '2137', '214E', '2159', '21AA', '21B9', '21C1', '21C2', '21DC', '2212', '2214', '2215', '2217', '2218', '221E', '2225', '2226', '2231', '2233', '2234', '2236', '223C', '223D', '2240', '2241', '2242', '224B', '2264', '2266', '2267', '226E', '2279', '2279', '227A', '227E', '2281', '2284', '2288', '2290', '229B', '229E', '229F', '22A0', '22A3', '22A7', '22A9', '22AA', '22B2', '22B4', '22B9', '22BA', '22C3', '22D3', '22D6', '22E4', '22E5', '22EB', '22F0', '22F1', '22F6', '22F7', '22F9', '22FC', '22FD', '22FE', '22FF', '2300', '2304', '2305', '230D', '230E', '2311', '2315', '2317', '231E', '2320', '2322', '2323', '2324', '2327', '2329', '232C', '2330', '2331', '2332', '2333', '2334', '2335', '2337', '2338', '233B', '2344', '2348', '234A', '234E', '2352', '2353', '2358', '235E', '2360', '2364', '2371', '2373', '237F', '2383', '238B', '2390', '2393', '2394', '2395', '2396', '2397', '2398', '239D', '239E', '239F', '23A5', '23B1', '23B3']


def get_clean_dataframe(path):
    data = pd.read_csv(path)
    df = pd.DataFrame(data)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.drop_duplicates(subset=["Time"], keep=False) 
    df["hour"] = df["Time"].dt.hour
    return df

def get_combined_real_data():
    full_df = pd.DataFrame()
    for name in names:
        df = get_clean_dataframe(f'data/data SPL August 2022 all/{name}-data.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df

def get_combined_self_imputed_data():
    full_df = pd.DataFrame()
    for name in names:
        df = get_clean_dataframe(f'imputed_data/self/{name}-self.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df

def get_combined_nearest_imputed_data():
    full_df = pd.DataFrame()
    for name in names:
        df = get_clean_dataframe(f'imputed_data/nearest/{name}-nearest.csv')
        full_df = pd.concat([full_df, df], ignore_index=True)
    return full_df


real = get_combined_real_data()
self = get_combined_self_imputed_data()
nearest = get_combined_nearest_imputed_data()


def get_samples_median(df, count):
    grouped_by_hour = df.groupby('hour')
    sampled_data = grouped_by_hour.sample(n=count, random_state=42)
    samples_grouped_by_hour = sampled_data.groupby('hour')
    medians = samples_grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians

def get_median_of_hour_per_count(count):
    self_medians = get_samples_median(self, count)
    nearest_medians = get_samples_median(nearest, count)
    return self_medians['dt_sound_level_dB'] - nearest_medians['dt_sound_level_dB']


def get_table_of_hours_and_occurrences():
    counts = list(range(10, 3650, 10))
    df = pd.DataFrame(index=range(24), columns=counts)
    for count in counts:
        median_diff = get_median_of_hour_per_count(count)
        df[count] = median_diff.values 
    df.to_csv('histogram_data.csv')

# get_table_of_hours_and_occurrences()

def get_histograms():
    df = pd.read_csv('histogram_data.csv', index_col=0)
    print(df)
    for hour in df.index[:1]:
        hour_df = df.loc[hour]
        plt.figure(figsize=(8, 4))
        plt.hist(df.loc[hour], bins=30, orientation="horizontal")

        plt.ylabel("Median difference (dB)")
        plt.xlabel("Count")
        plt.title(f"Histogram for hour {hour}")
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        plt.savefig(f"imputed_data/histograms/histogram_hour_{hour}.png")
        plt.close()

get_histograms()
