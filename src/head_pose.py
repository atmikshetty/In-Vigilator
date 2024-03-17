from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import threading as th

app = Flask(__name__)
socketio = SocketIO(app)

X_AXIS_CHEAT = 0
Y_AXIS_CHEAT = 0

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def pose():
    global X_AXIS_CHEAT, Y_AXIS_CHEAT

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_mesh.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        img_h, img_w, img_c = image.shape
        face_3d = []
        face_2d = []
        face_ids = [33, 263, 1, 61, 291, 199]

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in face_ids:
                        x, y = int(lm.x * img_w), int(lm.y * img_h)
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z])

                face_2d = np.array(face_2d, dtype=np.float64)
                face_3d = np.array(face_3d, dtype=np.float64)
                focal_length = 1 * img_w
                cam_matrix = np.array([[focal_length, 0, img_h / 2], [0, focal_length, img_w / 2], [0, 0, 1]])
                dist_matrix = np.zeros((4, 1), dtype=np.float64)
                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
                rmat, jac = cv2.Rodrigues(rot_vec)
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
                x_angle = angles[0] * 360
                y_angle = angles[1] * 360

                if y_angle < -10 or y_angle > 10:
                    X_AXIS_CHEAT = 1
                else:
                    X_AXIS_CHEAT = 0

                if x_angle < -5:
                    Y_AXIS_CHEAT = 1
                else:
                    Y_AXIS_CHEAT = 0

                socketio.emit('head_pose', {'x': int(x_angle), 'y': int(y_angle), 'x_cheat': X_AXIS_CHEAT, 'y_cheat': Y_AXIS_CHEAT})

        cv2.imshow('Head Pose Estimation', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    t1 = th.Thread(target=pose)
    t1.start()
    socketio.run(app)
