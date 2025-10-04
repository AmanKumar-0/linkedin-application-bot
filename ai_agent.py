"""
Enhanced AI Agent for LinkedIn Job Applications
Provides intelligent responses to application forms
"""

import json
import requests
import re
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import logging
from cv_analyzer import CVData

@dataclass
class FormResponse:
    """Structure for form field responses"""
    answer: str
    confidence: float
    reasoning: str
    field_type: str

class EnhancedAIAgent:
    """Enhanced AI agent with smart form handling and context awareness"""
    
    def __init__(self, cv_data: CVData, ollama_url: str = "http://localhost:11434", 
                 model: str = "qwen2.5:7b"):
        self.cv_data = cv_data
        self.ollama_url = ollama_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Context for different types of questions
        self.question_patterns = {
            'experience': [
                'experience', 'years', 'worked', 'professional', 'career',
                'how long', 'duration', 'time in'
            ],
            'authorization': [
                'authorized', 'eligible', 'work authorization', 'legally authorized',
                'right to work', 'work permit', 'employment authorization'
            ],
            'visa_sponsorship': [
                'visa', 'sponsor', 'sponsorship', 'h1b', 'work visa',
                'immigration', 'permit', 'green card'
            ],
            'relocation': [
                'relocate', 'move', 'willing to move', 'open to relocation',
                'relocating', 'based in', 'work from'
            ],
            'remote_work': [
                'remote', 'work from home', 'remote work', 'distributed',
                'remote position', 'work remotely'
            ],
            'salary': [
                'salary', 'compensation', 'pay', 'wage', 'ctc', 'package',
                'expected salary', 'current salary', 'pay range'
            ],
            'notice_period': [
                'notice', 'availability', 'start', 'when can you start',
                'notice period', 'available to start', 'earliest start'
            ],
            'education': [
                'degree', 'education', 'bachelor', 'master', 'phd', 'diploma',
                'graduate', 'university', 'college', 'qualification'
            ],
            'skills': [
                'skill', 'technology', 'programming', 'framework', 'tool',
                'proficient', 'experience with', 'familiar with'
            ],
            'language': [
                'english', 'language', 'proficiency', 'fluent', 'native',
                'communication', 'speak', 'written'
            ],
            'management': [
                'manage', 'management', 'lead', 'supervisor', 'team lead',
                'leadership', 'managed team', 'reports'
            ],
            'travel': [
                'travel', 'travelling', 'business travel', 'willing to travel',
                'travel percentage', 'on-site visits'
            ]
        }
        
        # Smart responses based on CV data and common sense
        self.smart_responses = self._build_smart_responses()
    
    def _build_smart_responses(self) -> Dict[str, Any]:
        """Build intelligent response patterns based on CV data"""
        return {
            'experience_years': str(self.cv_data.experience_years),
            'current_salary': getattr(self.cv_data, 'salary_expectation', '').split('-')[0].strip() if '-' in getattr(self.cv_data, 'salary_expectation', '') else '',
            'expected_salary': self.cv_data.salary_expectation,
            'notice_period': self.cv_data.notice_period or "30 days",
            'visa_status': self.cv_data.visa_status,
            'willing_to_relocate': self.cv_data.willing_to_relocate,
            'degree_completed': bool(self.cv_data.education),
            'english_proficiency': 'Professional' if 'english' in [lang.get('language', '').lower() 
                                                                  for lang in self.cv_data.languages] else 'Professional',
            'management_experience': '2' if any('lead' in exp.get('title', '').lower() or 'manager' in exp.get('title', '').lower() 
                                               for exp in self.cv_data.work_experience) else '0',
            'travel_percentage': '25%',  # Default reasonable percentage
            'start_immediately': 'Yes' if self.cv_data.notice_period in ['0 days', 'immediate', 'immediately'] else 'No'
        }
    
    def categorize_question(self, question: str) -> str:
        """Categorize the type of question being asked"""
        question_lower = question.lower()
        
        for category, patterns in self.question_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                return category
        
        return 'general'
    
    def get_smart_answer(self, question: str, options: List[str] = None, 
                        error_message: str = "", job_context: Dict = None) -> FormResponse:
        """Get intelligent answer based on question category and context"""
        
        category = self.categorize_question(question)
        confidence = 0.9  # Default high confidence
        reasoning = f"Based on CV data and question category: {category}"
        
        # Handle specific error patterns first
        if error_message:
            error_response = self._handle_error_message(question, error_message, options)
            if error_response:
                return error_response
        
        # Category-specific intelligent responses
        if category == 'experience':
            answer = self._handle_experience_question(question, options)
        elif category == 'authorization':
            answer = self._handle_authorization_question(question, options)
        elif category == 'visa_sponsorship':
            answer = self._handle_visa_question(question, options)
        elif category == 'relocation':
            answer = self._handle_relocation_question(question, options)
        elif category == 'remote_work':
            answer = self._handle_remote_work_question(question, options)
        elif category == 'salary':
            answer = self._handle_salary_question(question, options)
        elif category == 'notice_period':
            answer = self._handle_notice_period_question(question, options)
        elif category == 'education':
            answer = self._handle_education_question(question, options)
        elif category == 'language':
            answer = self._handle_language_question(question, options)
        elif category == 'management':
            answer = self._handle_management_question(question, options)
        elif category == 'travel':
            answer = self._handle_travel_question(question, options)
        else:
            # Use AI for complex or unrecognized questions
            answer = self._get_ai_response(question, options, job_context)
            confidence = 0.7  # Lower confidence for AI responses
            reasoning = "AI-generated response for complex question"
        
        return FormResponse(
            answer=answer,
            confidence=confidence,
            reasoning=reasoning,
            field_type=category
        )
    
    def _handle_error_message(self, question: str, error_message: str, 
                            options: List[str] = None) -> Optional[FormResponse]:
        """Handle specific error message patterns"""
        error_lower = error_message.lower()
        
        if "whole number between 0 and 99" in error_lower:
            if 'experience' in question.lower():
                return FormResponse(
                    answer=str(min(self.cv_data.experience_years, 99)),
                    confidence=0.95,
                    reasoning="Experience years from CV, capped at 99",
                    field_type="numeric"
                )
            elif 'notice' in question.lower():
                notice_days = re.findall(r'\d+', self.cv_data.notice_period or "30")
                days = int(notice_days[0]) if notice_days else 30
                return FormResponse(
                    answer=str(min(days, 99)),
                    confidence=0.9,
                    reasoning="Notice period from CV, capped at 99",
                    field_type="numeric"
                )
        
        elif "decimal number larger than 0.0" in error_lower:
            if 'salary' in question.lower():
                # Extract numeric part from salary expectation
                salary_numbers = re.findall(r'\d+', self.cv_data.salary_expectation or "60000")
                if salary_numbers:
                    return FormResponse(
                        answer=salary_numbers[0],
                        confidence=0.8,
                        reasoning="Salary from CV expectation",
                        field_type="decimal"
                    )
        
        return None
    
    def _handle_experience_question(self, question: str, options: List[str] = None) -> str:
        """Handle experience-related questions"""
        if options:
            # Look for exact match first
            exp_str = str(self.cv_data.experience_years)
            for option in options:
                if exp_str in option or option == exp_str:
                    return option
            
            # Look for range match
            for option in options:
                if re.search(r'(\d+)[-\s]?(\d+)', option):
                    range_match = re.search(r'(\d+)[-\s]?(\d+)', option)
                    min_exp, max_exp = int(range_match.group(1)), int(range_match.group(2))
                    if min_exp <= self.cv_data.experience_years <= max_exp:
                        return option
        
        return str(self.cv_data.experience_years)
    
    def _handle_authorization_question(self, question: str, options: List[str] = None) -> str:
        """Handle work authorization questions"""
        # Check visa status to determine authorization
        visa_status_lower = self.cv_data.visa_status.lower()
        
        if any(status in visa_status_lower for status in ['citizen', 'permanent resident', 'green card']):
            authorized = True
        else:
            authorized = False
        
        if options:
            yes_options = [opt for opt in options if opt.lower().strip() in ['yes', 'true', 'authorized']]
            no_options = [opt for opt in options if opt.lower().strip() in ['no', 'false', 'not authorized']]
            
            if authorized and yes_options:
                return yes_options[0]
            elif not authorized and no_options:
                return no_options[0]
        
        return "Yes" if authorized else "No"
    
    def _handle_visa_question(self, question: str, options: List[str] = None) -> str:
        """Handle visa sponsorship questions"""
        needs_sponsorship = 'citizen' not in self.cv_data.visa_status.lower() and 'permanent resident' not in self.cv_data.visa_status.lower()
        
        if 'sponsor' in question.lower():
            # Question asking if they need sponsorship
            answer = "Yes" if needs_sponsorship else "No"
        else:
            # Question asking about visa status
            answer = self.cv_data.visa_status
        
        if options:
            # Find best matching option
            for option in options:
                if (needs_sponsorship and any(word in option.lower() for word in ['yes', 'need', 'require'])) or \
                   (not needs_sponsorship and any(word in option.lower() for word in ['no', 'citizen', 'authorized'])):
                    return option
        
        return answer
    
    def _handle_relocation_question(self, question: str, options: List[str] = None) -> str:
        """Handle relocation questions"""
        willing = self.cv_data.willing_to_relocate
        
        if options:
            yes_options = [opt for opt in options if opt.lower().strip() in ['yes', 'true', 'willing']]
            no_options = [opt for opt in options if opt.lower().strip() in ['no', 'false', 'not willing']]
            
            if willing and yes_options:
                return yes_options[0]
            elif not willing and no_options:
                return no_options[0]
        
        return "Yes" if willing else "No"
    
    def _handle_remote_work_question(self, question: str, options: List[str] = None) -> str:
        """Handle remote work questions"""
        # Default to being open to remote work
        if options:
            remote_positive = [opt for opt in options if any(word in opt.lower() 
                             for word in ['yes', 'remote', 'willing', 'open'])]
            if remote_positive:
                return remote_positive[0]
        
        return "Yes"
    
    def _handle_salary_question(self, question: str, options: List[str] = None) -> str:
        """Handle salary-related questions"""
        salary_expectation = self.cv_data.salary_expectation
        
        if 'current' in question.lower():
            # Extract current salary if mentioned in expectation
            if '-' in salary_expectation:
                return salary_expectation.split('-')[0].strip()
            return salary_expectation
        
        return salary_expectation
    
    def _handle_notice_period_question(self, question: str, options: List[str] = None) -> str:
        """Handle notice period questions"""
        notice = self.cv_data.notice_period or "30 days"
        
        if options:
            # Look for matching option
            for option in options:
                if any(word in option.lower() for word in notice.lower().split()):
                    return option
        
        # Extract just the number if needed
        numbers = re.findall(r'\d+', notice)
        if numbers and 'number' in question.lower():
            return numbers[0]
        
        return notice
    
    def _handle_education_question(self, question: str, options: List[str] = None) -> str:
        """Handle education-related questions"""
        has_degree = bool(self.cv_data.education)
        
        if 'bachelor' in question.lower():
            has_bachelor = any('bachelor' in edu.get('degree', '').lower() 
                             for edu in self.cv_data.education)
            answer = "Yes" if has_bachelor else "No"
        else:
            answer = "Yes" if has_degree else "No"
        
        if options:
            for option in options:
                if (answer.lower() == 'yes' and any(word in option.lower() for word in ['yes', 'true', 'have'])) or \
                   (answer.lower() == 'no' and any(word in option.lower() for word in ['no', 'false', 'do not'])):
                    return option
        
        return answer
    
    def _handle_language_question(self, question: str, options: List[str] = None) -> str:
        """Handle language proficiency questions"""
        if 'english' in question.lower():
            # Check if English is in languages
            english_prof = 'Professional'
            for lang in self.cv_data.languages:
                if 'english' in lang.get('language', '').lower():
                    english_prof = lang.get('proficiency', 'Professional')
                    break
            
            if options:
                # Find best matching proficiency level
                prof_lower = english_prof.lower()
                for option in options:
                    if prof_lower in option.lower() or option.lower() in prof_lower:
                        return option
            
            return english_prof
        
        return "Professional"
    
    def _handle_management_question(self, question: str, options: List[str] = None) -> str:
        """Handle management experience questions"""
        has_mgmt_exp = any('lead' in exp.get('title', '').lower() or 
                          'manager' in exp.get('title', '').lower() or
                          'supervisor' in exp.get('title', '').lower()
                          for exp in self.cv_data.work_experience)
        
        if 'years' in question.lower() and has_mgmt_exp:
            return self.smart_responses['management_experience']
        
        answer = "Yes" if has_mgmt_exp else "No"
        
        if options:
            for option in options:
                if (answer.lower() == 'yes' and any(word in option.lower() for word in ['yes', 'true', 'have'])) or \
                   (answer.lower() == 'no' and any(word in option.lower() for word in ['no', 'false', 'do not'])):
                    return option
        
        return answer
    
    def _handle_travel_question(self, question: str, options: List[str] = None) -> str:
        """Handle travel-related questions"""
        if options:
            # Look for reasonable travel percentage options
            reasonable_options = [opt for opt in options if any(perc in opt for perc in ['25%', '20%', '30%', '10%'])]
            if reasonable_options:
                return reasonable_options[0]
        
        return self.smart_responses['travel_percentage']
    
    def _get_ai_response(self, question: str, options: List[str] = None, 
                        job_context: Dict = None) -> str:
        """Get AI response for complex questions"""
        try:
            context = self._build_context_prompt(job_context)
            
            if options:
                prompt = f"""{context}

Question: {question}
Available options: {options}

Based on the candidate profile above, select the EXACT option text that best matches. 
Return only the option text, nothing else.
"""
            else:
                prompt = f"""{context}

Question: {question}

Provide a concise, professional answer (max 50 characters) based on the candidate profile.
Examples:
- Experience: "4"
- Yes/No: "Yes" or "No"
- Text: brief professional response
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 100}
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()['response'].strip()
                return result.replace('"', '').replace("'", "").strip()
            
        except Exception as e:
            self.logger.error(f"AI response error: {e}")
        
        # Fallback to smart default
        return self._get_fallback_answer(question, options)
    
    def _build_context_prompt(self, job_context: Dict = None) -> str:
        """Build context prompt for AI"""
        context = f"""
