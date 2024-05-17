import pandas as pd
import matplotlib.pyplot as plt
import os

CREATE_INTERACTIVE_MAP = True

if CREATE_INTERACTIVE_MAP:
    import folium

data_dir = 'data'
region_folders = {
    'region_1_mustamäe_kristiine': 'Mustamäe-Kristiine',
    'region_2_data_kesklinn': 'Kesklinn',
    'region_3_kadriorg_lasnamäe': 'Kadriorg-Lasnamäe',
    'region_4_ülemiste': 'Ülemiste'
}

zone_to_region = {}

for folder, region_name in region_folders.items():
    folder_path = os.path.join(data_dir, folder)
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            zone_id = filename.split('-')[0]
            zone_to_region[zone_id] = region_name

data = pd.read_csv(os.path.join(data_dir, 'sensor_positions.csv'), header=None, names=['coordinates', 'station_id'])

data['coordinates'] = data['coordinates'].str.replace('[()]', '', regex=True)
data['latitude'] = data['coordinates'].apply(lambda x: float(x.split()[1]))
data['longitude'] = data['coordinates'].apply(lambda x: float(x.split()[0]))

data['region'] = data['station_id'].apply(lambda x: zone_to_region.get(x[:4], 'Unknown'))

plt.figure(figsize=(10, 6))
regions = data['region'].unique()
for region in regions:
    subset = data[data['region'] == region]
    plt.scatter(subset['longitude'], subset['latitude'], label=region)

plt.title('Station Locations')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.grid(True)
plt.savefig('station_locations.png')
plt.show()

if CREATE_INTERACTIVE_MAP:
    map_center = [data['latitude'].mean(), data['longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=12)

    region_colors = {
        'Mustamäe-Kristiine': 'blue',
        'Kesklinn': 'green',
        'Kadriorg-Lasnamäe': 'red',
        'Ülemiste': 'purple',
        'Unknown': 'gray'
    }

    for _, row in data.iterrows():
        folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=5,
            color=region_colors[row['region']],
            fill=True,
            fill_color=region_colors[row['region']],
            popup=f"Station ID: {row['station_id']}\nRegion: {row['region']}"
        ).add_to(m)

    m.save('station_locations_map.html')
