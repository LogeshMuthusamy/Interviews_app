# AI-Powered Virtual Interview Practice Application

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hireprepai.streamlit.app/)

**🚀 Live Demo:** [Access the App Here](https://hireprepai.streamlit.app/)

## 🎯 Project Overview

This is a comprehensive AI-powered virtual interview practice application built with Streamlit. It simulates realistic interview scenarios, provides accurate evaluation using advanced NLP models, and delivers actionable feedback to help users improve their interview skills.

## ✨ Features

### Core Functionality

- **🎤 Voice Interaction**: Speak your answers using your microphone with advanced speech-to-text
- **🤖 AI Interviewer**: Natural text-to-speech voice feedback
- **📹 Video Recording**: Webcam integration for visual feedback (future: facial expression analysis)
- **📊 Real-time Evaluation**: Instant scoring and feedback using NLP models

### Interview Modes

- **HR Interview**: Behavioral and situational questions
- **Technical Interview**: Programming, data science, and technical concept questions
- **Mixed Interview**: Combination of HR and technical questions

### Difficulty Levels

- **Beginner**: Entry-level questions
- **Intermediate**: Mid-level professional questions
- **Advanced**: Senior-level and expert questions

### Evaluation Metrics

1. **Technical Accuracy** (0-100): Correctness and depth of technical knowledge
2. **Communication Skills** (0-100): Fluency, clarity, structure
3. **Sentiment & Tone** (0-100): Confidence, positivity, professionalism
4. **Completeness** (0-100): Thoroughness and relevance

### Advanced Features

- **Speech Analysis**: Words per minute, filler words detection, pause tracking
- **Semantic Similarity**: BERT-based answer evaluation
- **Follow-up Questions**: Context-aware follow-up generation
- **Session Management**: Save and track all interview sessions
- **Comprehensive Reports**: PDF/Text/JSON reports with detailed analytics
- **Progress Tracking**: Real-time progress indicators

## 🏗️ Architecture

```
AI_interview_app/
├── app_enhanced.py          # Main Streamlit application (NEW VERSION)
├── app.py                   # Original simple version
├── requirements.txt         # Python dependencies
├── config/
│   └── questions.json       # Question bank with metadata
├── modules/
│   ├── stt_engine.py       # Speech-to-Text module
│   ├── nlp_evaluator.py    # NLP evaluation engine
│   ├── tts_engine.py       # Text-to-Speech module
│   ├── database.py         # Session storage and analytics
│   ├── report_generator.py # PDF/Text report generation
│   └── interview_flow.py   # Interview flow management
├── data/
│   └── interview_sessions.json  # Session database (auto-created)
└── reports/                # Generated reports (auto-created)
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Microphone access for speech input
- Webcam (optional, for video features)

### Step 1: Clone or Download the Project

```bash
cd AI_interview_app
```

### Step 2: Create Virtual Environment (Recommended)

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
# Install basic dependencies first
pip install streamlit SpeechRecognition gTTS pyttsx3 textblob fpdf

# For advanced NLP features (optional but recommended)
pip install sentence-transformers transformers torch

# Install all dependencies at once
pip install -r requirements.txt
```

### Step 4: Download Required Models (First Run)

The first time you run the app, it will automatically download required NLP models:

- sentence-transformers/all-MiniLM-L6-v2 (~80MB)
- TextBlob corpora

## 🎮 Usage

### Running the Application

```powershell
# Run the enhanced version (recommended)
streamlit run app_enhanced.py

# Or run the original simple version
streamlit run app.py
```

### Using the Application

1. **Configure Your Interview**
   - Enter your name
   - Select interview mode (HR/Technical/Mixed)
   - Choose difficulty level
   - Set number of questions (3-10)

2. **Start Interview**
   - Click "🚀 Start Interview" in the sidebar
   - Read the question displayed
   - Click the microphone button to record your answer
   - Speak clearly and naturally

3. **Review Feedback**
   - View instant scores for each answer
   - Review strengths and improvement areas
   - Check speech metrics (WPM, clarity, filler words)

4. **Complete Session**
   - Answer all questions or click "End Interview Early"
   - View comprehensive session analytics
   - Download PDF/Text/JSON reports

## 📊 Evaluation System

### Technical Accuracy (40% for Technical, 10% for HR)

- Keyword matching against expected terms
- Semantic similarity using BERT embeddings
- Technical concept coverage
- Answer depth and detail

### Communication Skills (25-35%)

- Speech fluency and structure
- Vocabulary diversity
- Sentence complexity
- Professional language usage

### Sentiment & Tone (15-30%)

- Confidence indicators
- Emotional positivity
- Uncertainty detection
- Overall professionalism

### Completeness (20-25%)

- Answer length appropriateness
- Question element coverage
- Expected duration match

## 🎯 Question Bank

The application includes **45+ curated questions** across:

- **HR**: 15 questions (5 per difficulty level)
- **Technical**: 15 questions (5 per difficulty level)
- **Mixed**: 15 questions (5 per difficulty level)

Each question includes:

- Expected keywords
- Technical concepts (for technical questions)
- Expected duration
- Follow-up triggers

## 📈 Reports and Analytics

### Session Reports Include:

- Overall score and grade
- Question-by-question breakdown
- Skill-wise performance analysis
- Strengths and weaknesses
- Actionable suggestions
- Missing technical points
- Speech metrics summary

### Export Formats:

- **PDF**: Professional formatted report with charts
- **Text**: Plain text for easy reading
- **JSON**: Machine-readable data for further analysis

## 🔧 Configuration

### Customizing Questions

Edit `config/questions.json` to add your own questions:

```json
{
  "Technical": {
    "Beginner": [
      {
        "question": "Your question here?",
        "keywords": ["key1", "key2", "key3"],
        "expected_duration": 60,
        "technical_concepts": ["concept1", "concept2"]
      }
    ]
  }
}
```

### TTS Engine Selection

In `app_enhanced.py`, modify:

```python
st.session_state.tts_engine = TTSEngine(engine="gtts")  # or "pyttsx3"
```

### STT Engine Selection

In `modules/stt_engine.py`, modify the default engine:

```python
stt_engine = STTEngine(engine="google")  # or "sphinx" for offline
```

## 🐛 Troubleshooting

### Common Issues

**1. Microphone not working**

- Check browser permissions for microphone access
- Ensure microphone is properly connected
- Try refreshing the page

**2. Audio transcription fails**

- Check internet connection (Google STT requires internet)
- Speak clearly and avoid background noise
- Try using a better quality microphone

**3. NLP models not loading**

- First run requires internet to download models
- Ensure sufficient disk space (~500MB)
- Try: `pip install --upgrade sentence-transformers`

**4. PDF generation fails**

- Install fpdf: `pip install fpdf`
- Text report will be generated as fallback

**5. Import errors**

- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## 🚧 Future Enhancements

### Planned Features

- [ ] Real-time facial expression analysis using OpenCV
- [ ] Body language and posture feedback
- [ ] Voice emotion detection
- [ ] Multi-language support
- [ ] Integration with OpenAI Whisper for better STT
- [ ] GPT-4 based dynamic question generation
- [ ] Video recording and playback
- [ ] Comparison with industry benchmarks
- [ ] Team/Organization dashboard
- [ ] Mobile app version

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional question banks
- New evaluation metrics
- UI/UX enhancements
- Performance optimizations
- Additional language support

## 📄 License

This project is created for educational purposes.

## 👥 Authors

- **Lead AI Architect & Developer**: AI Assistant
- **Project Requirements**: Based on comprehensive interview practice system specifications

## 🙏 Acknowledgments

- Streamlit for the excellent web framework
- Hugging Face for transformer models
- Google for Speech Recognition API
- Open source community for various libraries

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review the code comments
3. Consult the module documentation

---

## 🎓 Educational Use

This application is designed to help students and professionals:

- Practice for job interviews
- Improve communication skills
- Build confidence in technical discussions
- Track progress over time
- Identify areas for improvement

**Good luck with your interviews! 🚀**
