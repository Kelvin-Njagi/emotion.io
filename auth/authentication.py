# auth/authentication.py

import streamlit as st
import hashlib
from datetime import datetime, timedelta
from database.db_manager import db
from auth.security import SecurityManager
import re

class AuthenticationManager:
    def __init__(self):
        self.security = SecurityManager()
    
    def register_user(self, username, email, full_name, password, confirm_password, security_question, security_answer):
        """Register a new user"""
        # Validate inputs
        if not username or not email or not full_name:
            return False, "All fields are required"
        
        if password != confirm_password:
            return False, "Passwords do not match"
        
        # Validate password strength
        password_errors = self.security.validate_password_strength(password)
        if password_errors:
            return False, "\n".join(password_errors)
        
        if not self.security.validate_email(email):
            return False, "Invalid email format"
        
        # Check if username exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return False, "Username already exists"
        
        # Check if email exists
        existing_email = db.get_user_by_email(email)
        if existing_email:
            return False, "Email already registered"
        
        # Hash password
        password_hash = self.security.hash_password(password)
        
        # Hash security answer for storage
        security_answer_hash = self.security.hash_password(security_answer.lower().strip())
        
        # Create user
        try:
            user_id = db.create_user(username, email, password_hash, full_name, security_question, security_answer_hash)
            db.add_log(user_id, username, "REGISTRATION", "User registered successfully", "SUCCESS")
            return True, "Registration successful! Please wait for admin approval."
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login(self, username, password, ip_address="127.0.0.1", user_agent="Unknown"):
        """Authenticate user and create session"""
        user = db.get_user_by_username(username)
        
        if not user:
            db.add_log(None, username, "LOGIN", "Login failed - user not found", "FAILED", ip_address)
            return False, "Invalid username or password", None
        
        # Check if account is locked
        if user['locked_until']:
            lock_until = datetime.fromisoformat(user['locked_until'])
            if lock_until > datetime.now():
                return False, f"Account is locked until {lock_until.strftime('%Y-%m-%d %H:%M:%S')}", None
        
        # Verify password
        if not self.security.verify_password(password, user['password_hash']):
            # Increment failed login attempts
            attempts = user['failed_login_attempts'] + 1
            db.update_failed_login(username, attempts)
            
            max_attempts = int(db.get_setting('max_login_attempts') or 5)
            if attempts >= max_attempts:
                lock_duration = int(db.get_setting('lockout_duration_minutes') or 15)
                lock_until = datetime.now() + timedelta(minutes=lock_duration)
                db.lock_user_account(username, lock_until.isoformat())
                db.add_log(user['id'], username, "LOGIN", f"Account locked due to {attempts} failed attempts", "LOCKED", ip_address)
                return False, f"Too many failed attempts. Account locked for {lock_duration} minutes.", None
            
            db.add_log(user['id'], username, "LOGIN", f"Login failed - invalid password (attempt {attempts})", "FAILED", ip_address)
            return False, "Invalid username or password", None
        
        # Check if user is approved
        if not user['is_approved']:
            db.add_log(user['id'], username, "LOGIN", "Login failed - account not approved", "PENDING", ip_address)
            return False, "Your account is pending admin approval", None
        
        # Check if user is active
        if not user['is_active']:
            db.add_log(user['id'], username, "LOGIN", "Login failed - account disabled", "DISABLED", ip_address)
            return False, "Your account has been disabled. Please contact administrator.", None
        
        # Reset failed login attempts
        db.update_failed_login(username, 0)
        db.update_last_login(user['id'])
        
        # Create session
        session_token = self.security.generate_session_token()
        db.create_session(user['id'], session_token, ip_address, user_agent)
        
        # Log successful login
        db.add_log(user['id'], username, "LOGIN", "User logged in successfully", "SUCCESS", ip_address)
        
        return True, "Login successful", session_token
    
    def logout(self, session_token):
        """Logout user and invalidate session"""
        session = db.get_session(session_token)
        if session:
            db.invalidate_session(session_token)
            db.add_log(session['user_id'], session['username'], "LOGOUT", "User logged out", "SUCCESS")
        return True
    
    def verify_session(self, session_token):
        """Verify if session is valid"""
        session = db.get_session(session_token)
        if not session:
            return None
        
        # Check session timeout
        timeout_minutes = int(db.get_setting('session_timeout_minutes') or 30)
        if session['last_activity']:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
                db.invalidate_session(session_token)
                return None
        
        # Update last activity
        db.update_session_activity(session_token)
        
        user = db.get_user_by_id(session['user_id'])
        return user
    
    def reset_password_with_security(self, username, security_answer, new_password):
        """Reset password using security question"""
        user = db.get_user_by_username(username)
        
        if not user:
            return False, "User not found"
        
        # Verify security answer
        if not self.security.verify_password(security_answer.lower().strip(), user['security_answer']):
            db.add_log(user['id'], username, "PASSWORD_RESET", "Password reset failed - incorrect security answer", "FAILED")
            return False, "Incorrect security answer"
        
        # Validate new password
        password_errors = self.security.validate_password_strength(new_password)
        if password_errors:
            return False, "\n".join(password_errors)
        
        # Update password
        new_password_hash = self.security.hash_password(new_password)
        db.reset_user_password(user['id'], new_password_hash)
        
        # Invalidate all sessions
        db.invalidate_user_sessions(user['id'])
        
        db.add_log(user['id'], username, "PASSWORD_RESET", "Password reset successfully", "SUCCESS")
        return True, "Password reset successful. Please login with your new password."