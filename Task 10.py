## Task 9
"""
1. Take the median of each hour of one sensor
2. Treshold is 0.5
3. Take the same sensor's nearest imputed values
4. Start with the small amount of days and see where the self imputed data reaches the treshold 
(get the medians each hour of 1 day, 2 days, 4 days... and compare them with real data)
"""

import pandas as pd

# sensor_positions = pd.DataFrame(pd.read_csv("data/sensor_positions.csv", header=None, names=['location', 'name']))
names = ['2013', '2015', '2018', '201B', '201C', '201E', '201F', '2024', '2025', '2026', '2027', '2029', '202A', '202D', '202E', '202F', '2030', '2032', '2035', '2037', '203C', '203D', '203F', '2042', '2043', '2044', '2045', '204C', '204E', '2051', '2052', '2054', '2056', '2057', '2058', '205C', '205F', '2063', '2068', '206B', '2072', '2074', '2078', '207B', '207E', '2085', '2086', '2088', '208D', '2091', '2092', '2093', '209C', '20A5', '20A6', '20A9', '20CF', '20D0', '20D6', '2109', '2130', '2133', '2135', '2137', '214E', '2159', '21AA', '21B9', '21C1', '21C2', '21DC', '2212', '2214', '2215', '2217', '2218', '221E', '2225', '2226', '2231', '2233', '2234', '2236', '223C', '223D', '2240', '2241', '2242', '224B', '2264', '2266', '2267', '226E', '2279', '2279', '227A', '227E', '2281', '2284', '2288', '2290', '229B', '229E', '229F', '22A0', '22A3', '22A7', '22A9', '22AA', '22B2', '22B4', '22B9', '22BA', '22C3', '22D3', '22D6', '22E4', '22E5', '22EB', '22F0', '22F1', '22F6', '22F7', '22F9', '22FC', '22FD', '22FE', '22FF', '2300', '2304', '2305', '230D', '230E', '2311', '2315', '2317', '231E', '2320', '2322', '2323', '2324', '2327', '2329', '232C', '2330', '2331', '2332', '2333', '2334', '2335', '2337', '2338', '233B', '2344', '2348', '234A', '234E', '2352', '2353', '2358', '235E', '2360', '2364', '2371', '2373', '237F', '2383', '238B', '2390', '2393', '2394', '2395', '2396', '2397', '2398', '239D', '239E', '239F', '23A5', '23B1', '23B3']

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
    data = prepare_dataframe(pd.DataFrame(pd.read_csv(f'imputed_data/nearest/{name}-nearest.csv'))).tail(days * 1440)
    grouped_by_hour = data.groupby('hour')
    medians = grouped_by_hour['dt_sound_level_dB'].median().reset_index()
    return medians

for name in names:
    real_medians = get_medians_of_real_data(name).set_index("hour")

    for days in range(1, 15):
        imputed_medians = get_medians_of_self_imputed_data(name, days)
        real_medians[f'days_{days}'] = (real_medians['dt_sound_level_dB'] - imputed_medians['dt_sound_level_dB']).between(-0.5, 0.5)
    
    real_medians.to_csv(f'imputed_data/treshold_analysis/{name}-treshold-nearest-tail.csv')
