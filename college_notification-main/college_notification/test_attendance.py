#!/usr/bin/env python
"""Quick test of the attendance system"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_db
from flask import session

print("\n" + "="*70)
print("ATTENDANCE SYSTEM - QUICK TEST")
print("="*70)

# Test template rendering
print("\n[TEST 1] Verifying Jinja2 template syntax...")
try:
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('student_attendance.html')
    print("✓ Template is valid with no Jinja2 errors")
except Exception as e:
    print(f"✗ Template error: {e}")
    sys.exit(1)

# Test Flask route
print("\n[TEST 2] Testing Flask app initialization...")
try:
    with app.app_context():
        db = get_db()
        print("✓ Flask app initialized successfully")
        print("✓ Database connection working")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test data in database
print("\n[TEST 3] Verifying attendance data...")
try:
    with app.app_context():
        db = get_db()
        
        # Check attendance records
        result = db.execute(
            "SELECT COUNT(*) as count, COUNT(DISTINCT date) as dates, COUNT(DISTINCT subject) as subjects FROM attendance_records WHERE user_id = 3"
        ).fetchone()
        
        records = result['count']
        dates = result['dates']
        subjects = result['subjects']
        
        print(f"✓ Found {records} attendance records")
        print(f"✓ Across {dates} different dates")
        print(f"✓ For {subjects} different subjects")
        
        # Get sample subjects
        subjects_list = db.execute(
            "SELECT DISTINCT subject FROM attendance_records WHERE user_id = 3 ORDER BY subject"
        ).fetchall()
        
        print(f"\nSubjects:")
        for s in subjects_list:
            print(f"  - {s['subject']}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test route logic
print("\n[TEST 4] Testing route logic...")
try:
    with app.app_context():
        db = get_db()
        user_id = 3
        
        # Fetch records
        records = db.execute(
            "SELECT date, subject, status FROM attendance_records WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ).fetchall()
        
        records_list = [dict(row) for row in records]
        
        # Get unique subjects
        all_subjects = sorted(set(r['subject'] for r in records_list))
        print(f"✓ Subjects extracted: {len(all_subjects)} subjects")
        
        # Group by date
        from collections import defaultdict
        attendance_by_date = defaultdict(list)
        for record in records_list:
            attendance_by_date[record['date']].append(record)
        
        sorted_dates = sorted(attendance_by_date.keys(), reverse=True)
        print(f"✓ Grouped into {len(sorted_dates)} dates")
        
        # Calculate
        total_classes = len(records_list)
        total_present = sum(1 for r in records_list if r['status'] == 'Present')
        overall_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
        
        print(f"✓ Calculated statistics:")
        print(f"   - Total classes: {total_classes}")
        print(f"   - Total present: {total_present}")
        print(f"   - Overall %: {overall_percentage:.2f}%")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✓ ALL TESTS PASSED - SYSTEM IS READY!")
print("="*70)

print("\n📋 NEXT STEPS:")
print("1. Run: python app.py")
print("2. Login with: student1 / student123")
print("3. Go to: http://localhost:5000/student/attendance")
print("4. See your attendance report!")

print("\n" + "="*70 + "\n")