Candidate Profile:
- Name: {self.cv_data.name}
- Experience: {self.cv_data.experience_years} years as {self.cv_data.current_title}
- Location: {self.cv_data.location}
- Education: {', '.join([edu.get('degree', '') for edu in self.cv_data.education]) if self.cv_data.education else 'Not specified'}
- Skills: {', '.join(self.cv_data.technical_skills[:10])}
- Visa Status: {self.cv_data.visa_status}
- Notice Period: {self.cv_data.notice_period}
- Willing to Relocate: {self.cv_data.willing_to_relocate}
- Salary Expectation: {self.cv_data.salary_expectation}
"""
        
        if job_context:
            context += f"""
Job Context:
- Title: {job_context.get('title', 'N/A')}
- Company: {job_context.get('company', 'N/A')}
"""
        
        return context
    
    def _get_fallback_answer(self, question: str, options: List[str] = None) -> str:
        """Provide fallback answer when all else fails"""
        question_lower = question.lower()
        
        # Common fallback patterns
        if any(word in question_lower for word in ['authorized', 'eligible']):
            return 'No' if 'citizen' not in self.cv_data.visa_status.lower() else 'Yes'
        
        if any(word in question_lower for word in ['visa', 'sponsor']):
            return 'Yes'  # Assume needs sponsorship as fallback
        
        if any(word in question_lower for word in ['degree', 'bachelor', 'education']):
            return 'Yes' if self.cv_data.education else 'No'
        
        if any(word in question_lower for word in ['experience', 'years']):
            return str(self.cv_data.experience_years)
        
        if any(word in question_lower for word in ['relocate', 'move']):
            return 'Yes' if self.cv_data.willing_to_relocate else 'No'
        
        # Default positive response for ambiguous questions
        if options:
            positive_options = [opt for opt in options if any(word in opt.lower() 
                              for word in ['yes', 'true', 'willing', 'able', 'can'])]
            if positive_options:
                return positive_options[0]
        
        return 'Yes'
    
    def generate_cover_letter(self, job_title: str, company_name: str, 
                            job_description: str = "") -> str:
        """Generate a personalized cover letter"""
        try:
            prompt = f"""
