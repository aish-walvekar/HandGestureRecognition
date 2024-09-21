# Final working code
import cv2
import time
import pyttsx3
import mediapipe as mp

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Open the video capture
cap = cv2.VideoCapture(0)  # 0 for webcam, or provide a video file path

# Check if the video capture has been initialized correctly
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

frame_skip = 2  # Number of frames to skip
frame_count = 0  # Initialize frame counter
last_gesture = "Unknown Gesture"  # Track the last detected gesture
last_time = time.time()  # Time of the last gesture detection

input_state = "first number"  # Current input state
first_number = ""
second_number = ""
operator = "" 
calculation_result = ""  # Renamed to avoid conflict with MediaPipe result
count = 0

#Using the x,y,z values it detects the gesture made by the person
def detect_gesture(landmarks):
    thumb_tip_x = landmarks[mp_hands.HandLandmark.THUMB_TIP].x
    thumb_dip_x = landmarks[mp_hands.HandLandmark.THUMB_IP].x
    index_tip_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
    index_dip_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_DIP].y
    middle_tip_y = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
    middle_dip_y = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y
    ring_tip_y = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y
    ring_dip_y = landmarks[mp_hands.HandLandmark.RING_FINGER_DIP].y
    pinky_tip_y = landmarks[mp_hands.HandLandmark.PINKY_TIP].y
    pinky_dip_y = landmarks[mp_hands.HandLandmark.PINKY_DIP].y

    is_thumb_extended = thumb_tip_x > thumb_dip_x
    is_index_extended = index_tip_y < index_dip_y
    is_middle_extended = middle_tip_y < middle_dip_y
    is_ring_extended = ring_tip_y < ring_dip_y
    is_pinky_extended = pinky_tip_y < pinky_dip_y
    
    if is_index_extended and not (is_thumb_extended or is_middle_extended or is_ring_extended or is_pinky_extended):
        return 1
    elif is_index_extended and is_middle_extended and not (is_thumb_extended or is_ring_extended or is_pinky_extended):
        return 2
    elif is_index_extended and is_middle_extended and is_ring_extended and not (is_thumb_extended or is_pinky_extended):
        return 3
    elif is_index_extended and is_middle_extended and is_ring_extended and is_pinky_extended and not is_thumb_extended:
        return 4
    elif all([is_thumb_extended, is_index_extended, is_middle_extended, is_ring_extended, is_pinky_extended]):
        return 5
    elif not any([is_thumb_extended, is_index_extended, is_middle_extended, is_ring_extended, is_pinky_extended]):
        return 0
    elif is_thumb_extended and not any([is_index_extended, is_middle_extended, is_ring_extended, is_pinky_extended]):
        return 6
    elif is_thumb_extended and is_index_extended and not any([is_middle_extended, is_ring_extended, is_pinky_extended]):
        return 7
    elif is_thumb_extended and is_index_extended and is_middle_extended and not any([is_ring_extended, is_pinky_extended]):
        return 8
    elif is_thumb_extended and is_index_extended and is_ring_extended and not any([is_pinky_extended]):
        return 9
    elif is_thumb_extended and is_index_extended and is_pinky_extended and not any([is_middle_extended, is_ring_extended]):
        return "+"
    elif is_index_extended and is_pinky_extended and not any([is_middle_extended, is_ring_extended, is_thumb_extended]):
        return "-"
    elif is_thumb_extended and is_pinky_extended and not any([is_middle_extended, is_ring_extended, is_index_extended]):
        return "*"
    elif is_index_extended and is_pinky_extended and is_middle_extended and not any([is_thumb_extended, is_ring_extended]):
        return "/"
    elif is_index_extended and is_pinky_extended and is_thumb_extended and is_middle_extended and not any([is_ring_extended]):
        return "="
    else:
        return "Unknown Gesture"

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

speak(f"Welcome to Calculator using Hand Gesture Recognition ")

while True:
    ret, frame = cap.read() 

    if not ret:
        break
    
    # Process only every 'frame_skip' frame
    if frame_count % frame_skip == 0:
        current_time = time.time()
        
        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame and find hand landmarks (it has x,y,z values)
        hand_result = hands.process(rgb_frame)
        
        r = ""
        if hand_result.multi_hand_landmarks:
            for hand_landmarks in hand_result.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                
                # Detect the gesture
                gesture = detect_gesture(landmarks)
                
                if gesture == "Unknown Gesture":
                    speak(f"{gesture}")
                
                # Check if the gesture is valid and either different from the last one or enough time has passed
                if gesture != "Unknown Gesture" and (gesture != last_gesture or (current_time - last_time) > 5.0):
                    last_gesture = gesture  # Update last gesture
                    last_time = current_time  # Update last detection time
                    
                    # Handle input states
                    if input_state == "first number" and r == "":
                        if isinstance(gesture, int):
                            first_number += str(gesture)
                            speak(f"Number {gesture} entered")
                        if len(first_number) > 4:
                            input_state = "operator"
                            speak(f"Enter {input_state} Now ")
                    elif input_state == "operator":
                        if gesture in ["+", "-", "*", "/"]:
                            operator = gesture
                            r = operator
                            speak(f"Operator {gesture} entered")
                            input_state = "second number"
                            speak(f"Enter {input_state} of size 5 digits Now")
                    elif input_state == "second number": # and r != "":
                        if isinstance(gesture, int):
                            second_number += str(gesture)
                            speak(f"Number {gesture} entered")
                        if len(second_number) > 4:
                            input_state = "calculate"
                            speak("Wait for a few seconds to get the result")
                    elif input_state == "calculate":
                        if first_number and operator and second_number:
                            try:
                                first_number=str(int(first_number))
                                second_number=str(int(second_number))
                                calculation_result = str(eval(first_number + operator + second_number))
                                speak(f"The result is {calculation_result}")
                            except Exception as e:
                                calculation_result = "Error"
                                speak("There was an error in the calculation")
                            input_state = "first number"
                            first_number = ""
                            second_number = ""
                            operator = ""
                            calculation_result = ""

                # Display the prompts and results on the frame
                if input_state == "first number":
                    prompt = "Enter the first number"
                elif input_state == "operator":
                    prompt = "Enter the operator"
                elif input_state == "second number":
                    prompt = "Enter the second number"
                elif input_state == "calculate":
                    prompt = f"Result: {calculation_result}"

                cv2.putText(frame, prompt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
                # Display the current inputs on the frame
                cv2.putText(frame, f"First Number: {first_number}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Operator: {operator}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Second Number: {second_number}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Result: {calculation_result}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                
                # Draw the hand landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Display the frame
        cv2.imshow('Frame', frame)
        if len(first_number) == 0 and count == 0:
            speak(f"Enter {input_state} of size 5 digits Now")
            count += 1
        

    frame_count += 1
    
    # Exit on pressing 'q'qq
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close windows
cap.release()
cv2.destroyAllWindows()
