# ...existing code...

# ...existing code...
# ...existing code...
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
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
        identifier = request.form.get('identifier', '').strip()  # Can be roll_no or email
        password = request.form.get('password', '').strip()
        
        # Validate inputs
        if not identifier or not password:
            flash("Please enter Roll Number/Email and Password!", 'error')
            return render_template('login.html')
        
        db = get_db()
        # Query by roll_no OR email
        user = db.execute(
            "SELECT * FROM users WHERE roll_no = ? OR email = ?",
            (identifier, identifier)
        ).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()  # Clear old session
            session['user'] = user['username']
            session['user_id'] = user['id']
            session['role'] = user['role']
            session.permanent = True
            flash(f"Login Successful! Welcome {user['full_name']}!", 'success')
            print(f"[OK] User {user['username']} ({identifier}) logged in with role: {user['role']}")
            return redirect(url_for('home'))
        else:
            flash("Invalid Roll Number/Email or Password!", 'error')
            print(f"[ERROR] Login failed for identifier: {identifier}")
    
    return render_template('login.html')

# -------- REGISTER (STUDENT REGISTRATION) --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Secure student registration with comprehensive validation.
    
    Validations:
    - No empty fields allowed
    - Roll number must be unique
    - Email format validation
    - Mobile must be 10 digits
    - Password minimum 6 characters
    - Profile photo upload
    """
    import re
    from werkzeug.utils import secure_filename
    
    if request.method == 'POST':
        # Get all form fields
        full_name = request.form.get('full_name', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '').strip()
        semester = request.form.get('semester', '1')
        section = request.form.get('section', '').strip()  # Now accepts manual text input
        
        # Check all fields are provided
        required_fields = {
            'full_name': full_name,
            'roll_no': roll_no,
            'email': email,
            'mobile': mobile,
            'password': password,
            'semester': semester,
            'section': section
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            flash(error_msg, 'error')
            print(f"[ERROR] Registration failed - {error_msg}")
            return redirect(url_for('register'))
        
        # Validation: Email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash("Invalid email format! Please enter a valid email address.", 'error')
            print(f"[ERROR] Invalid email format: {email}")
            return redirect(url_for('register'))
        
        # Validation: Mobile number (exactly 10 digits)
        mobile_pattern = r'^\d{10}$'
        if not re.match(mobile_pattern, mobile):
            flash("Mobile number must be exactly 10 digits!", 'error')
            print(f"[ERROR] Invalid mobile number: {mobile}")
            return redirect(url_for('register'))
        
        # Validation: Password length (minimum 6 characters)
        if len(password) < 6:
            flash("Password must be at least 6 characters long!", 'error')
            print(f"[ERROR] Password too short for user: {full_name}")
            return redirect(url_for('register'))
        
        # Validation: Semester is valid (1-8)
        try:
            semester = int(semester)
            if semester < 1 or semester > 8:
                raise ValueError()
        except ValueError:
            flash("Semester must be between 1 and 8!", 'error')
            print(f"[ERROR] Invalid semester: {semester}")
            return redirect(url_for('register'))
        
        db = get_db()
        
        # Validation: Roll number uniqueness
        existing_roll = db.execute(
            "SELECT id FROM users WHERE roll_no = ?", 
            (roll_no,)
        ).fetchone()
        
        if existing_roll:
            flash("This roll number is already registered! Please use a different roll number.", 'error')
            print(f"[ERROR] Duplicate roll number: {roll_no}")
            return redirect(url_for('register'))
        
        # Validation: Email uniqueness (optional but recommended)
        existing_email = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        
        if existing_email:
            flash("This email is already registered! Please use a different email.", 'error')
            print(f"[ERROR] Duplicate email: {email}")
            return redirect(url_for('register'))
        
        # Handle profile photo upload
        photo_filename = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '':
                # Check file extension
                allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
                if '.' in file.filename:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    if ext in allowed_extensions:
                        # Generate secure filename with roll number
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        photo_filename = f"student_{roll_no}_{timestamp}.{ext}"
                        
                        # Create uploads directory if not exists
                        uploads_dir = os.path.join(app.static_folder, 'uploads')
                        if not os.path.exists(uploads_dir):
                            os.makedirs(uploads_dir)
                            print(f"[OK] Created uploads directory: {uploads_dir}")
                        
                        # Save file
                        file_path = os.path.join(uploads_dir, photo_filename)
                        file.save(file_path)
                        print(f"[OK] Profile photo saved: {photo_filename}")
                    else:
                        flash(f"Invalid file format! Allowed: {', '.join(allowed_extensions)}", 'error')
                        return redirect(url_for('register'))
                else:
                    flash("File without extension not allowed!", 'error')
                    return redirect(url_for('register'))
        
        # All validations passed - register the student
        try:
            photo_path = f"uploads/{photo_filename}" if photo_filename else None
            
            # Generate username from roll number
            username = f"student_{roll_no}"
            
            # Check if username already exists
            existing_username = db.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            
            if existing_username:
                # Use email as fallback username
                username = email.split('@')[0]
                counter = 1
                while db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
                    username = f"{email.split('@')[0]}{counter}"
                    counter += 1
            
            # Hash password before storing
            hashed_password = generate_password_hash(password)
            
            # Insert new user
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
            
            flash(f"Registration successful! You can now login with your Roll Number or Email.", 'success')
            print(f"[OK] New student registered - Roll: {roll_no}, Name: {full_name}, Username: {username}")
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError as e:
            db.rollback()
            flash("Registration failed! Please check your information and try again.", 'error')
            print(f"[ERROR] Database integrity error: {e}")
            return redirect(url_for('register'))
        except Exception as e:
            db.rollback()
            flash(f"Registration failed: {str(e)}", 'error')
            print(f"[ERROR] Registration error: {e}")
            import traceback
            traceback.print_exc()
            return redirect(url_for('register'))
    
    # GET request - show registration form
    return render_template('register_student.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot Password - Step 1: Email Input
    
    User enters their email address.
    System generates OTP and sends it via email.
    """
    import random
    from services.email_service import send_otp_email
    
    # Clear session on GET to show password reset page
    if request.method == 'GET' and 'user' in session:
        session.clear()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        # Validate email not empty
        if not email:
            flash("Please enter your email address!", 'error')
            print(f"[ERROR] Forgot password attempt - empty email")
            return redirect(url_for('forgot_password'))
        
        db = get_db()
        
        # Check if email exists in database
        user = db.execute(
            "SELECT id, username, full_name FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        
        if not user:
            # For security, don't reveal if email exists
            flash("If this email is registered, you will receive an OTP shortly.", 'info')
            print(f"[WARN] Forgot password attempt for non-existent email: {email}")
            return redirect(url_for('login'))
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Calculate OTP expiry (5 minutes from now)
        from datetime import datetime, timedelta
        otp_expiry = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Save OTP to database
        try:
            db.execute(
                "UPDATE users SET otp = ?, otp_expiry = ? WHERE email = ?",
                (otp, otp_expiry, email)
            )
            db.commit()
            print(f"[OK] OTP generated for email {email}: {otp} (expires at {otp_expiry})")
        except Exception as e:
            db.rollback()
            flash("Error generating OTP. Please try again.", 'error')
            print(f"[ERROR] Failed to save OTP: {e}")
            return redirect(url_for('forgot_password'))
        
        # Send OTP via email
        email_sent = send_otp_email(email, otp, validity_minutes=5)
        
        if email_sent:
            flash("OTP has been sent to your email. Please check your inbox (and spam folder).", 'success')
            print(f"[OK] OTP email sent successfully to {email}")
            
            # Store email in session for next step
            session['reset_email'] = email
            session['reset_full_name'] = user['full_name']
            
            return redirect(url_for('verify_otp'))
        else:
            # Email sending failed - still ask user to enter OTP
            flash("OTP generated but email sending failed. You may need to check settings.", 'warning')
            print(f"[WARN] Email sending failed for {email}, but OTP was created")
            
            session['reset_email'] = email
            session['reset_full_name'] = user['full_name']
            
            return redirect(url_for('verify_otp'))
    
    return render_template('forgot_password.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """
    Forgot Password - Step 2: OTP Verification
    
    User enters the OTP received via email.
    System verifies OTP validity and expiry.
    """
    from datetime import datetime
    
    # Check if user came from forgot-password route
    if 'reset_email' not in session:
        flash("Please start the password reset process from 'Forgot Password'.", 'warning')
        return redirect(url_for('forgot_password'))
    
    reset_email = session.get('reset_email')
    reset_full_name = session.get('reset_full_name', 'User')
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        
        # Validate OTP input
        if not entered_otp:
            flash("Please enter the OTP!", 'error')
            print(f"[ERROR] OTP verification attempt - empty OTP")
            return redirect(url_for('verify_otp'))
        
        # Validate OTP format (6 digits)
        if not entered_otp.isdigit() or len(entered_otp) != 6:
            flash("OTP must be 6 digits!", 'error')
            print(f"[ERROR] Invalid OTP format: {entered_otp}")
            return redirect(url_for('verify_otp'))
        
        db = get_db()
        
        # Get user and verify OTP
        user = db.execute(
            "SELECT id, otp, otp_expiry FROM users WHERE email = ?",
            (reset_email,)
        ).fetchone()
        
        if not user:
            flash("User not found. Please restart password reset.", 'error')
            print(f"[ERROR] User not found for email: {reset_email}")
            session.pop('reset_email', None)
            session.pop('reset_full_name', None)
            return redirect(url_for('forgot_password'))
        
        # Check if OTP is set
        if not user['otp']:
            flash("No OTP found. Please request a new OTP.", 'error')
            print(f"[ERROR] No OTP in database for {reset_email}")
            return redirect(url_for('forgot_password'))
        
        # Check if OTP matches
        if user['otp'] != entered_otp:
            flash("Incorrect OTP! Please try again.", 'error')
            print(f"[ERROR] OTP mismatch for {reset_email}: expected {user['otp']}, got {entered_otp}")
            return redirect(url_for('verify_otp'))
        
        # Check if OTP has expired
        otp_expiry = datetime.strptime(user['otp_expiry'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > otp_expiry:
            flash("OTP has expired! Please request a new OTP.", 'error')
            print(f"[ERROR] OTP expired for {reset_email} (expired at {otp_expiry})")
            
            # Clear used OTP from database
            db.execute(
                "UPDATE users SET otp = NULL, otp_expiry = NULL WHERE email = ?",
                (reset_email,)
            )
            db.commit()
            
            session.pop('reset_email', None)
            session.pop('reset_full_name', None)
            return redirect(url_for('forgot_password'))
        
        # OTP is valid!
        flash("OTP verified successfully! Now set your new password.", 'success')
        print(f"[OK] OTP verified successfully for {reset_email}")
        
        # Mark OTP verification in session (don't clear OTP yet, will clear after password reset)
        session['otp_verified'] = True
        
        return redirect(url_for('reset_password'))
    
    return render_template('verify_otp.html', reset_email=reset_email, reset_full_name=reset_full_name)


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Forgot Password - Step 3: Password Reset
    
    User sets a new password after OTP verification.
    """
    # Check if OTP was verified
    if not session.get('otp_verified'):
        flash("Please verify your OTP first!", 'warning')
        return redirect(url_for('forgot_password'))
    
    if 'reset_email' not in session:
        flash("Invalid session. Please start password reset again.", 'error')
        return redirect(url_for('forgot_password'))
    
    reset_email = session.get('reset_email')
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate inputs
        if not new_password or not confirm_password:
            flash("Please fill in all fields!", 'error')
            print(f"[ERROR] Password reset - missing fields")
            return redirect(url_for('reset_password'))
        
        # Check if passwords match
        if new_password != confirm_password:
            flash("Passwords do not match!", 'error')
            print(f"[ERROR] Password mismatch for {reset_email}")
            return redirect(url_for('reset_password'))
        
        # Validate password length
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long!", 'error')
            print(f"[ERROR] Password too short for {reset_email}")
            return redirect(url_for('reset_password'))
        
        # Prevent password same as username
        db = get_db()
        user = db.execute(
            "SELECT username FROM users WHERE email = ?",
            (reset_email,)
        ).fetchone()
        
        if user and new_password == user['username']:
            flash("Password cannot be the same as your username!", 'error')
            print(f"[ERROR] Password same as username for {reset_email}")
            return redirect(url_for('reset_password'))
        
        # Update password and clear OTP
        try:
            db.execute(
                "UPDATE users SET password = ?, otp = NULL, otp_expiry = NULL WHERE email = ?",
                (new_password, reset_email)
            )
            db.commit()
            
            flash("Password reset successfully! You can now login with your new password.", 'success')
            print(f"[OK] Password reset successfully for {reset_email}")
            
            # Clear session
            session.pop('reset_email', None)
            session.pop('reset_full_name', None)
            session.pop('otp_verified', None)
            
            return redirect(url_for('login'))
            
        except Exception as e:
            db.rollback()
            flash("Error updating password. Please try again.", 'error')
            print(f"[ERROR] Failed to update password: {e}")
            return redirect(url_for('reset_password'))
    
    return render_template('reset_password.html', reset_email=reset_email)


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
@app.route('/profile', methods=['GET', 'POST'])
@login_required()
def profile():
    """
    Student Profile Page - Display and edit student details
    
    GET: Display student profile with all details
    POST: Update mobile number and/or profile photo
    """
    import re
    from werkzeug.utils import secure_filename
    from werkzeug.security import generate_password_hash, check_password_hash
    
    db = get_db()
    user_id = session.get('user_id')
    
    # Fetch current user data
    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    
    if not user:
        flash("User not found!", 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        action = request.form.get('action', '').strip()
        
        # Action 1: Update Password
        if action == 'update_password':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validations
            if not current_password or not new_password or not confirm_password:
                flash("All password fields are required!", 'error')
                return redirect(url_for('profile'))
            
            # Verify current password
            if not check_password_hash(user['password'], current_password):
                flash("Current password is incorrect!", 'error')
                print(f"[ERROR] Wrong current password for user {user['username']}")
                return redirect(url_for('profile'))
            
            # Check new passwords match
            if new_password != confirm_password:
                flash("New passwords do not match!", 'error')
                return redirect(url_for('profile'))
            
            # Validate password length
            if len(new_password) < 6:
                flash("Password must be at least 6 characters long!", 'error')
                return redirect(url_for('profile'))
            
            # Check if new password is same as username
            if new_password == user['username']:
                flash("Password cannot be the same as username!", 'error')
                return redirect(url_for('profile'))
            
            # Hash and update password
            hashed_password = generate_password_hash(new_password)
            db.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            db.commit()
            flash("Password updated successfully!", 'success')
            print(f"[OK] Password updated for user {user['username']}")
            return redirect(url_for('profile'))
        
        # Action 2: Update Mobile Number
        elif action == 'update_mobile':
            mobile = request.form.get('mobile', '').strip()
            
            # Validations
            if not mobile:
                flash("Mobile number is required!", 'error')
                return redirect(url_for('profile'))
            
            mobile_pattern = r'^\d{10}$'
            if not re.match(mobile_pattern, mobile):
                flash("Mobile number must be exactly 10 digits!", 'error')
                return redirect(url_for('profile'))
            
            db.execute(
                "UPDATE users SET mobile = ? WHERE id = ?",
                (mobile, user_id)
            )
            db.commit()
            flash("Mobile number updated successfully!", 'success')
            print(f"[OK] Mobile number updated for user {user['username']}")
            return redirect(url_for('profile'))
        
        # Action 3: Update Profile Photo
        elif action == 'update_photo':
            if 'profile_photo' not in request.files:
                flash("No file provided!", 'error')
                return redirect(url_for('profile'))
            
            file = request.files['profile_photo']
            if file.filename == '':
                flash("No file selected!", 'error')
                return redirect(url_for('profile'))
            
            # Check file extension
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
            if '.' in file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower()
                if ext not in allowed_extensions:
                    flash(f"Invalid file format! Allowed: {', '.join(allowed_extensions)}", 'error')
                    return redirect(url_for('profile'))
            else:
                flash("File without extension not allowed!", 'error')
                return redirect(url_for('profile'))
            
            # Generate secure filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            photo_filename = f"student_{user['roll_no']}_{timestamp}.{ext}"
            
            # Create uploads directory if not exists
            uploads_dir = os.path.join(app.static_folder, 'uploads')
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
                print(f"[OK] Created uploads directory: {uploads_dir}")
            
            # Save file
            file_path = os.path.join(uploads_dir, photo_filename)
            file.save(file_path)
            print(f"[OK] Profile photo updated: {photo_filename}")
            
            # Update database
            photo_path = f"uploads/{photo_filename}"
            db.execute(
                "UPDATE users SET photo = ? WHERE id = ?",
                (photo_path, user_id)
            )
            db.commit()
            flash("Profile photo updated successfully!", 'success')
            return redirect(url_for('profile'))
    
    # GET request - display profile
    return render_template('profile.html', user=user, role=session.get('role'))

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

# -------- MARKS MANAGEMENT (Replacing Grades) --------
@app.route('/admin/marks')
@login_required(role=['admin', 'faculty'])
def manage_marks():
    """Manage marks for all students by course"""
    db = get_db()
    course_id = request.args.get('course_id')
    exam_type = request.args.get('exam_type', 'ST1')
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
    
    marks = []
    exam_types = ['ST1', 'ST2', 'PUT']
    
    if course_id:
        # Verify faculty can only access their own courses
        if session['role'] == 'faculty':
            course = db.execute(
                "SELECT id FROM courses WHERE id=? AND faculty_id=?",
                (course_id, user_id)
            ).fetchone()
            if not course:
                flash("You can only manage marks for your own courses!")
                return redirect(url_for('manage_marks'))
        
        marks = db.execute("""
            SELECT m.id, m.exam_type, s.roll_no, s.full_name, m.max_marks, m.obtained_marks,
                   ROUND((m.obtained_marks / m.max_marks) * 100, 2) as percentage
            FROM marks m
            JOIN students s ON m.student_id = s.id
            WHERE m.course_id=? AND m.exam_type=?
            ORDER BY s.roll_no
        """, (course_id, exam_type)).fetchall()
    
    return render_template('manage_marks.html', courses=courses, marks=marks, 
                          selected_course=course_id, exam_types=exam_types, 
                          selected_exam_type=exam_type)

@app.route('/admin/marks/add', methods=['GET', 'POST'])
@login_required(role=['admin', 'faculty'])
def add_marks_entry():
    """Add marks for a student in a course"""
    if request.method == 'POST':
        student_id = request.form['student_id']
        course_id = request.form['course_id']
        exam_type = request.form['exam_type']
        max_marks = float(request.form['max_marks'])
        obtained_marks = float(request.form['obtained_marks'])
        
        if obtained_marks > max_marks:
            flash("Obtained marks cannot exceed max marks!")
            return redirect(url_for('add_marks_entry'))
        
        db = get_db()
        try:
            db.execute("""INSERT INTO marks (student_id, course_id, exam_type, max_marks, obtained_marks)
                         VALUES (?, ?, ?, ?, ?)""",
                      (student_id, course_id, exam_type, max_marks, obtained_marks))
            db.commit()
            flash(f"Marks added successfully for {exam_type}!")
            return redirect(url_for('manage_marks', course_id=course_id, exam_type=exam_type))
        except sqlite3.IntegrityError:
            flash(f"Marks already exist for this student-course-exam pair!")
    
    db = get_db()
    students = db.execute("SELECT id, roll_no, full_name FROM students ORDER BY roll_no").fetchall()
    courses = db.execute("SELECT id, course_code, course_name FROM courses ORDER BY course_code").fetchall()
    exam_types = ['ST1', 'ST2', 'PUT']
    return render_template('add_edit_marks_entry.html', action='Add', students=students, 
                          courses=courses, exam_types=exam_types)

@app.route('/admin/marks/<int:id>/edit', methods=['GET', 'POST'])
@login_required(role=['admin', 'faculty'])
def edit_marks_entry(id):
    """Edit existing marks"""
    db = get_db()
    mark = db.execute("SELECT * FROM marks WHERE id=?", (id,)).fetchone()
    
    if not mark:
        flash("Mark record not found!")
        return redirect(url_for('manage_marks'))
    
    if request.method == 'POST':
        max_marks = float(request.form['max_marks'])
        obtained_marks = float(request.form['obtained_marks'])
        
        if obtained_marks > max_marks:
            flash("Obtained marks cannot exceed max marks!")
            return redirect(url_for('edit_marks_entry', id=id))
        
        db.execute("""UPDATE marks SET max_marks=?, obtained_marks=? WHERE id=?""",
                  (max_marks, obtained_marks, id))
        db.commit()
        flash("Marks updated successfully!")
        return redirect(url_for('manage_marks', course_id=mark['course_id'], exam_type=mark['exam_type']))
    
    return render_template('add_edit_marks_entry.html', action='Edit', mark=mark, 
                          exam_types=['ST1', 'ST2', 'PUT'])

@app.route('/admin/marks/<int:id>/delete', methods=['POST'])
@login_required(role=['admin', 'faculty'])
def delete_marks_entry(id):
    """Delete marks entry"""
    db = get_db()
    mark = db.execute("SELECT * FROM marks WHERE id=?", (id,)).fetchone()
    
    if not mark:
        flash("Mark record not found!")
        return redirect(url_for('manage_marks'))
    
    db.execute("DELETE FROM marks WHERE id=?", (id,))
    db.commit()
    flash("Marks deleted successfully!")
    return redirect(url_for('manage_marks', course_id=mark['course_id'], exam_type=mark['exam_type']))

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
    
    # Get marks for all enrolled courses
    marks = db.execute("""
        SELECT m.*, c.course_code, c.course_name
        FROM marks m
        JOIN courses c ON m.course_id = c.id
        WHERE m.student_id=?
        ORDER BY c.course_code, 
                 CASE WHEN m.exam_type='ST1' THEN 1 
                      WHEN m.exam_type='ST2' THEN 2 
                      WHEN m.exam_type='PUT' THEN 3 ELSE 4 END
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
                          marks=marks, attendance_summary=attendance_summary)

@app.route('/student/attendance')
@login_required(role='student')
def student_attendance():
    from datetime import datetime
    db = get_db()
    user_id = session.get('user_id')
    
    # If user_id not in session, fetch from database
    if not user_id:
        user_row = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
        if user_row:
            user_id = user_row[0]
            session['user_id'] = user_id
    
    # Fetch student information
    student_info = db.execute("""
        SELECT s.full_name, s.roll_no, s.section, s.semester, s.created_at
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE u.id = ?
    """, (user_id,)).fetchone()
    
    if not student_info:
        return render_template('student_attendance.html', 
                             student_info={}, 
                             daily_attendance=[], 
                             summary={})
    
    student_data = {
        'full_name': student_info['full_name'],
        'roll_no': student_info['roll_no'],
        'section': student_info['section'] or 'N/A',
        'semester': student_info['semester'],
        'registration_date': student_info['created_at'].split()[0] if student_info['created_at'] else 'N/A'
    }
    
    # Fetch all attendance records for the logged-in user
    attendance_records = db.execute("""
        SELECT date, subject, status
        FROM attendance_records
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,)).fetchall()
    
    # Convert to list of dicts
    records = [dict(row) for row in attendance_records]
    
    if not records:
        return render_template('student_attendance.html', 
                             student_info=student_data, 
                             daily_attendance=[], 
                             summary={})
    
    # Period mapping - map subjects to periods (I-VIII + Lunch)
    periods = ['I', 'II', 'III', 'IV', 'Lunch', 'V', 'VI', 'VII', 'VIII']
    
    # Get unique subjects and map to periods
    all_subjects = sorted(set(r['subject'] for r in records))
    subject_to_period = {}
    for idx, subject in enumerate(all_subjects):
        subject_to_period[subject] = periods[idx % len(periods)]
    
    # Group by date
    from collections import defaultdict
    attendance_by_date = defaultdict(list)
    for record in records:
        attendance_by_date[record['date']].append(record)
    
    # Sort dates in descending order
    sorted_dates = sorted(attendance_by_date.keys(), reverse=True)
    
    # Calculate statistics for each date
    daily_attendance = []
    for date_str in sorted_dates:
        day_records = attendance_by_date[date_str]
        
        # Calculate day name
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        day_name = date_obj.strftime('%A')
        
        # Create attendance dict for this date
        date_data = {
            'date': date_str,
            'day': day_name,
            'periods': {}  # Will store period -> (subject, status) mapping
        }
        
        # Initialize all periods with empty
        for period in periods:
            date_data['periods'][period] = None
        
        # Fill in actual records
        present_count = 0
        for record in day_records:
            subject = record['subject']
            period = subject_to_period.get(subject, 'I')
            status = record['status']
            date_data['periods'][period] = {
                'subject': subject,
                'status': status
            }
            if status == 'Present':
                present_count += 1
        
        total_lectures = len(day_records)
        percentage = (present_count / total_lectures * 100) if total_lectures > 0 else 0
        
        date_data['present'] = present_count
        date_data['total'] = total_lectures
        date_data['percentage'] = round(percentage, 2)
        
        daily_attendance.append(date_data)
    
    # Calculate overall summary
    total_classes = len(records)
    total_present = sum(1 for r in records if r['status'] == 'Present')
    total_absent = sum(1 for r in records if r['status'] == 'Absent')
    total_leave = sum(1 for r in records if r['status'] == 'Leave')
    overall_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
    
    summary = {
        'total_classes': total_classes,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_leave': total_leave,
        'overall_percentage': round(overall_percentage, 2)
    }
    
    return render_template('student_attendance.html', 
                         student_info=student_data,
                         periods=periods,
                         daily_attendance=daily_attendance,
                         summary=summary)

@app.route('/student/marks')
@login_required(role='student')
def student_marks():
    """Student views their marks grouped by subject and exam type"""
    db = get_db()
    user_id = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()[0]
    student = db.execute("SELECT id FROM students WHERE user_id=?", (user_id,)).fetchone()
    
    if not student:
        flash("Student profile not found!")
        return redirect(url_for('login'))
    
    # Get all marks for this student with course info
    marks_data = db.execute("""
        SELECT m.id, m.exam_type, m.max_marks, m.obtained_marks,
               ROUND((m.obtained_marks / m.max_marks) * 100, 2) as percentage,
               c.id as course_id, c.course_code, c.course_name
        FROM marks m
        JOIN courses c ON m.course_id = c.id
        WHERE m.student_id=?
        ORDER BY c.course_code, 
                 CASE WHEN m.exam_type='ST1' THEN 1 
                      WHEN m.exam_type='ST2' THEN 2 
                      WHEN m.exam_type='PUT' THEN 3 ELSE 4 END
    """, (student['id'],)).fetchall()
    
    # Group marks by course
    courses_marks = {}
    for mark in marks_data:
        course_key = (mark['course_id'], mark['course_code'], mark['course_name'])
        if course_key not in courses_marks:
            courses_marks[course_key] = {'ST1': None, 'ST2': None, 'PUT': None}
        courses_marks[course_key][mark['exam_type']] = mark
    
    # Calculate overall stats
    total_marks = 0
    total_obtained = 0
    for mark in marks_data:
        total_marks += mark['max_marks']
        total_obtained += mark['obtained_marks']
    
    overall_percentage = round((total_obtained / total_marks * 100), 2) if total_marks > 0 else 0
    
    return render_template('student_marks.html', courses_marks=courses_marks, 
                          overall_percentage=overall_percentage, total_subjects=len(courses_marks))

@app.route('/student/grades')
@login_required(role='student')
def student_grades():
    """Redirect to student_marks for backward compatibility"""
    return redirect(url_for('student_marks'))

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


# -------- FACULTY STUDENT MANAGEMENT --------
@app.route('/faculty/students')
@login_required(role='faculty')
def faculty_view_students():
    """
    Faculty view: Display all students from their assigned section.
    
    Security: Faculty can only see students from their own section.
    """
    db = get_db()
    
    # Get current faculty's section
    faculty = db.execute(
        "SELECT id, full_name, section FROM users WHERE username = ? AND role = 'faculty'",
        (session['user'],)
    ).fetchone()
    
    if not faculty:
        flash("Faculty profile not found!", 'error')
        return redirect(url_for('login'))
    
    faculty_section = faculty['section']
    
    if not faculty_section:
        flash("No section assigned to your account. Contact administrator.", 'warning')
        return render_template('faculty_students.html', students=[], faculty_name=faculty['full_name'], section=None)
    
    # Get all students in the same section
    students = db.execute("""
        SELECT id, full_name, roll_no, email, mobile, semester, section, photo, created_at
        FROM users
        WHERE role = 'student' AND section = ?
        ORDER BY roll_no ASC
    """, (faculty_section,)).fetchall()
    
    print(f"[OK] Faculty {session['user']} viewed {len(students) if students else 0} students in section {faculty_section}")
    
    return render_template(
        'faculty_students.html',
        students=students,
        faculty_name=faculty['full_name'],
        section=faculty_section
    )


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

# ========================================
# FACULTY TEACHING SUBJECTS MANAGEMENT
# ========================================

@app.route('/faculty/subjects', methods=['GET'])
@login_required(role='faculty')
def view_subjects():
    """Faculty views their own teaching subjects"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    subjects = db.execute("""
        SELECT * FROM subjects 
        WHERE faculty_id = ? 
        ORDER BY subject_code ASC
    """, (user['id'],)).fetchall()
    
    return render_template('faculty_subjects.html', subjects=subjects)


@app.route('/faculty/subject/add', methods=['GET', 'POST'])
@login_required(role='faculty')
def add_subject():
    """Faculty adds a new teaching subject"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        subject_code = request.form.get('subject_code', '').strip()
        description = request.form.get('description', '').strip()
        semester = request.form.get('semester', '1')
        credits = request.form.get('credits', '4')
        
        if not subject_name or not subject_code:
            flash("Subject name and code are required!", 'error')
            return render_template('add_edit_subject.html', mode='add')
        
        try:
            db.execute("""
                INSERT INTO subjects (faculty_id, subject_name, subject_code, description, semester, credits)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user['id'], subject_name, subject_code, description, semester, credits))
            db.commit()
            flash(f"Subject '{subject_name}' added successfully!", 'success')
            print(f"[INFO] Faculty {session['user']} added subject {subject_code}")
            return redirect(url_for('view_subjects'))
        
        except sqlite3.IntegrityError:
            flash("Subject code already exists! Use a unique code.", 'error')
            return render_template('add_edit_subject.html', mode='add')
        except Exception as e:
            flash(f"Error adding subject: {str(e)}", 'error')
            return render_template('add_edit_subject.html', mode='add')
    
    return render_template('add_edit_subject.html', mode='add')


@app.route('/faculty/subject/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required(role='faculty')
def edit_subject(subject_id):
    """Faculty edits their own subject"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Verify subject belongs to this faculty
    subject = db.execute("""
        SELECT * FROM subjects 
        WHERE id = ? AND faculty_id = ?
    """, (subject_id, user['id'])).fetchone()
    
    if not subject:
        flash("Subject not found or unauthorized access!", 'error')
        return redirect(url_for('view_subjects'))
    
    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        description = request.form.get('description', '').strip()
        semester = request.form.get('semester', '1')
        credits = request.form.get('credits', '4')
        
        if not subject_name:
            flash("Subject name is required!", 'error')
            return render_template('add_edit_subject.html', mode='edit', subject=subject)
        
        try:
            db.execute("""
                UPDATE subjects 
                SET subject_name=?, description=?, semester=?, credits=?
                WHERE id=? AND faculty_id=?
            """, (subject_name, description, semester, credits, subject_id, user['id']))
            db.commit()
            flash(f"Subject updated successfully!", 'success')
            print(f"[INFO] Faculty {session['user']} updated subject {subject_id}")
            return redirect(url_for('view_subjects'))
        
        except Exception as e:
            flash(f"Error updating subject: {str(e)}", 'error')
            return render_template('add_edit_subject.html', mode='edit', subject=subject)
    
    return render_template('add_edit_subject.html', mode='edit', subject=subject)


@app.route('/faculty/subject/delete/<int:subject_id>', methods=['POST'])
@login_required(role='faculty')
def delete_subject(subject_id):
    """Faculty deletes their own subject"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Verify subject belongs to this faculty
    subject = db.execute("""
        SELECT * FROM subjects 
        WHERE id = ? AND faculty_id = ?
    """, (subject_id, user['id'])).fetchone()
    
    if not subject:
        flash("Subject not found or unauthorized access!", 'error')
        return redirect(url_for('view_subjects'))
    
    try:
        subject_code = subject['subject_code']
        db.execute("DELETE FROM subjects WHERE id=? AND faculty_id=?", (subject_id, user['id']))
        db.commit()
        flash(f"Subject '{subject_code}' deleted successfully!", 'success')
        print(f"[INFO] Faculty {session['user']} deleted subject {subject_id}")
    except Exception as e:
        flash(f"Error deleting subject: {str(e)}", 'error')
    
    return redirect(url_for('view_subjects'))


# ========================================
# FACULTY ATTENDANCE MANAGEMENT
# ========================================

@app.route('/faculty/attendance', methods=['GET'])
@login_required(role='faculty')
def faculty_mark_attendance():
    """Faculty marks attendance for their subjects"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Get all subjects taught by this faculty
    subjects = db.execute("""
        SELECT * FROM subjects 
        WHERE faculty_id = ? 
        ORDER BY subject_code
    """, (user['id'],)).fetchall()
    
    # Get all students (can filter by enrolled students if needed)
    students = db.execute("""
        SELECT DISTINCT s.id, s.full_name, s.roll_no, s.semester, s.section
        FROM students s
        WHERE s.is_active = 1
        ORDER BY s.full_name
    """).fetchall()
    
    # Get today's attendance records for this faculty
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    attendance_records = db.execute("""
        SELECT * FROM faculty_attendance 
        WHERE faculty_id = ? AND attendance_date = ?
        ORDER BY student_id, subject_id
    """, (user['id'], today)).fetchall()
    
    return render_template('faculty_attendance.html', 
                         subjects=subjects, 
                         students=students,
                         attendance_records=attendance_records,
                         today=today)


@app.route('/faculty/attendance/save', methods=['POST'])
@login_required(role='faculty')
def save_attendance():
    """Save attendance marked by faculty"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login')), 401
    
    data = request.get_json()
    attendance_date = data.get('attendance_date')
    records = data.get('records', [])
    
    if not attendance_date or not records:
        return {'success': False, 'message': 'Invalid data'}, 400
    
    try:
        for record in records:
            student_id = record.get('student_id')
            subject_id = record.get('subject_id')
            status = record.get('status')
            remarks = record.get('remarks', '')
            
            # Verify subject belongs to this faculty
            subject = db.execute("""
                SELECT id FROM subjects 
                WHERE id = ? AND faculty_id = ?
            """, (subject_id, user['id'])).fetchone()
            
            if not subject:
                continue  # Skip if not authorized
            
            # Insert or update attendance
            db.execute("""
                INSERT OR REPLACE INTO faculty_attendance 
                (faculty_id, student_id, subject_id, attendance_date, status, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user['id'], student_id, subject_id, attendance_date, status, remarks))
        
        db.commit()
        print(f"[INFO] Faculty {session['user']} saved attendance for {len(records)} records on {attendance_date}")
        return {'success': True, 'message': 'Attendance saved successfully'}, 200
    
    except Exception as e:
        print(f"[ERROR] Error saving attendance: {str(e)}")
        return {'success': False, 'message': f'Error: {str(e)}'}, 500


@app.route('/faculty/attendance/view', methods=['GET'])
@login_required(role='faculty')
def view_attendance():
    """Faculty views attendance records"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Get filter parameters
    subject_id = request.args.get('subject_id', type=int)
    student_id = request.args.get('student_id', type=int)
    
    # Base query - only show attendance for this faculty's subjects
    query = """
        SELECT fa.*, s.subject_code, st.full_name, st.roll_no
        FROM faculty_attendance fa
        JOIN subjects s ON fa.subject_id = s.id
        JOIN students st ON fa.student_id = st.id
        WHERE s.faculty_id = ?
    """
    params = [user['id']]
    
    if subject_id:
        query += " AND fa.subject_id = ?"
        params.append(subject_id)
    
    if student_id:
        query += " AND fa.student_id = ?"
        params.append(student_id)
    
    query += " ORDER BY fa.attendance_date DESC, st.full_name"
    
    attendance_records = db.execute(query, params).fetchall()
    
    # Get subjects and students for filtering
    subjects = db.execute("""
        SELECT id, subject_code, subject_name FROM subjects 
        WHERE faculty_id = ? 
        ORDER BY subject_code
    """, (user['id'],)).fetchall()
    
    students = db.execute("""
        SELECT DISTINCT st.id, st.full_name, st.roll_no
        FROM students st
        JOIN faculty_attendance fa ON st.id = fa.student_id
        JOIN subjects s ON fa.subject_id = s.id
        WHERE s.faculty_id = ?
        ORDER BY st.full_name
    """, (user['id'],)).fetchall()
    
    return render_template('faculty_view_attendance.html',
                         attendance_records=attendance_records,
                         subjects=subjects,
                         students=students,
                         selected_subject=subject_id,
                         selected_student=student_id)


# ========================================
# FACULTY MARKS MANAGEMENT
# ========================================

@app.route('/faculty/marks', methods=['GET'])
@login_required(role='faculty')
def view_marks():
    """Faculty views marks they've entered"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Get filter parameters
    subject_id = request.args.get('subject_id', type=int)
    exam_type = request.args.get('exam_type', '')
    
    # Base query
    query = """
        SELECT fm.*, s.subject_code, s.subject_name, st.full_name, st.roll_no
        FROM faculty_marks fm
        JOIN subjects s ON fm.subject_id = s.id
        JOIN students st ON fm.student_id = st.id
        WHERE s.faculty_id = ?
    """
    params = [user['id']]
    
    if subject_id:
        query += " AND fm.subject_id = ?"
        params.append(subject_id)
    
    if exam_type:
        query += " AND fm.exam_type = ?"
        params.append(exam_type)
    
    query += " ORDER BY s.subject_code, st.full_name"
    
    marks_records = db.execute(query, params).fetchall()
    
    # Get subjects for filtering
    subjects = db.execute("""
        SELECT id, subject_code, subject_name FROM subjects 
        WHERE faculty_id = ? 
        ORDER BY subject_code
    """, (user['id'],)).fetchall()
    
    exam_types = ['Sessional', 'Assignment', 'Quiz', 'Final']
    
    return render_template('faculty_marks.html',
                         marks_records=marks_records,
                         subjects=subjects,
                         exam_types=exam_types,
                         selected_subject=subject_id,
                         selected_exam_type=exam_type)


@app.route('/faculty/marks/add', methods=['GET', 'POST'])
@login_required(role='faculty')
def add_marks():
    """Faculty adds marks for students"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Get faculty's subjects
    subjects = db.execute("""
        SELECT id, subject_code, subject_name FROM subjects 
        WHERE faculty_id = ? 
        ORDER BY subject_code
    """, (user['id'],)).fetchall()
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        student_id = request.form.get('student_id', type=int)
        exam_type = request.form.get('exam_type', 'Sessional')
        max_marks = request.form.get('max_marks', type=float) or 100
        obtained_marks = request.form.get('obtained_marks', type=float) or 0
        remarks = request.form.get('remarks', '').strip()
        
        # Verify subject belongs to this faculty
        subject = db.execute("""
            SELECT id FROM subjects 
            WHERE id = ? AND faculty_id = ?
        """, (subject_id, user['id'])).fetchone()
        
        if not subject:
            flash("Invalid subject or unauthorized access!", 'error')
            return redirect(url_for('add_marks'))
        
        if obtained_marks > max_marks:
            flash("Obtained marks cannot be greater than max marks!", 'error')
            return render_template('add_edit_marks.html', mode='add', subjects=subjects)
        
        try:
            # Insert or replace marks
            db.execute("""
                INSERT OR REPLACE INTO faculty_marks 
                (faculty_id, student_id, subject_id, exam_type, max_marks, obtained_marks, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user['id'], student_id, subject_id, exam_type, max_marks, obtained_marks, remarks))
            db.commit()
            flash(f"Marks added successfully!", 'success')
            print(f"[INFO] Faculty {session['user']} added marks for student {student_id}")
            return redirect(url_for('view_marks'))
        
        except Exception as e:
            flash(f"Error adding marks: {str(e)}", 'error')
            return render_template('add_edit_marks.html', mode='add', subjects=subjects)
    
    # Get all students for selection
    students = db.execute("""
        SELECT id, full_name, roll_no, semester, section FROM students 
        WHERE is_active = 1 
        ORDER BY full_name
    """).fetchall()
    
    exam_types = ['Sessional', 'Assignment', 'Quiz', 'Final']
    
    return render_template('add_edit_marks.html', 
                         mode='add', 
                         subjects=subjects, 
                         students=students,
                         exam_types=exam_types)


@app.route('/faculty/marks/edit/<int:mark_id>', methods=['GET', 'POST'])
@login_required(role='faculty')
def edit_marks(mark_id):
    """Faculty edits marks"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Verify mark belongs to this faculty's subject
    mark = db.execute("""
        SELECT fm.* FROM faculty_marks fm
        JOIN subjects s ON fm.subject_id = s.id
        WHERE fm.id = ? AND s.faculty_id = ?
    """, (mark_id, user['id'])).fetchone()
    
    if not mark:
        flash("Mark record not found or unauthorized access!", 'error')
        return redirect(url_for('view_marks'))
    
    if request.method == 'POST':
        max_marks = request.form.get('max_marks', type=float) or 100
        obtained_marks = request.form.get('obtained_marks', type=float) or 0
        remarks = request.form.get('remarks', '').strip()
        
        if obtained_marks > max_marks:
            flash("Obtained marks cannot be greater than max marks!", 'error')
            return render_template('add_edit_marks.html', mode='edit', mark=mark)
        
        try:
            db.execute("""
                UPDATE faculty_marks 
                SET max_marks=?, obtained_marks=?, remarks=?
                WHERE id=? AND faculty_id=?
            """, (max_marks, obtained_marks, remarks, mark_id, user['id']))
            db.commit()
            flash("Marks updated successfully!", 'success')
            print(f"[INFO] Faculty {session['user']} updated marks {mark_id}")
            return redirect(url_for('view_marks'))
        
        except Exception as e:
            flash(f"Error updating marks: {str(e)}", 'error')
            return render_template('add_edit_marks.html', mode='edit', mark=mark)
    
    # Get subjects and students for display
    subjects = db.execute("""
        SELECT id, subject_code, subject_name FROM subjects 
        WHERE faculty_id = ? 
        ORDER BY subject_code
    """, (user['id'],)).fetchall()
    
    students = db.execute("""
        SELECT id, full_name, roll_no FROM students 
        WHERE is_active = 1 
        ORDER BY full_name
    """).fetchall()
    
    exam_types = ['Sessional', 'Assignment', 'Quiz', 'Final']
    
    return render_template('add_edit_marks.html', 
                         mode='edit', 
                         mark=mark,
                         subjects=subjects,
                         students=students,
                         exam_types=exam_types)


@app.route('/faculty/marks/delete/<int:mark_id>', methods=['POST'])
@login_required(role='faculty')
def delete_marks(mark_id):
    """Faculty deletes marks"""
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
    
    if not user:
        flash("User profile not found!")
        return redirect(url_for('login'))
    
    # Verify mark belongs to this faculty's subject
    mark = db.execute("""
        SELECT fm.* FROM faculty_marks fm
        JOIN subjects s ON fm.subject_id = s.id
        WHERE fm.id = ? AND s.faculty_id = ?
    """, (mark_id, user['id'])).fetchone()
    
    if not mark:
        flash("Mark record not found or unauthorized access!", 'error')
        return redirect(url_for('view_marks'))
    
    try:
        db.execute("DELETE FROM faculty_marks WHERE id=? AND faculty_id=?", (mark_id, user['id']))
        db.commit()
        flash("Marks deleted successfully!", 'success')
        print(f"[INFO] Faculty {session['user']} deleted marks {mark_id}")
    except Exception as e:
        flash(f"Error deleting marks: {str(e)}", 'error')
    
    return redirect(url_for('view_marks'))


# ========================================
# STUDENT SIDE - VIEW MARKS & ATTENDANCE
# ========================================

@app.route('/student/marks', methods=['GET'])
@login_required(role='student')
def student_view_marks():
    """Students view their marks"""
    db = get_db()
    user_id = session.get('user_id')
    
    if not user_id:
        user_row = db.execute("SELECT id FROM users WHERE username=?", (session['user'],)).fetchone()
        if user_row:
            user_id = user_row[0]
            session['user_id'] = user_id
    
    # Get student profile
    student = db.execute("""
        SELECT id, full_name, roll_no FROM students 
        WHERE user_id = ?
    """, (user_id,)).fetchone()
    
    if not student:
        flash("Student profile not found!")
        return redirect(url_for('login'))
    
    # Get marks for this student
    marks = db.execute("""
        SELECT fm.*, s.subject_code, s.subject_name, u.username as faculty_name
        FROM faculty_marks fm
        JOIN subjects s ON fm.subject_id = s.id
        JOIN users u ON s.faculty_id = u.id
        WHERE fm.student_id = ?
        ORDER BY s.subject_code, fm.exam_type
    """, (student['id'],)).fetchall()
    
    return render_template('student_marks.html', marks=marks, student=student)

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


