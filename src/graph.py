from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import matplotlib.pyplot as plt

app = Flask(__name__)
socketio = SocketIO(app)

PLOT_LENGTH = 100
XDATA = []
YDATA = []

plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(XDATA, YDATA, 'r-')
ax.set_xlim(0, PLOT_LENGTH)
ax.set_ylim(0, 1)
ax.set_title("Real-time Graph")
ax.set_xlabel("Time")
ax.set_ylabel("Data")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('update_data')
def handle_update(data):
    x = data['x']
    y = data['y']
    XDATA.append(x)
    YDATA.append(y)
    if len(XDATA) > PLOT_LENGTH:
        XDATA.pop(0)
        YDATA.pop(0)
    line.set_xdata(XDATA)
    line.set_ydata(YDATA)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(1e-17)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app)
