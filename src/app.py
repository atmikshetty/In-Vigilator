from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
import threading as th
import audio
import head_pose
import detection
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

# Function to create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username and password match the stored credentials
        conn = create_connection('database.db')
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                row = cursor.fetchone()
                if row:
                    # If the user is authenticated, start the proctoring
                    start_proctoring_thread()
                    return redirect(url_for('index'))
                else:
                    return 'Invalid username or password'
            except sqlite3.Error as e:
                print("Error:", e)
            finally:
                conn.close()
        else:
            return 'Failed to connect to the database'
    else:
        return redirect(url_for('index'))

# Function to start proctoring
def start_proctoring():
    head_pose_thread = th.Thread(target=head_pose.pose)
    audio_thread = th.Thread(target=audio.sound)
    detection_thread = th.Thread(target=detection.run_detection)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()

    head_pose_thread.join()
    audio_thread.join()
    detection_thread.join()

def start_proctoring_thread():
    proctoring_thread = th.Thread(target=start_proctoring)
    proctoring_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
