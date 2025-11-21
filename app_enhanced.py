"""
Enhanced Streamlit Application
AI-Powered Virtual Interview Practice with Advanced Features
"""

import streamlit as st
import time
from datetime import datetime
import os
import sys
import traceback
from io import BytesIO
from pathlib import Path
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add modules to path
sys.path.append(os.path.dirname(__file__))

# Import custom modules
from modules.stt_engine import transcribe_audio
from modules.nlp_evaluator import evaluate_answer
from modules.tts_engine import TTSEngine, text_to_speech
from modules.database import get_database
from modules.report_generator import generate_report
from modules.interview_flow import InterviewFlowManager
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# Page configuration
st.set_page_config(page_title="AI Virtual Interview Coach", layout="wide")

# Global styles for the application
st.markdown("""
<style>
/* Reset and hide Streamlit elements */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* App background */
.stApp {
    background: #f3f4f6;
}

/* Login Card Styling */
[data-testid="stForm"] {
    background: #ffffff;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    border: 1px solid #e5e7eb;
}

/* Logo and branding */
.auth-logo {
    text-align: center;
    margin-bottom: 1.5rem;
}

.auth-logo .logo-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: #2563eb;
    border-radius: 8px;
    margin-bottom: 0.75rem;
}

.auth-logo .logo-icon svg {
    width: 24px;
    height: 24px;
    fill: white;
}

.auth-logo h1 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.25rem 0;
}

.auth-logo p {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
}

/* Tabs - minimal design */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #e5e7eb;
    background: transparent;
    padding: 0;
    margin-bottom: 1.5rem;
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    padding: 0.5rem 1rem;
    font-weight: 500;
    font-size: 0.875rem;
    color: #6b7280;
    border: none;
    background: transparent;
    border-bottom: 2px solid transparent;
    border-radius: 0;
}

.stTabs [aria-selected="true"] {
    color: #2563eb !important;
    border-bottom: 2px solid #2563eb;
    background: transparent !important;
    box-shadow: none;
}

/* Form styling */
.stTextInput label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.25rem;
}

.stTextInput input {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    color: #111827;
    background-color: #fff;
}

.stTextInput input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    outline: none;
}

/* Button styling */
button[kind="primary"] {
    background-color: #2563eb !important;
    color: white !important;
    border: none;
    border-radius: 6px;
    padding: 0.625rem 1rem;
    font-weight: 500;
    font-size: 0.875rem;
    width: 100%;
    margin-top: 0.5rem;
    transition: background-color 0.2s;
}

button[kind="primary"]:hover {
    background-color: #1d4ed8 !important;
}

/* Footer links */
.auth-footer {
    text-align: center;
    margin-top: 1.25rem;
    font-size: 0.75rem;
    color: #6b7280;
}

.auth-footer strong {
    color: #2563eb;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def ensure_data_directories():
    """Ensure all required data directories exist and are writable"""
    try:
        # Create data and reports directories if they don't exist
        data_dir = Path("data")
        reports_dir = Path("reports")
        
        for directory in [data_dir, reports_dir]:
            try:
                directory.mkdir(exist_ok=True)
                # Test write permissions
                test_file = directory / ".permission_test"
                test_file.touch()
                test_file.unlink()
                logger.info(f"Verified write access to {directory}")
            except (OSError, IOError) as e:
                logger.error(f"Cannot write to {directory}: {str(e)}")
                st.error(f"Error: Cannot write to {directory}. Please check directory permissions.")
                st.stop()
                
    except Exception as e:
        logger.error(f"Critical error initializing data directories: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("A critical error occurred while initializing the application. Please check the logs.")
        st.stop()

def initialize_session_state():
    """Initialize all session state variables"""
    
    # First ensure data directories exist and are writable
    ensure_data_directories()
    
    defaults = {
        'logged_in': False,
        'current_user': None,
        'interview_started': False,
        'wizard_active': False,
        'wizard_step': 1,  # Start at step 1
        'user_name': '',
        'session_id': None,
        'current_question': None,
        'question_count': 0,
        'transcript': [],
        'evaluations': [],
        'flow_manager': None,
        'tts_engine_name': 'gtts',  # Initialize engine name first
        'stt_engine_name': 'whisper',
        'speak_next_question': False,
        'session_complete': False,
        'evaluation_metrics': {
            'technical_accuracy': 0,
            'communication_skills': 0,
            'confidence': 0,
            'clarity': 0,
            'sentiment': 0
        },
        'role_name': '',
        'candidate_first_name': '',
        'job_description_text': '',
        'resume_text': '',
        'resume_pdf_bytes': None,
        'extra_context': '',
        'company_name': '', 
        'show_connect_modal': False,
        'processing': False,
        'paused': False,
        'show_feedback': False,
        'transcription_text': '',
        'error_message': '',
        'setup_interview_mode': 'Technical',
        'setup_difficulty': 'Intermediate',
        'setup_num_questions': 5,
        'question_start_time': None,
        'current_evaluation': None,
        'stt_metrics': {}
    }
    
    # Initialize session state with defaults
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize TTS engine separately to handle potential errors
    if 'tts_engine' not in st.session_state:
        try:
            st.session_state.tts_engine = TTSEngine(engine=st.session_state.tts_engine_name)
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            st.session_state.tts_engine = None
            st.session_state.error_message = f"Warning: TTS functionality may be limited: {str(e)}"
initialize_session_state()

# ============================================================================
# AUTHENTICATION PAGE
# ============================================================================

if not st.session_state.get('logged_in', False):
    # Hide sidebar on login page
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Use columns to center the login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and Header
        st.markdown("""
        <div class="auth-logo">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
            </div>
            <h1>INTERVIEWS</h1>
            <p>AI-Powered Interview Practice Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Sign in and Sign up
        tab_login, tab_register = st.tabs(["Sign in", "Sign up"])
        
        with tab_login:
            st.markdown('<p style="text-align:center;color:#334155;font-size:0.9375rem;margin-bottom:1.5rem;">to continue to Interviews Chat</p>', unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username or Email", placeholder="Enter your username or email", label_visibility="visible")
                password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="visible")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("CONTINUE", type="primary", use_container_width=True)
                
                if submit:
                    if username and password:
                        try:
                            db = get_database()
                            success, result = db.authenticate_user(username, password)
                            if success:
                                st.session_state.logged_in = True
                                st.session_state.current_user = result
                                st.session_state.user_name = result.get('full_name', username)
                                st.success("✅ Sign in successful!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"❌ {result}")
                        except Exception as e:
                            logger.error(f"Login error: {str(e)}")
                            st.error("❌ Sign in failed. Please check your credentials.")
                    else:
                        st.warning("⚠️ Please enter your username and password")
            
            st.markdown('<div class="auth-footer">No account? Switch to <strong>Sign up</strong> tab</div>', unsafe_allow_html=True)
        
        with tab_register:
            st.markdown('<p style="text-align:center;color:#334155;font-size:0.9375rem;margin-bottom:1.5rem;">Create your account</p>', unsafe_allow_html=True)
            
            with st.form("register_form", clear_on_submit=True):
                full_name = st.text_input("Full Name", placeholder="Enter your full name", label_visibility="visible")
                new_user = st.text_input("Username", placeholder="Choose a username", label_visibility="visible")
                new_pass = st.text_input("Password", type="password", placeholder="Create a password (min. 6 characters)", label_visibility="visible")
                confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", label_visibility="visible")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("CREATE ACCOUNT", type="primary", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass and full_name:
                        if new_pass != confirm_pass:
                            st.error("❌ Passwords do not match!")
                        elif len(new_pass) < 6:
                            st.error("❌ Password must be at least 6 characters long")
                        else:
                            try:
                                db = get_database()
                                success, msg = db.register_user(new_user, new_pass, full_name)
                                if success:
                                    st.success("✅ Account created successfully! Please sign in.")
                                else:
                                    st.error(f"❌ {msg}")
                            except Exception as e:
                                logger.error(f"Registration error: {str(e)}")
                                st.error("❌ Registration failed. Please try again.")
                    else:
                        st.warning("⚠️ Please fill in all fields")
            
            st.markdown('<div class="auth-footer">Already have an account? Switch to <strong>Sign in</strong> tab</div>', unsafe_allow_html=True)
    
    st.stop()  # Stop execution here if not logged in

# ============================================================================
# HELPER: Start interview (reusable for sidebar + hero button)
# ============================================================================

def start_interview_session(interview_mode: str, difficulty: str, num_questions: int):
    """Start a new interview session with proper validation and error handling"""
    try:
        # Validate inputs
        if not all([interview_mode, difficulty, num_questions > 0]):
            raise ValueError("Missing required interview parameters")
            
        # Initialize flow manager if needed
        if not hasattr(st.session_state, 'flow_manager') or not st.session_state.flow_manager:
            st.session_state.flow_manager = InterviewFlowManager()
        
        # Extract keywords from job description + resume for tailoring
        def extract_keywords(text: str, limit: int = 25):
            try:
                import re
                words = re.findall(r"[A-Za-z][A-Za-z0-9_+-]{2,}", text.lower())
                stop = set(['the','and','for','with','this','that','from','your','about','you','are','our','will','have','has','can','use','using','in','on','of','to','a','an','as','be'])
                filtered = [w for w in words if w not in stop and len(w) > 2]
                freq = {}
                for w in filtered:
                    freq[w] = freq.get(w,0)+1
                ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
                return [w for w,_ in ranked[:limit]]
            except Exception as e:
                logger.warning(f"Keyword extraction failed: {str(e)}")
                return []
                
        combined_source = (st.session_state.get('job_description_text', '') or '') + '\n' + (st.session_state.get('resume_text', '') or '')
        tailored_keywords = extract_keywords(combined_source)
        
        # Start the session with resume and job description for custom question generation
        st.session_state.flow_manager.start_session(
            interview_mode, 
            difficulty, 
            num_questions, 
            target_keywords=tailored_keywords,
            resume_text=st.session_state.get('resume_text', ''),
            job_description=st.session_state.get('job_description_text', '')
        )
        
        # Initialize database session
        db = get_database()
        meta = {
            'company': st.session_state.get('company_name', ''),
            'role': st.session_state.get('role_name', ''),
            'candidate_first_name': st.session_state.get('candidate_first_name', ''),
            'job_description': st.session_state.get('job_description_text', ''),
            'resume_text': st.session_state.get('resume_text', ''),
            'extra_context': st.session_state.get('extra_context', ''),
            'has_resume_pdf': bool(st.session_state.get('resume_pdf_bytes'))
        }
        
        # Create session in database
        st.session_state.session_id = db.create_session(
            interview_mode, 
            difficulty, 
            st.session_state.get('user_name', 'anonymous'),
            metadata=meta
        )
        
        # Get first question
        first_question = st.session_state.flow_manager.get_next_question()
        if not first_question:
            raise ValueError("Failed to get first question - no questions available")
            
        # Update session state
        st.session_state.update({
            'interview_mode': interview_mode,
            'difficulty': difficulty,
            'current_question': first_question,
            'question_count': 1,
            'question_start_time': time.time(),
            'interview_started': True,
            'transcript': [{"speaker": "AI", "text": first_question['question']}],
            'evaluations': [],
            'show_feedback': False,
            'session_complete': False,
            'paused': False,
            'error_message': ''
        })
        
        # Log the start of the interview
        logger.info(f"Interview started - Mode: {interview_mode}, Difficulty: {difficulty}")
        
    except Exception as e:
        error_msg = f"Failed to start interview: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        st.session_state.error_message = error_msg
        st.error(error_msg)
        return False
        
    return True
def end_interview_session():
    """Safely end the current interview session and clean up resources"""
    try:
        # End the session in the database if it exists
        if st.session_state.get('session_id'):
            try:
                db = get_database()
                db.end_session(st.session_state.session_id)
                logger.info(f"Successfully ended session {st.session_state.session_id}")
            except Exception as e:
                logger.error(f"Error ending session in database: {str(e)}")
        
        # Reset all interview-related session state
        reset_keys = [
            'interview_started', 'session_complete', 'current_question',
            'question_count', 'transcript', 'evaluations', 'current_evaluation',
            'show_feedback', 'paused', 'session_id', 'flow_manager',
            'interview_mode', 'difficulty', 'question_start_time'
        ]
        
        for key in reset_keys:
            if key in st.session_state:
                del st.session_state[key]
                
        logger.info("Interview session ended and cleaned up")
        
    except Exception as e:
        error_msg = f"Error ending interview session: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return False
        
    return True

def get_next_question():
    """Safely get the next question from the flow manager and update session state"""
    if not st.session_state.get('flow_manager'):
        st.error("Interview flow manager not initialized")
        return False
        
    try:
        # Get the next question from the flow manager
        next_question = st.session_state.flow_manager.get_next_question()
        
        # If no more questions, end the interview
        if not next_question:
            st.session_state.session_complete = True
            st.session_state.interview_started = False
            st.rerun()
            return False
            
        # Update session state with the new question
        st.session_state.update({
            'current_question': next_question,
            'question_count': st.session_state.get('question_count', 0) + 1,
            'question_start_time': time.time(),
            'show_feedback': False,
            'paused': False
        })
        
        # Add the AI's question to the transcript
        transcript_entry = {"speaker": "AI", "text": next_question['question']}
        st.session_state.transcript = st.session_state.get('transcript', []) + [transcript_entry]
        
        # Log to database if session exists
        if st.session_state.get('session_id'):
            try:
                db = get_database()
                db.append_transcript(
                    st.session_state.session_id, 
                    'AI', 
                    next_question['question']
                )
            except Exception as e:
                logger.error(f"Error updating transcript: {str(e)}")
        
        return True
        
    except Exception as e:
        error_msg = f"Failed to get next question: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        st.session_state.error_message = error_msg
        return False

# ============================================================================
# SIDEBAR COMPONENT
# ============================================================================

def show_sidebar():
    """Render the sidebar with navigation and session controls"""
    try:
        with st.sidebar:
            st.image("https://via.placeholder.com/200x60?text=AI+Interview+Coach", width=200)
            
            # Always show interview settings at the top
            st.markdown("### ⚙️ Interview Settings")
            
            # Interview Mode Selection
            interview_mode_options = ["Technical", "HR", "Behavioral", "Mixed"]
            current_mode = st.session_state.get('setup_interview_mode', 'Technical')
            mode_index = interview_mode_options.index(current_mode) if current_mode in interview_mode_options else 0
            
            selected_mode = st.selectbox(
                "Interview Type",
                interview_mode_options,
                index=mode_index,
                key="sidebar_interview_mode",
                help="Select the type of interview questions"
            )
            st.session_state.setup_interview_mode = selected_mode
            
            # Difficulty Level Selection
            difficulty_options = ["Beginner", "Intermediate", "Advanced"]
            current_diff = st.session_state.get('setup_difficulty', 'Intermediate')
            diff_index = difficulty_options.index(current_diff) if current_diff in difficulty_options else 1
            
            selected_difficulty = st.selectbox(
                "Difficulty Level",
                difficulty_options,
                index=diff_index,
                key="sidebar_difficulty",
                help="Select the difficulty level of questions"
            )
            st.session_state.setup_difficulty = selected_difficulty
            
            # Number of Questions
            num_questions = st.slider(
                "Number of Questions",
                min_value=3,
                max_value=15,
                value=st.session_state.get('setup_num_questions', 5),
                step=1,
                key="sidebar_num_questions",
                help="Total questions in the interview"
            )
            st.session_state.setup_num_questions = num_questions
            
            st.markdown("---")
            
            # Show interview status
            if st.session_state.interview_started:
                st.markdown(f"### 🎤 Interview in Progress")
                st.info(f"**Mode:** {st.session_state.interview_mode}  \n**Difficulty:** {st.session_state.difficulty}")
                
                if st.button("⏸️ Pause Interview", use_container_width=True):
                    st.session_state.paused = True
                    st.rerun()
                    
                if st.button("⏹️ End Interview", type="primary", use_container_width=True):
                    if end_interview_session():
                        st.success("Interview session ended successfully")
                    else:
                        st.error("Failed to end interview session. Please check the logs.")
                    st.rerun()
                    
            elif st.session_state.get('session_complete'):
                st.markdown("### ✅ Interview Complete")
                st.success("Your interview has been completed!")
                
            elif st.session_state.get('wizard_active', False):
                st.markdown("### 📝 Setup Wizard Active")
                st.info("Complete the wizard to start your interview with these settings.")
            
            st.markdown("---")
            
            # Progress indicator (only show during interview)
            if st.session_state.get('interview_started') and st.session_state.get('flow_manager'):
                progress = st.session_state.flow_manager.get_progress()
                progress_pct = progress.get('progress_percentage', 0)
                current_q = progress.get('current_question', 0)
                total_q = progress.get('total_questions', 0)
                st.markdown(f"""
<div style='background:#EEF2FF;border:1px solid #E0E7FF;padding:.85rem 1rem;border-radius:14px;display:flex;align-items:center;gap:1rem;margin-bottom:1rem;'>
    <div style='flex:1;height:10px;background:#E2E8F0;border-radius:8px;overflow:hidden;'>
        <div style='height:100%;width:{progress_pct}%;background:linear-gradient(90deg,#6366F1,#818CF8);transition:width .4s'></div>
    </div>
    <div style='font-size:.75rem;font-weight:600;color:#4F46E5;'>{current_q} / {total_q}</div>
</div>
""", unsafe_allow_html=True)
            
            # User info and logout
            if st.session_state.get('logged_in'):
                st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")
                if st.button("🔓 Logout", use_container_width=True):
                    st.session_state.logged_in = False
                    st.rerun()
                    
    except Exception as e:
        logger.error(f"Error in sidebar: {str(e)}")
        logger.error(traceback.format_exc())
        st.sidebar.error("An error occurred in the sidebar. Please refresh the page.")

# ============================================================================
# MAIN HEADER (Only shown when logged in)
# ============================================================================

if st.session_state.get('logged_in', False):
    # Call sidebar to make it visible
    show_sidebar()
    
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Virtual Interview Coach</h1>
        <p>Practice. Perfect. Succeed.</p>
    </div>
    """, unsafe_allow_html=True)

    # Inject custom navigation
    st.markdown("""
    <div class="custom-nav" style="display:block;">
        <div class="nav-logo">⚡ Interview Sidekick</div>
        <div class="nav-group">
            <div class="nav-item active">🕒 Realtime Assist</div>
            <div class="nav-item">📘 Interview Prep</div>
            <div class="nav-item">🔍 Question Bank</div>
            <div class="nav-item">📚 Context Library</div>
            <div class="nav-item">💬 Submit Feedback</div>
        </div>
        <div class="nav-footer">v0.1 experimental UI</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT AREA WITH TABS
# ============================================================================

tab_interview, tab_history, tab_settings, tab_about = st.tabs(["🗣️ Interview", "📚 History", "⚙️ Settings", "ℹ️ About"])

with tab_interview:
    if not st.session_state.interview_started and not st.session_state.wizard_active:
        # Redesigned landing (hero + cards)
        st.markdown("""
        <div class="greeting">
            <h1>Hey 👋, <span>Friend!</span></h1>
            <p>Let's get you ready for your next interview.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="dash-grid">', unsafe_allow_html=True)

        # Card 1: Real-time Assist
        st.markdown(f"""
        <div class="dash-card">
            <span class="badge">REAL-TIME ASSIST</span>
            <h3>Real-time Interview Assist</h3>
            <p>Practice live with dynamic AI guidance. Tailored questions based on your resume and job description.</p>
            <button class="primary-btn" onclick="document.getElementById('hero_start_btn_form_submit').click()">▶ Start Tailored Session</button>
            <div class="link-sm">Upgrade to unlock unlimited</div>
        </div>
        """, unsafe_allow_html=True)

        # Card 2: Tutorial / Steps
        st.markdown("""
        <div class="dash-card">
            <span class="badge" style="background:#DBEAFE;color:#1E3A8A;">HOW IT WORKS</span>
            <h3>Interview Tab</h3>
            <div class="tutorial-step"><div class="step-index">1</div><p>Start a tailored session via the wizard.</p></div>
            <div class="tutorial-step"><div class="step-index">2</div><p>Use the input/mic to provide your answer.</p></div>
            <div class="tutorial-step"><div class="step-index">3</div><p>Receive instant AI evaluation & guidance after each response.</p></div>
            <p style="margin-top:1rem;font-size:.75rem;color:#64748B;">Finish all questions to unlock a detailed performance report.</p>
        </div>
        """, unsafe_allow_html=True)

        # Card 3: Placeholder for future features / context library
        st.markdown("""
        <div class="dash-card">
            <span class="badge" style="background:#DCFCE7;color:#065F46;">RESOURCES</span>
            <h3>Smart Prep & Library</h3>
            <p>Explore curated question banks, role-specific context, and personalized improvement targets to accelerate readiness.</p>
            <p style="margin-top:auto;font-size:.75rem;color:#64748B;">Coming soon – contextual boosters & company-specific packs.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Actual Streamlit button logic to start the wizard
        with st.form(key="hero_start_form"):
            # The button in the card above triggers this submit via JS
            hero_start = st.form_submit_button("Start Tailored Session", type="primary", key="hero_start_btn", help="Click to start the pre-interview wizard for context setup.")
            if hero_start:
                st.session_state.wizard_active = True
                st.session_state.wizard_step = 1
                st.rerun()

    elif st.session_state.wizard_active and not st.session_state.interview_started:
        # ================= PRE-INTERVIEW WIZARD =================
        steps = ["Basic Info", "Job Description", "Now It's About You", "Extra Context"]
        current = st.session_state.wizard_step
        # Stepper bar
        step_cols = st.columns(len(steps))
        for idx, (col, label) in enumerate(zip(step_cols, steps), start=1):
            active = idx == current
            with col:
                st.markdown(f"<div style='background:linear-gradient(90deg,#6366F1,#818CF8);padding:.6rem 0;border-radius:12px;display:flex;flex-direction:column;align-items:center;opacity:{'1' if active else '0.6'}'>"
                            f"<div style='background:#FFFFFF;padding:.25rem .55rem;border-radius:20px;font-size:.75rem;font-weight:600;color:#6366F1'>{idx}</div>"
                            f"<div style='margin-top:.35rem;font-size:.75rem;color:#FFFFFF;font-weight:{'700' if active else '500'}'>{label}</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Render current step
        if current == 1:
            st.markdown("## Tell us about the job you're interviewing for •")
            company = st.text_input("Company *", value=st.session_state.get('company_name', ''), placeholder="Select or enter company name...", key="wiz_company")
            role = st.text_input("Role *", value=st.session_state.get('role_name', ''), placeholder="Select or enter job role...", key="wiz_role")
            first_name = st.text_input("First Name *", value=st.session_state.get('candidate_first_name', '') or st.session_state.get('user_name', ''), key="wiz_name")
            
            # Update session state
            st.session_state.company_name = company
            st.session_state.role_name = role
            st.session_state.candidate_first_name = first_name
            
            nav_cols = st.columns([1,1,6])
            with nav_cols[0]:
                is_valid = bool(company and role and first_name)
                if st.button("Next ➜", use_container_width=True, disabled=not is_valid, key="wiz1_next"):
                    st.session_state.wizard_step = 2
                    st.rerun()
                    
        elif current == 2:
            st.markdown("## Provide the job description •")
            job_desc = st.text_area("Paste Job Description", value=st.session_state.get('job_description_text', ''), height=260, placeholder="Paste the full job description here...", key="wiz_job_desc")
            st.session_state.job_description_text = job_desc
            
            nav_cols = st.columns([1,1,6])
            with nav_cols[0]:
                if st.button("◀ Back", use_container_width=True, key="wiz2_back"):
                    st.session_state.wizard_step = 1
                    st.rerun()
            with nav_cols[1]:
                is_valid = len(job_desc.strip()) >= 30
                if st.button("Next ➜", use_container_width=True, disabled=not is_valid, key="wiz2_next"):
                    st.session_state.wizard_step = 3
                    st.rerun()
                    
        elif current == 3:
            st.markdown("## Ok... now about you (professionally) •")
            st.write("Upload resume or tell us about your prior experience (max 4,000 char)")
            uploaded_pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"], help="Drag & drop or browse your PDF resume", key="wiz_resume_upload")
            if uploaded_pdf is not None:
                st.session_state.resume_pdf_bytes = uploaded_pdf.read()
                # Try PDF text extraction if library available
                try:
                    from pdfminer.high_level import extract_text  # type: ignore
                    from io import BytesIO as _BIO
                    pdf_text = extract_text(_BIO(st.session_state.resume_pdf_bytes))
                    if pdf_text and len(pdf_text.strip()) > 0:
                        # Only auto-fill if user hasn't typed anything yet
                        if not st.session_state.get('resume_text', '').strip():
                            st.session_state.resume_text = pdf_text[:4000]
                        st.success("Resume uploaded ✔ Text extracted")
                    else:
                        st.success("Resume uploaded ✔ (no extractable text)")
                except Exception:
                    st.success("Resume uploaded ✔ (text extraction unavailable)")
                    
            resume_text = st.text_area("Paste Your Resume / Experience Text Here", value=st.session_state.get('resume_text', ''), height=220, max_chars=4000, key="wiz_resume_text")
            st.session_state.resume_text = resume_text
            st.caption(f"{len(resume_text)} / 4000 characters")
            
            nav_cols = st.columns([1,1,1,5])
            with nav_cols[0]:
                if st.button("◀ Back", use_container_width=True, key="wiz3_back"):
                    st.session_state.wizard_step = 2
                    st.rerun()
            with nav_cols[1]:
                if st.button("Skip", use_container_width=True, key="wiz3_skip"):
                    st.session_state.wizard_step = 4
                    st.rerun()
            with nav_cols[2]:
                if st.button("Next ➜", use_container_width=True, key="wiz3_next"):
                    st.session_state.wizard_step = 4
                    st.rerun()
                    
        elif current == 4:
            st.markdown("## Extra Context •")
            extra = st.text_area("Add any extra notes (optional)", value=st.session_state.get('extra_context', ''), height=160, key="wiz_extra")
            st.session_state.extra_context = extra
            
            nav_cols = st.columns([1,1,6])
            with nav_cols[0]:
                if st.button("◀ Back", use_container_width=True, key="wiz4_back"):
                    st.session_state.wizard_step = 3
                    st.rerun()
            with nav_cols[1]:
                if st.button("Start Interview ▶", use_container_width=True, key="wiz4_start"):
                    # Now actually start real interview using sidebar settings
                    st.session_state.wizard_active = False # Exit wizard
                    start_interview_session(
                        interview_mode=st.session_state.get('setup_interview_mode', 'Technical'),
                        difficulty=st.session_state.get('setup_difficulty', 'Intermediate'),
                        num_questions=st.session_state.get('setup_num_questions', 5)
                    )

    elif st.session_state.session_complete:
        # Session complete - show results
        st.markdown("## 🎉 Interview Session Complete!")

        if st.session_state.session_id:
            db = get_database()
            session_data = db.get_session(st.session_state.session_id)
            analytics = db.get_analytics(st.session_state.session_id)
            
            # Overall score
            overall_score = session_data['overall_score']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Overall Score", f"{overall_score:.1f}/100", 
                         help="Your average score across all questions")
            
            with col2:
                st.metric("Questions Answered", analytics['total_questions'])
            
            with col3:
                st.metric("Questions Passed", analytics['questions_passed'],
                         help="Questions with score ≥ 60")
            
            with col4:
                st.metric("Duration", f"{analytics['duration_minutes']} min")
            
            st.markdown("---")
            
            # Skill breakdown
            st.markdown("### 📊 Skill Breakdown")
            
            skill_cols = st.columns(4)
            skills = analytics['skill_breakdown']
            skill_names = ['Technical Accuracy', 'Communication Skills', 'Sentiment & Tone', 'Completeness']
            skill_keys = ['technical_accuracy', 'communication_skills', 'sentiment_tone', 'completeness']
            
            for col, name, key in zip(skill_cols, skill_names, skill_keys):
                with col:
                    score = skills[key]
                    st.metric(name, f"{score:.1f}/100")
                    st.progress(score / 100)
            
            st.markdown("---")
            
            # Download report
            st.markdown("### 📄 Download Your Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Generate PDF Report", use_container_width=True):
                    with st.spinner("Generating PDF report..."):
                        try:
                            # Note: This requires the fpdf library (fpdf2)
                            report_path = generate_report(session_data, analytics, format="pdf")
                            
                            if os.path.exists(report_path):
                                with open(report_path, 'rb') as f:
                                    st.download_button(
                                        label="Download PDF",
                                        data=f.read(),
                                        file_name=f"interview_report_{st.session_state.session_id}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                            else:
                                st.warning("PDF generation requires fpdf library. Generating text report instead.")
                                report_path = generate_report(session_data, analytics, format="txt")
                                with open(report_path, 'r', encoding='utf-8') as f:
                                    st.download_button(
                                        label="Download Text Report",
                                        data=f.read(),
                                        file_name=f"interview_report_{st.session_state.session_id}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                        except Exception as e:
                            st.error(f"Error generating report: {e}")
            
            with col2:
                # JSON report
                json_report = generate_report(session_data, analytics, format="json")
                st.download_button(
                    label="📥 Download JSON Data",
                    data=json_report,
                    file_name=f"interview_data_{st.session_state.session_id}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.markdown("---")

        # New interview button
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
            # Reset session state
            st.session_state.interview_started = False
            st.session_state.session_complete = False
            st.session_state.session_id = None
            st.session_state.transcript = []
            st.session_state.evaluations = []
            st.session_state.current_question = None
            st.rerun()

    else:
        # ================= ACTIVE INTERVIEW DASHBOARD (Redesigned) =================
        
        # Helper: Process Answer
        def _process_answer(user_answer: str, stt_result_meta: dict):
            # 1. Update Transcript
            st.session_state.transcript.append({'speaker':'User','text': user_answer})
            if st.session_state.session_id:
                try:
                    get_database().append_transcript(st.session_state.session_id, 'User', user_answer)
                except Exception:
                    pass
            
            # 2. Evaluate Answer
            evaluation = evaluate_answer(user_answer, st.session_state.current_question, st.session_state.interview_mode, st.session_state.difficulty)
            st.session_state.current_evaluation = evaluation
            st.session_state.evaluations.append(evaluation)
            
            # 3. Log to Database
            if st.session_state.session_id:
                db = get_database()
                db.add_question_response(st.session_state.session_id, {
                    'question': st.session_state.current_question['question'],
                    'answer': user_answer,
                    'evaluation': evaluation,
                    'stt_metrics': stt_result_meta,
                    'duration': stt_result_meta.get('duration',0) if stt_result_meta else 0
                })
            
            # 4. Get Next Question or Complete Session
            next_question = st.session_state.flow_manager.get_next_question()
            if next_question:
                st.session_state.current_question = next_question
                st.session_state.question_count += 1
                st.session_state.transcript.append({'speaker':'AI','text': next_question['question']})
                if st.session_state.session_id:
                    try:
                        get_database().append_transcript(st.session_state.session_id, 'AI', next_question['question'])
                    except Exception:
                        pass
                st.session_state.question_start_time = time.time()
                st.session_state.speak_next_question = True # Flag to speak the new question
            else:
                st.session_state.session_complete = True
                if st.session_state.session_id:
                    db = get_database(); db.end_session(st.session_state.session_id)
                    
            # 5. Show Feedback UI
            st.session_state.show_feedback = True
            return

        # Top bar
        top_bar = st.container()
        with top_bar:
            bar_cols = st.columns([2,1,1,1.5,1,1])
            with bar_cols[0]:
                st.markdown(f"**Transcript**")
            with bar_cols[1]:
                # Camera toggle
                show_camera = st.checkbox("📹 Camera", value=True, key="show_camera_toggle")
                st.session_state.show_camera = show_camera
            with bar_cols[2]:
                # This button simulates starting a live mic recording
                if st.button("🎙️ Record", disabled=st.session_state.processing):
                    st.info("Recording simulated (use input below)")
            with bar_cols[3]:
                st.markdown(f"<div style='text-align:right;'>" 
                            f"<span style='background:#FEF9C3;padding:4px 10px;border:1px solid #FACC15;border-radius:20px;font-size:.7rem;font-weight:600;'>Free Trial</span> "
                            f"<span style='margin-left:6px;background:#6366F1;color:#fff;padding:4px 10px;border-radius:20px;font-size:.7rem;'>Q {st.session_state.question_count}</span></div>", unsafe_allow_html=True)
            with bar_cols[4]:
                st.markdown(f"<div style='font-size:.75rem;color:#475569;padding-top:.4rem;'>{st.session_state.company_name or 'Company'}</div>", unsafe_allow_html=True)
            with bar_cols[5]:
                if st.button("End Session", type="secondary"):
                    st.session_state.session_complete = True
                    if st.session_state.session_id:
                        db = get_database()
                        db.end_session(st.session_state.session_id)
                    st.rerun()

        # Main two panels
        left, right = st.columns([1,1])

        # LEFT: Transcript + input mic
        with left:
            st.markdown("""
            <div style='background:#FFFFFF;border:1px solid #E2E8F0;border-radius:18px;padding:2rem;min-height:520px;'>
              <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;height:140px;'>
                <div style='width:110px;height:110px;background:radial-gradient(circle,#EEF2FF,#E0E7FF);border-radius:50%;display:flex;align-items:center;justify-content:center;'>
                  <span style='font-size:2.2rem;color:#6366F1;'>🎙️</span>
                </div>
              </div>
              <div style='margin-top:1rem;font-size:.95rem;color:#1E293B;font-weight:600;'>Your interview transcript will appear here</div>
              <div style='margin:.4rem 0 1.2rem;font-size:.75rem;color:#64748B;'>Click Record and ask interview questions</div>
              
              <style>
                .transcription-box {
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 1rem;
                    min-height: 100px;
                    margin: 0.5rem 0;
                    background: #f8fafc;
                    font-size: 1rem;
                    line-height: 1.6;
                    color: #1e293b;
                    white-space: pre-wrap;
                    overflow-y: auto;
                    max-height: 200px;
                }
                .transcription-box:empty::before {
                    content: "Your speech will appear here...";
                    color: #94a3b8;
                    font-style: italic;
                }
                .confidence-meter {
                    height: 4px;
                    background: #e2e8f0;
                    border-radius: 2px;
                    margin-top: 0.5rem;
                    overflow: hidden;
                }
                .confidence-level {
                    height: 100%;
                    background: linear-gradient(90deg, #6366f1, #8b5cf6);
                    width: 0%;
                    transition: width 0.3s ease;
                }
              </style>
              
              <div class="transcription-box" id="transcriptionBox">
                  {{TRANSCRIPTION_TEXT}}
              </div>
              <div class="confidence-meter">
                  <div class="confidence-level" id="confidenceMeter" style="width: 0%;"></div>
              </div>
              <div style="text-align: right; color: #64748b; font-size: 0.75rem; margin-top: 0.25rem;">
                  Confidence: <span id="confidenceValue">0</span>%
              </div>
              
              <script>
              // Function to update the transcription in real-time
              function updateTranscription(text, confidence) {
                  const box = document.getElementById('transcriptionBox');
                  const meter = document.getElementById('confidenceMeter');
                  const value = document.getElementById('confidenceValue');
                  
                  if (box) box.textContent = text || 'Your speech will appear here...';
                  if (meter) meter.style.width = (confidence * 100) + '%';
                  if (value) value.textContent = Math.round(confidence * 100);
                  
                  // Auto-scroll to bottom
                  if (box) box.scrollTop = box.scrollHeight;
              }
              
              // Simulate real-time updates
              let demoText = "";
              const demoPhrases = [
                  "I believe my experience in machine learning makes me a strong candidate...",
                  "One of my key achievements was developing a recommendation system that improved user engagement by 30%...",
                  "I'm particularly excited about this role because it aligns perfectly with my skills in Python and data analysis..."
              ];
              
              function simulateTranscription() {
                  const phrase = demoPhrases[Math.floor(Math.random() * demoPhrases.length)];
                  let i = 0;
                  const interval = setInterval(() => {
                      if (i < phrase.length) {
                          demoText += phrase[i];
                          const currentConfidence = 0.7 + Math.random() * 0.25;
                          updateTranscription(demoText, currentConfidence);
                          i++;
                      } else {
                          clearInterval(interval);
                          // Reset after a delay
                          setTimeout(() => {
                              demoText = "";
                              updateTranscription("", 0);
                              // Start again
                              setTimeout(simulateTranscription, 1000);
                          }, 2000);
                      }
                  }, 50);
              }
              
              // Start simulation after a short delay
              setTimeout(simulateTranscription, 1500);
              </script>
            </div>
            """.replace("{{TRANSCRIPTION_TEXT}}", st.session_state.get('transcription_text', '')), 
            unsafe_allow_html=True
        )
        
        if st.session_state.current_question:
            q = st.session_state.current_question
            
            # 1. Webcam at the top (if enabled)
            if st.session_state.get('show_camera', True):
                st.markdown("#### 📹 Video Preview")
                camera_image = st.camera_input("Live Camera Feed", key=f"camera_{st.session_state.question_count}", label_visibility="collapsed")
                
                if camera_image:
                    st.image(camera_image, caption="✅ Camera active - Your video is being monitored", use_column_width=True)
                else:
                    st.markdown("""
                    <div style='background:#EFF6FF;border:1px solid #BFDBFE;padding:1rem;border-radius:8px;text-align:center;'>
                        <p style='margin:0;color:#1E40AF;font-size:0.875rem;'>📷 Click "Take Photo" to activate your camera</p>
                        <p style='margin:0.5rem 0 0 0;color:#64748B;font-size:0.8rem;'>The interviewer can see you during the session</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
            
            # 2. Question display
            question_label = f"Q{st.session_state.question_count}"
            
            # Add badge for custom/follow-up questions
            badge = ""
            if q.get('custom_generated'):
                badge = " <span style='background:#10B981;color:white;padding:0.25rem 0.75rem;border-radius:12px;font-size:0.75rem;font-weight:600;margin-left:0.5rem;'>📋 TAILORED</span>"
            elif q.get('is_follow_up'):
                badge = " <span style='background:#F59E0B;color:white;padding:0.25rem 0.75rem;border-radius:12px;font-size:0.75rem;font-weight:600;margin-left:0.5rem;'>↩️ FOLLOW-UP</span>"
            
            st.markdown(f"### {question_label}. {q['question']}{badge}", unsafe_allow_html=True)
            
            # TTS for the question
            if st.session_state.speak_next_question:
                with st.spinner("AI Speaking..."):
                    try:
                        audio_bytes = st.session_state.tts_engine.speak_text(q['question'])
                        if audio_bytes:
                            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
                    except Exception as e:
                        st.warning(f"TTS error: {e}")
                    st.session_state.speak_next_question = False

            if st.session_state.question_start_time:
                elapsed = time.time() - st.session_state.question_start_time
                st.caption(f"Elapsed: {elapsed:.1f}s")
            
            st.markdown("---")
            
            # 3. Answer submission methods
            st.markdown("#### Answer Input")
            
            # Audio input widgets
            audio_input = st.audio_input("Record answer", key=f"audio_{st.session_state.question_count}", disabled=st.session_state.processing or st.session_state.paused)
            uploaded = st.file_uploader("Upload audio (wav)", type=['wav'], key=f"upload_{st.session_state.question_count}")
            
            # Typed input with unique key per question
            typed_answer = st.text_area("Type answer (optional)", key=f"typed_answer_{st.session_state.question_count}", value="")
            submit_typed = st.button("Submit Typed Answer", use_container_width=True, disabled=st.session_state.processing or st.session_state.paused or not typed_answer.strip())
                
        # Process audio answer (recorded or uploaded)
        if not st.session_state.processing and not st.session_state.paused:
            if audio_input is not None or uploaded is not None:
                st.session_state.processing = True
                with st.spinner("🔄 Processing your answer..."):
                    try:
                        # Choose source
                        audio_source = audio_input if audio_input is not None else uploaded
                        stt_result = transcribe_audio(audio_source, engine=st.session_state.stt_engine_name)
                        
                        if stt_result['success']:
                            st.session_state.stt_metrics = stt_result
                            _process_answer(stt_result['text'], stt_result)
                        else:
                            st.error(f"❌ {stt_result.get('error', 'Could not process audio')}")
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
                    finally:
                        st.session_state.processing = False
                        st.rerun()
        
        # Process typed answer
        if submit_typed:
            if typed_answer and typed_answer.strip():
                st.session_state.processing = True
                _process_answer(typed_answer.strip(), stt_result_meta={})
                st.session_state.processing = False
                st.rerun()

        # Show feedback if available
        if st.session_state.show_feedback and st.session_state.current_evaluation:
                st.markdown("---")
                st.markdown("### 📋 Instant Feedback")

                eval_data = st.session_state.current_evaluation

                # Score display
                score_cols = st.columns(5)
                scores = [
                    ("Overall", eval_data['overall_score']),
                    ("Technical", eval_data['technical_accuracy']),
                    ("Communication", eval_data['communication_skills']),
                    ("Tone", eval_data['sentiment_tone']),
                    ("Completeness", eval_data['completeness'])
                ]

                for col, (label, score) in zip(score_cols, scores):
                    with col:
                        st.metric(label, f"{score:.0f}")

                # Radar chart for skills
                categories = ["Technical", "Communication", "Tone", "Completeness"]
                values = [
                    eval_data['technical_accuracy'],
                    eval_data['communication_skills'],
                    eval_data['sentiment_tone'],
                    eval_data['completeness']
                ]
                if PLOTLY_AVAILABLE:
                    # Note: Need to import plotly.graph_objects as go
                    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='Skills'))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Install plotly to see radar charts: pip install plotly")

                # Detailed feedback
                feedback = eval_data['feedback']

                if feedback.get('strengths'):
                    with st.expander("✅ Strengths", expanded=True):
                        for strength in feedback['strengths']:
                            st.markdown(f"- {strength}")

                if feedback.get('weaknesses'):
                    with st.expander("⚠️ Areas for Improvement"):
                        for weakness in feedback['weaknesses']:
                            st.markdown(f"- {weakness}")

                if feedback.get('suggestions'):
                    with st.expander("💡 Suggestions"):
                        for suggestion in feedback['suggestions']:
                            st.markdown(f"- {suggestion}")

                # Optional voice feedback
                if st.toggle("🔊 Speak Feedback", value=False):
                    with st.spinner("AI generating voice feedback..."):
                        try:
                            # Assuming generate_feedback_speech compiles feedback into a single string
                            speech_text = st.session_state.tts_engine.generate_feedback_speech(eval_data)
                            audio_bytes = st.session_state.tts_engine.speak_text(speech_text)
                            if audio_bytes:
                                st.audio(audio_bytes, format='audio/mp3', autoplay=True)
                        except Exception:
                            st.info("TTS engine not available for feedback speech.")

                # Continue button
                if st.button("➡️ Continue to Next Question", type="primary", use_container_width=True):
                    st.session_state.show_feedback = False
                    st.rerun()

# =============================
# HISTORY TAB
# =============================
with tab_history:
    st.markdown("### 📚 Past Sessions")
    db = get_database()
    sessions = db.get_recent_sessions(limit=20)
    if not sessions:
        st.info("No sessions found yet. Complete an interview to see history here.")
    else:
        # Create a display name that includes the user's name if available, falling back to anonymous
        options = [f"{s['session_id']} | {s.get('user_name', 'Anonymous')} | {s['mode']} | {s['difficulty']} | {s['start_time'][:19]}" for s in sessions]
        selected = st.selectbox("Select a session", options)
        if selected:
            sid = selected.split(" | ")[0]
            session = db.get_session(sid)
            analytics = db.get_analytics(sid)

            st.markdown(f"**User:** {session.get('user_name', 'Anonymous')} | **Mode:** {session['mode']} | **Difficulty:** {session['difficulty']}")
            st.markdown(f"**Overall Score:** {session['overall_score']:.1f}")

            # Skill bars
            skills = analytics.get('skill_breakdown', {})
            bar_cols = st.columns(4)
            # Use fixed order for display consistency
            skill_order = ['technical_accuracy', 'communication_skills', 'sentiment_tone', 'completeness']
            
            for k in skill_order:
                if k in skills:
                    v = skills[k]
                    with bar_cols.pop(0) if bar_cols else st.container(): # Use pop(0) to sequence columns
                        st.metric(k.replace('_',' ').title(), f"{v:.1f}")
                        st.progress(v/100)

            # Question list
            with st.expander("📝 Question Details", expanded=False):
                for idx, q in enumerate(session['questions'], 1):
                    st.markdown(f"**Q{idx}.** {q['question']}")
                    st.markdown(f"↪️ *Answer:* {q['answer']}")
                    # Safely access evaluation data
                    score = q['evaluation'].get('overall_score', 'N/A')
                    grade = q['evaluation'].get('grade', 'N/A')
                    st.caption(f"Score: {score}/100 | Grade: {grade}")
                    st.markdown("---")

            # Download buttons
            c1, c2, c3 = st.columns(3)
            with c1:
                # PDF report download (requires file to be written and then read)
                if st.button("📄 PDF Report", key=f"pdf_btn_{sid}"):
                    with st.spinner("Preparing PDF..."):
                        path = generate_report(session, analytics, format="pdf")
                        if os.path.exists(path):
                            with open(path, 'rb') as f:
                                st.download_button("Download PDF", f.read(), file_name=f"{sid}.pdf", mime="application/pdf", key=f"pdf_dl_{sid}")
                        else:
                            st.warning("PDF file not found. Check report generation library (fpdf/fpdf2).")

            with c2:
                # Text report download
                txt_path = generate_report(session, analytics, format="txt")
                with open(txt_path, 'r', encoding='utf-8') as f:
                    st.download_button("📄 Text Report", f.read(), file_name=f"{sid}.txt", key=f"txt_dl_{sid}")
            with c3:
                # JSON data download
                json_data = generate_report(session, analytics, format="json")
                st.download_button("📄 JSON Data", json_data, file_name=f"{sid}.json", mime="application/json", key=f"json_dl_{sid}")

# =============================
# SETTINGS TAB
# =============================
with tab_settings:
    st.markdown("### ⚙️ Application Settings")
    st.write("Customize your interview experience with these settings.")

    # Create tabs for different setting categories
    settings_tabs = st.tabs(["🎙️ Speech", "🎨 Interface", "📊 Evaluation", "🔐 Account"])
    
    with settings_tabs[0]:  # Speech Settings
        st.markdown("#### Speech Recognition & Synthesis")
        
        col1, col2 = st.columns(2)
        with col1:
            # STT Engine Selection
            st.session_state.stt_engine_name = st.selectbox(
                "Speech-to-Text Engine", 
                ["whisper", "google", "sphinx"], 
                index=["whisper", "google", "sphinx"].index(st.session_state.stt_engine_name),
                help="Choose the speech recognition engine (Whisper is recommended for accuracy)"
            )
            
            # STT Advanced Settings
            with st.expander("Advanced Speech Settings"):
                st.slider(
                    "Speech Recognition Confidence Threshold",
                    min_value=0.1, 
                    max_value=1.0, 
                    value=0.7, 
                    step=0.05,
                    help="Higher values require more confidence in speech recognition"
                )
                st.checkbox(
                    "Enable Real-time Transcription", 
                    value=True,
                    help="Show words as they're being recognized"
                )
        
        with col2:
            # TTS Engine Selection
            tts_choice = st.selectbox(
                "Text-to-Speech Engine", 
                ["gtts", "pyttsx3"], 
                index=["gtts", "pyttsx3"].index(st.session_state.tts_engine_name),
                help="Choose the voice for the AI interviewer"
            )
            if tts_choice != st.session_state.tts_engine_name:
                st.session_state.tts_engine_name = tts_choice
                st.session_state.tts_engine = TTSEngine(engine=tts_choice)
            
            # TTS Advanced Settings
            with st.expander("Voice Settings"):
                st.slider(
                    "Speech Rate", 
                    min_value=0.5, 
                    max_value=2.0, 
                    value=1.0, 
                    step=0.1,
                    help="Adjust the speaking rate of the AI"
                )
                st.slider(
                    "Pitch", 
                    min_value=0.5, 
                    max_value=2.0, 
                    value=1.0, 
                    step=0.1,
                    help="Adjust the pitch of the AI's voice"
                )
    
    with settings_tabs[1]:  # Interface Settings
        st.markdown("#### User Interface Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Display Options**")
            st.toggle("Dark Mode", value=False, key='dark_mode', help="Switch between light and dark theme")
            st.toggle("Show Video Preview", value=True, key='show_video', help="Display webcam feed during interviews")
            st.toggle("Enable Animations", value=True, key='enable_animations', help="Enable UI animations and transitions")
        
        with col2:
            st.markdown("**Layout**")
            st.toggle("Show Real-time Metrics", value=True, key='show_metrics', help="Display performance metrics during interviews")
            st.toggle("Compact Mode", value=False, key='compact_mode', help="Use a more compact layout")
            st.toggle("Sidebar Minimized", value=False, key='sidebar_minimized', help="Automatically minimize the sidebar")
        
        st.markdown("**Theme**")
        theme = st.selectbox(
            "Color Theme",
            ["Blue (Default)", "Green", "Purple", "Red", "Custom"],
            index=0,
            help="Choose a color scheme for the application"
        )
    
    with settings_tabs[2]:  # Evaluation Settings
        st.markdown("#### Evaluation & Feedback")
        
        st.markdown("**Scoring**")
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Technical Weight", 0, 100, 50, help="How much weight to give technical accuracy in scoring")
            st.checkbox("Enable Detailed Feedback", value=True, help="Provide in-depth analysis of responses")
        with col2:
            st.slider("Communication Weight", 0, 100, 30, help="How much weight to give communication skills")
            st.checkbox("Show Confidence Scores", value=True, help="Display confidence levels for evaluations")
        
        st.markdown("**Feedback Options**")
        st.checkbox("Provide Real-time Hints", value=True, help="Show suggestions during the interview")
        st.checkbox("Record Interview", value=True, help="Save a recording of the interview for review")
        st.checkbox("Email Session Report", value=False, help="Send a detailed report via email after completion")
        
        # Question Bank Preview
        st.markdown("#### Question Bank")
        if st.session_state.flow_manager is None:
            st.session_state.flow_manager = InterviewFlowManager()
            
        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            preview_mode = st.selectbox(
                "Interview Mode", 
                ["HR", "Technical", "Mixed"], 
                key='preview_mode',
                help="Filter questions by interview type"
            )
        with preview_col2:
            preview_level = st.selectbox(
                "Difficulty Level", 
                ["Beginner", "Intermediate", "Advanced", "Expert"], 
                key='preview_level',
                help="Filter questions by difficulty"
            )
            
        # Get and display questions
        qs = st.session_state.flow_manager.get_all_questions(preview_mode, preview_level)
        if qs:
            st.info(f"Showing {len(qs)} questions for {preview_mode} mode ({preview_level} level)")
            with st.expander("View Questions"):
                for i, q in enumerate(qs, 1):
                    st.markdown(f"**{i}.** {q['question']}")
        else:
            st.warning("No questions found for the selected criteria.")
    
    with settings_tabs[3]:  # Account Settings
        st.markdown("#### Account Management")
        
        st.markdown("**Profile**")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Full Name", value=st.session_state.user_name, key='user_fullname')
            st.text_input("Email", value="user@example.com", disabled=True)
        with col2:
            st.text_input("Job Title", placeholder="Current/Most Recent Position")
            st.text_input("Company", placeholder="Current/Most Recent Company")
        
        st.markdown("**Preferences**")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Default Interview Mode", ["Technical", "HR", "Mixed"])
            st.checkbox("Email Notifications", value=True)
        with col2:
            st.selectbox("Default Difficulty", ["Intermediate", "Beginner", "Advanced", "Expert"])
            st.checkbox("Weekly Progress Report", value=True)
        
        st.markdown("**Account Actions**")
        col1, col2, _ = st.columns(3)
        with col1:
            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.user_name = st.session_state.user_fullname
                st.success("Profile updated successfully!")
        with col2:
            if st.button("🔒 Change Password", use_container_width=True):
                st.info("Password change functionality will be implemented soon")
        
        st.markdown("---")
        if st.button("🚪 Sign Out", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    # Save all settings
    if st.button("💾 Apply All Settings", type="primary", use_container_width=True, key="save_all_settings"):
        st.success("All settings have been saved successfully!")
        st.balloons()

# =============================
# ABOUT TAB
# =============================
with tab_about:
    st.markdown("### ℹ️ About This App")
    st.write("AI Virtual Interview Coach with advanced evaluation, reporting, and rich UI.")
    st.write("Use the Settings and History tabs to customize and review your practice.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🤖 AI Virtual Interview Coach | Powered by Advanced NLP & Machine Learning</p>
    <p style='font-size: 0.8rem;'>Practice makes perfect. Good luck with your interviews!</p>
</div>
""", unsafe_allow_html=True) 