import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageTk  # For image display

class StudentManagementApp:
    def __init__(self, root):
        """
        Initialize the main application window and database connection
        """
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1000x600")
        
        # Database connection setup
        self.db_connection()
        
        # Create directory for storing face images
        self.dataset_path = os.path.join(os.path.dirname(__file__), "face_dataset")
        os.makedirs(self.dataset_path, exist_ok=True)
        
        # Setup the user interface
        self.setup_ui()
        
        # Load existing students into the interface
        self.load_students()
    
    def db_connection(self):
        """
        Establish connection to MySQL database with error handling
        """
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",      # Change to your MySQL username
                password="harsh@2002",      # Change to your MySQL password
                database="attendance_system"
            )
            self.cursor = self.db.cursor()
        except mysql.connector.Error as err:
            # Handle specific database errors
            if err.errno == 1049:  # Database doesn't exist
                messagebox.showerror("Database Error", 
                    "The 'attendance_system' database doesn't exist.\n"
                    "Please run the database setup script first.")
            elif err.errno == 1045:  # Access denied
                messagebox.showerror("Access Denied",
                    "Incorrect username/password.\n"
                    "Default credentials: user='root', password=''")
            else:
                messagebox.showerror("Database Error", f"Error {err.errno}: {err.msg}")
            self.root.destroy()
    
    def setup_ui(self):
        """
        Create and arrange all UI components
        """
        # Input Frame for student details
        input_frame = tk.LabelFrame(self.root, text="Student Information", padx=10, pady=10)
        input_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # Student ID
        tk.Label(input_frame, text="Student ID:").grid(row=0, column=0, sticky="e", pady=5)
        self.student_id_entry = tk.Entry(input_frame, width=25)
        self.student_id_entry.grid(row=0, column=1, pady=5)
        
        # Full Name
        tk.Label(input_frame, text="Full Name:").grid(row=1, column=0, sticky="e", pady=5)
        self.name_entry = tk.Entry(input_frame, width=25)
        self.name_entry.grid(row=1, column=1, pady=5)
        
        # Department
        tk.Label(input_frame, text="Department:").grid(row=2, column=0, sticky="e", pady=5)
        self.department_entry = tk.Entry(input_frame, width=25)
        self.department_entry.grid(row=2, column=1, pady=5)
        
        # Email
        tk.Label(input_frame, text="Email:").grid(row=3, column=0, sticky="e", pady=5)
        self.email_entry = tk.Entry(input_frame, width=25)
        self.email_entry.grid(row=3, column=1, pady=5)
        
        # Control Buttons
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Button(button_frame, text="Add", width=10, command=self.add_student).pack(side="left", padx=5)
        tk.Button(button_frame, text="Update", width=10, command=self.update_student).pack(side="left", padx=5)
        tk.Button(button_frame, text="Delete", width=10, command=self.delete_student).pack(side="left", padx=5)
        tk.Button(button_frame, text="Clear", width=10, command=self.clear_form).pack(side="left", padx=5)
        
        # Face Capture Button
        tk.Button(input_frame, text="Capture Face", width=20, 
                 command=self.capture_face, bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=2, pady=10)
        
        # Student List (Treeview)
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Student ID", "Name", "Department", "Email"), 
                                show="headings", selectmode="browse")
        
        # Configure columns
        columns = [
            ("ID", 50, "center"),
            ("Student ID", 100, "center"),
            ("Name", 200, "w"),
            ("Department", 150, "w"),
            ("Email", 200, "w")
        ]
        
        for col, width, anchor in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_student)
    
    def load_students(self):
        """Load all students from database into the treeview"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch students from database
            self.cursor.execute("SELECT id, student_id, name, department, email FROM students")
            
            # Insert into treeview
            for row in self.cursor.fetchall():
                self.tree.insert("", "end", values=row)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to load students:\n{err}")
    
    def load_selected_student(self, event):
        """Load selected student's data into the form fields"""
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.clear_form()
            
            # Populate form fields
            entries = [
                self.student_id_entry,
                self.name_entry,
                self.department_entry,
                self.email_entry
            ]
            
            for entry, value in zip(entries, values[1:]):  # Skip ID
                entry.insert(0, value)
    
    def add_student(self):
        """Add a new student to the database"""
        # Get form data
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        department = self.department_entry.get().strip()
        email = self.email_entry.get().strip()
        
        # Validate required fields
        if not student_id or not name:
            messagebox.showerror("Error", "Student ID and Name are required!")
            return
        
        try:
            # Insert into database
            self.cursor.execute(
                "INSERT INTO students (student_id, name, department, email) VALUES (%s, %s, %s, %s)",
                (student_id, name, department, email)
            )
            self.db.commit()
            
            messagebox.showinfo("Success", "Student added successfully!")
            self.load_students()
            self.clear_form()
            
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add student:\n{err}")
    
    def update_student(self):
        """Update selected student's information"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a student first!")
            return
            
        # Get form data
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        department = self.department_entry.get().strip()
        email = self.email_entry.get().strip()
        
        # Validate required fields
        if not student_id or not name:
            messagebox.showerror("Error", "Student ID and Name are required!")
            return
            
        try:
            # Update database record
            self.cursor.execute(
                """UPDATE students 
                SET student_id=%s, name=%s, department=%s, email=%s 
                WHERE id=%s""",
                (student_id, name, department, email, self.tree.item(selected, "values")[0])
            )
            self.db.commit()
            
            messagebox.showinfo("Success", "Student updated successfully!")
            self.load_students()
            
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update student:\n{err}")
    
    def delete_student(self):
        """Delete selected student from database"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a student first!")
            return
            
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            return
            
        try:
            # Get student ID before deletion for cleanup
            student_id = self.tree.item(selected, "values")[1]
            
            # Delete from database
            self.cursor.execute("DELETE FROM students WHERE id=%s", 
                               (self.tree.item(selected, "values")[0],))
            self.db.commit()
            
            # Delete face images
            self.delete_face_images(student_id)
            
            messagebox.showinfo("Success", "Student deleted successfully!")
            self.load_students()
            self.clear_form()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete student:\n{err}")
    
    def delete_face_images(self, student_id):
        """Delete all face images for a student"""
        try:
            for filename in os.listdir(self.dataset_path):
                if filename.startswith(f"{student_id}_"):
                    os.remove(os.path.join(self.dataset_path, filename))
        except Exception as e:
            print(f"Error deleting face images: {e}")
    
    def capture_face(self):
        """Capture and store face images and encoding for selected student"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a student first!")
            return
            
        student_id = self.tree.item(selected, "values")[1]
        sample_count = 0
        face_encodings = []
        
        # Initialize video capture
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open video device")
            return
        
        # Create window for video feed
        cv2.namedWindow("Face Capture", cv2.WINDOW_NORMAL)
        
        try:
            while sample_count < 5:  # Capture 5 samples
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to RGB for face recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if face_locations:
                    # Get face encodings
                    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                    face_encodings.append(face_encoding)
                    
                    # Save face image
                    sample_count += 1
                    img_path = os.path.join(self.dataset_path, f"{student_id}_{sample_count}.jpg")
                    cv2.imwrite(img_path, frame)
                    
                    # Draw rectangle around face
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"Sample {sample_count}/5", (left, top-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Display the frame
                cv2.imshow("Face Capture", frame)
                
                # Break on ESC key or when we have enough samples
                if cv2.waitKey(1) == 27 or sample_count >= 5:
                    break
            
            if face_encodings:
                # Calculate average encoding for better accuracy
                avg_encoding = np.mean(face_encodings, axis=0)
                
                # Store in database
                try:
                    self.cursor.execute(
                        "UPDATE students SET face_encoding=%s WHERE student_id=%s",
                        (avg_encoding.tobytes(), student_id)
                    )
                    self.db.commit()
                    messagebox.showinfo("Success", f"Captured {sample_count} face samples!")
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Failed to save face encoding:\n{err}")
        
        finally:
            # Release resources
            cap.release()
            cv2.destroyAllWindows()
    
    def clear_form(self):
        """Clear all input fields"""
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.department_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()