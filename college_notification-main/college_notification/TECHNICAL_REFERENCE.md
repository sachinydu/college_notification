# TECHNICAL REFERENCE: ROLE-BASED AUTHENTICATION

## CODE REFERENCE GUIDE

---

## 1. LOGIN LOGIC

### Current Implementation (app.py, lines 101-152)

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type', '').strip()  # 'employee' or 'student'
        identifier = request.form.get('identifier', '').strip()  # Email/Roll/Mobile/Username
        password = request.form.get('password', '').strip()
        
        if not user_type or not identifier or not password:
            flash("Please select user type and enter credentials!", 'error')
            return render_template('login.html')
        
        if user_type not in ['employee', 'student']:
            flash("Invalid user type selected!", 'error')
            return render_template('login.html')
        
        db = get_db()
        # Search by any identifier
        user = db.execute(
            "SELECT * FROM users WHERE roll_no = ? OR email = ? OR mobile = ? OR username = ?",
            (identifier, identifier, identifier, identifier)
        ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            # Validate role matches user_type
            allowed_roles = []
            if user_type == 'employee':
                allowed_roles = ['admin', 'faculty']
            elif user_type == 'student':
                allowed_roles = ['student']
            
            if user['role'] not in allowed_roles:
                flash(f"Access denied!", 'error')
                return render_template('login.html')
            
            # Create session
            session.clear()
            session['user'] = user['username']
            session['user_id'] = user['id']
            session['role'] = user['role']
            session.permanent = True
            
            flash(f"Login Successful!", 'success')
            return redirect(url_for('home'))  # Redirects based on role
        else:
            flash("Invalid credentials!", 'error')
    
    return render_template('login.html')
```

---

## 2. ROLE-BASED REDIRECT

### Home Route (app.py, lines 90-98)

```python
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session['role'] == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    else:
        # Student dashboard
        db = get_db()
        recent_notices = db.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()
        upcoming_events = db.execute("SELECT * FROM events ORDER BY date ASC LIMIT 5").fetchall()
        return render_template('student_home.html', notices=recent_notices, events=upcoming_events)
```

**Output**:
- Admin → `/admin` (admin_dashboard)
- Faculty → `/faculty/dashboard` (faculty_dashboard)
- Student → `/student/dashboard` (student_home.html)

---

## 3. ADD FACULTY ROUTE

### Implementation (app.py, lines 1078-1165)

```python
@app.route('/admin/add-faculty', methods=['GET', 'POST'])
@login_required(role='admin')
def add_faculty():
    """Admin-only route to add faculty members"""
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        subject = request.form.get('subject', '').strip()
        department = request.form.get('department', '').strip()
        
        # Validate required fields
        required_fields = {
            'full_name': full_name,
            'email': email,
            'password': password,
            'subject': subject,
            'department': department
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            flash(f"Missing: {', '.join(missing_fields)}", 'error')
            return redirect(url_for('add_faculty'))
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash("Invalid email format!", 'error')
            return redirect(url_for('add_faculty'))
        
        # Password length validation
        if len(password) < 6:
            flash("Password must be at least 6 characters!", 'error')
            return redirect(url_for('add_faculty'))
        
        db = get_db()
        
        # Check email uniqueness
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("Email already registered!", 'error')
            return redirect(url_for('add_faculty'))
        
        # Generate username from email
        username = email.split('@')[0].lower()
        
        # Ensure username uniqueness
        counter = 1
        original_username = username
        while db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        try:
            # Insert user with role='faculty'
            db.execute("""
                INSERT INTO users (
                    username, password, email, full_name, 
                    role, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username, hashed_password, email, full_name,
                'faculty', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            user_id = db.lastrowid
            
            # Insert into faculty table
            cursor = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='faculty'"
            ).fetchone()
            
            if cursor:
                db.execute("""
                    INSERT INTO faculty (user_id, subject, department, created_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, subject, department, 
                      datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            db.commit()
            
            flash(f"Faculty created! Username: {username}, Password: {password}", 'success')
            return redirect(url_for('manage_users'))
            
        except sqlite3.IntegrityError as e:
            db.rollback()
            flash("Error creating faculty!", 'error')
    
    return render_template('add_faculty.html')
```

---

## 4. STUDENT REGISTRATION

### Implementation (app.py, lines 153-312)

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Secure student registration with comprehensive validation"""
    
    if request.method == 'POST':
        # Get all form fields
        full_name = request.form.get('full_name', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '').strip()
        semester = request.form.get('semester', '1')
        section = request.form.get('section', '').strip()
        
        # Check all fields
        required_fields = {
            'full_name': full_name,
            'roll_no': roll_no,
            'email': email,
            'mobile': mobile,
            'password': password,
            'semester': semester,
            'section': section
        }
        
        missing = [f for f, v in required_fields.items() if not v]
        if missing:
            flash(f"Missing: {', '.join(missing)}", 'error')
            return redirect(url_for('register'))
        
        # Validation: Email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash("Invalid email!", 'error')
            return redirect(url_for('register'))
        
        # Validation: Mobile (10 digits)
        if not re.match(r'^\d{10}$', mobile):
            flash("Mobile must be exactly 10 digits!", 'error')
            return redirect(url_for('register'))
        
        # Validation: Password length
        if len(password) < 6:
            flash("Password min 6 chars!", 'error')
            return redirect(url_for('register'))
        
        # Validation: Semester (1-8)
        try:
            semester = int(semester)
            if semester < 1 or semester > 8:
                raise ValueError()
        except ValueError:
            flash("Semester must be 1-8!", 'error')
            return redirect(url_for('register'))
        
        db = get_db()
        
        # Check roll number uniqueness
        if db.execute("SELECT id FROM users WHERE roll_no = ?", (roll_no,)).fetchone():
            flash("Roll number already registered!", 'error')
            return redirect(url_for('register'))
        
        # Check email uniqueness
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            flash("Email already registered!", 'error')
            return redirect(url_for('register'))
        
        # Handle profile photo
        photo_filename = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower()
                if ext in {'jpg', 'jpeg', 'png', 'gif'}:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    photo_filename = f"student_{roll_no}_{timestamp}.{ext}"
                    
                    uploads_dir = os.path.join(app.static_folder, 'uploads')
                    os.makedirs(uploads_dir, exist_ok=True)
                    
                    file.save(os.path.join(uploads_dir, photo_filename))
        
        try:
            # Generate username
            username = f"student_{roll_no}"
            
            if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                username = email.split('@')[0]
                counter = 1
                while db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                    username = f"{email.split('@')[0]}{counter}"
                    counter += 1
            
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert user with role='student' (hard-coded)
            photo_path = f"uploads/{photo_filename}" if photo_filename else None
            
            db.execute("""
                INSERT INTO users (
                    username, password, email, full_name, roll_no, 
                    mobile, semester, section, photo, role, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                username, hashed_password, email, full_name, 
                roll_no, mobile, semester, section, photo_path, 'student',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            db.commit()
            
            flash("Registration successful! You can now login.", 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.rollback()
            flash(f"Registration failed: {str(e)}", 'error')
            return redirect(url_for('register'))
    
    return render_template('register_student.html')
```

---

## 5. LOGIN DECORATOR

### Implementation (app.py, lines 68-88)

```python
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
                        flash(f"You need to be {role}!")
                        return redirect(url_for('login'))
                else:
                    if session.get('role') != role:
                        flash(f"You need to be {role}!")
                        return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### Usage Examples

```python
# Admin only
@app.route('/admin')
@login_required(role='admin')
def admin_dashboard():
    pass

# Admin or Faculty
@app.route('/attendance/mark', methods=['POST'])
@login_required(role=['admin', 'faculty'])
def mark_attendance():
    pass

# Any authenticated user
@app.route('/profile')
@login_required()
def user_profile():
    pass
```

---

## 6. MIGRATION SCRIPT

### Faculty Table Creation (migrate_add_faculty_table.py)

```python
def migrate_add_faculty_table():
    """Create faculty table"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='faculty'"
    )
    if cursor.fetchone():
        print("[INFO] Faculty table already exists")
        return True
    
    # Create faculty table
    cursor.execute("""
        CREATE TABLE faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            subject TEXT,
            department TEXT,
            qualification TEXT,
            experience_years INTEGER DEFAULT 0,
            specialization TEXT,
            office_hours TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Migrate existing faculty users
    cursor.execute("SELECT id FROM users WHERE role = 'faculty'")
    faculty_users = cursor.fetchall()
    
    for user_id, in faculty_users:
        cursor.execute(
            "INSERT INTO faculty (user_id, subject, department) VALUES (?, ?, ?)",
            (user_id, 'Unknown', 'Unknown')
        )
    
    conn.commit()
    conn.close()
    
    print("[OK] Faculty table created!")
    return True
```

---

## 7. DEFAULT USER SETUP

### insert_default_users.py (Key Changes)

```python
users = [
    {
        'username': 'admin',
        'email': 'admin@erp.com',           # ← CHANGED from admin@college.edu
        'password_plain': 'admin123',       # ← Unchanged
        'role': 'admin',
        'full_name': 'System Administrator',
        'mobile': '9000000001',
        'section': 'Admin'
    },
    # ... other users
]

for user in users:
    hashed_password = generate_password_hash(user['password_plain'])
    
    cursor.execute("""
        INSERT INTO users (username, password, email, role, full_name, mobile, section)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user['username'], hashed_password, user['email'], user['role'],
          user['full_name'], user['mobile'], user['section']))
```

---

## 8. FORM VALIDATION REGEX

```python
# Email validation
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Mobile validation (10 digits)
mobile_pattern = r'^\d{10}$'

# Username validation (if needed)
username_pattern = r'^[a-zA-Z0-9_]{3,20}$'
```

---

## 9. FLOW DIAGRAMS

### Login Flow
```
Entry: /login
  ↓
User Type Selected?
  ├─ Employee → Check role in [admin, faculty]
  ├─ Student → Check role is 'student'
  └─ Invalid → Error & Redirect
  ↓
Find User by Identifier
  ├─ roll_no
  ├─ email
  ├─ mobile
  └─ username
  ↓
Password Match?
  ├─ No → Error & Redirect
  └─ Yes ↓
Role Validation
  ├─ Pass → Create Session
  └─ Fail → Error & Redirect
  ↓
Session Created
  session['user'] = username
  session['user_id'] = id
  session['role'] = role
  ↓
Redirect to /home
  ↓
Home Route Redirect
  ├─ admin → /admin
  ├─ faculty → /faculty/dashboard
  └─ student → /student/dashboard
```

### Registration Flow
```
Entry: /register
  ↓
Form Submitted?
  ├─ No → Show Form
  └─ Yes ↓
All Fields Present?
  ├─ No → Error & Redirect
  └─ Yes ↓
Validate Email Format
  ├─ No → Error & Redirect
  └─ Yes ↓
Validate Mobile (10 digits)
  ├─ No → Error & Redirect
  └─ Yes ↓
Password >= 6 chars?
  ├─ No → Error & Redirect
  └─ Yes ↓
Semester Valid (1-8)?
  ├─ No → Error & Redirect
  └─ Yes ↓
Check Uniqueness
  ├─ roll_no exists? → Error & Redirect
  ├─ email exists? → Error & Redirect
  └─ No ↓
Hash Password
  ↓
Insert User with role='student' (hard-coded)
  ↓
Success → Redirect to /login
```

---

## 10. SECURITY CHECKLIST

```
✅ Passwords hashed with Werkzeug
✅ Session tokens generated
✅ SQL injection prevention (parameterized queries)
✅ Email format validation
✅ Role validation on every protected route
✅ Unique email enforcement
✅ Unique roll number enforcement (students)
✅ Password minimum length (6 chars)
✅ File upload type validation
✅ Role-based access control on all routes
```

---

## INTEGRATION POINTS

### Required Database Tables
- users (core authentication)
- faculty (faculty-specific data)

### Required Session Variables
- session['user'] - username
- session['user_id'] - numeric ID
- session['role'] - admin/faculty/student

### Required Templates
- login.html
- register_student.html  
- add_faculty.html
- admin_dashboard.html
- faculty_dashboard.html
- student_home.html

### Required Routes
- /login (public)
- /register (public)
- /logout (authenticated)
- /admin/add-faculty (admin only)
- /admin/** (admin only)
- /faculty/** (faculty only)
- /student/** (student only)

---

**End of Technical Reference** 📚
