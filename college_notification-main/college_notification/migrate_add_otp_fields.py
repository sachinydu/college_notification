#!/usr/bin/env python3
"""
Migration: Add OTP Fields for Forgot Password System

This script adds the following fields to the users table:
- otp (temporary 6-digit OTP)
- otp_expiry (timestamp when OTP expires)

These fields are required for the secure password reset system.
"""

import sqlite3
import os
import sys
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'college.db')

def check_column_exists(db, table, column):
    """Check if a column exists in a table"""
    try:
        cursor = db.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        return column in columns
    except Exception as e:
        print(f"[ERROR] Error checking column: {e}")
        return False

def migrate():
    """Execute the migration"""
    try:
        if not os.path.exists(DB_PATH):
            print(f"[ERROR] Database not found at {DB_PATH}")
            return False
        
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        
        print(f"[*] Connected to database: {DB_PATH}")
        print(f"[*] Starting migration...")
        
        # List of columns to add for OTP system
        migrations = [
            ("otp", "TEXT DEFAULT NULL"),
            ("otp_expiry", "TEXT DEFAULT NULL")
        ]
        
        # Check and add each column if it doesn't exist
        added_columns = []
        for column_name, column_def in migrations:
            if not check_column_exists(db, 'users', column_name):
                try:
                    db.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                    added_columns.append(column_name)
                    print(f"[OK] Added column: {column_name}")
                except Exception as e:
                    print(f"[ERROR] Failed to add column {column_name}: {e}")
                    db.rollback()
                    return False
            else:
                print(f"[SKIP] Column already exists: {column_name}")
        
        # Commit changes
        db.commit()
        
        if added_columns:
            print(f"\n[OK] Successfully added {len(added_columns)} columns:")
            for col in added_columns:
                print(f"    - {col}")
        else:
            print(f"[INFO] All columns already exist - no changes needed")
        
        # Verify the new schema
        print(f"\n[*] Verifying schema (users table columns):")
        cursor = db.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for row in columns:
            col_id, col_name, col_type, not_null, default, pk = row
            print(f"    {col_id}: {col_name} ({col_type})")
        
        # Close database
        db.close()
        
        print(f"\n[SUCCESS] Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if migrate():
        sys.exit(0)
    else:
        sys.exit(1)
