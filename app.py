import streamlit as st
import time # Used to simulate AI processing time
import speech_recognition as sr # The tool we installed for audio
import io  # For handling in-memory audio bytes

# --- 1. CONFIGURATION AND STATE MANAGEMENT ---

# Must be the first Streamlit command
st.set_page_config(page_title="🤖 AI Virtual Interviewer", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State: This is how Streamlit remembers information across clicks.
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = "Welcome! Configure your interview in the sidebar to begin."
if 'transcript' not in st.session_state:
    st.session_state.transcript = []

# Dummy question generator (will be replaced by AI later)
QUESTION_BANK = {
    "HR": ["Tell me about a time you handled conflict.", "Where do you see yourself in 5 years?"],
    "Technical": ["Explain the difference between a list and a tuple in Python.", "What is a primary key in SQL?"],
    "Mixed": ["What's your biggest weakness?", "Walk me through a recent data project."],
}
def get_next_question(mode, index):
    """Retrieves the next question based on the selected mode."""
    q_list = QUESTION_BANK.get(mode, QUESTION_BANK["HR"])
    return q_list[index % len(q_list)] # Cycle through questions

# --- 2. SIDEBAR (SETTINGS) ---

with st.sidebar:
    st.header("⚙️ Interview Setup")
    
    # 2.1 Mode Selection 
    interview_mode = st.selectbox(
        "Select Interview Mode",
        ("HR", "Technical", "Mixed"),
        key='selected_mode'
    )
    
    # 2.2 Difficulty Level 
    difficulty = st.select_slider(
        "Difficulty Level",
        options=['Beginner', 'Intermediate', 'Advanced'],
        key='selected_difficulty'
    )

    st.markdown("---")
    
    # 2.3 Start/Reset Button Logic 
    if st.button("Start Interview / Reset", type="primary"):
        st.session_state.interview_started = True
        st.session_state.question_index = 0
        st.session_state.transcript = [] # Clear previous session
        st.session_state.current_question = get_next_question(interview_mode, 0)
        st.session_state.transcript.append({"speaker": "AI", "text": st.session_state.current_question})
        st.success("Interview started! Look at the main screen for your first question.")

# --- 3. MAIN DASHBOARD LAYOUT ---

st.title("🤖 AI-Powered Virtual Interview Practice")
st.markdown(f"**Mode:** `{st.session_state.get('selected_mode', 'HR')}` | **Difficulty:** `{st.session_state.get('selected_difficulty', 'Beginner')}`")
st.write("---")

# 3.1 Split the View into Two Columns
col1, col2 = st.columns([1, 2]) # 1: Camera (Visuals), 2: Transcript (Content)

# COLUMN 1: Visuals (Camera & AI Avatar) 
with col1:
    st.subheader("Candidate Visuals")
    # This is your camera input/preview 
    st.camera_input("Your Live Video Feed", key="live_camera")
    
    # Placeholder for AI feedback (later used for tone/sentiment analysis)
    st.markdown("---")
    st.info("AI Tone Analysis: Waiting for response...")


# COLUMN 2: Interview Flow (Transcript & Input) 
with col2:
    st.subheader("Interview Transcript & Input")
    
    # 3.2 Dynamic Transcript Display (The Conversation)
    transcript_placeholder = st.empty()
    
    # Display the current conversation log
    # Note: Some Streamlit versions don't support container(height/border)
    # Use a simple container for broad compatibility
    with transcript_placeholder.container():
        for entry in st.session_state.transcript:
            if entry["speaker"] == "AI":
                st.chat_message("assistant").write(entry["text"])
            else:
                st.chat_message("user").write(entry["text"])

    st.markdown("---")

    # 3.3 Audio Input & Processing 
    if st.session_state.interview_started:
        st.write(f"**AI Question:** *{st.session_state.current_question}*")
        
        # Audio input widget 
        audio_value = st.audio_input("🎤 Record Your Answer", key="user_mic_input")

        # Logic to process the user's recorded answer
        if audio_value is not None:
            with st.spinner("Transcribing and evaluating your answer..."):
                time.sleep(2) # Simulate processing time

                # --- SPEECH-TO-TEXT IMPLEMENTATION ---
                recognizer = sr.Recognizer()
                try:
                    # Streamlit's audio_input returns an UploadedFile-like object.
                    # Convert to BytesIO so SpeechRecognition can read it reliably.
                    audio_bytes = audio_value.getvalue() if hasattr(audio_value, 'getvalue') else audio_value.read()
                    with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio_data = recognizer.record(source)
                        user_text = recognizer.recognize_google(audio_data)

                        # Update transcript with user's answer
                        st.session_state.transcript.append({"speaker": "User", "text": user_text})

                        # --- NEXT QUESTION LOGIC ---
                        st.session_state.question_index += 1
                        next_q = get_next_question(st.session_state.get('selected_mode', 'HR'), st.session_state.question_index)
                        
                        st.session_state.current_question = next_q
                        st.session_state.transcript.append({"speaker": "AI", "text": next_q})

                        # Rerun the script to update the transcript with the new Q&A
                        st.rerun() 

                except sr.UnknownValueError:
                    st.warning("⚠️ Could not understand audio. Please try recording again.")
                except sr.RequestError:
                    st.error("🚫 Google Speech Recognition service failed.")

    else:
        st.info("Click 'Start Interview' in the sidebar to load the first question.")

# --- END OF APP ---