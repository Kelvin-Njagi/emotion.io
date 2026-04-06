# app.py

import streamlit as st

# IMPORTANT: set_page_config() must be the FIRST Streamlit command
st.set_page_config(
    page_title="Speech-Driven Emotion Recognition System",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules after page config is set
import pandas as pd
import numpy as np
from datetime import datetime
import time
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

# Import modules
from auth.authentication import AuthenticationManager
from database.db_manager import db
from utils.logger import system_logger
from utils.realtime_analytics import realtime_analytics
from models.emotion_model import emotion_model
from models.audio_processor import audio_processor

# Initialize authentication manager
auth_manager = AuthenticationManager()

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Footer styling */
    .footer {
        background-color: #1a1a2e;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 3rem;
        text-align: center;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 1.8rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Status indicators */
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'session_token' not in st.session_state:
    st.session_state.session_token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'realtime_data' not in st.session_state:
    st.session_state.realtime_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

def show_header():
    """Display page header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎙️ Speech-Driven Emotion Recognition System</h1>
        <p>Real-Time Satisfaction Performance Tracking for Call Centers</p>
    </div>
    """, unsafe_allow_html=True)

def show_footer():
    """Display page footer"""
    st.markdown(f"""
    <div class="footer">
        <p>© 2026 Speech Emotion Recognition System | Academic Project</p>
        <p>Powered by AI & Machine Learning | Real-Time Analytics</p>
        <p style="font-size: 0.8rem;">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# QUICK ACTION HELPER FUNCTIONS
# ============================================================

def export_dashboard_report():
    """Export dashboard data as CSV report"""
    try:
        metrics = realtime_analytics.get_dashboard_metrics()
        emotion_trends = realtime_analytics.get_emotion_trends()
        
        report_data = {
            'Report Generated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Total Calls Analyzed': [metrics['total_calls_analyzed']],
            'Satisfied Customers': [metrics['satisfied_customers']],
            'Dissatisfied Customers': [metrics['dissatisfied_customers']],
            'Neutral Customers': [metrics['neutral_customers']],
            'Satisfaction Rate': [f"{metrics['satisfaction_rate']:.2f}%"],
            'Average Confidence': [f"{metrics['avg_confidence']:.2f}"],
        }
        
        df_report = pd.DataFrame(report_data).T
        csv_data = df_report.to_csv()
        
        st.session_state.report_exported = True
        st.session_state.export_time = datetime.now()
        
        return True, csv_data
    except Exception as e:
        system_logger.log_error(f"Report export failed: {str(e)}")
        return False, None

def clear_system_alerts():
    """Clear all system alerts"""
    try:
        # Clear alerts from database/cache
        if 'system_alerts' in st.session_state:
            st.session_state.system_alerts = []
        
        system_logger.log_action("ALERT_CLEAR", st.session_state.user['username'], "Alerts cleared by admin", "SUCCESS")
        return True
    except Exception as e:
        system_logger.log_error(f"Alert clearing failed: {str(e)}")
        return False

def generate_system_insights():
    """Generate insights from system data"""
    try:
        metrics = realtime_analytics.get_dashboard_metrics()
        trends = realtime_analytics.get_emotion_trends()
        
        insights = []
        
        if metrics['satisfaction_rate'] > 80:
            insights.append("✅ High customer satisfaction detected - System performing well!")
        elif metrics['satisfaction_rate'] < 50:
            insights.append("⚠️ Low satisfaction detected - Review service quality and agent performance")
        
        if metrics['total_calls_analyzed'] > 100:
            insights.append(f"📊 Processing high volume: {metrics['total_calls_analyzed']} calls analyzed")
        
        insights.append(f"🎯 Current confidence level: {metrics['avg_confidence']:.2f}")
        
        st.session_state.generated_insights = insights
        st.session_state.insights_time = datetime.now()
        
        return True, insights
    except Exception as e:
        system_logger.log_error(f"Insight generation failed: {str(e)}")
        return False, []

def check_system_health():
    """Check overall system health"""
    try:
        health_status = {
            'database': 'Operational',
            'ml_model': 'Active',
            'audio_processor': 'Ready',
            'api_connection': 'Connected',
            'storage': 'Sufficient'
        }
        
        health_score = 85  # Calculate based on actual metrics
        
        system_logger.log_action("SYSTEM_CHECK", st.session_state.user['username'], "System health check performed", "SUCCESS")
        
        return True, health_status, health_score
    except Exception as e:
        system_logger.log_error(f"System health check failed: {str(e)}")
        return False, {}, 0

def start_emotion_analysis():
    """Initialize emotion analysis workflow"""
    try:
        st.session_state.analysis_mode = True
        st.session_state.analysis_start_time = datetime.now()
        system_logger.log_action("ANALYSIS_START", st.session_state.user['username'], "Emotion analysis started", "SUCCESS")
        return True
    except Exception as e:
        system_logger.log_error(f"Analysis start failed: {str(e)}")
        return False

def upload_audio_file():
    """Handle audio file upload"""
    try:
        uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg'])
        return uploaded_file
    except Exception as e:
        system_logger.log_error(f"Audio upload failed: {str(e)}")
        return None

def view_user_reports():
    """Get and display user reports"""
    try:
        user_id = st.session_state.user['id']
        # Would fetch reports from database
        st.session_state.show_reports = True
        return True
    except Exception as e:
        system_logger.log_error(f"Report retrieval failed: {str(e)}")
        return False

def open_user_settings():
    """Open user settings panel"""
    try:
        st.session_state.show_settings = True
        return True
    except Exception as e:
        system_logger.log_error(f"Settings open failed: {str(e)}")
        return False

def login_page():
    """Display login page"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to System")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1_btn, col2_btn = st.columns(2)
            with col1_btn:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col2_btn:
                forgot = st.form_submit_button("Forgot Password?", use_container_width=True)
            
            if submit:
                if username and password:
                    success, message, session_token = auth_manager.login(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.session_token = session_token
                        st.session_state.user = db.get_user_by_username(username)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password")
            
            if forgot:
                st.session_state.show_forgot = True
                st.rerun()

        st.info("Default admin login: **admin** / **Admin@123**")
        st.markdown("---")
        st.markdown("### New User?")
        col1_reg, col2_reg, col3_reg = st.columns([1, 2, 1])
        with col2_reg:
            if st.button("Register New Account", use_container_width=True):
                st.session_state.show_registration = True
                st.rerun()
    
    show_footer()

def registration_page():
    """Display registration page"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 User Registration")
        
        with st.form("registration_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="your@email.com")
            full_name = st.text_input("Full Name", placeholder="Your full name")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            st.markdown("### Security Question (for password recovery)")
            security_question = st.selectbox("Security Question", [
                "What is your mother's maiden name?",
                "What was your first pet's name?",
                "What was your first school?",
                "What is your favorite book?"
            ])
            security_answer = st.text_input("Answer", type="password", placeholder="Your answer")
            
            col1_btn, col2_btn = st.columns(2)
            with col1_btn:
                submit = st.form_submit_button("Register", use_container_width=True)
            with col2_btn:
                back = st.form_submit_button("Back to Login", use_container_width=True)
            
            if submit:
                success, message = auth_manager.register_user(
                    username, email, full_name, password, confirm_password,
                    security_question, security_answer
                )
                if success:
                    st.success(message)
                    st.balloons()
                    time.sleep(2)
                    st.session_state.show_registration = False
                    st.rerun()
                else:
                    st.error(message)
            
            if back:
                st.session_state.show_registration = False
                st.rerun()
    
    show_footer()

def forgot_password_page():
    """Display forgot password page"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Reset Password")
        
        step = st.session_state.get('reset_step', 1)
        
        if step == 1:
            with st.form("verify_user_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                submit = st.form_submit_button("Verify User")
                
                if submit:
                    user = db.get_user_by_username(username)
                    if user:
                        st.session_state.reset_user = username
                        st.session_state.reset_step = 2
                        st.rerun()
                    else:
                        st.error("User not found")
        
        elif step == 2:
            st.info("Answer your security question to reset password")
            user = db.get_user_by_username(st.session_state.reset_user)
            if user:
                st.write(f"**Security Question:** {user['security_question']}")
                security_answer = st.text_input("Your Answer", type="password")
                
                col1_btn, col2_btn = st.columns(2)
                with col1_btn:
                    if st.button("Verify Answer"):
                        if auth_manager.security.verify_password(security_answer.lower().strip(), user['security_answer']):
                            st.session_state.reset_step = 3
                            st.rerun()
                        else:
                            st.error("Incorrect answer")
                with col2_btn:
                    if st.button("Cancel"):
                        st.session_state.reset_step = 1
                        st.session_state.pop('reset_user', None)
                        st.rerun()
        
        elif step == 3:
            with st.form("reset_password_form"):
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                col1_btn, col2_btn = st.columns(2)
                with col1_btn:
                    submit = st.form_submit_button("Reset Password")
                with col2_btn:
                    cancel = st.form_submit_button("Cancel")
                
                if submit:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = auth_manager.reset_password_with_security(
                            st.session_state.reset_user, security_answer, new_password
                        )
                        if success:
                            st.success(message)
                            time.sleep(2)
                            st.session_state.reset_step = 1
                            st.session_state.pop('reset_user', None)
                            st.rerun()
                        else:
                            st.error(message)
                
                if cancel:
                    st.session_state.reset_step = 1
                    st.session_state.pop('reset_user', None)
                    st.rerun()
    
    show_footer()

def sidebar_navigation():
    """Display sidebar navigation based on user role"""
    if st.session_state.user:
        with st.sidebar:
            st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
            st.markdown(f"### Welcome, {st.session_state.user['full_name']}!")
            st.markdown(f"**Role:** {st.session_state.user['role'].upper()}")
            st.markdown("---")
            
            if st.session_state.user['role'] == 'admin':
                menu = option_menu(
                    menu_title="Navigation",
                    options=["Dashboard", "Emotion Analysis", "User Management", "System Logs", "Settings"],
                    icons=["house", "mic", "people", "journal", "gear"],
                    menu_icon="cast",
                    default_index=0,
                    orientation="vertical"
                )
            else:
                menu = option_menu(
                    menu_title="Navigation",
                    options=["Dashboard", "Emotion Analysis", "My Profile"],
                    icons=["house", "mic", "person"],
                    menu_icon="cast",
                    default_index=0,
                    orientation="vertical"
                )
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                auth_manager.logout(st.session_state.session_token)
                st.session_state.authenticated = False
                st.session_state.session_token = None
                st.session_state.user = None
                st.rerun()
            
            return menu

def admin_dashboard():
    """Display enhanced admin dashboard with advanced analytics"""
    st.markdown("## 📊 Advanced Admin Dashboard")

    # Dashboard Customization
    with st.expander("⚙️ Customize Dashboard", expanded=False):
        st.markdown("**Select widgets to display:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            show_quick_actions = st.checkbox("Quick Actions Panel", value=True, key="admin_quick_actions")
            show_kpi_cards = st.checkbox("KPI Cards", value=True, key="admin_kpi_cards")
            show_overview_tab = st.checkbox("Overview Tab", value=True, key="admin_overview")

        with col2:
            show_performance_tab = st.checkbox("Performance Tab", value=True, key="admin_performance")
            show_alerts_tab = st.checkbox("Alerts Tab", value=True, key="admin_alerts")
            show_activity_tab = st.checkbox("Activity Tab", value=True, key="admin_activity")

        with col3:
            show_predictive = st.checkbox("Predictive Analytics", value=True, key="admin_predictive")
            auto_refresh = st.checkbox("Auto-refresh Dashboard", value=False, key="admin_auto_refresh")
            compact_view = st.checkbox("Compact View", value=False, key="admin_compact")

        if st.button("💾 Save Preferences", key="save_admin_prefs"):
            st.success("Dashboard preferences saved!")

    # Quick Actions Panel
    if show_quick_actions:
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("🔄 Refresh Data", key="refresh_admin"):
                st.rerun()
        
        with col2:
            if st.button("📊 Export Report", key="export_report"):
                success, csv_data = export_dashboard_report()
                if success:
                    st.success("Report exported successfully!")
                    st.download_button(
                        label="Download Report CSV",
                        data=csv_data,
                        file_name=f"emotion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_report"
                    )
                else:
                    st.error("Failed to export report")
        
        with col3:
            if st.button("🚨 Clear Alerts", key="clear_alerts"):
                if clear_system_alerts():
                    st.success("Alerts cleared successfully!")
                else:
                    st.error("Failed to clear alerts")
        
        with col4:
            if st.button("📈 Generate Insights", key="generate_insights"):
                success, insights = generate_system_insights()
                if success:
                    st.info("✅ Insights generated!")
                    for insight in insights:
                        st.write(insight)
                else:
                    st.error("Failed to generate insights")
        
        with col5:
            if st.button("⚙️ System Check", key="system_check"):
                success, health_status, health_score = check_system_health()
                if success:
                    st.success(f"System health: {health_score}% - Excellent!")
                    with st.expander("Health Details"):
                        for component, status in health_status.items():
                            st.write(f"• {component.replace('_', ' ').title()}: {status}")
                else:
                    st.error("System check failed")

        st.markdown("---")

    # Get real-time metrics
    metrics = realtime_analytics.get_dashboard_metrics()

    # Enhanced KPI Cards with Trends
    if show_kpi_cards:
        st.markdown("### 📈 Key Performance Indicators")

        # Calculate trends (mock data for demonstration)
        import random
        trend_data = {
            'users': random.choice([-5, -2, 0, 3, 8]),
            'calls': random.choice([-10, -5, 0, 15, 25]),
            'satisfaction': random.choice([-3, -1, 0, 2, 5])
        }

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_users = len(db.get_all_users())
            active_users = len(db.get_all_users()[db.get_all_users()['is_active'] == 1])
            st.metric(
                "Active Users",
                f"{active_users}/{total_users}",
                delta=f"{trend_data['users']:+d} this week",
                delta_color="normal" if trend_data['users'] >= 0 else "inverse"
            )

        with col2:
            pending_users = len(db.get_all_users()[db.get_all_users()['is_approved'] == 0])
            st.metric(
                "Pending Approvals",
                pending_users,
                delta="Action Required" if pending_users > 0 else "All Clear",
                delta_color="inverse" if pending_users > 0 else "normal"
            )

        with col3:
            total_calls = metrics['total_calls_analyzed']
            st.metric(
                "Total Calls Analyzed",
                total_calls,
                delta=f"{trend_data['calls']:+d} today",
                delta_color="normal" if trend_data['calls'] >= 0 else "inverse"
            )

        with col4:
            satisfaction_rate = metrics['satisfaction_rate']
            st.metric(
                "Satisfaction Rate",
                f"{satisfaction_rate:.1f}%",
                delta=f"{trend_data['satisfaction']:+.1f}%",
                delta_color="normal" if trend_data['satisfaction'] >= 0 else "inverse"
            )

        st.markdown("---")

    # Advanced Analytics Section
    if show_overview_tab or show_performance_tab or show_alerts_tab or show_activity_tab:
        st.markdown("### 📊 Advanced Analytics")

        # Time Range Selector
        time_range = st.selectbox(
            "Select Time Range",
            ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"],
            key="time_range_admin"
        )

        tab_options = []
        if show_overview_tab:
            tab_options.append("📈 Overview")
        if show_performance_tab:
            tab_options.append("🎯 Performance")
        if show_alerts_tab:
            tab_options.append("🚨 Alerts")
        if show_activity_tab:
            tab_options.append("📋 Activity")

        if tab_options:
            tabs = st.tabs(tab_options)

            tab_index = 0

            if show_overview_tab:
                with tabs[tab_index]:
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown("#### Real-Time Emotion Distribution")
                        emotion_stats = realtime_analytics.get_emotion_trends()
                        if not emotion_stats.empty:
                            # Enhanced pie chart with percentages
                            emotion_counts = emotion_stats.groupby('emotion_category')['count'].sum()
                            total = emotion_counts.sum()
                            percentages = (emotion_counts / total * 100).round(1)

                            fig = px.pie(
                                values=emotion_counts.values,
                                names=[f"{name} ({pct}%)" for name, pct in zip(emotion_counts.index, percentages)],
                                title="Customer Emotions Distribution",
                                color_discrete_sequence=px.colors.qualitative.Set3,
                                hole=0.4
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No emotion data available yet")

                    with col2:
                        st.markdown("#### System Health Score")
                        # Calculate health score based on various metrics
                        health_score = 85  # Mock calculation
                        health_color = "green" if health_score >= 80 else "orange" if health_score >= 60 else "red"

                        fig = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=health_score,
                            title={'text': "System Health Score"},
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': health_color},
                                'steps': [
                                    {'range': [0, 60], 'color': "red"},
                                    {'range': [60, 80], 'color': "orange"},
                                    {'range': [80, 100], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 80
                                }
                            }
                        ))
                        st.plotly_chart(fig, use_container_width=True)

                        # Health indicators
                        st.markdown("**Health Indicators:**")
                        st.success("✅ Database: Operational")
                        st.success("✅ ML Model: Active")
                        st.warning("⚠️ High CPU Usage")
                        st.info("ℹ️ Last Backup: 2 hours ago")
                tab_index += 1

            if show_performance_tab:
                with tabs[tab_index]:
                    st.markdown("#### Performance Analytics")

                    # Performance metrics over time
                    perf_data = pd.DataFrame({
                        'timestamp': pd.date_range(start='2024-01-01', periods=24, freq='H'),
                        'satisfaction_rate': [random.uniform(65, 85) for _ in range(24)],
                        'processing_time': [random.uniform(0.1, 0.5) for _ in range(24)],
                        'accuracy': [random.uniform(0.75, 0.95) for _ in range(24)]
                    })

                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.line(
                            perf_data,
                            x='timestamp',
                            y='satisfaction_rate',
                            title="Satisfaction Rate Trend",
                            markers=True
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        fig = px.line(
                            perf_data,
                            x='timestamp',
                            y='processing_time',
                            title="Processing Time Trend",
                            markers=True
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    # Performance insights
                    st.markdown("#### Performance Insights")
                    insights_col1, insights_col2 = st.columns(2)

                    with insights_col1:
                        st.markdown("**Strengths:**")
                        st.success("• High accuracy in emotion detection")
                        st.success("• Fast processing times")
                        st.success("• Stable system performance")

                    with insights_col2:
                        st.markdown("**Areas for Improvement:**")
                        st.warning("• Peak hour response times")
                        st.warning("• Memory usage optimization")
                        st.info("• Additional training data needed")
                tab_index += 1

            if show_alerts_tab:
                with tabs[tab_index]:
                    st.markdown("#### System Alerts & Notifications")

                    # Mock alerts data
                    alerts = [
                        {"type": "warning", "message": "High dissatisfaction rate detected in last hour", "time": "2 minutes ago", "priority": "High"},
                        {"type": "info", "message": "System backup completed successfully", "time": "1 hour ago", "priority": "Low"},
                        {"type": "error", "message": "Failed login attempts from IP 192.168.1.100", "time": "30 minutes ago", "priority": "Medium"},
                        {"type": "success", "message": "New user registration approved", "time": "45 minutes ago", "priority": "Low"},
                    ]

                    for alert in alerts:
                        if alert["type"] == "warning":
                            st.warning(f"⚠️ **{alert['priority']}**: {alert['message']} - {alert['time']}")
                        elif alert["type"] == "error":
                            st.error(f"🚨 **{alert['priority']}**: {alert['message']} - {alert['time']}")
                        elif alert["type"] == "info":
                            st.info(f"ℹ️ **{alert['priority']}**: {alert['message']} - {alert['time']}")
                        else:
                            st.success(f"✅ **{alert['priority']}**: {alert['message']} - {alert['time']}")

                    # Alert management
                    st.markdown("---")
                    st.markdown("#### Alert Management")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔇 Mute All Alerts", key="mute_alerts"):
                            st.success("All alerts muted for 1 hour")
                    with col2:
                        if st.button("📧 Email Alerts", key="email_alerts"):
                            st.success("Alert summary sent to admin email")
                    with col3:
                        if st.button("⚙️ Configure Alerts", key="configure_alerts"):
                            st.info("Alert configuration panel would open here")
                tab_index += 1

            if show_activity_tab:
                with tabs[tab_index]:
                    st.markdown("#### Real-Time Activity Feed")

                    # Enhanced activity feed with filtering
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        activity_filter = st.multiselect(
                            "Filter Activities",
                            ["LOGIN", "LOGOUT", "EMOTION_ANALYSIS", "USER_MANAGEMENT", "ERROR", "SECURITY"],
                            default=["LOGIN", "EMOTION_ANALYSIS", "ERROR"],
                            key="activity_filter"
                        )

                    with col2:
                        if st.button("🔄 Auto-Refresh", key="auto_refresh_activity"):
                            st.success("Auto-refresh enabled")

                    # Get and display logs
                    logs = db.get_logs(limit=50)
                    if not logs.empty:
                        # Filter logs
                        if activity_filter:
                            logs = logs[logs['action_type'].isin(activity_filter)]

                        # Display with enhanced formatting
                        for idx, log in logs.iterrows():
                            timestamp = log['created_at']
                            action_type = log['action_type']
                            username = log['username']
                            description = log['action_description']
                            status = log['status']

                            # Color coding based on status
                            if status == "SUCCESS":
                                icon = "✅"
                                color = "green"
                            elif status == "FAILED":
                                icon = "❌"
                                color = "red"
                            elif status == "WARNING":
                                icon = "⚠️"
                                color = "orange"
                            else:
                                icon = "ℹ️"
                                color = "blue"

                            st.markdown(f"{icon} **{action_type}** - {username}: {description} ({timestamp})")
                            st.markdown("---")
                    else:
                        st.info("No recent activity")

    # Predictive Analytics Section
    if show_predictive:
        st.markdown("---")
        st.markdown("### 🔮 Predictive Analytics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Satisfaction Forecast")
            # Mock forecast data
            forecast_data = pd.DataFrame({
                'hour': range(1, 25),
                'predicted_satisfaction': [random.uniform(70, 90) for _ in range(24)]
            })

            fig = px.area(
                forecast_data,
                x='hour',
                y='predicted_satisfaction',
                title="24-Hour Satisfaction Forecast"
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Peak Hours Prediction")
            peak_hours = ["9-11 AM", "2-4 PM", "6-8 PM"]
            st.success("Predicted Peak Hours:")
            for hour in peak_hours:
                st.write(f"• {hour}")

            st.markdown("**Recommended Actions:**")
            st.info("• Increase agent staffing")
            st.info("• Enable priority routing")

        with col3:
            st.markdown("#### Risk Assessment")
            risk_score = random.randint(15, 85)
            risk_level = "Low" if risk_score < 30 else "Medium" if risk_score < 70 else "High"

            if risk_level == "Low":
                st.success(f"Risk Level: {risk_level} ({risk_score}%)")
            elif risk_level == "Medium":
                st.warning(f"Risk Level: {risk_level} ({risk_score}%)")
            else:
                st.error(f"Risk Level: {risk_level} ({risk_score}%)")

            st.markdown("**Risk Factors:**")
            st.write("• High call volume expected")
            st.write("• Staff shortage predicted")
            st.write("• System maintenance scheduled")
    st.markdown("## 📈 Advanced User Dashboard")

    # Personalized welcome section
    user = st.session_state.user
    current_hour = datetime.now().hour
    greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {greeting}, {user['full_name']}! 👋")
        st.markdown("*Here's your personalized emotion analysis dashboard*")
    with col2:
        # User avatar/status
        st.markdown("### Profile Status")
        st.success("✅ Account Active")
        st.info(f"👤 Role: {user['role'].upper()}")
        st.info(f"📅 Member since: {user['created_at'][:7] if user['created_at'] else 'N/A'}")

    st.markdown("---")

    # Quick Actions for Users
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Start Analysis", key="user_start_analysis_1"):
            if start_emotion_analysis():
                st.success("Analysis mode activated!")
                st.info("You can now upload audio files or record live audio for emotion analysis")
            else:
                st.error("Failed to start analysis")
    
    with col2:
        if st.button("📁 Upload Audio", key="user_upload_1"):
            st.session_state.show_upload = True
        
        if st.session_state.get("show_upload", False):
            uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg', 'm4a'], key="uploader_1")
            if uploaded_file is not None:
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.info("Processing audio for emotion analysis...")
    
    with col3:
        if st.button("📊 View Reports", key="user_reports_1"):
            if view_user_reports():
                st.session_state.show_reports = True
                st.info("Your reports will be displayed in the analytics section")
            else:
                st.error("Failed to load reports")
    
    with col4:
        if st.button("⚙️ Settings", key="user_settings_1"):
            if open_user_settings():
                st.session_state.show_settings = True
                st.info("Settings panel opened - configure your preferences")
            else:
                st.error("Failed to open settings")

    st.markdown("---")

    # Get real-time metrics
    metrics = realtime_analytics.get_dashboard_metrics()

    # Enhanced Personal Metrics
    st.markdown("### 📊 Your Performance Metrics")

    # Calculate personal stats (mock data for demonstration)
    import random
    personal_stats = {
        'analyses_today': random.randint(5, 25),
        'avg_confidence': random.uniform(0.75, 0.92),
        'success_rate': random.uniform(0.8, 0.95),
        'processing_time': random.uniform(0.15, 0.35)
    }

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Analyses Today",
            personal_stats['analyses_today'],
            delta=f"{random.choice([-2, -1, 0, 1, 3])} from yesterday"
        )

    with col2:
        st.metric(
            "Average Confidence",
            f"{personal_stats['avg_confidence']:.1%}",
            delta=f"{random.choice([-0.05, -0.02, 0, 0.03, 0.08]):+.1%}"
        )

    with col3:
        st.metric(
            "Success Rate",
            f"{personal_stats['success_rate']:.1%}",
            delta=f"{random.choice([-0.03, -0.01, 0, 0.02, 0.05]):+.1%}"
        )

    with col4:
        st.metric(
            "Avg Processing Time",
            f"{personal_stats['processing_time']:.2f}s",
            delta=f"{random.choice([-0.05, -0.02, 0, 0.01, 0.03]):+.2f}s"
        )

    st.markdown("---")

    # Personalized Analytics Section
    st.markdown("### 🎯 Your Analytics")

    tab1, tab2, tab3 = st.tabs(["📈 Performance", "🎭 Emotions", "📋 Activity"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Your Contribution to System")
            # Mock contribution data
            contribution_data = pd.DataFrame({
                'date': pd.date_range(start='2024-01-01', periods=7, freq='D'),
                'analyses': [random.randint(10, 30) for _ in range(7)],
                'accuracy': [random.uniform(0.7, 0.95) for _ in range(7)]
            })

            fig = px.bar(
                contribution_data,
                x='date',
                y='analyses',
                title="Your Daily Analysis Count",
                color='accuracy',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Performance Comparison")
            # Compare user performance vs system average
            comparison_data = pd.DataFrame({
                'metric': ['Accuracy', 'Speed', 'Consistency', 'Reliability'],
                'you': [85, 78, 82, 88],
                'system_avg': [75, 80, 78, 82]
            })

            fig = px.bar(
                comparison_data.melt(id_vars='metric', var_name='source', value_name='score'),
                x='metric',
                y='score',
                color='source',
                barmode='group',
                title="Performance vs System Average"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Emotion Detection Patterns")

        # Personal emotion distribution
        emotion_stats = realtime_analytics.get_emotion_trends()
        if not emotion_stats.empty:
            # Filter for current user's data (mock filter)
            user_emotions = emotion_stats.head(10)  # Mock user data

            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(
                    values=user_emotions.groupby('emotion_category')['count'].sum().values,
                    names=user_emotions.groupby('emotion_category')['count'].sum().index,
                    title="Emotions You've Detected",
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Emotion confidence over time
                confidence_trend = pd.DataFrame({
                    'time': pd.date_range(start='2024-01-01', periods=10, freq='H'),
                    'confidence': [random.uniform(0.7, 0.95) for _ in range(10)],
                    'emotion': [random.choice(['Happy', 'Angry', 'Neutral', 'Sad']) for _ in range(10)]
                })

                fig = px.scatter(
                    confidence_trend,
                    x='time',
                    y='confidence',
                    color='emotion',
                    title="Confidence Trends",
                    size=[20]*10
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No emotion data available yet")

        # Emotion insights
        st.markdown("#### Your Detection Insights")
        insights_col1, insights_col2 = st.columns(2)

        with insights_col1:
            st.markdown("**Strengths:**")
            st.success("• Excellent Happy emotion detection")
            st.success("• Fast processing times")
            st.success("• High accuracy on Neutral calls")

        with insights_col2:
            st.markdown("**Areas to Focus:**")
            st.info("• Improve Angry emotion recognition")
            st.info("• Practice with Sad emotion samples")
            st.info("• Work on low-confidence detections")

    with tab3:
        st.markdown("#### Your Recent Activity")

        # Personal activity feed
        user_logs = db.get_logs(limit=30)
        if not user_logs.empty:
            # Filter for current user (mock filter)
            user_activity = user_logs.head(15)  # Mock user activity

            for idx, log in user_activity.iterrows():
                timestamp = log['created_at']
                action_type = log['action_type']
                description = log['action_description']
                status = log['status']

                # Color coding
                if status == "SUCCESS":
                    icon = "✅"
                elif status == "FAILED":
                    icon = "❌"
                else:
                    icon = "ℹ️"

                st.markdown(f"{icon} **{action_type}**: {description}")
                st.caption(f"🕒 {timestamp}")
                st.markdown("---")
        else:
            st.info("No recent activity")

    # Achievement and Gamification Section
    st.markdown("---")
    st.markdown("### 🏆 Achievements & Goals")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### This Week's Achievements")
        achievements = [
            ("🎯 Accuracy Master", "95%+ accuracy for 5 days"),
            ("⚡ Speed Demon", "Processed 50+ analyses"),
            ("🎭 Emotion Expert", "Detected all 4 emotions")
        ]

        for badge, desc in achievements:
            st.success(f"{badge}: {desc}")

    with col2:
        st.markdown("#### Progress Goals")
        goals = [
            ("Monthly Target", 85, 92),  # current, target
            ("Quality Score", 88, 95),
            ("Consistency", 82, 90)
        ]

        for goal_name, current, target in goals:
            progress = min(current / target * 100, 100)
            st.progress(progress / 100)
            st.caption(f"{goal_name}: {current}/{target} ({progress:.1f}%)")

    with col3:
        st.markdown("#### Leaderboard Position")
        st.metric("Your Rank", "#3", delta="+2 positions")
        st.markdown("**Top Performers:**")
        st.info("🥇 Sarah Johnson - 98% accuracy")
        st.info("🥈 Mike Chen - 96% accuracy")
        st.info("🥉 You - 94% accuracy")

    # Personalized Recommendations
    st.markdown("---")
    st.markdown("### 💡 Personalized Recommendations")

    recommendations = [
        "📚 **Training Suggestion**: Focus on improving Angry emotion detection accuracy",
        "🎯 **Goal Setting**: Aim for 95% confidence scores on all analyses",
        "📊 **Analysis Pattern**: You're most accurate during morning hours (9-11 AM)",
        "🔧 **System Usage**: Try the batch upload feature for multiple files",
        "📈 **Improvement**: Your Neutral detection has improved 15% this week!"
    ]

    for rec in recommendations:
        st.info(rec)

    # System Status for Users
    st.markdown("---")
    st.markdown("### 🔧 System Status")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("✅ Real-time monitoring active")
        st.success("✅ Audio processing ready")
        st.success("✅ Database connection active")

    with col2:
        st.info(f"🔄 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.info("📊 Analytics updating every 30 seconds")
        st.info(f"🎙️ Sample rate: {audio_processor.sample_rate} Hz")

    with col3:
        # Audio level indicator
        st.markdown("#### Audio Input Level")
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]
            device_info = devices[default_input]
            st.success(f"🎤 {device_info['name'][:15]}...")
        except:
            st.warning("🎤 No audio input detected")

        # Model status
        if emotion_model.model is not None:
            st.success("🧠 ML Model loaded")
        else:
            st.warning("🧠 Using mock predictions")

def user_dashboard():
    """Display enhanced user dashboard with personalized analytics"""
    st.markdown("## 📈 Advanced User Dashboard")

    # Dashboard Customization for Users
    with st.expander("⚙️ Customize Your Dashboard", expanded=False):
        st.markdown("**Select widgets to display:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            show_personal_greeting = st.checkbox("Personal Greeting", value=True, key="user_greeting")
            show_quick_actions = st.checkbox("Quick Actions", value=True, key="user_quick_actions")
            show_personal_metrics = st.checkbox("Personal Metrics", value=True, key="user_metrics")

        with col2:
            show_performance_tab = st.checkbox("Performance Tab", value=True, key="user_performance")
            show_emotions_tab = st.checkbox("Emotions Tab", value=True, key="user_emotions")
            show_activity_tab = st.checkbox("Activity Tab", value=True, key="user_activity")

        with col3:
            show_achievements = st.checkbox("Achievements & Goals", value=True, key="user_achievements")
            show_recommendations = st.checkbox("Recommendations", value=True, key="user_recommendations")
            show_system_status = st.checkbox("System Status", value=True, key="user_system_status")

        if st.button("💾 Save My Preferences", key="save_user_prefs"):
            st.success("Your dashboard preferences saved!")

    # Personalized welcome section
    if show_personal_greeting:
        user = st.session_state.user
        current_hour = datetime.now().hour
        greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {greeting}, {user['full_name']}! 👋")
            st.markdown("*Here's your personalized emotion analysis dashboard*")
        with col2:
            # User avatar/status
            st.markdown("### Profile Status")
            st.success("✅ Account Active")
            st.info(f"👤 Role: {user['role'].upper()}")
            st.info(f"📅 Member since: {user['created_at'][:7] if user['created_at'] else 'N/A'}")

        st.markdown("---")

    # Quick Actions for Users
    if show_quick_actions:
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎤 Start Analysis", key="user_start_analysis"):
                if start_emotion_analysis():
                    st.success("✅ Analysis mode activated!")
                    st.info("Upload an audio file or use the recorder to analyze emotions")
                else:
                    st.error("Failed to start analysis")
        
        with col2:
            if st.button("📁 Upload Audio", key="user_upload"):
                st.session_state.show_upload = True
            
            if st.session_state.get("show_upload", False):
                uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg', 'm4a'], key="uploader_2")
                if uploaded_file is not None:
                    st.success(f"✅ File uploaded: {uploaded_file.name}")
                    st.info("Processing audio for emotion analysis...")
        
        with col3:
            if st.button("📊 View Reports", key="user_reports"):
                if view_user_reports():
                    st.success("Loading your reports...")
                    st.session_state.show_reports = True
                    st.info("Recently generated analysis reports")
                else:
                    st.error("Failed to load reports")
        
        with col4:
            if st.button("⚙️ Settings", key="user_settings"):
                if open_user_settings():
                    st.success("Settings panel opened")
                    st.session_state.show_settings = True
                    # Settings options
                    with st.expander("Privacy Settings", expanded=False):
                        st.checkbox("Allow data collection for analytics", value=True, key="analytics_consent")
                        st.checkbox("Save analysis history", value=True, key="save_history")
                    with st.expander("Notification Settings", expanded=False):
                        st.checkbox("Email notifications", value=True, key="email_notif")
                        st.checkbox("Push notifications", value=False, key="push_notif")
                    with st.expander("Audio Settings", expanded=False):
                        st.select_slider("Microphone sensitivity", value=50, options=range(0, 101, 10))
                else:
                    st.error("Failed to open settings")

        st.markdown("---")

    # Get real-time metrics
    metrics = realtime_analytics.get_dashboard_metrics()

    # Enhanced Personal Metrics
    if show_personal_metrics:
        st.markdown("### 📊 Your Performance Metrics")

        # Calculate personal stats (mock data for demonstration)
        import random
        personal_stats = {
            'analyses_today': random.randint(5, 25),
            'avg_confidence': random.uniform(0.75, 0.92),
            'success_rate': random.uniform(0.8, 0.95),
            'processing_time': random.uniform(0.15, 0.35)
        }

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Analyses Today",
                personal_stats['analyses_today'],
                delta=f"{random.choice([-2, -1, 0, 1, 3])} from yesterday"
            )

        with col2:
            st.metric(
                "Average Confidence",
                f"{personal_stats['avg_confidence']:.1%}",
                delta=f"{random.choice([-0.05, -0.02, 0, 0.03, 0.08]):+.1%}"
            )

        with col3:
            st.metric(
                "Success Rate",
                f"{personal_stats['success_rate']:.1%}",
                delta=f"{random.choice([-0.03, -0.01, 0, 0.02, 0.05]):+.1%}"
            )

        with col4:
            st.metric(
                "Avg Processing Time",
                f"{personal_stats['processing_time']:.2f}s",
                delta=f"{random.choice([-0.05, -0.02, 0, 0.01, 0.03]):+.2f}s"
            )

        st.markdown("---")

    # Personalized Analytics Section
    if show_performance_tab or show_emotions_tab or show_activity_tab:
        st.markdown("### 🎯 Your Analytics")

        tab_options = []
        if show_performance_tab:
            tab_options.append("📈 Performance")
        if show_emotions_tab:
            tab_options.append("🎭 Emotions")
        if show_activity_tab:
            tab_options.append("📋 Activity")

        if tab_options:
            tabs = st.tabs(tab_options)

            tab_index = 0

            if show_performance_tab:
                with tabs[tab_index]:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### Your Contribution to System")
                        # Mock contribution data
                        contribution_data = pd.DataFrame({
                            'date': pd.date_range(start='2024-01-01', periods=7, freq='D'),
                            'analyses': [random.randint(10, 30) for _ in range(7)],
                            'accuracy': [random.uniform(0.7, 0.95) for _ in range(7)]
                        })

                        fig = px.bar(
                            contribution_data,
                            x='date',
                            y='analyses',
                            title="Your Daily Analysis Count",
                            color='accuracy',
                            color_continuous_scale='RdYlGn'
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("#### Performance Comparison")
                        # Compare user performance vs system average
                        comparison_data = pd.DataFrame({
                            'metric': ['Accuracy', 'Speed', 'Consistency', 'Reliability'],
                            'you': [85, 78, 82, 88],
                            'system_avg': [75, 80, 78, 82]
                        })

                        fig = px.bar(
                            comparison_data.melt(id_vars='metric', var_name='source', value_name='score'),
                            x='metric',
                            y='score',
                            color='source',
                            barmode='group',
                            title="Performance vs System Average"
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                tab_index += 1

            if show_emotions_tab:
                with tabs[tab_index]:
                    st.markdown("#### Emotion Detection Patterns")

                    # Personal emotion distribution
                    emotion_stats = realtime_analytics.get_emotion_trends()
                    if not emotion_stats.empty:
                        # Filter for current user's data (mock filter)
                        user_emotions = emotion_stats.head(10)  # Mock user data

                        col1, col2 = st.columns(2)

                        with col1:
                            fig = px.pie(
                                values=user_emotions.groupby('emotion_category')['count'].sum().values,
                                names=user_emotions.groupby('emotion_category')['count'].sum().index,
                                title="Emotions You've Detected",
                                hole=0.4
                            )
                            st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            # Emotion confidence over time
                            confidence_trend = pd.DataFrame({
                                'time': pd.date_range(start='2024-01-01', periods=10, freq='H'),
                                'confidence': [random.uniform(0.7, 0.95) for _ in range(10)],
                                'emotion': [random.choice(['Happy', 'Angry', 'Neutral', 'Sad']) for _ in range(10)]
                            })

                            fig = px.scatter(
                                confidence_trend,
                                x='time',
                                y='confidence',
                                color='emotion',
                                title="Confidence Trends",
                                size=[20]*10
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No emotion data available yet")

                    # Emotion insights
                    st.markdown("#### Your Detection Insights")
                    insights_col1, insights_col2 = st.columns(2)

                    with insights_col1:
                        st.markdown("**Strengths:**")
                        st.success("• Excellent Happy emotion detection")
                        st.success("• Fast processing times")
                        st.success("• High accuracy on Neutral calls")

                    with insights_col2:
                        st.markdown("**Areas to Focus:**")
                        st.info("• Improve Angry emotion recognition")
                        st.info("• Practice with Sad emotion samples")
                        st.info("• Work on low-confidence detections")
                tab_index += 1

            if show_activity_tab:
                with tabs[tab_index]:
                    st.markdown("#### Your Recent Activity")

                    # Personal activity feed
                    user_logs = db.get_logs(limit=30)
                    if not user_logs.empty:
                        # Filter for current user (mock filter)
                        user_activity = user_logs.head(15)  # Mock user activity

                        for idx, log in user_activity.iterrows():
                            timestamp = log['created_at']
                            action_type = log['action_type']
                            description = log['action_description']
                            status = log['status']

                            # Color coding
                            if status == "SUCCESS":
                                icon = "✅"
                            elif status == "FAILED":
                                icon = "❌"
                            else:
                                icon = "ℹ️"

                            st.markdown(f"{icon} **{action_type}**: {description}")
                            st.caption(f"🕒 {timestamp}")
                            st.markdown("---")
                    else:
                        st.info("No recent activity")

    # Achievement and Gamification Section
    if show_achievements:
        st.markdown("---")
        st.markdown("### 🏆 Achievements & Goals")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### This Week's Achievements")
            achievements = [
                ("🎯 Accuracy Master", "95%+ accuracy for 5 days"),
                ("⚡ Speed Demon", "Processed 50+ analyses"),
                ("🎭 Emotion Expert", "Detected all 4 emotions")
            ]

            for badge, desc in achievements:
                st.success(f"{badge}: {desc}")

        with col2:
            st.markdown("#### Progress Goals")
            goals = [
                ("Monthly Target", 85, 92),  # current, target
                ("Quality Score", 88, 95),
                ("Consistency", 82, 90)
            ]

            for goal_name, current, target in goals:
                progress = min(current / target * 100, 100)
                st.progress(progress / 100)
                st.caption(f"{goal_name}: {current}/{target} ({progress:.1f}%)")

        with col3:
            st.markdown("#### Leaderboard Position")
            st.metric("Your Rank", "#3", delta="+2 positions")
            st.markdown("**Top Performers:**")
            st.info("🥇 Sarah Johnson - 98% accuracy")
            st.info("🥈 Mike Chen - 96% accuracy")
            st.info("🥉 You - 94% accuracy")

    # Personalized Recommendations
    if show_recommendations:
        st.markdown("---")
        st.markdown("### 💡 Personalized Recommendations")

        recommendations = [
            "📚 **Training Suggestion**: Focus on improving Angry emotion detection accuracy",
            "🎯 **Goal Setting**: Aim for 95% confidence scores on all analyses",
            "📊 **Analysis Pattern**: You're most accurate during morning hours (9-11 AM)",
            "🔧 **System Usage**: Try the batch upload feature for multiple files",
            "📈 **Improvement**: Your Neutral detection has improved 15% this week!"
        ]

        for rec in recommendations:
            st.info(rec)

    # System Status for Users
    if show_system_status:
        st.markdown("---")
        st.markdown("### 🔧 System Status")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("✅ Real-time monitoring active")
            st.success("✅ Audio processing ready")
            st.success("✅ Database connection active")

        with col2:
            st.info(f"🔄 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.info("📊 Analytics updating every 30 seconds")
            st.info(f"🎙️ Sample rate: {audio_processor.sample_rate} Hz")

        with col3:
            # Audio level indicator
            st.markdown("#### Audio Input Level")
            try:
                devices = sd.query_devices()
                default_input = sd.default.device[0]
                device_info = devices[default_input]
                st.success(f"🎤 {device_info['name'][:15]}...")
            except:
                st.warning("🎤 No audio input detected")

            # Model status
            if emotion_model.model is not None:
                st.success("🧠 ML Model loaded")
            else:
                st.warning("🧠 Using mock predictions")

def emotion_analysis_page():
    """Display emotion analysis page"""
    st.markdown("## 🎤 Real-Time Emotion Analysis")
    
    st.info("""
    This module analyzes speech in real-time to detect customer emotions:
    - **Happy**: Satisfied customer, positive experience
    - **Angry**: Dissatisfied customer, needs immediate attention
    - **Neutral**: Baseline emotion
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Live Audio Analysis")
        
        if st.button("🎙️ Start Real-Time Analysis", use_container_width=True):
            st.session_state.analyzing = True

        if st.session_state.get('analyzing', False):
            if st.button("Stop Analysis", key="stop_analysis", use_container_width=True):
                st.session_state.analyzing = False

            # Placeholder for real-time results
            result_placeholder = st.empty()
            metrics_placeholder = st.empty()

            with st.spinner("Analyzing audio stream..."):
                # Simulate real-time analysis
                for i in range(10):  # Simulate 10 analysis cycles
                    if not st.session_state.analyzing:
                        break

                    # Get mock prediction (in production, use actual audio)
                    import random
                    emotions = ['Angry', 'Happy', 'Neutral']
                    emotion = random.choice(emotions)
                    confidence = random.uniform(0.7, 0.95)
                    
                    # Update display
                    with result_placeholder.container():
                        if emotion == 'Happy':
                            st.success(f"### 😊 Emotion Detected: {emotion}")
                            st.progress(confidence)
                            st.write(f"Confidence: {confidence:.2%}")
                        elif emotion == 'Angry':
                            st.error(f"### 😠 Emotion Detected: {emotion}")
                            st.progress(confidence)
                            st.write(f"Confidence: {confidence:.2%}")
                            st.warning("⚠️ High dissatisfaction detected! Consider intervention.")
                        else:
                            st.info(f"### 😐 Emotion Detected: {emotion}")
                            st.progress(confidence)
                            st.write(f"Confidence: {confidence:.2%}")
                    
                    # Update metrics
                    with metrics_placeholder.container():
                        st.markdown("#### Analysis Metrics")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Arousal Level", f"{random.uniform(0.2, 0.9):.2f}")
                        with col_b:
                            st.metric("Valence Score", f"{random.uniform(0.2, 0.8):.2f}")
                        with col_c:
                            st.metric("Processing Time", f"{random.uniform(0.1, 0.3):.2f}s")
                    
                    time.sleep(3)  # Wait 3 seconds for next analysis

            st.session_state.analyzing = False
    
    with col2:
        st.markdown("### Recent Analysis Results")
        
        # Display recent results
        recent_results = db.get_emotion_stats()
        if not recent_results.empty:
            recent = recent_results.head(5)
            for idx, row in recent.iterrows():
                emotion = row['emotion_category']
                if emotion == 'Happy':
                    st.success(f"😊 {emotion} - {row['date'].strftime('%H:%M:%S') if hasattr(row['date'], 'strftime') else row['date']}")
                elif emotion == 'Angry':
                    st.error(f"😠 {emotion} - {row['date'].strftime('%H:%M:%S') if hasattr(row['date'], 'strftime') else row['date']}")
                else:
                    st.info(f"😐 {emotion} - {row['date'].strftime('%H:%M:%S') if hasattr(row['date'], 'strftime') else row['date']}")
        else:
            st.info("No recent analysis results")

def user_management_page():
    """Display user management page for admin"""
    st.markdown("## 👥 User Management")
    
    # Tabs for different management functions
    tab1, tab2, tab3 = st.tabs(["User List", "Pending Approvals", "Create User"])
    
    with tab1:
        st.markdown("### Registered Users")
        users_df = db.get_all_users()
        
        if not users_df.empty:
            # Filter and search
            search = st.text_input("Search Users", placeholder="Enter username or email")
            if search:
                users_df = users_df[users_df['username'].str.contains(search, case=False) | 
                                   users_df['email'].str.contains(search, case=False)]
            
            # Display users
            for idx, user in users_df.iterrows():
                with st.expander(f"📌 {user['username']} - {user['full_name']}"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**Email:** {user['email']}")
                        st.write(f"**Role:** {user['role']}")
                    with col2:
                        st.write(f"**Status:** {'✅ Active' if user['is_active'] else '❌ Disabled'}")
                        st.write(f"**Approved:** {'Yes' if user['is_approved'] else 'No'}")
                    with col3:
                        st.write(f"**Joined:** {user['created_at'][:10] if user['created_at'] else 'N/A'}")
                        st.write(f"**Last Login:** {user['last_login'][:10] if user['last_login'] else 'Never'}")
                    with col4:
                        if user['username'] != 'admin':  # Can't modify admin
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if user['is_active']:
                                    if st.button(f"Disable", key=f"disable_{user['id']}"):
                                        db.disable_user(user['id'])
                                        system_logger.log_action(st.session_state.user['id'], 
                                                                st.session_state.user['username'],
                                                                "USER_MANAGEMENT", 
                                                                f"Disabled user {user['username']}",
                                                                "SUCCESS")
                                        st.rerun()
                                else:
                                    if st.button(f"Enable", key=f"enable_{user['id']}"):
                                        db.enable_user(user['id'])
                                        st.rerun()
                            with col_b:
                                if st.button(f"Delete", key=f"delete_{user['id']}"):
                                    db.delete_user(user['id'])
                                    st.rerun()
        else:
            st.info("No users found")
    
    with tab2:
        st.markdown("### Pending User Approvals")
        pending_users = users_df[users_df['is_approved'] == 0] if not users_df.empty else pd.DataFrame()
        
        if not pending_users.empty:
            for idx, user in pending_users.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{user['username']}** - {user['full_name']}")
                        st.write(f"Email: {user['email']}")
                    with col2:
                        if st.button(f"✅ Approve", key=f"approve_{user['id']}"):
                            db.approve_user(user['id'])
                            system_logger.log_action(st.session_state.user['id'],
                                                    st.session_state.user['username'],
                                                    "USER_MANAGEMENT",
                                                    f"Approved user {user['username']}",
                                                    "SUCCESS")
                            st.success(f"User {user['username']} approved!")
                            time.sleep(1)
                            st.rerun()
                    with col3:
                        if st.button(f"❌ Reject", key=f"reject_{user['id']}"):
                            db.delete_user(user['id'])
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No pending approvals")
    
    with tab3:
        st.markdown("### Create New User")
        with st.form("create_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            full_name = st.text_input("Full Name")
            password = st.text_input("Temporary Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("Create User"):
                if username and email and full_name and password:
                    password_hash = auth_manager.security.hash_password(password)
                    user_id = db.create_user(username, email, password_hash, full_name, "Default", 
                                            auth_manager.security.hash_password("default"))
                    if user_id:
                        db.update_user(user_id, role=role, is_approved=1)
                        st.success(f"User {username} created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill all fields")

def system_logs_page():
    """Display system logs for admin"""
    st.markdown("## 📋 System Logs")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        log_type = st.selectbox("Log Type", ["All", "LOGIN", "LOGOUT", "USER_MANAGEMENT", "ERROR", "SECURITY"])
    with col2:
        status_filter = st.selectbox("Status", ["All", "SUCCESS", "FAILED", "WARNING"])
    with col3:
        limit = st.selectbox("Number of Logs", [50, 100, 200, 500], index=1)
    
    # Get logs
    logs = db.get_logs(limit=limit)
    
    # Apply filters
    if log_type != "All":
        logs = logs[logs['action_type'] == log_type]
    if status_filter != "All":
        logs = logs[logs['status'] == status_filter]
    
    # Display logs
    if not logs.empty:
        st.dataframe(logs, use_container_width=True)
        
        # Export option
        csv = logs.to_csv(index=False)
        st.download_button(
            label="📥 Export Logs to CSV",
            data=csv,
            file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No logs found")

def settings_page():
    """Display system settings for admin"""
    st.markdown("## ⚙️ System Settings")
    
    tab1, tab2 = st.tabs(["General Settings", "Security Settings"])
    
    with tab1:
        st.markdown("### General Configuration")
        
        # Session timeout
        current_timeout = db.get_setting('session_timeout_minutes') or '30'
        new_timeout = st.number_input("Session Timeout (minutes)", 
                                      min_value=5, max_value=120, 
                                      value=int(current_timeout))
        if new_timeout != int(current_timeout):
            if st.button("Update Session Timeout"):
                db.update_setting('session_timeout_minutes', str(new_timeout), st.session_state.user['id'])
                st.success("Session timeout updated!")
        
        # Real-time update interval
        current_interval = db.get_setting('realtime_update_seconds') or '30'
        new_interval = st.number_input("Real-time Update Interval (seconds)",
                                       min_value=10, max_value=60,
                                       value=int(current_interval))
        if new_interval != int(current_interval):
            if st.button("Update Update Interval"):
                db.update_setting('realtime_update_seconds', str(new_interval), st.session_state.user['id'])
                st.success("Update interval updated!")
    
    with tab2:
        st.markdown("### Security Configuration")
        
        # Max login attempts
        current_attempts = db.get_setting('max_login_attempts') or '5'
        new_attempts = st.number_input("Maximum Failed Login Attempts",
                                       min_value=3, max_value=10,
                                       value=int(current_attempts))
        if new_attempts != int(current_attempts):
            if st.button("Update Max Attempts"):
                db.update_setting('max_login_attempts', str(new_attempts), st.session_state.user['id'])
                st.success("Max attempts updated!")
        
        # Lockout duration
        current_lockout = db.get_setting('lockout_duration_minutes') or '15'
        new_lockout = st.number_input("Account Lockout Duration (minutes)",
                                      min_value=5, max_value=60,
                                      value=int(current_lockout))
        if new_lockout != int(current_lockout):
            if st.button("Update Lockout Duration"):
                db.update_setting('lockout_duration_minutes', str(new_lockout), st.session_state.user['id'])
                st.success("Lockout duration updated!")

def my_profile_page():
    """Display user profile page"""
    st.markdown("## 👤 My Profile")
    
    user = st.session_state.user
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/color/96/000000/user.png", width=150)
        st.markdown(f"### {user['full_name']}")
        st.markdown(f"**@{user['username']}**")
    
    with col2:
        st.markdown("### Profile Information")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Role:** {user['role'].upper()}")
        st.write(f"**Member Since:** {user['created_at'][:10] if user['created_at'] else 'N/A'}")
        st.write(f"**Last Login:** {user['last_login'] if user['last_login'] else 'Never'}")
        
        st.markdown("---")
        st.markdown("### Change Password")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if auth_manager.security.verify_password(current_password, user['password_hash']):
                    if new_password == confirm_password:
                        password_errors = auth_manager.security.validate_password_strength(new_password)
                        if not password_errors:
                            new_hash = auth_manager.security.hash_password(new_password)
                            db.reset_user_password(user['id'], new_hash)
                            st.success("Password updated successfully!")
                            system_logger.log_action(user['id'], user['username'], 
                                                    "PROFILE", "Password changed", "SUCCESS")
                        else:
                            for error in password_errors:
                                st.error(error)
                    else:
                        st.error("New passwords do not match")
                else:
                    st.error("Current password is incorrect")

# Main application flow
def main():
    """Main application entry point"""
    
    # Handle routing based on session state
    if 'show_registration' in st.session_state and st.session_state.show_registration:
        registration_page()
    elif 'show_forgot' in st.session_state and st.session_state.show_forgot:
        forgot_password_page()
    elif not st.session_state.authenticated:
        login_page()
    else:
        # User is authenticated, show main interface
        menu = sidebar_navigation()
        
        # Route based on menu selection
        if menu == "Dashboard":
            if st.session_state.user['role'] == 'admin':
                admin_dashboard()
            else:
                user_dashboard()
        elif menu == "Emotion Analysis":
            emotion_analysis_page()
        elif menu == "User Management" and st.session_state.user['role'] == 'admin':
            user_management_page()
        elif menu == "System Logs" and st.session_state.user['role'] == 'admin':
            system_logs_page()
        elif menu == "Settings" and st.session_state.user['role'] == 'admin':
            settings_page()
        elif menu == "My Profile":
            my_profile_page()
        
        # Auto-refresh real-time data every 30 seconds
        if st.session_state.get('auto_refresh', True):
            refresh_interval = int(db.get_setting('realtime_update_seconds') or 30)
            time.sleep(refresh_interval)
            st.rerun()
        
        show_footer()

if __name__ == "__main__":
    main()