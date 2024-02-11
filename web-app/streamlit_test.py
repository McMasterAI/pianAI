import cv2
import mediapipe as mp
import streamlit as st
import numpy as np

button_clicked = False

def calculate_distance(points, tip, mid):
    x_tip, y_tip = points.landmark[tip].x, points.landmark[tip].y
    x_mid, y_mid = points.landmark[mid].x, points.landmark[mid].y
    distance = ((x_mid - x_tip)**2 + (y_mid - y_tip)**2)**0.5
    return distance

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
    
    distance_text = st.empty()

    while True:
        
        # Read a frame from the webcam
        ret, frame = cap.read()

        if not ret:
            st.error("Error: Failed to capture frame.")
            break

        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe Hands
        results = hands.process(rgb_frame)

        # Draw hand landmarks on the frame if hands are detected
        if results.multi_hand_landmarks:
            for points in results.multi_hand_landmarks:
				#for each point from the skeleton draw it using the mediapipe function
                mp.solutions.drawing_utils.draw_landmarks(frame, points, mp_hands.HAND_CONNECTIONS)
                distance_from_calibration_middle = calculate_distance(points,
														mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value,
														mp_hands.HandLandmark.MIDDLE_FINGER_PIP.value)
                distance_from_calibration_pinky_thumb = calculate_pinky_thumb_distance(points,
																				mp_hands.HandLandmark.PINKY_TIP.value,
																				mp_hands.HandLandmark.THUMB_TIP.value)

        if(distance_from_calibration_middle > 0.1 and distance_from_calibration_pinky_thumb > 0.035):
            distance_text.text("Hand Flat! Make sure you keep your fingers curved.")
        else:
            distance_text.text("Hand in proper curved position")
		
		# Display the frame in Streamlit
        placeholder.image(frame, channels="BGR", use_column_width=True)

    # Release the webcam and close the Streamlit app when done
    cap.release()

if __name__ == "__main__":
    main()
    



