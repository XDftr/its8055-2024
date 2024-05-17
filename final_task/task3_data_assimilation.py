import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

data_dir = 'data'
region_folder = 'region_4_ülemiste'

start_date = '2022-08-02'
end_date = '2022-08-13'

output_dir = 'task3'
os.makedirs(output_dir, exist_ok=True)

all_data = []
for filename in os.listdir(os.path.join(data_dir, region_folder)):
    if filename.endswith('.csv'):
        file_path = os.path.join(data_dir, region_folder, filename)
        data = pd.read_csv(file_path, parse_dates=['Time'])
        all_data.append(data)

df = pd.concat(all_data)
df = df.sort_values(by='Time')
df = df[(df['Time'] >= start_date) & (df['Time'] <= end_date)]
df = df.drop_duplicates(subset='Time')
df.set_index('Time', inplace=True)

df_resampled = df.resample('1T').mean().interpolate(method='linear')

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df_resampled['dt_sound_level_dB'].values.reshape(-1, 1))


def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:i + seq_length]
        y = data[i + seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


seq_length = 60
X, y = create_sequences(scaled_data, seq_length)

split_idx = int(0.8 * len(X))
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(50),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

y_pred_scaled = model.predict(X_test)
y_pred = scaler.inverse_transform(y_pred_scaled)

df_resampled['predicted_dB'] = np.nan
df_resampled.iloc[seq_length:len(y_pred) + seq_length, df_resampled.columns.get_loc('predicted_dB')] = y_pred.flatten()


def get_period(hour):
    if 7 <= hour < 19:
        return 'day'
    elif 19 <= hour < 23:
        return 'evening'
    else:
        return 'night'


df_resampled['period'] = df_resampled.index.hour.map(get_period)

original_results = {}
for period in ['day', 'evening', 'night']:
    period_data = df_resampled[df_resampled['period'] == period]
    exceedance_count = (period_data['dt_sound_level_dB'] > 65).sum()
    total_count = period_data.shape[0]
    exceedance_percentage = (exceedance_count / total_count) * 100
    original_results[period] = exceedance_percentage

lstm_results = {}
for period in ['day', 'evening', 'night']:
    period_data = df_resampled[df_resampled['period'] == period]
    exceedance_count = (period_data['predicted_dB'] > 65).sum()
    total_count = period_data.shape[0]
    exceedance_percentage = (exceedance_count / total_count) * 100
    lstm_results[period] = exceedance_percentage

results_df = pd.DataFrame({
    'Original_Exceedance_Percentage': pd.Series(original_results),
    'LSTM_Exceedance_Percentage': pd.Series(lstm_results)
})
results_df.to_csv(os.path.join(output_dir, 'exceedance_results_comparison_lstm.csv'))
