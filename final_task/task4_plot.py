import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('task4/recorded_spl_data.csv', parse_dates=['Time'])

plt.figure(figsize=(14, 7))
plt.plot(data['Time'], data['SPL'], label='SPL (dB)')
plt.xlabel('Time')
plt.ylabel('SPL (dB)')
plt.title('Sound Pressure Level (SPL) Over Time')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('task4/spl_plot.png')
plt.show()
