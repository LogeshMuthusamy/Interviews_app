# 📁 Project Structure

```
AI_interview_app/
│
├── 📄 app_enhanced.py              # Main application (Premium UI, 1000+ lines)
├── 📄 app.py                       # Original simple version
│
├── 📚 Documentation
│   ├── README.md                   # Complete project documentation
│   ├── QUICKSTART.md              # 5-minute quick start guide
│   ├── INSTALLATION.md            # Detailed installation guide
│   └── PROJECT_SUMMARY.md         # Project completion summary
│
├── ⚙️ Configuration
│   ├── requirements.txt           # Python dependencies (20+ packages)
│   ├── setup.ps1                  # Automated PowerShell setup
│   ├── test_setup.py              # Installation verification
│   └── .gitignore                 # Git configuration
│
├── 📂 config/                     # Configuration files
│   ├── questions.json             # 45+ interview questions
│   │   ├── HR (Beginner/Intermediate/Advanced)
│   │   ├── Technical (Beginner/Intermediate/Advanced)
│   │   └── Mixed (Beginner/Intermediate/Advanced)
│   └── settings.json              # Application settings
│       ├── Speech recognition config
│       ├── TTS settings
│       ├── NLP parameters
│       ├── Scoring weights
│       └── UI preferences
│
├── 📂 modules/                    # Core application modules
│   ├── __init__.py                # Package initialization
│   ├── stt_engine.py              # Speech-to-Text Engine
│   │   ├── Google Speech Recognition
│   │   ├── Confidence scoring
│   │   ├── WPM tracking
│   │   ├── Filler word detection
│   │   └── Clarity score calculation
│   │
│   ├── nlp_evaluator.py           # NLP Evaluation Engine
│   │   ├── Technical accuracy (BERT embeddings)
│   │   ├── Communication skills analysis
│   │   ├── Sentiment & tone detection
│   │   ├── Completeness scoring
│   │   └── Feedback generation
│   │
│   ├── tts_engine.py              # Text-to-Speech Engine
│   │   ├── gTTS integration
│   │   ├── pyttsx3 support
│   │   ├── Voice feedback generation
│   │   └── Message templates
│   │
│   ├── database.py                # Database Management
│   │   ├── JSON storage
│   │   ├── Session lifecycle
│   │   ├── Analytics calculation
│   │   └── Historical tracking
│   │
│   ├── report_generator.py        # Report Generation
│   │   ├── PDF report creation
│   │   ├── Text report fallback
│   │   ├── JSON export
│   │   └── Analytics visualization
│   │
│   └── interview_flow.py          # Interview Flow Manager
│       ├── Question selection
│       ├── Follow-up generation
│       ├── Progress tracking
│       └── Session management
│
├── 📂 data/                       # Session data (auto-generated)
│   ├── .gitkeep                   # Directory marker
│   └── interview_sessions.json    # Stored sessions (created at runtime)
│
└── 📂 reports/                    # Generated reports (auto-generated)
    ├── .gitkeep                   # Directory marker
    └── interview_report_*.pdf     # Session reports (created at runtime)

```

---

## 📊 File Statistics

| Category             | Files  | Lines of Code | Description                |
| -------------------- | ------ | ------------- | -------------------------- |
| **Main Application** | 2      | ~1,200        | Streamlit UI and logic     |
| **Core Modules**     | 6      | ~2,500        | STT, NLP, TTS, DB, Reports |
| **Configuration**    | 2      | ~500          | Questions and settings     |
| **Documentation**    | 4      | ~2,000        | User and developer guides  |
| **Setup Scripts**    | 3      | ~400          | Installation and testing   |
| **Total**            | **17** | **~6,600**    | Complete project           |

---

## 🔧 Module Dependencies

```
app_enhanced.py
    ├── modules.stt_engine
    │   └── speech_recognition
    │   └── io, numpy
    │
    ├── modules.nlp_evaluator
    │   └── sentence_transformers (optional)
    │   └── textblob (optional)
    │   └── re, collections
    │
    ├── modules.tts_engine
    │   └── gtts
    │   └── pyttsx3 (optional)
    │   └── io, tempfile
    │
    ├── modules.database
    │   └── json, os, datetime
    │
    ├── modules.report_generator
    │   └── fpdf (optional)
    │   └── json, datetime
    │
    └── modules.interview_flow
        └── json, random
```

---

## 🎯 Key Features by Module

### 🎤 STT Engine (stt_engine.py)

