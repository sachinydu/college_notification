#!/usr/bin/env python3
"""
Script to insert default admin and faculty users into the database
Run this once to set up initial admin and faculty accounts
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB = os.path.join(os.path.dirname(__file__), 'college.db')

def insert_default_users():
    """Insert default admin and faculty users"""
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("INSERTING DEFAULT ADMIN AND FACULTY USERS")
        print("=" * 70)
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("[ERROR] Users table does not exist. Run init_db_only.py first!")
            return False
        
        # Check if users already exist
        cursor.execute("SELECT COUNT(*) FROM users WHERE email IN (?, ?)", 
                      ('admin@college.edu', 'faculty1@college.edu'))
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print("[INFO] Admin and/or faculty users already exist. Skipping creation.")
            cursor.execute("SELECT id, username, email, role, full_name FROM users WHERE email IN (?, ?)",
                          ('admin@college.edu', 'faculty1@college.edu'))
            for row in cursor.fetchall():
                print(f"   - {row[2]} ({row[1]}) - Role: {row[3]}")
            return True
        
        # Default users to insert
        users = [
            {
                'username': 'admin',
                'email': 'admin@college.edu',
                'password_plain': 'admin123',
                'role': 'admin',
                'full_name': 'System Administrator',
                'mobile': '9000000001',
                'section': 'Admin'
            },
            {
                'username': 'faculty1',
                'email': 'faculty1@college.edu',
                'password_plain': 'faculty123',
                'role': 'faculty',
                'full_name': 'Dr. John Smith',
                'mobile': '9000000002',
                'section': 'CSE-A'
            }
        ]
        
        # Insert each user
        for user in users:
            hashed_password = generate_password_hash(user['password_plain'])
            
            # Check if columns exist (migration may not have been run)
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, email, role, full_name, mobile, section)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user['username'], hashed_password, user['email'], user['role'], 
                      user['full_name'], user['mobile'], user['section']))
            except Exception as e:
                # If migration columns don't exist, try without them
                if 'no such column' in str(e).lower():
                    print(f"[WARN] Migration columns not found. Inserting basic user record...")
                    cursor.execute("""
                        INSERT INTO users (username, password, email, role)
                        VALUES (?, ?, ?, ?)
                    """, (user['username'], hashed_password, user['email'], user['role']))
                else:
                    raise
            
            print(f"[OK] Inserted user: {user['email']}")
            print(f"     - Username: {user['username']}")
            print(f"     - Password: {user['password_plain']}")
            print(f"     - Role: {user['role']}")
            print(f"     - Full Name: {user['full_name']}")
        
        conn.commit()
        
        # Verify insertion
        print("\n[*] Verifying inserted users:")
        cursor.execute("SELECT id, username, email, role, full_name FROM users WHERE role IN (?, ?)",
                      ('admin', 'faculty'))
        rows = cursor.fetchall()
        for row in rows:
            print(f"   ✓ ID: {row[0]}, Email: {row[2]}, Role: {row[3]}")
        
        print("\n" + "=" * 70)
        print("DEFAULT USERS CREATED SUCCESSFULLY!")
        print("=" * 70)
        print("\nYou can now login with:")
        print("  Admin:   admin@college.edu / admin123")
        print("  Faculty: faculty1@college.edu / faculty123")
        print("\n" + "=" * 70)
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == '__main__':
    insert_default_users()
