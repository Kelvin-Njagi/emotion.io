# utils/realtime_analytics.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.db_manager import db
import time
import threading
import random

class RealtimeAnalytics:
    def __init__(self):
        self.update_interval = 30  # seconds
        self.cache = {}
        self.last_update = None
    
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def get_dashboard_metrics(_self):
        """Get real-time dashboard metrics with caching"""
        metrics = db.get_realtime_metrics()
        
        if metrics:
            total = metrics['total_calls'] or 0
            satisfied = metrics['satisfied'] or 0
            dissatisfied = metrics['dissatisfied'] or 0
            neutral = metrics['neutral'] or 0
            
            satisfaction_rate = (satisfied / total * 100) if total > 0 else 0
            
            return {
                'total_calls_analyzed': total,
                'satisfied_customers': satisfied,
                'dissatisfied_customers': dissatisfied,
                'neutral_customers': neutral,
                'satisfaction_rate': satisfaction_rate,
                'avg_confidence': metrics['avg_conf'] or 0,
                'timestamp': datetime.now()
            }
        
        return {
            'total_calls_analyzed': 0,
            'satisfied_customers': 0,
            'dissatisfied_customers': 0,
            'neutral_customers': 0,
            'satisfaction_rate': 0,
            'avg_confidence': 0,
            'timestamp': datetime.now()
        }
    
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def get_emotion_trends(_self, hours=24):
        """Get emotion trends over time with caching"""
        emotion_stats = db.get_emotion_stats()
        
        if emotion_stats.empty:
            return pd.DataFrame()
        
        # Convert date to datetime
        emotion_stats['date'] = pd.to_datetime(emotion_stats['date'])
        
        # Filter last N hours
        cutoff = datetime.now() - timedelta(hours=hours)
        emotion_stats = emotion_stats[emotion_stats['date'] >= cutoff]
        
        return emotion_stats
    
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def get_performance_metrics(_self):
        """Get system performance metrics with caching"""
        logs = db.get_logs(limit=1000)
        
        metrics = {
            'total_logins': len(logs[logs['action_type'] == 'LOGIN']),
            'successful_logins': len(logs[(logs['action_type'] == 'LOGIN') & (logs['status'] == 'SUCCESS')]),
            'failed_logins': len(logs[(logs['action_type'] == 'LOGIN') & (logs['status'] == 'FAILED')]),
            'total_analyses': len(db.get_emotion_stats()),
        }
        
        return metrics
    
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def get_advanced_metrics(_self):
        """Get advanced analytics metrics with caching"""
        metrics = _self.get_dashboard_metrics()

        # Add advanced calculations
        emotion_stats = db.get_emotion_stats()
        if not emotion_stats.empty:
            # Calculate trends
            hourly_trends = emotion_stats.groupby(['date', 'emotion_category'])['count'].sum().unstack().fillna(0)
            trend_analysis = {
                'peak_emotion': emotion_stats.groupby('emotion_category')['count'].sum().idxmax(),
                'avg_confidence': emotion_stats['avg_confidence'].mean(),
                'total_sessions': len(emotion_stats),
                'most_active_hour': emotion_stats['date'].dt.hour.mode().iloc[0] if len(emotion_stats) > 0 else 0
            }
        else:
            trend_analysis = {
                'peak_emotion': 'N/A',
                'avg_confidence': 0,
                'total_sessions': 0,
                'most_active_hour': 0
            }

        # System performance metrics
        logs = db.get_logs(limit=1000)
        performance = {
            'uptime_percentage': 99.9,  # Mock
            'avg_response_time': 0.25,  # Mock
            'error_rate': len(logs[logs['status'] == 'FAILED']) / len(logs) * 100 if len(logs) > 0 else 0,
            'active_users': len(db.get_all_users()[db.get_all_users()['is_active'] == 1])
        }

        return {
            **metrics,
            'trend_analysis': trend_analysis,
            'performance': performance,
            'alerts_count': 3,  # Mock
            'system_health': 85  # Mock
        }

@st.cache_data(ttl=120)  # Cache for 120 seconds (longer for predictive data)
    def get_predictive_insights(_self):
        """Generate predictive analytics insights with caching"""
        # Mock predictive data
        predictions = {
            'next_hour_load': random.randint(10, 50),
            'peak_hours': ['9-11 AM', '2-4 PM', '6-8 PM'],
            'satisfaction_forecast': random.uniform(75, 90),
            'risk_level': random.choice(['Low', 'Medium', 'High']),
            'recommended_actions': [
                'Increase agent staffing during peak hours',
                'Enable priority routing for angry customers',
                'Schedule maintenance during low-traffic periods'
            ]
        }
        return predictions

    @st.cache_data(ttl=120)  # Cache for 120 seconds
    def get_user_performance_metrics(_self, user_id):
        """Get personalized performance metrics for a user with caching"""
        # Mock user-specific metrics
        return {
            'total_analyses': random.randint(50, 200),
            'accuracy_score': random.uniform(0.8, 0.95),
            'avg_confidence': random.uniform(0.75, 0.92),
            'processing_speed': random.uniform(0.15, 0.35),
            'rank': random.randint(1, 20),
            'achievements': ['Accuracy Master', 'Speed Demon', 'Emotion Expert']
        }

@st.cache_resource
def get_realtime_analytics():
    """Get cached realtime analytics instance"""
    return RealtimeAnalytics()

# Initialize realtime analytics with caching
realtime_analytics = get_realtime_analytics()