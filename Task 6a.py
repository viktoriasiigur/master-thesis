# Task 6a: Create bland-altman plot for self and nearest and compare

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

names = ['2013', '2015', '2018', '201B', '201C', '201E', '201F', '2024', '2025', '2026', '2027', '2029', '202A', '202D', '202E', '202F', '2030', '2032', '2035', '2037', '203C', '203D', '203F', '2042', '2043', '2044', '2045', '204C', '204E', '2051', '2052', '2054', '2056', '2057', '2058', '205C', '205F', '2063', '2068', '206B', '2072', '2074', '2078', '207B', '207E', '2085', '2086', '2088', '208D', '2091', '2092', '2093', '209C', '20A5', '20A6', '20A9', '20CF', '20D0', '20D6', '2109', '2130', '2133', '2135', '2137', '214E', '2159', '21AA', '21B9', '21C1', '21C2', '21DC', '2212', '2214', '2215', '2217', '2218', '221E', '2225', '2226', '2231', '2233', '2234', '2236', '223C', '223D', '2240', '2241', '2242', '224B', '2264', '2266', '2267', '226E', '2279', '2279', '227A', '227E', '2281', '2284', '2288', '2290', '229B', '229E', '229F', '22A0', '22A3', '22A7', '22A9', '22AA', '22B2', '22B4', '22B9', '22BA', '22C3', '22D3', '22D6', '22E4', '22E5', '22EB', '22F0', '22F1', '22F6', '22F7', '22F9', '22FC', '22FD', '22FE', '22FF', '2300', '2304', '2305', '230D', '230E', '2311', '2315', '2317', '231E', '2320', '2322', '2323', '2324', '2327', '2329', '232C', '2330', '2331', '2332', '2333', '2334', '2335', '2337', '2338', '233B', '2344', '2348', '234A', '234E', '2352', '2353', '2358', '235E', '2360', '2364', '2371', '2373', '237F', '2383', '238B', '2390', '2393', '2394', '2395', '2396', '2397', '2398', '239D', '239E', '239F', '23A5', '23B1', '23B3']

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
    plt.title(f"Bland-Altman plot - {description_1} vs {description_2}")
    plt.xlabel('Hour')
    plt.ylabel('dB differences')
    plt.xticks(np.arange(0, 24, 1))
    plt.grid(alpha=0.5)
    plt.savefig(f"imputed_data/bland-altman-{description_1}-vs-{description_2}.png")


real_samples = get_samples_median(real_df, 3650)
self_samples = get_samples_median(self_imputed_df, 10000)
nearest_samples = get_samples_median(nearest_imputed_df, 10000)

# bland_altman_plot(real_samples, self_samples, "real", "self_imputed")
# bland_altman_plot(real_samples, nearest_samples, "real", "nearest_imputed")
bland_altman_plot(self_samples, nearest_samples, "self_imputed", "nearest_imputed")
