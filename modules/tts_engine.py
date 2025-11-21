"""
Text-to-Speech Module
Handles voice synthesis for AI interviewer feedback
"""

import logging
from typing import Optional
import io
import os
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import TTS libraries
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not available")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available")


class TTSEngine:
    """Text-to-Speech engine with multiple backend support"""
    
    def __init__(self, engine: str = "gtts", voice: str = "en", rate: int = 150):
        """
        Initialize TTS Engine
        
        Args:
            engine: "gtts" (Google) or "pyttsx3" (offline)
            voice: Voice language/accent
            rate: Speech rate (words per minute)
        """
        self.engine_type = engine
        self.voice = voice
        self.rate = rate
        self.engine = None
        
        if engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', rate)
                
                # Try to set a pleasant voice
                voices = self.engine.getProperty('voices')
                if voices:
                    # Prefer female voice (often clearer)
                    for v in voices:
                        if 'female' in v.name.lower() or 'zira' in v.name.lower():
                            self.engine.setProperty('voice', v.id)
                            break
                
                logger.info("pyttsx3 engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")
                self.engine = None
    
    def speak_text(self, text: str, save_path: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            save_path: Optional path to save audio file
            
        Returns:
            Audio bytes if successful, None otherwise
        """
        try:
            if self.engine_type == "gtts" and GTTS_AVAILABLE:
                return self._speak_gtts(text, save_path)
            elif self.engine_type == "pyttsx3" and self.engine:
                return self._speak_pyttsx3(text, save_path)
            else:
                logger.warning("No TTS engine available")
                return None
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def _speak_gtts(self, text: str, save_path: Optional[str] = None) -> bytes:
        """Speak using Google TTS"""
        tts = gTTS(text=text, lang='en', slow=False)
        
        if save_path:
            tts.save(save_path)
            with open(save_path, 'rb') as f:
                return f.read()
        else:
            # Save to memory
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            return audio_fp.read()
    
    def _speak_pyttsx3(self, text: str, save_path: Optional[str] = None) -> Optional[bytes]:
        """Speak using pyttsx3 (offline)"""
        if not self.engine:
            return None
        
        if save_path:
            self.engine.save_to_file(text, save_path)
            self.engine.runAndWait()
            
            if os.path.exists(save_path):
                with open(save_path, 'rb') as f:
                    return f.read()
        else:
            # pyttsx3 doesn't support direct memory output easily
            # So we'll use a temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()
            
            try:
                with open(tmp_path, 'rb') as f:
                    audio_bytes = f.read()
                os.unlink(tmp_path)
                return audio_bytes
            except Exception:
                return None
        
        return None
    
    def generate_feedback_speech(self, evaluation: dict, question: str = None) -> str:
        """
        Generate natural-sounding feedback speech from evaluation results
        
        Args:
            evaluation: Evaluation dictionary from NLP evaluator
            question: Optional next question to include
            
        Returns:
            Formatted text suitable for TTS
        """
        score = evaluation['overall_score']
        grade = evaluation['grade']
        
        # Start with score announcement
        feedback_text = f"You scored {score} out of 100, which is a {grade}. "
        
        # Add strengths
        strengths = evaluation['feedback'].get('strengths', [])
        if strengths:
            if len(strengths) == 1:
                feedback_text += f"Your strength was: {strengths[0]}. "
            else:
                feedback_text += "Your strengths were: " + ", and ".join(strengths) + ". "
        
        # Add one key improvement area
        weaknesses = evaluation['feedback'].get('weaknesses', [])
        if weaknesses:
            feedback_text += f"For improvement: {weaknesses[0]}. "
        
        # Add next question if provided
        if question:
            feedback_text += f"Now, here's your next question: {question}"
        
        return feedback_text
    
    def generate_welcome_speech(self, mode: str, difficulty: str) -> str:
        """Generate welcome message"""
        return (f"Welcome to your {difficulty} level {mode} interview practice session. "
                f"I will ask you questions, and you can respond using your microphone. "
                f"Take a deep breath, relax, and let's begin. Good luck!")
    
    def generate_conclusion_speech(self, session_score: float, total_questions: int) -> str:
        """Generate session conclusion message"""
        return (f"Your interview practice session is now complete. "
                f"You answered {total_questions} questions with an average score of {session_score:.1f}. "
                f"Great job! Review your detailed feedback report for specific areas of improvement.")


# Convenience functions
def text_to_speech(text: str, engine: str = "gtts") -> Optional[bytes]:
    """
    Convert text to speech audio
    
    Args:
        text: Text to convert
        engine: TTS engine to use
        
    Returns:
        Audio bytes
    """
    tts_engine = TTSEngine(engine=engine)
    return tts_engine.speak_text(text)


def generate_feedback_speech(evaluation: dict, next_question: str = None) -> str:
    """Generate feedback speech text from evaluation"""
    tts_engine = TTSEngine()
    return tts_engine.generate_feedback_speech(evaluation, next_question)
