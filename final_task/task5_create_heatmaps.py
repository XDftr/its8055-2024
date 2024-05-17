import pandas as pd
import os
import folium
from folium.plugins import HeatMap

data_dir = 'data'
region_folders = [
    'region_1_mustamäe_kristiine',
    'region_2_data_kesklinn',
    'region_3_kadriorg_lasnamäe',
    'region_4_ülemiste'
]

start_date = '2022-08-02'
end_date = '2022-08-13'

location_data = pd.read_csv('data/sensor_positions.csv', header=None, names=['coordinates', 'zone'])
location_data['coordinates'] = location_data['coordinates'].str.replace('[()]', '', regex=True)
location_data[['latitude', 'longitude']] = location_data['coordinates'].str.split(' ', expand=True)
location_data['latitude'] = location_data['latitude'].astype(float)
location_data['longitude'] = location_data['longitude'].astype(float)

location_data.rename(columns={'latitude': 'longitude', 'longitude': 'latitude'}, inplace=True)

all_data = []
for folder in region_folders:
    folder_path = os.path.join(data_dir, folder)
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            data = pd.read_csv(file_path, parse_dates=['Time'])
            data['zone'] = filename.split('-')[0]
            all_data.append(data)

df = pd.concat(all_data)
df = df.sort_values(by='Time')

df = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)]

df = pd.merge(df, location_data, on='zone')

def get_period(hour):
    if 7 <= hour < 19:
        return 'day'
    elif 19 <= hour < 23:
        return 'evening'
    else:
        return 'night'

df['period'] = df['Time'].dt.hour.map(get_period)

def calculate_average_spl(df, period):
    period_df = df[df['period'] == period]
    avg_spl = period_df.groupby(['latitude', 'longitude'])['dt_sound_level_dB'].mean().reset_index()
    return avg_spl

day_avg_spl = calculate_average_spl(df, 'day')
evening_avg_spl = calculate_average_spl(df, 'evening')
night_avg_spl = calculate_average_spl(df, 'night')

def create_heatmap(avg_spl, title, output_file):
    if avg_spl.empty:
        print(f"No data available for {title}")
        return

    m = folium.Map(location=[avg_spl['latitude'].mean(), avg_spl['longitude'].mean()], zoom_start=12)

    heat_data = [[row['latitude'], row['longitude'], row['dt_sound_level_dB']] for index, row in avg_spl.iterrows()]
    HeatMap(heat_data, min_opacity=0.5, max_opacity=1.0, radius=25, blur=15).add_to(m)

    colormap = folium.StepColormap(
        colors=['#ADFF2F', '#008000', '#FFFF00', '#FFD700', '#FFA500', '#FF4500', '#8B00FF'],
        vmin=45, vmax=80,
        index=[45, 50, 55, 60, 65, 70, 75, 80],
        caption='SPL dB'
    )
    colormap.add_to(m)
    m.save(output_file)

os.makedirs('task5', exist_ok=True)
create_heatmap(day_avg_spl, 'Daytime SPL Heatmap', 'task5/day_heatmap.html')
create_heatmap(evening_avg_spl, 'Evening SPL Heatmap', 'task5/evening_heatmap.html')
create_heatmap(night_avg_spl, 'Nighttime SPL Heatmap', 'task5/night_heatmap.html')
