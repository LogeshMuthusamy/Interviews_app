"""
Modules Package
AI-Powered Virtual Interview Practice Application
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .stt_engine import transcribe_audio, STTEngine
from .nlp_evaluator import evaluate_answer, NLPEvaluator
from .tts_engine import text_to_speech, TTSEngine, generate_feedback_speech
from .database import get_database, InterviewDatabase
from .report_generator import generate_report, InterviewReportGenerator
from .interview_flow import create_flow_manager, InterviewFlowManager

__all__ = [
    'STTEngine',
    'transcribe_audio',
    'NLPEvaluator',
    'evaluate_answer',
    'TTSEngine',
    'text_to_speech',
    'generate_feedback_speech',
    'InterviewDatabase',
    'get_database',
    'InterviewReportGenerator',
    'generate_report',
    'InterviewFlowManager',
    'create_flow_manager'
]
