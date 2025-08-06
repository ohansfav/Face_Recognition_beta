import sqlite3
import csv
from datetime import datetime
import os

# Ensure database is created in the program directory
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")

def initialize_database():
    """Initialize database if it doesn't exist"""
    # Only create tables if they don't exist
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        face_encoding BLOB
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        week INTEGER,
        marked BOOLEAN DEFAULT FALSE,
        date_marked TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()

def add_user(name, face_encoding):
    """Add a new user to the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE id = ?", (name,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE users 
                SET face_encoding = ? 
                WHERE id = ?
            """, (face_encoding.tobytes(), name))
        else:
            cursor.execute("""
                INSERT INTO users (id, name, face_encoding) 
                VALUES (?, ?, ?)
            """, (name, name, face_encoding.tobytes()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

def get_users():
    """Get all registered users"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def mark_attendance(student_id, week):
    """Mark attendance for a student in a specific week"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute("""
            SELECT * FROM attendance 
            WHERE student_id = ? AND week = ?
        """, (student_id, week))
        
        if cursor.fetchone():
            # Update existing record
            cursor.execute("""
                UPDATE attendance 
                SET marked = TRUE, 
                    date_marked = ? 
                WHERE student_id = ? AND week = ?
            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), student_id, week))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO attendance 
                (student_id, week, marked, date_marked) 
                VALUES (?, ?, TRUE, ?)
            """, (student_id, week, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False

def get_attendance():
    """Get all attendance records"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.name, a.week, a.marked, a.date_marked 
            FROM users u 
            LEFT JOIN attendance a ON u.id = a.student_id
        """)
        
        attendance_dict = {}
        for name, week, marked, date in cursor.fetchall():
            if name not in attendance_dict:
                attendance_dict[name] = {}
            if marked:
                attendance_dict[name][f'week_{week}'] = True
                attendance_dict[name][f'week_{week}_date'] = date
        
        conn.close()
        return attendance_dict
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return {}

def remove_attendance(name, week=None):
    """Remove attendance record(s) for a user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if week is None:
            # Clear all weeks for the user
            cursor.execute("""
            UPDATE attendance 
            SET week=NULL, marked=NULL, date_marked=NULL
            WHERE student_id = ?
            """, (name,))
        else:
            # Clear specific week
            cursor.execute(f"UPDATE attendance SET week = NULL, marked = NULL, date_marked = NULL WHERE student_id = ?",
                         (name,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error removing attendance: {e}")
        return False

EXPORT_FOLDER = 'exports'

def export_attendance_to_excel(filename='attendance_report.csv'):
    """Export attendance records to an Excel file"""
    try:
        export_path = os.path.join(EXPORT_FOLDER, filename)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM users ORDER BY name')
        users = cursor.fetchall()
        
        cursor.execute('''
            SELECT u.name, a.week, a.marked 
            FROM users u 
            LEFT JOIN attendance a ON u.id = a.student_id
            ORDER BY u.name, a.week
        ''')
        records = cursor.fetchall()
        
        # Process data without using openpyxl
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name'] + [f'Week {i+1}' for i in range(12)])
            
            attendance_data = {}
            for name, week, marked in records:
                if name not in attendance_data:
                    attendance_data[name] = [''] * 12
                if marked and week is not None:
                    attendance_data[name][week-1] = '✓'
            
            for user in users:
                name = user[0]
                row = [name]
                row.extend(attendance_data.get(name, [''] * 12))
                writer.writerow(row)
        
        conn.close()
        return export_path
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def export_attendance_to_csv(filename='attendance_report.csv'):
    """Export attendance records to CSV"""
    try:
        # Create exports directory if it doesn't exist
        if not os.path.exists('exports'):
            os.makedirs('exports')
            
        export_path = os.path.join('exports', filename)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get all users and attendance data
        cursor.execute('SELECT name FROM users ORDER BY name')
        users = cursor.fetchall()
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name'] + [f'Week {i+1}' for i in range(12)])
            
            for user in users:
                name = user[0]
                cursor.execute('''
                    SELECT week, marked FROM attendance 
                    WHERE student_id = ? ORDER BY week
                ''', (name,))
                attendance = cursor.fetchall()
                
                row = [name]
                attendance_dict = {week: mark for week, mark in attendance}
                for week in range(1, 13):
                    row.append('✓' if attendance_dict.get(week, False) else '')
                writer.writerow(row)
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def remove_user(user_id):
    """Remove a user and their attendance records"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Remove attendance records first
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (user_id,))
        
        # Then remove user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error removing user: {e}")
        return False

def clear_all_users():
    """Remove all users and attendance records"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Clear attendance first
        cursor.execute('DELETE FROM attendance')
        
        # Then clear users
        cursor.execute('DELETE FROM users')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing users: {e}")
        return False