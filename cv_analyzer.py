"""
Enhanced CV Analyzer with AI Integration
Extracts comprehensive information from CV files
"""

import os
import re
import json
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import logging

@dataclass
class CVData:
    """Structured CV data"""
    # Personal Information
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    # Professional Information
    current_title: str = ""
    experience_years: int = 0
    summary: str = ""
    
    # Skills and Expertise
    technical_skills: List[str] = None
    soft_skills: List[str] = None
    tools_technologies: List[str] = None
    programming_languages: List[str] = None
    frameworks: List[str] = None
    databases: List[str] = None
    cloud_platforms: List[str] = None
    
    # Education
    education: List[Dict[str, str]] = None
    certifications: List[str] = None
    
    # Work Experience
    work_experience: List[Dict[str, Union[str, List[str]]]] = None
    
    # Projects
    projects: List[Dict[str, str]] = None
    
    # Languages
    languages: List[Dict[str, str]] = None
    
    # Additional Information
    achievements: List[str] = None
    publications: List[str] = None
    volunteer_work: List[str] = None
    
    # Preferences (inferred or explicit)
    salary_expectation: str = ""
    notice_period: str = ""
    visa_status: str = ""
    willing_to_relocate: bool = True
    preferred_locations: List[str] = None
    
    def __post_init__(self):
        # Initialize lists if None
        for field_name, field_type in self.__annotations__.items():
            if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                if getattr(self, field_name) is None:
                    setattr(self, field_name, [])

class EnhancedCVAnalyzer:
    """Enhanced CV analyzer with multiple extraction methods"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.ollama_url = ollama_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Skill categories for better organization
        self.skill_categories = {
            'programming_languages': [
                'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'swift', 'kotlin', 'scala', 'r', 'matlab', 'typescript', 'dart'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'express',
                'laravel', 'rails', 'asp.net', 'flutter', 'react native', 'ionic', 'xamarin'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'sqlite', 'oracle', 'sql server', 'dynamodb', 'firebase', 'neo4j'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean',
                'linode', 'vultr', 'cloudflare', 'vercel', 'netlify'
            ],
            'tools_technologies': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
                'jira', 'confluence', 'slack', 'postman', 'swagger', 'grafana', 'prometheus'
            ]
        }
    
    def extract_cv_text(self, cv_path: str) -> str:
        """Extract text from various CV formats"""
        try:
            if not os.path.exists(cv_path):
                self.logger.warning(f"CV file not found: {cv_path}")
                return self._find_alternative_cv()
            
            file_ext = cv_path.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                return self._extract_pdf_text(cv_path)
            elif file_ext in ['docx', 'doc']:
                return self._extract_docx_text(cv_path)
            elif file_ext == 'txt':
                return self._extract_txt_text(cv_path)
            else:
                self.logger.error(f"Unsupported CV format: {file_ext}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error extracting CV text: {e}")
            return ""
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            self.logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            self.logger.error(f"Error reading PDF: {e}")
            return ""
    
    def _extract_docx_text(self, docx_path: str) -> str:
        """Extract text from DOCX"""
        try:
            import docx
            doc = docx.Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            self.logger.error("python-docx not installed. Install with: pip install python-docx")
            return ""
        except Exception as e:
            self.logger.error(f"Error reading DOCX: {e}")
            return ""
    
    def _extract_txt_text(self, txt_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error reading TXT: {e}")
            return ""
    
    def _find_alternative_cv(self) -> str:
        """Find alternative CV files in common locations"""
        possible_paths = [
            "cv.pdf", "resume.pdf", "CV.pdf", "Resume.pdf",
            "cv.docx", "resume.docx", "CV.docx", "Resume.docx",
            "cv.txt", "resume.txt", "CV.txt", "Resume.txt"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found alternative CV: {path}")
                return self.extract_cv_text(path)
        
        self.logger.warning("No CV file found in common locations")
        return ""
    
    def analyze_cv_with_ai(self, cv_text: str) -> CVData:
        """Use AI to analyze CV and extract structured data"""
        try:
            if not cv_text.strip():
                self.logger.warning("Empty CV text provided")
                return self._create_fallback_cv_data()
            
            prompt = self._create_analysis_prompt(cv_text)
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "num_predict": 2000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()['response'].strip()
                return self._parse_ai_response(result, cv_text)
            else:
                self.logger.error(f"AI API error: {response.status_code}")
                return self._fallback_manual_parsing(cv_text)
                
        except Exception as e:
            self.logger.error(f"Error analyzing CV with AI: {e}")
            return self._fallback_manual_parsing(cv_text)
    
    def _create_analysis_prompt(self, cv_text: str) -> str:
        """Create comprehensive AI analysis prompt"""
        return f"""
Analyze this CV/Resume and extract comprehensive information in JSON format. Be thorough and accurate.

