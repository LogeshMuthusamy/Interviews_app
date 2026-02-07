"""
Interview Flow Manager
Manages question selection, follow-up generation, and interview progression
"""

import json
import random
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional: Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class InterviewFlowManager:
    """Manages the flow of interview questions and follow-ups"""
    
    def __init__(self, questions_path: str = "config/questions.json"):
        """
        Initialize the flow manager
        
        Args:
            questions_path: Path to questions JSON file
        """
        self.questions_path = questions_path
        self.questions_bank = {}
        self.current_session = None
        self.api_key = None
        self.llm_model = None
        self.load_questions()
    
    def configure_llm(self, api_key: str):
        """Configure LLM for dynamic generation"""
        if api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                self.llm_model = genai.GenerativeModel('gemini-pro')
                self.api_key = api_key
                logger.info("Questions LLM Configured")
            except Exception as e:
                logger.error(f"Failed to config LLM: {e}")

    def load_questions(self):
        """Load questions from JSON file"""
        try:
            with open(self.questions_path, 'r', encoding='utf-8') as f:
                self.questions_bank = json.load(f)
            logger.info("Questions loaded successfully")
        except FileNotFoundError:
            logger.error(f"Questions file not found: {self.questions_path}")
            self.questions_bank = self._get_default_questions()
        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            self.questions_bank = self._get_default_questions()
    
    def start_session(self, mode: str, difficulty: str, 
                     num_questions: int = 5, target_keywords: Optional[List[str]] = None,
                     resume_text: str = "", job_description: str = "",
                     custom_questions_list: Optional[List[Dict]] = None,
                     api_key: str = None) -> Dict:
        """
        Start a new interview session
        
        Args:
            mode: Interview mode (HR/Technical/Mixed)
            difficulty: Difficulty level
            num_questions: Number of questions for the session
            target_keywords: Keywords extracted from resume/job description
            resume_text: Full resume text for generating custom questions
            job_description: Full job description for generating custom questions
            custom_questions_list: hardcoded list of questions provided by interviewer
            api_key: Optional Gemini API Key
            
        Returns:
            Session configuration dictionary
        """
        # Configure LLM if key provided
        if api_key:
            self.configure_llm(api_key)

        # 1. If explicit custom questions are provided (from Interviewer), use them exclusively or prioritize them
        if custom_questions_list:
            available = custom_questions_list
            num_questions = len(custom_questions_list) # Override count
            logger.info(f"Using {len(custom_questions_list)} forced custom questions from interviewer")
        else:
            # 2. Dynamic Generation (LLM or Template)
            available = []
            
            # Try LLM Generation first if available
            if self.llm_model and (resume_text or job_description):
                try:
                    logger.info("Attempting LLM question generation...")
                    available = self._generate_questions_with_llm(
                        resume_text, job_description, mode, difficulty, num_questions
                    )
                except Exception as e:
                    logger.error(f"LLM Generation failed: {e}")
                    available = [] # Fallback
            
            # Fallback to standard logic if LLM failed or not available
            if not available:
                available = self._get_questions_for_session(mode, difficulty)
                
                # Generate custom questions based on resume content (Template based)
                custom_generated = []
                if resume_text or job_description:
                    custom_generated = self._generate_resume_based_questions(
                        resume_text, job_description, mode, difficulty, target_keywords or []
                    )
                
                # Combine custom and default questions
                if custom_generated:
                    available = custom_generated + available
                
                # Sort/Prioritize
                if target_keywords:
                    keyword_set = set(kw.lower() for kw in target_keywords if kw)
                    def score_question(q):
                        qk = [k.lower() for k in q.get('keywords', [])]
                        return len(keyword_set.intersection(qk))
                    available = sorted(available, key=lambda q: (score_question(q), random.random()), reverse=True)

        self.current_session = {
            'mode': mode,
            'difficulty': difficulty,
            'num_questions': num_questions,
            'current_index': 0,
            'questions_asked': [],
            'available_questions': available,
            'follow_up_needed': False,
            'last_answer': None # Track for follow-ups
        }
        
        return self.current_session
    
    def get_next_question(self) -> Optional[Dict]:
        """
        Get the next question in the interview
        
        Returns:
            Question dictionary or None if session is complete
        """
        if not self.current_session:
            logger.error("No active session")
            return None
        
        # Check if we need a follow-up question
        if self.current_session['follow_up_needed']:
            follow_up = self._generate_follow_up()
            if follow_up:
                self.current_session['follow_up_needed'] = False
                return follow_up
        
        # Check if session is complete
        if self.current_session['current_index'] >= self.current_session['num_questions']:
            return None
        
        # Get next question from available pool
        available = self.current_session['available_questions']
        if not available:
            # Recycle questions if we ran out but still need more
            logger.info("Recycling questions pool")
            self.current_session['available_questions'] = self._get_questions_for_session(
                self.current_session['mode'], 
                self.current_session['difficulty']
            )
            available = self.current_session['available_questions']
            
            # If still empty (e.g. no questions at all), then stop
            if not available:
                logger.warning("No questions available even after reload")
                return None
        
        # Select a question (random to avoid repetition)
        question = random.choice(available)
        available.remove(question)
        
        self.current_session['questions_asked'].append(question)
        self.current_session['current_index'] += 1
        
        return question
    
    def should_ask_follow_up(self, evaluation: Dict) -> bool:
        """
        Determine if a follow-up question is needed based on evaluation
        
        Args:
            evaluation: Evaluation results from NLP evaluator
            
        Returns:
            True if follow-up is recommended
        """
        # Follow-up if score is borderline or specific issues detected
        score = evaluation['overall_score']
        
        # Low completeness suggests need for clarification
        if evaluation['completeness'] < 60:
            self.current_session['follow_up_needed'] = True
            self.current_session['follow_up_reason'] = 'incomplete'
            return True
        
        # Very short answer
        if score < 50:
            self.current_session['follow_up_needed'] = True
            self.current_session['follow_up_reason'] = 'too_short'
            return True
        
        return False
    
    def _generate_questions_with_llm(self, resume: str, jd: str, mode: str, difficulty: str, count: int) -> List[Dict]:
        """Generate tailored questions using Gemini"""
        prompt = f"""
        Act as an expert {mode} interviewer.
        Generate {count} unique, challenging interview questions for a {difficulty} level candidate based on the following context.
        
        Resume Summary: {resume[:2000]}...
        Job Description: {jd[:1000]}...
        
        Return the output as a strictly valid JSON list of objects.
        Each object must have these keys: "question", "keywords" (list of strings), "expected_duration" (int seconds), "ideal_answer" (brief string).
        
        Example: [{{ "question": "...", "keywords": ["..."], "expected_duration": 60, "ideal_answer": "..." }}]
        Do not use markdown formatting.
        """
        
        response = self.llm_model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        questions = json.loads(text)
        
        # Tag them
        for q in questions:
            q['custom_generated'] = True
            
        return questions

    def _generate_follow_up(self) -> Optional[Dict]:
        """Generate a contextual follow-up question"""
        if not self.current_session['questions_asked']:
            return None
            
        last_question = self.current_session['questions_asked'][-1]
        
        # Try LLM Follow up
        if self.llm_model and self.current_session.get('last_answer'):
            try:
                prompt = f"""
                The candidate just answered a question.
                Question: "{last_question['question']}"
                Answer: "{self.current_session['last_answer']}"
                
                Generate a short, single sentence follow-up question to dig deeper, clarify, or challenge the candidate.
                Return ONLY the question text.
                """
                response = self.llm_model.generate_content(prompt)
                follow_up_text = response.text.strip()
                
                return {
                    'question': follow_up_text,
                    'keywords': last_question.get('keywords', []),
                    'expected_duration': 60,
                    'is_follow_up': True,
                    'original_question': last_question['question']
                }
            except Exception as e:
                logger.error(f"LLM Followup failed: {e}")
        
        # Fallback to Template
        reason = self.current_session.get('follow_up_reason', 'generic')
        
        # Follow-up templates based on reason
        follow_ups = {
            'incomplete': [
                "Can you elaborate more on that?",
                "Could you provide more details about your answer?",
                "Can you give a specific example to illustrate your point?"
            ],
            'too_short': [
                "That's interesting. Can you explain further?",
                "Could you expand on that idea?",
                "What else can you tell me about this?"
            ],
            'vague': [
                "Can you be more specific?",
                "Could you give a concrete example?",
                "What exactly do you mean by that?"
            ],
            'no_example': [
                "Can you provide a specific example from your experience?",
                "Could you share a real situation where this happened?",
                "Walk me through a specific instance."
            ]
        }
        
        templates = follow_ups.get(reason, follow_ups['incomplete'])
        follow_up_text = random.choice(templates)
        
        return {
            'question': follow_up_text,
            'keywords': last_question['keywords'],
            'expected_duration': 60,
            'is_follow_up': True,
            'original_question': last_question['question']
        }
    
    def _get_questions_for_session(self, mode: str, difficulty: str) -> List[Dict]:
        """Get appropriate questions for the session"""
        try:
            questions = self.questions_bank.get(mode, {}).get(difficulty, [])
            # Make a copy so we don't modify original
            return [q.copy() for q in questions]
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            return []
    
    def _generate_resume_based_questions(self, resume_text: str, job_description: str, 
                                        mode: str, difficulty: str, keywords: List[str]) -> List[Dict]:
        """
        Generate custom interview questions based on resume and job description content
        
        Args:
            resume_text: Candidate's resume text
            job_description: Job description text
            mode: Interview mode
            difficulty: Difficulty level
            keywords: Extracted keywords
            
        Returns:
            List of custom questions
        """
        custom_questions = []
        
        try:
            import re
            
            # Extract skills/technologies from resume
            tech_patterns = [
                r'\b(python|java|javascript|react|angular|node|sql|mongodb|aws|azure|docker|kubernetes)\b',
                r'\b(machine learning|ai|data science|frontend|backend|full stack|devops)\b',
                r'\b(agile|scrum|jira|git|ci/cd|microservices|api)\b'
            ]
            
            found_skills = set()
            combined_text = (resume_text + " " + job_description).lower()
            for pattern in tech_patterns:
                matches = re.findall(pattern, combined_text, re.IGNORECASE)
                found_skills.update(matches)
            
            # Generate questions based on found skills
            if found_skills and mode in ["Technical", "Mixed"]:
                skill_list = list(found_skills)[:5]  # Limit to 5 skills
                
                for skill in skill_list:
                    if difficulty == "Beginner":
                        custom_questions.append({
                            "question": f"Can you explain your experience with {skill.title()}?",
                            "keywords": [skill.lower(), "experience", "knowledge", "use"],
                            "expected_duration": 90,
                            "follow_up_triggers": ["vague"],
                            "custom_generated": True
                        })
                    elif difficulty == "Intermediate":
                        custom_questions.append({
                            "question": f"Tell me about a specific project where you used {skill.title()}. What challenges did you face?",
                            "keywords": [skill.lower(), "project", "challenge", "solution", "implementation"],
                            "expected_duration": 120,
                            "follow_up_triggers": ["no_details"],
                            "custom_generated": True
                        })
                    else:  # Advanced
                        custom_questions.append({
                            "question": f"How would you architect a scalable solution using {skill.title()}? What trade-offs would you consider?",
                            "keywords": [skill.lower(), "architecture", "scalability", "trade-off", "design"],
                            "expected_duration": 150,
                            "follow_up_triggers": ["theoretical"],
                            "custom_generated": True
                        })
            
            # Extract company names from resume for behavioral questions
            if mode in ["HR", "Behavioral", "Mixed"]:
                company_pattern = r'(?:at|with|for)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)'
                companies = re.findall(company_pattern, resume_text)
                
                if companies:
                    company = companies[0]
                    custom_questions.append({
                        "question": f"Tell me about your experience working at {company}. What was your biggest achievement there?",
                        "keywords": ["experience", "achievement", "responsibility", "contribution", "impact"],
                        "expected_duration": 120,
                        "follow_up_triggers": ["generic"],
                        "custom_generated": True
                    })
            
            # Generate questions based on job description requirements
            if job_description:
                jd_lower = job_description.lower()
                
                if "lead" in jd_lower or "manage" in jd_lower:
                    custom_questions.append({
                        "question": "This role involves leadership responsibilities. Can you describe your experience leading teams or projects?",
                        "keywords": ["leadership", "team", "management", "coordination", "mentoring"],
                        "expected_duration": 120,
                        "follow_up_triggers": ["no_example"],
                        "custom_generated": True
                    })
                
                if "collaborate" in jd_lower or "cross-functional" in jd_lower:
                    custom_questions.append({
                        "question": "How do you approach working with cross-functional teams or stakeholders from different departments?",
                        "keywords": ["collaboration", "communication", "stakeholder", "teamwork", "coordination"],
                        "expected_duration": 90,
                        "follow_up_triggers": ["vague"],
                        "custom_generated": True
                    })
            
            logger.info(f"Generated {len(custom_questions)} custom questions")
            
        except Exception as e:
            logger.error(f"Error generating custom questions: {e}")
        
        return custom_questions[:3]  # Limit to 3 custom questions per session
    
    def get_progress(self) -> Dict:
        """
        Get current session progress
        
        Returns:
            Progress dictionary with current state
        """
        if not self.current_session:
            return {'active': False}
        
        return {
            'active': True,
            'current_question': self.current_session['current_index'],
            'total_questions': self.current_session['num_questions'],
            'progress_percentage': (self.current_session['current_index'] / 
                                  self.current_session['num_questions'] * 100),
            'mode': self.current_session['mode'],
            'difficulty': self.current_session['difficulty']
        }
    
    def end_session(self):
        """End the current session"""
        self.current_session = None
    
    def _get_default_questions(self) -> Dict:
        """Provide default questions if file loading fails"""
        return {
            "HR": {
                "Beginner": [
                    {
                        "question": "Tell me about yourself.",
                        "keywords": ["background", "experience", "skills"],
                        "expected_duration": 90
                    },
                    {
                        "question": "What are your strengths?",
                        "keywords": ["strength", "skill", "ability"],
                        "expected_duration": 60
                    }
                ]
            },
            "Technical": {
                "Beginner": [
                    {
                        "question": "What is a variable in programming?",
                        "keywords": ["variable", "data", "storage"],
                        "expected_duration": 60,
                        "technical_concepts": ["programming_basics"]
                    }
                ]
            },
            "Mixed": {
                "Beginner": [
                    {
                        "question": "Tell me about a technical project you've worked on.",
                        "keywords": ["project", "technical", "experience"],
                        "expected_duration": 120
                    }
                ]
            }
        }
    
    def get_all_questions(self, mode: Optional[str] = None, 
                         difficulty: Optional[str] = None) -> List[Dict]:
        """
        Get all questions matching criteria
        
        Args:
            mode: Optional mode filter
            difficulty: Optional difficulty filter
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        modes = [mode] if mode else self.questions_bank.keys()
        
        for m in modes:
            if m in self.questions_bank:
                difficulties = [difficulty] if difficulty else self.questions_bank[m].keys()
                
                for d in difficulties:
                    if d in self.questions_bank[m]:
                        questions.extend(self.questions_bank[m][d])
        
        return questions


# Convenience function
def create_flow_manager(questions_path: str = "config/questions.json") -> InterviewFlowManager:
    """Create a new flow manager instance"""
    return InterviewFlowManager(questions_path)
