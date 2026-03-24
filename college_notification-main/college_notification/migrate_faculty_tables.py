#!/usr/bin/env python3
"""
Migration script to add Faculty Management System tables
Creates: subjects, faculty_attendance, faculty_marks
"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), 'college.db')

def migrate():
    """Create Faculty Management System tables"""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("ADDING FACULTY MANAGEMENT SYSTEM TABLES")
        print("=" * 60)
        
        # 1. SUBJECTS TABLE - Faculty manages their own subjects
        print("\n1. Creating 'subjects' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL,
                subject_code TEXT UNIQUE NOT NULL,
                description TEXT,
                semester INTEGER DEFAULT 1,
                credits INTEGER DEFAULT 4,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (faculty_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(faculty_id, subject_code)
            )
        """)
        print("   ✓ Subjects table created successfully!")
        
        # 2. FACULTY ATTENDANCE TABLE - Faculty marks attendance
        print("\n2. Creating 'faculty_attendance' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT CHECK(status IN ('Present', 'Absent', 'Leave')) DEFAULT 'Absent',
                remarks TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (faculty_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                UNIQUE(faculty_id, student_id, subject_id, attendance_date)
            )
        """)
        print("   ✓ Faculty attendance table created successfully!")
        
        # 3. FACULTY MARKS TABLE - Faculty enters marks
        print("\n3. Creating 'faculty_marks' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty_marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                exam_type TEXT DEFAULT 'Sessional',  -- Sessional/Assignment/Quiz/Final
                max_marks REAL DEFAULT 100,
                obtained_marks REAL DEFAULT 0,
                remarks TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (faculty_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                UNIQUE(faculty_id, student_id, subject_id, exam_type)
            )
        """)
        print("   ✓ Faculty marks table created successfully!")
        
        conn.commit()
        
        # Verify tables were created
        print("\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('subjects', 'faculty_attendance', 'faculty_marks')")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   ✓ Table '{table[0]}' exists")
        
        # Check schema
        print("\nSubjects table schema:")
        cursor.execute("PRAGMA table_info(subjects)")
        for col in cursor.fetchall():
            print(f"   - {col[1]}: {col[2]}")
        
        print("\nFaculty Attendance table schema:")
        cursor.execute("PRAGMA table_info(faculty_attendance)")
        for col in cursor.fetchall():
            print(f"   - {col[1]}: {col[2]}")
        
        print("\nFaculty Marks table schema:")
        cursor.execute("PRAGMA table_info(faculty_marks)")
        for col in cursor.fetchall():
            print(f"   - {col[1]}: {col[2]}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    migrate()
