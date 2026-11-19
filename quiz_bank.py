"""
Comprehensive Placement Assessment Question Bank
Categorized by:
1. Aptitude & Logical Reasoning
2. Data Structures & Algorithms
3. Computer Science Fundamentals (OS, DBMS, CN)
4. Verbal & Communication Skills
"""

QUESTION_BANK = [
    # Aptitude & Quantitative
    {
        "id": 1,
        "category": "Aptitude",
        "question": "A train 240 m long passes a pole in 24 seconds. How long will it take to pass a platform 650 m long?",
        "options": ["65 seconds", "89 seconds", "100 seconds", "150 seconds"],
        "answer": 1, # Index 1 = 89 seconds
        "explanation": "Speed = 240/24 = 10 m/s. Total distance for platform = 240 + 650 = 890 m. Time = 890 / 10 = 89 seconds.",
        "difficulty": "Medium"
    },
    {
        "id": 2,
        "category": "Aptitude",
        "question": "If 12 men or 18 women can do a piece of work in 14 days, in how many days can 8 men and 16 women do the same work?",
        "options": ["9 days", "10 days", "12 days", "8 days"],
        "answer": 0, # Index 0 = 9 days
        "explanation": "12 Men = 18 Women => 1 Man = 1.5 Women. 8 men + 16 women = (8 * 1.5) + 16 = 28 women. If 18 women take 14 days, 28 women take (18 * 14) / 28 = 9 days.",
        "difficulty": "Hard"
    },
    {
        "id": 3,
        "category": "Aptitude",
        "question": "Find the missing number in the sequence: 4, 9, 25, 49, 121, ?",
        "options": ["144", "169", "196", "225"],
        "answer": 1, # Index 1 = 169
        "explanation": "These are squares of consecutive prime numbers: 2^2, 3^2, 5^2, 7^2, 11^2. The next prime is 13, and 13^2 = 169.",
        "difficulty": "Easy"
    },
    {
        "id": 4,
        "category": "Aptitude",
        "question": "A vendor buys lemons at 6 for $10 and sells them at 4 for $8. What is his profit percentage?",
        "options": ["15%", "20%", "25%", "30%"],
        "answer": 1, # Index 1 = 20%
        "explanation": "Cost of 1 lemon = $10/6 = $5/3. Selling price of 1 lemon = $8/4 = $2. Profit = 2 - (5/3) = $1/3. Profit % = ((1/3) / (5/3)) * 100 = 20%.",
        "difficulty": "Medium"
    },
    {
        "id": 5,
        "category": "Aptitude",
        "question": "In a group of 60 students, 35 like Python, 25 like Java, and 10 like both. How many like neither?",
        "options": ["5", "10", "12", "15"],
        "answer": 1, # Index 1 = 10
        "explanation": "Students liking at least one = 35 + 25 - 10 = 50. Total = 60. Neither = 60 - 50 = 10.",
        "difficulty": "Easy"
    },

    # Data Structures & Algorithms
    {
        "id": 6,
        "category": "DSA",
        "question": "What is the worst-case time complexity of finding an element in an unsorted Balanced Binary Search Tree (AVL Tree)?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "answer": 1, # Index 1 = O(log n)
        "explanation": "In an AVL tree, the height is guaranteed to be bounded by O(log n), so search is always O(log n) in worst case.",
        "difficulty": "Medium"
    },
    {
        "id": 7,
        "category": "DSA",
        "question": "Which of the following data structures is most suitable for implementing an LRU (Least Recently Used) Cache?",
        "options": ["Array and Stack", "Hash Map and Doubly Linked List", "Binary Heap and Queue", "Trie and Circular Array"],
        "answer": 1, # Index 1 = Hash Map and Doubly Linked List
        "explanation": "A Doubly Linked List provides O(1) removal and insertion at head/tail, and a Hash Map provides O(1) key-to-node lookup.",
        "difficulty": "Medium"
    },
    {
        "id": 8,
        "category": "DSA",
        "question": "What algorithmic design paradigm does Dijkstra's shortest path algorithm use?",
        "options": ["Divide and Conquer", "Dynamic Programming", "Greedy Algorithm", "Backtracking"],
        "answer": 2, # Index 2 = Greedy Algorithm
        "explanation": "Dijkstra's algorithm selects the nearest unvisited node greedily at each step.",
        "difficulty": "Easy"
    },
    {
        "id": 9,
        "category": "DSA",
        "question": "Given an array of size N, what is the minimum number of comparisons needed to find both the maximum and minimum elements?",
        "options": ["2N - 2", "3N/2 - 2", "N - 1", "N log N"],
        "answer": 1, # Index 1 = 3N/2 - 2
        "explanation": "By comparing elements in pairs, we make 1 comparison between the pair, and 2 comparisons with current min and max. Total comparisons = 3N/2 - 2.",
        "difficulty": "Hard"
    },
    {
        "id": 10,
        "category": "DSA",
        "question": "What is the time complexity to detect a cycle in a directed graph using DFS?",
        "options": ["O(V)", "O(E)", "O(V + E)", "O(V * E)"],
        "answer": 2, # Index 2 = O(V + E)
        "explanation": "Standard DFS traversal with recursion stack tracking (three-color state: unvisited, visiting, visited) takes O(V + E) time.",
        "difficulty": "Medium"
    },

    # CS Fundamentals (OS, DBMS, CN)
    {
        "id": 11,
        "category": "CS Core",
        "question": "Which of the following ACID properties in DBMS ensures that all operations within a transaction are completed or none are?",
        "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
        "answer": 0, # Index 0 = Atomicity
        "explanation": "Atomicity ensures 'all or nothing' execution of transaction steps.",
        "difficulty": "Easy"
    },
    {
        "id": 12,
        "category": "CS Core",
        "question": "In operating systems, which condition is NOT one of the Coffman conditions required for a deadlock to occur?",
        "options": ["Mutual Exclusion", "Preemption Allowed", "Hold and Wait", "Circular Wait"],
        "answer": 1, # Index 1 = Preemption Allowed
        "explanation": "The condition is 'No Preemption'. If preemption is allowed, deadlocks can be broken and avoided.",
        "difficulty": "Medium"
    },
    {
        "id": 13,
        "category": "CS Core",
        "question": "At which layer of the OSI model does the TLS/SSL handshake protocol operate?",
        "options": ["Network Layer", "Transport Layer / Session Layer", "Data Link Layer", "Physical Layer"],
        "answer": 1, # Index 1
        "explanation": "TLS operates above the transport layer (Layer 4) and provides session encryption (Layer 4/5/6).",
        "difficulty": "Medium"
    },
    {
        "id": 14,
        "category": "CS Core",
        "question": "What is the difference between Clustered and Non-Clustered index in SQL?",
        "options": [
            "Clustered alters physical order of table rows; non-clustered maintains a separate structure pointing to rows",
            "A table can have multiple clustered indexes, but only one non-clustered",
            "Clustered index is always slower than non-clustered",
            "Non-clustered indexes cannot have duplicate keys"
        ],
        "answer": 0,
        "explanation": "Clustered index dictates the physical sorting of the table rows on disk. Hence, only one clustered index can exist per table.",
        "difficulty": "Medium"
    },
    {
        "id": 15,
        "category": "CS Core",
        "question": "What causes the 'Thrashing' phenomenon in virtual memory systems?",
        "options": [
            "CPU executing infinite loops",
            "Too frequent page faults causing operating system to spend more time swapping than executing",
            "Cache memory overheating",
            "Corrupted disk partition"
        ],
        "answer": 1,
        "explanation": "Thrashing occurs when the system spends more time servicing page faults and paging than executing actual instructions.",
        "difficulty": "Easy"
    },

    # Verbal & Soft Skills
    {
        "id": 16,
        "category": "Verbal",
        "question": "Choose the correct antonym for the word 'METICULOUS':",
        "options": ["Careful", "Careless", "Thorough", "Detailed"],
        "answer": 1, # Index 1 = Careless
        "explanation": "Meticulous means showing great attention to detail. Its opposite is careless or sloppy.",
        "difficulty": "Easy"
    },
    {
        "id": 17,
        "category": "Verbal",
        "question": "In the STAR interview response methodology, what do the letters stand for?",
        "options": [
            "Strategy, Timing, Attitude, Result",
            "Situation, Task, Action, Result",
            "Skill, Theory, Application, Review",
            "Solution, Technique, Analysis, Report"
        ],
        "answer": 1, # Index 1
        "explanation": "STAR is the standard behavioral interview format: Situation, Task, Action, Result.",
        "difficulty": "Easy"
    },
    {
        "id": 18,
        "category": "Verbal",
        "question": "Identify the grammatically correct sentence:",
        "options": [
            "Neither of the candidates have submitted their assignment.",
            "Neither of the candidates has submitted his or her assignment.",
            "Neither candidate have submitted there assignment.",
            "Neither of the candidate had submitted them assignment."
        ],
        "answer": 1,
        "explanation": "'Neither' is singular and takes a singular verb 'has' and singular pronoun.",
        "difficulty": "Medium"
    },
    {
        "id": 19,
        "category": "Verbal",
        "question": "During a technical interview, if you don't know the answer to an architectural question, the best approach is:",
        "options": [
            "Guess blindly and act confident",
            "Change the topic immediately",
            "Acknowledge what you know, explain your thought process/intuition, and ask clarifying questions",
            "Remain completely silent"
        ],
        "answer": 2,
        "explanation": "Interviewers value intellectual honesty, problem-solving reasoning, and communication under ambiguity.",
        "difficulty": "Easy"
    },
    {
        "id": 20,
        "category": "DSA",
        "question": "What is the amortized time complexity of inserting an element into a dynamic array (like std::vector or Python list)?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
        "answer": 0, # Index 0 = O(1)
        "explanation": "Although doubling the array takes O(n), it occurs so infrequently that the amortized cost per append operation is O(1).",
        "difficulty": "Medium"
    }
]

def get_questions_by_category(category="All", limit=10):
    if category == "All":
        qs = QUESTION_BANK
    else:
        qs = [q for q in QUESTION_BANK if q["category"] == category]
    return qs[:limit]
