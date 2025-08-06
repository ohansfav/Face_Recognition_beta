import tkinter as tk
from tkinter import messagebox, simpledialog
from database import get_users, initialize_database, mark_attendance, get_attendance, remove_attendance
from FR import recognize_and_mark
import subprocess  # Fix: Import subprocess module
import cv2
import face_recognition
import base64
import time
from FR import draw_facial_landmarks  # Reusing the existing AR drawing function
import numpy as np
import pandas as pd
from datetime import datetime
import sys

# Add export_attendance_to_csv to imports
from database import (
    get_users, 
    initialize_database, 
    mark_attendance, 
    get_attendance, 
    remove_attendance,
    export_attendance_to_csv  # Add this import
)

# Global variable for table_frame
table_frame = None

COLORS = {
    'primary': '#2c3e50',    # Dark blue-gray
    'secondary': '#3498db',  # Light blue
    'success': '#2ecc71',    # Green
    'warning': '#f1c40f',    # Yellow
    'danger': '#e74c3c',     # Red
    'background': '#ecf0f1', # Light gray
    'text': '#2c3e50',       # Dark blue-gray
    'white': '#ffffff'       # White
}

GRADIENTS = {
    'primary': ['#2c3e50', '#3498db'],
    'success': ['#27ae60', '#2ecc71'],
    'warning': ['#f39c12', '#f1c40f'],
    'danger': ['#c0392b', '#e74c3c']
}

