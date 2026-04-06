# database/db_manager.py

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

class DatabaseManager:
    def __init__(self, db_path="emotion_system.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with schema and seed defaults"""
        # Skip if database already exists and has tables
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            if cursor.fetchone():  # Tables already exist
                self.ensure_default_admin()
                return
        
        # Only load and execute schema on first run
        with open("database/schema.sql", "r") as f:
            schema = f.read()
        
        with self.get_connection() as conn:
            conn.executescript(schema)
        
        self.ensure_default_admin()
    
    def ensure_default_admin(self):
        """Ensure the default admin account exists and has the correct password."""
        default_admin = {
            "username": "admin",
            "email": "admin@emotionsystem.com",
            "password_hash": "$2b$12$k4AhQBJgfVgXJ0ftZHKy2eDagmmQrYgzpSHVLqabRix2oXA9ets96",
            "full_name": "System Administrator",
            "role": "admin",
        }
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (default_admin["username"],))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE users
                    SET email = ?, password_hash = ?, full_name = ?, role = ?, is_approved = 1, is_active = 1
                    WHERE username = ?
                """, (
                    default_admin["email"],
                    default_admin["password_hash"],
                    default_admin["full_name"],
                    default_admin["role"],
                    default_admin["username"]
                ))
            else:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name, role, is_approved, is_active)
                    VALUES (?, ?, ?, ?, ?, 1, 1)
                """, (
                    default_admin["username"],
                    default_admin["email"],
                    default_admin["password_hash"],
                    default_admin["full_name"],
                    default_admin["role"]
                ))
    
    # User operations
    def create_user(self, username, email, password_hash, full_name, security_question, security_answer):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, security_question, security_answer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, full_name, security_question, security_answer))
            return cursor.lastrowid
    
    def get_user_by_username(self, username):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()
    
    def get_user_by_email(self, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
    
    def update_user(self, user_id, **kwargs):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for key, value in kwargs.items():
                cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_id))
    
    def update_failed_login(self, username, attempts):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET failed_login_attempts = ? WHERE username = ?", (attempts, username))
    
    def lock_user_account(self, username, lock_until):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?", (lock_until, username))
    
    def update_last_login(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
    
    def get_all_users(self):
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT id, username, email, full_name, role, is_approved, is_active, created_at, last_login FROM users", conn)
    
    def approve_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_approved = 1 WHERE id = ?", (user_id,))
    
    def disable_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    
    def enable_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_id,))
    
    def delete_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    def reset_user_password(self, user_id, new_password_hash):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ?, last_password_reset = CURRENT_TIMESTAMP WHERE id = ?", (new_password_hash, user_id))
    
    # Session operations
    def create_session(self, user_id, session_token, ip_address, user_agent):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (user_id, session_token, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            """, (user_id, session_token, ip_address, user_agent))
            return cursor.lastrowid
    
    def get_session(self, session_token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_token = ? AND is_active = 1", (session_token,))
            return cursor.fetchone()
    
    def update_session_activity(self, session_token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_token = ?", (session_token,))
    
    def invalidate_session(self, session_token):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET is_active = 0 WHERE session_token = ?", (session_token,))
    
    def invalidate_user_sessions(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
    
    # Log operations
    def add_log(self, user_id, username, action_type, action_description, status, ip_address=None, details=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (user_id, username, action_type, action_description, status, ip_address, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, action_type, action_description, status, ip_address, details))
    
    def get_logs(self, limit=100):
        with self.get_connection() as conn:
            return pd.read_sql_query(f"""
                SELECT id, username, action_type, action_description, status, created_at 
                FROM system_logs 
                ORDER BY created_at DESC 
                LIMIT {limit}
            """, conn)
    
    # Emotion analysis operations
    def save_emotion_analysis(self, user_id, session_id, emotion_category, confidence_score, arousal_score, valence_score, audio_duration, call_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO emotion_analysis (user_id, session_id, emotion_category, confidence_score, arousal_score, valence_score, audio_duration, call_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, emotion_category, confidence_score, arousal_score, valence_score, audio_duration, call_id))
            return cursor.lastrowid
    
    def get_emotion_stats(self):
        with self.get_connection() as conn:
            stats = pd.read_sql_query("""
                SELECT 
                    emotion_category,
                    COUNT(*) as count,
                    AVG(confidence_score) as avg_confidence,
                    DATE(timestamp) as date
                FROM emotion_analysis
                GROUP BY emotion_category, DATE(timestamp)
                ORDER BY timestamp DESC
            """, conn)
            return stats
    
    def get_realtime_metrics(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(CASE WHEN emotion_category = 'Happy' THEN 1 ELSE 0 END) as satisfied,
                    SUM(CASE WHEN emotion_category = 'Angry' THEN 1 ELSE 0 END) as dissatisfied,
                    SUM(CASE WHEN emotion_category = 'Neutral' THEN 1 ELSE 0 END) as neutral,
                    AVG(confidence_score) as avg_conf
                FROM emotion_analysis
                WHERE timestamp >= datetime('now', '-1 hour')
            """)
            return cursor.fetchone()
    
    # Settings operations
    def get_setting(self, key):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def update_setting(self, key, value, updated_by):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE system_settings SET setting_value = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE setting_key = ?", (value, updated_by, key))


@st.cache_resource
def get_database():
    """Get cached database instance"""
    return DatabaseManager()

# Initialize database with caching
db = get_database()