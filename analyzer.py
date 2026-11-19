"""
Placement Readiness Index (PRI) Engine, Skill Gap Analyzer & Roadmap Generator
"""
import re

ROLE_BENCHMARKS = {
    "Software Development Engineer": {
        "DSA": 90,
        "System Design": 80,
        "Core Languages": 85,
        "Databases": 75,
        "Cloud/DevOps": 60,
        "Aptitude/Soft Skills": 80,
        "required_skills": ["dsa", "c++", "java", "python", "oop", "dbms", "os", "system design", "algorithms", "git"]
    },
    "Full Stack Web Developer": {
        "DSA": 75,
        "System Design": 75,
        "Core Languages": 85,
        "Databases": 85,
        "Cloud/DevOps": 70,
        "Aptitude/Soft Skills": 75,
        "required_skills": ["javascript", "react", "node.js", "html", "css", "sql", "mongodb", "rest api", "git", "docker"]
    },
    "Data Scientist & AI Engineer": {
        "DSA": 75,
        "System Design": 70,
        "Core Languages": 90,
        "Databases": 80,
        "Cloud/DevOps": 65,
        "Aptitude/Soft Skills": 80,
        "required_skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "sql", "deep learning", "statistics", "data analysis"]
    },
    "Cloud & DevOps Engineer": {
        "DSA": 65,
        "System Design": 85,
        "Core Languages": 75,
        "Databases": 70,
        "Cloud/DevOps": 90,
        "Aptitude/Soft Skills": 75,
        "required_skills": ["linux", "docker", "kubernetes", "aws", "ci/cd", "terraform", "bash", "python", "networking", "git"]
    },
    "Data Analyst / Business Analyst": {
        "DSA": 55,
        "System Design": 55,
        "Core Languages": 75,
        "Databases": 90,
        "Cloud/DevOps": 50,
        "Aptitude/Soft Skills": 90,
        "required_skills": ["sql", "excel", "power bi", "tableau", "python", "statistics", "communication", "critical thinking", "data cleaning"]
    },
    "Quality Assurance & SDET": {
        "DSA": 70,
        "System Design": 65,
        "Core Languages": 80,
        "Databases": 70,
        "Cloud/DevOps": 65,
        "Aptitude/Soft Skills": 80,
        "required_skills": ["selenium", "java", "python", "testing", "junit", "api testing", "postman", "jira", "automation", "git"]
    }
}

