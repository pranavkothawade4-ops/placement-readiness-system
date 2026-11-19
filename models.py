import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table for Authentication & Authorization
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            department TEXT,
            roll_no TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if 'status' column exists in existing users table, add if missing
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row['name'] for row in cursor.fetchall()]
    if 'status' not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'approved'")
    
    # Ensure all admin accounts are approved
    cursor.execute("UPDATE users SET status = 'approved' WHERE role = 'admin'")
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT,
            year INTEGER DEFAULT 4,
            cgpa REAL,
            backlogs INTEGER DEFAULT 0,
            academic_score REAL DEFAULT 0,
            technical_score REAL DEFAULT 0,
            project_score REAL DEFAULT 0,
            aptitude_score REAL DEFAULT 0,
            soft_skill_score REAL DEFAULT 0,
            pri_score REAL DEFAULT 0,
            tier TEXT,
            expected_ctc_min REAL DEFAULT 0,
            expected_ctc_max REAL DEFAULT 0,
            placement_prob REAL DEFAULT 0,
            target_role TEXT,
            profile_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Mock assessment test results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_name TEXT,
            category TEXT,
            total_questions INTEGER,
            correct_count INTEGER,
            score_pct REAL,
            details_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    ''')
    
    # Resume match records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            target_role TEXT,
            match_percentage REAL,
            matched_skills TEXT,
            missing_skills TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Ensure default admin account is seeded
    seed_default_admin()

# User Authentication Helpers
def create_user(name, email, password, role='student', department='', roll_no='', status=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = generate_password_hash(password)
    
    # Default status: students are 'pending' until TPO approves; admins are 'approved'
    if status is None:
        status = 'approved' if role == 'admin' else 'pending'
        
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role, department, roll_no, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name.strip(), email.strip().lower(), pwd_hash, role, department.strip(), roll_no.strip(), status))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {'success': True, 'user_id': user_id, 'status': status}
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': 'An account with this email address already exists.'}
    except Exception as e:
        conn.close()
        return {'success': False, 'error': str(e)}

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_users_by_status(status=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status and status != 'All':
        cursor.execute("SELECT * FROM users WHERE role = 'student' AND status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM users WHERE role = 'student' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_user_status(user_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
    conn.commit()
    conn.close()
    return True

def delete_user_by_id(user_id):
    """
    Deletes user by user_id and cleans up any linked student records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None
    
    user_dict = dict(user)
    # Delete from users
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    # Delete from students if roll_no or email matches
    if user_dict.get('roll_no'):
        cursor.execute("DELETE FROM students WHERE roll_no = ?", (user_dict['roll_no'],))
    if user_dict.get('email'):
        cursor.execute("DELETE FROM students WHERE email = ?", (user_dict['email'],))
        
    conn.commit()
    conn.close()
    return user_dict

def delete_student_by_id(student_id):
    """
    Deletes student profile by student_id and removes associated student user account.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return None
        
    student_dict = dict(student)
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    cursor.execute("DELETE FROM mock_test_results WHERE student_id = ?", (student_id,))
    
    # Also delete user account if matching roll_no or email
    if student_dict.get('roll_no'):
        cursor.execute("DELETE FROM users WHERE roll_no = ? AND role = 'student'", (student_dict['roll_no'],))
    if student_dict.get('email'):
        cursor.execute("DELETE FROM users WHERE email = ? AND role = 'student'", (student_dict['email'],))
        
    conn.commit()
    conn.close()
    return student_dict

def get_all_users_detailed(role='student'):
    """
    Returns all registered users with their assessment status.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.name, u.email, u.role, u.department, u.roll_no, u.status, u.created_at,
               s.id as student_id, s.pri_score, s.tier, s.cgpa
        FROM users u
        LEFT JOIN students s ON u.roll_no = s.roll_no OR u.email = s.email
        WHERE u.role = ?
        ORDER BY u.created_at DESC
    ''', (role,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_approval_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM users WHERE role = 'student' GROUP BY status")
    rows = cursor.fetchall()
    stats = {'pending': 0, 'approved': 0, 'rejected': 0, 'total': 0}
    for r in rows:
        st = r['status']
        if st in stats:
            stats[st] = r['count']
        stats['total'] += r['count']
    conn.close()
    return stats

def verify_user_login(email, password):
    user = get_user_by_email(email)
    if not user:
        return None, "Invalid email address or user not registered."
    if not check_password_hash(user['password_hash'], password):
        return None, "Incorrect password. Please try again."
        
    user_status = user.get('status', 'approved')
    if user['role'] != 'admin':
        if user_status == 'pending':
            return None, "ACCOUNT PENDING APPROVAL: Your registration has been submitted but is awaiting approval from the Training & Placement Officer (TPO). Please contact the placement cell or check back once approved."
        elif user_status == 'rejected':
            return None, "ACCOUNT REJECTED: Your registration was rejected by the Training & Placement Officer. Please reach out to the college placement department for clarification."
            
    return user, None

def seed_default_admin():
    admin = get_user_by_email("admin@campus.edu")
    if not admin:
        create_user(
            name="Campus TPO Head",
            email="admin@campus.edu",
            password="admin123",
            role="admin",
            department="Placement Cell",
            roll_no="TPO-ADMIN-01",
            status="approved"
        )
        print("Default TPO Admin account seeded: admin@campus.edu / admin123")
    else:
        # Ensure status is approved
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET status = 'approved' WHERE email = 'admin@campus.edu'")
        conn.commit()
        conn.close()

# Helper DB methods
def save_student_assessment(student_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if student with roll_no exists
    cursor.execute("SELECT id FROM students WHERE roll_no = ?", (student_data.get('roll_no'),))
    existing = cursor.fetchone()
    
    profile_json = json.dumps(student_data)
    
    if existing:
        student_id = existing['id']
        cursor.execute('''
            UPDATE students SET
                name = ?, email = ?, department = ?, year = ?, cgpa = ?, backlogs = ?,
                academic_score = ?, technical_score = ?, project_score = ?, aptitude_score = ?,
                soft_skill_score = ?, pri_score = ?, tier = ?, expected_ctc_min = ?,
                expected_ctc_max = ?, placement_prob = ?, target_role = ?, profile_json = ?,
                created_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            student_data.get('name'),
            student_data.get('email'),
            student_data.get('department'),
            student_data.get('year', 4),
            student_data.get('cgpa'),
            student_data.get('backlogs', 0),
            student_data.get('academic_score', 0),
            student_data.get('technical_score', 0),
            student_data.get('project_score', 0),
            student_data.get('aptitude_score', 0),
            student_data.get('soft_skill_score', 0),
            student_data.get('pri_score', 0),
            student_data.get('tier', 'Developing'),
            student_data.get('expected_ctc_min', 0),
            student_data.get('expected_ctc_max', 0),
            student_data.get('placement_prob', 0),
            student_data.get('target_role', 'Software Development Engineer'),
            profile_json,
            student_id
        ))
    else:
        cursor.execute('''
            INSERT INTO students (
                roll_no, name, email, department, year, cgpa, backlogs,
                academic_score, technical_score, project_score, aptitude_score,
                soft_skill_score, pri_score, tier, expected_ctc_min,
                expected_ctc_max, placement_prob, target_role, profile_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_data.get('roll_no'),
            student_data.get('name'),
            student_data.get('email'),
            student_data.get('department'),
            student_data.get('year', 4),
            student_data.get('cgpa'),
            student_data.get('backlogs', 0),
            student_data.get('academic_score', 0),
            student_data.get('technical_score', 0),
            student_data.get('project_score', 0),
            student_data.get('aptitude_score', 0),
            student_data.get('soft_skill_score', 0),
            student_data.get('pri_score', 0),
            student_data.get('tier', 'Developing'),
            student_data.get('expected_ctc_min', 0),
            student_data.get('expected_ctc_max', 0),
            student_data.get('placement_prob', 0),
            student_data.get('target_role', 'Software Development Engineer'),
            profile_json
        ))
        student_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return student_id

def get_student_by_id(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        if data.get('profile_json'):
            try:
                data['profile'] = json.loads(data['profile_json'])
            except Exception:
                data['profile'] = {}
        return data
    return None

def get_student_by_roll(roll_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        if data.get('profile_json'):
            try:
                data['profile'] = json.loads(data['profile_json'])
            except Exception:
                data['profile'] = {}
        return data
    return None

def get_all_students(filter_dept=None, filter_tier=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM students WHERE 1=1"
    params = []
    
    if filter_dept and filter_dept != 'All':
        query += " AND department = ?"
        params.append(filter_dept)
        
    if filter_tier and filter_tier != 'All':
        query += " AND tier = ?"
        params.append(filter_tier)
        
    if search:
        query += " AND (name LIKE ? OR roll_no LIKE ? OR target_role LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
        
    query += " ORDER BY pri_score DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tpo_summary_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total_count FROM students")
    total_count = cursor.fetchone()['total_count']
    
    if total_count == 0:
        conn.close()
        return {
            'total_students': 0,
            'avg_pri': 0,
            'avg_cgpa': 0,
            'ready_percentage': 0,
            'avg_ctc': 0,
            'tier_counts': {},
            'dept_averages': {}
        }
        
    cursor.execute("SELECT AVG(pri_score) as avg_pri, AVG(cgpa) as avg_cgpa, AVG(expected_ctc_min + expected_ctc_max)/2 as avg_ctc FROM students")
    row = cursor.fetchone()
    avg_pri = round(row['avg_pri'] or 0, 1)
    avg_cgpa = round(row['avg_cgpa'] or 0, 2)
    avg_ctc = round(row['avg_ctc'] or 0, 2)
    
    # Ready count (PRI >= 60)
    cursor.execute("SELECT COUNT(*) as ready_count FROM students WHERE pri_score >= 60")
    ready_count = cursor.fetchone()['ready_count']
    ready_pct = round((ready_count / total_count) * 100, 1)
    
    # Tier breakdown
    cursor.execute("SELECT tier, COUNT(*) as count FROM students GROUP BY tier")
    tier_counts = {r['tier']: r['count'] for r in cursor.fetchall()}
    
    # Dept breakdown
    cursor.execute("SELECT department, AVG(pri_score) as avg_pri, COUNT(*) as count FROM students GROUP BY department")
    dept_averages = {r['department']: {'avg_pri': round(r['avg_pri'], 1), 'count': r['count']} for r in cursor.fetchall()}
    
    conn.close()
    return {
        'total_students': total_count,
        'avg_pri': avg_pri,
        'avg_cgpa': avg_cgpa,
        'ready_percentage': ready_pct,
        'avg_ctc': avg_ctc,
        'tier_counts': tier_counts,
        'dept_averages': dept_averages
    }

def record_quiz_result(student_id, student_name, category, total_q, correct, score_pct, details):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mock_test_results (student_id, student_name, category, total_questions, correct_count, score_pct, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, student_name, category, total_q, correct, score_pct, json.dumps(details)))
    conn.commit()
    conn.close()

def get_student_quiz_history(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mock_test_results WHERE student_id = ? ORDER BY created_at DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
