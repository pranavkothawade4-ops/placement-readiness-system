# 🎓 PlacementPulse: Student Skill & Placement Readiness Analysis System

An end-to-end AI-powered web platform designed to evaluate college student skill sets, compute a holistic **Placement Readiness Index (PRI)**, predict placement outcomes & CTC package ranges via Machine Learning, benchmark competencies against industry standards, identify critical skill gaps, provide customized 30-day preparation sprint roadmaps, and match resumes (including PDF uploads) with ATS keyword analytics.

---

## 🔒 Authentication, Authorization & TPO Approval Workflow

The platform implements a complete **User Signup &rarr; TPO Approval &rarr; User Login** verification cycle:

```
[Student Signs Up] ──> [Account Status: 'pending'] ──> [Login Blocked with Pending Notice]
                                  │
                                  ▼
                   [TPO Admin Reviews in Dashboard]
                                  │
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
              [Approve]                      [Reject]
                   │                             │
                   ▼                             ▼
         [Status: 'approved']           [Status: 'rejected']
                   │                             │
                   ▼                             ▼
       [Student Login Allowed]         [Login Denied with Notice]
```

1. **User Signup (`/signup`)**:
   - Students register with Name, Email, Password, Department, and Roll Number.
   - Upon signup, their account status is set to `pending`.
   - The user is notified: *"Your account is currently pending approval by the Training & Placement Officer (TPO)."*
   - Direct auto-login is prevented until TPO approval.

2. **Login Attempt During Pending Status (`/login`)**:
   - If an unapproved student attempts to sign in, authentication halts with:
     > **ACCOUNT PENDING APPROVAL**: *Your registration has been submitted but is awaiting approval from the Training & Placement Officer (TPO).*

3. **TPO Review & Decision Queue (`/tpo`)**:
   - The TPO Dashboard features a dedicated **Student Account Registration Approvals** queue showing:
     - Student Name, Roll No, Department, Email, Registration Timestamp, and Status.
   - One-click **Approve** and **Reject** buttons immediately update the candidate's authorization.

4. **Post-Approval Student Login (`/login`)**:
   - Once approved, students can log in normally to access all diagnostic, mock test, and resume tools.

5. **Separate TPO Admin Access**:
   - Regular students are strictly blocked from `/tpo`.
   - TPO Officers log in via `/admin/login` (Default: `admin@campus.edu` / `admin123`).

---

## 📄 PDF Resume & CV Upload (Resume Matcher)

- **Direct PDF Upload**: Students can drag and drop or browse any `.pdf` resume/CV file directly into the Resume Matcher.
- **Automated Text Extraction**: Powered by `pypdf`, extracting skills, projects, and experience across all pages.
- **ATS Keyword Alignment**: Compares extracted text against industry job descriptions across 6 target career tracks (SDE, Web Dev, Data Science, DevOps, Business Analyst, SDET) or a custom JD.
- **Visual Keyword Breakdown**: Displays matched keywords in green chips, missing high-impact keywords in red chips, and actionable ATS formatting advice.

---

## 🚀 Core Platform Features

### 1. 5-Pillar Placement Readiness Index (PRI) Engine
Evaluates candidates out of 100 points across the five critical dimensions campus recruiters assess:
- **Pillar 1: Academic Foundation (15 pts)**: CGPA cutoffs, semester consistency, and active backlog penalty.
- **Pillar 2: Technical Competence & DSA Mastery (35 pts)**: Problem count on LeetCode/HackerRank, core language proficiency (C++, Java, Python), database/SQL depth, and CS fundamentals (OS, DBMS, Networks).
- **Pillar 3: Hands-on Projects & Experience (20 pts)**: Flagship applications, live cloud deployment URLs (AWS/Render/Vercel), open-source GitHub activity, internships, and hackathons.
- **Pillar 4: Aptitude & Reasoning Speed (15 pts)**: Quantitative ability, logical reasoning, and puzzle solving to clear preliminary Round 1 screening.
- **Pillar 5: Soft Skills & Interview Articulation (15 pts)**: Verbal communication, STAR methodology for behavioral interviews, and technical confidence.

### 2. Machine Learning Placement & CTC Forecasting
- **Random Forest Classifier**: Predicts placement tier probability (`Super Dream (Tier 1 Product)`, `Dream (Tier 2 High-Growth)`, `Core / Service (Tier 3)`, or `Developing / Needs Polish`).
- **Random Forest Regressor**: Estimates expected campus salary package band (e.g. ₹18.5 - 28.0 LPA).
- **Feature Importance Tracking**: Quantifies which competencies contribute most to placement probability.