class PlacementReadinessAnalyzer:
    @staticmethod
    def calculate_pri(form_data):
        """
        Calculates 5 Pillar scores and total Placement Readiness Index (0-100).
        """
        # 1. Academic Foundation Pillar (Max 15)
        cgpa = float(form_data.get('cgpa', 7.0))
        backlogs = int(form_data.get('backlogs', 0))
        
        # CGPA score (0 - 12 points)
        academic_base = min(max((cgpa - 5.0) / 5.0 * 12.0, 0), 12.0)
        # Backlog deduction (3 points bonus for 0 backlogs, minus 2 for each backlog)
        if backlogs == 0:
            backlog_factor = 3.0
        else:
            backlog_factor = max(0.0, 3.0 - (backlogs * 1.5))
        academic_pillar = round(min(academic_base + backlog_factor, 15.0), 1)

        # 2. Technical Competence & DSA Pillar (Max 35)
        # DSA problems count (0 - 500+)
        dsa_count = int(form_data.get('dsa_problems', 0))
        if dsa_count >= 300:
            dsa_score = 15.0
        elif dsa_count >= 150:
            dsa_score = 11.5
        elif dsa_count >= 50:
            dsa_score = 8.0
        else:
            dsa_score = (dsa_count / 50.0) * 5.0

        # Technical skill ratings (1 - 5 each)
        dsa_rating = float(form_data.get('dsa_rating', 3)) # out of 5
        prog_rating = float(form_data.get('prog_rating', 3)) # out of 5
        db_rating = float(form_data.get('db_rating', 3)) # out of 5
        cs_core_rating = float(form_data.get('cs_core_rating', 3)) # out of 5 (OS, DBMS, Networks)
        
        tech_ratings_score = ((dsa_rating + prog_rating + db_rating + cs_core_rating) / 20.0) * 20.0
        technical_pillar = round(min(dsa_score + tech_ratings_score, 35.0), 1)

        # 3. Practical Experience & Projects Pillar (Max 20)
        projects_count = int(form_data.get('projects_count', 1))
        internship_months = int(form_data.get('internship_months', 0))
        hackathons = int(form_data.get('hackathons', 0))
        has_github = 1 if form_data.get('has_github') in ['1', 'true', 'on', True] else 0
        has_live_deployment = 1 if form_data.get('has_live_deployment') in ['1', 'true', 'on', True] else 0
        
        proj_pts = min(projects_count * 2.5, 7.5)
        intern_pts = min(internship_months * 1.5, 6.0)
        hackathon_pts = min(hackathons * 1.5, 3.0)
        repo_pts = 2.0 if has_github else 0.0
        deploy_pts = 1.5 if has_live_deployment else 0.0
        
        project_pillar = round(min(proj_pts + intern_pts + hackathon_pts + repo_pts + deploy_pts, 20.0), 1)

        # 4. Aptitude & Logical Reasoning Pillar (Max 15)
        aptitude_pct = float(form_data.get('aptitude_score', 65))
        aptitude_pillar = round(min((aptitude_pct / 100.0) * 15.0, 15.0), 1)

        # 5. Soft Skills & Interview Readiness Pillar (Max 15)
        comm_rating = float(form_data.get('comm_rating', 3)) # 1-5
        interview_confidence = float(form_data.get('interview_confidence', 3)) # 1-5
        leadership_exp = 1.5 if form_data.get('leadership_exp') in ['1', 'true', 'on', True] else 0.0
        mock_interviews_done = int(form_data.get('mock_interviews_done', 0))
        mock_pts = min(mock_interviews_done * 1.0, 3.5)
        
        soft_base = ((comm_rating + interview_confidence) / 10.0) * 10.0
        soft_skill_pillar = round(min(soft_base + leadership_exp + mock_pts, 15.0), 1)

        total_pri = round(academic_pillar + technical_pillar + project_pillar + aptitude_pillar + soft_skill_pillar, 1)

        # Determine Tier
        if total_pri >= 82 and backlogs == 0 and cgpa >= 7.5:
            tier = "Super Dream (Tier 1 Product)"
        elif total_pri >= 68:
            tier = "Dream (Tier 2 High-Growth)"
        elif total_pri >= 52:
            tier = "Core / Service (Tier 3)"
        else:
            tier = "Developing / Needs Polish"

        return {
            'pri_score': total_pri,
            'tier': tier,
            'academic_score': academic_pillar,
            'technical_score': technical_pillar,
            'project_score': project_pillar,
            'aptitude_score': aptitude_pillar,
            'soft_skill_score': soft_skill_pillar,
            'pillars': {
                'Academic Foundation': {'score': academic_pillar, 'max': 15, 'pct': round((academic_pillar/15)*100, 1)},
                'Technical & DSA': {'score': technical_pillar, 'max': 35, 'pct': round((technical_pillar/35)*100, 1)},
                'Projects & Experience': {'score': project_pillar, 'max': 20, 'pct': round((project_pillar/20)*100, 1)},
                'Aptitude & Reasoning': {'score': aptitude_pillar, 'max': 15, 'pct': round((aptitude_pillar/15)*100, 1)},
                'Soft Skills & Interview': {'score': soft_skill_pillar, 'max': 15, 'pct': round((soft_skill_pillar/15)*100, 1)},
            }
        }

    @staticmethod
    def analyze_role_fitment(student_data):
        """
        Computes role match % and radar metrics across target job roles.
        """
        target_role = student_data.get('target_role', 'Software Development Engineer')
        if target_role not in ROLE_BENCHMARKS:
            target_role = "Software Development Engineer"
            
        benchmark = ROLE_BENCHMARKS[target_role]
        
        # Calculate candidate dimensions (0 - 100 scale)
        dsa_count = int(student_data.get('dsa_problems', 0))
        dsa_rating = float(student_data.get('dsa_rating', 3))
        cand_dsa = min(max((dsa_count / 300.0) * 50 + (dsa_rating / 5.0) * 50, 20), 100)
        
        cs_core = float(student_data.get('cs_core_rating', 3))
        cand_sys_design = min(max((cs_core / 5.0) * 80 + (int(student_data.get('projects_count', 1)) * 5), 20), 100)
        
        cand_languages = min(max((float(student_data.get('prog_rating', 3)) / 5.0) * 100, 20), 100)
        cand_db = min(max((float(student_data.get('db_rating', 3)) / 5.0) * 100, 20), 100)
        
        has_deploy = 1 if student_data.get('has_live_deployment') in ['1', 'true', 'on', True] else 0
        cand_cloud = min(max(40 + (has_deploy * 35) + int(student_data.get('certifications', 0)) * 10, 20), 100)
        
        comm = float(student_data.get('comm_rating', 3))
        apt = float(student_data.get('aptitude_score', 65))
        cand_soft = min(max((comm / 5.0) * 50 + (apt / 100.0) * 50, 20), 100)

        candidate_dimensions = {
            "DSA": round(cand_dsa, 1),
            "System Design": round(cand_sys_design, 1),
            "Core Languages": round(cand_languages, 1),
            "Databases": round(cand_db, 1),
            "Cloud/DevOps": round(cand_cloud, 1),
            "Aptitude/Soft Skills": round(cand_soft, 1)
        }

        # Calculate role fitment scores for all roles
        role_matches = []
        for role_name, b_dims in ROLE_BENCHMARKS.items():
            diffs = []
            for dim in ["DSA", "System Design", "Core Languages", "Databases", "Cloud/DevOps", "Aptitude/Soft Skills"]:
                req = b_dims[dim]
                cand = candidate_dimensions[dim]
                # Ratio capped at 1.0
                ratio = min(cand / req, 1.0)
                diffs.append(ratio)
            match_pct = round((sum(diffs) / len(diffs)) * 100, 1)
            role_matches.append({
                'role': role_name,
                'match_pct': match_pct,
                'is_target': (role_name == target_role)
            })

        role_matches = sorted(role_matches, key=lambda x: x['match_pct'], reverse=True)

        return {
            'target_role': target_role,
            'benchmark': benchmark,
            'candidate_dimensions': candidate_dimensions,
            'all_role_matches': role_matches
        }

    @staticmethod
    def identify_skill_gaps_and_roadmap(student_data, pri_result):
        """
        Identifies critical skill gaps and builds a 30-day targeted preparation roadmap.
        """
        gaps = []
        strengths = []
        
        # Academic checks
        cgpa = float(student_data.get('cgpa', 7.0))
        backlogs = int(student_data.get('backlogs', 0))
        if backlogs > 0:
            gaps.append({
                'category': 'Academic',
                'severity': 'High',
                'title': f'{backlogs} Active Backlog(s) Detected',
                'description': 'Most Tier-1 product firms and top MNCs enforce a strict zero-backlog eligibility criterion at the time of recruitment.',
                'action': 'Prioritize clearing remaining backlog subjects in the immediate upcoming semester examination.'
            })
        elif cgpa >= 8.5:
            strengths.append("High academic standing (CGPA >= 8.5), eligible for 100% of campus drive cutoffs.")
            
        # DSA checks
        dsa_count = int(student_data.get('dsa_problems', 0))
        if dsa_count < 100:
            gaps.append({
                'category': 'DSA & Coding',
                'severity': 'High',
                'title': f'Low Problem Solving Volume ({dsa_count} problems solved)',
                'description': 'Top product interviews require consistent mastery over Stacks, Queues, Binary Trees, and Dynamic Programming.',
                'action': 'Solve the Blind 75 or NeetCode 150 problem list. Target at least 2-3 medium problems per day.'
            })
        elif dsa_count >= 250:
            strengths.append(f"Strong coding foundation with {dsa_count}+ solved algorithmic problems.")

        # Project checks
        projects_count = int(student_data.get('projects_count', 1))
        has_live_deployment = student_data.get('has_live_deployment') in ['1', 'true', 'on', True]
        has_github = student_data.get('has_github') in ['1', 'true', 'on', True]
        
        if projects_count < 2 or not has_live_deployment:
            gaps.append({
                'category': 'Practical Experience',
                'severity': 'Medium',
                'title': 'Project Depth & Deployment Gap',
                'description': 'Interviewers heavily favor full-stack or end-to-end architectures that are deployed with live working demo URLs and clean GitHub code.',
                'action': 'Deploy your flagship project on Vercel/Render/AWS and add a polished README with architecture diagram.'
            })
        else:
            strengths.append("Proven hands-on practical skills with deployed applications.")

        # Aptitude checks
        aptitude_pct = float(student_data.get('aptitude_score', 65))
        if aptitude_pct < 65:
            gaps.append({
                'category': 'Aptitude & Reasoning',
                'severity': 'High',
                'title': f'Aptitude Benchmark Underperformance ({aptitude_pct}%)',
                'description': 'Round 1 of 90% of placement drives is a timed aptitude screening. Weakness here prevents reaching the interview stage.',
                'action': 'Practice 30 minutes of Speed Math, Time & Work, Probability, and Syllogisms daily on IndiaBix or test series.'
            })
        elif aptitude_pct >= 85:
            strengths.append("High aptitude screening readiness (Score >= 85%).")

        # Soft Skills checks
        comm = float(student_data.get('comm_rating', 3))
        if comm < 3.5:
            gaps.append({
                'category': 'Communication & HR',
                'severity': 'Medium',
                'title': 'Interview Articulation & Communication Polish',
                'description': 'Technical competency must be clearly articulated using the STAR (Situation, Task, Action, Result) framework during HR and Managerial rounds.',
                'action': 'Record yourself answering "Tell me about yourself" and behavioral scenarios; review audio pacing and clarity.'
            })

        # 30-Day Personalized Roadmap
        roadmap = [
            {
                "week": "Week 1: Core DSA & Algorithmic Drills",
                "focus": "Data Structures Foundations & Problem Solving",
                "days": [
                    {"day": "Day 1-2", "task": "Arrays, Two-Pointers, Sliding Window, and HashMaps (10 problems)"},
                    {"day": "Day 3-4", "task": "Linked Lists, Stacks, Queues & Monotonic Stack patterns (8 problems)"},
                    {"day": "Day 5-6", "task": "Binary Trees, BST Traversal & Recursion Backtracking (8 problems)"},
                    {"day": "Day 7", "task": "Weekly Timed Contest (60 mins) & Problem Review"}
                ]
            },
            {
                "week": "Week 2: Advanced Topics & CS Fundamentals",
                "focus": "Dynamic Programming, Graphs & Core CS Subjects",
                "days": [
                    {"day": "Day 8-9", "task": "Graph BFS/DFS, Cycle Detection, Dijkstra's Algorithm (6 problems)"},
                    {"day": "Day 10-11", "task": "1D & 2D Dynamic Programming (Knapsack, LCS, LIS patterns)"},
                    {"day": "Day 12-13", "task": "DBMS & OS Revision: Normalization, Indexing, Transactions, Deadlocks"},
                    {"day": "Day 14", "task": "SQL Query Practice: Joins, Group By, Window Functions (LeetCode SQL 50)"}
                ]
            },
            {
                "week": "Week 3: Project Architecture, System Design & Resume",
                "focus": "Hands-on Showcase & Portfolio Elevation",
                "days": [
                    {"day": "Day 15-16", "task": "Audit Flagship Project: Refactor code, write unit tests, dockerize or host live"},
                    {"day": "Day 17-18", "task": "Design README: Add system architecture diagram, tech stack badges & live URL"},
                    {"day": "Day 19-20", "task": "ATS Resume Tailoring: Quantify impact (e.g., 'Reduced latency by 35% using Redis')"},
                    {"day": "Day 21", "task": "System Design Basics: Scalability, Caching, Load Balancing & Microservices"}
                ]
            },
            {
                "week": "Week 4: Mock Tests, STAR Stories & Final Polish",
                "focus": "Simulation & Behavioral Excellence",
                "days": [
                    {"day": "Day 22-24", "task": "Take 3 full-length timed Placement Aptitude & Technical Mock Tests"},
                    {"day": "Day 25-26", "task": "Prepare 5 STAR stories: Failure, Conflict, Innovation, Leadership, Pressure"},
                    {"day": "Day 27-28", "task": "Conduct Peer Mock Interviews for both DSA coding and HR rounds"},
                    {"day": "Day 29-30", "task": "Company-specific research, recent interview experiences & final confidence check"}
                ]
            }
        ]

        return {
            'gaps': gaps,
            'strengths': strengths,
            'roadmap': roadmap
        }

    @staticmethod
    def match_resume_to_jd(resume_text, target_role, custom_jd=None):
        """
        Parses resume text and compares against target role skill keywords.
        """
        keywords_dict = {
            "Software Development Engineer": [
                "python", "java", "c++", "data structures", "algorithms", "oop",
                "dbms", "sql", "git", "linux", "rest api", "system design", "docker", "unit testing"
            ],
            "Full Stack Web Developer": [
                "javascript", "typescript", "react", "next.js", "node.js", "express",
                "html5", "css3", "tailwind", "mongodb", "postgresql", "rest api", "git", "redux"
            ],
            "Data Scientist & AI Engineer": [
                "python", "machine learning", "deep learning", "pandas", "numpy", "scikit-learn",
                "tensorflow", "pytorch", "sql", "data visualization", "statistics", "eda", "nlp"
            ],
            "Cloud & DevOps Engineer": [
                "aws", "azure", "docker", "kubernetes", "ci/cd", "jenkins", "terraform",
                "linux", "bash", "git", "networking", "ansible", "monitoring", "prometheus"
            ],
            "Data Analyst / Business Analyst": [
                "sql", "excel", "power bi", "tableau", "python", "statistics",
                "data modeling", "dashboards", "business intelligence", "etl", "reporting"
            ],
            "Quality Assurance & SDET": [
                "selenium", "automation testing", "java", "python", "test cases",
                "postman", "api testing", "jira", "junit", "testng", "cucumber", "ci/cd"
            ]
        }

        role_keywords = keywords_dict.get(target_role, keywords_dict["Software Development Engineer"])
        
        # If custom JD provided, extract prominent tech words
        if custom_jd and len(custom_jd.strip()) > 20:
            words = set(re.findall(r'\b[a-zA-Z#+.-]{2,15}\b', custom_jd.lower()))
            # Combine common tech keywords found in JD
            custom_targets = [w for w in words if len(w) > 2]
            if len(custom_targets) >= 5:
                # Merge unique
                role_keywords = list(set(role_keywords + custom_targets[:15]))

        resume_lower = resume_text.lower()
        matched = []
        missing = []

        for kw in role_keywords:
            # Word boundary check
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, resume_lower):
                matched.append(kw)
            else:
                missing.append(kw)

        total_kw = len(role_keywords)
        match_pct = round((len(matched) / total_kw * 100), 1) if total_kw > 0 else 0

        # Suggestions
        suggestions = []
        if match_pct < 60:
            suggestions.append("Your resume currently matches less than 60% of core role keywords. ATS scanners may filter it out before human review.")
        if missing:
            suggestions.append(f"Consider naturally incorporating missing keywords such as: {', '.join(missing[:5])}.")
        if "git" in missing or "github" in missing:
            suggestions.append("Add links to your public GitHub repositories with commit activity.")
        if "metrics" not in resume_lower and "%" not in resume_text:
            suggestions.append("Use quantifiable metrics (e.g., 'Enhanced response time by 40%', 'Processed 10,000+ records') to demonstrate impact.")

        return {
            'role': target_role,
            'match_percentage': match_pct,
            'matched_skills': matched,
            'missing_skills': missing,
            'total_keywords_analyzed': total_kw,
            'suggestions': suggestions
        }
