#!/usr/bin/env python3
"""
Test script to verify login functionality
"""

import sys
import os
sys.path.append('.')

from app import app, get_db
from werkzeug.security import check_password_hash

def test_login():
    """Test login functionality with demo users"""
    with app.app_context():
        db = get_db()

        print("=" * 60)
        print("TESTING LOGIN FUNCTIONALITY")
        print("=" * 60)

        # Test cases
        test_cases = [
            {
                'identifier': 'admin',
                'password': 'admin123',
                'user_type': 'employee',
                'expected_role': 'admin'
            },
            {
                'identifier': 'faculty1',
                'password': 'faculty123',
                'user_type': 'employee',
                'expected_role': 'faculty'
            },
            {
                'identifier': 'student1',
                'password': 'student123',
                'user_type': 'student',
                'expected_role': 'student'
            },
            {
                'identifier': 'admin@college.edu',
                'password': 'admin123',
                'user_type': 'employee',
                'expected_role': 'admin'
            },
            {
                'identifier': '9000000001',
                'password': 'admin123',
                'user_type': 'employee',
                'expected_role': 'admin'
            },
            {
                'identifier': 'CS2024001',  # roll number
                'password': 'student123',
                'user_type': 'student',
                'expected_role': 'student'
            }
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test['identifier']} ({test['user_type']}) ---")

            # Query user by various identifiers (same logic as login function)
            user = db.execute(
                "SELECT u.*, s.roll_no, s.phone as mobile FROM users u "
                "LEFT JOIN students s ON u.id = s.user_id "
                "WHERE u.username = ? OR u.email = ? OR u.mobile = ?",
                (test['identifier'], test['identifier'], test['identifier'])
            ).fetchone()

            # If not found, try student-specific identifiers
            if not user:
                user = db.execute(
                    "SELECT u.*, s.roll_no, s.phone as mobile FROM users u "
                    "INNER JOIN students s ON u.id = s.user_id "
                    "WHERE s.roll_no = ? OR s.phone = ?",
                    (test['identifier'], test['identifier'])
                ).fetchone()

            if user:
                print(f"✓ User found: {user['username']} (ID: {user['id']}, Role: {user['role']})")
                password_match = check_password_hash(user['password'], test['password'])
                print(f"✓ Password match: {password_match}")

                if password_match:
                    # Check role based on user_type selection
                    allowed_roles = []
                    if test['user_type'] == 'employee':
                        allowed_roles = ['admin', 'faculty']
                    elif test['user_type'] == 'student':
                        allowed_roles = ['student']

                    if user['role'] in allowed_roles:
                        print(f"✓ Role check passed: {user['role']} in {allowed_roles}")
                        print(f"✓ LOGIN SUCCESSFUL for {test['identifier']}")
                    else:
                        print(f"✗ Role mismatch: {user['role']} not in {allowed_roles}")
                else:
                    print(f"✗ Password incorrect")
            else:
                print(f"✗ User not found with identifier: {test['identifier']}")

        print("\n" + "=" * 60)
        print("LOGIN TESTING COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    test_login()