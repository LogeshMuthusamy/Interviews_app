# Quick Start Guide - AI Virtual Interview Coach

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies

Open PowerShell in the project directory and run:

```powershell
# Install essential packages (fast installation)
pip install streamlit SpeechRecognition gTTS textblob fpdf

# Download TextBlob data
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### 2. Run the Application

```powershell
streamlit run app_enhanced.py
```

The browser will automatically open to `http://localhost:8501`

### 3. Start Your First Interview

1. **Enter your name** in the sidebar
2. **Select mode**: Choose "HR" for your first try
3. **Select difficulty**: Start with "Beginner"
4. **Number of questions**: Start with 3 questions
5. **Click "🚀 Start Interview"**

### 4. Answer Questions

1. Read the question displayed on screen
2. Click the **microphone button** 🎤
3. **Speak your answer clearly** (30-60 seconds)
4. Stop recording when done
5. View instant feedback!

### 5. Complete and Download Report

- Answer all questions
- View your final scores
- Click "Generate PDF Report" to download

---

## ⚡ Quick Tips

### For Best Results:

✅ Use a good quality microphone  
✅ Speak clearly and at normal pace  
✅ Keep background noise minimal  
✅ Take 2-3 seconds to think before answering  
✅ Answer in 30-90 seconds per question

### What to Avoid:

❌ Speaking too fast or too slow  
❌ Using excessive filler words (um, uh, like)  
❌ Very short answers (< 20 words)  
❌ Going off-topic

---

## 🎯 Scoring Guide

| Score  | Grade | Meaning                               |
| ------ | ----- | ------------------------------------- |
| 90-100 | A     | Excellent - Interview ready!          |
| 80-89  | B     | Very Good - Minor improvements needed |
| 70-79  | C     | Good - Practice key areas             |
| 60-69  | D     | Satisfactory - More practice needed   |
| < 60   | F     | Needs Improvement - Keep practicing   |

---

## 🔧 Troubleshooting

### Microphone not working?

1. Refresh the browser page
2. Allow microphone permissions when prompted
3. Check if microphone is working in other apps

### Speech not recognized?

1. Speak louder and clearer
2. Reduce background noise
3. Move closer to microphone
4. Check internet connection (required for Google STT)

### Application won't start?

```powershell
# Reinstall Streamlit
pip install --upgrade streamlit

# Clear Streamlit cache
streamlit cache clear
```

---

## 📚 Practice Schedule

### Week 1: Basics

- Do 3-5 HR Beginner questions daily
- Focus on clear communication
- Review feedback after each session

### Week 2: Technical

- Add 3 Technical Beginner questions daily
- Practice explaining concepts clearly
- Work on reducing filler words

### Week 3: Advanced

- Mix HR and Technical questions
- Increase to Intermediate difficulty
- Focus on completeness and depth

### Week 4: Mock Interviews

- Do full 10-question sessions
- Practice Advanced level
- Aim for 80+ overall score

---

## 🎓 Interview Tips

### Structure Your Answers

**For HR Questions:**

1. **Situation**: Describe the context
2. **Task**: Explain your role
3. **Action**: Detail what you did
4. **Result**: Share the outcome

**For Technical Questions:**

1. **Define**: What is it?
2. **Explain**: How does it work?
3. **Example**: Provide a use case
4. **Advantage**: Why is it useful?

### Improve Communication

- **Pause before answering** (2-3 seconds to organize thoughts)
- **Speak in complete sentences**
- **Use transition words** (however, therefore, additionally)
- **Provide examples** when possible
- **End with a summary** for complex answers

### Boost Your Score

- **Technical Accuracy**: Use correct terminology and concepts
- **Communication**: Vary your vocabulary, avoid repetition
- **Confidence**: Use assertive language ("I believe", "In my experience")
- **Completeness**: Answer all parts of the question

---

## 📊 Advanced Features

### Custom Questions

Edit `config/questions.json` to add your own questions

### Export Data

Download reports in PDF, Text, or JSON format for analysis

### Track Progress

Review past sessions in the database at `data/interview_sessions.json`

### Multiple Sessions

Create different profiles by changing your name in the sidebar

---

## 🎯 Next Steps

1. ✅ Complete your first practice session
2. 📊 Review your detailed feedback
3. 📝 Note areas for improvement
4. 🔄 Practice consistently (daily recommended)
5. 📈 Track your score improvements over time
6. 🎯 Aim for 85+ before real interviews

---

**Ready to ace your interviews? Let's get started! 🚀**

For detailed documentation, see [README.md](README.md)