Write a professional, compelling cover letter for this position. Keep it concise (250-300 words) and personalized.

Position: {job_title} at {company_name}
Job Description: {job_description[:800]}...

Candidate Information:
- Name: {self.cv_data.name}
- Current Role: {self.cv_data.current_title}
- Experience: {self.cv_data.experience_years} years
- Key Skills: {', '.join(self.cv_data.technical_skills[:8])}
- Education: {', '.join([edu.get('degree', '') for edu in self.cv_data.education]) if self.cv_data.education else 'Professional background'}
- Location: {self.cv_data.location}

Requirements:
- Professional tone, not overly enthusiastic
- Highlight relevant skills and experience
- Show genuine interest in the role and company
- Mention specific skills that match the job requirements
- Keep it concise and impactful
- End with a call to action

Format as a proper cover letter without placeholders.
"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 500}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            
        except Exception as e:
            self.logger.error(f"Cover letter generation error: {e}")
        
        # Fallback template
        return self._generate_fallback_cover_letter(job_title, company_name)
    
    def _generate_fallback_cover_letter(self, job_title: str, company_name: str) -> str:
        """Generate a fallback cover letter template"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With {self.cv_data.experience_years} years of experience as a {self.cv_data.current_title}, I am confident that my technical skills and professional background make me an ideal candidate for this role.

My expertise includes {', '.join(self.cv_data.technical_skills[:5])}, which aligns well with the requirements for this position. Throughout my career, I have successfully delivered innovative solutions and contributed to the growth of the organizations I've worked with.

I am particularly drawn to {company_name} because of its reputation for innovation and excellence. I am eager to bring my skills and enthusiasm to your team and contribute to your continued success.

I would welcome the opportunity to discuss how my background and passion for technology can benefit {company_name}. Thank you for your consideration.

Best regards,
{self.cv_data.name}"""