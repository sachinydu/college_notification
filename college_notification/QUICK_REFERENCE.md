# ⚡ Quick Reference Card - College ERP

## 🚀 GET STARTED IN 30 SECONDS

```bash
# 1. Go to project directory
cd college_notification

# 2. Run the app
python app.py

# 3. Open browser
http://localhost:5000/

# 4. Login with demo account
Username: admin
Password: admin123
```

---

## 👤 Demo Accounts

### Admin
```
URL:      http://localhost:5000/
Username: admin
Password: admin123
Access:   All ERP Features
```

### Faculty
```
URL:      http://localhost:5000/
Username: faculty1
Password: faculty123
Access:   Grades & Attendance
```

### Student  
```
URL:      http://localhost:5000/
Username: student1
Password: student123
Access:   Dashboard, Grades, Attendance
```

---

## 📊 Main Features

| Feature | Admin | Faculty | Student |
|---------|-------|---------|---------|
| Students | ✅ | ✅ | ❌ |
| Courses | ✅ | ✅ | ✅ |
| Enrollment | ✅ | ❌ | ❌ |
| Attendance | ✅ | ✅ | ✅ |
| Grades | ✅ | ✅ | ✅ |
| Dashboard | ✅ | ✅ | ✅ |

---

## 🗂️ Key Pages

### For Admin:
- `/admin` - Dashboard
- `/admin/students` - Manage Students
- `/admin/courses` - Manage Courses
- `/admin/enrollments` - Manage Enrollments
- `/admin/attendance` - Mark Attendance
- `/admin/grades` - Manage Grades

### For Student:
- `/student/dashboard` - Dashboard
- `/student/grades` - View Grades
- `/student/attendance` - View Attendance

### For Faculty:
- `/faculty/dashboard` - Dashboard
- `/admin/grades?course_id=X` - Manage Grades
- `/admin/attendance` - Mark Attendance

---

## 📝 Database Tables

```
students      - Student profiles
courses       - Courses offered
enrollments   - Student-Course links
attendance    - Daily attendance
grades        - Student marks
users         - User accounts
notices       - Notifications
events        - Events
```

---

## 🎯 Common Tasks

### Add a Student
1. Login as Admin
2. Click "Students" in sidebar
3. Click "+ Add Student"
4. Fill form and submit

### Create a Course
1. Login as Admin
2. Click "Courses" in sidebar
3. Click "+ Add Course"
4. Assign faculty (optional)
5. Click Add Course

### Enroll Student
1. Login as Admin
2. Click "Enrollments"
3. Click "+ Add Enrollment"
4. Select student & course
5. Confirm

### Mark Attendance
1. Login as Admin/Faculty
2. Click "Attendance"
3. Select course and date
4. Click Present/Absent/Leave
5. Changes auto-save

### Add Grades
1. Login as Admin/Faculty
2. Click "Grades"
3. Click "+ Add Grade"
4. Enter marks (grade auto-calculates)
5. Save

---

## 🔍 Grade Scale

```
A+  →  90-100%
A   →  80-89%
B   →  70-79%
C   →  60-69%
D   →  50-59%
F   →  Below 50%
```

---

## 🛠️ Troubleshooting

### App won't start?
```bash
# Check Python installed
python --version

# Install Flask if needed
pip install flask

# Run again
python app.py
```

### Database issue?
```bash
# Delete database
rm college.db

# Restart app (auto-recreates DB)
python app.py
```

### Can't login?
- Check username/password spelling
- Try demo accounts (see above)
- Clear browser cookies

### Pages not loading?
- Check URL path (case-sensitive)
- Verify login first
- Restart app

---

## 📚 Documentation

| Document | Content |
|----------|---------|
| README_ERP.md | Overview & Quick Start |
| ERP_FEATURES.md | Complete Feature List |
| DEPLOYMENT_GUIDE.md | Setup & Deployment |
| SYSTEM_OVERVIEW.md | Architecture & Diagrams |
| CHANGELOG.md | All Changes Made |

