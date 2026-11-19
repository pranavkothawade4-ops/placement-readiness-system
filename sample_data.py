"""
Initial seed data generator for Placement Readiness System.
Pre-populates sample students across departments so the TPO Dashboard & Analytics are immediately rich.
"""
import random
from models import get_db_connection, save_student_assessment
from analyzer import PlacementReadinessAnalyzer
from ml_engine import ml_engine

SAMPLE_STUDENTS = [
    {
        "roll_no": "21CS001", "name": "Aarav Sharma", "email": "aarav.sharma@campus.edu",
        "department": "Computer Science", "year": 4, "cgpa": 9.4, "backlogs": 0,
        "dsa_problems": 380, "dsa_rating": 4.8, "prog_rating": 4.9, "db_rating": 4.5, "cs_core_rating": 4.6,
        "projects_count": 4, "internship_months": 6, "hackathons": 2, "has_github": True, "has_live_deployment": True,
        "aptitude_score": 92, "comm_rating": 4.8, "interview_confidence": 4.7, "leadership_exp": True,
        "mock_interviews_done": 4, "certifications": 3, "target_role": "Software Development Engineer"
    },
    {
        "roll_no": "21CS042", "name": "Priya Nair", "email": "priya.nair@campus.edu",
        "department": "Computer Science", "year": 4, "cgpa": 8.9, "backlogs": 0,
        "dsa_problems": 240, "dsa_rating": 4.2, "prog_rating": 4.5, "db_rating": 4.3, "cs_core_rating": 4.0,
        "projects_count": 3, "internship_months": 3, "hackathons": 1, "has_github": True, "has_live_deployment": True,
        "aptitude_score": 86, "comm_rating": 4.5, "interview_confidence": 4.2, "leadership_exp": True,
        "mock_interviews_done": 3, "certifications": 2, "target_role": "Full Stack Web Developer"
    },
    {
        "roll_no": "21IT015", "name": "Rohan Verma", "email": "rohan.v@campus.edu",
        "department": "Information Technology", "year": 4, "cgpa": 8.2, "backlogs": 0,
        "dsa_problems": 180, "dsa_rating": 3.8, "prog_rating": 4.0, "db_rating": 4.2, "cs_core_rating": 3.9,
        "projects_count": 3, "internship_months": 3, "hackathons": 1, "has_github": True, "has_live_deployment": False,
        "aptitude_score": 78, "comm_rating": 4.0, "interview_confidence": 3.8, "leadership_exp": False,
        "mock_interviews_done": 2, "certifications": 2, "target_role": "Data Scientist & AI Engineer"
    },
    {
        "roll_no": "21EC028", "name": "Ananya Deshmukh", "email": "ananya.d@campus.edu",
        "department": "Electronics & Comm", "year": 4, "cgpa": 7.8, "backlogs": 0,
        "dsa_problems": 110, "dsa_rating": 3.4, "prog_rating": 3.6, "db_rating": 3.2, "cs_core_rating": 3.5,
        "projects_count": 2, "internship_months": 2, "hackathons": 0, "has_github": True, "has_live_deployment": False,
        "aptitude_score": 72, "comm_rating": 3.8, "interview_confidence": 3.5, "leadership_exp": False,
        "mock_interviews_done": 1, "certifications": 1, "target_role": "Cloud & DevOps Engineer"
    },
    {
        "roll_no": "21DS009", "name": "Kabir Patel", "email": "kabir.p@campus.edu",
        "department": "Data Science", "year": 4, "cgpa": 8.7, "backlogs": 0,
        "dsa_problems": 210, "dsa_rating": 4.1, "prog_rating": 4.3, "db_rating": 4.6, "cs_core_rating": 4.1,
        "projects_count": 4, "internship_months": 4, "hackathons": 2, "has_github": True, "has_live_deployment": True,
        "aptitude_score": 88, "comm_rating": 4.4, "interview_confidence": 4.3, "leadership_exp": True,
        "mock_interviews_done": 3, "certifications": 3, "target_role": "Data Scientist & AI Engineer"
    },
    {
        "roll_no": "21ME033", "name": "Vikram Singh", "email": "vikram.s@campus.edu",
        "department": "Mechanical Engineering", "year": 4, "cgpa": 7.1, "backlogs": 0,
        "dsa_problems": 65, "dsa_rating": 2.8, "prog_rating": 3.0, "db_rating": 2.9, "cs_core_rating": 2.7,
        "projects_count": 1, "internship_months": 0, "hackathons": 0, "has_github": False, "has_live_deployment": False,
        "aptitude_score": 68, "comm_rating": 3.5, "interview_confidence": 3.0, "leadership_exp": False,
        "mock_interviews_done": 1, "certifications": 1, "target_role": "Quality Assurance & SDET"
    },
    {
        "roll_no": "21CS088", "name": "Neha Kulkarni", "email": "neha.k@campus.edu",
        "department": "Computer Science", "year": 4, "cgpa": 9.1, "backlogs": 0,
        "dsa_problems": 310, "dsa_rating": 4.6, "prog_rating": 4.7, "db_rating": 4.4, "cs_core_rating": 4.5,
        "projects_count": 3, "internship_months": 4, "hackathons": 1, "has_github": True, "has_live_deployment": True,
        "aptitude_score": 90, "comm_rating": 4.6, "interview_confidence": 4.5, "leadership_exp": True,
        "mock_interviews_done": 4, "certifications": 2, "target_role": "Software Development Engineer"
    },
    {
        "roll_no": "21IT044", "name": "Siddharth Rao", "email": "sid.rao@campus.edu",
        "department": "Information Technology", "year": 4, "cgpa": 6.8, "backlogs": 1,
        "dsa_problems": 45, "dsa_rating": 2.6, "prog_rating": 2.9, "db_rating": 3.0, "cs_core_rating": 2.8,
        "projects_count": 1, "internship_months": 0, "hackathons": 0, "has_github": True, "has_live_deployment": False,
        "aptitude_score": 58, "comm_rating": 3.0, "interview_confidence": 2.7, "leadership_exp": False,
        "mock_interviews_done": 0, "certifications": 0, "target_role": "Core / Service (Tier 3)"
    },
    {
        "roll_no": "21EC055", "name": "Tanvi Joshi", "email": "tanvi.j@campus.edu",
        "department": "Electronics & Comm", "year": 4, "cgpa": 6.2, "backlogs": 2,
        "dsa_problems": 20, "dsa_rating": 2.0, "prog_rating": 2.4, "db_rating": 2.2, "cs_core_rating": 2.0,
        "projects_count": 1, "internship_months": 0, "hackathons": 0, "has_github": False, "has_live_deployment": False,
        "aptitude_score": 45, "comm_rating": 2.8, "interview_confidence": 2.2, "leadership_exp": False,
        "mock_interviews_done": 0, "certifications": 0, "target_role": "Core / Service (Tier 3)"
    },
    {
        "roll_no": "21DS022", "name": "Aditya Banerjee", "email": "aditya.b@campus.edu",
        "department": "Data Science", "year": 4, "cgpa": 8.4, "backlogs": 0,
        "dsa_problems": 160, "dsa_rating": 3.9, "prog_rating": 4.1, "db_rating": 4.4, "cs_core_rating": 3.8,
        "projects_count": 3, "internship_months": 2, "hackathons": 1, "has_github": True, "has_live_deployment": True,
        "aptitude_score": 82, "comm_rating": 4.2, "interview_confidence": 4.0, "leadership_exp": False,
        "mock_interviews_done": 2, "certifications": 2, "target_role": "Data Analyst / Business Analyst"
    }
]