'''

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

#calculating distance between middle finger midpoint and tip

#displays messages on the screen
def text_to_screen(frame, message, time):
    text_size = 1
    #retrieve height and width of screen, not intersted in the colour channels
    height, width, _ = frame.shape

    cv2.putText(frame, message, (int(width / 4), int(height / 2)),
                cv2.FONT_HERSHEY_SIMPLEX, text_size, (255, 255, 255), 2, cv2.LINE_AA)
    #FONT_HERSHEY_SIMPLEX = normal size sans serfis font, can be changed

    cv2.imshow('Hand Tracking', frame)
    cv2.waitKey(time * 1000)

#creating the calibration putton
def calibration_button(frame):
    text = "Press me to begin calibration process"
    size = (650, 100)
    position = ((frame.shape[1] - size[0]) // 2, (frame.shape[0] - size[1]) // 2)

    #display black rectangle button on the screen
    button_image = frame.copy()
    cv2.rectangle(button_image, position, (position[0] + size[0], position[1] + size[1]), (0, 0, 0), cv2.FILLED)
    #with text overtop
    cv2.putText(button_image, text, (position[0] + 10, position[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    return button_image, position, size

#checks if button clicked
def if_button_clicked(event, x, y, flags, param):
    #flags provides details by setMouseCallback about if certain mouse buttons are being pressed
    #param isnt necesarily used but needed to maintain callback signature for function to work properly
    global button_clicked, position, size

    if event == cv2.EVENT_LBUTTONDOWN: #checking if the left mouse is pressed, so basically if a click happened on the screen
        #checks if the click is inside the button's rectangle
        button_x, button_y, button_width, button_height = position[0], position[1], size[0], size[1]
        #and if it happened within the area of where the button is located
        if button_x < x < button_x + button_width and button_y < y < button_y + button_height: 
            #then button clicked is set to true so it can break out of the loop in the display button function and start the calibration process
            button_clicked = True

#simplay displays the button
def display_button(cap):
    global button_clicked, position, size #refers to the same variable used in other functions

    cv2.namedWindow('Hand Tracking') #creates a window that pops up
    cv2.setMouseCallback('Hand Tracking', if_button_clicked) #called the if_button_clicked function if an action occurs on teh screen

    while not button_clicked: #do this before the button is clicked
        read, frame = cap.read() #reads the frame, returns if it was read or not and the actual from 
        if not read:
            break #if it fails we break out of the lopp

        button_image, position, size = calibration_button(frame)  #passes the current frame and based off of that returns dimensions

        cv2.imshow('Hand Tracking', button_image) #displays the buttob
        key = cv2.waitKey(1) & 0xFF #stores what key was clicked
        if key == 13: #if the enter key is clicked it terminates the loop and the calibration process continues
            break
        elif cv2.getWindowProperty('Hand Tracking', cv2.WND_PROP_VISIBLE) < 1: #checks if the window has been closed or not visible and also terminates the loop
            break

    cv2.destroyAllWindows() #once button is clicked, remove it from the screen


#calculating distance between pinky tip and thumb tip
def calculate_pinky_thumb_distance(points, pinky_tip, thumb_tip):
    x_pinky_tip, y_pinky_tip = points.landmark[pinky_tip].x, points.landmark[pinky_tip].y
    x_thumb_tip, y_thumb_tip = points.landmark[thumb_tip].x, points.landmark[thumb_tip].y
    distance = ((x_thumb_tip - x_pinky_tip)**2 + (y_thumb_tip - y_pinky_tip)**2)**0.5
    return distance


button_clicked = False

#main function called and where all the processes begin
def main():
    cap = cv2.VideoCapture(0)  #starts it up to a default webcame

    #displays the button to start calibration
    display_button(cap)
    
    read, frame = cap.read()
    if read: #if the frame is succesfully read it displays the following message for 5 seconds
        text_to_screen(frame, "Calibration will begin in 5 seconds, please lay your hand as flat as possible, spread your fingers out as far as possibleand do not move", 5)

    #initalizing some values
    distance_from_calibration_middle = 0
    current_distance_middle = 0

    distance_from_calibration_pinky_thumb = 0
    current_distance_pinky_thumb = 0

    is_calibrating = True
    calibration_time = 3

    calibration_start_time = cv2.getTickCount() #gets the time at which the calibration started

    while is_calibrating:
        read, frame = cap.read() #returns a frame from the webcam
        if not read: #if it wasnt succesfully read break the loop
            break

        #converting from bgr to rgb
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #let mediapipe process the frame so it can detect/create the landmarks/skeleton
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
                
        #while these calculations are being done it displays the message to  let the user know what is happening
        elapsed_time = (cv2.getTickCount() - calibration_start_time) / cv2.getTickFrequency()
        if elapsed_time < calibration_time:
            text_to_screen(frame, "Calibrating...", 1)

        #calibration done, now is able to exit loop
        else:
            is_calibrating = False
            text_to_screen(frame, "Calibration complete. You may now begin playing", 2)

    #all the activity for hand tracking/flat hand logic after calibration is done
    while cap.isOpened():
        #reads frame from the webcam
        read, frame = cap.read()
        if not read:#if failed to be read end loop
            break

        #need to convert from bgr to rbg
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #mediapipe detects the hands
        results = hands.process(frame_rgb)

        #if the hands are detected then draw the skeleton on the hands
        if results.multi_hand_landmarks:
            for points in results.multi_hand_landmarks:
                #where the drawing is happening using the mediapipe function
                mp.solutions.drawing_utils.draw_landmarks(frame, points, mp_hands.HAND_CONNECTIONS)  

                #this gets the coordinates for each point
                for idx, point in enumerate(points.landmark):
                    height, width, _ = frame.shape #gets the dimension of the current frame
                    cx, cy = int(point.x * width), int(point.y * height) #gets the current coordinate

                    #and draws a point at the selected joints
                    if idx in [mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value,
                               mp_hands.HandLandmark.MIDDLE_FINGER_PIP.value,
                               mp_hands.HandLandmark.PINKY_TIP.value, 
                               mp_hands.HandLandmark.THUMB_TIP.value]:
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

                        #calculates current distances
                        current_distance_middle = calculate_distance(points,
                                                                        mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value,
                                                                        mp_hands.HandLandmark.MIDDLE_FINGER_PIP.value)
                        

                        current_distance_pinky_thumb = calculate_pinky_thumb_distance(points,
                                                                            mp_hands.HandLandmark.PINKY_TIP.value,
                                                                            mp_hands.HandLandmark.THUMB_TIP.value)

                        #checks if the distance between the two joints is so too fafr away, thus considering it flat
                        if current_distance_middle > (0.85 * distance_from_calibration_middle):
                            if current_distance_pinky_thumb < (distance_from_calibration_pinky_thumb * 0.72) :
                                #displays the message in red, top right corner of screen
                                cv2.putText(frame, "Hand is flat!", (width - 600, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                            2, (0, 0, 255), 2, cv2.LINE_AA)

        #displays the frame
        cv2.imshow('Hand Tracking', frame)

        #if q is pressed it terminated the entire process
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #shutting everything down
    cap.release()
    cv2.destroyAllWindows()


main()
'''