---

## 🔐 Security Tips

- ⚠️ Change admin password in production
- ⚠️ Use HTTPS for production
- ⚠️ Set secure secret key
- ⚠️ Hash passwords before production
- ⚠️ Implement rate limiting

---

## 📊 Example Data

**Sample Student:**
- Roll No: CS2024001
- Name: John Doe
- Username: student1
- Semester: 2

**Sample Courses:**
- CS101 - Data Structures (4 Credits)
- CS102 - Database Management (4 Credits)

**Sample Grades:**
- CS101: 85 marks = Grade A
- CS102: 92 marks = Grade A+

---

## 🎨 UI Features

✅ Responsive design (Mobile & Desktop)
✅ Color-coded badges & alerts
✅ Bootstrap tables
✅ Quick search & filter
✅ Form validation
✅ Status indicators
✅ Breadcrumb navigation

---

## 📈 System Stats

**Total Features:** 7 modules
**Routes:** 25+
**Database Tables:** 8
**Templates:** 21+
**Documentation:** 5 guides
**Lines of Code:** 3000+

---

## 🚀 Next Steps

1. ✅ Start the app
2. ✅ Login with demo accounts
3. ✅ Explore each module
4. ✅ Read detailed documentation
5. ✅ Customize for your college
6. ✅ Deploy to production

---

## 💡 Tips

- Bookmark `/admin` for quick access
- Use Firefox/Chrome for best experience
- Keep browser window wide for tables
- Check console (F12) for errors
- Export attendance reports manually if needed

---

## 🆘 Help Resources

**In-App Help:** Click Help in sidebar
**Documentation:** See .md files in project
**GitHub Issues:** Report bugs on GitHub
**Stack Overflow:** Search Flask + SQLite

---

## ✨ Features at a Glance

```
┌─────────────────────────────────┐
│  COLLEGE ERP SYSTEM             │
├─────────────────────────────────┤
│ ✅ Student Management           │
│ ✅ Course Management            │
│ ✅ Enrollment Tracking          │
│ ✅ Attendance Management        │
│ ✅ Grades & Assessment          │
│ ✅ Student Portal               │
│ ✅ Faculty Portal               │
│ ✅ Notifications (Existing)     │
│ ✅ Events (Existing)            │
│ ✅ Role-Based Access            │
│ ✅ Responsive Design            │
│ ✅ Demo Data Included           │
└─────────────────────────────────┘
```

---

## 📞 Quick Links

- **Admin Dashboard:** [/admin](/admin)
- **Students:** [/admin/students](/admin/students)
- **Courses:** [/admin/courses](/admin/courses)
- **Grades:** [/admin/grades](/admin/grades)
- **Attendance:** [/admin/attendance](/admin/attendance)
- **Student Dashboard:** [/student/dashboard](/student/dashboard)
- **Faculty Dashboard:** [/faculty/dashboard](/faculty/dashboard)

---

**Status:** ✅ Ready to Use  
**Version:** 1.0 - ERP Edition  
**Created:** January 20, 2026

---

## Quick Shortcut Cheat Sheet

```
LOGIN:
  Admin    → username: admin / password: admin123
  Faculty  → username: faculty1 / password: faculty123
  Student  → username: student1 / password: student123

NAVIGATION:
  Sidebar  → Click menu items (Admin)
  Top Bar  → Click links (Student/Faculty)

FORMS:
  Add      → Click + button
  Edit     → Click Edit button in table
  Delete   → Click Delete (with confirmation)
  View     → Click table row or link

FILTERS:
  Course   → Select from dropdown
  Date     → Pick from date picker
  Semester → Select from options
  Status   → Select from dropdown

MARKS:
  Student  → See dashboard for overview
  Faculty  → Go to Grades to enter
  Admin    → Go to Grades to manage
```

---

**Remember:** Everything is working out of the box!  
Just run `python app.py` and login with any demo account.

**Enjoy your College ERP System!** 🎓
