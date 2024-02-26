import cv2
import mediapipe as mp
import streamlit as st
import numpy as np
import time

# calculating distance between middle finger midpoint and tip
def calculate_distance(points, tip, mid):
    x_tip, y_tip = points.landmark[tip].x, points.landmark[tip].y
    x_mid, y_mid = points.landmark[mid].x, points.landmark[mid].y
    distance = ((x_mid - x_tip)**2 + (y_mid - y_tip)**2)**0.5
    return distance

#calclulate distance between pinky and thumb
def calculate_pinky_thumb_distance(points, pinky_tip, thumb_tip):
    x_pinky_tip, y_pinky_tip = points.landmark[pinky_tip].x, points.landmark[pinky_tip].y
    x_thumb_tip, y_thumb_tip = points.landmark[thumb_tip].x, points.landmark[thumb_tip].y
    distance = ((x_thumb_tip - x_pinky_tip)**2 + (y_thumb_tip - y_pinky_tip)**2)**0.5
    return distance

def main():

    #initalizing some values
    global distance_from_calibration_middle
    global distance_from_calibration_pinky_thumb
    global distance_text
    distance_from_calibration_pinky_thumb = 0
    distance_from_calibration_middle = 0
    
    st.title("pianAI")
    
    # Create a placeholder for displaying the webcam feed
    placeholder = st.empty()
    calibration_button_placeholder = st.empty()

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    # Open the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Error: Unable to open the webcam.")
        return

    # External data placeholders (replace with actual data)
    external_data_1 = "MIDI Data:"
    external_data_2 = "Data 2: Placeholder"

    # External data column
    st.sidebar.title("### Audio Data")
    st.sidebar.write(external_data_1)
    st.sidebar.write(external_data_2)

    #setting text and buton values to empty
    distance_text = st.empty()
    calibration_button_placeholder = st.empty()
    callibration_message = st.empty()

    #initalizing flags
    calibration_started = False
    calibration_completed = False
    

    while True :
        if not calibration_started :
            #only display button if calibration hasnt been done yet
            button_clicked = calibration_button_placeholder.button("Begin Calibration!")


            if button_clicked:
                calibration_started = True
                calibration_button_placeholder.empty()
                
                
                callibration_message.write("Callibration will begin in 5 seconds. Please lay your hand as flast as possible and as wide as possible, right above the piano. Thank you!")
                calibration_start_time = time.time()
                calibration_time = 10
                #keep the message on the screen for 5 seconds
                time.sleep(5) 

                
                while True:
                    # display this message to let the user know what is happening during calibration
                    elapsed_time = time.time() - calibration_start_time
                    if elapsed_time < calibration_time:
                        remaining_time = int(calibration_time - elapsed_time)
                        callibration_message.empty()
                        #countdown
                        distance_text.text(f"Calibrating... Please wait for {remaining_time} seconds.")

                        #read a frame from the webcam
                        ret, frame = cap.read()

                        if not ret:
                            st.error("Error: Failed to capture frame.")
                            break

                        #converting from bgr to rgb
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        #mmediapipe processing the frame to detect/create the landmarks/skeleton
                        results = hands.process(frame_rgb)

                        #if the hands are detected on the screen, produce the skeleton
                        if results.multi_hand_landmarks:
                            for points in results.multi_hand_landmarks:
                                #for each point from the skeleton draw it using the mediapipe function
                                mp.solutions.drawing_utils.draw_landmarks(frame, points, mp_hands.HAND_CONNECTIONS)

                                #calculates the distance between mid and tip joint of middle finger
                                distance_from_calibration_middle = calculate_distance(points,
                                                                                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value,
                                                                                    mp_hands.HandLandmark.MIDDLE_FINGER_PIP.value)

                                #calculates the distance between pinky tip and thumb tip
                                distance_from_calibration_pinky_thumb = calculate_pinky_thumb_distance(points,
                                                                                                    mp_hands.HandLandmark.PINKY_TIP.value,
                                                                                                    mp_hands.HandLandmark.THUMB_TIP.value)

                    else:
                        calibration_completed = True
                        break
                    
                    #display the frame in Streamlit
                    placeholder.image(frame, channels="BGR", use_column_width=True)

            #hide the button after calibration is done
            button_clicked = False
            #remove the calibration message
            callibration_message.empty()

            while True:
                calibration_started = False

                #read a frame from the webcam
                ret, frame = cap.read()

                if not ret:
                    st.error("Error: Failed to capture frame.")
                    break

                #convert the BGR image to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                #process the frame with MediaPipe Hands
                results = hands.process(rgb_frame)

                #only begin assesing hand position if calibration is done
                if calibration_completed :

                    #draw hand landmarks on the frame if hands are detected
                    if results.multi_hand_landmarks:
                        for points in results.multi_hand_landmarks:
                            #where the drawing is happening using the mediapipe function
                            mp.solutions.drawing_utils.draw_landmarks(frame, points, mp_hands.HAND_CONNECTIONS)

                            #this gets the coordinates for each point
                            for idx, point in enumerate(points.landmark):
                                height, width, _ = frame.shape  # gets the dimension of the current frame
                                cx, cy = int(point.x * width), int(point.y * height)  # gets the current coordinate

                                #and draws a point at the selected joints
                                if idx in [mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value,
                                        mp_hands.HandLandmark.MIDDLE_FINGER_PIP.value,
                                        mp_hands.HandLandmark.PINKY_TIP.value,
                                        mp_hands.HandLandmark.THUMB_TIP.value]:
                                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

                                    # calculates current distances
                                    current_distance_middle = calculate_distance(points,
                                                                                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value,
                                                                                    mp_hands.HandLandmark.MIDDLE_FINGER_PIP.value)

                                    current_distance_pinky_thumb = calculate_pinky_thumb_distance(points,
                                                                                                    mp_hands.HandLandmark.PINKY_TIP.value,
                                                                                                    mp_hands.HandLandmark.THUMB_TIP.value)

                                    #checks if the distance between the two joints is so too far away, thus considering it flat
                                    if current_distance_middle > (0.85 * distance_from_calibration_middle):
                                        #only if the distance between the pinky and thumb is not far enough to dismiss flatness
                                        if current_distance_pinky_thumb < (distance_from_calibration_pinky_thumb * 0.72):
                                            # displays the message in red, top right corner of screen
                                            distance_text.text("Hand Flat! Make sure you keep your fingers curved.")
                                        else:
                                            distance_text.text("Hand in proper curved position")
                                    else :
                                        distance_text.text("Hand in proper curved position")

                                    
                                    #if current_distance_pinky_thumb > (distance_from_calibration_pinky_thumb * 0.72):
                                        #distance_text.text("Hand in proper curved position")
                                    #if current_distance_pinky_thumb < (distance_from_calibration_pinky_thumb * 0.72) and current_distance_middle > (0.85 * distance_from_calibration_middle):
                                        #distance_text.text("Hand Flat! Make sure you keep your fingers curved.")
                                    #if current_distance_pinky_thumb < (distance_from_calibration_pinky_thumb * 0.72) and current_distance_middle < (0.85 * distance_from_calibration_middle):
                                        #distance_text.text("Hand in proper curved position")
                                    

                #display the frame in Streamlit
                placeholder.image(frame, channels="BGR", use_column_width=True)

        # Release the webcam and close the Streamlit app when done
        cap.release()

if __name__ == "__main__":
    main()
