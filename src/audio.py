from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import sounddevice as sd
import threading as th

app = Flask(__name__)
socketio = SocketIO(app)

SOUND_AMPLITUDE = 0
AUDIO_CHEAT = 0

CALLBACKS_PER_SECOND = 38
SUS_FINDING_FREQUENCY = 2
SOUND_AMPLITUDE_THRESHOLD = 20
FRAMES_COUNT = int(CALLBACKS_PER_SECOND / SUS_FINDING_FREQUENCY)
AMPLITUDE_LIST = [0] * FRAMES_COUNT
SUS_COUNT = 0
count = 0

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def print_sound(indata, outdata, frames, time, status):
    global SOUND_AMPLITUDE, SUS_COUNT, count, SOUND_AMPLITUDE_THRESHOLD, AUDIO_CHEAT

    vnorm = int(np.linalg.norm(indata) * 10)
    AMPLITUDE_LIST.append(vnorm)
    count += 1
    AMPLITUDE_LIST.pop(0)

    if count == FRAMES_COUNT:
        avg_amp = sum(AMPLITUDE_LIST) / FRAMES_COUNT
        SOUND_AMPLITUDE = avg_amp

        if SUS_COUNT >= 2:
            AUDIO_CHEAT = 1
            SUS_COUNT = 0

        if avg_amp > SOUND_AMPLITUDE_THRESHOLD:
            SUS_COUNT += 1
        else:
            SUS_COUNT = 0
            AUDIO_CHEAT = 0

        count = 0

        socketio.emit('sound_amplitude', {'amplitude': SOUND_AMPLITUDE, 'cheat': AUDIO_CHEAT})

def sound():
    with sd.Stream(callback=print_sound):
        sd.sleep(-1)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    t1 = th.Thread(target=sound)
    t1.start()
    socketio.run(app)
