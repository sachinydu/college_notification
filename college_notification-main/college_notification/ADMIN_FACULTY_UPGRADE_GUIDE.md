# Flask ERP Admin & Faculty Authentication Upgrade - Quick Start Guide

## ✅ Upgrade Complete!

Your Flask ERP project has been successfully upgraded to support **Admin**, **Faculty**, and **Student** roles with unified login and role-based authentication.

---

## 🚀 Quick Start Setup (5 minutes)

### Step 1: Run Database Migrations
```bash
cd college_notification/
python migrate_add_registration_fields.py
```

This adds necessary columns to the users table:
- `full_name`, `mobile`, `section`, `semester`, `roll_no`, `photo`

### Step 2: Start the Application
```bash
python app.py
```

### Step 3: Access the Application
- Navigate to: `http://localhost:5000`
- You'll be redirected to login page

---

## 📋 How to Use

### Option A: Create Admin User (for Testing)

You need to manually insert an admin user into the database:

```sql
INSERT INTO users (username, password, email, role, full_name, mobile, section) 
VALUES (
    'admin',
    'pbkdf2:sha256:260000$xxxxx$xxxxx',  -- Use password hasher
    'admin@college.edu',
    'admin',
    'System Administrator',
    '9000000000',
    'Admin'
);
```

**Or use Python to create admin user:**
```python
from werkzeug.security import generate_password_hash
import sqlite3

db = sqlite3.connect('college.db')
hashed = generate_password_hash('admin123')
db.execute(
    "INSERT INTO users (username, password, email, role, full_name, mobile, section) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ('admin', hashed, 'admin@college.edu', 'admin', 'Administrator', '9000000000', 'Admin')
)
db.commit()
```

### Option B: Create Faculty Users (via Admin Dashboard)

1. Login with **Admin** account
2. Navigate to **Faculty** (in sidebar)
3. Click **Add New Faculty**
4. Fill in form:
   - Username: `faculty1`
   - Email: `faculty1@college.edu`
   - Full Name: `Dr. John Smith`
   - Section: `CSE-A`
   - Mobile: `9999999999`
   - Password: `faculty123`
5. Click **Add Faculty** → Faculty account created instantly

### Option C: Create Student Users (Standard Registration)

1. Click **Register** on login page
2. Fill student registration form with:
   - Full Name, Roll Number, Email, Mobile
   - Semester, Section
   - Password
3. Submit → Student account created

---

## 🔐 Login Examples

### Admin Login
```
Email: admin@college.edu
Password: admin123
↓
Redirects to → Admin Dashboard (/admin)
```

### Faculty Login
```
Email: faculty1@college.edu
Password: faculty123
↓
Redirects to → Faculty Dashboard (/faculty/dashboard)
Can view students in their section
```

### Student Login
```
Roll Number: CSE001
Email: student@college.edu
Password: student123
↓
Redirects to → Student Dashboard (/student-dashboard)
Can view grades, attendance, notices
```

---

## 📚 Key Features Implemented

### 1. **Unified Login System**
- Single login page for all three roles
- Login with **Roll Number OR Email** (students)
- Login with **Email** (faculty & admin)
- Automatic role-based redirects

### 2. **Admin Dashboard** (`/admin`)
- Manage Faculty Members
  - Add faculty with section assignment
  - Edit faculty details
  - Delete faculty accounts
- View all user/system statistics
- Manage courses, students, attendance, marks

### 3. **Faculty Dashboard** (`/faculty/dashboard`)
- View assigned courses
- See total students count
- **NEW**: View section students (`/faculty/students`)
  - Automatically filtered by faculty's assigned section
  - See student details (name, roll number, email, etc.)

### 4. **Student Dashboard** (`/student-dashboard`)
- View recent notices
- View upcoming events
- Access marks, attendance, profile

### 5. **Role-Based Security**
- All routes protected with `@login_required(role='...')` decorator
- Faculty cannot access admin pages
- Students cannot access faculty/admin pages
- Unauthorized access → Flash message + redirect to login

---

## 📂 Files Added/Modified

### New Routes in app.py
```
/admin/faculty              - View all faculty
/admin/faculty/add          - Add new faculty (GET/POST)
/admin/faculty/<id>/edit    - Edit faculty (GET/POST)
/admin/faculty/<id>/delete  - Delete faculty (POST)
```

### New Templates Created
```
templates/add_faculty.html      - Faculty creation form
templates/edit_faculty.html     - Faculty editing form
templates/manage_faculty.html   - Faculty listing page
```

