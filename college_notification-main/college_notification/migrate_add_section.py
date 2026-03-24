#!/usr/bin/env python3
"""
Migration script to add missing 'section' column to students table
This script runs safely - it checks if the column exists before adding it
"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), 'college.db')

def migrate():
    """Add section column to students table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        # Check if section column already exists
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'section' not in columns:
            print("✓ Adding 'section' column to students table...")
            cursor.execute("""
                ALTER TABLE students
                ADD COLUMN section TEXT DEFAULT 'A'
            """)
            conn.commit()
            print("✓ Column 'section' added successfully!")
        else:
            print("✓ 'section' column already exists in students table")
        
        # Verify the column exists now
        cursor.execute("PRAGMA table_info(students)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"\nStudents table columns: {columns}")
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    migrate()
