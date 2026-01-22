# ...existing code...

# ...existing code...
# ...existing code...
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
import sqlite3
import os
from functools import wraps
from datetime import datetime

# Database file name - ABSOLUTE PATH
DB = os.path.join(os.path.dirname(__file__), 'college.db')

# Flask app setup
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key_here'

# ----------------------------------------
# Grade Calculation Function
# ----------------------------------------
def calculate_grade(percentage):
    """Calculate grade based on percentage"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

# ----------------------------------------
# Database connection functions
# ----------------------------------------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        print(f"[*] Schema path: {schema_path}")
        
        if not os.path.exists(schema_path):
            print(f"[ERROR] schema.sql not found!")
            print(f"   Expected at: {schema_path}")
            return
        
        try:
            with open(schema_path, 'r') as f:
                sql_script = f.read()
                print(f"[OK] schema.sql loaded ({len(sql_script)} bytes)")
                db.executescript(sql_script)
            db.commit()
            print("[OK] Database initialized successfully!")
        except Exception as e:
            print(f"[ERROR] Database initialization error: {e}")
            db.rollback()

# ----------------------------------------
# Login Required Decorator
# ----------------------------------------
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                flash("Please login first!")
                return redirect(url_for('login'))
            if role:
                if isinstance(role, list):
                    if session.get('role') not in role:
                        print(f"[ERROR] Unauthorized: {session.get('user')} has role '{session.get('role')}' but needs {role}")
                        flash(f"You need to be {role} to access this page!")
                        return redirect(url_for('login'))
                else:
                    if session.get('role') != role:
                        print(f"[ERROR] Unauthorized: {session.get('user')} has role '{session.get('role')}' but needs '{role}'")
                        flash(f"You need to be {role} to access this page!")
                        return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ----------------------------------------
# Routes
# ----------------------------------------

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    else:
        db = get_db()
        recent_notices = db.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()
        upcoming_events = db.execute("SELECT * FROM events ORDER BY date ASC LIMIT 5").fetchall()
        return render_template('student_home.html', notices=recent_notices, events=upcoming_events)

# -------- LOGIN --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session.clear()  # Clear old session
            session['user'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            session.permanent = True
            flash(f"Login Successful! Welcome {username}!")
            print(f"[OK] User {username} logged in with role: {user['role']}")
            return redirect(url_for('home'))
        else:
            flash("Invalid Username or Password!")
            print(f"[ERROR] Login failed for {username}")
    
    # Clear session on GET request to ensure login page is shown
    if 'user' in session:
        session.clear()
    
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # Clear session on GET to show password reset page
    if request.method == 'GET' and 'user' in session:
        session.clear()
    
    if request.method == 'POST':
        username = request.form['username']
        db = get_db()
        user = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if user:
            # For now, just show the new password (in production, send email)
            new_password = username + '123'  # Default new password
            db.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
            db.commit()
            flash(f"Password reset successfully! New password: {new_password}")
            print(f"[INFO] Password reset for {username}")
        else:
            flash("Username not found!")
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# -------- ADMIN --------
@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    db = get_db()
    
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    student_count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    course_count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    notice_count = db.execute("SELECT COUNT(*) FROM notices").fetchone()[0]
    event_count = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    
    recent_notices = db.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()
    recent_events = db.execute("SELECT * FROM events ORDER BY date ASC LIMIT 5").fetchall()
    
    return render_template('admin_dashboard.html', 
                         user_count=user_count,
                         student_count=student_count,
                         course_count=course_count,
                         notice_count=notice_count,
                         event_count=event_count,
                         notices=recent_notices,
                         events=recent_events)

@app.route('/add_notice', methods=['GET', 'POST'])
@login_required(role='admin')
def add_notice():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'General')
        db = get_db()
        db.execute("INSERT INTO notices (title, content, category) VALUES (?, ?, ?)", (title, content, category))
        db.commit()
        flash("Notice added successfully!")
        return redirect(url_for('notifications'))
    return render_template('add_edit_notice.html', action='Add')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_notice(id):
    db = get_db()
    notice = db.execute("SELECT * FROM notices WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'General')
        db.execute("UPDATE notices SET title=?, content=?, category=? WHERE id=?", (title, content, category, id))
        db.commit()
        flash("Notice updated successfully!")
        return redirect(url_for('notifications'))
    return render_template('add_edit_notice.html', action='Edit', notice=notice)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required(role='admin')
def delete_notice(id):
    db = get_db()
    db.execute("DELETE FROM notices WHERE id=?", (id,))
    db.commit()
    flash("Notice deleted successfully!")
    return redirect(url_for('notifications'))

# -------- NEW ROUTES --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'student'
        
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            db.commit()
            flash("Registration Successful! Please Login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
            
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required()
def profile():
    if request.method == 'POST':
        flash("Profile updated (simulation)!")
        return redirect(url_for('profile'))
    return render_template('profile.html', user=session['user'], role=session['role'])

@app.route('/notice/<int:id>')
@login_required()
def notice_detail(id):
    db = get_db()
    notice = db.execute("SELECT * FROM notices WHERE id=?", (id,)).fetchone()
    if not notice:
        flash("Notice not found!")
        return redirect(url_for('home'))
    return render_template('notice_detail.html', notice=notice)

@app.route('/settings')
@login_required()
def settings():
    return render_template('settings.html')

@app.route('/search')
@login_required()
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        db = get_db()
        results = db.execute("SELECT * FROM notices WHERE title LIKE ? OR content LIKE ?", 
                           ('%'+query+'%', '%'+query+'%')).fetchall()
    return render_template('search.html', query=query, results=results)

@app.route('/events')
@login_required()
def events():
    db = get_db()
    events = db.execute("SELECT * FROM events ORDER BY date ASC").fetchall()
    return render_template('events.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required(role='admin')
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        db = get_db()
        db.execute("INSERT INTO events (title, description, date, location) VALUES (?, ?, ?, ?)", 
                   (title, description, date, location))
        db.commit()
        flash("Event added successfully!")
        return redirect(url_for('events'))
    return render_template('add_edit_event.html', action='Add')

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_event(id):
    db = get_db()
    event = db.execute("SELECT * FROM events WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        db.execute("UPDATE events SET title=?, description=?, date=?, location=? WHERE id=?", 
                   (title, description, date, location, id))
        db.commit()
        flash("Event updated successfully!")
        return redirect(url_for('events'))
    return render_template('add_edit_event.html', action='Edit', event=event)

@app.route('/delete_event/<int:id>', methods=['POST'])
@login_required(role='admin')
def delete_event(id):
    db = get_db()
    db.execute("DELETE FROM events WHERE id=?", (id,))
    db.commit()
    flash("Event deleted successfully!")
    return redirect(url_for('events'))

# ===================== ERP MODULES =====================

# -------- USER MANAGEMENT (Admin) --------
@app.route('/admin/users')
@login_required(role='admin')
def manage_users():
    db = get_db()
    users = db.execute("""
        SELECT id, username, email, role, created_at FROM users 
        ORDER BY created_at DESC
    """).fetchall()
    return render_template('manage_users.html', users=users)

@app.route('/admin/user/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                      (username, password, email, role))
            db.commit()
            flash(f"User '{username}' created successfully with password: {password}")
            print(f"[OK] User {username} created with role {role}")
            return redirect(url_for('manage_users'))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
    return render_template('add_user.html')

@app.route('/admin/user/<int:id>/reset-password', methods=['POST'])
@login_required(role='admin')
def reset_user_password(id):
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id=?", (id,)).fetchone()
    if user:
        new_password = user['username'] + '123'
        db.execute("UPDATE users SET password=? WHERE id=?", (new_password, id))
        db.commit()
        flash(f"Password reset to: {new_password}")
        print(f"[INFO] Password reset for user {id}")
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_user(id):
    if id == session.get('user_id'):
        flash("Cannot delete your own account!")
        return redirect(url_for('manage_users'))
    
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id=?", (id,)).fetchone()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    flash(f"User {user['username']} deleted!")
    return redirect(url_for('manage_users'))

# -------- STUDENT MANAGEMENT --------
@app.route('/admin/students')
@login_required(role='admin')
def manage_students():
    db = get_db()
    students = db.execute("""
        SELECT s.id, s.roll_no, s.full_name, s.semester, u.username, u.email, s.is_active
        FROM students s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.roll_no
    """).fetchall()
    return render_template('manage_students.html', students=students)

@app.route('/admin/student/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_student():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        roll_no = request.form['roll_no']
        full_name = request.form['full_name']
        phone = request.form['phone']
        semester = request.form['semester']
        
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                      (username, password, email, 'student'))
            db.commit()
            user_id = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()[0]
            db.execute("INSERT INTO students (user_id, roll_no, full_name, phone, semester) VALUES (?, ?, ?, ?, ?)",
                      (user_id, roll_no, full_name, phone, semester))
            db.commit()
            flash("Student added successfully!")
            return redirect(url_for('manage_students'))
        except sqlite3.IntegrityError as e:
            flash(f"Error: {str(e)}")
    return render_template('add_edit_student.html', action='Add')

@app.route('/admin/student/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_student(id):
    db = get_db()
    student = db.execute("""
        SELECT s.*, u.username, u.email
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE s.id=?
    """, (id,)).fetchone()
    
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        semester = request.form['semester']
        is_active = request.form.get('is_active', 0)
        
        db.execute("UPDATE students SET full_name=?, phone=?, semester=?, is_active=? WHERE id=?",
                  (full_name, phone, semester, is_active, id))
        db.commit()
        flash("Student updated successfully!")
        return redirect(url_for('manage_students'))
    return render_template('add_edit_student.html', action='Edit', student=student)

# -------- COURSE MANAGEMENT --------
@app.route('/admin/courses')
@login_required(role='admin')
def manage_courses():
    db = get_db()
    courses = db.execute("""
        SELECT c.*, u.username as faculty_name
        FROM courses c
        LEFT JOIN users u ON c.faculty_id = u.id
        ORDER BY c.semester, c.course_code
    """).fetchall()
    return render_template('manage_courses.html', courses=courses)

@app.route('/admin/course/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_course():
    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        credits = request.form['credits']
        semester = request.form['semester']
        section = request.form['section']
        faculty_id = request.form.get('faculty_id') or None
        description = request.form['description']
        
        db = get_db()
        
        # Check if faculty already has a course assigned
        if faculty_id:
            existing_course = db.execute(
                "SELECT id FROM courses WHERE faculty_id=?",
                (faculty_id,)
            ).fetchone()
            if existing_course:
                flash("This faculty already has a subject assigned! Each faculty can teach only one subject.")
                faculty_list = db.execute("""
                    SELECT u.id, u.username, c.course_name
                    FROM users u
                    LEFT JOIN courses c ON u.id = c.faculty_id
                    WHERE u.role='faculty'
                    ORDER BY u.username
                """).fetchall()
                return render_template('add_edit_course.html', action='Add', faculty=faculty_list)
        
        try:
            db.execute("""INSERT INTO courses (course_code, course_name, credits, semester, section, faculty_id, description)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (course_code, course_name, credits, semester, section, faculty_id, description))
            db.commit()
            flash("Course added successfully!")
            return redirect(url_for('manage_courses'))
        except sqlite3.IntegrityError:
            flash("Course code already exists!")
    
    db = get_db()
    # Get faculty with their assigned courses
    faculty_list = db.execute("""
        SELECT u.id, u.username, c.course_name
        FROM users u
        LEFT JOIN courses c ON u.id = c.faculty_id
        WHERE u.role='faculty'
        ORDER BY u.username
    """).fetchall()
    return render_template('add_edit_course.html', action='Add', faculty=faculty_list)

