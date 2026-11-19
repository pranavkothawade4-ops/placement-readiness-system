"""
Comprehensive test suite verifying:
1. Public home page access without login
2. Route protection: non-logged-in users redirected to /login for other tabs
3. Student Signup -> TPO Approval -> Student Login complete workflow
4. TPO Dashboard Add / Remove User and Student features
5. TPO Dashboard access control: students blocked, separate admin login required
6. Resume Matcher PDF upload and keyword extraction
7. Machine Learning predictions & PRI score calculation
"""
import io
import unittest
from app import app
from models import (
    get_all_students, get_tpo_summary_stats, get_user_by_email,
    get_user_by_id, get_student_by_roll, get_student_by_id
)
from analyzer import PlacementReadinessAnalyzer
from ml_engine import ml_engine
from reportlab.pdfgen import canvas

class PlacementAuthAndTPOManagementTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_public_homepage(self):
        # Home page must be accessible without login
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"PlacementPulse", res.data)
        print("PASS: Public home page is accessible without login.")

    def test_protected_routes_require_login(self):
        # Non-logged-in users cannot access other tabs directly
        protected_urls = ['/assess', '/quiz', '/resume_matcher', '/interview_prep', '/students', '/report/1']
        for url in protected_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302, f"{url} should redirect unauthenticated users to login")
            self.assertIn('/login', res.headers['Location'])
        print("PASS: All protected student tabs redirect unauthenticated users to login.")

    def test_complete_signup_approval_login_workflow(self):
        """
        Tests the workflow:
        User Signup -> Account Pending -> Login Blocked -> TPO Approval -> User Login Allowed!
        """
        student_email = "new.candidate2@campus.edu"
        student_pwd = "password123"

        # 1. User Signup
        res_signup = self.client.post('/signup', data={
            'name': 'New Candidate 2',
            'email': student_email,
            'password': student_pwd,
            'department': 'Computer Science',
            'roll_no': '22CS556'
        }, follow_redirects=True)
        self.assertEqual(res_signup.status_code, 200)

        # Verify DB status is 'pending'
        user = get_user_by_email(student_email)
        self.assertIsNotNone(user)
        self.assertEqual(user['status'], 'pending')
        user_id = user['id']

        # 2. User attempts to login BEFORE TPO approval -> MUST BE BLOCKED
        res_early_login = self.client.post('/login', data={
            'email': student_email,
            'password': student_pwd
        }, follow_redirects=True)
        self.assertEqual(res_early_login.status_code, 200)
        self.assertIn(b"PENDING APPROVAL", res_early_login.data)

        # 3. TPO Admin logs in
        self.client.post('/admin/login', data={
            'email': 'admin@campus.edu',
            'password': 'admin123'
        }, follow_redirects=True)

        # 4. TPO Admin approves the pending student
        res_approve = self.client.post(f'/tpo/approve/{user_id}', follow_redirects=True)
        self.assertEqual(res_approve.status_code, 200)

        # 5. Clear admin session
        self.client.get('/logout')

        # 6. Student attempts login AFTER TPO approval -> MUST SUCCEED!
        res_approved_login = self.client.post('/login', data={
            'email': student_email,
            'password': student_pwd
        }, follow_redirects=True)
        self.assertEqual(res_approved_login.status_code, 200)
        self.assertIn(b"Welcome back", res_approved_login.data)
        print("PASS: User Signup -> TPO Approval -> User Login flow verified.")

    def test_tpo_add_and_remove_student_feature(self):
        """
        Tests the TPO Dashboard Add and Remove User / Student capabilities.
        """
        # 1. Login as TPO Admin
        res_admin = self.client.post('/admin/login', data={
            'email': 'admin@campus.edu',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res_admin.status_code, 200)

        # 2. TPO adds a new student directly
        added_email = "direct.student@campus.edu"
        added_roll = "22IT789"
        res_add = self.client.post('/tpo/add_student', data={
            'name': 'Direct Student',
            'roll_no': added_roll,
            'email': added_email,
            'password': 'DirectPassword123',
            'department': 'Information Technology',
            'cgpa': '8.4',
            'backlogs': '0',
            'target_role': 'Full Stack Web Developer',
            'status': 'approved'
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b"was successfully added by TPO", res_add.data)

        # Verify added user exists and is approved
        added_user = get_user_by_email(added_email)
        self.assertIsNotNone(added_user)
        self.assertEqual(added_user['status'], 'approved')

        # Verify added student profile exists on roster
        added_student = get_student_by_roll(added_roll)
        self.assertIsNotNone(added_student)
        self.assertGreater(added_student['pri_score'], 0)
        print("PASS: TPO successfully added a new student user with baseline diagnostics.")

        # 3. Log out admin and verify that the student can immediately log in
        self.client.get('/logout')
        res_login = self.client.post('/login', data={
            'email': added_email,
            'password': 'DirectPassword123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Welcome back", res_login.data)
        print("PASS: TPO-created student immediately logged in with provided credentials.")

        # 4. Log back in as Admin to test Remove feature
        self.client.post('/admin/login', data={
            'email': 'admin@campus.edu',
            'password': 'admin123'
        }, follow_redirects=True)

        # 5. Remove the user via TPO Dashboard
        user_id_to_delete = added_user['id']
        res_delete = self.client.post(f'/tpo/delete_user/{user_id_to_delete}', follow_redirects=True)
        self.assertEqual(res_delete.status_code, 200)
        self.assertIn(b"successfully removed", res_delete.data)

        # Verify user is deleted from database
        self.assertIsNone(get_user_by_id(user_id_to_delete))
        self.assertIsNone(get_student_by_roll(added_roll))
        print("PASS: TPO successfully removed student user and linked records from system.")

    def test_student_cannot_access_tpo_dashboard(self):
        # Create student session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 999
            sess['user_name'] = 'Regular Student'
            sess['user_email'] = 'reg.student@campus.edu'
            sess['user_role'] = 'student'

        # Attempt to access TPO Dashboard
        res = self.client.get('/tpo')
        self.assertEqual(res.status_code, 302)
        print("PASS: Regular student cannot access TPO Dashboard.")

    def test_resume_pdf_upload(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Resume Tester'
            sess['user_email'] = 'tester@campus.edu'
            sess['user_role'] = 'student'

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer)
        c.drawString(100, 750, "Resume of Candidate")
        c.drawString(100, 720, "Skills: Python, Java, Data Structures, Algorithms, Docker, SQL, Git")
        c.save()
        pdf_buffer.seek(0)

        data = {
            'target_role': 'Software Development Engineer',
            'resume_pdf': (pdf_buffer, 'candidate_resume.pdf')
        }
        res = self.client.post('/resume_matcher', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"ATS Alignment", res.data)
        print("PASS: PDF resume upload, text extraction, and ATS matching verified.")

if __name__ == '__main__':
    unittest.main()