def seed_sample_students_if_empty():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM students")
    count = cursor.fetchone()['count']
    conn.close()
    
    if count == 0:
        print("Seeding initial student dataset...")
        for student_info in SAMPLE_STUDENTS:
            # Calculate PRI
            pri_calc = PlacementReadinessAnalyzer.calculate_pri(student_info)
            student_info.update(pri_calc)
            
            # Predict ML outcome
            ml_pred = ml_engine.predict(student_info)
            student_info['expected_ctc_min'] = ml_pred['expected_ctc_min']
            student_info['expected_ctc_max'] = ml_pred['expected_ctc_max']
            student_info['placement_prob'] = ml_pred['placement_probability']
            
            save_student_assessment(student_info)
        print("Initial sample dataset seeded successfully.")
        
    # Seed sample student user accounts if none exist
    seed_sample_users_if_empty()

def seed_sample_users_if_empty():
    from models import create_user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
    count = cursor.fetchone()['count']
    conn.close()

    if count == 0:
        # Create an approved student account
        create_user(
            name="Aarav Sharma",
            email="aarav.sharma@campus.edu",
            password="password123",
            role="student",
            department="Computer Science",
            roll_no="21CS001",
            status="approved"
        )
        # Create pending student accounts awaiting TPO approval
        create_user(
            name="Sanjana Mehra",
            email="sanjana.m@campus.edu",
            password="password123",
            role="student",
            department="Information Technology",
            roll_no="22IT105",
            status="pending"
        )
        create_user(
            name="Devendra Joshi",
            email="devendra.j@campus.edu",
            password="password123",
            role="student",
            department="Electronics & Comm",
            roll_no="22EC074",
            status="pending"
        )
        print("Sample student accounts (approved & pending) seeded.")
