"""
Report Generator Module
Generates comprehensive PDF reports with charts and detailed feedback
"""

import json
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import PDF generation libraries
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    logger.warning("fpdf not available. PDF generation disabled.")


class InterviewReportGenerator:
    """Generate detailed interview performance reports"""
    
    def __init__(self):
        self.pdf = None
    
    def generate_pdf_report(self, session_data: Dict, analytics: Dict, 
                           output_path: str = None) -> str:
        """
        Generate a comprehensive PDF report
        
        Args:
            session_data: Session data from database
            analytics: Analytics data from database
            output_path: Optional custom output path
            
        Returns:
            Path to generated PDF file
        """
        if not FPDF_AVAILABLE:
            logger.error("fpdf library not available")
            return self._generate_text_report(session_data, analytics, output_path)
        
        try:
            self.pdf = FPDF()
            self.pdf.add_page()
            
            # Title Page
            self._add_title_page(session_data)
            
            # Executive Summary
            self._add_executive_summary(session_data, analytics)
            
            # Detailed Question-by-Question Analysis
            self._add_question_analysis(session_data)
            
            # Skill Breakdown
            self._add_skill_breakdown(analytics)
            
            # Recommendations
            self._add_recommendations(session_data, analytics)
            
            # Save PDF
            if not output_path:
                output_path = f"reports/interview_report_{session_data['session_id']}.pdf"
            
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            self.pdf.output(output_path)
            logger.info(f"PDF report generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return self._generate_text_report(session_data, analytics, output_path)
    
    def _add_title_page(self, session_data: Dict):
        """Add title page to PDF"""
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 20, 'Interview Performance Report', 0, 1, 'C')
        
        self.pdf.set_font('Arial', '', 12)
        self.pdf.ln(10)
        self.pdf.cell(0, 10, f"Session ID: {session_data['session_id']}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Candidate: {session_data['user_name']}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Date: {session_data['start_time'][:10]}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Mode: {session_data['mode']}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Difficulty: {session_data['difficulty']}", 0, 1, 'C')
        
        self.pdf.ln(20)
    
    def _add_executive_summary(self, session_data: Dict, analytics: Dict):
        """Add executive summary section"""
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'Executive Summary', 0, 1)
        self.pdf.ln(5)
        
        self.pdf.set_font('Arial', '', 11)
        
        # Overall Score
        overall_score = session_data['overall_score']
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.set_text_color(0, 128, 0) if overall_score >= 70 else self.pdf.set_text_color(255, 0, 0)
        self.pdf.cell(0, 10, f"Overall Score: {overall_score:.1f}/100", 0, 1)
        self.pdf.set_text_color(0, 0, 0)
        
        # Statistics
        self.pdf.set_font('Arial', '', 11)
        self.pdf.cell(0, 8, f"Total Questions: {analytics['total_questions']}", 0, 1)
        self.pdf.cell(0, 8, f"Questions Passed: {analytics['questions_passed']}", 0, 1)
        self.pdf.cell(0, 8, f"Duration: {analytics['duration_minutes']} minutes", 0, 1)
        
        self.pdf.ln(10)
    
    def _add_question_analysis(self, session_data: Dict):
        """Add detailed question-by-question analysis"""
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'Question-by-Question Analysis', 0, 1)
        self.pdf.ln(5)
        
        for idx, q_data in enumerate(session_data['questions'], 1):
            self.pdf.set_font('Arial', 'B', 12)
            self.pdf.cell(0, 8, f"Question {idx}", 0, 1)
            
            self.pdf.set_font('Arial', '', 10)
            self.pdf.multi_cell(0, 6, f"Q: {q_data['question']}")
            self.pdf.ln(2)
            
            self.pdf.multi_cell(0, 6, f"A: {q_data['answer'][:200]}...")
            self.pdf.ln(2)
            
            # Scores
            eval_data = q_data.get('evaluation', {})
            score = eval_data.get('overall_score', 0)
            grade = eval_data.get('grade', 'N/A')
            
            self.pdf.set_font('Arial', 'B', 10)
            self.pdf.cell(0, 6, f"Score: {score}/100 - {grade}", 0, 1)
            
            # Feedback
            self.pdf.set_font('Arial', '', 9)
            feedback = eval_data.get('feedback', {})
            strengths = feedback.get('strengths', [])
            if strengths:
                self.pdf.cell(0, 6, f"Strengths: {', '.join(strengths[:2])}", 0, 1)
            
            weaknesses = feedback.get('weaknesses', [])
            if weaknesses:
                self.pdf.cell(0, 6, f"Areas for Improvement: {', '.join(weaknesses[:2])}", 0, 1)
            
            self.pdf.ln(5)
            
            # Page break if needed
            if self.pdf.get_y() > 250:
                self.pdf.add_page()
    
    def _add_skill_breakdown(self, analytics: Dict):
        """Add skill breakdown section"""
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'Skill Breakdown', 0, 1)
        self.pdf.ln(5)
        
        skill_breakdown = analytics['skill_breakdown']
        
        self.pdf.set_font('Arial', '', 11)
        for skill, score in skill_breakdown.items():
            skill_name = skill.replace('_', ' ').title()
            self.pdf.cell(100, 8, skill_name, 0, 0)
            self.pdf.cell(0, 8, f"{score:.1f}/100", 0, 1)
        
        self.pdf.ln(10)
    
    def _add_recommendations(self, session_data: Dict, analytics: Dict):
        """Add recommendations section"""
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'Recommendations', 0, 1)
        self.pdf.ln(5)
        
        self.pdf.set_font('Arial', '', 11)
        
        # Collect all suggestions
        all_suggestions = []
        for q_data in session_data['questions']:
            feedback = q_data.get('evaluation', {}).get('feedback', {})
            suggestions = feedback.get('suggestions', [])
            all_suggestions.extend(suggestions)
        
        # Get unique suggestions
        unique_suggestions = list(set(all_suggestions))[:5]
        
        for idx, suggestion in enumerate(unique_suggestions, 1):
            self.pdf.multi_cell(0, 6, f"{idx}. {suggestion}")
            self.pdf.ln(2)
        
        self.pdf.ln(10)
        
        # Overall recommendation
        overall_score = session_data['overall_score']
        if overall_score >= 80:
            recommendation = "Excellent performance! You're well-prepared for interviews."
        elif overall_score >= 70:
            recommendation = "Good performance. Focus on the specific areas mentioned above."
        elif overall_score >= 60:
            recommendation = "Satisfactory performance. Practice more in weak areas."
        else:
            recommendation = "More practice needed. Focus on fundamentals and build confidence."
        
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.multi_cell(0, 8, f"Overall Recommendation: {recommendation}")
    
    def _generate_text_report(self, session_data: Dict, analytics: Dict, 
                            output_path: str = None) -> str:
        """Generate text-based report as fallback"""
        if not output_path:
            output_path = f"reports/interview_report_{session_data['session_id']}.txt"
        
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("INTERVIEW PERFORMANCE REPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Session ID: {session_data['session_id']}\n")
            f.write(f"Candidate: {session_data['user_name']}\n")
            f.write(f"Mode: {session_data['mode']}\n")
            f.write(f"Difficulty: {session_data['difficulty']}\n")
            f.write(f"Date: {session_data['start_time'][:10]}\n\n")
            
            f.write("="*60 + "\n")
            f.write("EXECUTIVE SUMMARY\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Overall Score: {session_data['overall_score']:.1f}/100\n")
            f.write(f"Total Questions: {analytics['total_questions']}\n")
            f.write(f"Questions Passed: {analytics['questions_passed']}\n")
            f.write(f"Duration: {analytics['duration_minutes']} minutes\n\n")
            
            f.write("="*60 + "\n")
            f.write("SKILL BREAKDOWN\n")
            f.write("="*60 + "\n\n")
            
            for skill, score in analytics['skill_breakdown'].items():
                f.write(f"{skill.replace('_', ' ').title()}: {score:.1f}/100\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("QUESTION ANALYSIS\n")
            f.write("="*60 + "\n\n")
            
            for idx, q_data in enumerate(session_data['questions'], 1):
                f.write(f"\nQuestion {idx}:\n")
                f.write(f"Q: {q_data['question']}\n")
                f.write(f"A: {q_data['answer']}\n\n")
                
                eval_data = q_data.get('evaluation', {})
                score = eval_data.get('overall_score', 0)
                grade = eval_data.get('grade', 'N/A')
                f.write(f"Score: {score}/100 - {grade}\n")
                
                feedback = eval_data.get('feedback', {})
                if feedback.get('strengths'):
                    f.write(f"Strengths: {', '.join(feedback['strengths'])}\n")
                
                if feedback.get('weaknesses'):
                    f.write(f"Weaknesses: {', '.join(feedback['weaknesses'])}\n")
                
                f.write("-"*60 + "\n")
        
        logger.info(f"Text report generated: {output_path}")
        return output_path
    
    def generate_json_report(self, session_data: Dict, analytics: Dict) -> str:
        """Generate JSON format report for data exchange"""
        report = {
            'metadata': {
                'session_id': session_data['session_id'],
                'user_name': session_data['user_name'],
                'mode': session_data['mode'],
                'difficulty': session_data['difficulty'],
                'timestamp': session_data['start_time']
            },
            'summary': {
                'overall_score': session_data['overall_score'],
                'total_questions': analytics['total_questions'],
                'questions_passed': analytics['questions_passed'],
                'duration_minutes': analytics['duration_minutes']
            },
            'skill_breakdown': analytics['skill_breakdown'],
            'questions': session_data['questions']
        }
        
        return json.dumps(report, indent=2, ensure_ascii=False)


# Convenience function
def generate_report(session_data: Dict, analytics: Dict, 
                   format: str = "pdf", output_path: str = None) -> str:
    """
    Generate interview report
    
    Args:
        session_data: Session data from database
        analytics: Analytics data
        format: "pdf", "txt", or "json"
        output_path: Optional custom output path
        
    Returns:
        Path to generated report or JSON string
    """
    generator = InterviewReportGenerator()
    
    if format == "pdf":
        return generator.generate_pdf_report(session_data, analytics, output_path)
    elif format == "txt":
        return generator._generate_text_report(session_data, analytics, output_path)
    elif format == "json":
        return generator.generate_json_report(session_data, analytics)
    else:
        raise ValueError(f"Unsupported format: {format}")
