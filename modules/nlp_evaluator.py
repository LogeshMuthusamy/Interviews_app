"""
NLP Evaluation Engine
Advanced evaluation system using transformer models for technical accuracy,
communication skills, and sentiment analysis
"""

import re
from typing import Dict, List, Tuple
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import transformer models (will be optional dependencies)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Using fallback evaluation.")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logger.warning("TextBlob not available. Using basic sentiment analysis.")

# Optional: Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class NLPEvaluator:
    """Advanced NLP-based answer evaluation system"""
    
    def __init__(self, api_key: str = None):
        """Initialize NLP models
        Args:
            api_key: Optional Google Gemini API Key for LLM-based evaluation
        """
        self.model = None
        self.api_key = api_key
        self.use_llm = bool(api_key and GEMINI_AVAILABLE)
        
        if self.use_llm:
            try:
                genai.configure(api_key=self.api_key)
                self.llm_model = genai.GenerativeModel('gemini-pro')
                logger.info("Configured Google Gemini LLM")
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")
                self.use_llm = False
        
        if not self.use_llm and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Load a lightweight but effective model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded SentenceTransformer model successfully")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}")
                self.model = None
    
    def evaluate_answer(self, 
                       user_answer: str,
                       question: Dict,
                       interview_mode: str,
                       difficulty: str) -> Dict:
        """
        Comprehensive evaluation of user's answer
        
        Args:
            user_answer: The transcribed answer text
            question: Question dictionary with keywords and metadata
            interview_mode: "HR", "Technical", or "Mixed"
            difficulty: "Beginner", "Intermediate", or "Advanced"
            
        Returns:
            Dictionary with detailed scores and feedback
        """
        # --- LLM PATH ---
        if self.use_llm:
            try:
                return self._evaluate_with_gemini(user_answer, question, interview_mode, difficulty)
            except Exception as e:
                logger.error(f"Gemini evaluation failed, falling back to local: {e}")
                # Fallthrough to local
        
        # --- LOCAL PATH ---
        
        # 1. Technical Accuracy Score (if applicable)
        technical_score = self._evaluate_technical_accuracy(
            user_answer, question, interview_mode
        )
        
        # 2. Communication Skills Score
        communication_score = self._evaluate_communication_skills(user_answer)
        
        # 3. Sentiment & Tone Analysis
        sentiment_score = self._evaluate_sentiment_and_tone(user_answer)
        
        # 4. Completeness & Relevance
        completeness_score = self._evaluate_completeness(user_answer, question)
        
        # 5. Calculate Overall Score
        if interview_mode == "Technical":
            weights = {'technical': 0.40, 'communication': 0.25, 
                      'sentiment': 0.15, 'completeness': 0.20}
        elif interview_mode == "HR":
            weights = {'technical': 0.10, 'communication': 0.35,
                      'sentiment': 0.30, 'completeness': 0.25}
        else:  # Mixed
            weights = {'technical': 0.30, 'communication': 0.30,
                      'sentiment': 0.20, 'completeness': 0.20}
        
        overall_score = (
            technical_score * weights['technical'] +
            communication_score * weights['communication'] +
            sentiment_score * weights['sentiment'] +
            completeness_score * weights['completeness']
        )
        
        # 6. Generate Feedback
        feedback = self._generate_feedback(
            user_answer, question, technical_score, communication_score,
            sentiment_score, completeness_score, interview_mode
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'technical_accuracy': round(technical_score, 1),
            'communication_skills': round(communication_score, 1),
            'sentiment_tone': round(sentiment_score, 1),
            'completeness': round(completeness_score, 1),
            'feedback': feedback,
            'grade': self._get_grade(overall_score),
            'pass': overall_score >= 60
        }

    def _evaluate_with_gemini(self, user_answer: str, question: Dict, mode: str, difficulty: str) -> Dict:
        """Use Google Gemini to evaluate the answer"""
        import json
        
        prompt = f"""
        Act as an expert {mode} interviewer. Evaluate the candidate's answer for a {difficulty} level position.
        
        Question: "{question.get('question')}"
        Expected Keywords/Context: {', '.join(question.get('keywords', []))}
        Ideal Answer (Reference): "{question.get('ideal_answer', 'Not provided')}"
        
        Candidate's Answer: "{user_answer}"
        
        Provide a strictly valid JSON response with the following structure:
        {{
            "technical_accuracy": <0-100 score>,
            "communication_skills": <0-100 score>,
            "sentiment_tone": <0-100 score>,
            "completeness": <0-100 score>,
            "overall_score": <0-100 weighted average>,
            "feedback": {{
                "strengths": ["point 1", "point 2"],
                "weaknesses": ["point 1", "point 2"],
                "suggestions": ["specific improvement tip 1", "tip 2"]
            }}
        }}
        Do not include markdown formatting like ```json ... ```. Just the raw JSON string.
        """
        
        try:
            response = self.llm_model.generate_content(prompt)
            data = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            
            # Ensure proper structure
            data['grade'] = self._get_grade(data['overall_score'])
            data['pass'] = data['overall_score'] >= 60
            return data
        except Exception as e:
            logger.error(f"Gemini parsing error: {e}")
            raise e  # Trigger fallback

    def _evaluate_technical_accuracy(self, answer: str, question: Dict, 
                                    mode: str) -> float:
        """
        Evaluate technical accuracy using keyword matching and semantic similarity
        """
        # Check for very short or non-answers
        answer_lower = answer.lower().strip()
        word_count = len(answer.split())
        
        # Detect non-answers or refusal to answer
        non_answer_phrases = [
            'i don\'t know', 'i dont know', 'not sure', 'no idea',
            'don\'t know', 'dont know', 'i have no idea', 'i am not sure',
            'i\'m not sure', 'no clue', 'cannot answer', 'can\'t answer',
            'don\'t understand', 'dont understand', 'not familiar'
        ]
        
        if any(phrase in answer_lower for phrase in non_answer_phrases):
            return 5.0  # Very low score for admitting ignorance
        
        if word_count < 5:
            return 10.0  # Very low score for too short answers
        
        if mode == "HR":
            # HR questions still need some technical evaluation
            score = 25.0  # Lower baseline for HR
        else:
            score = 15.0  # Lower base score for technical questions
        
        # Check for keywords with partial matching
        keywords = question.get('keywords', [])
        matched_keywords = 0
        partial_matches = 0
        
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in answer_lower:
                matched_keywords += 1
            elif any(word in answer_lower for word in kw_lower.split()):
                partial_matches += 1
        
        if keywords:
            keyword_ratio = matched_keywords / len(keywords)
            partial_ratio = partial_matches / len(keywords)
            score += keyword_ratio * 45  # Up to 45 points for exact keyword matches
            score += partial_ratio * 15  # Up to 15 points for partial matches
            
            # Heavy penalty if no keywords matched at all
            if matched_keywords == 0 and partial_matches == 0:
                score -= 20
        
        # Check for technical concepts (if available)
        technical_concepts = question.get('technical_concepts', [])
        if technical_concepts:
            matched_concepts = 0
            for concept in technical_concepts:
                concept_normalized = concept.replace('_', ' ').lower()
                if concept_normalized in answer_lower:
                    matched_concepts += 1
            
            if technical_concepts:
                concept_ratio = matched_concepts / len(technical_concepts)
                score += concept_ratio * 20  # Up to 20 points for concepts
                
                # Penalty for missing most concepts
                if concept_ratio < 0.3:
                    score -= 10
        
        # Semantic similarity using transformer model (if available)
        if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                question_text = question['question']
                embeddings = self.model.encode([question_text, answer])
                similarity = self._cosine_similarity(embeddings[0], embeddings[1])
                score += similarity * 20  # Up to 20 points for semantic relevance
            except Exception as e:
                logger.warning(f"Semantic similarity failed: {e}")
        
        # Bonus for depth (longer, detailed answers)
        if word_count > 50:
            score += min((word_count - 50) / 10, 10)  # Up to 10 bonus points
        elif word_count < 20:
            score -= 10  # Penalty for too brief
        
        return min(100, max(0, score))
    
    def _evaluate_communication_skills(self, answer: str) -> float:
        """
        Evaluate communication quality: fluency, structure, clarity
        """
        answer_lower = answer.lower().strip()
        words = answer.split()
        word_count = len(words)
        
        # Detect non-answers
        non_answer_phrases = [
            'i don\'t know', 'i dont know', 'not sure', 'no idea',
            'don\'t know', 'dont know', 'i have no idea'
        ]
        
        if any(phrase in answer_lower for phrase in non_answer_phrases):
            return 15.0  # Very low score for non-answers
        
        if word_count < 5:
            return 20.0  # Low score for very short answers
        
        score = 30.0  # Lower baseline
        
        # 1. Length appropriateness
        if 30 <= word_count <= 200:
            score += 20
        elif 20 <= word_count < 30:
            score += 15
        elif 10 <= word_count < 20:
            score += 10
        elif word_count < 10:
            score -= 10
        
        # 2. Sentence structure (check for complete sentences)
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) >= 3:
            score += 15  # Multiple sentences show structure
        elif len(sentences) >= 2:
            score += 10
        else:
            score += 5
        
        # 3. Vocabulary diversity
        unique_words = len(set(words))
        if word_count > 0:
            diversity_ratio = unique_words / word_count
            if diversity_ratio > 0.7:
                score += 15
            elif diversity_ratio > 0.5:
                score += 10
            else:
                score += 5
        
        # 4. Avoid excessive repetition
        word_freq = Counter(word.lower() for word in words)
        most_common = word_freq.most_common(1)
        if most_common and most_common[0][1] > word_count * 0.2:
            score -= 15  # Penalty for repetition
        
        # 5. Professional language check
        professional_indicators = ['because', 'therefore', 'however', 'additionally',
                                  'furthermore', 'consequently', 'specifically']
        professional_count = sum(1 for word in professional_indicators 
                               if word in answer.lower())
        score += min(professional_count * 3, 10)
        
        return min(100, max(0, score))
    
    def _evaluate_sentiment_and_tone(self, answer: str) -> float:
        """
        Analyze sentiment and emotional tone
        """
        answer_lower = answer.lower().strip()
        word_count = len(answer.split())
        
        # Detect non-answers
        non_answer_phrases = [
            'i don\'t know', 'i dont know', 'not sure', 'no idea',
            'don\'t know', 'dont know', 'i have no idea'
        ]
        
        if any(phrase in answer_lower for phrase in non_answer_phrases):
            return 20.0  # Low score for non-answers
        
        if word_count < 5:
            return 25.0
        
        score = 35.0  # Lower baseline
        
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(answer)
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
                
                # Positive polarity is good (confident, optimistic)
                if polarity > 0.2:
                    score += polarity * 30  # Up to 30 points
                elif polarity > 0:
                    score += polarity * 20
                elif polarity < -0.3:
                    score -= 20  # Penalty for negative tone
                
                # Moderate subjectivity is good (personal but not too emotional)
                if 0.3 <= subjectivity <= 0.6:
                    score += 15
                elif 0.2 <= subjectivity < 0.3:
                    score += 10
                elif subjectivity < 0.2:
                    score += 5  # Too factual/robotic
                    
            except Exception as e:
                logger.warning(f"TextBlob sentiment analysis failed: {e}")
        
        # Check for confidence indicators
        confidence_words = ['confident', 'certainly', 'definitely', 'absolutely',
                          'believe', 'sure', 'experience', 'successfully']
        confidence_count = sum(1 for word in confidence_words 
                             if word in answer.lower())
        score += min(confidence_count * 4, 12)
        
        # Check for uncertainty indicators (negative)
        uncertainty_words = ['maybe', 'perhaps', 'not sure', 'i think', 
                           'possibly', 'might', 'could be', 'guess']
        uncertainty_count = sum(1 for phrase in uncertainty_words 
                              if phrase in answer.lower())
        score -= min(uncertainty_count * 6, 20)
        
        return min(100, max(0, score))
    
    def _evaluate_completeness(self, answer: str, question: Dict) -> float:
        """
        Evaluate if the answer is complete and addresses the question
        """
        answer_lower = answer.lower().strip()
        word_count = len(answer.split())
        
        # Detect non-answers
        non_answer_phrases = [
            'i don\'t know', 'i dont know', 'not sure', 'no idea',
            'don\'t know', 'dont know', 'i have no idea'
        ]
        
        if any(phrase in answer_lower for phrase in non_answer_phrases):
            return 10.0  # Very low score for non-answers
        
        if word_count < 5:
            return 15.0
        
        score = 25.0  # Lower baseline
        
        # Check if answer meets expected duration (word count proxy)
        expected_duration = question.get('expected_duration', 60)
        expected_words = expected_duration * 2.5  # ~150 WPM / 60 seconds * 2.5
        
        if word_count >= expected_words * 0.8:
            score += 30
        elif word_count >= expected_words * 0.6:
            score += 25
        elif word_count >= expected_words * 0.4:
            score += 15
        elif word_count < expected_words * 0.2:
            score -= 10
        
        # Check if key question elements are addressed
        question_text = question['question'].lower()
        
        # Extract question keywords
        question_words = set(re.findall(r'\w+', question_text))
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why',
                     'when', 'where', 'who', 'which', 'do', 'does', 'you', 'your'}
        question_keywords = question_words - stop_words
        
        # Check how many question keywords appear in answer
        matched = sum(1 for kw in question_keywords if kw in answer_lower)
        if question_keywords:
            match_ratio = matched / len(question_keywords)
            score += match_ratio * 30
            
            # Penalty if very few keywords matched
            if match_ratio < 0.2:
                score -= 15
        
        # Check for examples or explanations
        explanation_indicators = ['for example', 'such as', 'like', 'because', 
                                 'this means', 'in other words', 'specifically']
        has_explanation = any(phrase in answer_lower for phrase in explanation_indicators)
        if has_explanation:
            score += 10
        
        return min(100, max(0, score))
    
    def _generate_feedback(self, answer: str, question: Dict,
                          technical: float, communication: float,
                          sentiment: float, completeness: float,
                          mode: str) -> Dict:
        """Generate detailed, actionable feedback"""
        
        strengths = []
        weaknesses = []
        suggestions = []
        missing_points = []
        
        answer_lower = answer.lower().strip()
        
        # Check for non-answers first
        non_answer_phrases = [
            'i don\'t know', 'i dont know', 'not sure', 'no idea',
            'don\'t know', 'dont know'
        ]
        is_non_answer = any(phrase in answer_lower for phrase in non_answer_phrases)
        
        if is_non_answer:
            weaknesses.append("❌ Admitted lack of knowledge or provided no substantive answer")
            suggestions.append("💡 Even if unsure, try to provide a partial answer or related knowledge")
            suggestions.append("💡 Explain your thought process or mention related concepts you do know")
        
        # Technical Accuracy Feedback
        if technical >= 80:
            strengths.append("✅ Strong technical understanding demonstrated")
        elif technical >= 60:
            strengths.append("✅ Good grasp of core concepts")
        elif technical >= 40:
            weaknesses.append("⚠️ Technical accuracy needs improvement")
            suggestions.append("💡 Include more specific technical terminology and concepts")
        else:
            weaknesses.append("❌ Answer lacks technical substance")
            suggestions.append("💡 Study the core concepts related to this question")
            suggestions.append("💡 Provide specific examples and technical details")
        
        # Check for missing keywords
        keywords = question.get('keywords', [])
        missed = [kw for kw in keywords if kw.lower() not in answer_lower]
        if missed and mode in ["Technical", "Mixed"]:
            missing_points.extend(missed[:5])  # Show up to 5 missing points
            if len(missed) >= 3:
                weaknesses.append(f"⚠️ Missing {len(missed)} key concepts in your answer")
        
        # Communication Feedback
        word_count = len(answer.split())
        if communication >= 80:
            strengths.append("✅ Excellent communication and articulation")
        elif communication >= 60:
            strengths.append("✅ Clear and coherent response")
        elif communication >= 40:
            weaknesses.append("⚠️ Communication could be more structured")
            if word_count < 20:
                suggestions.append("💡 Provide more detailed explanations (aim for 30-100 words)")
        else:
            weaknesses.append("❌ Poor communication structure")
            if word_count < 10:
                suggestions.append("💡 Your answer is too brief - elaborate more")
            suggestions.append("💡 Use complete sentences and organize your thoughts")
        
        # Sentiment Feedback
        if sentiment >= 80:
            strengths.append("✅ Confident and positive tone")
        elif sentiment >= 60:
            strengths.append("✅ Professional demeanor")
        elif sentiment >= 40:
            weaknesses.append("⚠️ Could show more confidence")
            suggestions.append("💡 Use more assertive language and avoid uncertainty")
        else:
            weaknesses.append("❌ Tone shows lack of confidence or negativity")
            suggestions.append("💡 Avoid phrases like 'I don't know', 'not sure', 'maybe'")
        
        # Completeness Feedback
        if completeness >= 80:
            strengths.append("✅ Comprehensive answer addressing all aspects")
        elif completeness >= 60:
            strengths.append("✅ Answer covers main points")
        elif completeness >= 40:
            weaknesses.append("⚠️ Answer lacks depth or completeness")
            suggestions.append("💡 Ensure you fully address all parts of the question")
        else:
            weaknesses.append("❌ Answer is incomplete or off-topic")
            suggestions.append("💡 Review the question carefully and provide relevant information")
            suggestions.append("💡 Include examples or specific details to strengthen your answer")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
            'missing_technical_points': missing_points
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A (Excellent)"
        elif score >= 80:
            return "B (Very Good)"
        elif score >= 70:
            return "C (Good)"
        elif score >= 60:
            return "D (Satisfactory)"
        else:
            return "F (Needs Improvement)"
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return float(dot_product / (norm1 * norm2)) if norm1 and norm2 else 0.0
        except Exception:
            return 0.0


# Convenience function
def evaluate_answer(user_answer: str, question: Dict, 
                   interview_mode: str, difficulty: str, api_key: str = None) -> Dict:
    """
    Evaluate an interview answer
    
    Args:
        user_answer: User's transcribed answer
        question: Question dictionary
        interview_mode: Interview type
        difficulty: Difficulty level
        api_key: Optional Gemini API Key
        
    Returns:
        Evaluation results dictionary
    """
    evaluator = NLPEvaluator(api_key=api_key)
    return evaluator.evaluate_answer(user_answer, question, interview_mode, difficulty)
