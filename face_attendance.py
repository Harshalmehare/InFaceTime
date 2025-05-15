import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition
import numpy as np
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk

class FaceAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1000x700")
        
        # Database connection
        self.db_connect()
        
        # Face recognition variables
        self.known_face_encodings = []
        self.known_student_ids = []
        self.known_student_names = []
        self.today_attendance = set()
        
        # Video capture
        self.video_capture = None
        self.current_frame = None
        self.is_running = False
        
        # Load known faces
        self.load_known_faces()
        
        # Setup GUI
        self.setup_ui()
        
        # Load initial data
        self.load_attendance_data()
    
    def db_connect(self):
        """Connect to MySQL database with error handling"""
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="harsh@2002",
                database="attendance_system"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", 
                               f"Could not connect to database:\n{err}")
            self.root.destroy()
    
    def load_known_faces(self):
        """Load face encodings and student info from database"""
        try:
            self.cursor.execute("SELECT student_id, name, face_encoding FROM students")
            for student_id, name, encoding_bytes in self.cursor.fetchall():
                encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
                self.known_face_encodings.append(encoding)
                self.known_student_ids.append(student_id)
                self.known_student_names.append(name)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", 
                               f"Error loading face data:\n{err}")
    
    def setup_ui(self):
        """Create the user interface"""
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header frame
        header_frame = tk.Frame(main_frame, bg="#4a6baf")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        tk.Label(header_frame, text="Face Recognition Attendance System", 
                font=("Arial", 16, "bold"), bg="#4a6baf", fg="white"
                ).pack(pady=10)
        
        # Video and controls frame
        video_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.GROOVE)
        video_frame.grid(row=1, column=0, sticky="nsew")
        video_frame.grid_rowconfigure(0, weight=1)
        video_frame.grid_columnconfigure(0, weight=1)
        
        # Video display
        self.video_label = tk.Label(video_frame, bg="black")
        self.video_label.grid(row=0, column=0, sticky="nsew")
        
        # Control buttons
        control_frame = tk.Frame(video_frame, bg="white")
        control_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.start_btn = tk.Button(control_frame, text="Start Attendance", 
                                 command=self.start_attendance, width=15,
                                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Attendance", 
                                command=self.stop_attendance, width  = 15,
                                bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                                state=tk.DISABLED)
        self.stop_btn.pack(side="left", padx=5)
        
        # Attendance log
        log_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.GROOVE)
        log_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        tk.Label(log_frame, text="Attendance Log", font=("Arial", 12, "bold"), 
                bg="white").pack(pady=5)
        
        # Treeview for attendance records
        self.tree = ttk.Treeview(log_frame, columns=("ID", "Name", "Date", "Time"), 
                                show="headings", height=8)
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Name", width=150, anchor="w")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Time", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("System Ready")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                            bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                            bg="light gray", font=("Arial", 10))
        status_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    
    def load_attendance_data(self, date=None):
        """Load attendance records for the specified date (default: today)"""
        if not date:
            date = datetime.now().date()
        
        try:
            # Clear current data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get attendance records
            self.cursor.execute("""
                SELECT a.student_id, s.name, a.date, a.time 
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE a.date = %s
                ORDER BY a.time DESC
            """, (date,))
            
            # Add to treeview
            for row in self.cursor.fetchall():
                self.tree.insert("", "end", values=row)
                
            # Update status
            self.status_var.set(f"Showing attendance for {date}")
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", 
                               f"Error loading attendance data:\n{err}")
    
    def start_attendance(self):
        """Start the attendance system"""
        if not self.known_face_encodings:
            messagebox.showerror("Error", "No face data loaded. Register students first.")
            return
            
        # Initialize video capture
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            messagebox.showerror("Error", "Could not open video device")
            return
        
        # Get today's attendance to prevent duplicates
        today = datetime.now().date()
        try:
            self.cursor.execute(
                "SELECT student_id FROM attendance WHERE date = %s",
                (today,)
            )
            self.today_attendance = {row[0] for row in self.cursor.fetchall()}
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", 
                               f"Error loading today's attendance:\n{err}")
            return
        
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Attendance system running - Detecting faces...")
        
        # Start processing frames
        self.is_running = True
        self.process_frame()
    
    def stop_attendance(self):
        """Stop the attendance system"""
        self.is_running = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        # Clear video display
        self.video_label.config(image='')
        
        # Update UI
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Attendance system stopped")
        
        # Refresh attendance data
        self.load_attendance_data()
    
    def process_frame(self):
        """Process each video frame for face recognition"""
        if not self.is_running or not self.video_capture:
            return
            
        # Capture frame
        ret, frame = self.video_capture.read()
        if not ret:
            self.status_var.set("Error reading frame from camera")
            return
        
        # Convert to RGB and resize for faster processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        
        # Find all faces in the frame
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        
        # Process each face
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, 
                face_encoding,
                tolerance=0.6  # Adjust for strictness
            )
            
            # Get the best match
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                face_encoding
            )
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                student_id = self.known_student_ids[best_match_index]
                name = self.known_student_names[best_match_index]
                
                # Scale up face locations
                top *= 4; right *= 4; bottom *= 4; left *= 4
                
                # Draw rectangle and label
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, f"{name} ({student_id})", 
                           (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                           (255, 255, 255), 1)
                
                # Mark attendance if not already marked today
                if student_id not in self.today_attendance:
                    self.mark_attendance(student_id, name)
                    self.today_attendance.add(student_id)
        
        # Convert to PhotoImage and display
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)
        
        # Schedule next frame processing
        self.video_label.after(10, self.process_frame)
    
    def mark_attendance(self, student_id, name):
        """Record attendance in the database"""
        try:
            now = datetime.now()
            self.cursor.execute(
                "INSERT INTO attendance (student_id, date, time) VALUES (%s, %s, %s)",
                (student_id, now.date(), now.time())
            )
            self.db.commit()
            self.status_var.set(f"Attendance marked for {name} ({student_id}) at {now.time()}")
        except mysql.connector.Error as err:
            self.status_var.set(f"Error marking attendance: {err}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceAttendanceSystem(root)
    root.mainloop()