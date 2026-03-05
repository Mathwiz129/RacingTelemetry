from gpiozero import DigitalInputDevice
from time import sleep, time
import csv
from datetime import datetime
from collections import deque

# -------- SETTINGS --------
HALL_PIN = 2
MAGNETS_PER_REV = 4
SAMPLE_TIME = 1.0
SMOOTH_SAMPLES = 5
CSV_FILE = "rpm_log.csv"
# --------------------------

sensor = DigitalInputDevice(HALL_PIN, pull_up=True)

tick_count = 0
rpm_buffer = deque(maxlen=SMOOTH_SAMPLES)

def magnet_detected():
    global tick_count
    tick_count += 1

sensor.when_activated = magnet_detected

# create csv file
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "rpm"])

print("RPM logger started")

start_time = time()

while True:

    sleep(SAMPLE_TIME)

    ticks = tick_count
    tick_count = 0

    revs = ticks / MAGNETS_PER_REV
    rpm = revs * 60

    rpm_buffer.append(rpm)
    smoothed_rpm = sum(rpm_buffer) / len(rpm_buffer)

    timestamp = datetime.now().isoformat()

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, round(smoothed_rpm, 2)])

    print("RPM:", round(smoothed_rpm, 1))