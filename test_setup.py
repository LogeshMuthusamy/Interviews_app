"""
Test script to verify installation and functionality
Run this after setup to ensure everything is working
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    tests = {
        "Streamlit": "streamlit",
        "Speech Recognition": "speech_recognition",
        "gTTS": "gtts",
        "TextBlob": "textblob",
        "NumPy": "numpy",
        "Sentence Transformers": "sentence_transformers",
        "Transformers": "transformers",
        "FPDF": "fpdf"
    }
    
    results = {}
    for name, module in tests.items():
        try:
            __import__(module)
            results[name] = "✓ OK"
            print(f"  {name}: ✓")
        except ImportError as e:
            results[name] = f"✗ FAILED: {e}"
            print(f"  {name}: ✗ (Optional)")
    
    return results

def test_modules():
    """Test custom modules"""
    print("\nTesting custom modules...")
    
    try:
        from modules import stt_engine, nlp_evaluator, tts_engine
        from modules import database, report_generator, interview_flow
        print("  All custom modules: ✓")
        return True
    except Exception as e:
        print(f"  Custom modules: ✗ Error: {e}")
        return False

def test_config():
    """Test configuration files"""
    print("\nTesting configuration...")
    
    import json
    
    files_to_check = [
        "config/questions.json",
        "config/settings.json"
    ]
    
    all_ok = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
                print(f"  {file_path}: ✓")
            except Exception as e:
                print(f"  {file_path}: ✗ Invalid JSON: {e}")
                all_ok = False
        else:
            print(f"  {file_path}: ✗ Not found")
            all_ok = False
    
    return all_ok

def test_directories():
    """Test required directories"""
    print("\nTesting directories...")
    
    dirs = ["data", "reports", "config", "modules"]
    all_ok = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  {dir_name}/: ✓")
        else:
            print(f"  {dir_name}/: ✗ Not found")
            all_ok = False
    
    return all_ok

def test_nlp_model():
    """Test NLP model loading"""
    print("\nTesting NLP model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("  Loading model (this may take a moment)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test encoding
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)
        
        print(f"  Model loaded: ✓")
        print(f"  Embedding shape: {embedding.shape}")
        return True
    except Exception as e:
        print(f"  Model test: ✗ Error: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition setup"""
    print("\nTesting speech recognition...")
    
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        print("  Speech recognizer initialized: ✓")
        return True
    except Exception as e:
        print(f"  Speech recognition: ✗ Error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    
    try:
        from modules.database import get_database
        
        db = get_database()
        session_id = db.create_session("HR", "Beginner", "Test User")
        
        # Add test data
        db.add_question_response(session_id, {
            'question': 'Test question?',
            'answer': 'Test answer',
            'evaluation': {
                'overall_score': 75,
                'technical_accuracy': 70,
                'communication_skills': 80,
                'sentiment_tone': 75,
                'completeness': 75,
                'grade': 'C (Good)',
                'pass': True,
                'feedback': {
                    'strengths': ['Clear communication'],
                    'weaknesses': [],
                    'suggestions': [],
                    'missing_technical_points': []
                }
            }
        })
        
        db.end_session(session_id)
        
        # Verify
        session = db.get_session(session_id)
        if session and len(session['questions']) == 1:
            print("  Database operations: ✓")
            return True
        else:
            print("  Database operations: ✗ Data mismatch")
            return False
            
    except Exception as e:
        print(f"  Database test: ✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("AI Virtual Interview Coach - System Test")
    print("="*60)
    print()
    
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['modules'] = test_modules()
    results['config'] = test_config()
    results['directories'] = test_directories()
    results['nlp_model'] = test_nlp_model()
    results['speech_recognition'] = test_speech_recognition()
    results['database'] = test_database()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("✓ All tests passed!")
        print("\nYou're ready to run the application:")
        print("  streamlit run app_enhanced.py")
    else:
        print("⚠ Some tests failed. Check the output above.")
        print("\nYou can still try running the application:")
        print("  streamlit run app_enhanced.py")
        print("\nSome features may not work if dependencies are missing.")
    
    print("\n" + "="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