CV Text:
{cv_text}

Extract and return ONLY a valid JSON object with these exact fields:
{{
    "name": "Full name",
    "email": "Email address",
    "phone": "Phone number with country code",
    "location": "Current city, country",
    "linkedin_url": "LinkedIn profile URL",
    "github_url": "GitHub profile URL",
    "portfolio_url": "Portfolio website URL",
    "current_title": "Most recent job title or desired position",
    "experience_years": 0,
    "summary": "Professional summary or objective",
    "technical_skills": ["Array of technical skills"],
    "soft_skills": ["Array of soft skills"],
    "tools_technologies": ["Array of tools and technologies"],
    "programming_languages": ["Array of programming languages"],
    "frameworks": ["Array of frameworks and libraries"],
    "databases": ["Array of databases"],
    "cloud_platforms": ["Array of cloud platforms"],
    "education": [
        {{
            "degree": "Degree name",
            "institution": "Institution name",
            "year": "Graduation year",
            "field": "Field of study"
        }}
    ],
    "certifications": ["Array of certifications"],
    "work_experience": [
        {{
            "title": "Job title",
            "company": "Company name",
            "duration": "Start - End dates",
            "responsibilities": ["Array of key responsibilities"],
            "achievements": ["Array of achievements"]
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Project description",
            "technologies": "Technologies used",
            "url": "Project URL if available"
        }}
    ],
    "languages": [
        {{
            "language": "Language name",
            "proficiency": "Proficiency level"
        }}
    ],
    "achievements": ["Array of achievements and awards"],
    "publications": ["Array of publications"],
    "volunteer_work": ["Array of volunteer experiences"],
    "salary_expectation": "Expected salary range",
    "notice_period": "Notice period",
    "visa_status": "Visa/work authorization status",
    "willing_to_relocate": true,
    "preferred_locations": ["Array of preferred work locations"]
}}