@app.route('/admin/course/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role='admin')
def edit_course(id):
    db = get_db()
    course = db.execute("SELECT * FROM courses WHERE id=?", (id,)).fetchone()
    
    if request.method == 'POST':
        course_name = request.form['course_name']
        credits = request.form['credits']
        semester = request.form['semester']
        section = request.form['section']
        new_faculty_id = request.form.get('faculty_id') or None
        description = request.form['description']
        
        # Check if faculty is being changed to someone who already has a course
        if new_faculty_id and new_faculty_id != course['faculty_id']:
            existing_course = db.execute(
                "SELECT id FROM courses WHERE faculty_id=? AND id != ?",
                (new_faculty_id, id)
            ).fetchone()
            if existing_course:
                flash("This faculty already has a subject assigned! Each faculty can teach only one subject.")
                faculty_list = db.execute("""
                    SELECT u.id, u.username, c.course_name
                    FROM users u
                    LEFT JOIN courses c ON u.id = c.faculty_id
                    WHERE u.role='faculty'
                    ORDER BY u.username
                """).fetchall()
                return render_template('add_edit_course.html', action='Edit', course=course, faculty=faculty_list)
        
        db.execute("""UPDATE courses SET course_name=?, credits=?, semester=?, section=?, faculty_id=?, description=?
                     WHERE id=?""",
                  (course_name, credits, semester, section, new_faculty_id, description, id))
        db.commit()
        flash("Course updated successfully!")
        return redirect(url_for('manage_courses'))
    
    # Get faculty with their assigned courses
    faculty_list = db.execute("""
        SELECT u.id, u.username, c.course_name
        FROM users u
        LEFT JOIN courses c ON u.id = c.faculty_id
        WHERE u.role='faculty'
        ORDER BY u.username
    """).fetchall()
    return render_template('add_edit_course.html', action='Edit', course=course, faculty=faculty_list)

@app.route('/admin/course/<int:id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_course(id):
    db = get_db()
    db.execute("DELETE FROM courses WHERE id=?", (id,))
    db.commit()
    flash("Course deleted successfully!")
    return redirect(url_for('manage_courses'))

# -------- ENROLLMENT MANAGEMENT --------
@app.route('/admin/enrollments')
@login_required(role='admin')
def manage_enrollments():
    db = get_db()
    enrollments = db.execute("""
        SELECT e.id, s.roll_no, s.full_name, c.course_code, c.course_name, e.enrolled_date
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY s.roll_no, c.course_code
    """).fetchall()
    return render_template('manage_enrollments.html', enrollments=enrollments)

@app.route('/admin/enrollment/add', methods=['GET', 'POST'])
@login_required(role='admin')
def add_enrollment():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        
        db = get_db()
        try:
            db.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                      (student_id, course_id))
            db.commit()
            flash("Enrollment added successfully!")
            return redirect(url_for('manage_enrollments'))
        except sqlite3.IntegrityError:
            flash("Student already enrolled in this course!")
    
    db = get_db()
    students = db.execute("SELECT id, roll_no, full_name FROM students ORDER BY roll_no").fetchall()
    courses = db.execute("SELECT id, course_code, course_name FROM courses ORDER BY course_code").fetchall()
    return render_template('add_edit_enrollment.html', action='Add', students=students, courses=courses)

@app.route('/admin/enrollment/<int:id>/delete', methods=['POST'])
@login_required(role='admin')
def delete_enrollment(id):
    db = get_db()
    db.execute("DELETE FROM enrollments WHERE id=?", (id,))
    db.commit()
    flash("Enrollment deleted successfully!")
    return redirect(url_for('manage_enrollments'))

# -------- ATTENDANCE MANAGEMENT --------
@app.route('/admin/attendance')
@login_required(role=['admin', 'faculty'])
def manage_attendance():
    db = get_db()
    course_id = request.args.get('course_id')
    attendance_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # If faculty, show only their courses
    if session['role'] == 'faculty':
        courses = db.execute(
            "SELECT id, course_code, course_name FROM courses WHERE faculty_id=? ORDER BY course_code",
            (session.get('user_id'),)
        ).fetchall()
    else:
        # Admin sees all courses
        courses = db.execute("SELECT id, course_code, course_name FROM courses ORDER BY course_code").fetchall()
    
    attendance_records = []
    if course_id:
        # Verify faculty can only access their own courses
        if session['role'] == 'faculty':
            course = db.execute(
                "SELECT id FROM courses WHERE id=? AND faculty_id=?",
                (course_id, session.get('user_id'))
            ).fetchone()
            if not course:
                flash("You can only manage attendance for your own courses!")
                return redirect(url_for('manage_attendance'))
        
        # Get all students enrolled in this course with their attendance status
        attendance_records = db.execute("""
            SELECT s.id as student_id, s.roll_no, s.full_name, 
                   COALESCE(a.status, 'Not Marked') as status, 
                   a.id as attendance_id, a.attendance_date
            FROM students s
            JOIN enrollments e ON s.id = e.student_id
            LEFT JOIN attendance a ON s.id = a.student_id AND a.course_id = ? AND a.attendance_date = ?
            WHERE e.course_id = ?
            ORDER BY s.roll_no
        """, (course_id, attendance_date, course_id)).fetchall()
    
    return render_template('manage_attendance.html', courses=courses, attendance_records=attendance_records,
                          selected_course=course_id, selected_date=attendance_date)

@app.route('/admin/attendance/mark', methods=['POST'])
@login_required(role=['admin', 'faculty'])
def mark_attendance():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    attendance_date = data.get('date')
    status = data.get('status')
    
    # Verify faculty can only mark attendance for their own courses
    if session['role'] == 'faculty':
        db = get_db()
        course = db.execute(
            "SELECT id FROM courses WHERE id=? AND faculty_id=?",
            (course_id, session.get('user_id'))
        ).fetchone()
        if not course:
            return jsonify({'success': False, 'error': 'Unauthorized'})
    
    db = get_db()
    try:
        # Check if record exists
        existing = db.execute(
            "SELECT id FROM attendance WHERE student_id=? AND course_id=? AND attendance_date=?",
            (student_id, course_id, attendance_date)
        ).fetchone()
        
        if existing:
            db.execute(
                "UPDATE attendance SET status=? WHERE student_id=? AND course_id=? AND attendance_date=?",
                (status, student_id, course_id, attendance_date)
            )
        else:
            db.execute(
                "INSERT INTO attendance (student_id, course_id, attendance_date, status) VALUES (?, ?, ?, ?)",
                (student_id, course_id, attendance_date, status)
            )
        
        db.commit()
        print(f"[OK] Attendance marked for student {student_id}: {status}")
        return jsonify({'success': True})
    except Exception as e:
        print(f"[ERROR] Attendance marking failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

# -------- GRADES MANAGEMENT --------
@app.route('/admin/grades')
@login_required(role=['admin', 'faculty'])
def manage_grades():
    db = get_db()
    course_id = request.args.get('course_id')
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    
    # If faculty, show only their courses
    if session['role'] == 'faculty':
        courses = db.execute(
            "SELECT id, course_code, course_name FROM courses WHERE faculty_id=? ORDER BY course_code",
            (user_id,)
        ).fetchall()
    else:
        # Admin sees all courses
        courses = db.execute("SELECT id, course_code, course_name FROM courses ORDER BY course_code").fetchall()
    
    grades = []
    
    if course_id:
        # Verify faculty can only access their own courses
        if session['role'] == 'faculty':
            course = db.execute(
                "SELECT id FROM courses WHERE id=? AND faculty_id=?",
                (course_id, user_id)
            ).fetchone()
            if not course:
                flash("You can only manage grades for your own courses!")
                return redirect(url_for('manage_grades'))
        
        grades = db.execute("""
            SELECT g.id, s.roll_no, s.full_name, g.marks_obtained, g.total_marks, g.grade
            FROM grades g
            JOIN students s ON g.student_id = s.id
            WHERE g.course_id=?
            ORDER BY s.roll_no
        """, (course_id,)).fetchall()
    
    return render_template('manage_grades.html', courses=courses, grades=grades, selected_course=course_id)

@app.route('/admin/grade/add', methods=['GET', 'POST'])
@login_required(role=['admin', 'faculty'])
def add_grade():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        marks = float(request.form['marks_obtained'])
        total_marks = float(request.form['total_marks'])
        
        percentage = (marks / total_marks) * 100
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 80:
            grade = 'A'
        elif percentage >= 70:
            grade = 'B'
        elif percentage >= 60:
            grade = 'C'
        elif percentage >= 50:
            grade = 'D'
        else:
            grade = 'F'
        
        db = get_db()
        try:
            db.execute("""INSERT INTO grades (student_id, course_id, marks_obtained, total_marks, grade)
                         VALUES (?, ?, ?, ?, ?)""",
                      (student_id, course_id, marks, total_marks, grade))
            db.commit()
            flash("Grade added successfully!")
            return redirect(url_for('manage_grades', course_id=course_id))
        except sqlite3.IntegrityError:
            flash("Grade already exists for this student-course pair!")
    
    db = get_db()
    students = db.execute("SELECT id, roll_no, full_name FROM students ORDER BY roll_no").fetchall()
    courses = db.execute("SELECT id, course_code, course_name FROM courses ORDER BY course_code").fetchall()
    return render_template('add_edit_grade.html', action='Add', students=students, courses=courses)

@app.route('/admin/grade/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role=['admin', 'faculty'])
def edit_grade(id):
    db = get_db()
    grade = db.execute("SELECT * FROM grades WHERE id=?", (id,)).fetchone()
    
    if request.method == 'POST':
        marks = float(request.form['marks_obtained'])
        total_marks = float(request.form['total_marks'])
        
        percentage = (marks / total_marks) * 100
        if percentage >= 90:
            grade_letter = 'A+'
        elif percentage >= 80:
            grade_letter = 'A'
        elif percentage >= 70:
            grade_letter = 'B'
        elif percentage >= 60:
            grade_letter = 'C'
        elif percentage >= 50:
            grade_letter = 'D'
        else:
            grade_letter = 'F'
        
        db.execute("""UPDATE grades SET marks_obtained=?, total_marks=?, grade=? WHERE id=?""",
                  (marks, total_marks, grade_letter, id))
        db.commit()
        flash("Grade updated successfully!")
        return redirect(url_for('manage_grades', course_id=grade['course_id']))
    
    return render_template('add_edit_grade.html', action='Edit', grade=grade)

# -------- SESSIONAL MARKS --------
@app.route('/faculty/sessional-marks')
@login_required(role='faculty')
def sessional_marks():
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    course_id = request.args.get('course_id')
    
    # Get faculty's courses
    courses = db.execute(
        "SELECT id, course_code, course_name, section FROM courses WHERE faculty_id=? ORDER BY course_code",
        (user_id,)
    ).fetchall()
    
    marks_data = []
    section = None
    
    if course_id:
        # Verify course belongs to faculty
        course = db.execute(
            "SELECT section FROM courses WHERE id=? AND faculty_id=?",
            (course_id, user_id)
        ).fetchone()
        if course:
            section = course['section']
            marks_data = db.execute("""
                SELECT sm.id, s.roll_no, s.full_name, sm.quiz_marks, sm.assignment_marks, 
                       sm.presentation_marks, sm.total_sessional
                FROM sessional_marks sm
                JOIN students s ON sm.student_id = s.id
                WHERE sm.course_id=?
                ORDER BY s.roll_no
            """, (course_id,)).fetchall()
    
    return render_template('faculty_sessional_marks.html', courses=courses, marks_data=marks_data, 
                          selected_course=course_id, section=section)

@app.route('/faculty/sessional-marks/add', methods=['GET', 'POST'])
@login_required(role='faculty')
def add_sessional_marks():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        quiz_marks = float(request.form.get('quiz_marks', 0))
        assignment_marks = float(request.form.get('assignment_marks', 0))
        presentation_marks = float(request.form.get('presentation_marks', 0))
        total_sessional = quiz_marks + assignment_marks + presentation_marks
        
        db = get_db()
        user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
        
        # Verify faculty owns this course
        course = db.execute(
            "SELECT section FROM courses WHERE id=? AND faculty_id=?",
            (course_id, user_id)
        ).fetchone()
        if not course:
            flash("Unauthorized!")
            return redirect(url_for('sessional_marks'))
        
        try:
            db.execute("""INSERT INTO sessional_marks (student_id, course_id, section, quiz_marks, 
                         assignment_marks, presentation_marks, total_sessional)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (student_id, course_id, course['section'], quiz_marks, assignment_marks, 
                       presentation_marks, total_sessional))
            db.commit()
            flash("Sessional marks added successfully!")
        except sqlite3.IntegrityError:
            flash("Marks already exist for this student!")
        
        return redirect(url_for('sessional_marks', course_id=course_id))
    
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    courses = db.execute(
        "SELECT id, course_code, course_name FROM courses WHERE faculty_id=?",
        (user_id,)
    ).fetchall()
    
    return render_template('add_sessional_marks.html', courses=courses)

# -------- PRE-TEST MARKS --------
@app.route('/faculty/pre-test-marks')
@login_required(role='faculty')
def pre_test_marks():
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    course_id = request.args.get('course_id')
    
    # Get faculty's courses
    courses = db.execute(
        "SELECT id, course_code, course_name, section FROM courses WHERE faculty_id=? ORDER BY course_code",
        (user_id,)
    ).fetchall()
    
    marks_data = []
    section = None
    
    if course_id:
        # Verify course belongs to faculty
        course = db.execute(
            "SELECT section FROM courses WHERE id=? AND faculty_id=?",
            (course_id, user_id)
        ).fetchone()
        if course:
            section = course['section']
            marks_data = db.execute("""
                SELECT ptm.id, s.roll_no, s.full_name, ptm.pre_test_marks, ptm.total_pre_test, ptm.remarks
                FROM pre_test_marks ptm
                JOIN students s ON ptm.student_id = s.id
                WHERE ptm.course_id=?
                ORDER BY s.roll_no
            """, (course_id,)).fetchall()
    
    return render_template('faculty_pre_test_marks.html', courses=courses, marks_data=marks_data,
                          selected_course=course_id, section=section)

@app.route('/faculty/pre-test-marks/add', methods=['GET', 'POST'])
@login_required(role='faculty')
def add_pre_test_marks():
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        pre_test_marks = float(request.form.get('pre_test_marks', 0))
        total_pre_test = float(request.form.get('total_pre_test', 10))
        remarks = request.form.get('remarks', '')
        
        db = get_db()
        user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
        
        # Verify faculty owns this course
        course = db.execute(
            "SELECT section FROM courses WHERE id=? AND faculty_id=?",
            (course_id, user_id)
        ).fetchone()
        if not course:
            flash("Unauthorized!")
            return redirect(url_for('pre_test_marks'))
        
        try:
            db.execute("""INSERT INTO pre_test_marks (student_id, course_id, section, pre_test_marks, 
                         total_pre_test, remarks)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (student_id, course_id, course['section'], pre_test_marks, total_pre_test, remarks))
            db.commit()
            flash("Pre-test marks added successfully!")
        except sqlite3.IntegrityError:
            flash("Pre-test marks already exist for this student!")
        
        return redirect(url_for('pre_test_marks', course_id=course_id))
    
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    courses = db.execute(
        "SELECT id, course_code, course_name FROM courses WHERE faculty_id=?",
        (user_id,)
    ).fetchall()
    
    return render_template('add_pre_test_marks.html', courses=courses)

# Exam Management (Faculty) - Beginner-friendly placeholder routes
@app.route('/faculty/exams/add', methods=['GET', 'POST'])
@login_required(role='faculty')
def add_exam():
    """Show form to add a new exam (placeholder)."""
    return '<h2>Add Exam (Coming Soon)</h2>'

@app.route('/faculty/exams/<int:exam_id>/marks')
@login_required(role='faculty')
def exam_marks(exam_id):
    """Show marks for a specific exam (placeholder)."""
    return f'<h2>Exam Marks (Coming Soon) for Exam ID: {exam_id}</h2>'

@app.route('/faculty/exams/<int:exam_id>/marks/add', methods=['GET', 'POST'])
@login_required(role='faculty')
def add_exam_marks(exam_id):
    """Show form to add marks for a specific exam (placeholder)."""
    return f'<h2>Add Exam Marks (Coming Soon) for Exam ID: {exam_id}</h2>'

@app.route('/student/dashboard')
@login_required(role='student')
def student_dashboard():
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    student = db.execute("SELECT * FROM students WHERE user_id=?", (user_id,)).fetchone()
    
    if not student:
        flash("Student profile not found!")
        return redirect(url_for('home'))
    
    courses = db.execute("""
        SELECT c.* FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.student_id=?
        ORDER BY c.semester
    """, (student['id'],)).fetchall()
    
    grades = db.execute("""
        SELECT g.*, c.course_code, c.course_name
        FROM grades g
        JOIN courses c ON g.course_id = c.id
        WHERE g.student_id=?
        ORDER BY c.course_code
    """, (student['id'],)).fetchall()
    
    attendance_summary = db.execute("""
        SELECT c.course_code, c.course_name,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absent,
               COUNT(*) as total
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id=?
        GROUP BY a.course_id
    """, (student['id'],)).fetchall()
    
    return render_template('student_dashboard.html', student=student, courses=courses,
                          grades=grades, attendance_summary=attendance_summary)

@app.route('/student/attendance')
@login_required(role='student')
def student_attendance():
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    student = db.execute("SELECT id FROM students WHERE user_id=?", (user_id,)).fetchone()
    
    attendance = db.execute("""
        SELECT a.*, c.course_code, c.course_name
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id=?
        ORDER BY a.attendance_date DESC
    """, (student['id'],)).fetchall()
    
    return render_template('student_attendance.html', attendance=attendance)

@app.route('/student/grades')
@login_required(role='student')
def student_grades():
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    student = db.execute("SELECT id FROM students WHERE user_id=?", (user_id,)).fetchone()
    
    grades = db.execute("""
        SELECT g.*, c.course_code, c.course_name
        FROM grades g
        JOIN courses c ON g.course_id = c.id
        WHERE g.student_id=?
        ORDER BY c.course_code
    """, (student['id'],)).fetchall()
    
    return render_template('student_grades.html', grades=grades)

# -------- FACULTY DASHBOARD --------
@app.route('/faculty/dashboard')
@login_required(role='faculty')
def faculty_dashboard():
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("Faculty profile not found!")
        return redirect(url_for('login'))
    
    courses = db.execute("SELECT * FROM courses WHERE faculty_id=? ORDER BY course_code", (user['id'],)).fetchall()
    
    student_count = db.execute("""
        SELECT COUNT(DISTINCT e.student_id) FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE c.faculty_id=?
    """, (user['id'],)).fetchone()[0]
    
    print(f"[INFO] Faculty {session['user']} accessed dashboard - {len(courses) if courses else 0} courses, {student_count} students")
    return render_template('faculty_dashboard.html', courses=courses, student_count=student_count)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/notifications')
@login_required()
def notifications():
    db = get_db()
    notices = db.execute("SELECT * FROM notices ORDER BY created_at DESC").fetchall()
    return render_template('notifications.html', notices=notices)

# Placeholder route for manage_exams to fix BuildError
@app.route('/faculty/exams', methods=['GET'])
@login_required(role='faculty')
def manage_exams():
    return '<h2>Faculty Exams Placeholder Page</h2><p>This page will be implemented soon.</p>'

# ----------------------------------------
# Run Flask app
# ----------------------------------------
if __name__ == '__main__':
    # Only initialize database if it does not exist
    if not os.path.exists(DB):
        print("[*] Initializing database...")
        init_db()
        with app.app_context():
            db = get_db()
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if tables:
                print(f"[OK] Tables created: {[t[0] for t in tables]}")
            else:
                print("[ERROR] No tables found!")
    print("[*] Starting Flask app...")
    app.run(debug=True)


