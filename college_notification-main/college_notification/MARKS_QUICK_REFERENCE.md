# Marks System - Quick Reference Guide

## 🚀 Quick Start

### Student Marks View
**URL:** `/student/marks`

**What It Shows:**
- All subjects with ST1, ST2, PUT marks
- Each exam in a card showing: Marks/Max and Percentage
- Subject-level summaries
- Overall performance metrics

**Example Output:**
```
CS101 - Data Structures
┌────────────────────┬────────────────────┬────────────────────┐
│ ST1: 45/50 (90%)   │ ST2: 48/50 (96%)   │ PUT: 85/100 (85%)  │
└────────────────────┴────────────────────┴────────────────────┘
Subject Total: 178/200 (89%)
```

---

### Admin Marks Management
**URL:** `/admin/marks`

**Features:**
1. Select a course
2. Select exam type (ST1/ST2/PUT)
3. View all students' marks in table
4. Edit/Delete individual entries
5. View summary statistics

**Actions:**
- ✏️ Edit marks
- 🗑️ Delete marks
- ➕ Add new marks

---

## 📊 Database Query Examples

### Get Student Marks for GUI
```python
marks_data = db.execute("""
    SELECT m.id, m.exam_type, m.max_marks, m.obtained_marks,
           ROUND((m.obtained_marks / m.max_marks) * 100, 2) as percentage,
           c.id as course_id, c.course_code, c.course_name
    FROM marks m
    JOIN courses c ON m.course_id = c.id
    WHERE m.student_id=?
    ORDER BY c.course_code
""", (student_id,)).fetchall()
```

### Get Course-Wise Marks (Admin)
```python
marks = db.execute("""
    SELECT m.id, m.exam_type, s.roll_no, s.full_name, 
           m.max_marks, m.obtained_marks,
           ROUND((m.obtained_marks / m.max_marks) * 100, 2) as percentage
    FROM marks m
    JOIN students s ON m.student_id = s.id
    WHERE m.course_id=? AND m.exam_type=?
    ORDER BY s.roll_no
""", (course_id, exam_type)).fetchall()
```

---

## 🛠️ Common Operations

### Add Marks (New Entry)
```python
db.execute("""
    INSERT INTO marks (student_id, course_id, exam_type, max_marks, obtained_marks)
    VALUES (?, ?, ?, ?, ?)
""", (student_id, course_id, 'ST1', 50, 45))
db.commit()
```

### Update Marks
```python
db.execute("""
    UPDATE marks SET max_marks=?, obtained_marks=? 
    WHERE id=?
""", (50, 47, mark_id))
db.commit()
```

### Delete Marks
```python
db.execute("DELETE FROM marks WHERE id=?", (mark_id,))
db.commit()
```

### Calculate Subject Percentage
```python
total_obtained = sum(m['obtained_marks'] for m in subject_marks)
total_max = sum(m['max_marks'] for m in subject_marks)
percentage = (total_obtained / total_max) * 100
```

---

## 🎨 CSS Classes for Styling

### Percentage Badges
```css
.percentage-value.high      /* >= 75% - Green */
.percentage-value.medium    /* 60-74% - Yellow */
.percentage-value.low       /* < 60% - Red */
```

### Exam Type Badges
```css
.exam-type-badge.st1   /* Blue - Sessional Test 1 */
.exam-type-badge.st2   /* Purple - Sessional Test 2 */
.exam-type-badge.put   /* Pink - Pre University Test */
```

---

## 📱 Responsive Breakpoints

- **Desktop**: 3-column grid
- **Tablet**: 2-column grid  
- **Mobile**: 1-column layout

Breakpoint: `@media (max-width: 768px)`

---

## ⚠️ Important Notes

1. **Exam Type Values (Case Sensitive):**
   - `'ST1'` - Sessional Test 1
   - `'ST2'` - Sessional Test 2
   - `'PUT'` - Pre University Test

2. **Unique Constraint:**
   - Each student can have only ONE mark per `(student_id, course_id, exam_type)` combination
   - Duplicate entries will raise `IntegrityError`

3. **Validation:**
   - `obtained_marks` cannot exceed `max_marks`
   - Both must be non-negative numbers
   - Percentage is auto-calculated as `(obtained_marks / max_marks) * 100`

4. **No Grade System:**
   - Grades table is completely removed/unused
   - All grading now done through percentages
   - Students see marks and percentages only

---

## 🔍 Troubleshooting

### Issue: "Marks already exist for this student-course-exam pair"
**Solution:** Delete existing mark first or update instead of insert

### Issue: "Obtained marks cannot exceed max marks"
**Solution:** Enter a valid obtained_marks value that is ≤ max_marks

### Issue: Marks not showing for student
**Solution:** Check if:
- Marks exist in database (`SELECT * FROM marks WHERE student_id=X`)
- Student is enrolled in course (`SELECT * FROM enrollments WHERE student_id=X`)
- Exam type is correct ('ST1', 'ST2', or 'PUT')

### Issue: Percentage showing as 0%
**Solution:** Check if max_marks=0 (division by zero). Set max_marks > 0

---

## 📈 State Diagram

```
Student Login
    ↓
View Marks (/student/marks)
    ↓
Query marks grouped by course & exam_type
    ↓
Calculate percentage for each
    ↓
Display in card format:
├─ Subject header
├─ ST1 card (if exists)
├─ ST2 card (if exists)
├─ PUT card (if exists)
├─ Subject summary
└─ Overall performance

Admin View (/admin/marks)
    ↓
Select course & exam type
    ↓
Query marks as table rows
    ↓
Display with edit/delete options
    ↓
Show summary statistics
```

---

## 🔐 Security Notes

- All queries use parameterized statements (? placeholders)
- Role-based access: `@login_required(role='faculty')` or `@login_required(role='admin')`
- Faculty can only manage their own courses
- Admin can manage all marks

---

## 📞 Support Contacts

For issues with:
- **Marks calculations**: Check `app.py` lines 1750-1775
- **UI/Templates**: Check `templates/student_marks.html` or `manage_marks.html`
- **Database**: Check `schema.sql` marks table definition

---

**Last Updated:** March 25, 2026
**Status:** Production Ready ✅