- Multi-engine support (Google, Sphinx)
- Audio preprocessing
- Confidence scoring (0-1)
- Speech metrics:
  - Words per minute
  - Filler word detection (14 types)
  - Pause counting
  - Clarity score (0-100)

### 🧠 NLP Evaluator (nlp_evaluator.py)

- 4-dimensional scoring:
  1. **Technical Accuracy** (0-100)
     - Keyword matching
     - BERT semantic similarity
     - Concept coverage
  2. **Communication Skills** (0-100)
     - Fluency analysis
     - Vocabulary diversity
     - Structure scoring
  3. **Sentiment & Tone** (0-100)
     - TextBlob sentiment
     - Confidence detection
     - Professional language
  4. **Completeness** (0-100)
     - Length appropriateness
     - Question coverage
- Detailed feedback generation
- Grade assignment (A-F)

### 🔊 TTS Engine (tts_engine.py)

- Dual backend (online/offline)
- Natural feedback generation
- Template-based messages
- Voice customization

### 💾 Database (database.py)

- Session CRUD operations
- Analytics engine
- Historical tracking
- JSON persistence

### 📄 Report Generator (report_generator.py)

- PDF with charts
- Text fallback
- JSON export
- Comprehensive analytics

### 🔄 Interview Flow (interview_flow.py)

- Smart question selection
- Follow-up generation
- Progress tracking
- Session state management

---

## 🎨 UI Components (app_enhanced.py)

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│            Main Header (Gradient)               │
│         🤖 AI Virtual Interview Coach           │
└─────────────────────────────────────────────────┘

┌──────────┬──────────────────────────────────────┐
│          │                                      │
│ Sidebar  │         Main Content Area           │
│          │                                      │
│ ⚙️ Setup  │  ┌────────────┬─────────────────┐  │
│          │  │            │                 │  │
│ • Name   │  │  Video     │   Conversation  │  │
│ • Mode   │  │  Preview   │   Transcript    │  │
│ • Level  │  │            │                 │  │
│ • Count  │  │  📹        │   💬 Chat       │  │
│          │  │            │                 │  │
│ 🚀 Start  │  │  Metrics   │   🎤 Record    │  │
│          │  │            │                 │  │
│ 📈 Track  │  └────────────┴─────────────────┘  │
│          │                                      │
│          │         📊 Feedback Section          │
│          │                                      │
└──────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                   Footer                        │
└─────────────────────────────────────────────────┘
```

### Features

- ✅ Gradient header
- ✅ Custom CSS styling
- ✅ Real-time progress bar
- ✅ Interactive score cards
- ✅ Chat-style transcript
- ✅ Collapsible feedback
- ✅ Video preview
- ✅ Speech metrics display
- ✅ Download buttons

---

## 📦 Dependencies Overview

### Core (Required)

```
streamlit              # Web framework
SpeechRecognition     # STT
gTTS                  # TTS
textblob              # Sentiment
fpdf                  # PDF reports
```

### Advanced (Recommended)

```
sentence-transformers  # BERT embeddings
transformers          # NLP models
torch                 # ML backend
```

### Optional (Enhanced features)

```
pyttsx3               # Offline TTS
pandas                # Data analysis
matplotlib            # Visualization
plotly                # Interactive charts
opencv-python         # Video processing
```

---

## 🚀 Quick Commands

### Setup

```powershell
.\setup.ps1                    # Automated setup
```

### Run

```powershell
streamlit run app_enhanced.py  # Premium version
streamlit run app.py           # Simple version
```

### Test

```powershell
python test_setup.py           # Verify installation
```

### Clean

```powershell
Remove-Item data\*.json       # Clear sessions
Remove-Item reports\*         # Clear reports
```

---

## 📈 Development Workflow

1. **Configuration** → Edit `config/*.json`
2. **Modules** → Modify `modules/*.py`
3. **UI** → Update `app_enhanced.py`
4. **Test** → Run `python test_setup.py`
5. **Deploy** → Run `streamlit run app_enhanced.py`

---

## 🔐 Security Notes

- ✅ No hardcoded credentials
- ✅ Local data storage
- ✅ Environment-based config
- ✅ No external API keys required
- ⚠️ Google STT requires internet

---

## 📝 Maintenance

### Regular Updates

- Review question bank quarterly
- Update NLP models annually
- Check dependency versions monthly
- Backup session data weekly

### Logs Location

- Session data: `data/interview_sessions.json`
- Reports: `reports/*.pdf`
- Streamlit cache: `.streamlit/cache/`

---

**For complete documentation, see README.md** 📚
