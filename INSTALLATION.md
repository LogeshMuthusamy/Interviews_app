# Complete Installation & Usage Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Using the Application](#using-the-application)
5. [Features Overview](#features-overview)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended for optimal performance)
- **Disk Space**: ~2GB for application and models
- **Internet**: Required for first-time setup and Google Speech Recognition

### Hardware Requirements

- **Microphone**: Any USB or built-in microphone
- **Webcam**: Optional (for video features)
- **Speakers/Headphones**: For voice feedback

---

## Installation

### Method 1: Automated Setup (Recommended for Windows)

1. **Open PowerShell** in the project directory:

   ```powershell
   cd c:\gate\AI_interview_app
   ```

2. **Run the setup script**:

   ```powershell
   .\setup.ps1
   ```

3. **Wait for installation** to complete (5-10 minutes on first run)

### Method 2: Manual Installation

1. **Create virtual environment**:

   ```powershell
   python -m venv venv
   ```

2. **Activate virtual environment**:

   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1

   # Windows CMD
   venv\Scripts\activate.bat

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Upgrade pip**:

   ```powershell
   python -m pip install --upgrade pip
   ```

4. **Install dependencies**:

   ```powershell
   # Option A: Install all at once (slower but complete)
   pip install -r requirements.txt

   # Option B: Install in stages (faster, can skip optional packages)

   # Stage 1: Core packages (required)
   pip install streamlit SpeechRecognition gTTS textblob fpdf

   # Stage 2: NLP packages (optional but recommended)
   pip install sentence-transformers transformers torch

   # Stage 3: Additional packages (optional)
   pip install pandas numpy Pillow matplotlib plotly
   ```

5. **Download language data**:
   ```powershell
   python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
   ```

### Method 3: Minimal Installation (Basic Features Only)

If you want to quickly test the app with minimal dependencies:

```powershell
pip install streamlit SpeechRecognition gTTS textblob
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

**Note**: This will disable advanced NLP features but the app will still work.

---

## Running the Application

### Start the Application

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the enhanced version (recommended)
streamlit run app_enhanced.py

# Or run the simple version
streamlit run app.py
```

### Access the Application

The browser should automatically open to:

```
http://localhost:8501
```

If it doesn't open automatically, open your browser and navigate to that URL.

### Stop the Application

Press `Ctrl + C` in the PowerShell window to stop the server.

---

## Using the Application

### First-Time Setup

1. **Browser Permissions**:

   - Allow microphone access when prompted
   - Allow camera access (optional)

2. **Test Your Microphone**:
   - Speak and check if the browser detects audio
   - Adjust microphone volume in system settings if needed

### Starting an Interview

1. **Enter Your Name** (optional, but helps with tracking)

2. **Configure Interview**:

   - **Mode**: HR, Technical, or Mixed
   - **Difficulty**: Beginner, Intermediate, or Advanced
   - **Questions**: 3-10 questions (5 recommended)

3. **Click "🚀 Start Interview"**

### Answering Questions

1. **Read the question** displayed on screen

2. **Click the microphone button** 🎤 to start recording

3. **Speak your answer**:

   - Speak clearly and at normal pace
   - Aim for 30-90 seconds
   - Avoid excessive filler words

4. **Recording automatically stops** when you're done

5. **Wait for processing**:

   - Transcription: ~2-5 seconds
   - Evaluation: ~3-5 seconds

6. **Review feedback**:

   - Overall score and grade
   - Breakdown by skill area
   - Strengths and weaknesses
   - Specific suggestions

7. **Continue to next question**

### Completing the Interview

1. **Answer all questions** or click "End Interview Early"

2. **View session summary**:

   - Overall performance score
   - Skill breakdown
   - Pass/fail rate
   - Duration

3. **Download reports**:

   - PDF: Professional formatted report
   - Text: Simple text file
   - JSON: Raw data for analysis

4. **Start new interview** or review past sessions

---

## Features Overview

### Core Features

#### 🎤 Speech Recognition

- **Google Speech Recognition**: Cloud-based, high accuracy
- **Real-time transcription**: See your words as they're processed
- **Confidence scoring**: Know how well you were understood

#### 🤖 AI Evaluation

- **Technical Accuracy**: Keyword matching, semantic similarity
- **Communication Skills**: Fluency, structure, vocabulary
- **Sentiment Analysis**: Confidence, tone, professionalism
- **Completeness**: Coverage, depth, relevance

#### 📊 Speech Metrics

- **Words Per Minute**: Track speaking pace (ideal: 130-150)
- **Filler Words**: Detect "um", "uh", "like", etc.
- **Pauses**: Monitor natural breaks in speech
- **Clarity Score**: Overall speech quality (0-100)

#### 📈 Progress Tracking

- **Real-time progress bar**: See how far you've come
- **Question counter**: Track current position
- **Session history**: Review past interviews
- **Score trends**: Monitor improvement over time

### Advanced Features

#### 📄 Report Generation

- **PDF Reports**: Professional formatting with charts
- **Text Reports**: Simple, readable format
- **JSON Export**: Raw data for custom analysis

#### 🎯 Smart Question Selection

- **Difficulty-based**: Questions matched to your level
- **Follow-up questions**: Context-aware clarifications
- **No repetition**: Unique questions each session

#### 💾 Session Management

- **Auto-save**: All responses saved automatically
- **Session retrieval**: Review past interviews
- **Analytics**: Track improvement metrics

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'xyz'`

**Solution**:

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall specific package
pip install xyz

# Or reinstall all
pip install -r requirements.txt
```

#### 2. Microphone Not Working

**Problem**: Audio not being recorded or recognized

**Solutions**:

- Refresh the browser page
- Check browser permissions (usually top-right in address bar)
- Test microphone in system settings
- Try a different browser (Chrome recommended)
- Check if microphone is the default recording device

#### 3. Speech Recognition Fails

**Problem**: "Could not understand audio" error

**Solutions**:

- Speak louder and more clearly
- Move closer to microphone
- Reduce background noise
- Check internet connection (Google STT requires internet)
- Try recording a longer answer (at least 5 seconds)

#### 4. Slow Performance

**Problem**: Application is slow or unresponsive

**Solutions**:

- Close other applications
- Restart the Streamlit server
- Clear browser cache
- Reduce number of questions per session
- Use simpler version: `streamlit run app.py`

#### 5. Model Download Fails

**Problem**: sentence-transformers model won't download

**Solutions**:

```powershell
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# If still fails, disable advanced features:
# Edit app_enhanced.py, find:
# SENTENCE_TRANSFORMERS_AVAILABLE = True
# Change to:
# SENTENCE_TRANSFORMERS_AVAILABLE = False
```

#### 6. PDF Generation Fails

**Problem**: "PDF generation failed" error

**Solutions**:

```powershell
# Install/reinstall fpdf
pip install --upgrade fpdf

# If still fails, use text report instead
# (application will automatically fallback)
```

#### 7. Port Already in Use

**Problem**: "Address already in use" error

**Solutions**:

```powershell
# Option 1: Use different port
streamlit run app_enhanced.py --server.port 8502

# Option 2: Find and kill process using port 8501
netstat -ano | findstr :8501
# Note the PID (last column)
taskkill /PID <PID> /F
```

---

## Advanced Configuration

### Customizing Questions

Edit `config/questions.json`:

```json
{
  "Technical": {
    "Beginner": [
      {
        "question": "Your custom question here?",
        "keywords": ["keyword1", "keyword2"],
        "expected_duration": 60,
        "technical_concepts": ["concept1"]
      }
    ]
  }
}
```

### Adjusting Scoring Weights

Edit `config/settings.json`:

```json
{
  "scoring_weights": {
    "Technical": {
      "technical": 0.5, // Increase technical weight
      "communication": 0.2,
      "sentiment": 0.15,
      "completeness": 0.15
    }
  }
}
```

### Changing Speech Settings

Edit `config/settings.json`:

```json
{
  "speech_recognition": {
    "energy_threshold": 300, // Microphone sensitivity
    "pause_threshold": 0.8, // Pause detection (seconds)
    "dynamic_energy": true // Auto-adjust to environment
  }
}
```

---

## Testing Your Installation

Run the test script:

```powershell
python test_setup.py
```

This will verify:

- ✓ All dependencies installed
- ✓ Custom modules working
- ✓ Configuration files valid
- ✓ NLP models loaded
- ✓ Database functional

---

## Performance Tips

### For Best Experience:

1. **Use Chrome or Edge** (best Streamlit support)
2. **Close unnecessary tabs** (reduce memory usage)
3. **Use good quality microphone** (better recognition)
4. **Minimize background noise** (clearer audio)
5. **Speak at normal pace** (130-150 WPM ideal)
6. **Practice regularly** (consistency is key)

### For Slower Systems:

1. **Reduce questions** (try 3 instead of 5)
2. **Use basic version** (`streamlit run app.py`)
3. **Disable video** (don't click camera button)
4. **Skip advanced NLP** (don't install sentence-transformers)

---

## Getting Help

### Resources

- **Quick Start**: See `QUICKSTART.md`
- **Full Documentation**: See `README.md`
- **Test Installation**: Run `python test_setup.py`

### Self-Help Steps

1. Check this troubleshooting guide
2. Run test script to identify issues
3. Review error messages carefully
4. Check system requirements
5. Try minimal installation

---

## Next Steps

After successful installation:

1. ✅ Run test script: `python test_setup.py`
2. ✅ Start application: `streamlit run app_enhanced.py`
3. ✅ Complete QUICKSTART guide
4. ✅ Do your first practice interview
5. ✅ Review feedback and improve
6. ✅ Practice regularly for best results

---

**Ready to start? Run the application and ace your interviews! 🚀**

```powershell
streamlit run app_enhanced.py
```

Good luck! 🎯
