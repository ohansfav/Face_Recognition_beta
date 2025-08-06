import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import get_attendance, get_users

def show_reports_window():
    reports_window = tk.Toplevel()
    reports_window.title("Attendance Analytics")
    reports_window.geometry("800x600")

    # Get data
    attendance_data = get_attendance()
    users = get_users()

    # Calculate statistics
    total_users = len(users)
    weeks = range(1, 13)
    weekly_attendance = []
    
    for week in weeks:
        week_attendance = sum(1 for user_attendance in attendance_data.values() 
                            if f"week_{week}" in user_attendance 
                            and user_attendance[f"week_{week}"])
        weekly_attendance.append(week_attendance)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Weekly attendance graph
    ax1.plot(weeks, weekly_attendance, marker='o')
    ax1.set_title('Weekly Attendance Trend')
    ax1.set_xlabel('Week')
    ax1.set_ylabel('Number of Students')
    ax1.grid(True)

    # Attendance rate pie chart
    total_possible = total_users * 12
    total_attended = sum(weekly_attendance)
    attendance_rate = (total_attended / total_possible) * 100 if total_possible > 0 else 0
    
    ax2.pie([attendance_rate, 100-attendance_rate], 
            labels=['Present', 'Absent'], 
            colors=['#2ecc71', '#e74c3c'],
            autopct='%1.1f%%')
    ax2.set_title('Overall Attendance Rate')

    # Embed in tkinter window
    canvas = FigureCanvasTkAgg(fig, master=reports_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    plt.tight_layout()