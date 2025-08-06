import sys
import cv2
import face_recognition
import numpy as np
from tkinter import messagebox
from database import mark_attendance, get_users
import time

def draw_facial_landmarks(frame, landmarks):
    """Draw facial landmarks with triangulation"""
    try:
        # Convert landmarks to numpy arrays for easier processing
        points = []
        for feature in landmarks.values():
            points.extend(feature)
        points = np.array(points, dtype=np.int32)

        # Draw landmarks
        for point in points:
            cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)

        # Create triangulation
        if len(points) > 3:
            hull = cv2.convexHull(points)
            cv2.polylines(frame, [hull], True, (0, 255, 0), 1)

    except Exception as e:
        print(f"Error drawing landmarks: {e}")

def recognize_and_mark(selected_name, week_number):
    try:
        # Pre-load user data
        users = get_users()
        if not users:
            messagebox.showerror("Error", "No registered users found.")
            return False

        names = [user[1] for user in users]
        encodings = [np.frombuffer(user[2], dtype=np.float64) for user in users]

        # Initialize video capture with optimal settings
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open camera.")
            return False

        # Optimize camera settings
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        # Initialize variables
        frame_count = 0
        match_count = 0
        required_matches = 3
        last_face_locations = []
        last_landmarks_list = []
        process_this_frame = True

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process every 3rd frame for detection
            if frame_count % 3 == 0:
                # Resize for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Detect faces in smaller frame
                face_locations = face_recognition.face_locations(
                    rgb_small_frame, 
                    model="hog"  # Use HOG for faster processing
                )

                if face_locations:
                    # Scale back to original size
                    face_locations = [(top*4, right*4, bottom*4, left*4) 
                                    for top, right, bottom, left in face_locations]
                    
                    if len(face_locations) == 1:  # Only process if one face detected
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        last_landmarks_list = face_recognition.face_landmarks(rgb_frame, face_locations)
                        
                        # Get and compare face encoding
                        face_encoding = face_recognition.face_encodings(
                            rgb_frame, 
                            face_locations,
                            num_jitters=0  # Reduce jitters for speed
                        )[0]
                        
                        # Use numpy for faster comparison
                        face_distances = face_recognition.face_distance(encodings, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        
                        if face_distances[best_match_index] < 0.6:  # Adjusted threshold
                            if names[best_match_index] == selected_name:
                                match_count += 1
                            else:
                                match_count = 0
                        else:
                            match_count = 0
                            
                        last_face_locations = face_locations
                    else:
                        match_count = 0

            # Draw AR elements every frame
            if last_face_locations and last_landmarks_list:
                for (top, right, bottom, left), landmarks in zip(last_face_locations, last_landmarks_list):
                    # Draw box
                    color = (0, 255, 0) if match_count > 0 else (0, 165, 255)
                    cv2.rectangle(frame, (left-10, top-10), (right+10, bottom+10), color, 2)
                    
                    # Draw progress bar
                    progress_width = int((right - left) * (match_count / required_matches))
                    cv2.rectangle(frame, (left, top-20), (left + progress_width, top-15), color, -1)
                    
                    # Add match counter
                    if match_count > 0:
                        cv2.putText(frame, f"Match: {match_count}/{required_matches}", 
                                  (left, top-25), cv2.FONT_HERSHEY_SIMPLEX, 
                                  0.6, color, 2)

            # Show frame
            cv2.imshow("Face Recognition", frame)
            
            # Check for completion or quit
            if match_count >= required_matches:
                cv2.destroyAllWindows()
                cap.release()
                return True

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()
        return False

    except Exception as e:
        print(f"Error in recognize_and_mark: {e}")
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()
        return False

    return False

if __name__ == "__main__":
    # Example usage (rows and table_frame should be passed from the main program)
    recognize_and_mark(selected_name="", week_number=1)