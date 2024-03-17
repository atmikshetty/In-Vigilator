import audio
import head_pose
import detection
import threading as th
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

if __name__ == "__main__":
    head_pose_thread = th.Thread(target=head_pose.pose)
    audio_thread = th.Thread(target=audio.sound)
    detection_thread = th.Thread(target=detection.run_detection)

    head_pose_thread.start()
    audio_thread.start()
    detection_thread.start()

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('get_audio_data')
    def get_audio_data():
        emit('audio_data', {'amplitude': audio.SOUND_AMPLITUDE})

    @socketio.on('get_head_pose_data')
    def get_head_pose_data():
        emit('head_pose_data', {'x': head_pose.x, 'y': head_pose.y})

    socketio.run(app)
