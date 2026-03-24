# Flask ERP - Role-Based Authentication System

## Overview
The Flask ERP system now supports three user roles:
- **Admin**: System administrator with full management capabilities
- **Faculty**: Teachers who manage their assigned section students
- **Student**: Regular users who view their dashboard, grades, attendance, etc.

## System Requirements & Setup

### 1. Database Migration
Before running the application, ensure the database schema is updated with required fields:

```bash
# Run this from the college_notification directory
python migrate_add_registration_fields.py
```

This migration adds the following columns to the `users` table:
- `full_name`: User's full name (TEXT)
- `roll_no`: Student roll number (TEXT, unique index)
- `mobile`: Phone number (TEXT)
- `semester`: Current semester (INTEGER, default 1)
- `section`: Assigned section (TEXT, default 'A')
- `photo`: Profile photo path (TEXT)

### 2. Login System

#### Unified Login Page
- URL: `/login`
- A single login page for all three roles
- Users can login using:
  - **Students**: Roll number OR email + password
  - **Faculty**: Email + password
  - **Admin**: Email + password

#### Login Flow Example

**Student Login:**
```
Input: roll_no="CSE001" or email="student@college.edu", password="pass123"
✓ Login successful → Redirected to /student-dashboard
```

**Faculty Login:**
```
Input: email="faculty@college.edu", password="pass123"
✓ Login successful → Redirected to /faculty-dashboard
```

**Admin Login:**
```
Input: email="admin@college.edu", password="pass123"
✓ Login successful → Redirected to /admin-dashboard (redirects to /admin in code)
```

### 3. Role-Based Access Control

All protected routes use the `@login_required(role='role_name')` decorator:

```python
@app.route('/admin/faculty')
@login_required(role='admin')  # Only admin can access
def manage_faculty():
    ...

@app.route('/faculty/students')
@login_required(role='faculty')  # Only faculty can access
def faculty_view_students():
    ...
```

Unauthorized access attempts result in:
```
Flash Message: "You need to be {role} to access this page!"
Redirect: → Login page
```

## Admin Functionality

### Faculty Management System

#### 1. View All Faculty
- **Route**: `/admin/faculty`
- **Features**:
  - List all faculty members
  - Display: Name, Email, Section, Mobile, Joined Date
  - Statistics: Total faculty, sections covered

#### 2. Add New Faculty
- **Route**: `/admin/faculty/add`
- **Form Fields**:
  - Username (required, unique)
  - Full Name (required)
  - Email (required, unique, validated format)
  - Section (required) - e.g., "CSE-A", "ECE-B"
  - Mobile Number (optional, 10 digits if provided)
  - Password (required, min 6 characters)
- **Security**: Passwords are hashed using werkzeug
- **Success**: Faculty can login immediately after creation

#### 3. Edit Faculty
- **Route**: `/admin/faculty/{id}/edit`
- **Editable Fields**:
  - Full Name
  - Email (validated for uniqueness)
  - Section
  - Mobile Number
- **Non-editable**: Username (for audit trail)

#### 4. Delete Faculty
- **Route**: `/admin/faculty/{id}/delete`
- **Safeguards**:
  - Prevents self-deletion
  - Cascading delete (removes related records if foreign keys set)
  - Confirmation dialog required

### Other Admin Features
- User Management: `/admin/users`
- Course Management: `/admin/courses`
- Enrollment Management: `/admin/enrollments`
- Attendance Management: `/admin/attendance`
- Marks Management: `/admin/marks`

## Faculty Functionality

### Dashboard
- **Route**: `/faculty/dashboard`
- **Display**:
  - Assigned courses
  - Total students in section
  - Quick access to student management

### Section Students Management
- **Route**: `/faculty/students`
- **Features**:
  - View all students in assigned section
  - Filter students by section (automatic, based on faculty.section)
  - Security: Faculty can ONLY see students from their section
- **Query**: 
  ```sql
  SELECT s.* FROM students s
  JOIN users u ON s.user_id = u.id
  WHERE s.section = faculty_section
  ```

### Other Faculty Features
- Marks Management: `/faculty/marks` (for their students)
- Attendance Management: `/faculty/attendance`
- Course Management: View assigned courses

## Student Functionality

### Dashboard
- **Route**: `/student-dashboard`
- **Display**:
  - Recent notices
  - Upcoming events
  - Performance overview

### Features
- View Grades/Marks: `/student/marks` (replaced old `/student/grades`)
- View Attendance: `/student/attendance`
- View Notices: `/notifications`
- View Events: `/events`
- Profile: `/profile`
- Settings: `/settings`

## Session Management

Session variables set on login:
```python
session['user'] = user['username']           # For display
session['user_id'] = user['id']              # For queries
session['role'] = user['role']               # For access control ('admin', 'faculty', 'student')
session.permanent = True                     # Persistent session
```

Example check in templates:
```html
{% if session.role == 'admin' %}
    <!-- Show admin navigation -->
{% elif session.role == 'faculty' %}
    <!-- Show faculty navigation -->
{% else %}
    <!-- Show student navigation -->
{% endif %}
```