### Modified Files
```
app.py                          - Added faculty management routes
templates/base.html             - Added faculty management nav links
ROLE_BASED_AUTHENTICATION.md    - Complete documentation
```

---

## 🔑 Session & Authorization

### Session Variables (Set on Login)
```python
session['user']      # Username for display
session['user_id']   # User ID for queries
session['role']      # 'admin', 'faculty', or 'student'
```

### Role Check in Code
```python
# In Python/Flask routes:
if session['role'] == 'admin':
    # Show admin menu
elif session['role'] == 'faculty':
    # Show faculty menu
else:
    # Show student menu
```

### In HTML Templates
```html
{% if session.role == 'admin' %}
    <a href="{{ url_for('manage_faculty') }}">Manage Faculty</a>
{% endif %}
```

---

## ⚙️ Database Schema

### Users Table (Updated by Migration)
```sql
users (
    id,              -- Primary key
    username,        -- Unique, for login
    password,        -- Hashed
    email,           -- Unique, for login
    role,            -- 'admin', 'faculty', 'student'
    full_name,       -- Added by migration
    mobile,          -- Added by migration
    section,         -- Added by migration (e.g., 'CSE-A')
    semester,        -- Added by migration
    roll_no,         -- Added by migration (for students)
    photo,           -- Added by migration (profile photo)
    created_at       -- Account creation date
)
```

### Students Table (Existing)
```sql
students (
    id,
    user_id,         -- Foreign key → users.id
    roll_no,         -- Unique roll number
    full_name,
    date_of_birth,
    phone,
    address,
    semester,
    section,         -- Section assignment
    is_active,
    created_at
)
```

---

## ✨ Testing Workflow

### Complete Test Flow:

1. **Start Fresh**
   ```bash
   rm college.db           # Delete old database
   python init_db_only.py  # Create fresh database
   python migrate_add_registration_fields.py  # Add columns
   ```

2. **Create Admin**
   - Use Python script from Option A above

3. **Admin Creates Faculty**
   - Login as admin → Manage Faculty → Add New Faculty
   - Creates: `faculty1@college.edu` with section `CSE-A`

4. **Register Student**
   - Logout → Register → Fill form
   - Creates: `student@college.edu` with roll `CSE001` in section `CSE-A`

5. **Test Logins**
   ```
   Admin:   admin@college.edu / admin123
   Faculty: faculty1@college.edu / faculty123
   Student: student@college.edu / student123 OR CSE001 / student123
   ```

6. **Test Role Separation**
   - Admin sees admin dashboard & faculty management
   - Faculty sees faculty students (only from CSE-A section)
   - Student sees student dashboard, marks, attendance

---

## 🐛 Troubleshooting

### Q: Faculty cannot see students
**A:** Check that:
- Faculty has a `section` value (e.g., 'CSE-A')
- Students have the same `section` value in students table
- Run: `SELECT * FROM users WHERE role='faculty'` → Check section column

### Q: Login keeps redirecting to login page
**A:** Check that:
- Role is set correctly: `SELECT role FROM users WHERE email='...'`
- `@login_required` decorator is applied

### Q: "You need to be admin to access this page" error
**A:** Normal behavior - you're logged in as a different role. Try logging in as admin.

### Q: Password hashing issues
**A:** Ensure werkzeug is installed: `pip install werkzeug`

---

## 📖 Complete Documentation

For detailed documentation, see:
```
college_notification/ROLE_BASED_AUTHENTICATION.md
```

Contains:
- Full API endpoint reference
- Database schema details
- Security considerations
- Future enhancement suggestions

---

## ✅ Checklist - What's Working

- [x] Unified login page for all roles
- [x] Login with roll_no OR email for students
- [x] Role-based redirects on login
- [x] Admin dashboard with faculty management
- [x] Faculty add/edit/delete functionality
- [x] Faculty can view only their section students
- [x] Student registration unchanged
- [x] Role-based access control
- [x] Session management
- [x] Navigation updated for all roles
- [x] Database migrations ready
- [x] No breaking changes to student system

---

## 🎯 Next Steps

1. **Test the complete flow** using the testing workflow above
2. **Customize** section names as needed (CSE-A, ECE-B, etc.)
3. **Set up initial admin** using the provided scripts
4. **Train users** on the new role-based system
5. **Monitor** faculty-student assignments by section

---

**Status**: ✅ Ready for Production

For support or questions, refer to:
- `ROLE_BASED_AUTHENTICATION.md` - Full documentation
- `app.py` - Implementation code
- `templates/` - UI templates

---

**Version**: 2.0  
**Last Updated**: 2024  
**Upgrade Date**: Complete
