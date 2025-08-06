import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from database import export_attendance_to_excel
import os

def send_email_report():
    try:
        # Generate Excel report
        filename = 'attendance_report.xlsx'
        if not export_attendance_to_excel(filename):
            raise Exception("Failed to generate Excel report")

        # Email configuration
        sender_email = "your_email@gmail.com"  # Replace with your email
        sender_password = "your_app_password"   # Replace with your app password
        receiver_email = "receiver@email.com"   # Replace with recipient email

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Attendance Report"

        # Add body
        body = "Please find attached the attendance report."
        message.attach(MIMEText(body, "plain"))

        # Attach Excel file
        with open(filename, "rb") as file:
            excel_attachment = MIMEApplication(file.read(), _subtype="xlsx")
            excel_attachment.add_header(
                "Content-Disposition", 
                "attachment", 
                filename=filename
            )
            message.attach(excel_attachment)

        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)

        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False