Instructions:
- Extract ALL skills comprehensively - don't miss any technical skills, tools, or technologies
- For experience_years, calculate total professional experience
- Be accurate with contact information and URLs
- Include all education details with proper formatting
- Extract project details thoroughly
- Identify soft skills from descriptions
- Return only valid JSON, no additional text
"""
    
    def _parse_ai_response(self, ai_response: str, original_text: str) -> CVData:
        """Parse AI response and create CVData object"""
        try:
            # Clean up response to extract JSON
            if '```json' in ai_response:
                ai_response = ai_response.split('```json')[1].split('```')[0]
            elif '```' in ai_response:
                ai_response = ai_response.split('```')[1].split('```')[0]
            
            # Try to parse JSON
            data = json.loads(ai_response.strip())
            
            # Create CVData object with validation
            cv_data = CVData()
            
            # Map data with type checking and defaults
            for field, value in data.items():
                if hasattr(cv_data, field):
                    if field == 'experience_years':
                        cv_data.experience_years = int(value) if isinstance(value, (int, str)) and str(value).isdigit() else 0
                    elif field == 'willing_to_relocate':
                        cv_data.willing_to_relocate = bool(value) if isinstance(value, bool) else True
                    elif isinstance(getattr(cv_data, field), list):
                        setattr(cv_data, field, value if isinstance(value, list) else [])
                    else:
                        setattr(cv_data, field, str(value) if value else "")
            
            # Post-process and validate
            self._validate_and_enhance_cv_data(cv_data, original_text)
            
            return cv_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI JSON response: {e}")
            return self._fallback_manual_parsing(original_text)
        except Exception as e:
            self.logger.error(f"Error processing AI response: {e}")
            return self._fallback_manual_parsing(original_text)
    
    def _validate_and_enhance_cv_data(self, cv_data: CVData, original_text: str):
        """Validate and enhance CV data with additional processing"""
        # Categorize skills more accurately
        all_skills = (cv_data.technical_skills + cv_data.tools_technologies + 
                     cv_data.programming_languages + cv_data.frameworks + 
                     cv_data.databases + cv_data.cloud_platforms)
        
        # Re-categorize skills
        cv_data.programming_languages = []
        cv_data.frameworks = []
        cv_data.databases = []
        cv_data.cloud_platforms = []
        cv_data.tools_technologies = []
        
        for skill in all_skills:
            skill_lower = skill.lower()
            categorized = False
            
            for category, keywords in self.skill_categories.items():
                if any(keyword in skill_lower for keyword in keywords):
                    current_list = getattr(cv_data, category)
                    if skill not in current_list:
                        current_list.append(skill)
                    categorized = True
                    break
            
            if not categorized and skill not in cv_data.tools_technologies:
                cv_data.tools_technologies.append(skill)
        
        # Extract additional information using regex
        text_lower = original_text.lower()
        
        # Extract visa status if not found
        if not cv_data.visa_status:
            if any(term in text_lower for term in ['indian citizen', 'indian national']):
                cv_data.visa_status = "Indian Citizen"
            elif any(term in text_lower for term in ['us citizen', 'american citizen']):
                cv_data.visa_status = "US Citizen"
            elif any(term in text_lower for term in ['green card', 'permanent resident']):
                cv_data.visa_status = "Permanent Resident"
            else:
                cv_data.visa_status = "Requires Sponsorship"
        
        # Extract notice period
        notice_match = re.search(r'notice period[:\s]*(\d+)\s*(days?|months?)', text_lower)
        if notice_match and not cv_data.notice_period:
            cv_data.notice_period = f"{notice_match.group(1)} {notice_match.group(2)}"
        
        # Validate experience years
        if cv_data.experience_years == 0:
            exp_matches = re.findall(r'(\d+)[\+]?\s*year[s]?\s*(?:of\s+)?(?:experience|exp)', text_lower)
            if exp_matches:
                cv_data.experience_years = max(int(match) for match in exp_matches)
    
    def _fallback_manual_parsing(self, cv_text: str) -> CVData:
        """Fallback manual parsing when AI fails"""
        cv_data = CVData()
        text_lower = cv_text.lower()
        
        # Extract basic information using regex
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, cv_text, re.IGNORECASE)
        if emails:
            cv_data.email = emails[0]
        
        # Phone
        phone_pattern = r'[\+]?[1-9]?[0-9]{1,4}[\s-]?[\(]?[0-9]{1,4}[\)]?[\s-]?[0-9]{1,4}[\s-]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, cv_text)
        if phones:
            cv_data.phone = phones[0]
        
        # Skills extraction
        for category, keywords in self.skill_categories.items():
            found_skills = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_skills.append(keyword.title())
            setattr(cv_data, category, found_skills)
        
        # Experience years
        exp_matches = re.findall(r'(\d+)[\+]?\s*year[s]?\s*(?:of\s+)?(?:experience|exp)', text_lower)
        if exp_matches:
            cv_data.experience_years = max(int(match) for match in exp_matches)
        
        return cv_data
    
    def _create_fallback_cv_data(self) -> CVData:
        """Create fallback CV data when everything fails"""
        return CVData(
            name="Please update in config",
            email="your.email@example.com",
            phone="+1-XXX-XXX-XXXX",
            location="Your City, Country",
            current_title="Software Developer",
            experience_years=3,
            technical_skills=["Python", "JavaScript", "SQL"],
            visa_status="Please specify"
        )
    
    def generate_job_search_keywords(self, cv_data: CVData) -> List[str]:
        """Generate relevant job search keywords based on CV data"""
        keywords = []
        
        # Add current title variations
        if cv_data.current_title:
            keywords.append(cv_data.current_title)
            # Add common variations
            title_lower = cv_data.current_title.lower()
            if 'senior' in title_lower:
                keywords.append(cv_data.current_title.replace('Senior ', ''))
            elif 'junior' not in title_lower:
                keywords.append(f"Senior {cv_data.current_title}")
        
        # Add skill-based keywords
        primary_skills = cv_data.programming_languages + cv_data.frameworks[:3]
        for skill in primary_skills:
            if skill.lower() not in [k.lower() for k in keywords]:
                keywords.extend([
                    f"{skill} Developer",
                    f"{skill} Engineer"
                ])
        
        # Add general role keywords based on skills
        if any(skill.lower() in ['react', 'angular', 'vue', 'frontend', 'javascript'] 
               for skill in cv_data.technical_skills + cv_data.frameworks):
            keywords.extend(["Frontend Developer", "Frontend Engineer", "UI Developer"])
        
        if any(skill.lower() in ['python', 'java', 'node', 'backend', 'api', 'database'] 
               for skill in cv_data.technical_skills + cv_data.programming_languages):
            keywords.extend(["Backend Developer", "Backend Engineer", "API Developer"])
        
        if any(skill.lower() in ['react', 'angular', 'python', 'java', 'fullstack', 'full stack'] 
               for skill in cv_data.technical_skills + cv_data.frameworks + cv_data.programming_languages):
            keywords.extend(["Full Stack Developer", "Full Stack Engineer"])
        
        # Remove duplicates and limit
        keywords = list(dict.fromkeys(keywords))  # Preserve order while removing duplicates
        return keywords[:15]  # Limit to top 15 keywords
    
    def export_cv_data(self, cv_data: CVData, format: str = "json") -> str:
        """Export CV data in various formats"""
        try:
            if format.lower() == "json":
                return json.dumps(asdict(cv_data), indent=2, ensure_ascii=False)
            elif format.lower() == "dict":
                return asdict(cv_data)
            else:
                return str(cv_data)
        except Exception as e:
            self.logger.error(f"Error exporting CV data: {e}")
            return "{}"