from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import threading as th
import time
import csv
import matplotlib.pyplot as plt
import head_pose
import audio

app = Flask(__name__)
socketio = SocketIO(app)

PLOT_LENGTH = 200

GLOBAL_CHEAT = 0
PERCENTAGE_CHEAT = 0
CHEAT_THRESH = 0.6
XDATA = list(range(PLOT_LENGTH))
YDATA = [0] * PLOT_LENGTH

csv_file = "detections.csv"

def avg(current, previous):
    if previous > 1:
        return 0.65
    if current == 0:
        if previous < 0.01:
            return 0.01
        return previous / 1.01
    if previous == 0:
        return current
    return 1 * previous + 0.1 * current

def process():
    global GLOBAL_CHEAT, PERCENTAGE_CHEAT, CHEAT_THRESH

    if GLOBAL_CHEAT == 0:
        if head_pose.X_AXIS_CHEAT == 0:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.2, PERCENTAGE_CHEAT)
            else:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0.2, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.4, PERCENTAGE_CHEAT)
        else:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0.1, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.4, PERCENTAGE_CHEAT)
            else:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0.15, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.25, PERCENTAGE_CHEAT)
    else:
        if head_pose.X_AXIS_CHEAT == 0:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.55, PERCENTAGE_CHEAT)
            else:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0.55, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.85, PERCENTAGE_CHEAT)
        else:
            if head_pose.Y_AXIS_CHEAT == 0:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0.6, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.85, PERCENTAGE_CHEAT)
            else:
                if audio.AUDIO_CHEAT == 0:
                    PERCENTAGE_CHEAT = avg(0.5, PERCENTAGE_CHEAT)
                else:
                    PERCENTAGE_CHEAT = avg(0.85, PERCENTAGE_CHEAT)

    if PERCENTAGE_CHEAT > CHEAT_THRESH:
        GLOBAL_CHEAT = 1
        print("CHEATING")
    else:
        GLOBAL_CHEAT = 0

    with open(csv_file, mode='a', newline='') as csvfile:
        fieldnames = ['Cheat Probability', 'Global Cheat']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # If the file is empty, write the header
        if csvfile.tell() == 0:
            writer.writeheader()
        
        # Write data to the CSV file
        writer.writerow({'Cheat Probability': PERCENTAGE_CHEAT, 'Global Cheat': GLOBAL_CHEAT})
    
    print("Cheat percent: ", PERCENTAGE_CHEAT, GLOBAL_CHEAT)

def run_detection():
    global XDATA, YDATA

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(XDATA, YDATA, 'r-')
    ax.set_xlim(0, PLOT_LENGTH)
    ax.set_ylim(0, 1)
    ax.set_title("Suspicious Behaviour Detection")
    ax.set_xlabel("Time")
    ax.set_ylabel("Cheat Probability")
    
    while True:
        YDATA.pop(0)
        YDATA.append(PERCENTAGE_CHEAT)
        line.set_xdata(XDATA)
        line.set_ydata(YDATA)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(1/5)
        process()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    t1 = th.Thread(target=run_detection)
    t1.start()
    app.run(debug=True)
