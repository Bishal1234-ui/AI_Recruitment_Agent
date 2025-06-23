import sqlite3


def save_result_to_db(name, email, resume_path, decision, score, justification):
    conn = sqlite3.connect("recruitment_results.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT,
            candidate_email TEXT,
            resume_path TEXT,
            decision TEXT,
            compatibility_score INTEGER,
            justification TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO results (candidate_name, candidate_email, resume_path, decision, compatibility_score, justification)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, resume_path, decision, score, justification))
    conn.commit()
    conn.close()