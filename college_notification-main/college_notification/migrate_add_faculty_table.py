#!/usr/bin/env python3
"""
Migration Script: Add Faculty Table
Creates a dedicated faculty table to store faculty-specific information
including subject and department assignments
"""

import sqlite3
import os
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), 'college.db')

def migrate_add_faculty_table():
    """Create faculty table with subject and department fields"""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("MIGRATION: Adding Faculty Table")
        print("=" * 70)
        
        # Check if faculty table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='faculty'")
        if cursor.fetchone():
            print("[INFO] Faculty table already exists. Skipping creation.")
            # Display existing faculty records
            cursor.execute("SELECT id, user_id, subject, department FROM faculty")
            rows = cursor.fetchall()
            if rows:
                print(f"\n[*] Existing {len(rows)} faculty records:")
                for row in rows:
                    print(f"   - ID: {row[0]}, User ID: {row[1]}, Subject: {row[2]}, Department: {row[3]}")
            return True
        
        print("[*] Creating faculty table...")
        
        # Create faculty table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                subject TEXT,
                department TEXT,
                qualification TEXT,
                experience_years INTEGER DEFAULT 0,
                specialization TEXT,
                office_hours TEXT,
                created_at TEXT DEFAULT (datetime('now','localtime')),
                updated_at TEXT DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("[OK] Faculty table created successfully!")
        
        # Check for existing faculty users and add them to the faculty table if not present
        cursor.execute("SELECT id, username, email FROM users WHERE role = 'faculty'")
        faculty_users = cursor.fetchall()
        
        if faculty_users:
            print(f"\n[*] Found {len(faculty_users)} existing faculty users. Adding to faculty table...")
            
            for user_id, username, email in faculty_users:
                # Check if already in faculty table
                cursor.execute("SELECT id FROM faculty WHERE user_id = ?", (user_id,))
                if not cursor.fetchone():
                    # Add basic faculty record
                    cursor.execute("""
                        INSERT INTO faculty (user_id, subject, department, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, 'Unknown', 'Unknown', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    print(f"   ✓ Added {username} ({email}) to faculty table")
            
            conn.commit()
            print("[OK] Existing faculty users added to faculty table!")
        
        print("\n[*] Migration Summary:")
        cursor.execute("SELECT COUNT(*) FROM faculty")
        count = cursor.fetchone()[0]
        print(f"   - Total faculty records: {count}")
        
        print("[OK] Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = migrate_add_faculty_table()
    if not success:
        exit(1)
