import os
import io
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import pypdf

from config import Config
from models import (
    init_db, create_user, verify_user_login, get_user_by_id,
    save_student_assessment, get_student_by_id,
    get_student_by_roll, get_all_students, get_tpo_summary_stats,
    record_quiz_result, get_users_by_status, update_user_status, get_approval_stats,
    delete_user_by_id, delete_student_by_id, get_all_users_detailed
)
from analyzer import PlacementReadinessAnalyzer
from ml_engine import ml_engine
from quiz_bank import get_questions_by_category, QUESTION_BANK
from sample_data import seed_sample_students_if_empty

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database & seed initial records on startup
with app.app_context():
    init_db()
    seed_sample_students_if_empty()

# ----------------- AUTHENTICATION DECORATORS -----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash("Please sign in with your student or administrative account to access this section.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_role = session.get('user_role')
        if not session.get('user_id'):
            flash("The TPO Dashboard requires administrative officer authentication. Please log in as an administrator.", "warning")
            return redirect(url_for('admin_login', next=request.url))
        if user_role != 'admin':
            flash("Access Restricted: The TPO Dashboard is strictly reserved for Placement Officers and College Administrators.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ----------------- AUTHENTICATION ROUTES -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))

    next_url = request.args.get('next') or request.form.get('next') or ''

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user, err = verify_user_login(email, password)
        if err:
            flash(err, "danger")
            return render_template('login.html', next_url=next_url)

        # Set session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']

        flash(f"Welcome back, {user['name']}! You have successfully signed in.", "success")
        
        # If admin logged in via standard login, allow them to navigate
        if user['role'] == 'admin' and next_url and 'tpo' in next_url:
            return redirect(url_for('tpo_dashboard'))
        if next_url and next_url != request.url and 'admin' not in next_url:
            return redirect(next_url)
        return redirect(url_for('index'))

    return render_template('login.html', next_url=next_url)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    next_url = request.args.get('next') or request.form.get('next') or ''

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user, err = verify_user_login(email, password)
        if err:
            flash(err, "danger")
            return render_template('admin_login.html', next_url=next_url)

        if user['role'] != 'admin':
            flash("Access Denied: This portal is exclusively for Training & Placement Officers (TPO). Student accounts cannot access the admin portal.", "danger")
            return render_template('admin_login.html', next_url=next_url)

        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']

        flash("Administrator authenticated successfully. Welcome to the TPO Batch Dashboard.", "success")
        return redirect(url_for('tpo_dashboard'))

    return render_template('admin_login.html', next_url=next_url)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        department = request.form.get('department', '').strip()
        roll_no = request.form.get('roll_no', '').strip()

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template('signup.html')

        res = create_user(
            name=name,
            email=email,
            password=password,
            role='student',
            department=department,
            roll_no=roll_no
        )

        if not res['success']:
            flash(res['error'], "danger")
            return render_template('signup.html')

        # User Signup -> TPO Approval Flow:
        # Accounts are created with status='pending'. They must be approved by TPO before login.
        flash("Registration submitted successfully! Your account is currently pending approval by the Training & Placement Officer (TPO). Once approved, you will be able to log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))


# ----------------- MAIN PORTAL ROUTES -----------------
@app.route('/')
def index():
    # Home page is accessible without login
    stats = get_tpo_summary_stats()
    return render_template('index.html', stats=stats)

@app.route('/assess', methods=['GET', 'POST'])
@login_required
def assess():
    if request.method == 'POST':
        try:
            form = request.form
            student_data = {
                'name': form.get('name', session.get('user_name', 'Student')).strip(),
                'roll_no': form.get('roll_no', 'N/A').strip(),
                'email': form.get('email', session.get('user_email', '')).strip(),
                'department': form.get('department', 'Computer Science'),
                'year': int(form.get('year', 4)),
                'cgpa': float(form.get('cgpa', 7.5)),
                'backlogs': int(form.get('backlogs', 0)),
                'target_role': form.get('target_role', 'Software Development Engineer'),
                'dsa_problems': int(form.get('dsa_problems', 0)),
                'dsa_rating': float(form.get('dsa_rating', 3)),
                'prog_rating': float(form.get('prog_rating', 3)),
                'db_rating': float(form.get('db_rating', 3)),
                'cs_core_rating': float(form.get('cs_core_rating', 3)),
                'projects_count': int(form.get('projects_count', 1)),
                'internship_months': int(form.get('internship_months', 0)),
                'hackathons': int(form.get('hackathons', 0)),
                'certifications': int(form.get('certifications', 0)),
                'has_github': 'has_github' in form,
                'has_live_deployment': 'has_live_deployment' in form,
                'aptitude_score': float(form.get('aptitude_score', 65)),
                'comm_rating': float(form.get('comm_rating', 3)),
                'interview_confidence': float(form.get('interview_confidence', 3)),
                'leadership_exp': 'leadership_exp' in form,
                'mock_interviews_done': int(form.get('mock_interviews_done', 0))
            }

            # 1. Calculate 5-Pillar Scores and Placement Readiness Index (PRI)
            pri_calc = PlacementReadinessAnalyzer.calculate_pri(student_data)
            student_data.update(pri_calc)

            # 2. Run Machine Learning Model Forecast
            ml_pred = ml_engine.predict(student_data)
            student_data['expected_ctc_min'] = ml_pred['expected_ctc_min']
            student_data['expected_ctc_max'] = ml_pred['expected_ctc_max']
            student_data['placement_prob'] = ml_pred['placement_probability']

            # 3. Save into SQLite
            student_id = save_student_assessment(student_data)

            flash(f"Assessment complete! Your Placement Readiness Index is {student_data['pri_score']} / 100 ({student_data['tier']}).", "success")
            return redirect(url_for('view_report', student_id=student_id))

        except Exception as e:
            flash(f"Error processing assessment: {str(e)}", "danger")
            return redirect(url_for('assess'))

    return render_template('assess.html')

@app.route('/report/<int:student_id>')
@login_required
def view_report(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash("Student profile not found.", "warning")
        return redirect(url_for('students_list'))

    profile = student.get('profile', {})
    
    # 1. Radar Benchmark & Fitment
    role_analysis = PlacementReadinessAnalyzer.analyze_role_fitment(profile)
    
    # 2. Skill Gaps & 30-Day Preparation Roadmap
    pri_info = {
        'pri_score': student['pri_score'],
        'tier': student['tier']
    }
    gaps_and_roadmap = PlacementReadinessAnalyzer.identify_skill_gaps_and_roadmap(profile, pri_info)

    return render_template(
        'report.html',
        student=student,
        role_analysis=role_analysis,
        gaps_and_roadmap=gaps_and_roadmap
    )

@app.route('/quiz')
@login_required
def quiz():
    category = request.args.get('category', 'All')
    questions = get_questions_by_category(category, limit=12)
    return render_template(
        'quiz.html',
        questions=questions,
        selected_category=category,
        total_count=len(QUESTION_BANK)
    )

@app.route('/resume_matcher', methods=['GET', 'POST'])
@login_required
def resume_matcher():
    match_result = None
    target_role = "Software Development Engineer"
    resume_text = ""
    custom_jd = ""
    uploaded_pdf_name = None

    if request.method == 'POST':
        target_role = request.form.get('target_role', 'Software Development Engineer')
        custom_jd = request.form.get('custom_jd', '')
        resume_text = request.form.get('resume_text', '')

        # Check if user uploaded a PDF file
        pdf_file = request.files.get('resume_pdf')
        if pdf_file and pdf_file.filename:
            if pdf_file.filename.lower().endswith('.pdf'):
                try:
                    pdf_bytes = pdf_file.read()
                    pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                    extracted_pages = []
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_pages.append(page_text)
                    
                    pdf_extracted_text = "\n".join(extracted_pages).strip()
                    if pdf_extracted_text:
                        resume_text = pdf_extracted_text
                        uploaded_pdf_name = pdf_file.filename
                        flash(f"Successfully extracted text from '{pdf_file.filename}' ({len(pdf_reader.pages)} page(s)).", "success")
                    else:
                        flash("PDF was uploaded, but no selectable text was found (it may be a scanned image). Please paste text manually.", "warning")
                except Exception as e:
                    flash(f"Error reading PDF file: {str(e)}", "danger")
            else:
                flash("Invalid file format. Please upload a PDF file (.pdf).", "danger")

        if resume_text.strip():
            match_result = PlacementReadinessAnalyzer.match_resume_to_jd(
                resume_text=resume_text,
                target_role=target_role,
                custom_jd=custom_jd
            )
        else:
            if request.method == 'POST' and not uploaded_pdf_name:
                flash("Please upload a PDF resume or paste resume text to analyze.", "warning")

    return render_template(
        'resume_matcher.html',
        match_result=match_result,
        target_role=target_role,
        resume_text=resume_text,
        custom_jd=custom_jd,
        uploaded_pdf_name=uploaded_pdf_name
    )

@app.route('/tpo')
@admin_required
def tpo_dashboard():
    # Only authenticated admin / TPO can access this
    filter_dept = request.args.get('department', 'All')
    filter_tier = request.args.get('tier', 'All')
    search = request.args.get('search', '').strip()

    students = get_all_students(filter_dept=filter_dept, filter_tier=filter_tier, search=search)
    stats = get_tpo_summary_stats()
    
    # TPO Approval Workflow data
    pending_students = get_users_by_status('pending')
    approval_stats = get_approval_stats()
    all_users = get_all_users_detailed('student')

    return render_template(
        'tpo_dashboard.html',
        students=students,
        stats=stats,
        pending_students=pending_students,
        approval_stats=approval_stats,
        all_users=all_users,
        selected_dept=filter_dept,
        selected_tier=filter_tier,
        search_query=search
    )

@app.route('/tpo/add_student', methods=['POST'])
@admin_required
def tpo_add_student():
    try:
        form = request.form
        name = form.get('name', '').strip()
        email = form.get('email', '').strip()
        roll_no = form.get('roll_no', '').strip()
        password = form.get('password', 'Campus@123').strip() or 'Campus@123'
        department = form.get('department', 'Computer Science').strip()
        cgpa = float(form.get('cgpa', 7.5))
        backlogs = int(form.get('backlogs', 0))
        target_role = form.get('target_role', 'Software Development Engineer').strip()
        status = form.get('status', 'approved').strip() # Default to approved when TPO creates

        if not name or not email or not roll_no:
            flash("Student Name, Roll Number, and Email are required.", "danger")
            return redirect(url_for('tpo_dashboard'))

        # 1. Create user account
        res = create_user(
            name=name,
            email=email,
            password=password,
            role='student',
            department=department,
            roll_no=roll_no,
            status=status
        )

        if not res['success']:
            flash(f"Error creating student account: {res['error']}", "danger")
            return redirect(url_for('tpo_dashboard'))

        # 2. Initialize student diagnostic record in students table
        student_data = {
            'name': name,
            'email': email,
            'roll_no': roll_no,
            'department': department,
            'year': int(form.get('year', 4)),
            'cgpa': cgpa,
            'backlogs': backlogs,
            'target_role': target_role,
            'dsa_problems': int(form.get('dsa_problems', 80)),
            'dsa_rating': float(form.get('dsa_rating', 3)),
            'prog_rating': float(form.get('prog_rating', 3)),
            'db_rating': float(form.get('db_rating', 3)),
            'cs_core_rating': float(form.get('cs_core_rating', 3)),
            'projects_count': int(form.get('projects_count', 2)),
            'internship_months': int(form.get('internship_months', 0)),
            'hackathons': int(form.get('hackathons', 0)),
            'certifications': int(form.get('certifications', 1)),
            'has_github': 'has_github' in form,
            'has_live_deployment': 'has_live_deployment' in form,
            'aptitude_score': float(form.get('aptitude_score', 70)),
            'comm_rating': float(form.get('comm_rating', 3)),
            'interview_confidence': float(form.get('interview_confidence', 3)),
            'leadership_exp': 'leadership_exp' in form,
            'mock_interviews_done': 1
        }

        # Calculate PRI and forecast
        pri_calc = PlacementReadinessAnalyzer.calculate_pri(student_data)
        student_data.update(pri_calc)

        ml_pred = ml_engine.predict(student_data)
        student_data['expected_ctc_min'] = ml_pred['expected_ctc_min']
        student_data['expected_ctc_max'] = ml_pred['expected_ctc_max']
        student_data['placement_prob'] = ml_pred['placement_probability']

        save_student_assessment(student_data)

        flash(f"Student {name} ({roll_no}) was successfully added by TPO and registered with status: {status.upper()}.", "success")
        return redirect(url_for('tpo_dashboard'))

    except Exception as e:
        flash(f"Error adding student: {str(e)}", "danger")
        return redirect(url_for('tpo_dashboard'))

@app.route('/tpo/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def tpo_delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User not found.", "warning")
        return redirect(url_for('tpo_dashboard'))

    if user['role'] == 'admin':
        flash("Action Denied: You cannot delete an administrator account.", "danger")
        return redirect(url_for('tpo_dashboard'))

    deleted_info = delete_user_by_id(user_id)
    if deleted_info:
        flash(f"User account '{deleted_info['name']}' ({deleted_info['email']}) and associated student records were successfully removed.", "success")
    else:
        flash("Could not delete user account.", "warning")

    return redirect(url_for('tpo_dashboard'))

@app.route('/tpo/delete_student/<int:student_id>', methods=['POST'])
@admin_required
def tpo_delete_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash("Student record not found.", "warning")
        return redirect(url_for('tpo_dashboard'))

    deleted_info = delete_student_by_id(student_id)
    if deleted_info:
        flash(f"Student assessment profile for '{deleted_info['name']}' ({deleted_info['roll_no']}) was successfully removed from the placement roster.", "success")
    else:
        flash("Could not delete student record.", "warning")

    return redirect(url_for('tpo_dashboard'))

@app.route('/tpo/approve/<int:user_id>', methods=['POST'])
@admin_required
def tpo_approve_student(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Student user not found.", "warning")
        return redirect(url_for('tpo_dashboard'))
        
    update_user_status(user_id, 'approved')
    flash(f"Student account for {user['name']} ({user['email']}) has been APPROVED. The student can now log in.", "success")
    return redirect(url_for('tpo_dashboard'))

@app.route('/tpo/reject/<int:user_id>', methods=['POST'])
@admin_required
def tpo_reject_student(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Student user not found.", "warning")
        return redirect(url_for('tpo_dashboard'))
        
    update_user_status(user_id, 'rejected')
    flash(f"Student registration for {user['name']} ({user['email']}) has been REJECTED.", "warning")
    return redirect(url_for('tpo_dashboard'))

@app.route('/interview_prep')
@login_required
def interview_prep():
    return render_template('interview_prep.html')

@app.route('/students')
@login_required
def students_list():
    filter_dept = request.args.get('department', 'All')
    filter_tier = request.args.get('tier', 'All')
    search = request.args.get('search', '').strip()

    students = get_all_students(filter_dept=filter_dept, filter_tier=filter_tier, search=search)
    return render_template(
        'students_list.html',
        students=students,
        selected_dept=filter_dept,
        selected_tier=filter_tier,
        search_query=search
    )

# REST API for external integrations / quick predict
@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json() or {}
    pri_info = PlacementReadinessAnalyzer.calculate_pri(data)
    ml_pred = ml_engine.predict(data)
    fitment = PlacementReadinessAnalyzer.analyze_role_fitment(data)
    return jsonify({
        'status': 'success',
        'pri': pri_info,
        'ml_forecast': ml_pred,
        'role_fitment': fitment
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
