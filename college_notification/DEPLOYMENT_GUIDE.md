# College ERP System - Integration & Deployment Guide

## Quick Start

### 1. Prerequisites
- Python 3.8+
- Flask 2.0+
- SQLite3

### 2. Installation

```bash
# Navigate to project directory
cd college_notification

# Install dependencies (if using requirements.txt)
pip install flask

# Run the application
python app.py
```

### 3. Database Setup
The database is automatically initialized on first run with:
- Users table with admin, faculty, and student accounts
- Students table with sample student
- Courses table with 2 sample courses
- Enrollments linking students to courses
- Grades with sample grades
- Attendance and other ERP tables

### 4. Access the System

**Default Credentials:**

```
ADMIN:
  URL: http://localhost:5000/
  Username: admin
  Password: admin123

FACULTY:
  Username: faculty1
  Password: faculty123

STUDENT:
  Username: student1
  Password: student123
```

## System Architecture

### Database Tables

```
users
├── id (PK)
├── username (UNIQUE)
├── password
├── email
├── role (admin, faculty, student)
└── created_at

students
├── id (PK)
├── user_id (FK -> users)
├── roll_no (UNIQUE)
├── full_name
├── date_of_birth
├── phone
├── address
├── semester
├── is_active
└── created_at

courses
├── id (PK)
├── course_code (UNIQUE)
├── course_name
├── credits
├── semester
├── faculty_id (FK -> users)
├── description
└── created_at

enrollments
├── id (PK)
├── student_id (FK -> students)
├── course_id (FK -> courses)
└── enrolled_date

attendance
├── id (PK)
├── student_id (FK -> students)
├── course_id (FK -> courses)
├── attendance_date
├── status (Present, Absent, Leave)
└── created_at

grades
├── id (PK)
├── student_id (FK -> students)
├── course_id (FK -> courses)
├── marks_obtained
├── total_marks
├── grade
└── created_at
```

## API Endpoints

### Admin Routes

#### Student Management
- `GET /admin/students` - List all students
- `GET /admin/student/add` - Add student form
- `POST /admin/student/add` - Create new student
- `GET /admin/student/<id>/edit` - Edit student form
- `POST /admin/student/<id>/edit` - Update student

#### Course Management
- `GET /admin/courses` - List all courses
- `GET /admin/course/add` - Add course form
- `POST /admin/course/add` - Create new course
- `GET /admin/course/<id>/edit` - Edit course form
- `POST /admin/course/<id>/edit` - Update course
- `POST /admin/course/<id>/delete` - Delete course

#### Enrollment Management
- `GET /admin/enrollments` - List enrollments
- `GET /admin/enrollment/add` - Add enrollment form
- `POST /admin/enrollment/add` - Create enrollment
- `POST /admin/enrollment/<id>/delete` - Remove enrollment

#### Attendance Management
- `GET /admin/attendance` - View/mark attendance
- `POST /admin/attendance/mark` - Mark attendance (JSON API)

#### Grades Management
- `GET /admin/grades` - View grades
- `GET /admin/grade/add` - Add grade form
- `POST /admin/grade/add` - Create grade
- `GET /admin/grade/<id>/edit` - Edit grade form
- `POST /admin/grade/<id>/edit` - Update grade

### Student Routes

- `GET /student/dashboard` - Student dashboard
- `GET /student/grades` - View student grades
- `GET /student/attendance` - View student attendance

### Faculty Routes

- `GET /faculty/dashboard` - Faculty dashboard
- `GET /admin/grades?course_id=<id>` - Manage course grades
- `GET /admin/attendance` - Mark course attendance

## Role-Based Access Control

### Admin
- ✅ Full access to all ERP modules
- ✅ Create/Edit/Delete students, courses, enrollments
- ✅ Manage attendance and grades for all courses
- ✅ View all system data

### Faculty
- ✅ View assigned courses
- ✅ Manage grades for assigned courses
- ✅ Mark attendance for assigned courses
- ❌ Cannot modify courses or enrollments

### Student
- ✅ View own dashboard
- ✅ View own grades
- ✅ View own attendance
- ✅ View enrolled courses
- ❌ Cannot modify any data

## Features by Module

### 1. Student Management
- Search by roll number or name
- Filter by semester
- Activate/deactivate students
- View student profile details
- Track enrollment status

### 2. Course Management
- Organize by semester
- Assign faculty members
- Track credits
- View course descriptions
- Manage course availability

### 3. Enrollment Management
- Link students to courses
- Prevent duplicate enrollments
- View enrollment dates
- Remove students from courses
- Track student course history

### 4. Attendance Tracking
- Mark attendance by date and course
- Three attendance statuses: Present, Absent, Leave
- View attendance by course
- Calculate attendance percentage
- Historical attendance records

### 5. Grades Management
- Input marks and automatically calculate grades
- Support for custom total marks
- Automatic letter grade assignment
- View grades by student or course
- Edit grades after entry

### 6. Student Portal
- Personal dashboard with statistics
- Course enrollment information
- Grade reports with percentages
- Attendance summary with percentages
- Quick access to academic information

### 7. Faculty Portal
- Dashboard showing assigned courses
- Total students taught count
- Quick access to grade entry
- Attendance marking interface

## Customization

### Adding New User Roles

Edit `login_required()` decorator in `app.py` and add role checks:

```python
@app.route('/path')
@login_required(role=['admin', 'new_role'])
def function_name():
    # Your code
```

### Modifying Grading Scale

Edit the grade calculation logic in `add_grade()` and `edit_grade()` routes:

```python
# Calculate grade
percentage = (marks / total_marks) * 100
if percentage >= 90:
    grade = 'A+'
# ... modify thresholds as needed
```

### Customizing Database Fields

1. Update `schema.sql` with new fields
2. Modify templates in `templates/` folder
3. Update Flask routes in `app.py`
4. Delete `college.db` and restart app for fresh database

## Deployment

### For Production:
1. Set `app.run(debug=False)` in app.py
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure proper database (PostgreSQL, MySQL)
4. Set up secure session management
5. Implement HTTPS
6. Set secure secret key in `app.secret_key`

### Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Database Errors
- Delete `college.db` to reset database
- Check file permissions
- Ensure SQLite3 is installed

### Routes Not Found
- Check Flask route spelling
- Verify templates exist in correct folder
- Check URL patterns match `url_for()` calls

### Permission Denied
- Verify user role in session
- Check `@login_required()` decorator on route
- Clear browser cookies and login again

## Future Enhancements

- Email notifications for grades/attendance
- SMS alerts
- Advanced reporting and analytics
- Online exam management
- Assignment submission system
- Hostel and fees management
- Time table scheduling
- Alumni portal
- Mobile app support
