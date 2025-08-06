import sys
import tkinter as tk
import cv2
import face_recognition
from tkinter import messagebox
from database import add_user
import sqlite3

def register_face(user_id):
    name = user_id  # Use the provided user ID as the name

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open default camera.")
        return

    messagebox.showinfo("Info", "Press 'S' in the camera window to capture your face, 'Q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image.")
            break

        # Display the camera feed
        cv2.imshow("Registration - Press 'S' to capture, 'Q' to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):  # Capture face
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)  # Detect face locations
            encodings = face_recognition.face_encodings(rgb, boxes)  # Encode detected faces

            if encodings:
                face_encoding = encodings[0]
                # Add user to database with face encoding
                if add_user(name, face_encoding):
                    messagebox.showinfo("Success", "User registered successfully!")
                else:
                    messagebox.showerror("Error", "Failed to register user.")
            else:
                messagebox.showerror("Error", "No face detected. Please try again.")
            break
        elif key == ord('q'):  # Quit registration
            break

    cap.release()
    cv2.destroyAllWindows()

def add_user(name, encoding):
    try:
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        query = "INSERT INTO users (name, encoding) VALUES (?, ?)"
        cursor.execute(query, (name, encoding.tobytes()))  # Convert encoding to bytes for storage
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

def main():
    root = tk.Tk()
    root.title("Register New Face")
    tk.Button(root, text="Start Registration", command=lambda: register_face("User")).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    if user_id:
        register_face(user_id)