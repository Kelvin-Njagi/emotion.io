# utils/logger.py

import streamlit as st
from datetime import datetime
from database.db_manager import db
import traceback

class SystemLogger:
    @staticmethod
    def log_action(user_id, username, action_type, action_description, status="SUCCESS", ip_address=None, details=None):
        """Log system action"""
        try:
            db.add_log(user_id, username, action_type, action_description, status, ip_address, details)
        except Exception as e:
            print(f"Logging error: {e}")
    
    @staticmethod
    def log_error(user_id, username, error_type, error_message, stack_trace=None):
        """Log system error"""
        details = f"Error: {error_message}\nStack: {stack_trace}" if stack_trace else error_message
        SystemLogger.log_action(user_id, username, "ERROR", error_type, "FAILED", details=details[:500])
    
    @staticmethod
    def log_security_event(user_id, username, event_type, details):
        """Log security-related event"""
        SystemLogger.log_action(user_id, username, "SECURITY", event_type, "WARNING", details=details)
    
    @staticmethod
    def get_activity_summary(days=7):
        """Get activity summary for last N days"""
        logs = db.get_logs(limit=10000)
        
        if logs.empty:
            return {}
        
        # Filter by date
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        summary = {
            'total_actions': len(logs),
            'actions_by_type': logs['action_type'].value_counts().to_dict(),
            'success_rate': (len(logs[logs['status'] == 'SUCCESS']) / len(logs) * 100) if len(logs) > 0 else 0,
            'top_users': logs['username'].value_counts().head(5).to_dict()
        }
        
        return summary

# Initialize logger
system_logger = SystemLogger()