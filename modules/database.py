"""
Database Module
Handles storage and retrieval of interview sessions and analytics
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    logger.warning("pymongo not available. Using JSON storage.")


class InterviewDatabase:
    """Hybrid database supporting both JSON files and MongoDB"""
    
    def __init__(self, db_path: str = "data/interview_sessions.json", users_path: str = "data/users.json", meetings_path: str = "data/meetings.json", mongo_uri: str = None):
        """
        Initialize database
        
        Args:
            db_path: Path to JSON database file
            users_path: Path to JSON users file
            meetings_path: Path to JSON meetings file
            mongo_uri: MongoDB connection string (optional)
        """
        self.use_mongo = False
        self.mongo_client = None
        self.db = None
        
        # Try connecting to MongoDB if URI provided and driver available
        if mongo_uri and MONGO_AVAILABLE:
            try:
                self.mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
                self.mongo_client.server_info() # Trigger connection check
                self.db = self.mongo_client['ai_interview_coach']
                self.use_mongo = True
                logger.info("Connected to MongoDB successfully")
            except (ConnectionFailure, Exception) as e:
                logger.warning(f"MongoDB connection failed: {e}. Falling back to JSON storage.")
                self.use_mongo = False

        self.db_path = db_path
        self.users_path = users_path
        self.meetings_path = meetings_path
        self.sessions = []
        self.users = {}
        self.meetings = {}
        
        if not self.use_mongo:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            # Load existing data
            self._load_database()
            self._load_users()
            self._load_meetings()
    
    def _ensure_data_directory(self, path):
        """Ensure data directory exists and is writable"""
        try:
            dir_path = os.path.dirname(os.path.abspath(path))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created data directory: {dir_path}")
            # Test write permissions
            test_file = os.path.join(dir_path, '.permission_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return True
        except (OSError, IOError) as e:
            logger.error(f"Permission error accessing {dir_path}: {e}")
            return False

    def _load_users(self):
        """Load users from file or MongoDB"""
        if self.use_mongo:
            return  # No need to preload for Mongo
            
        try:
            if os.path.exists(self.users_path):
                with open(self.users_path, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                logger.info(f"Loaded {len(self.users)} users from database")
            else:
                # Ensure directory exists before trying to create file
                if self._ensure_data_directory(self.users_path):
                    self.users = {}
                    # Create empty users file
                    with open(self.users_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                else:
                    logger.error("Failed to initialize users database: No write permissions")
                    self.users = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing users file: {e}. Initializing new users database.")
            self.users = {}
        except Exception as e:
            logger.error(f"Unexpected error loading users: {e}")
            self.users = {}

    def _save_users(self):
        """Save users to file (No-op for Mongo)"""
        if self.use_mongo:
            return

        try:
            if not self._ensure_data_directory(self.users_path):
                logger.error("Cannot save users: No write permissions to data directory")
                return False
                
            # Write to temporary file first, then rename for atomicity
            temp_path = f"{self.users_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2)
            
            # On Windows, need to remove destination first if it exists
            if os.path.exists(self.users_path):
                os.replace(temp_path, self.users_path)
            else:
                os.rename(temp_path, self.users_path)
                
            return True
        except Exception as e:
            logger.error(f"Failed to save users: {e}")
            # Try to clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

    def _load_meetings(self):
        """Load meetings from file or MongoDB"""
        if self.use_mongo:
            return
            
        try:
            if os.path.exists(self.meetings_path):
                with open(self.meetings_path, 'r', encoding='utf-8') as f:
                    self.meetings = json.load(f)
                logger.info(f"Loaded {len(self.meetings)} meetings from database")
            else:
                if self._ensure_data_directory(self.meetings_path):
                    self.meetings = {}
                    with open(self.meetings_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                else:
                    logger.error("Failed to initialize meetings database")
        except Exception as e:
            logger.error(f"Error loading meetings: {e}")
            self.meetings = {}

    def _save_meetings(self):
        """Save meetings to file"""
        if self.use_mongo:
            return

        try:
            temp_path = f"{self.meetings_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.meetings, f, indent=2)
            
            if os.path.exists(self.meetings_path):
                os.replace(temp_path, self.meetings_path)
            else:
                os.rename(temp_path, self.meetings_path)
            return True
        except Exception as e:
            logger.error(f"Failed to save meetings: {e}")
            return False

    def register_user(self, username, password, full_name="", role="student", email=""):
        """Register a new user"""
        # Basic hash
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user_data = {
            "username": username,
            "password": hashed_pw,
            "full_name": full_name,
            "role": role,
            "email": email,
            "created_at": datetime.now().isoformat()
        }

        if self.use_mongo:
            if self.db.users.find_one({"username": username}):
                return False, "Username already exists"
            self.db.users.insert_one(user_data)
            return True, "Registration successful"
        else:
            if username in self.users:
                return False, "Username already exists"
            
            self.users[username] = {
                "password": hashed_pw,
                "full_name": full_name,
                "role": role,
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            self._save_users()
            return True, "Registration successful"

    def create_meeting(self, interviewer_username, meeting_type="async", custom_questions=None):
        """
        Create a new meeting ID
        
        Args:
            interviewer_username: Username of creator
            meeting_type: 'async' or 'live'
            custom_questions: List of dictionaries [{'question': '...', 'expected_answer': '...'}]
        """
        import random
        import string
        
        meeting_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        meeting_data = {
            "created_by": interviewer_username,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "type": meeting_type,
            "participants": [],
            "custom_questions": custom_questions or []
        }
        
        if self.use_mongo:
            self.db.meetings.insert_one({"_id": meeting_id, **meeting_data})
        else:
            self.meetings[meeting_id] = meeting_data
            self._save_meetings()
            
        return meeting_id

    def verify_meeting(self, meeting_id):
        """Verify if a meeting ID exists and is active"""
        if self.use_mongo:
            meeting = self.db.meetings.find_one({"_id": meeting_id})
            return bool(meeting and meeting.get('active', True))
        else:
            meeting = self.meetings.get(meeting_id)
            return bool(meeting and meeting.get('active', True))

    def delete_meeting(self, meeting_id):
        """Permanently delete a meeting"""
        if self.use_mongo:
            self.db.meetings.delete_one({"_id": meeting_id})
            # Optionally also remove associated sessions if desired, but keeping them might be safer for history
            return True
        else:
            if meeting_id in self.meetings:
                del self.meetings[meeting_id]
                self._save_meetings()
                return True
            return False

    def authenticate_user(self, username, password):
        """Authenticate a user"""
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        if self.use_mongo:
            user = self.db.users.find_one({"username": username})
            if user and user["password"] == hashed_pw:
                return True, user
            return False, "Invalid credentials"
        else:
            if username not in self.users:
                return False, "User not found"
            
            if self.users[username]["password"] == hashed_pw:
                # Inject username into result for consistency
                user_obj = self.users[username].copy()
                user_obj['username'] = username
                return True, user_obj
            else:
                return False, "Invalid password"

    def update_user_api_key(self, username, api_key):
        """Update user's API key"""
        if self.use_mongo:
             self.db.users.update_one(
                {"username": username},
                {"$set": {"api_key": api_key}}
            )
             return True
        else:
            if username in self.users:
                self.users[username]["api_key"] = api_key
                self._save_users()
                return True
            return False

    def _load_database(self):
        """Load database from file"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from database")
            else:
                # Ensure directory exists before trying to create file
                if self._ensure_data_directory(self.db_path):
                    self.sessions = []
                    # Create empty sessions file
                    with open(self.db_path, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                else:
                    logger.error("Failed to initialize sessions database: No write permissions")
                    self.sessions = []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing sessions file: {e}. Initializing new sessions database.")
            self.sessions = []
        except Exception as e:
            logger.error(f"Unexpected error loading sessions: {e}")
            self.sessions = []
    
    def _save_database(self):
        """Save database to file"""
        if self.use_mongo:
            return True

        try:
            if not self._ensure_data_directory(self.db_path):
                logger.error("Cannot save sessions: No write permissions to data directory")
                return False
                
            # Write to temporary file first, then rename for atomicity
            temp_path = f"{self.db_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2)
            
            # On Windows, need to remove destination first if it exists
            if os.path.exists(self.db_path):
                os.replace(temp_path, self.db_path)
            else:
                os.rename(temp_path, self.db_path)
                
            return True
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
            # Try to clean up temp file if it exists
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

    def create_session(self, mode: str, difficulty: str, user_name: str = "Anonymous", metadata: Optional[Dict] = None, meeting_id: str = None) -> str:
        """
        Create a new interview session
        
        Args:
            mode: Interview mode (HR/Technical/Mixed)
            difficulty: Difficulty level
            user_name: User's name
            metadata: Additional metadata
            meeting_id: Meeting ID if applicable
            
        Returns:
            Session ID
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(hash(datetime.now()))[-6:]}"
        
        session = {
            'session_id': session_id,
            'user_name': user_name,
            'mode': mode,
            'difficulty': difficulty,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'questions': [],
            'overall_score': 0,
            'status': 'active',
            'metadata': metadata or {},
            'meeting_id': meeting_id,
            'transcript': []
        }
        
        if self.use_mongo:
             self.db.sessions.insert_one(session)
             return session_id

        self.sessions.append(session)
        self._save_database()
        
        return session_id
    
    def add_question_response(self, session_id: str, question_data: Dict):
        """
        Add a question and response to a session
        
        Args:
            session_id: Session identifier
            question_data: Dictionary containing question, answer, and evaluation
        """
        session = self._get_session(session_id)
        if session:
            session['questions'].append({
                'timestamp': datetime.now().isoformat(),
                'question': question_data['question'],
                'answer': question_data['answer'],
                'evaluation': question_data['evaluation'],
                'stt_metrics': question_data.get('stt_metrics', {}),
                'duration': question_data.get('duration', 0)
            })
            self._save_database()
        else:
            logger.warning(f"Session {session_id} not found")

    def update_session_meta(self, session_id: str, new_meta: Dict):
        """Merge new metadata into existing session metadata"""
        session = self._get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found for metadata update")
            return False
        existing = session.get('metadata', {})
        existing.update(new_meta)
        session['metadata'] = existing
        self._save_database()
        return True

    def append_transcript(self, session_id: str, speaker: str, text: str):
        """Append a transcript entry to session metadata for live storage"""
        session = self._get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found for transcript append")
            return False
        meta = session.get('metadata', {})
        transcript = meta.get('transcript', [])
        transcript.append({
            'timestamp': datetime.now().isoformat(),
            'speaker': speaker,
            'text': text
        })
        meta['transcript'] = transcript
        session['metadata'] = meta
        self._save_database()
        return True
    
    def end_session(self, session_id: str):
        """
        Mark session as completed and calculate final score
        
        Args:
            session_id: Session identifier
        """
        session = self._get_session(session_id)
        if session:
            session['end_time'] = datetime.now().isoformat()
            session['status'] = 'completed'
            
            # Calculate overall score
            if session['questions']:
                scores = [q['evaluation']['overall_score'] 
                         for q in session['questions']]
                session['overall_score'] = sum(scores) / len(scores)
            
            self._save_database()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session dictionary or None
        """
        return self._get_session(session_id)
    
    def get_meetings_by_creator(self, username):
        """Get all meetings created by a specific user"""
        if self.use_mongo:
             return list(self.db.meetings.find({"created_by": username}))
        else:
            return {k: v for k, v in self.meetings.items() if v.get('created_by') == username}

    def _get_session(self, session_id: str) -> Optional[Dict]:
        """Internal method to get session"""
        for session in self.sessions:
            if session['session_id'] == session_id:
                return session
        return None
    
    def update_session_status(self, session_id, status, selection_result=None, email_sent=False):
        """Update session final status and emailing"""
        session = self._get_session(session_id)
        if session:
            session['status'] = status # e.g., 'reviewed'
            if selection_result:
                session['human_selection'] = selection_result # 'Selected' or 'Rejected'
            if email_sent:
                session['email_sent'] = True
            
            if self.use_mongo:
                update_fields = {"status": status}
                if selection_result: update_fields["human_selection"] = selection_result
                if email_sent: update_fields["email_sent"] = True
                self.db.sessions.update_one({"session_id": session_id}, {"$set": update_fields})
            else:
                self._save_database()
            return True
        return False
        
    def get_user_sessions(self, user_name: str) -> List[Dict]:
        """Get all sessions for a user"""
        if self.use_mongo:
            return list(self.db.sessions.find({"user_name": user_name}))
        return [s for s in self.sessions if s['user_name'] == user_name]

    def get_sessions_by_meeting(self, meeting_id: str) -> List[Dict]:
        """Get all sessions associated with a meeting ID"""
        if self.use_mongo:
            return list(self.db.sessions.find({"meeting_id": meeting_id}))
        # Filter sessions where meeting_id matches
        return [s for s in self.sessions if s.get('meeting_id') == meeting_id]

    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent sessions
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries
        """
        sorted_sessions = sorted(
            self.sessions,
            key=lambda x: x['start_time'],
            reverse=True
        )
        return sorted_sessions[:limit]
    
    def get_analytics(self, session_id: Optional[str] = None) -> Dict:
        """
        Get analytics for a session or all sessions
        
        Args:
            session_id: Optional session ID for specific analytics
            
        Returns:
            Analytics dictionary
        """
        if session_id:
            session = self._get_session(session_id)
            if not session:
                return {}
            return self._calculate_session_analytics(session)
        else:
            return self._calculate_overall_analytics()
    
    def _calculate_session_analytics(self, session: Dict) -> Dict:
        """Calculate analytics for a single session"""
        if not session['questions']:
            return {
                'total_questions': 0,
                'average_score': 0,
                'skill_breakdown': {
                    'technical_accuracy': 0,
                    'communication_skills': 0,
                    'sentiment_tone': 0,
                    'completeness': 0
                },
                'duration_minutes': 0,
                'questions_passed': 0,
                'questions_failed': 0
            }
        
        questions = session['questions']
        
        # Calculate averages
        technical_scores = []
        communication_scores = []
        sentiment_scores = []
        completeness_scores = []
        
        for q in questions:
            eval_data = q.get('evaluation', {})
            technical_scores.append(eval_data.get('technical_accuracy', 0))
            communication_scores.append(eval_data.get('communication_skills', 0))
            sentiment_scores.append(eval_data.get('sentiment_tone', 0))
            completeness_scores.append(eval_data.get('completeness', 0))
        
        # Avoid division by zero
        count = len(questions) or 1
        
        return {
            'total_questions': len(questions),
            'average_score': session.get('overall_score', 0),
            'skill_breakdown': {
                'technical_accuracy': sum(technical_scores) / count,
                'communication_skills': sum(communication_scores) / count,
                'sentiment_tone': sum(sentiment_scores) / count,
                'completeness': sum(completeness_scores) / count
            },
            'duration_minutes': self._calculate_duration(session),
            'questions_passed': sum(1 for q in questions 
                                   if q['evaluation']['overall_score'] >= 60),
            'questions_failed': sum(1 for q in questions 
                                   if q['evaluation']['overall_score'] < 60)
        }
    
    def _calculate_overall_analytics(self) -> Dict:
        """Calculate analytics across all sessions"""
        if self.use_mongo:
            total_sessions = self.db.sessions.count_documents({})
            completed_sessions = list(self.db.sessions.find({'status': 'completed'}))
        else:
            if not self.sessions:
                return {'total_sessions': 0}
            total_sessions = len(self.sessions)
            completed_sessions = [s for s in self.sessions if s['status'] == 'completed']
        
        if not completed_sessions:
            return {'total_sessions': total_sessions, 'completed_sessions': 0}
        
        total_questions = sum(len(s['questions']) for s in completed_sessions)
        avg_score = sum(s['overall_score'] for s in completed_sessions) / len(completed_sessions)
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': len(completed_sessions),
            'total_questions_answered': total_questions,
            'overall_average_score': avg_score,
            'mode_distribution': self._get_mode_distribution(),
            'difficulty_distribution': self._get_difficulty_distribution()
        }
    
    def _get_mode_distribution(self) -> Dict:
        """Get distribution of interview modes"""
        if self.use_mongo:
            pipeline = [{"$group": {"_id": "$mode", "count": {"$sum": 1}}}]
            return {doc["_id"]: doc["count"] for doc in self.db.sessions.aggregate(pipeline)}
            
        modes = {}
        for session in self.sessions:
            mode = session['mode']
            modes[mode] = modes.get(mode, 0) + 1
        return modes
    
    def _get_difficulty_distribution(self) -> Dict:
        """Get distribution of difficulty levels"""
        if self.use_mongo:
            pipeline = [{"$group": {"_id": "$difficulty", "count": {"$sum": 1}}}]
            return {doc["_id"]: doc["count"] for doc in self.db.sessions.aggregate(pipeline)}

        difficulties = {}
        for session in self.sessions:
            diff = session['difficulty']
            difficulties[diff] = difficulties.get(diff, 0) + 1
        return difficulties
    
    def _calculate_duration(self, session: Dict) -> float:
        """Calculate session duration in minutes"""
        if not session['end_time']:
            return 0
        
        try:
            start = datetime.fromisoformat(session['start_time'])
            end = datetime.fromisoformat(session['end_time'])
            duration = (end - start).total_seconds() / 60
            return round(duration, 1)
        except Exception:
            return 0


# Singleton instance
_db_instance = None

def get_database() -> InterviewDatabase:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = InterviewDatabase()
    return _db_instance
