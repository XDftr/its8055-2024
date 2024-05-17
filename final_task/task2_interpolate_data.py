import pandas as pd
import os
import matplotlib.pyplot as plt

data_dir = 'data'
region_folders = [
    'region_1_mustamäe_kristiine',
    'region_2_data_kesklinn',
    'region_3_kadriorg_lasnamäe',
    'region_4_ülemiste'
]

start_date = '2022-08-02'
end_date = '2022-08-13'

output_dir = 'task2'
os.makedirs(output_dir, exist_ok=True)

all_data = []
for folder in region_folders:
    folder_path = os.path.join(data_dir, folder)
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            data = pd.read_csv(file_path, parse_dates=['Time'])
            all_data.append(data)

df = pd.concat(all_data)
df = df.sort_values(by='Time')

df = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)]

df = df.drop_duplicates(subset='Time')

df.set_index('Time', inplace=True)

df_resampled = df.resample('1T').mean()

linear_interpolated = df_resampled.interpolate(method='linear')
spline_interpolated = df_resampled.interpolate(method='spline', order=3)

linear_interpolated.to_csv(os.path.join(output_dir, 'linear_interpolated.csv'))
spline_interpolated.to_csv(os.path.join(output_dir, 'spline_interpolated.csv'))


def create_plot(data_sets, labels, title, filename, xlim=None):
    plt.figure(figsize=(30, 10))
    for data, label in zip(data_sets, labels):
        if label == 'Original Data':
            plt.plot(data.index, data['dt_sound_level_dB'], 'o', markersize=3, alpha=0.5, label=label)
        elif label == 'Linear Interpolation':
            plt.plot(data.index, data['dt_sound_level_dB'], '-', linewidth=2, label=label, color='blue')
        elif label == 'Spline Interpolation':
            plt.plot(data.index, data['dt_sound_level_dB'], '-', linewidth=2, label=label, color='red')
    plt.legend()
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('SPL (dB)')
    plt.grid(True)
    if xlim:
        plt.xlim(xlim)
    plt.savefig(os.path.join(output_dir, filename))
    plt.show()


create_plot([df], ['Original Data'], 'Original Data', 'original_data.png')
create_plot([linear_interpolated], ['Linear Interpolation'], 'Linear Interpolation', 'linear_interpolation.png')
create_plot([spline_interpolated], ['Spline Interpolation'], 'Spline Interpolation', 'spline_interpolation.png')
create_plot([df, linear_interpolated, spline_interpolated],
            ['Original Data', 'Linear Interpolation', 'Spline Interpolation'],
            'Original, Linear, and Spline Interpolation',
            'original_linear_spline.png')
