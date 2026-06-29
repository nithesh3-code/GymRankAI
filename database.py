import sqlite3

def create_database():

    conn = sqlite3.connect("workouts.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise TEXT,
        weight REAL,
        reps INTEGER,
        sets INTEGER,
        volume REAL,
        xp INTEGER,
        rank TEXT,
        workout_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completed_workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_date TEXT UNIQUE,
        xp INTEGER
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise TEXT,
        target INTEGER
    )
    """)


    conn.commit()
    conn.close()