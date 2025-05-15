import mysql.connector

def create_database():
    try:
        # Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="harsh@2002"
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system")
        print("Database 'attendance_system' created successfully")
        
        # Switch to the database
        cursor.execute("USE attendance_system")
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20) UNIQUE,
                name VARCHAR(100),
                department VARCHAR(50),
                email VARCHAR(100),
                face_encoding LONGBLOB
            )
        """)
        
        # Create attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20),
                date DATE,
                time TIME,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)
        
        print("Tables created successfully")
        connection.commit()
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database()