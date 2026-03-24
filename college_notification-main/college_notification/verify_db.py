#!/usr/bin/env python
"""Test script to verify the attendance system"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'college.db')

print("=" * 60)
print("ATTENDANCE SYSTEM VERIFICATION")
print("=" * 60)

if os.path.exists(db_path):
    print(f"\n[✓] Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n[✓] Tables in database ({len(tables)}):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   ✓ {table:25} ({count} records)")
    
    # Check attendance_records specifically
    if 'attendance_records' in tables:
        cursor.execute("SELECT COUNT(*) FROM attendance_records")
        count = cursor.fetchone()[0]
        print(f"\n[✓] attendance_records table has {count} records")
        
        if count > 0:
            cursor.execute("SELECT DISTINCT user_id FROM attendance_records LIMIT 1")
            user = cursor.fetchone()
            if user:
                print(f"[✓] Sample data for user_id: {user[0]}")
    
    conn.close()
    print("\n[✓] Database verification complete!")
else:
    print(f"\n[✗] Database not found at {db_path}")

print("\n" + "=" * 60)