## Navigation Structure

### Admin Navigation (Sidebar)
```
Dashboard
├── Management
│   ├── Faculty (NEW)
│   ├── Courses
│   ├── Enrollments
│   ├── Attendance
│   └── Marks
├── Communications
│   ├── Notifications
│   ├── Events
│   └── Search
└── User
    ├── Profile
    ├── Settings
    └── Help
```

### Faculty Navigation (Sidebar)
```
Dashboard
Students (NEW)
Grades
Attendance
Notices
Profile
Settings
Help
```

### Student Navigation (Sidebar)
```
Dashboard
Grades
Attendance
Events
Notices
Profile
Settings
Help
```

## Database Schema (Relevant Sections)

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL,  -- 'admin', 'faculty', or 'student'
    full_name TEXT DEFAULT '',
    roll_no TEXT,  -- For students
    mobile TEXT DEFAULT '',
    semester INTEGER DEFAULT 1,
    section TEXT DEFAULT 'A',  -- Section assignment for faculty/students
    photo TEXT DEFAULT '',
    email_notifications_enabled INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
```

### Students Table (Maintains separate record for detailed info)
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    date_of_birth TEXT,
    phone TEXT,
    address TEXT,
    semester INTEGER DEFAULT 1,
    section TEXT DEFAULT 'A',
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Testing Checklist

### 1. Admin Login & Faculty Management
- [ ] Login as admin with email and password
- [ ] Navigate to Faculty Management (`/admin/faculty`)
- [ ] Add new faculty with required fields
- [ ] Edit faculty details
- [ ] Delete faculty member
- [ ] Verify faculty can login after creation

### 2. Faculty Login & Student View
- [ ] Login as newly created faculty
- [ ] Navigate to Students page (`/faculty/students`)
- [ ] Verify only students from faculty's section are shown
- [ ] Check student list matches section assignment

### 3. Student Login
- [ ] Student registration works correctly
- [ ] Student can login with roll number
- [ ] Student can login with email
- [ ] Student dashboard displays correctly
- [ ] Student can view marks/attendance/events

### 4. Access Control
- [ ] Faculty cannot access admin pages
- [ ] Student cannot access faculty pages
- [ ] Student cannot access admin pages
- [ ] Unauthorized access shows appropriate error

### 5. Role-Based Navigation
- [ ] Admin sidebar shows faculty management link
- [ ] Faculty sidebar shows students link
- [ ] Student sidebar shows correct navigation items
- [ ] Logout redirects to login page

## Common Issues & Solutions

### Issue: Migration Script Fails
**Solution**: Ensure the database file exists at `/college.db`. Run `python init_db_only.py` first.

### Issue: Faculty Cannot See Students
**Solution**: Ensure faculty has a `section` value assigned in the users table and students have the same section value in students table.

### Issue: Login always redirects to admin
**Solution**: Check that `session['role']` is being set correctly in login route. Verify user role in database.

### Issue: "No filter named 'regex_replace'"
**Solution**: This error is fixed. Use string slicing in templates: `{{ phone[:5] }} {{ phone[5:] }}`

## Security Considerations

1. **Password Hashing**: All passwords are hashed using werkzeug.security
2. **Session Management**: Session includes user_id and role for quick authorization checks
3. **SQL Injection Prevention**: All queries use parameterized statements (?)
4. **CSRF Protection**: Flask-WTF forms include CSRF tokens (if using WTForms)
5. **Role-Based Access**: Decorator prevents unauthorized access at route level
6. **Section Isolation**: Faculty queries filtered by section automatically

## Future Enhancements

1. Two-factor authentication (2FA)
2. IP-based access restrictions for admin
3. Activity logging for audit trails
4. Automatic role assignment based on email domain
5. Bulk faculty import from CSV
6. Permission-based access control (more granular than role-based)

## API Endpoints Reference

### Public Routes
- `/login` - GET/POST
- `/register` - GET/POST (student registration)
- `/` - Redirects based on role if logged in

### Admin Routes (Protected)
- `/admin` - Dashboard
- `/admin/faculty` - List faculty
- `/admin/faculty/add` - Add faculty
- `/admin/faculty/<id>/edit` - Edit faculty
- `/admin/faculty/<id>/delete` - Delete faculty
- `/admin/courses` - Manage courses
- `/admin/students` - Manage students
- `/admin/attendance` - Manage attendance
- `/admin/marks` - Manage marks

### Faculty Routes (Protected)
- `/faculty/dashboard` - Dashboard
- `/faculty/students` - View section students
- `/faculty/marks` - Mark student grades
- `/faculty/attendance` - Mark attendance

### Student Routes (Protected)
- `/student-dashboard` - Dashboard
- `/student/grades` - View grades (redirects to marks)
- `/student/marks` - View marks
- `/student/attendance` - View attendance

---

**Last Updated**: 2024
**Version**: 2.0 (Role-Based Authentication)
