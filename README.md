Face Recognition Attendance System
A Python project that uses facial recognition to record student attendance. It includes tools for managing student data, capturing face images, recording attendance through webcam, and exporting attendance reports.

Requirements
Install the necessary Python packages:

bash
Copy
Edit
pip install opencv-python face_recognition numpy mysql-connector-python openpyxl Pillow
Setup Instructions
Step 1: Set Up the Database
Run the following command to create the attendance_system MySQL database and required tables:

bash
Copy
Edit
python database_setup.py
This will create two tables:

students

attendance

Step 2: Add Student Data and Capture Faces
Start the student management system to add new students and capture face samples:

bash
Copy
Edit
python student_management.py
Enter student details (ID, name, department, email).

Click "Capture Face" to collect 5 face samples from the webcam.

Step 3: Start Attendance System
Launch the real-time face recognition attendance system:

bash
Copy
Edit
python face_attendance.py
Click "Start Attendance" to begin detection via webcam.

Detected students will be automatically logged.

Click "Stop Attendance" to stop the session.

Step 4: View and Export Attendance
To filter and export attendance records:

bash
Copy
Edit
python attendance_filter.py
You can search by name, department, or date.

Click "Download Excel" to export results as an Excel file.

Features
Real-time facial recognition attendance

Student management and face image capture

Excel export of attendance reports

Search attendance by name, department, or date

Technologies Used
Python (Tkinter, OpenCV, face_recognition)

MySQL for data storage

openpyxl for Excel export

Pillow for image handling
