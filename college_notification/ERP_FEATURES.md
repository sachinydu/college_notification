# College ERP System - Enhanced Features

This document describes all the new ERP (Enterprise Resource Planning) features added to the College Notification System.

## Overview

The system has been enhanced with comprehensive ERP functionality to manage academic operations including student management, course management, enrollment tracking, attendance management, and grades tracking.

## New Features

### 1. **Student Management**
- Add new students with login credentials
- Edit student details (name, phone, semester, status)
- View all active and inactive students
- Track student enrollment status
- **Routes:**
  - `/admin/students` - View all students
  - `/admin/student/add` - Add new student
  - `/admin/student/<id>/edit` - Edit student details

### 2. **Course Management**
- Create courses with course code, name, credits, and semester
- Assign faculty members to courses
- Edit course details
- Delete courses
- **Routes:**
  - `/admin/courses` - View all courses
  - `/admin/course/add` - Add new course
  - `/admin/course/<id>/edit` - Edit course
  - `/admin/course/<id>/delete` - Delete course

### 3. **Enrollment Management**
- Enroll students in courses
- View enrollment records
- Remove students from courses
- **Routes:**
  - `/admin/enrollments` - View enrollments
  - `/admin/enrollment/add` - Add enrollment
  - `/admin/enrollment/<id>/delete` - Remove enrollment

### 4. **Attendance Management**
- Mark attendance for students (Present, Absent, Leave)
- View attendance by course and date
- Calculate attendance percentage
- **Routes:**
  - `/admin/attendance` - Manage attendance records
  - `/admin/attendance/mark` - Mark attendance (API)

### 5. **Grades Management**
- Add grades for student-course combinations
- Auto-calculate letter grades based on marks
- Edit existing grades
- View grades by course
- **Grading Scale:**
  - A+ / A: 80 - 100%
  - B: 70 - 79%
  - C: 60 - 69%
  - D: 50 - 59%
  - F: Below 50%
- **Routes:**
  - `/admin/grades` - View grades
  - `/admin/grade/add` - Add grade
  - `/admin/grade/<id>/edit` - Edit grade

### 6. **Student Portal**
- **Student Dashboard** - Overview of courses, grades, attendance
- **Student Grades** - View all earned grades with percentages
- **Student Attendance** - View attendance records with status
- **Routes:**
  - `/student/dashboard` - Student dashboard
  - `/student/grades` - View student grades
  - `/student/attendance` - View student attendance

### 7. **Faculty Portal**
- **Faculty Dashboard** - Overview of assigned courses and student count
- **Manage Grades** - Add/edit grades for assigned courses
- **Mark Attendance** - Mark attendance for enrolled students
- **Routes:**
  - `/faculty/dashboard` - Faculty dashboard
  - (Uses same grade and attendance management as admin)

## Database Schema

### New Tables:
- **students** - Student profile information linked to user accounts
- **courses** - Course details with faculty assignment
- **enrollments** - Student-course enrollments
- **attendance** - Daily attendance records
- **grades** - Student grades for courses

### User Roles:
- **admin** - Full access to all ERP features
- **faculty** - Can manage grades and attendance for assigned courses
- **student** - Can view own grades, attendance, and course information

## Demo Credentials

### Admin Account
- Username: `admin`
- Password: `admin123`

### Faculty Account
- Username: `faculty1`
- Password: `faculty123`
- Assigned to: Data Structures, Database Management courses

### Student Account
- Username: `student1`
- Password: `student123`
- Roll No: `CS2024001`
- Enrolled in: Data Structures, Database Management courses

## Key Features

### For Administrators:
- Complete control over students, courses, enrollments
- Manage all academic records (attendance, grades)
- Assign faculty to courses
- Monitor system-wide activity

### For Faculty:
- View assigned courses
- Mark student attendance
- Enter and manage student grades
- View enrolled student information

### For Students:
- View enrolled courses
- Check grades and academic progress
- View attendance records and percentage
- Access course information

## Database Initialization

The system automatically initializes the database with demo data including:
- Admin, Faculty, and Student user accounts
- Sample courses (Data Structures, Database Management)
- Sample enrollments and grades

## Bootstrap Navigation

The navigation has been updated to show:
- **Admin View:** Full ERP menu with Students, Courses, Enrollments, Attendance, Grades
- **Faculty View:** Course Dashboard with Grades and Attendance management
- **Student View:** Dashboard, Grades, Attendance, Events, and Notices

## Technical Implementation

### Backend (Flask):
- New database tables with proper foreign key relationships
- Role-based access control
- API endpoints for attendance marking
- Automatic grade letter calculation

### Frontend (Templates):
- Responsive Bootstrap tables for all management views
- Forms for adding/editing records
- Student portal for viewing personal academic data
- Faculty-specific dashboards

## Future Enhancements

Potential additional features:
- Fees management
- Time-table scheduling
- Exam management
- Hostel management
- Library management
- Report generation and analytics
- Student leave management
- Online assignment submission
- Email notifications
