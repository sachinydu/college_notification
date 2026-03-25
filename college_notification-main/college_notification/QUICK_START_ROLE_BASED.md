# ROLE-BASED SYSTEM - QUICK START GUIDE

## ⚡ 5-Minute Setup

### Step 1: Initialize Database
```bash
cd college_notification
python init_db_only.py
```
**Output**: `[OK] Database initialized with all tables.`

### Step 2: Create Faculty Table
```bash
python migrate_add_faculty_table.py
```
**Output**: `[OK] Faculty table created successfully!`

### Step 3: Setup Default Admin
```bash
python insert_default_users.py
```
**Output**: Shows admin credentials (admin@erp.com / admin123)

### Step 4: Start Application
```bash
python app.py
```
**Output**: Flask server running at `http://localhost:5000`

---

## 🧪 TESTING CHECKLIST

### ✅ Test 1: Admin Login
1. Go to: `http://localhost:5000/login`
2. Select: **Employee**
3. Enter:
   - Email: `admin@erp.com`
   - Password: `admin123`
4. Click: **Login**
5. **Expected**: Redirects to `/admin` (Admin Dashboard)

### ✅ Test 2: Create Faculty
1. From admin dashboard, go to: `/admin/add-faculty`
2. Fill form:
   - Name: `Dr. John Smith`
   - Email: `john@college.edu`
   - Password: `john@123`
   - Subject: `Computer Science`
   - Department: `CSE`
3. Click: **Create Faculty Account**
4. **Expected**: Success message with username: `john`

### ✅ Test 3: Faculty Login
1. Go to: `http://localhost:5000/login`
2. Select: **Employee**
3. Enter:
   - Email: `john@college.edu`
   - Password: `john@123`
4. Click: **Login**
5. **Expected**: Redirects to `/faculty/dashboard`

### ✅ Test 4: Student Registration
1. Go to: `http://localhost:5000/register`
2. Fill form:
   - Name: `Alice Johnson`
   - Roll No: `CS20001`
   - Email: `alice@student.edu`
   - Mobile: `9876543210`
   - Password: `alice@123`
   - Semester: `3`
   - Section: `CSE-A`
   - Photo: (skip for now)
3. Click: **Register**
4. **Expected**: Success message, redirects to login

### ✅ Test 5: Student Login
1. Go to: `http://localhost:5000/login`
2. Select: **Student**
3. Enter identifier (one of):
   - Roll No: `CS20001`
   - Email: `alice@student.edu`
   - Password: `alice@123`
4. Click: **Login**
5. **Expected**: Redirects to `/student/dashboard`

### ✅ Test 6: Role Isolation
1. Try to access `/admin/**` as student
   - **Expected**: Access denied message
2. Try to access `/faculty/**` as student
   - **Expected**: Access denied message
3. Try to access `/admin/**` as faculty
   - **Expected**: Access denied message

### ✅ Test 7: Role Mismatch
1. Go to: `http://localhost:5000/login`
2. Select: **Student**
3. Enter: `admin@erp.com` / `admin123`
4. **Expected**: Error message "role mismatch"

---

## 📊 ROLE MATRIX

| Feature | Student | Faculty | Admin |
|---------|---------|---------|-------|
| Self-Register | ✅ | ❌ | ❌ |
| Created By | User | Admin | Init Script |
| Route | `/register` | `/admin/add-faculty` | `insert_default_users.py` |
| Username | Auto (student_roll) | Auto (email) | admin |
| Password | User Set | Admin Set | admin123 |
| Email | Required | Required | admin@erp.com |
| Subject | N/A | Required | N/A |
| Department | N/A | Required | N/A |

---

## 🔐 LOGIN CREDENTIALS

### Default Admin
```
User Type: Employee
Email: admin@erp.com
Password: admin123
```

### Sample Faculty
```
User Type: Employee
Email: john@college.edu
Password: (as set during creation)
```

### Sample Student
```
User Type: Student
Roll No: CS20001
Password: (as set during registration)
```

---

## 📋 DATABASE VERIFICATION

### Check Users
```bash
python -c "
import sqlite3
conn = sqlite3.connect('college_notification/college.db')
c = conn.cursor()
c.execute('SELECT id, username, email, role FROM users')
for row in c.fetchall():
    print(row)
"
```

### Check Faculty Table
```bash
python -c "
import sqlite3
conn = sqlite3.connect('college_notification/college.db')
c = conn.cursor()
c.execute('SELECT user_id, subject, department FROM faculty')
for row in c.fetchall():
    print(row)
"
```

---

## 🚀 COMMON OPERATIONS

### Add Another Faculty
1. Login as `admin@erp.com`
2. Navigate to `/admin/add-faculty`
3. Fill details
4. Click submit

### Register Another Student
1. Navigate to `/register`
2. Fill unique email and roll number
3. Use strong password
4. Click submit

### Reset Everything
```bash
# Delete database and restart
rm college_notification/college.db
python init_db_only.py
python migrate_add_faculty_table.py
python insert_default_users.py
python app.py
```

---

## ❌ TROUBLESHOOTING

### Issue: `admin@erp.com: access denied`
- Ensure you selected "Employee" not "Student"

### Issue: `Can't find user`
- Verify email/roll number exists
- Check for typos
- Try different identifier (email vs roll number)

### Issue: `Faculty table not found`
- Run: `python migrate_add_faculty_table.py`

### Issue: `Duplicate email error`
- Email already exists in system
- Use different email address

### Issue: `Password too short`
- Minimum password length is 6 characters
- Use: `password123` instead of `pass`

### Issue: `Invalid email format`
- Email must have format: `user@domain.com`
- Check for special characters

### Issue: `Mobile must be 10 digits`
- Enter exactly 10 digits
- Don't include country code

---

## 📱 MOBILE REGISTRATION FORMAT

**Valid**: 9876543210
**Invalid**: 98765 (too short)
**Invalid**: 989876543210 (too long)
**Invalid**: +919876543210 (country code not allowed)

---

## 🎯 NEXT: INTEGRATION TESTING

### Test Course Assignment
1. Login as faculty
2. Assign students to course
3. View course dashboard

### Test Attendance
1. Login as faculty
2. Mark attendance
3. Login as student to verify

### Test Marks
1. Login as faculty
2. Enter marks
3. Login as student to view

---

## 📞 SUPPORT

If you encounter issues:

1. **Check logs**: Look for error messages in terminal
2. **Verify database**: Use SQL queries to check data
3. **Clear session**: Logout and login again
4. **Restart app**: Stop and start Flask server
5. **Reset database**: Delete .db file and reinitialize

---

## ✅ FINAL VERIFICATION

Before deploying to production:

```
✅ Admin can login
✅ Admin can create faculty
✅ Faculty can login
✅ Student can self-register
✅ Student can login
✅ Role-based dashboards work
✅ Role isolation enforced
✅ All validators working
✅ Database migrations complete
✅ No console errors
```

---

**Quick Start Complete!** 🎉
Now proceed with comprehensive testing and production deployment.
