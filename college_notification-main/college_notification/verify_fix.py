#!/usr/bin/env python3
"""
Verification script to test the database schema and queries
"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), 'college.db')

def verify_schema():
    """Verify the database schema is correct"""
    try:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=" * 60)
        print("DATABASE SCHEMA VERIFICATION")
        print("=" * 60)
        
        # Check students table structure
        print("\n1. Students Table Schema:")
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   ✓ {col['name']}: {col['type']}")
        
        # Check if section column exists
        column_names = [col['name'] for col in columns]
        if 'section' in column_names:
            print("\n   ✅ 'section' column exists!")
        else:
            print("\n   ❌ 'section' column MISSING!")
            return False
        
        # Test the problematic query
        print("\n2. Testing Student Info Query:")
        print("   Query: SELECT s.full_name, s.roll_no, s.section, s.semester, s.created_at FROM students s")
        
        cursor.execute("""
            SELECT s.full_name, s.roll_no, s.section, s.semester, s.created_at
            FROM students s
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            print("   ✅ Query executed successfully!")
            print(f"   Sample data: {dict(result)}")
        else:
            print("   ℹ️  No student records found (this is OK if database is empty)")
        
        # Check attendance_records table
        print("\n3. Attendance Records Table:")
        cursor.execute("SELECT COUNT(*) as count FROM attendance_records")
        count = cursor.fetchone()['count']
        print(f"   ✓ Total records: {count}")
        
        # Check users table
        print("\n4. Users Table:")
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']
        print(f"   ✓ Total users: {users_count}")
        
        # Check the complete student attendance query (the one from app.py)
        if users_count > 0:
            print("\n5. Testing Student Attendance Route Query:")
            cursor.execute("""
                SELECT u.id, u.username, u.role
                FROM users u
                WHERE u.role = 'student'
                LIMIT 1
            """)
            student_user = cursor.fetchone()
            
            if student_user:
                user_id = student_user['id']
                print(f"   Using user_id: {user_id} ({student_user['username']})")
                
                cursor.execute("""
                    SELECT s.full_name, s.roll_no, s.section, s.semester, s.created_at
                    FROM students s
                    JOIN users u ON s.user_id = u.id
                    WHERE u.id = ?
                """, (user_id,))
                
                student = cursor.fetchone()
                if student:
                    print("   ✅ Student attendance query works!")
                    print(f"   Student: {dict(student)}")
                else:
                    print("   ℹ️  No student profile found for this user (OK if student profile not created)")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ ALL VERIFICATIONS PASSED!")
        print("=" * 60)
        return True
        
    except sqlite3.OperationalError as e:
        print(f"\n❌ SQLite Error: {e}")
        print("The database may be corrupted or incompletely initialized.")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    verify_schema()
