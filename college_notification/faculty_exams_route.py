from flask import render_template, request, redirect, url_for, session, flash
from app import app, get_db, login_required

@app.route('/faculty/exams', methods=['GET'])
@login_required(role='faculty')
def manage_exams():
    db = get_db()
    user_id = session['user_id']
    course_id = request.args.get('course_id', type=int)
    # Get faculty's courses
    courses = db.execute(
        "SELECT id, course_name, course_code FROM courses WHERE faculty_id=? ORDER BY course_name",
        (user_id,)
    ).fetchall()
    exams = []
    if course_id:
        # Verify course belongs to faculty
        course = db.execute(
            "SELECT id FROM courses WHERE id=? AND faculty_id=?",
            (course_id, user_id)
        ).fetchone()
        if course:
            exams = db.execute(
                "SELECT id, exam_name, max_marks, created_at FROM exams WHERE course_id=? ORDER BY created_at DESC",
                (course_id,)
            ).fetchall()
        else:
            flash("Unauthorized!")
            return redirect(url_for('manage_exams'))
    return render_template('faculty_exams.html', courses=courses, exams=exams, course_id=course_id)
