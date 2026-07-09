import sqlite3
from typing import Optional, Dict, List

USER_DATABASE_PATH = "user_database.db"

def get_user_connection():
    conn = sqlite3.connect(USER_DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_user_database():
    conn = get_user_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS child_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            country_guideline TEXT NOT NULL DEFAULT 'WHO',
            gender TEXT,
            blood_group TEXT,
            allergies TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            child_id INTEGER NOT NULL,
            recipient_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'sent',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def register_user(name: str, email: str, password: str) -> bool:
    conn = get_user_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_user_by_email(email: str) -> Optional[Dict]:
    conn = get_user_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    user = get_user_by_email(email)
    if user and user['password'].strip() == password.strip():
        return user
    return None

def get_all_users() -> list:
    conn = get_user_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_child(name: str, date_of_birth: str, country_guideline: str, user_id: int,
              gender: Optional[str] = None, blood_group: Optional[str] = None, 
              allergies: Optional[str] = None) -> int:
    conn = get_user_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO child_profiles (user_id, name, date_of_birth, country_guideline, gender, blood_group, allergies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, date_of_birth, country_guideline, gender, blood_group, allergies))
    child_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return child_id

def get_child(child_id: int) -> Optional[Dict]:
    conn = get_user_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM child_profiles WHERE id = ?", (child_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_children(user_id: Optional[int] = None) -> List[Dict]:
    conn = get_user_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM child_profiles WHERE user_id = ? ORDER BY name", (user_id,))
    else:
        cursor.execute("SELECT * FROM child_profiles ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_child(child_id: int, **kwargs) -> bool:
    conn = get_user_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for key, value in kwargs.items():
        if key in ['name', 'date_of_birth', 'country_guideline', 'gender', 'blood_group', 'allergies']:
            fields.append(f"{key} = ?")
            values.append(value)
    if fields:
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(child_id)
        cursor.execute(f"UPDATE child_profiles SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    conn.close()
    return True

def delete_child(child_id: int) -> bool:
    conn = get_user_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM child_profiles WHERE id = ?", (child_id,))
    conn.commit()
    conn.close()
    return True

def log_email(user_id: int, child_id: int, recipient_email: str, subject: str, content: str, status: str = 'sent') -> int:
    """Log a sent email to the database."""
    conn = get_user_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO emails (user_id, child_id, recipient_email, subject, content, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, child_id, recipient_email, subject, content, status))
    email_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return email_id

def get_sent_emails(user_id: int = None, child_id: int = None) -> List[Dict]:
    """Retrieve sent emails, optionally filtered by user or child."""
    conn = get_user_connection()
    cursor = conn.cursor()
    
    if user_id and child_id:
        cursor.execute("SELECT * FROM emails WHERE user_id = ? AND child_id = ? ORDER BY sent_at DESC", (user_id, child_id))
    elif user_id:
        cursor.execute("SELECT * FROM emails WHERE user_id = ? ORDER BY sent_at DESC", (user_id,))
    elif child_id:
        cursor.execute("SELECT * FROM emails WHERE child_id = ? ORDER BY sent_at DESC", (child_id,))
    else:
        cursor.execute("SELECT * FROM emails ORDER BY sent_at DESC")
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_user_account(user_id: int) -> bool:
    import database as db
    conn = get_user_connection()
    cursor = conn.cursor()
    
    try:
        children = get_all_children(user_id)
        
        for child in children:
            db.delete_all_vaccinations(child['id'])
            db.delete_health_event(child['id']) if db.get_health_events(child['id']) else None
            reminder_settings = db.get_reminder_settings(child['id'])
            if reminder_settings:
                cursor.execute("DELETE FROM reminder_settings WHERE child_id = ?", (child['id'],))
            cursor.execute("DELETE FROM sent_reminders WHERE vaccination_id IN (SELECT id FROM vaccinations WHERE child_id = ?)", (child['id'],))
        
        cursor.execute("DELETE FROM emails WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM child_profiles WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user account: {e}")
        return False
    finally:
        conn.close()

init_user_database()
