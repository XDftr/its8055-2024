import serial
import time
import csv

# For recording was used code provided in Moodle

serial_port = 'COM3'
baud_rate = 500000
timeout = 1

ser = serial.Serial(serial_port, baud_rate, timeout=timeout)

recording_duration = 13 * 60

with open('task4/recorded_spl_data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Time', 'SPL'])

    start_time = time.time()

    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                try:
                    spl = float(line)
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    csv_writer.writerow([current_time, spl])
                    print(f"{current_time}, {spl}")
                except ValueError:
                    continue

            if time.time() - start_time >= recording_duration:
                print("Recording completed.")
                break
    except KeyboardInterrupt:
        print("Data capture stopped")
    finally:
        ser.close()
