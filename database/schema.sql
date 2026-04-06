-- database/schema.sql

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    is_approved BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until DATETIME,
    security_question TEXT,
    security_answer TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    last_password_reset DATETIME
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_token TEXT UNIQUE NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- System logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    action_type TEXT,
    action_description TEXT,
    status TEXT,
    ip_address TEXT,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Emotion analysis results table
CREATE TABLE IF NOT EXISTS emotion_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id TEXT,
    emotion_category TEXT,
    confidence_score REAL,
    arousal_score REAL,
    valence_score REAL,
    audio_duration REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    call_id TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Real-time metrics table
CREATE TABLE IF NOT EXISTS realtime_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_calls_analyzed INTEGER DEFAULT 0,
    satisfied_customers INTEGER DEFAULT 0,
    dissatisfied_customers INTEGER DEFAULT 0,
    neutral_customers INTEGER DEFAULT 0,
    avg_confidence REAL DEFAULT 0,
    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- System settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by INTEGER,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (password: Admin@123)
INSERT OR IGNORE INTO users (username, email, password_hash, full_name, role, is_approved, is_active)
VALUES ('admin', 'admin@emotionsystem.com', '$2b$12$k4AhQBJgfVgXJ0ftZHKy2eDagmmQrYgzpSHVLqabRix2oXA9ets96', 'System Administrator', 'admin', 1, 1);

-- Insert default settings
INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
VALUES 
    ('session_timeout_minutes', '30', 'Session timeout duration'),
    ('max_login_attempts', '5', 'Maximum failed login attempts before lock'),
    ('lockout_duration_minutes', '15', 'Account lockout duration'),
    ('realtime_update_seconds', '30', 'Real-time dashboard update interval');