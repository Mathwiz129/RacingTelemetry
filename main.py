from gpiozero import DigitalInputDevice
from time import sleep
from datetime import datetime
from collections import deque
from flask import Flask
import threading
import csv

# -------- SETTINGS --------
HALL_PIN = 2
MAGNETS_PER_REV = 4
SAMPLE_TIME = 1.0
SMOOTH_SAMPLES = 5
CSV_FILE = "rpm_log.csv"
# --------------------------

app = Flask(__name__)

sensor = DigitalInputDevice(HALL_PIN, pull_up=True)

tick_count = 0
current_rpm = 0
rpm_buffer = deque(maxlen=SMOOTH_SAMPLES)

def magnet_detected():
    global tick_count
    tick_count += 1

sensor.when_activated = magnet_detected

# create CSV file
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "rpm"])

def rpm_loop():
    global tick_count, current_rpm

    print("RPM logger started")

    while True:

        sleep(SAMPLE_TIME)

        ticks = tick_count
        tick_count = 0

        revs = ticks / MAGNETS_PER_REV
        rpm = revs * 60

        rpm_buffer.append(rpm)
        current_rpm = sum(rpm_buffer) / len(rpm_buffer)

        timestamp = datetime.now().isoformat()

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, round(current_rpm, 2)])

        print("RPM:", round(current_rpm,1))


@app.route("/")
def index():
    return f"<h1>RPM: {round(current_rpm,1)}</h1>"


def start_rpm_thread():
    thread = threading.Thread(target=rpm_loop)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    start_rpm_thread()
    app.run(host="0.0.0.0", port=5000)