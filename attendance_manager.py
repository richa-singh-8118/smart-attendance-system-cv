import os
import csv
from datetime import datetime

class AttendanceManager:
    def __init__(self, db_folder='database'):
        self.db_folder = db_folder
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
            
    def mark_attendance(self, name, location="Office - Main Gate", late_threshold="09:15:00"):
        """
        Marks attendance for the given name in a daily CSV file.
        Includes arrival status (On Time/Late) and location tagging.
        """
        if name == "Unknown":
            return False
            
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        # Late detection logic
        status = "On Time"
        if time_str > late_threshold:
            status = "Late"
            
        file_path = os.path.join(self.db_folder, f'Attendance_{date_str}.csv')
        file_exists = os.path.isfile(file_path)
        
        already_marked = False
        if file_exists:
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                next(reader, None) # Skip header
                for row in reader:
                    if row and row[0] == name:
                        already_marked = True
                        break
                        
        if not already_marked:
            # Write new entry with Location and Status
            with open(file_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Name', 'Time', 'Date', 'Location', 'Status'])
                writer.writerow([name, time_str, date_str, location, status])
            return True, status
        return False, None