def register():
    user_id = simpledialog.askstring("Register", "Enter Student/Staff ID:")
    if user_id:
        # Create registration window
        register_window = tk.Toplevel(root)
        register_window.title("Face Registration")
        register_window.geometry("800x600")
        register_window.configure(bg=COLORS['background'])

        def start_registration():
            try:
                # Initialize video capture with optimized settings
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    messagebox.showerror("Error", "Could not open camera.")
                    return

                # Set optimal camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                frame_count = 0
                last_face_locations = []
                last_landmarks_list = []
                rgb_frame = None

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % 3 == 0:
                        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        last_face_locations = face_recognition.face_locations(rgb_small_frame)
                        last_face_locations = [(top*4, right*4, bottom*4, left*4) 
                                             for top, right, bottom, left in last_face_locations]
                        
                        if last_face_locations:
                            last_landmarks_list = face_recognition.face_landmarks(rgb_frame, last_face_locations)

                    if last_face_locations:
                        for (top, right, bottom, left), landmarks in zip(last_face_locations, last_landmarks_list):
                            cv2.rectangle(frame, (left-10, top-10), (right+10, bottom+10), (0, 255, 0), 2)
                            draw_facial_landmarks(frame, landmarks)
                            
                            scan_line_y = int(top + (bottom - top) * (time.time() % 1))
                            cv2.line(frame, (left, scan_line_y), (right, scan_line_y), (0, 255, 0), 1)

                    if frame_count % 15 == 0:
                        cv2.putText(frame, "Press 'S' to Save", (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                        cv2.putText(frame, "Press 'Q' to Quit", (10, 60), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    cv2.imshow("Face Registration", frame)
                    frame_count += 1

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('s'):
                        if len(last_face_locations) == 1:
                            # Save face encoding directly without subprocess
                            face_encoding = face_recognition.face_encodings(rgb_frame, last_face_locations)[0]
                            from database import add_user
                            if add_user(user_id, face_encoding):
                                messagebox.showinfo("Success", "Face registered successfully!")
                            else:
                                messagebox.showerror("Error", "Failed to register face")
                            break
                        else:
                            messagebox.showwarning("Warning", "Please ensure only one face is visible")
                    elif key == ord('q'):
                        break

                cap.release()
                cv2.destroyAllWindows()
                register_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {str(e)}")
                if 'cap' in locals():
                    cap.release()
                cv2.destroyAllWindows()
                register_window.destroy()

        # Add instructions and start button
        tk.Label(
            register_window,
            text="Position your face in front of the camera\nand press 'S' to save",
            font=("Arial", 14),
            bg=COLORS['background'],
            fg=COLORS['text']
        ).pack(pady=20)

        tk.Button(
            register_window,
            text="Start Face Registration",
            font=("Arial", 14),
            bg=COLORS['success'],
            fg=COLORS['white'],
            command=start_registration,
            width=20,
            cursor="hand2"
        ).pack(pady=20)

def attendance():
    global table_frame  # Use global table_frame to avoid recreation
    try:
        # Fetch registered users and attendance data from the database
        users = get_users()
        attendance_data = get_attendance()
        names = [user[1] for user in users]  # Extract names
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch registered users: {e}")
        return

    if not names:
        messagebox.showerror("No Users", "No registered users found.")
        return

    # Clear and configure main window
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=COLORS['background'])
    
    # Create header frame
    header_frame = tk.Frame(root, bg=COLORS['primary'])
    header_frame.pack(fill='x', pady=0)
    
    tk.Label(
        header_frame,
        text="Student Attendance Management",
        font=("Arial", 24, "bold"),
        fg=COLORS['white'],
        bg=COLORS['primary'],
        pady=20
    ).pack()

    # Create main content frame
    content_frame = tk.Frame(root, bg=COLORS['background'])
    content_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # Adjust canvas and table size
    canvas = tk.Canvas(content_frame, bg=COLORS['background'], width=780)  # Fixed width
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    table_frame = tk.Frame(canvas, bg=COLORS['background'])

    # Configure scrolling
    table_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=table_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Create header row with smaller width
    headers = ["Name"] + [f"W{i}" for i in range(1, 13)]  # Shortened week labels
    for col, header in enumerate(headers):
        tk.Label(
            table_frame,
            text=header,
            font=("Arial", 11, "bold"),
            bg=COLORS['secondary'],
            fg=COLORS['white'],
            borderwidth=1,
            relief="solid",
            width=8 if col == 0 else 4,  # Wider for name, narrower for weeks
            pady=8
        ).grid(row=0, column=col, sticky='nsew', padx=1, pady=1)

    # Populate rows with registered names and attendance data
    rows = {}
    for row, name in enumerate(names, start=1):
        # Create name button
        button = tk.Button(
            table_frame,
            text=name,
            font=("Arial", 11),
            bg=COLORS['white'],
            fg=COLORS['text'],
            borderwidth=1,
            relief="solid",
            width=8,  # Wider for name
            cursor="hand2",
            command=lambda n=name: select_user(n, rows)
        )
        button.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
        
        # Bind hover effects
        button.bind('<Enter>', lambda e, b=button: b.configure(bg=COLORS['secondary'], fg=COLORS['white']))
        button.bind('<Leave>', lambda e, b=button: b.configure(bg=COLORS['white'], fg=COLORS['text']))
        
        rows[name] = row
        
        # Create attendance cells
        for col in range(1, 13):
            week_key = f"week_{col}"
            mark = attendance_data.get(name, {}).get(week_key, "")
            cell = tk.Label(
                table_frame,
                text=mark,
                font=("Arial", 11),
                bg=COLORS['white'] if not mark else COLORS['success'],
                fg=COLORS['text'] if not mark else COLORS['white'],
                borderwidth=1,
                relief="solid",
                width=4  # Narrower for week cells
            )
            cell.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)

    # Create bottom button frame
    button_frame = tk.Frame(root, bg=COLORS['background'])
    button_frame.pack(pady=20, padx=20)

    tk.Button(
        button_frame,
        text="Back to Main Menu",
        font=("Arial", 14),
        bg=COLORS['primary'],
        fg=COLORS['white'],
        command=show_main_menu,
        width=25,
        cursor="hand2"
    ).pack(pady=10)

def select_user(selected_name, rows):
    attendance_window = tk.Toplevel(root)
    attendance_window.title("Mark Attendance")
    attendance_window.geometry("600x700")
    attendance_window.configure(bg=COLORS['background'])
    
    # Add header frame with gradient
    header_frame = tk.Frame(attendance_window, bg=COLORS['primary'], height=100)
    header_frame.pack(fill='x', pady=0)
    header_frame.pack_propagate(False)

    tk.Label(
        header_frame,
        text="Attendance Portal",
        font=("Arial", 24, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white']
    ).pack(pady=(20,0))

    tk.Label(
        header_frame,
        text=selected_name,
        font=("Arial", 16),
        bg=COLORS['primary'],
        fg=COLORS['white']
    ).pack()

    # Create main content frame
    content_frame = tk.Frame(attendance_window, bg=COLORS['background'])
    content_frame.pack(padx=40, pady=30, fill='both', expand=True)

    # Add attendance status indicators
    status_frame = tk.Frame(content_frame, bg=COLORS['background'])
    status_frame.pack(fill='x', pady=(0,20))

    def create_status_box(title, value, color):
        box = tk.Frame(status_frame, bg=COLORS['white'], padx=15, pady=10)
        box.pack(side='left', expand=True, padx=5)
        
        tk.Label(
            box,
            text=title,
            font=("Arial", 12),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack()
        
        tk.Label(
            box,
            text=value,
            font=("Arial", 20, "bold"),
            bg=COLORS['white'],
            fg=color
        ).pack()

    # Get attendance statistics
    total_weeks = 12
    attended = sum(1 for mark in get_attendance().get(selected_name, {}).values() if mark)
    attendance_rate = (attended / total_weeks) * 100

    create_status_box("Total Weeks", str(total_weeks), COLORS['primary'])
    create_status_box("Attended", str(attended), COLORS['success'])
    create_status_box("Rate", f"{attendance_rate:.1f}%", COLORS['secondary'])

    # Week selection with modern styling
    tk.Label(
        content_frame,
        text="Select Week",
        font=("Arial", 14, "bold"),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack(pady=(20,10))

    weeks_frame = tk.Frame(content_frame, bg=COLORS['background'])
    weeks_frame.pack(fill='x', pady=10)

    selected_week = tk.StringVar(value="Week 1")
    
    # Get current attendance data
    attendance_data = get_attendance().get(selected_name, {})
    
    for i in range(1, 13, 4):
        row_frame = tk.Frame(weeks_frame, bg=COLORS['background'])
        row_frame.pack(fill='x', pady=5)
        
        for j in range(4):
            week_num = i + j
            if week_num <= 12:
                # Check if week is marked
                is_marked = attendance_data.get(f'week_{week_num}', False)
                
                btn = tk.Button(
                    row_frame,
                    text=f"Week {week_num}" + (" ✓" if is_marked else ""),
                    font=("Arial", 12),
                    bg=COLORS['success'] if is_marked else COLORS['white'],
                    fg=COLORS['white'] if is_marked else COLORS['text'],
                    command=lambda w=f"Week {week_num}": selected_week.set(w),
                    width=12,
                    cursor="hand2"
                )
                btn.pack(side='left', padx=5, expand=True)

    # Face scan section
    scan_frame = tk.Frame(content_frame, bg=COLORS['background'])
    scan_frame.pack(fill='x', pady=20)

    def start_face_scan():
        week_number = int(selected_week.get().split(" ")[1])
        progress_label.config(text="Scanning face...")
        
        # Perform face recognition
        if recognize_and_mark(selected_name, week_number):
            if mark_attendance(selected_name, week_number):
                messagebox.showinfo("Success", 
                    f"Attendance marked for {selected_name} - Week {week_number}")
                
                # Update the attendance display
                attendance_data = get_attendance()
                attended = sum(1 for mark in attendance_data.get(selected_name, {}).values() if mark)
                attendance_rate = (attended / total_weeks) * 100
                
                # Update statistics
                for widget in status_frame.winfo_children():
                    widget.destroy()
                
                create_status_box("Total Weeks", str(total_weeks), COLORS['primary'])
                create_status_box("Attended", str(attended), COLORS['success'])
                create_status_box("Rate", f"{attendance_rate:.1f}%", COLORS['secondary'])
                
                # Update all week buttons to show correct state
                for widget in weeks_frame.winfo_children():
                    for btn in widget.winfo_children():
                        week_text = btn.cget('text').split(" ")[1]  # Get week number
                        week_num = int(week_text)
                        is_marked = attendance_data.get(selected_name, {}).get(f'week_{week_num}', False)
                        
                        btn.configure(
                            text=f"Week {week_num}" + (" ✓" if is_marked else ""),
                            bg=COLORS['success'] if is_marked else COLORS['white'],
                            fg=COLORS['white'] if is_marked else COLORS['text']
                        )
                
                # Update main attendance table
                if table_frame:
                    row = rows.get(selected_name)
                    if row is not None:
                        cell = table_frame.grid_slaves(row=row, column=week_number)[0]
                        cell.configure(
                            text="✓",
                            bg=COLORS['success'],
                            fg=COLORS['white']
                        )
                
                # Update progress label
                progress_label.config(text="Ready to scan next week")
            else:
                messagebox.showerror("Error", "Failed to mark attendance")
                progress_label.config(text="Scan failed - Try again")
        else:
            messagebox.showerror("Error", "Face recognition failed")
            progress_label.config(text="Scan failed - Try again")

    tk.Button(
        scan_frame,
        text="Start Face Scan",
        font=("Arial", 14, "bold"),
        bg=COLORS['success'],
        fg=COLORS['white'],
        command=start_face_scan,
        width=20,
        cursor="hand2"
    ).pack(pady=10)

    progress_label = tk.Label(
        scan_frame,
        text="Ready to scan",
        font=("Arial", 12),
        bg=COLORS['background'],
        fg=COLORS['text']
    )
    progress_label.pack()

    # Bottom buttons
    button_frame = tk.Frame(content_frame, bg=COLORS['background'])
    button_frame.pack(side='bottom', fill='x', pady=20)

    tk.Button(
        button_frame,
        text="View History",
        font=("Arial", 12),
        bg=COLORS['secondary'],
        fg=COLORS['white'],
        command=lambda: show_attendance_history(selected_name),
        width=15,
        cursor="hand2"
    ).pack(side='left', padx=5, expand=True)

    tk.Button(
        button_frame,
        text="Cancel",
        font=("Arial", 12),
        bg=COLORS['danger'],
        fg=COLORS['white'],
        command=attendance_window.destroy,
        width=15,
        cursor="hand2"
    ).pack(side='left', padx=5, expand=True)

def admin_login():
    login = tk.Toplevel(root)
    login.title("Admin Login")
    tk.Label(login, text="Username:").pack()
    username_entry = tk.Entry(login)
    username_entry.pack()
    tk.Label(login, text="Password:").pack()
    password_entry = tk.Entry(login, show="*")
    password_entry.pack()

    def check_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "admin" and password == "admin":
            login.destroy()
            admin_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    tk.Button(login, text="Login", command=check_login).pack(pady=10)

def show_user_details():
    details_window = tk.Toplevel(root)
    details_window.title("User Management")
    details_window.geometry("1000x600")
    details_window.configure(bg=COLORS['background'])

    # Create scrollable container
    main_container = tk.Frame(details_window, bg=COLORS['background'])
    main_container.pack(fill='both', expand=True)

    canvas = tk.Canvas(main_container, bg=COLORS['background'])
    scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Header
    tk.Label(
        scrollable_frame,
        text="Registered Users Details",
        font=("Arial", 20, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white'],
        pady=15
    ).pack(fill='x')

    # Get all users
    users = get_users()

    for user in users:
        user_id, name, face_encoding = user
        
        user_frame = tk.Frame(
            scrollable_frame,
            bg=COLORS['white'],
            padx=20,
            pady=15,
            relief="raised",
            bd=1
        )
        user_frame.pack(fill='x', padx=20, pady=10)

        # User header with ID and name
        header_frame = tk.Frame(user_frame, bg=COLORS['white'])
        header_frame.pack(fill='x')

        tk.Label(
            header_frame,
            text=f"ID: {user_id}",
            font=("Arial", 14, "bold"),
            bg=COLORS['white'],
            fg=COLORS['primary']
        ).pack(side='left')

        tk.Label(
            header_frame,
            text=f"Name: {name}",
            font=("Arial", 14),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(side='left', padx=20)

        # Attendance statistics
        stats_frame = tk.Frame(user_frame, bg=COLORS['white'])
        stats_frame.pack(fill='x', pady=(10,0))

        attendance_data = get_attendance().get(name, {})
        total_attendance = sum(1 for key, value in attendance_data.items() if key.startswith('week_') and value)
        attendance_rate = (total_attendance / 12) * 100

        tk.Label(
            stats_frame,
            text=f"Total Attendance: {total_attendance}/12",
            font=("Arial", 12),
            bg=COLORS['white']
        ).pack(side='left')

        tk.Label(
            stats_frame,
            text=f"Rate: {attendance_rate:.1f}%",
            font=("Arial", 12),
            bg=COLORS['white']
        ).pack(side='left', padx=20)

        # Weekly attendance grid
        weeks_frame = tk.Frame(user_frame, bg=COLORS['white'])
        weeks_frame.pack(fill='x', pady=10)

        for week in range(1, 13):
            week_key = f'week_{week}'
            is_present = attendance_data.get(week_key, False)
            
            week_label = tk.Label(
                weeks_frame,
                text=f"W{week}",
                font=("Arial", 10),
                bg=COLORS['success'] if is_present else COLORS['danger'],
                fg=COLORS['white'],
                width=3,
                pady=2
            )
            week_label.pack(side='left', padx=2)

        # Action buttons
        button_frame = tk.Frame(user_frame, bg=COLORS['white'])
        button_frame.pack(fill='x', pady=(10,0))

        tk.Button(
            button_frame,
            text="View Details",
            font=("Arial", 11),
            bg=COLORS['secondary'],
            fg=COLORS['white'],
            command=lambda n=name: show_attendance_history(n),
            cursor="hand2"
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Remove User",
            font=("Arial", 11),
            bg=COLORS['danger'],
            fg=COLORS['white'],
            command=lambda i=user_id: remove_specific_user_from_view(i, details_window),
            cursor="hand2"
        ).pack(side='left', padx=5)

    # Pack scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Add mousewheel scrolling
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

def admin_panel():
    panel = tk.Toplevel(root)
    panel.title("Admin Dashboard")
    panel.geometry("800x600")
    panel.configure(bg=COLORS['background'])

    # Main container with scroll
    main_container = tk.Frame(panel, bg=COLORS['background'])
    main_container.pack(fill='both', expand=True)

    canvas = tk.Canvas(main_container, bg=COLORS['background'])
    scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Important: Set a fixed width for the window content
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=780)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Header
    header_frame = tk.Frame(scrollable_frame, bg=COLORS['primary'], height=100)
    header_frame.pack(fill='x', pady=0)
    header_frame.pack_propagate(False)

    tk.Label(
        header_frame,
        text="Admin Dashboard",
        font=("Arial", 24, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white']
    ).pack(pady=(30,0))

    # Main content
    content_frame = tk.Frame(scrollable_frame, bg=COLORS['background'])
    content_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Statistics section
    stats_frame = tk.Frame(content_frame, bg=COLORS['background'])
    stats_frame.pack(fill='x', pady=(0,20))

    def create_stat_box(title, value, color):
        box = tk.Frame(stats_frame, bg=COLORS['white'], padx=15, pady=10)
        box.pack(side='left', expand=True, padx=5)
        
        tk.Label(
            box,
            text=title,
            font=("Arial", 12),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack()
        
        tk.Label(
            box,
            text=value,
            font=("Arial", 20, "bold"),
            bg=COLORS['white'],
            fg=color
        ).pack()

    # Get and display statistics
    total_users = len(get_users())
    total_attendance = sum(len(marks) for marks in get_attendance().values())
    attendance_rate = f"{(total_attendance / (total_users * 12) * 100):.1f}%" if total_users > 0 else "0%"

    create_stat_box("Total Users", str(total_users), COLORS['primary'])
    create_stat_box("Total Attendance", str(total_attendance), COLORS['success'])
    create_stat_box("Attendance Rate", attendance_rate, COLORS['secondary'])

    # Warning section
    warning_frame = tk.Frame(content_frame, bg=COLORS['danger'], pady=10)
    warning_frame.pack(fill='x', pady=10)
    
    tk.Label(
        warning_frame,
        text="⚠️ Warning: User removal actions cannot be undone!",
        font=("Arial", 12, "bold"),
        bg=COLORS['danger'],
        fg=COLORS['white']
    ).pack()

    # Actions section
    actions_frame = tk.Frame(content_frame, bg=COLORS['background'])
    actions_frame.pack(fill='x', pady=10)

    tk.Label(
        content_frame,
        text="Quick Actions",
        font=("Arial", 16, "bold"),
        bg=COLORS['background'],
        fg=COLORS['text']
    ).pack(pady=(20,10))

    def create_action_button(text, command, icon="📊"):
        btn_frame = tk.Frame(actions_frame, bg=COLORS['white'])
        btn_frame.pack(fill='x', pady=5)
        
        tk.Label(
            btn_frame,
            text=icon,
            font=("Arial", 20),
            bg=COLORS['white'],
            width=2
        ).pack(side='left', padx=10)
        
        tk.Button(
            btn_frame,
            text=text,
            font=("Arial", 12),
            bg=COLORS['white'],
            fg=COLORS['text'],
            command=command,
            bd=0,
            cursor="hand2",
            anchor='w',
            width=30
        ).pack(side='left', fill='x', expand=True, padx=10, pady=8)

    create_action_button("View All Users", show_user_details, "👥")
    create_action_button("Export Attendance Report", export_excel, "📊")
    create_action_button("Remove Attendance Records", remove_specific_user, "🗑️")
    create_action_button("View Attendance Analytics", show_user_details, "📈")
    create_action_button("Send Email Report", send_email_report, "📧")
    create_action_button("Change Admin Password", change_admin_password, "🔑")

    # Pack scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Logout button at bottom
    tk.Button(
        panel,
        text="Logout",
        font=("Arial", 12),
        bg=COLORS['danger'],
        fg=COLORS['white'],
        command=panel.destroy,
        width=15,
        cursor="hand2"
    ).pack(pady=10)

    # Configure mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Add keyboard shortcuts
    def _on_key(event):
        if event.keysym == 'Escape':
            panel.destroy()
    panel.bind('<Key>', _on_key)

def send_email_report():
    from emailer import send_email_report
    send_email_report()
    messagebox.showinfo("Email", "Email sent (check your inbox).")

def change_admin_password():
    new_pass = simpledialog.askstring("Change Password", "Enter new admin password:", show="*")
    if new_pass:
        # Save new password securely (implement this in your database or config)
        messagebox.showinfo("Success", "Admin password changed.")

def show_main_menu():
    # Clear the main window and display the main menu
    for widget in root.winfo_children():
        widget.destroy()

    # Configure root window
    root.configure(bg=COLORS['background'])

    # Create header frame
    header_frame = tk.Frame(root, bg=COLORS['primary'])
    header_frame.pack(fill='x', pady=0)

    # Add welcome text
    tk.Label(
        header_frame,
        text="AI Attendance System",
        font=("Arial", 28, "bold"),
        fg=COLORS['white'],
        bg=COLORS['primary'],
        pady=25
    ).pack()

    # Create main content frame with padding
    content_frame = tk.Frame(root, bg=COLORS['background'])
    content_frame.pack(pady=40, padx=50, fill='both', expand=True)

    # Add descriptive text
    tk.Label(
        content_frame,
        text="Welcome to Smart Attendance Management",
        font=("Arial", 16),
        fg=COLORS['text'],
        bg=COLORS['background'],
        pady=10
    ).pack()

    # Create buttons with hover effect
    def on_enter(e):
        e.widget.configure(bg=COLORS['secondary'])

    def on_leave(e):
        e.widget.configure(bg=COLORS['primary'])

    # Register button
    register_btn = tk.Button(
        content_frame,
        text="Register New Face",
        font=("Arial", 14, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white'],
        command=register,
        width=25,
        cursor="hand2",
        relief="flat",
        pady=10
    )
    register_btn.pack(pady=15)
    register_btn.bind("<Enter>", on_enter)
    register_btn.bind("<Leave>", on_leave)

    # Attendance button
    attendance_btn = tk.Button(
        content_frame,
        text="Mark Attendance",
        font=("Arial", 14, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white'],
        command=attendance,
        width=25,
        cursor="hand2",
        relief="flat",
        pady=10
    )
    attendance_btn.pack(pady=15)
    attendance_btn.bind("<Enter>", on_enter)
    attendance_btn.bind("<Leave>", on_leave)

    # Admin button
    admin_btn = tk.Button(
        content_frame,
        text="Admin Login",
        font=("Arial", 14, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white'],
        command=admin_login,
        width=25,
        cursor="hand2",
        relief="flat",
        pady=10
    )
    admin_btn.pack(pady=15)
    admin_btn.bind("<Enter>", on_enter)
    admin_btn.bind("<Leave>", on_leave)

    # Add footer
    tk.Label(
        content_frame,
        text="© 2025 AI Attendance System",
        font=("Arial", 10),
        fg=COLORS['text'],
        bg=COLORS['background'],
        pady=20
    ).pack(side="bottom")

def remove_specific_user():
    """Remove a specific user from the database"""
    user_id = simpledialog.askstring("Remove User", "Enter Student/Staff ID to remove:")
    if user_id:
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove user {user_id}?"):
            from database import remove_user
            if remove_user(user_id):
                messagebox.showinfo("Success", "User removed successfully")
            else:
                messagebox.showerror("Error", "Failed to remove user")

def clear_all_users():
    """Clear all users from the database"""
    if messagebox.askyesno("Confirm", "Are you sure you want to remove ALL users? This cannot be undone!"):
        confirm = simpledialog.askstring(
            "Confirm", 
            "Type 'DELETE' to confirm removal of all users:",
            parent=root
        )
        if confirm == "DELETE":
            from database import clear_all_users
            if clear_all_users():
                messagebox.showinfo("Success", "All users have been removed")
            else:
                messagebox.showerror("Error", "Failed to remove users")

def export_excel():
    """Export attendance records to CSV"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'attendance_report_{timestamp}.csv'
        
        if export_attendance_to_csv(filename):
            messagebox.showinfo(
                "Success", 
                f"Attendance exported to:\n{filename}\n\nLocation: exports folder"
            )
        else:
            messagebox.showerror("Error", "Failed to export attendance data")
    except Exception as e:
        messagebox.showerror("Error", f"Export failed: {str(e)}")

def show_attendance_history(selected_name):
    """Show attendance history for a specific user"""
    history_window = tk.Toplevel(root)
    history_window.title(f"Attendance History - {selected_name}")
    history_window.geometry("600x400")
    history_window.configure(bg=COLORS['background'])

    # Header
    header_frame = tk.Frame(history_window, bg=COLORS['primary'], height=80)
    header_frame.pack(fill='x', pady=0)
    header_frame.pack_propagate(False)

    tk.Label(
        header_frame,
        text=f"Attendance History for {selected_name}",
        font=("Arial", 16, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white']
    ).pack(pady=(20,0))

    # Content frame
    content_frame = tk.Frame(history_window, bg=COLORS['background'])
    content_frame.pack(padx=20, pady=20, fill='both', expand=True)

    # Create history table
    attendance_data = get_attendance().get(selected_name, {})
    
    # Headers
    headers = ["Week", "Status", "Date Marked"]
    for col, header in enumerate(headers):
        tk.Label(
            content_frame,
            text=header,
            font=("Arial", 12, "bold"),
            bg=COLORS['secondary'],
            fg=COLORS['white'],
            width=15,
            pady=5
        ).grid(row=0, column=col, padx=2, pady=2, sticky='nsew')

    # Populate data
    for week in range(1, 13):
        week_key = f"week_{week}"
        status = "✓" if attendance_data.get(week_key) else "✗"
        status_color = COLORS['success'] if status == "✓" else COLORS['danger']
        
        # Week number
        tk.Label(
            content_frame,
            text=f"Week {week}",
            font=("Arial", 11),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).grid(row=week, column=0, padx=2, pady=2, sticky='nsew')
        
        # Status
        tk.Label(
            content_frame,
            text=status,
            font=("Arial", 11, "bold"),
            bg=status_color,
            fg=COLORS['white']
        ).grid(row=week, column=1, padx=2, pady=2, sticky='nsew')
        
        # Date (if marked)
        date_text = attendance_data.get(f"{week_key}_date", "Not marked")
        tk.Label(
            content_frame,
            text=date_text,
            font=("Arial", 11),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).grid(row=week, column=2, padx=2, pady=2, sticky='nsew')

    # Configure grid weights
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    content_frame.grid_columnconfigure(2, weight=1)

def show_user_details():
    details_window = tk.Toplevel(root)
    details_window.title("User Management")
    details_window.geometry("1000x600")
    details_window.configure(bg=COLORS['background'])

    # Create scrollable container
    main_container = tk.Frame(details_window, bg=COLORS['background'])
    main_container.pack(fill='both', expand=True)

    canvas = tk.Canvas(main_container, bg=COLORS['background'])
    scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Header
    tk.Label(
        scrollable_frame,
        text="Registered Users Details",
        font=("Arial", 20, "bold"),
        bg=COLORS['primary'],
        fg=COLORS['white'],
        pady=15
    ).pack(fill='x')

    # Get all users
    users = get_users()

    for user in users:
        user_id, name, face_encoding = user
        
        user_frame = tk.Frame(
            scrollable_frame,
            bg=COLORS['white'],
            padx=20,
            pady=15,
            relief="raised",
            bd=1
        )
        user_frame.pack(fill='x', padx=20, pady=10)

        # User header with ID and name
        header_frame = tk.Frame(user_frame, bg=COLORS['white'])
        header_frame.pack(fill='x')

        tk.Label(
            header_frame,
            text=f"ID: {user_id}",
            font=("Arial", 14, "bold"),
            bg=COLORS['white'],
            fg=COLORS['primary']
        ).pack(side='left')

        tk.Label(
            header_frame,
            text=f"Name: {name}",
            font=("Arial", 14),
            bg=COLORS['white'],
            fg=COLORS['text']
        ).pack(side='left', padx=20)

        # Attendance statistics
        stats_frame = tk.Frame(user_frame, bg=COLORS['white'])
        stats_frame.pack(fill='x', pady=(10,0))

        attendance_data = get_attendance().get(name, {})
        total_attendance = sum(1 for key, value in attendance_data.items() if key.startswith('week_') and value)
        attendance_rate = (total_attendance / 12) * 100

        tk.Label(
            stats_frame,
            text=f"Total Attendance: {total_attendance}/12",
            font=("Arial", 12),
            bg=COLORS['white']
        ).pack(side='left')

        tk.Label(
            stats_frame,
            text=f"Rate: {attendance_rate:.1f}%",
            font=("Arial", 12),
            bg=COLORS['white']
        ).pack(side='left', padx=20)

        # Weekly attendance grid
        weeks_frame = tk.Frame(user_frame, bg=COLORS['white'])
        weeks_frame.pack(fill='x', pady=10)

        for week in range(1, 13):
            week_key = f'week_{week}'
            is_present = attendance_data.get(week_key, False)
            
            week_label = tk.Label(
                weeks_frame,
                text=f"W{week}",
                font=("Arial", 10),
                bg=COLORS['success'] if is_present else COLORS['danger'],
                fg=COLORS['white'],
                width=3,
                pady=2
            )
            week_label.pack(side='left', padx=2)

        # Action buttons
        button_frame = tk.Frame(user_frame, bg=COLORS['white'])
        button_frame.pack(fill='x', pady=(10,0))

        tk.Button(
            button_frame,
            text="View Details",
            font=("Arial", 11),
            bg=COLORS['secondary'],
            fg=COLORS['white'],
            command=lambda n=name: show_attendance_history(n),
            cursor="hand2"
        ).pack(side='left', padx=5)

        tk.Button(
            button_frame,
            text="Remove User",
            font=("Arial", 11),
            bg=COLORS['danger'],
            fg=COLORS['white'],
            command=lambda i=user_id: remove_specific_user_from_view(i, details_window),
            cursor="hand2"
        ).pack(side='left', padx=5)

    # Pack scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Add mousewheel scrolling
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

def remove_specific_user_from_view(user_id, parent_window):
    if messagebox.askyesno("Confirm", f"Are you sure you want to remove user {user_id}?"):
        from database import remove_user
        if remove_user(user_id):
            messagebox.showinfo("Success", "User removed successfully")
            parent_window.destroy()
            show_user_details()  # Refresh the view
        else:
            messagebox.showerror("Error", "Failed to remove user")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI Attendance System")
    root.geometry("800x600")  # Set initial window size
    root.protocol("WM_DELETE_WINDOW", root.quit)  # Proper window closing
    
    # Initialize database
    initialize_database()
    
    # Show the main menu
    show_main_menu()
    
    # Start the main event loop
    root.mainloop()