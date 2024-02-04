from flask import Flask, render_template, Response
from flask_cors import CORS
from flask_socketio import SocketIO
import cv2
import mediapipe as mp
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Global variables to handle video stream
video_capture = cv2.VideoCapture(0)
frame_lock = threading.Lock()

# Text for calibration
text_to_display = "Calibration will begin in 5 seconds. Please lay your hand as flat as possible, spread your fingers out, and do not move."


def generate_frames():
    global video_capture, text_to_display
    while True:
        success, frame = video_capture.read()  # Read a frame from the webcam
        if not success:
            break
			
        with frame_lock:
            # Convert the frame to RGB for use with MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe hands
            results = hands.process(frame_rgb)
            text_to_display = "test"
            # If hands are detected, draw landmarks on the frame
            if results.multi_hand_landmarks:
                for points in results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(frame, points, mp_hands.HAND_CONNECTIONS)
                    index_finger_tip = points.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
                    text_to_display = f"Hand Coordinates: (x={index_finger_tip.x:.2f}, y={index_finger_tip.y:.2f})"
        # Encode the frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()

        socketio.emit('update', {'image': image_bytes, 'text': text_to_display})

# -- Flask Routes --
@app.route('/')
def index():
    return render_template('index.html', text_to_display=text_to_display)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(target=generate_frames)

if __name__ == '__main__':
    app.run(debug=True)
    

# -- Hand Tracking Functions --
    
#calculating distance between middle finger midpoint and tip
def calculate_distance(points, tip, mid):
    x_tip, y_tip = points.landmark[tip].x, points.landmark[tip].y
    x_mid, y_mid = points.landmark[mid].x, points.landmark[mid].y
    distance = ((x_mid - x_tip)**2 + (y_mid - y_tip)**2)**0.5
    return distance

#calculating distance between pinky tip and thumb tip
def calculate_pinky_thumb_distance(points, pinky_tip, thumb_tip):
    x_pinky_tip, y_pinky_tip = points.landmark[pinky_tip].x, points.landmark[pinky_tip].y
    x_thumb_tip, y_thumb_tip = points.landmark[thumb_tip].x, points.landmark[thumb_tip].y
    distance = ((x_thumb_tip - x_pinky_tip)**2 + (y_thumb_tip - y_pinky_tip)**2)**0.5
    return distance