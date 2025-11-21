"""
Speech-to-Text Module
Handles audio transcription using OpenAI Whisper and Google Speech Recognition
"""

import speech_recognition as sr
import io
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STTEngine:
    """Advanced Speech-to-Text engine with multiple backend support"""
    
    def __init__(self, engine: str = "google"):
        """
        Initialize STT Engine
        
        Args:
            engine: "google", "whisper", or "sphinx" (offline)
        """
        self.engine = engine
        self.recognizer = sr.Recognizer()
        
        # Configure recognizer for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
    def transcribe_audio(self, audio_file) -> Dict[str, any]:
        """
        Transcribe audio file to text with confidence scoring
        
        Args:
            audio_file: Audio file object (WAV format)
            
        Returns:
            Dict containing:
                - text: Transcribed text
                - confidence: Confidence score (0-1)
                - duration: Audio duration in seconds
                - words_per_minute: Speaking rate
                - filler_words: Count of filler words
                - pauses: Number of detected pauses
        """
        try:
            # Read audio file
            audio_data = None
            duration = 0
            
            if hasattr(audio_file, 'read'):
                audio_bytes = audio_file.read()
                audio_file_obj = io.BytesIO(audio_bytes)
                
                with sr.AudioFile(audio_file_obj) as source:
                    # Record audio with noise adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = self.recognizer.record(source)
                    duration = source.DURATION if hasattr(source, 'DURATION') else 0
            
            if audio_data is None:
                return self._empty_result("Could not read audio file")
            
            # Transcribe using selected engine
            text, confidence = self._transcribe_with_engine(audio_data)
            
            if not text:
                return self._empty_result("No speech detected")
            
            # Analyze speech patterns
            analysis = self._analyze_speech(text, duration)
            
            return {
                'success': True,
                'text': text,
                'confidence': confidence,
                'duration': duration,
                'words_per_minute': analysis['wpm'],
                'filler_words': analysis['filler_count'],
                'filler_word_list': analysis['filler_list'],
                'pauses': analysis['pause_count'],
                'word_count': analysis['word_count'],
                'clarity_score': self._calculate_clarity_score(text, analysis)
            }
            
        except sr.UnknownValueError:
            return self._empty_result("Speech was unclear or unintelligible")
        except sr.RequestError as e:
            return self._empty_result(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            logger.error(f"STT Error: {str(e)}")
            return self._empty_result(f"Transcription error: {str(e)}")
    
    def _transcribe_with_engine(self, audio_data) -> Tuple[str, float]:
        """Transcribe using the selected engine"""
        text = ""
        confidence = 0.0
        
        if self.engine == "google":
            try:
                # Google Speech Recognition with language support
                result = self.recognizer.recognize_google(
                    audio_data,
                    language="en-US",
                    show_all=True
                )
                
                if result and 'alternative' in result:
                    text = result['alternative'][0]['transcript']
                    confidence = result['alternative'][0].get('confidence', 0.8)
                else:
                    text = self.recognizer.recognize_google(audio_data)
                    confidence = 0.7  # Default confidence
                    
            except Exception as e:
                logger.warning(f"Google STT failed: {e}, trying basic recognition")
                text = self.recognizer.recognize_google(audio_data)
                confidence = 0.7
        
        elif self.engine == "sphinx":
            # Offline recognition (CMU Sphinx)
            text = self.recognizer.recognize_sphinx(audio_data)
            confidence = 0.6  # Sphinx doesn't provide confidence scores
        
        return text, confidence
    
    def _analyze_speech(self, text: str, duration: float) -> Dict:
        """Analyze speech patterns for communication metrics"""
        
        # Common filler words in English
        filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 
                       'literally', 'so', 'well', 'right', 'okay', 'yeah', 'hmm']
        
        words = text.lower().split()
        word_count = len(words)
        
        # Count filler words
        filler_count = 0
        found_fillers = []
        for filler in filler_words:
            count = text.lower().count(filler)
            if count > 0:
                filler_count += count
                found_fillers.append(f"{filler}({count})")
        
        # Calculate words per minute
        wpm = (word_count / duration * 60) if duration > 0 else 0
        
        # Estimate pauses (simplified - based on sentence structure)
        pause_indicators = ['. ', ', ', '? ', '! ']
        pause_count = sum(text.count(indicator) for indicator in pause_indicators)
        
        return {
            'word_count': word_count,
            'wpm': round(wpm, 1),
            'filler_count': filler_count,
            'filler_list': found_fillers,
            'pause_count': pause_count
        }
    
    def _calculate_clarity_score(self, text: str, analysis: Dict) -> float:
        """
        Calculate speech clarity score based on multiple factors
        
        Returns:
            Score from 0-100
        """
        score = 100.0
        
        # Penalize excessive filler words (max -30 points)
        filler_ratio = analysis['filler_count'] / max(analysis['word_count'], 1)
        score -= min(filler_ratio * 100, 30)
        
        # Penalize too fast or too slow speech (max -20 points)
        wpm = analysis['wpm']
        if wpm < 100 or wpm > 180:
            deviation = abs(140 - wpm)  # 140 is ideal WPM
            score -= min(deviation / 4, 20)
        
        # Bonus for appropriate pause usage (up to +10 points)
        pause_ratio = analysis['pause_count'] / max(analysis['word_count'] / 20, 1)
        if 0.5 <= pause_ratio <= 2.0:
            score += 10
        
        return max(0, min(100, score))
    
    def _empty_result(self, error_message: str) -> Dict:
        """Return empty result with error message"""
        return {
            'success': False,
            'text': '',
            'error': error_message,
            'confidence': 0.0,
            'duration': 0,
            'words_per_minute': 0,
            'filler_words': 0,
            'filler_word_list': [],
            'pauses': 0,
            'word_count': 0,
            'clarity_score': 0
        }


# Utility function for easy import
def transcribe_audio(audio_file, engine: str = "google") -> Dict:
    """
    Convenience function for transcribing audio
    
    Args:
        audio_file: Audio file object
        engine: STT engine to use
        
    Returns:
        Transcription results dictionary
    """
    stt_engine = STTEngine(engine=engine)
    return stt_engine.transcribe_audio(audio_file)