### 3. Industry Role Fitment & Radar Benchmark Comparison
Compares the candidate's actual abilities against industry requirements across 6 target career tracks:
1. Software Development Engineer (SDE)
2. Full Stack Web Developer
3. Data Scientist & AI Engineer
4. Cloud & DevOps Engineer
5. Data Analyst / Business Analyst
6. Quality Assurance & SDET

Renders an interactive **Radar Chart** directly mapping candidate capabilities vs role expectations.

### 4. Skill Gap Diagnostics & 30-Day Sprint Roadmap
- Highlights specific bottlenecks (e.g., *low problem count*, *un-deployed projects*, *active backlogs*, *aptitude weakness*).
- Formulates a customized 4-week, day-by-day action roadmap to systematically eliminate gaps before placement season.

### 5. Training & Placement Officer (TPO) Batch Analytics & User Management
- **Direct Add Student / User**:
  - The TPO Officer can directly onboard students via the **"+ Add Student / User"** modal.
  - Automatically provisions user credentials, sets authorization status (`approved` by default), computes baseline PRI scores, and populates the placement roster.
- **Remove Student / User**:
  - TPO can permanently remove any student user account from the **Registered Student Accounts** directory.
  - TPO can remove candidates from the placement roster with one-click deletion and confirmation.
- **Approval Queue**:
  - One-click **Approve** and **Reject** buttons for self-registered students waiting in the pending queue.
- **Batch Analytics & Reporting**:
  - Aggregated batch metrics: Placement Ready Rate (%), Batch Average PRI, Expected CTC.
  - Interactive charts: Placement Tier Distribution (Donut Chart) & Department Readiness (Bar Chart).
  - Filterable student roster table (by Branch, Placement Tier, and Search).
  - **One-click Export to CSV** for placement drives.
  - Dedicated **At-Risk Students** warning section for remedial training.

---

## 📂 Project Directory Structure

```
placement-readiness-system/
├── app.py                     # Main Flask web application, auth & REST routes
├── config.py                  # System configuration (DB path, Secret key)
├── models.py                  # Database connection, schemas, users, and queries
├── ml_engine.py               # Random Forest ML model for placement & CTC prediction
├── analyzer.py                # 5-Pillar PRI engine, gap analysis, and radar benchmark
├── quiz_bank.py               # Placement mock test question bank with explanations
├── sample_data.py             # Pre-seeded realistic student dataset for TPO dashboard
├── requirements.txt           # Package dependencies
├── test_app.py                # Comprehensive test suite (Auth, RBAC, PDF, ML)
├── static/
│   ├── css/
│   │   └── custom.css         # Custom animations, badges, glassmorphism, print styles
│   └── js/
│       └── app.js             # CSV export, alerts, and print helpers
└── templates/
    ├── base.html              # Base layout with navbar, auth states, and footer
    ├── index.html             # Public landing portal & platform overview
    ├── login.html             # Student Sign In portal
    ├── signup.html            # Student Sign Up registration
    ├── admin_login.html       # Separate TPO Officer Administrative Login
    ├── assess.html            # 4-section student skill evaluation wizard
    ├── report.html            # Detailed diagnostics report & radar chart
    ├── quiz.html              # Timed interactive placement mock quiz
    ├── resume_matcher.html    # PDF upload & ATS resume keyword matcher
    ├── tpo_dashboard.html     # Restricted TPO & recruiter analytics dashboard
    ├── interview_prep.html    # STAR behavioral guide & interview questions
    └── students_list.html     # Filterable student candidate directory
```

---

## 🏃 Quick Start Guide

### 1. Navigate to Project Directory
```powershell
cd "C:\Users\Admin\.gemini\antigravity\scratch\placement-readiness-system"
```

### 2. Verify / Run Test Suite
```powershell
python test_app.py
```
*(All 6 tests verify authentication, RBAC route protection, PDF upload text extraction, and ML predictions).*

### 3. Start the Web Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🔑 Demo Login Accounts

| Role | Portal URL | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | `/login` or `/signup` | Any signed up email | User chosen | Access to Home, Skills Assessment, Mock Quiz, PDF Resume Matcher, Interview Prep, Roster |
| **TPO Admin** | `/admin/login` | `admin@campus.edu` | `admin123` | Full access to all student features + **TPO Batch Analytics Dashboard** with CSV export |
