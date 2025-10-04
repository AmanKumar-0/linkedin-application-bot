import time
import math
import random
import os
import platform
import json
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import utils
import constants
import config
import undetected_chromedriver as uc

class AIAgent:
    def __init__(self, ollama_url="http://localhost:11434", model="qwen2.5:7b", cv_path="cv.pdf"):
        self.ollama_url = ollama_url
        self.model = model
        self.cv_path = cv_path
        self.cv_text = self.extract_cv_text()
        self.cv_data = self.parse_cv_with_ai()
        print(f"🤖 CV Analysis Complete! Extracted {len(self.cv_data.get('skills', []))} skills and other details.")
        
    def extract_cv_text(self):
        """Extract text from CV file (supports PDF, DOCX, TXT)"""
        try:
            if not os.path.exists(self.cv_path):
                # Try common CV file locations
                possible_paths = [
                    "cv.pdf", "resume.pdf", "CV.pdf", "Resume.pdf",
                    "cv.docx", "resume.docx", "CV.docx", "Resume.docx", 
                    "cv.txt", "resume.txt", "CV.txt", "Resume.txt"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        self.cv_path = path
                        print(f"📄 Found CV file: {path}")
                        break
                else:
                    print("❌ No CV file found. Please place your CV as 'cv.pdf', 'resume.pdf', 'cv.docx', etc.")
                    return self.get_fallback_cv_text()
            
            file_ext = self.cv_path.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                return self.extract_pdf_text()
            elif file_ext in ['docx', 'doc']:
                return self.extract_docx_text()
            elif file_ext == 'txt':
                return self.extract_txt_text()
            else:
                print(f"❌ Unsupported CV format: {file_ext}")
                return self.get_fallback_cv_text()
                
        except Exception as e:
            print(f"❌ Error reading CV: {e}")
            return self.get_fallback_cv_text()
    
    def extract_pdf_text(self):
        """Extract text from PDF using PyPDF2"""
        try:
            import PyPDF2
            with open(self.cv_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")
            return self.get_fallback_cv_text()
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return self.get_fallback_cv_text()
    
    def extract_docx_text(self):
        """Extract text from DOCX using python-docx"""
        try:
            import docx
            doc = docx.Document(self.cv_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            print("⚠️ python-docx not installed. Install with: pip install python-docx")
            return self.get_fallback_cv_text()
        except Exception as e:
            print(f"❌ Error reading DOCX: {e}")
            return self.get_fallback_cv_text()
    
    def extract_txt_text(self):
        """Extract text from TXT file"""
        try:
            with open(self.cv_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"❌ Error reading TXT: {e}")
            return self.get_fallback_cv_text()
    
    def get_fallback_cv_text(self):
        """Fallback CV text if file reading fails"""
        return f"""
        Name: {getattr(config, 'full_name', 'Your Name')}
        Email: {getattr(config, 'email', 'your.email@example.com')}
        Phone: {getattr(config, 'phone', '+91-XXXXXXXXXX')}
        Experience: {getattr(config, 'experience_years', '3')} years
        Current Title: {getattr(config, 'current_title', 'Software Developer')}
        Skills: {', '.join(getattr(config, 'skills', ['Python', 'JavaScript', 'React', 'SQL']))}
        Education: {getattr(config, 'education', 'Bachelor in Computer Science')}
        Location: {getattr(config, 'location', 'India')}
        """
    
    def parse_cv_with_ai(self):
        """Use AI to parse CV and extract structured data"""
        try:
            prompt = f"""
Analyze this CV/Resume text and extract the following information in JSON format. Be precise and extract all relevant details:

CV Text:
{self.cv_text}

Extract and return ONLY a valid JSON object with these fields:
{{
    "name": "Full name of the person",
    "email": "Email address", 
    "phone": "Phone number",
    "experience_years": "Total years of experience as a number",
    "current_title": "Most recent job title",
    "skills": ["Array", "of", "technical", "skills", "programming languages", "frameworks", "tools"],
    "education": "Highest education degree and field",
    "location": "Current location/city",
    "certifications": ["Array", "of", "certifications"],
    "languages": ["Array", "of", "spoken", "languages"],
    "previous_companies": ["Array", "of", "previous", "company", "names"],
    "projects": ["Array", "of", "key", "projects"],
    "achievements": ["Array", "of", "key", "achievements"],
    "linkedin_url": "LinkedIn profile URL if mentioned",
    "github_url": "GitHub profile URL if mentioned",
    "portfolio_url": "Portfolio website URL if mentioned"
}}

Important: 
- Extract ALL technical skills, programming languages, frameworks, and tools mentioned
- Be comprehensive with skills array - include everything technical
- For experience_years, calculate total years from all positions
- Return only valid JSON, no extra text
"""

            response = requests.post(f"{self.ollama_url}/api/generate", 
                                   json={
                                       "model": self.model,
                                       "prompt": prompt,
                                       "stream": False,
                                       "options": {
                                           "temperature": 0.1,
                                           "top_p": 0.8
                                       }
                                   }, 
                                   timeout=60)
            
            if response.status_code == 200:
                result = response.json()['response'].strip()
                
                # Clean up the response to extract JSON
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0]
                elif '```' in result:
                    result = result.split('```')[1].split('```')[0]
                
                # Try to parse JSON
                try:
                    cv_data = json.loads(result)
                    
                    # Add some defaults and processing
                    cv_data['availability'] = getattr(config, 'availability', 'Immediately')
                    cv_data['salary_expectation'] = getattr(config, 'salary_expectation', 'As per company standards')
                    cv_data['notice_period'] = getattr(config, 'notice_period', '30 days')
                    cv_data['visa_status'] = getattr(config, 'visa_status', 'Indian Citizen')
                    cv_data['willing_to_relocate'] = getattr(config, 'willing_to_relocate', True)
                    
                    # Ensure experience_years is set properly
                    if not cv_data.get('experience_years') or cv_data['experience_years'] == '0':
                        cv_data['experience_years'] = str(getattr(config, 'experience_years', '4'))
                    
                    # Ensure skills is a list
                    if isinstance(cv_data.get('skills'), str):
                        cv_data['skills'] = [skill.strip() for skill in cv_data['skills'].split(',')]
                    
                    return cv_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing AI response as JSON: {e}")
                    print(f"AI Response: {result[:200]}...")
                    
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error parsing CV with AI: {e}")
        
        # Fallback to manual parsing
        return self.manual_cv_parsing()
    
    def manual_cv_parsing(self):
        """Fallback manual CV parsing using regex and keywords"""
        cv_data = {
            "name": "",
            "email": "",
            "phone": "",
            "experience_years": "0",
            "current_title": "",
            "skills": [],
            "education": "",
            "location": "",
            "certifications": [],
            "languages": [],
            "previous_companies": [],
            "projects": [],
            "achievements": [],
            "linkedin_url": "",
            "github_url": "",
            "portfolio_url": ""
        }
        
        import re
        text = self.cv_text.lower()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, self.cv_text, re.IGNORECASE)
        if emails:
            cv_data['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'[\+]?[1-9]?[0-9]{1,4}[\s-]?[\(]?[0-9]{1,4}[\)]?[\s-]?[0-9]{1,4}[\s-]?[0-9]{1,9}'
        phones = re.findall(phone_pattern, self.cv_text)
        if phones:
            cv_data['phone'] = phones[0]
        
        # Extract skills using common tech keywords
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'nodejs', 'express',
            'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'html', 'css', 'bootstrap',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
            'linux', 'windows', 'mac', 'api', 'rest', 'graphql', 'microservices',
            'machine learning', 'deep learning', 'ai', 'data science', 'analytics'
        ]
        
        found_skills = []
        for skill in tech_skills:
            if skill in text:
                found_skills.append(skill.title())
        
        cv_data['skills'] = found_skills or getattr(config, 'skills', ['Python', 'JavaScript', 'SQL'])
        
        # Extract experience years (look for patterns like "3 years", "5+ years")
        exp_pattern = r'(\d+)[\+]?\s*year[s]?\s*(?:of\s+)?(?:experience|exp)'
        exp_matches = re.findall(exp_pattern, text)
        if exp_matches:
            cv_data['experience_years'] = str(max(exp_matches, key=int))
        else:
            # Fallback to config or default
            cv_data['experience_years'] = str(getattr(config, 'experience_years', '4'))
        
        # Set defaults from config if available
        cv_data['name'] = getattr(config, 'full_name', 'Your Name')
        cv_data['location'] = getattr(config, 'location', 'India')
        cv_data['current_title'] = getattr(config, 'current_title', 'Software Developer')
        cv_data['education'] = getattr(config, 'education', 'Bachelor in Computer Science')
        
        return cv_data
    


    def simple_ai_answer(self, question, options=None, error_message=""):
        """Simple AI that returns exact answers for LinkedIn forms with adaptive human-like logic"""
        try:
            # Handle specific error message formats first
            if error_message:
                print(f"🔍 Error format: {error_message}")
                
                # Handle whole number between 0 and 99
                if "whole number between 0 and 99" in error_message.lower():
                    # For experience questions, use reasonable experience years
                    if any(word in question.lower() for word in ['experience', 'years', 'terraform', 'helm', 'kubernetes']):
                        exp_years = self.cv_data.get('experience_years', '4')
                        # Ensure it's between 0-99
                        try:
                            years = min(max(int(exp_years), 0), 99)
                            return str(years)
                        except:
                            return "3"  # Safe default
                    return "2"  # Default for other fields
                
                # Handle decimal number larger than 0.0
                elif "decimal number larger than 0.0" in error_message.lower():
                    if any(word in question.lower() for word in ['experience', 'years']):
                        exp_years = self.cv_data.get('experience_years', '4')
                        try:
                            years = max(float(exp_years), 0.1)  # Ensure > 0.0
                            return str(years)
                        except:
                            return "3.0"  # Safe default
                    return "1.5"  # Default decimal
                
                # Handle notice period format
                elif "notice" in question.lower() and any(word in error_message.lower() for word in ['number', 'days']):
                    return "20"  # Standard 20 days notice

            # ADAPTIVE HUMAN-LIKE LOGIC: Be strategic about answers to get shortlisted
            
            # Handle Yes/No dropdowns with strategic logic based on config
            if options and len(options) <= 4:
                yes_options = [opt for opt in options if opt.lower().strip() in ['yes', 'true']]
                no_options = [opt for opt in options if opt.lower().strip() in ['no', 'false']]
                
                if yes_options and no_options:
                    print(f"🤖 Yes/No dropdown detected - Being strategic...")
                    
                    # VISA/SPONSORSHIP questions - Answer based on config visa_status
                    visa_status = getattr(config, 'visa_status', 'Indian Citizen')
                    
                    if any(word in question.lower() for word in ['authorized', 'eligible', 'citizen']):
                        # Work authorization based on visa status
                        if any(status in visa_status.lower() for status in ['us citizen', 'american citizen', 'green card', 'permanent resident']):
                            print(f"🔍 Work authorization question - {visa_status} -> Yes")
                            return yes_options[0]
                        else:
                            print(f"🔍 Work authorization question - {visa_status} needs authorization -> No")
                            return no_options[0]
                        
                    elif 'visa' in question.lower() and 'sponsor' in question.lower():
                        # Visa sponsorship based on visa status
                        if any(status in visa_status.lower() for status in ['us citizen', 'american citizen', 'green card', 'permanent resident']):
                            print(f"🔍 Visa sponsorship question - {visa_status} doesn't need sponsorship -> No")
                            return no_options[0]
                        else:
                            print(f"🔍 Visa sponsorship question - {visa_status} needs sponsorship -> Yes")
                            return yes_options[0]
                    
                    # TECHNICAL SKILLS questions - Always YES if we have experience
                    elif any(tech in question.lower() for tech in [
                        'python', 'javascript', 'typescript', 'react', 'next.js', 'node.js',
                        'fastapi', 'django', 'flask', 'express', 'mongodb', 'postgresql',
                        'mysql', 'redis', 'docker', 'kubernetes', 'aws', 'azure', 'git',
                        'html', 'css', 'bootstrap', 'tailwind', 'sql', 'nosql', 'rest',
                        'api', 'graphql', 'microservices', 'backend', 'frontend', 'fullstack'
                    ]):
                        print(f"🔍 Technical skill question detected -> Yes (have experience)")
                        return yes_options[0]
                    
                    # EDUCATION questions - Usually YES for bachelor's degree
                    elif any(word in question.lower() for word in ['bachelor', 'degree', 'graduate', 'education']):
                        print(f"🔍 Education question -> Yes (have degree)")
                        return yes_options[0]
                    
                    # EXPERIENCE/YEARS questions - YES if we have the experience
                    elif any(word in question.lower() for word in ['experience', 'years', 'worked']):
                        print(f"🔍 Experience question -> Yes (have experience)")
                        return yes_options[0]
                    
                    # REMOTE/WFH questions - YES (more opportunities)
                    elif any(word in question.lower() for word in ['remote', 'work from home', 'wfh', 'hybrid']):
                        print(f"🔍 Remote work question -> Yes (flexible)")
                        return yes_options[0]
                    
                    # RELOCATION questions - Based on config
                    elif any(word in question.lower() for word in ['relocate', 'move', 'willing to travel']):
                        willing_to_relocate = getattr(config, 'willing_to_relocate', True)
                        if willing_to_relocate:
                            print(f"🔍 Relocation question -> Yes (willing to relocate)")
                            return yes_options[0]
                        else:
                            print(f"🔍 Relocation question -> No (not willing to relocate)")
                            return no_options[0]
                    
                    # DEFAULT: For most other questions, say YES to increase chances
                    else:
                        print(f"🔍 General Yes/No question -> Yes (default positive)")
                        return yes_options[0]
            # Handle phone number fields
            if any(word in question.lower() for word in ['phone', 'mobile', 'number', 'contact']):
                if 'country' in question.lower() and options:
                    # Return India country code option
                    for option in options:
                        if 'india' in option.lower() and '+91' in option:
                            return option
                else:
                    # Return actual phone number without country code
                    phone = getattr(config, 'phone_number', '+91-9876543210')
                    # Remove country code if present for phone number field
                    if phone.startswith('+91'):
                        return phone[3:].replace('-', '')  # Remove +91 and dashes
                    return phone.replace('-', '')
            
            # Handle notice period questions with smart format detection
            if any(word in question.lower() for word in ['notice', 'joining', 'availability', 'when can you start']):
                notice_period = getattr(config, 'notice_period', '30 days')
                
                # If error message doesn't specify numeric format, it's likely a text field
                if error_message and not any(word in error_message.lower() for word in ['number', 'decimal', 'integer', 'digit', 'numeric']):
                    # Text field - provide full formatted response
                    return notice_period
                else:
                    # Numeric field - extract just the number
                    numbers = re.findall(r'\d+', notice_period)
                    if numbers:
                        return numbers[0]
                    return "30"  # fallback
            
            # Handle salary questions with smart currency and format detection
            if any(word in question.lower() for word in ['salary', 'ctc', 'compensation', 'pay', 'wage']):
                current_salary = getattr(config, 'current_salary', '18')  # INR LPA
                expected_salary = getattr(config, 'salary_expectation', '27')  # INR LPA
                
                # Detect currency context
                is_usd = 'usd' in question.lower() or '$' in question.lower() or 'dollar' in question.lower()
                is_inr = 'inr' in question.lower() or '₹' in question.lower() or 'rupee' in question.lower() or 'lpa' in question.lower()
                is_monthly = 'month' in question.lower() or 'monthly' in question.lower()
                is_yearly = 'year' in question.lower() or 'yearly' in question.lower() or 'annual' in question.lower()
                
                # Determine which salary to use
                if 'current' in question.lower():
                    base_salary = float(current_salary)
                else:
                    base_salary = float(expected_salary)
                
                # Smart format detection based on error message and context
                if error_message:
                    error_lower = error_message.lower()
                    # If error doesn't specify number format, it's likely a text field
                    if not any(word in error_lower for word in ['number', 'decimal', 'integer', 'digit', 'numeric']):
                        # Text field - provide formatted response
                        if is_usd:
                            if is_monthly:
                                usd_monthly = int((base_salary * 100000) / (12 * 83))
                                return f"${usd_monthly:,} per month"
                            else:
                                usd_yearly = int((base_salary * 100000) / 83)
                                return f"${usd_yearly:,} per year"
                        else:
                            if is_monthly:
                                inr_monthly = int((base_salary * 100000) / 12)
                                return f"₹{inr_monthly:,} per month"
                            else:
                                inr_lpa = base_salary
                                return f"₹{inr_lpa} LPA"
                
                # For numeric fields or when no specific format detected
                if is_usd:
                    if is_monthly:
                        usd_monthly = int((base_salary * 100000) / (12 * 83))
                        return str(usd_monthly)
                    else:
                        usd_yearly = int((base_salary * 100000) / 83)
                        return str(usd_yearly)
                elif is_inr:
                    if is_monthly:
                        inr_monthly = int((base_salary * 100000) / 12)
                        return str(inr_monthly)
                    else:
                        return str(int(base_salary))
                else:
                    # Default based on context - if no currency specified, assume text field and add appropriate currency
                    if not options:  # Text field
                        return f"₹{base_salary} LPA"
                    else:
                        return str(int(base_salary))
            
            # Handle location questions - return exact option from dropdown
            if any(word in question.lower() for word in ['location', 'city', 'country', 'phone country', 'where', 'address']):
                my_location = self.cv_data.get('location', 'Bangalore, India')
                
                if options:
                    # For location dropdowns, find the best matching option
                    if 'phone' in question.lower() or 'country code' in question.lower():
                        # Phone country code - look for India
                        for option in options:
                            if 'india' in option.lower() and '+91' in option:
                                return option
                    else:
                        # City/location - look for Indian cities or Bangalore
                        for option in options:
                            if any(city in option.lower() for city in ['bangalore', 'bengaluru', 'mumbai', 'delhi', 'india']):
                                return option
                        # If no Indian city found, just return the location from CV
                        return my_location
                else:
                    # For autocomplete location fields, return a clear city name
                    return 'Bangalore'  # Simple, clear location that will match autocomplete
            
            # Create a focused prompt for exact answers
            cv_info = f"""
My Profile:
- Name: {self.cv_data.get('name', 'Aman Kumar')} 
- Experience: {self.cv_data.get('experience_years', '4')} years
- Location: {self.cv_data.get('location', 'India')}
- Current Salary: {getattr(config, 'current_salary', '18')} LPA
- Expected Salary: {getattr(config, 'salary_expectation', '27')} LPA
- Visa Status: Indian Citizen (need sponsorship)
- Education: Bachelor's Degree
- English: Professional level
- Willing to relocate: Yes
"""

            if options:
                prompt = f"""{cv_info}

Question: {question}
Available options: {options}

Return ONLY the exact option text that matches best. Nothing else.
For Yes/No: Return "Yes" or "No"  
For experience: Return the number like "4"
For salary: Return number only
For dropdowns: Return exact option text
"""
            else:
                # Determine if this is likely a text field or numeric field based on error message
                is_text_field = True
                if error_message:
                    error_lower = error_message.lower()
                    if any(word in error_lower for word in ['number', 'decimal', 'integer', 'digit', 'numeric']):
                        is_text_field = False
                
                if is_text_field:
                    prompt = f"""{cv_info}

Question: {question}
{f"Validation Error Context: {error_message}" if error_message else ""}

This appears to be a text input field. Provide a complete, professional answer.
Examples:
- Experience questions: "4 years of experience in Python development"
- Salary questions: "₹27 LPA" or "$65,000 per year" 
- Notice period: "30 days notice period"
- Skills: "Python, JavaScript, React, SQL"
- Text descriptions: Keep professional and relevant, max 100 characters
"""
                else:
                    prompt = f"""{cv_info}

Question: {question}
{f"Validation Error Context: {error_message}" if error_message else ""}

This appears to be a numeric input field. Return ONLY the number.
Examples:
- Experience questions: "4"
- Salary questions: "27" or "65000"
- Notice period: "30"
- Years: Just the number
"""

            response = requests.post(f"{self.ollama_url}/api/generate", 
                                   json={
                                       "model": self.model,
                                       "prompt": prompt,
                                       "stream": False,
                                       "options": {"temperature": 0.1}
                                   }, timeout=20)
            
            if response.status_code == 200:
                result = response.json()['response'].strip()
                # Clean up the response
                result = result.replace('"', '').replace("'", "").strip()
                return result
                
        except Exception as e:
            print(f"💥 AI Error: {e}")
            # Smart fallbacks
            if 'experience' in question.lower() or 'years' in question.lower():
                return '4'
            elif any(word in question.lower() for word in ['authorized', 'eligible', 'citizen']):
                return 'No'  # Indian citizen needs sponsorship
            elif 'visa' in question.lower() and 'sponsor' in question.lower():
                return 'Yes'  # Need sponsorship
            elif any(word in question.lower() for word in ['bachelor', 'degree']):
                return 'Yes'
            elif 'english' in question.lower() or 'language' in question.lower():
                return 'Professional'
            return 'Yes'  # Default positive answer

    def query_ollama(self, question, context=""):
        """Wrapper for simple_ai_answer - for backward compatibility"""
        return self.simple_ai_answer(question,context)
    
    def generate_cover_letter(self, job_title, company_name, job_description=""):
        """Generate a cover letter for the position"""
        prompt = f"""
Write a professional cover letter for the position of {job_title} at {company_name}.
Keep it concise (max 300 words) and professional.

Job Description: {job_description[:500]}...

Candidate Info:
- Name: {self.cv_data['name']}
- Experience: {self.cv_data['experience_years']} years as {self.cv_data['current_title']}
- Key Skills: {', '.join(self.cv_data['skills'][:5])}
- Education: {self.cv_data['education']}

Make it personalized and engaging but professional.
"""
        return self.query_ollama(prompt)

class StealthLinkedin:
    def __init__(self):
        browser = config.browser[0].lower()
        linkedinEmail = config.email
        
        # Initialize AI Agent with CV analysis
        cv_path = getattr(config, 'cv_path', 'cv.pdf')  # Allow custom CV path in config
        self.ai_agent = AIAgent(cv_path=cv_path)
        
        if browser == "firefox":
            self.setup_firefox_driver()
        elif browser == "chrome":
            self.setup_chrome_driver()
        
        if len(linkedinEmail) > 0:
            self.stealth_login(linkedinEmail)
    
    def setup_firefox_driver(self):
        """Setup Firefox with stealth options"""
        options = Options()
        
        # Disable automation indicators
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("general.useragent.override", 
                             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0")
        
        # Additional privacy settings
        options.set_preference("privacy.trackingprotection.enabled", False)
        options.set_preference("geo.enabled", False)
        options.set_preference("media.navigator.enabled", False)
        
        # Performance and stealth
        options.set_preference("javascript.enabled", True)
        options.set_preference("network.http.use-cache", True)
        
        self.driver = webdriver.Firefox(options=options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def setup_chrome_driver(self):
        """Setup Chrome with stealth options"""
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        
        options = ChromeOptions()
        
        # Basic stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        
        # Options to prevent background mode and keep window active
        options.add_argument("--disable-background-mode")
        options.add_argument("--disable-backgrounding-occluded-windows") 
        options.add_argument("--disable-renderer-backgrounding")
        
        # User agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Maximize window to ensure it's visible
        self.driver.maximize_window()
        
    def human_like_delay(self, min_delay=1, max_delay=3):
        """More realistic delays that mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def human_like_typing(self, element, text, typing_delay=0.1):
        """Type with human-like delays between characters"""
        try:
            # Ensure element is in view and interactable
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.human_like_delay(0.5, 1)
            
            # Bring window to focus if possible
            self.driver.execute_script("window.focus();")
            
            # Click to focus the element
            element.click()
            self.human_like_delay(0.2, 0.5)
            
            element.clear()
            self.human_like_delay(0.2, 0.5)
            
            for char in str(text):
                element.send_keys(char)
                time.sleep(random.uniform(0.05, typing_delay))
        except Exception as e:
            print(f"⚠️ Typing error: {e}")
            # Fallback: try direct send_keys
            try:
                element.clear()
                element.send_keys(str(text))
            except:
                pass
    
    def random_mouse_movement(self):
        """Add random mouse movements to appear more human"""
        try:
            action = ActionChains(self.driver)
            # Move to random coordinates
            x = random.randint(100, 500)
            y = random.randint(100, 400)
            action.move_by_offset(x, y).perform()
            time.sleep(0.5)
            action.move_by_offset(-x, -y).perform()
        except:
            pass
    
    def ensure_window_focus(self):
        """Ensure the browser window has focus and is visible"""
        try:
            self.driver.execute_script("window.focus();")
            # Try to bring window to front (platform specific)
            if platform.system() == "Darwin":  # macOS
                os.system("osascript -e 'tell application \"Chrome\" to activate'")
            elif platform.system() == "Windows":
                try:
                    import win32gui
                    hwnd = win32gui.FindWindow(None, self.driver.title)
                    win32gui.SetForegroundWindow(hwnd)
                except ImportError:
                    pass  # win32gui not available
        except:
            pass  # Fallback: just continue without focus management

    def safe_element_interaction(self, element, action_type="click", text=None):
        """Safely interact with elements, handling focus and visibility issues"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                print(f"🔄 Safe interaction attempt {attempt + 1} - {action_type} on {element.tag_name}" + (f" with text '{text}'" if text else ""))
                
                # Ensure window is active and visible
                self.ensure_window_focus()
                
                # Handle any overlays or modals that might be blocking
                # self.handle_overlays()
                
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
                self.human_like_delay(0.5, 1)
                
                # Wait for element to be interactable
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.element_to_be_clickable(element))
                
                # Additional check - ensure element is not obscured
                is_obscured = self.driver.execute_script("""
                    var elem = arguments[0];
                    var rect = elem.getBoundingClientRect();
                    var centerX = rect.left + rect.width / 2;
                    var centerY = rect.top + rect.height / 2;
                    var topElement = document.elementFromPoint(centerX, centerY);
                    return topElement !== elem && !elem.contains(topElement);
                """, element)
                
                if is_obscured:
                    print(f"   ⚠️ Element appears to be obscured, trying JavaScript interaction")
                    if action_type == "click":
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    elif action_type == "select" and text:
                        # Direct JavaScript selection
                        result = self.driver.execute_script("""
                            var select = arguments[0];
                            var text = arguments[1];
                            for(var i = 0; i < select.options.length; i++) {
                                if(select.options[i].text.trim() === text.trim()) {
                                    select.selectedIndex = i;
                                    select.dispatchEvent(new Event('change', {bubbles: true}));
                                    return true;
                                }
                            }
                            return false;
                        """, element, str(text))
                        return result
                
                if action_type == "click":
                    element.click()
                elif action_type == "type" and text:
                    element.click()
                    self.human_like_delay(0.2, 0.5)
                    element.clear()
                    self.human_like_delay(0.2, 0.5)
                    element.send_keys(str(text))
                elif action_type == "select" and text:
                    print(f"🔍 Creating Select object for element: {element.tag_name}")
                    select = Select(element)
                    print(f"🔍 Available options: {[opt.text.strip() for opt in select.options]}")
                    print(f"🔍 Attempting to select: '{text}'")
                    select.select_by_visible_text(text)
                    print(f"✅ Successfully selected: '{text}'")
                    
                return True
                
            except Exception as e:
                print(f"⚠️ Safe interaction attempt {attempt + 1} failed ({action_type}): {e}")
                
                if attempt < max_attempts - 1:
                    self.human_like_delay(1, 2)
                    continue
                
                # Final fallback: JavaScript interaction
                try:
                    print(f"🔄 Trying JavaScript fallback for {action_type}...")
                    self.ensure_window_focus()
                    
                    if action_type == "click":
                        self.driver.execute_script("arguments[0].click();", element)
                    elif action_type == "type" and text:
                        self.driver.execute_script("arguments[0].focus();", element)
                        self.driver.execute_script("arguments[0].value = '';", element)
                        self.driver.execute_script("arguments[0].value = arguments[1];", element, str(text))
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", element)
                        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", element)
                    elif action_type == "select" and text:
                        print(f"🔄 JavaScript select fallback - looking for: '{text}'")
                        options_text = self.driver.execute_script("""
                            var select = arguments[0];
                            var options = [];
                            for(var i = 0; i < select.options.length; i++) {
                                options.push(select.options[i].text.trim());
                            }
                            return options;
                        """, element)
                        print(f"🔍 JS available options: {options_text}")
                        
                        result = self.driver.execute_script("""
                            var select = arguments[0];
                            var text = arguments[1];
                            var found = false;
                            for(var i = 0; i < select.options.length; i++) {
                                if(select.options[i].text.trim() === text.trim()) {
                                    select.selectedIndex = i;
                                    select.dispatchEvent(new Event('change', {bubbles: true}));
                                    found = true;
                                    break;
                                }
                            }
                            return found;
                        """, element, str(text))
                        
                        if result:
                            print(f"✅ JavaScript select successful: '{text}'")
                        else:
                            print(f"❌ JavaScript select failed - option '{text}' not found")
                        
                    print(f"✅ JavaScript fallback succeeded ({action_type})")
                    return True
                except Exception as fallback_error:
                    print(f"❌ JavaScript fallback also failed ({action_type}): {fallback_error}")
                    return False

    # def handle_overlays(self):
        """Handle any overlays or modals that might be blocking interactions"""
        try:
            # Look for common overlay patterns
            overlay_selectors = [
                ".search-typeahead-v2__hit",
                ".artdeco-modal-overlay",
                ".typeahead-results",
                "[data-test-single-typeahead-entity-form-search-result]"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlays = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for overlay in overlays:
                        if overlay.is_displayed():
                            # Try to click elsewhere to dismiss
                            self.driver.execute_script("arguments[0].style.display = 'none';", overlay)
                            print(f"🔄 Dismissed overlay: {selector}")
                except:
                    continue
                    
            # Small delay to let overlays disappear
            self.human_like_delay(0.5, 1)
            
        except Exception as e:
            print(f"⚠️ Error handling overlays: {e}")
    
    def stealth_login(self, email):
        """Login with human-like behavior"""
        try:
            self.driver.get("https://www.linkedin.com")
            self.human_like_delay(2, 4)
            
            # Sometimes browse a bit before logging in
            if random.choice([True, False]):
                sign_in_link = self.driver.find_element(By.LINK_TEXT, "Sign in")
                sign_in_link.click()
            else:
                self.driver.get("https://www.linkedin.com/login")
            
            self.human_like_delay(3, 5)
            
            # Find and fill username
            username_field = self.driver.find_element(By.ID, "username")
            self.random_mouse_movement()
            username_field.click()
            self.human_like_delay(0.5, 1.5)
            self.human_like_typing(username_field, email)
            
            self.human_like_delay(1, 2)
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.click()
            self.human_like_delay(0.5, 1.5)
            self.human_like_typing(password_field, config.password)
            
            self.human_like_delay(2, 4)
            
            # Submit form
            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()
            
            self.human_like_delay(5, 8)
            
            # Check if login was successful or if there's a challenge
            current_url = self.driver.current_url
            if "challenge" in current_url or "checkpoint" in current_url:
                print("⚠️ LinkedIn security challenge detected. Please solve it manually.")
                input("Press Enter after solving the challenge...")
                
        except Exception as e:
            print(f"Login error: {e}")

    def fill_form_field(self, element, question_text, job_context="", force_fill=False):
        """Fill form field using AI agent with flexible input type handling"""
        try:
            # Check if field already has a value
            current_value = element.get_attribute('value')
            tag_name = element.tag_name.lower()
            
            # For select elements, check if a meaningful option is selected
            if tag_name == "select":
                try:
                    select = Select(element)
                    selected_option = select.first_selected_option.text.strip()
                    if selected_option and selected_option.lower() not in ['select', 'choose', 'please select', '', '--']:
                        print(f"⏭️ Dropdown already has selection: {selected_option}")
                        return False
                except:
                    pass
            elif current_value and current_value.strip() and not force_fill:
                print(f"⏭️ Field already filled: {question_text[:30]}... -> {current_value[:20]}...")
                return False
            
            print(f"🔧 Attempting to fill: {question_text[:50]}...")
            
            # Get AI response with input type intelligence
            ai_response = self.ai_agent.query_ollama(question_text, job_context)
            
            if ai_response:
                print(f"🤖 AI Response: {ai_response[:50]}...")
                
                # Check element type
                input_type = element.get_attribute('type') if tag_name == 'input' else None
                
                if tag_name == "select":
                    # Handle dropdown selection with better matching
                    return self.handle_dropdown_selection(element, question_text, ai_response, job_context)
                        
                elif input_type == "radio":
                    # Handle radio button groups
                    return self.handle_radio_selection(element, question_text, ai_response, job_context)
                    
                elif input_type == "checkbox":
                    # Handle checkboxes with better logic
                    return self.handle_checkbox_selection(element, question_text, ai_response)
                    
                elif input_type == "number" or any(word in question_text.lower() for word in ['years', 'experience', 'age']):
                    # Handle numeric inputs
                    return self.handle_numeric_input(element, question_text, ai_response)
                    
                elif input_type in ["text", "email", "tel"] or tag_name == "textarea":
                    # Check if this is a location/city field that needs special handling
                    if any(word in question_text.lower() for word in ['location', 'city', 'where', 'based']):
                        return self.handle_location_field(element, question_text, ai_response)
                    else:
                        # Handle regular text inputs
                        return self.handle_text_input(element, question_text, ai_response, tag_name)
                    
                else:
                    # Default text handling
                    return self.handle_text_input(element, question_text, ai_response, tag_name)
            else:
                print(f"❌ No AI response for: {question_text[:30]}...")
                    
            return False
                
        except Exception as e:
            print(f"❌ Error filling field '{question_text[:30]}...': {e}")
            return False

    def handle_dropdown_selection(self, element, question_text, ai_response, job_context):
        """Simplified dropdown selection - more reliable"""
        try:
            print(f"🔄 Dropdown: {question_text[:50]}...")
            
            select = Select(element)
            all_options = select.options
            # remove 0th if it's a placeholder like "Select", "Choose", etc.
            if all_options and all_options[0].text.strip().lower() in ['select', 'choose', 'please select', 'pick one', '--']:
                all_options = all_options[1:]
            options = [opt.text.strip() for opt in all_options if opt.text.strip()]
            
            if not options:
                print(f"❌ No options found")
                return False
            
            print(f"📋 Options: {options}")
            print(f"🤖 AI says: {ai_response}")
            
            # 1. Try exact match first
            for option in all_options:
                option_text = option.text.strip()
                if option_text.lower() == ai_response.strip().lower():
                    print(f"🎯 Exact match: {option_text}")
                    try:
                        select.select_by_visible_text(option_text)
                        print(f"✅ Selected: {option_text}")
                        return True
                    except Exception as e:
                        print(f"❌ Selection failed: {e}")
                        continue
            
            # 2. Smart matching for common scenarios
            question_lower = question_text.lower()
            ai_lower = ai_response.lower()
            
            # Experience years
            if 'experience' in question_lower or 'years' in question_lower:
                exp_years = self.ai_agent.cv_data.get('experience_years', '4')
                for option in all_options:
                    opt_text = option.text.strip()
                    if exp_years in opt_text or (exp_years + ' year' in opt_text):
                        try:
                            select.select_by_visible_text(opt_text)
                            print(f"✅ Selected experience: {opt_text}")
                            return True
                        except:
                            continue
            
            # Yes/No questions
            yes_options = [opt for opt in all_options if opt.text.strip().lower() in ['yes', 'true']]
            no_options = [opt for opt in all_options if opt.text.strip().lower() in ['no', 'false']]
            
            if yes_options or no_options:
                should_say_yes = any(word in ai_lower for word in ['yes', 'true', 'authorized', 'eligible', 'willing', 'comfortable'])
                
                if should_say_yes and yes_options:
                    try:
                        select.select_by_visible_text(yes_options[0].text.strip())
                        print(f"✅ Selected Yes: {yes_options[0].text.strip()}")
                        return True
                    except:
                        pass
                elif not should_say_yes and no_options:
                    try:
                        select.select_by_visible_text(no_options[0].text.strip())
                        print(f"✅ Selected No: {no_options[0].text.strip()}")
                        return True
                    except:
                        pass
            
            # Language proficiency
            if any(word in question_lower for word in ['english', 'language', 'proficiency']):
                prof_options = ['Professional', 'Native', 'Fluent', 'Advanced']
                for prof_level in prof_options:
                    matching_opts = [opt for opt in all_options if prof_level.lower() in opt.text.lower()]
                    if matching_opts:
                        try:
                            select.select_by_visible_text(matching_opts[0].text.strip())
                            print(f"✅ Selected proficiency: {matching_opts[0].text.strip()}")
                            return True
                        except:
                            continue
            
            # 3. Fallback: Select first non-empty, non-default option
            skip_options = ['select', 'choose', 'please select', 'pick one', '', '--', 'none']
            for option in all_options:
                opt_text = option.text.strip()
                if opt_text and opt_text.lower() not in skip_options:
                    try:
                        select.select_by_visible_text(opt_text)
                        print(f"⚠️ Fallback selection: {opt_text}")
                        return True
                    except:
                        continue
            
            print(f"❌ Could not select any option")
            return False
            
        except Exception as e:
            print(f"❌ Dropdown error: {e}")
            return False

    def handle_radio_selection(self, element, question_text, ai_response, job_context):
        """Handle radio button selections"""
        try:
            name = element.get_attribute('name')
            if not name:
                # Try to find radio group by looking at nearby elements
                parent = element.find_element(By.XPATH, "./..")
                radio_group = parent.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            else:
                radio_group = self.driver.find_elements(By.CSS_SELECTOR, f"input[type='radio'][name='{name}']")
            
            options = []
            
            for radio in radio_group:
                if radio.is_displayed():
                    # Try multiple ways to get the radio button label
                    label = None
                    
                    # Method 1: Check for associated label
                    radio_id = radio.get_attribute('id')
                    if radio_id:
                        try:
                            label_elem = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                            label = label_elem.text.strip()
                        except:
                            pass
                    
                    # Method 2: Look for label in parent element
                    if not label:
                        try:
                            parent = radio.find_element(By.XPATH, "./..")
                            # Look for span or div with text near the radio button
                            text_elements = parent.find_elements(By.CSS_SELECTOR, "span, div, label")
                            for elem in text_elements:
                                text = elem.text.strip()
                                if text and len(text) < 20 and text.lower() in ['yes', 'no']:
                                    label = text
                                    break
                        except:
                            pass
                    
                    # Method 3: Use value attribute as fallback
                    if not label:
                        label = radio.get_attribute('value') or ""
                    
                    if label:
                        options.append((radio, label))
            
            if not options:
                print(f"⚠️ No radio options found for: {question_text[:30]}...")
                return False
            
            print(f"🔍 Radio options for '{question_text[:50]}...': {[label for _, label in options]}")
            
            # Handle common yes/no questions directly based on question content
            question_lower = question_text.lower()
            ai_lower = ai_response.lower()
            
            # Handle work authorization and visa questions based on visa status
            visa_status = self.ai_agent.cv_data.get('visa_status', 'Indian Citizen')
            
            # For work authorization questions  
            if 'authorized' in question_lower or 'eligible' in question_lower:
                # If US/Canadian citizen or green card holder -> Yes
                # If international (Indian, etc.) -> No (need sponsorship)
                if any(status in visa_status.lower() for status in ['us citizen', 'american citizen', 'green card', 'permanent resident']):
                    target_answer = 'yes'
                else:
                    target_answer = 'no'  # International citizens need authorization
                print(f"🔍 Work authorization question - visa status: {visa_status} -> answering {target_answer}")
                
            # For visa sponsorship questions  
            elif 'visa' in question_lower and 'sponsor' in question_lower:
                # If US/Canadian citizen or green card holder -> No (don't need sponsorship)
                # If international (Indian, etc.) -> Yes (need sponsorship)
                if any(status in visa_status.lower() for status in ['us citizen', 'american citizen', 'green card', 'permanent resident']):
                    target_answer = 'no'
                else:
                    target_answer = 'yes'  # International citizens need sponsorship
                print(f"🔍 Visa sponsorship question - visa status: {visa_status} -> answering {target_answer}")
            else:
                # Use AI response for other questions
                if any(word in ai_lower for word in ['yes', 'true', 'agree', 'accept']):
                    target_answer = 'yes'
                elif any(word in ai_lower for word in ['no', 'false', 'disagree', 'decline']):
                    target_answer = 'no'
                else:
                    target_answer = None
            
            # Find and click the matching radio button with enhanced clicking
            if target_answer:
                for radio, label in options:
                    if target_answer.lower() == label.lower():
                        if self.enhanced_radio_click(radio, label):
                            print(f"✅ Selected radio ({target_answer}): {label}")
                            return True
            
            # Ask AI to choose from radio options
            option_texts = [label for _, label in options]
            choice_prompt = f"Question: {question_text}\nAvailable options: {', '.join(option_texts)}\nBased on profile: {ai_response}\n\nSelect EXACTLY one option:"
            chosen_option = self.ai_agent.query_ollama(choice_prompt, job_context)
            
            if chosen_option:
                print(f"🤖 AI chose: {chosen_option}")
                
                # Find best matching radio button with improved scoring
                best_match = None
                best_score = 0
                
                for radio, label in options:
                    score = 0
                    chosen_words = chosen_option.lower().split()
                    label_words = label.lower().split()
                    
                    # Exact match gets highest score
                    if chosen_option.lower() == label.lower():
                        score = 100
                    # Partial matches
                    elif chosen_option.lower() in label.lower() or label.lower() in chosen_option.lower():
                        score = 50
                    # Word matches
                    else:
                        common_words = set(chosen_words) & set(label_words)
                        score = len(common_words) * 10
                        
                        # Individual word matches
                        for word in chosen_words:
                            if word in label.lower():
                                score += len(word)
                    
                    if score > best_score:
                        best_match = radio
                        best_score = score
                
                if best_match:
                    # Find the label for the best match
                    best_label = next(label for radio, label in options if radio == best_match)
                    if self.enhanced_radio_click(best_match, best_label):
                        print(f"✅ Selected radio (score {best_score}): {best_label}")
                        return True
            
            # Fallback: select first option
            if options:
                first_radio, first_label = options[0]
                if self.enhanced_radio_click(first_radio, first_label):
                    print(f"⚠️ Fallback radio selection: {first_label}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Radio error for '{question_text[:30]}...': {e}")
            return False

    def enhanced_radio_click(self, radio_element, label_text):
        """Enhanced radio button clicking with multiple strategies"""
        try:
            print(f"🔄 Attempting to click radio: {label_text}")
            
            # Strategy 1: Direct click on radio button
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio_element)
                self.human_like_delay(0.5, 1)
                
                # Try clicking the radio directly
                radio_element.click()
                print(f"✅ Direct radio click successful")
                return True
            except Exception as e:
                print(f"⚠️ Direct radio click failed: {e}")
            
            # Strategy 2: Click via JavaScript
            try:
                self.driver.execute_script("arguments[0].click();", radio_element)
                print(f"✅ JavaScript radio click successful")
                return True
            except Exception as e:
                print(f"⚠️ JavaScript radio click failed: {e}")
            
            # Strategy 3: Click associated label
            try:
                radio_id = radio_element.get_attribute('id')
                if radio_id:
                    label_elem = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                    label_elem.click()
                    print(f"✅ Label click successful")
                    return True
            except Exception as e:
                print(f"⚠️ Label click failed: {e}")
            
            # Strategy 4: Click parent container
            try:
                parent = radio_element.find_element(By.XPATH, "./..")
                parent.click()
                print(f"✅ Parent container click successful")
                return True
            except Exception as e:
                print(f"⚠️ Parent click failed: {e}")
            
            # Strategy 5: Use ActionChains
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(radio_element).click().perform()
                print(f"✅ ActionChains click successful")
                return True
            except Exception as e:
                print(f"⚠️ ActionChains click failed: {e}")
            
            print(f"❌ All radio click strategies failed for: {label_text}")
            return False
            
        except Exception as e:
            print(f"❌ Enhanced radio click error: {e}")
            return False

    def handle_checkbox_selection(self, element, question_text, ai_response):
        """Enhanced checkbox handling"""
        try:
            print(f"☑️ Checkbox: {question_text[:50]}...")
            
            # Agreement checkboxes - always check
            agreement_keywords = ['terms', 'conditions', 'privacy', 'policy', 'agree', 'understand', 'declare']
            if any(word in question_text.lower() for word in agreement_keywords):
                if not element.is_selected():
                    return self.enhanced_checkbox_click(element, "agreement checkbox")
                return True
            
            # Other checkboxes - check if AI says yes
            should_check = any(word in ai_response.lower() for word in ['yes', 'true', 'willing', 'authorized'])
            
            if should_check and not element.is_selected():
                return self.enhanced_checkbox_click(element, f"AI response: {ai_response[:30]}")
            elif element.is_selected():
                print(f"✅ Already checked")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Checkbox error: {e}")
            return False

    def enhanced_checkbox_click(self, checkbox_element, reason):
        """Enhanced checkbox clicking with multiple strategies"""
        try:
            print(f"🔄 Attempting to click checkbox: {reason}")
            
            # Strategy 1: Direct click on checkbox
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_element)
                self.human_like_delay(0.5, 1)
                
                checkbox_element.click()
                print(f"✅ Direct checkbox click successful")
                return True
            except Exception as e:
                print(f"⚠️ Direct checkbox click failed: {e}")
            
            # Strategy 2: Click via JavaScript
            try:
                self.driver.execute_script("arguments[0].click();", checkbox_element)
                print(f"✅ JavaScript checkbox click successful")
                return True
            except Exception as e:
                print(f"⚠️ JavaScript checkbox click failed: {e}")
            
            # Strategy 3: Click associated label
            try:
                checkbox_id = checkbox_element.get_attribute('id')
                if checkbox_id:
                    label_elem = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                    label_elem.click()
                    print(f"✅ Checkbox label click successful")
                    return True
            except Exception as e:
                print(f"⚠️ Checkbox label click failed: {e}")
            
            # Strategy 4: Click parent container
            try:
                parent = checkbox_element.find_element(By.XPATH, "./..")
                parent.click()
                print(f"✅ Checkbox parent container click successful")
                return True
            except Exception as e:
                print(f"⚠️ Checkbox parent click failed: {e}")
            
            print(f"❌ All checkbox click strategies failed")
            return False
            
        except Exception as e:
            print(f"❌ Enhanced checkbox click error: {e}")
            return False

    def handle_numeric_input(self, element, question_text, ai_response):
        """Handle numeric inputs"""
        try:
            # For experience questions, use CV data directly
            if 'experience' in question_text.lower() or 'year' in question_text.lower():
                experience_years = self.ai_agent.cv_data.get('experience_years', '4')
                print(f"🔍 Using experience from CV: {experience_years}")
                if self.safe_element_interaction(element, "type", experience_years):
                    print(f"✅ Entered experience: {experience_years}")
                    return True
            
            # Extract number from AI response for other numeric fields
            numbers = re.findall(r'\d+', ai_response)
            
            if numbers:
                number = numbers[0]
                if self.safe_element_interaction(element, "type", number):
                    print(f"✅ Entered number: {number}")
                    return True
            
            # Fallback: if it's asking for experience and we couldn't parse, use default
            if 'experience' in question_text.lower():
                default_exp = str(getattr(config, 'experience_years', '4'))
                if self.safe_element_interaction(element, "type", default_exp):
                    print(f"✅ Entered fallback experience: {default_exp}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Numeric input error: {e}")
            return False

    def handle_location_field(self, element, question_text, ai_response):
        """Handle location/city fields with autocomplete"""
        try:
            # Use location from CV data
            location = self.ai_agent.cv_data.get('location', 'Bangalore, India')
            print(f"🔍 Using location from CV: {location}")
            
            # Type the location
            if self.safe_element_interaction(element, "type", location):
                print(f"✅ Filled location: {question_text[:30]}... -> {location}")
                
                # Wait for autocomplete suggestions
                self.human_like_delay(2, 3)
                
                # Try to select first suggestion if available
                try:
                    suggestion_selectors = [
                        ".typeahead-results li:first-child",
                        ".search-typeahead-v2__hit:first-child",
                        ".autocomplete-result:first-child",
                        "[data-test-single-typeahead-entity-form-search-result]:first-child"
                    ]
                    
                    for selector in suggestion_selectors:
                        try:
                            suggestion = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if suggestion.is_displayed():
                                if self.safe_element_interaction(suggestion, "click"):
                                    print(f"✅ Selected location suggestion")
                                    return True
                        except:
                            continue
                    
                    # If no suggestion found, just press Enter
                    element.send_keys(Keys.ENTER)
                    print(f"✅ Pressed Enter for location field")
                    return True
                    
                except Exception as e:
                    print(f"⚠️ Location autocomplete failed: {e}")
                    return True  # Still consider success if we typed the location
                
            return False
            
        except Exception as e:
            print(f"❌ Location field error: {e}")
            return False

    def handle_text_input(self, element, question_text, ai_response, tag_name):
        """Handle text inputs with appropriate length limits"""
        try:
            # Determine max length based on field type and question
            if tag_name == 'textarea' or any(word in question_text.lower() for word in ['cover letter', 'describe', 'explain', 'why']):
                max_length = 500
            elif any(word in question_text.lower() for word in ['name', 'title', 'company']):
                max_length = 50
            else:
                max_length = 100
            
            clean_response = ai_response[:max_length].strip()
            
            # Use safe interaction method
            if self.safe_element_interaction(element, "type", clean_response):
                print(f"✅ Filled text: {question_text[:30]}... -> {clean_response[:50]}...")
                return True
            else:
                print(f"❌ Failed to fill text field: {question_text[:30]}...")
                return False
            
        except Exception as e:
            print(f"❌ Text input error: {e}")
            return False

    def try_next_step_without_filling(self):
        """Try to proceed to next step without filling any fields"""
        continue_btns = [
            "button[aria-label='Continue to next step']",
            "button[aria-label='Continue']", 
            "button[aria-label='Review your application']",
            "button[aria-label='Submit application']",
            "button[data-easy-apply-next-button]",
            "//button[contains(text(), 'Next')]",
            "//button[contains(text(), 'Continue')]",
            "//button[contains(text(), 'Review')]",
            "//button[contains(text(), 'Review your application')]",
            "//button[contains(text(), 'Submit application')]",
            "//button[contains(text(), 'Submit Application')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Apply')]",
            ".jobs-easy-apply-footer button:not([disabled])",
            "button[type='submit']:not([disabled])",
            ".jobs-easy-apply-content button:not([disabled])"
        ]
        
        # Get current page state to detect if we actually moved forward
        initial_url = self.driver.current_url
        initial_page_source_hash = hash(self.driver.page_source[:1000])  # Hash first 1000 chars for comparison
        
        for btn_selector in continue_btns:
            try:
                if btn_selector.startswith("//"):
                    # XPath selector
                    continue_btn = self.driver.find_element(By.XPATH, btn_selector)
                else:
                    continue_btn = self.driver.find_element(By.CSS_SELECTOR, btn_selector)
                    
                if continue_btn.is_enabled() and continue_btn.is_displayed():
                    button_text = continue_btn.text.strip() or continue_btn.get_attribute('aria-label') or 'Next'
                    
                    # Use safe interaction
                    if self.safe_element_interaction(continue_btn, "click"):
                        self.human_like_delay(2, 3)
                        
                        # Check if page actually changed
                        new_url = self.driver.current_url
                        new_page_source_hash = hash(self.driver.page_source[:1000])
                        
                        if new_url != initial_url or new_page_source_hash != initial_page_source_hash:
                            print(f"✅ Clicked '{button_text}' - Page changed successfully")
                            return True
                        else:
                            print(f"⚠️ Clicked '{button_text}' but page didn't change - may have validation errors")
                            # Check for validation errors after clicking
                            errors = self.get_form_errors()
                            if errors:
                                print(f"🔍 Validation errors found: {errors[:2]}...")  # Show first 2 errors
                                return False  # Don't claim success if there are validation errors
                            else:
                                print(f"✅ Clicked '{button_text}' - No visible errors, assuming success")
                                return True
            except Exception as e:
                continue
        
        print("❌ No working next button found")
        return False

    def get_form_errors(self):
        """Detect form validation errors"""
        error_selectors = [
            ".artdeco-inline-feedback--error",
            ".form-element-validation-error", 
            "[aria-describedby*='error']",
            ".error-message",
            ".validation-error",
            "[role='alert']",
            ".artdeco-inline-feedback[data-test-form-element-feedback-type='ERROR']"
        ]
        
        errors = []
        for selector in error_selectors:
            try:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in error_elements:
                    if elem.is_displayed():
                        error_text = elem.text.strip()
                        if error_text:
                            errors.append(error_text)
            except:
                continue
        
        return errors

    def find_required_empty_fields(self):
        """Find required fields that are empty"""
        required_fields = []
        
        # Enhanced required field detection for LinkedIn forms
        required_selectors = [
            "input[required]",
            "textarea[required]",
            "select[required]",
            "input[aria-required='true']",
            "textarea[aria-required='true']", 
            "select[aria-required='true']",
            "input[class*='required']",
            "textarea[class*='required']",
            "select[class*='required']"
        ]
        
        for selector in required_selectors:
            try:
                fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for field in fields:
                    if field.is_displayed():
                        # Check if field is empty
                        current_value = field.get_attribute('value') or ""
                        tag_name = field.tag_name.lower()
                        
                        is_empty = False
                        if tag_name == "select":
                            # For select elements, check if default option is selected
                            selected_text = field.find_element(By.CSS_SELECTOR, "option:checked").text.strip()
                            is_empty = not selected_text or selected_text in ["Select", "Choose", "Please select", ""]
                        elif tag_name in ["input", "textarea"]:
                            is_empty = not current_value.strip()
                        
                        if is_empty:
                            label = self.get_field_label(field)
                            if label:
                                required_fields.append((field, label))
                                print(f"🔍 Found required empty field: {label[:50]}...")
            except Exception as e:
                print(f"⚠️ Error checking required field: {e}")
                continue
        
        # Also look for fields with asterisk (*) indicators near labels
        try:
            asterisk_labels = self.driver.find_elements(By.XPATH, "//label[contains(text(), '*')]")
            for label_elem in asterisk_labels:
                if label_elem.is_displayed():
                    # Find associated input field
                    for_attr = label_elem.get_attribute('for')
                    if for_attr:
                        try:
                            field = self.driver.find_element(By.ID, for_attr)
                            if field.is_displayed():
                                current_value = field.get_attribute('value') or ""
                                if not current_value.strip():
                                    label_text = label_elem.text.strip()
                                    if (field, label_text) not in required_fields:
                                        required_fields.append((field, label_text))
                                        print(f"🔍 Found asterisk-marked required field: {label_text[:50]}...")
                        except:
                            continue
        except:
            pass
                
        print(f"🔍 Total required empty fields found: {len(required_fields)}")
        return required_fields

    def detect_form_questions(self):
        """Detect if there are actual form questions that need to be answered"""
        actual_questions = []
        
        try:
            # Look for actual form questions - labels that are associated with input fields
            # and contain question-like text
            question_patterns = [
                "//label[contains(text(), '?')]",  # Questions with question marks
                "//label[contains(text(), 'authorized')]",
                "//label[contains(text(), 'eligible')]", 
                "//label[contains(text(), 'visa')]",
                "//label[contains(text(), 'sponsorship')]",
                "//label[contains(text(), 'Bachelor')]",
                "//label[contains(text(), 'degree')]",
                "//label[contains(text(), 'commut')]",
                "//label[contains(text(), 'experience')]",
                "//label[contains(text(), 'years')]",
                "//fieldset/legend[contains(text(), '?')]",
                "//div[contains(@class, 'form-element')]//label[contains(text(), '?')]"
            ]
            
            # Skip these non-question elements
            skip_keywords = [
                'upload', 'resume', 'cover letter', 'search', 'alert', 'deselect', 
                'select resume', 'set alert', 'choose file', 'browse'
            ]
            
            for pattern in question_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    for elem in elements:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            # Only include if it's a real question and not in skip list
                            if (text and len(text) > 10 and 
                                not any(skip in text.lower() for skip in skip_keywords)):
                                
                                # Check if this label is associated with a form input
                                label_for = elem.get_attribute('for')
                                if label_for:
                                    try:
                                        associated_input = self.driver.find_element(By.ID, label_for)
                                        if associated_input.is_displayed():
                                            actual_questions.append(text[:100])
                                    except:
                                        pass
                                else:
                                    # Look for nearby form inputs
                                    try:
                                        parent = elem.find_element(By.XPATH, "./..")
                                        inputs = parent.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                                        if any(inp.is_displayed() for inp in inputs):
                                            actual_questions.append(text[:100])
                                    except:
                                        pass
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error detecting questions: {e}")
        
        # Remove duplicates
        actual_questions = list(set(actual_questions))
        
        if actual_questions:
            print(f"🔍 Detected {len(actual_questions)} actual form questions:")
            for i, q in enumerate(actual_questions[:5]):  # Show first 5
                print(f"   {i+1}. {q}")
        
        return actual_questions

    def find_required_fields_with_asterisk(self):
        """Find fields with asterisk (*) - these are definitely required"""
        required_fields = []
        
        # Find all labels with asterisk
        labels_with_asterisk = self.driver.find_elements(By.XPATH, "//label[contains(text(), '*')]")
        
        for label_elem in labels_with_asterisk:
            try:
                if not label_elem.is_displayed():
                    continue
                    
                label_text = label_elem.text.strip()
                print(f"🌟 Found required field label: {label_text}")
                
                # Find the associated form field
                field_element = None
                
                # Method 1: Use 'for' attribute
                for_attr = label_elem.get_attribute('for')
                if for_attr:
                    try:
                        field_element = self.driver.find_element(By.ID, for_attr)
                    except:
                        pass
                
                # Method 2: Look for input/select/textarea in same container
                if not field_element:
                    try:
                        parent = label_elem.find_element(By.XPATH, "./..")
                        field_candidates = parent.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                        for candidate in field_candidates:
                            if candidate.is_displayed():
                                field_element = candidate
                                break
                    except:
                        pass
                
                # Method 3: Look for following siblings
                if not field_element:
                    try:
                        siblings = label_elem.find_elements(By.XPATH, "./following-sibling::*")
                        for sibling in siblings:
                            if sibling.tag_name.lower() in ['input', 'select', 'textarea'] and sibling.is_displayed():
                                field_element = sibling
                                break
                    except:
                        pass
                
                if field_element:
                    required_fields.append((field_element, label_text))
                    print(f"  ✅ Found associated {field_element.tag_name} element")
                else:
                    print(f"  ❌ Could not find form element for: {label_text}")
                    
            except Exception as e:
                print(f"⚠️ Error processing asterisk label: {e}")
                continue
        
        return required_fields

    def is_field_already_filled(self, field):
        """Check if a field already has meaningful content"""
        try:
            if field.tag_name == 'select':
                select = Select(field)
                current = select.first_selected_option.text.strip()
                return current and current.lower() not in ['select', 'choose', 'please select', '', '--', 'none']
            elif field.get_attribute('type') == 'checkbox':
                return field.is_selected()
            elif field.get_attribute('type') == 'radio':
                name = field.get_attribute('name')
                if name:
                    radios = self.driver.find_elements(By.CSS_SELECTOR, f"input[type='radio'][name='{name}']")
                    return any(radio.is_selected() for radio in radios)
                return field.is_selected()
            else:
                value = field.get_attribute('value') or ''
                return len(value.strip()) > 0
        except:
            return False

    def find_all_form_fields(self):
        """Find relevant form fields that need to be filled (skip search, upload, etc.)"""
        relevant_fields = []
        
        # Skip fields that are not part of the application form
        skip_field_keywords = [
            'search', 'upload', 'browse', 'choose file', 'resume', 'cover letter',
            'alert', 'notification', 'email alert', 'job alert', 'deselect', 'select resume',
            'find', 'location search', 'company search', 'search-global-typeahead'
        ]
        
        # Prioritize field types - more important ones first
        field_selectors = [
            ("input[type='radio']", "radio"),           # Yes/No questions
            ("input[type='checkbox']", "checkbox"),     # Agreement checkboxes  
            ("select", "dropdown"),                     # Dropdowns
            ("input[type='number']", "number"),         # Numeric inputs
            ("textarea", "textarea"),                   # Text areas
            ("input[type='text']", "text"),            # Text inputs (but filtered)
            ("input[type='email']", "email"),          # Email inputs
            ("input[type='tel']", "phone")             # Phone inputs
        ]
        
        for selector, field_type in field_selectors:
            try:
                fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for field in fields:
                    if not field.is_displayed():
                        continue
                        
                    # Get field context
                    label = self.get_field_label(field)
                    field_id = field.get_attribute('id') or ''
                    field_name = field.get_attribute('name') or ''
                    field_class = field.get_attribute('class') or ''
                    
                    # Skip search fields by ID/class/name patterns
                    search_patterns = [
                        'search', 'typeahead', 'autocomplete', 'find', 'lookup', 
                        'jobs-search', 'search-box', 'query', 'keyword', 'filter',
                        'jobs-location', 'location-search', 'company-search',
                        'single-typeahead', 'search-typeahead', 'combobox-input',
                        'search-global-typeahead', 'global-nav', 'nav-search'
                    ]
                    field_attributes = (field_id + field_name + field_class).lower()
                    if any(pattern in field_attributes for pattern in search_patterns):
                        print(f"⏭️ Skipping search field: {field_id or field_name or field_class}")
                        continue
                    
                    # Also skip by role and aria attributes
                    role = field.get_attribute('role') or ''
                    aria_label = field.get_attribute('aria-label') or ''
                    placeholder = field.get_attribute('placeholder') or ''
                    
                    # Skip LinkedIn header search and navigation elements
                    if ('combobox' in role.lower() or 
                        'search' in (aria_label + role + placeholder).lower() or
                        placeholder.lower() == 'search'):
                        print(f"⏭️ Skipping search field by role/aria/placeholder: {role or aria_label or placeholder}")
                        continue
                    
                    # Skip fields that are outside the application modal
                    try:
                        # Check if field is inside the easy-apply modal
                        modal_ancestor = field.find_element(By.XPATH, "./ancestor::*[contains(@data-test-modal-id, 'easy-apply') or contains(@class, 'jobs-easy-apply')]")
                        # If we found a modal ancestor, this field is part of the application form
                    except:
                        # If no modal ancestor found, this field is probably not part of the application
                        if field_type == 'text' and 'search' in (aria_label + placeholder).lower():
                            print(f"⏭️ Skipping field outside application modal: {aria_label or placeholder}")
                            continue
                    
                    # Skip if label contains skip keywords
                    if label:
                        label_lower = label.lower()
                        if any(skip in label_lower for skip in skip_field_keywords):
                            print(f"⏭️ Skipping irrelevant field: {label[:30]}...")
                            continue
                        
                        # Include if it's a form question or checkbox/radio (these are usually required)
                        should_include = False
                        
                        if field_type in ['radio', 'checkbox']:
                            # Always include radio buttons and checkboxes
                            should_include = True
                        elif field_type == 'dropdown':
                            # Include dropdowns that aren't location searches
                            should_include = True
                        elif len(label) > 5 and ('?' in label or 
                             any(word in label_lower for word in [
                                 'experience', 'years', 'authorized', 'eligible', 'visa', 
                                 'sponsorship', 'degree', 'bachelor', 'commut', 'willing',
                                 'available', 'salary', 'notice', 'start', 'agree', 'terms',
                                 'onsite', 'remote', 'work', 'location', 'city', 'country'
                             ])):
                            should_include = True
                            
                            relevant_fields.append((field, label, field_type))
                        if should_include:
                            print(f"🔍 Found {field_type} field: {label[:50]}...")
                    
                    # Special case: unlabeled checkboxes and radio buttons (still include them)
                    elif field_type in ['radio', 'checkbox']:
                        # Try to get context from nearby text
                        try:
                            parent = field.find_element(By.XPATH, "./..")
                            context_text = parent.text.strip()[:100]
                            if context_text and len(context_text) > 5:
                                relevant_fields.append((field, context_text, field_type))
                                print(f"🔍 Found unlabeled {field_type}: {context_text[:50]}...")
                        except:
                            relevant_fields.append((field, f"Unlabeled {field_type}", field_type))
                            print(f"🔍 Found unlabeled {field_type} field")
                            
            except Exception as e:
                print(f"⚠️ Error finding {field_type} fields: {e}")
                continue
        
        return relevant_fields

    def handle_application_form(self, job_context=""):
        """Simple form handler: Click Next until errors, then AI fills fields"""
        try:
            print("🚀 SIMPLE FLOW: Trying to click Next first...")
            
            # Step 1: Try to click Next/Continue immediately
            if self.try_next_step_without_filling():
                print("✅ Clicked Next successfully - no form filling needed!")
                return True
            
            # Step 2: If Next failed, check for form errors
            print("⚠️ Next button failed - checking for form errors...")
            errors = self.get_form_errors()
            
            if errors:
                print(f"🔍 Found {len(errors)} form errors - AI will fill only error fields")
                
                # Check for validation errors first - these are priority
                errors = self.get_form_errors()
                if errors:
                    print(f"� Found validation errors: {len(errors)} errors detected")
                    print("�🚫 NOT trying to skip - will fill error fields first")
                    
                    # Find and fill fields with errors first
                    error_fields = self.find_fields_with_errors()
                    filled_count = 0
                    
                    for field, label in error_fields:
                        if self.fill_form_field(field, label, job_context, force_fill=True):
                            filled_count += 1
                            self.human_like_delay(1, 2)
                    
                    print(f"🤖 Filled {filled_count} error fields")
                    
                    # Try to proceed after filling error fields
                    if filled_count > 0:
                        if self.try_next_step_without_filling():
                            return True
                else:
                    print("🚫 NOT trying to skip - will fill form fields first")
                    
                    # No validation errors, but we have form fields to fill
                    filled_count = 0
                    
                    # Try to fill all relevant form fields
                    # Use simple handler instead of complex logic
                    return self.simple_form_handler(job_context)
            
        except Exception as e:
            print(f"❌ Error handling form: {e}")
            return False

    def simple_form_handler(self, job_context=""):
        """Clean simple form handler: Click Next until errors, then AI fills fields"""
        try:
            print("🚀 SIMPLE FLOW: Trying to click Next first...")
            
            # Step 1: Try to click Next/Continue immediately
            if self.try_next_step_without_filling():
                print("✅ Clicked Next successfully - no form filling needed!")
                return True
            
            # Step 2: If Next failed, check for form errors
            print("⚠️ Next button failed - checking for form errors...")
            errors = self.get_form_errors()
            
            if errors:
                print(f"🔍 Found {len(errors)} form errors - AI will fill only error fields")
                
                # Find and fill only the fields with errors
                error_fields = self.find_fields_with_errors()
                filled_count = 0
                
                for field, label in error_fields:  # Fill ALL error fields
                    print(f"🤖 Filling error field: {label}")
                    if self.simple_fill_field(field, label):
                        filled_count += 1
                        self.human_like_delay(0.5, 1)  # Faster delays
                    # Don't try Next after each field - fill all first!
                
                print(f"📝 Filled {filled_count} error fields, trying Next again...")
                return self.try_next_step_without_filling()
            
            # Step 3: No errors found, check for required fields
            print("🔍 No errors found - checking for required empty fields...")
            required_fields = self.find_required_empty_fields()
            
            if required_fields:
                print(f"📝 Found {len(required_fields)} required fields - filling them...")
                
                filled_count = 0
                for field, label in required_fields:  # Fill ALL required fields, not just 3
                    print(f"🤖 Filling required field: {label}")
                    if self.simple_fill_field(field, label):
                        filled_count += 1
                        self.human_like_delay(0.5, 1)
                    # Don't try Next after each field - fill all first!
                
                print(f"📝 Filled {filled_count} required fields, trying Next again...")
                return self.try_next_step_without_filling()
            
            print("❌ No errors or required fields found, but Next still failed")
            return False
            
        except Exception as e:
            print(f"❌ Simple form handler error: {e}")
            return False

    def handle_location_autocomplete_field(self, field, label, answer):
        """Handle location fields with autocomplete dropdown"""
        try:
            print(f"🗺️ Handling location autocomplete: {label}")
            
            # Clear and type the location
            field.clear()
            self.human_like_typing(field, answer)
            
            # Wait for autocomplete suggestions to appear
            self.human_like_delay(1, 2)
            
            # Try to select the first suggestion (index 0)
            suggestion_selectors = [
                "[role='listbox'] [role='option']:first-child",  # Generic listbox options
                ".typeahead-results li:first-child",             # LinkedIn typeahead
                ".search-typeahead-v2__hit:first-child",         # LinkedIn search typeahead
                ".autocomplete-result:first-child",              # General autocomplete
                "[data-test-single-typeahead-entity-form-search-result]:first-child",  # LinkedIn form result
                ".basic-typeahead__item:first-child",            # Basic typeahead
                "[id*='typeahead'] li:first-child",              # ID-based typeahead
                "[class*='suggestion']:first-child",            # Class-based suggestions
                "[class*='dropdown'] li:first-child"            # Dropdown list items
            ]
            
            suggestion_found = False
            for selector in suggestion_selectors:
                try:
                    suggestion = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if suggestion.is_displayed():
                        suggestion.click()
                        print(f"✅ Selected first location suggestion: {selector}")
                        suggestion_found = True
                        break
                except:
                    continue
            
            if not suggestion_found:
                # Try using arrow down + enter method
                try:
                    field.send_keys(Keys.ARROW_DOWN)
                    self.human_like_delay(0.5, 1)
                    field.send_keys(Keys.ENTER)
                    print(f"✅ Used arrow down + enter for location selection")
                    suggestion_found = True
                except:
                    pass
            
            if not suggestion_found:
                # Just press Enter to accept what we typed
                try:
                    field.send_keys(Keys.ENTER)
                    print(f"✅ Pressed Enter to accept typed location")
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"❌ Location autocomplete error: {e}")
            return False

    def get_field_error_message(self, field):
        """Get specific error message for a field"""
        try:
            # Check for aria-describedby error
            aria_describedby = field.get_attribute('aria-describedby')
            if aria_describedby:
                try:
                    error_elem = self.driver.find_element(By.ID, aria_describedby)
                    if error_elem.is_displayed():
                        return error_elem.text.strip()
                except:
                    pass
            
            # Look for error messages near the field
            error_selectors = [
                ".artdeco-inline-feedback--error",
                ".form-element-validation-error",
                "[role='alert']",
                ".error-message"
            ]
            
            # Check parent containers for error messages
            try:
                parent = field.find_element(By.XPATH, "./..")
                for selector in error_selectors:
                    try:
                        error_elem = parent.find_element(By.CSS_SELECTOR, selector)
                        if error_elem.is_displayed():
                            return error_elem.text.strip()
                    except:
                        continue
            except:
                pass
            
            return ""
        except:
            return ""

    def simple_fill_field(self, field, label):
        """Simple field filling using AI"""
        try:
            # Get options for dropdown/select fields
            options = []
            if field.tag_name == 'select':
                select_options = field.find_elements(By.TAG_NAME, 'option')
                options = [opt.text.strip() for opt in select_options if opt.text.strip()]
            
            # Check for specific error messages near this field
            error_message = self.get_field_error_message(field)
            
            # Get AI answer with error context
            answer = self.ai_agent.simple_ai_answer(label, options if options else None, error_message)
            
            if field.tag_name == 'select':
                # Handle dropdown with retry logic for stale elements
                max_retries = 3
                
                for retry in range(max_retries):
                    try:
                        # Re-find the select element to avoid stale element reference
                        if retry > 0:
                            # Try to relocate the element by its attributes
                            field_id = field.get_attribute('id')
                            field_name = field.get_attribute('name')
                            field_class = field.get_attribute('class')
                            
                            if field_id:
                                field = self.driver.find_element(By.ID, field_id)
                            elif field_name:
                                field = self.driver.find_element(By.NAME, field_name)
                            elif field_class:
                                field = self.driver.find_element(By.CLASS_NAME, field_class.split()[0])
                        
                        from selenium.webdriver.support.ui import Select
                        select = Select(field)
                        
                        print(f"🔍 Dropdown options: {[opt.text.strip() for opt in select.options]}")
                        print(f"🔍 AI answer: '{answer}'")
                        
                        # Skip placeholder options
                        placeholder_options = ['select an option', 'select', 'choose', 'please select', '', '--', 'none']
                        valid_options = [opt for opt in select.options if opt.text.strip().lower() not in placeholder_options]
                        
                        print(f"🔍 Valid options (excluding placeholders): {[opt.text.strip() for opt in valid_options]}")
                        
                        # Try exact match first (only from valid options)
                        for option in valid_options:
                            option_text = option.text.strip()
                            if option_text.lower() == answer.lower():
                                select.select_by_visible_text(option_text)
                                print(f"✅ Selected dropdown option (exact): {option_text}")
                                return True
                        
                        # Try partial match (only from valid options)
                        for option in valid_options:
                            option_text = option.text.strip()
                            if answer.lower() in option_text.lower():
                                select.select_by_visible_text(option_text)
                                print(f"✅ Selected dropdown option (partial): {option_text}")
                                return True
                        
                        # Try reverse partial match (only from valid options)
                        for option in valid_options:
                            option_text = option.text.strip()
                            if option_text.lower() in answer.lower():
                                select.select_by_visible_text(option_text)
                                print(f"✅ Selected dropdown option (reverse partial): {option_text}")
                                return True
                        
                        # Try direct Yes/No matching for simple dropdowns
                        if answer.lower() in ['yes', 'no']:
                            for option in valid_options:
                                option_text = option.text.strip().lower()
                                if option_text == answer.lower():
                                    select.select_by_visible_text(option.text.strip())
                                    print(f"✅ Selected dropdown (Yes/No match): {option.text.strip()}")
                                    return True
                        
                        # Smart fallback for common patterns (only from valid options)
                        if answer.lower() == 'professional' and any('professional' in opt.text.lower() for opt in valid_options):
                            for option in valid_options:
                                if 'professional' in option.text.lower():
                                    select.select_by_visible_text(option.text.strip())
                                    print(f"✅ Selected dropdown (smart match): {option.text.strip()}")
                                    return True
                        
                        # Final fallback: If we can't match, select the first valid option (not placeholder)
                        if valid_options:
                            first_valid = valid_options[0]
                            select.select_by_visible_text(first_valid.text.strip())
                            print(f"⚠️ Fallback selection (first valid): {first_valid.text.strip()}")
                            return True
                        
                        print(f"❌ Could not find matching option for: '{answer}' in {[opt.text.strip() for opt in select.options]}")
                        return False
                        
                    except Exception as e:
                        print(f"⚠️ Dropdown attempt {retry + 1} failed: {e}")
                        if retry == max_retries - 1:
                            print(f"❌ All dropdown attempts failed")
                            return False
                        self.human_like_delay(0.5, 1)  # Wait before retry
                        continue
                
                return False
                
            elif field.tag_name == 'input':
                input_type = field.get_attribute('type')
                
                if input_type in ['radio', 'checkbox']:
                    # For radio/checkbox, click if answer is positive
                    if answer.lower() in ['yes', 'true', '1']:
                        field.click()
                        return True
                else:
                    # Check if this is a location/city autocomplete field
                    is_location_field = any(word in label.lower() for word in ['location', 'city', 'address', 'where'])
                    
                    if is_location_field:
                        return self.handle_location_autocomplete_field(field, label, answer)
                    else:
                        # Regular input field
                        field.clear()
                        self.human_like_typing(field, answer)
                        return True
            
            elif field.tag_name == 'textarea':
                field.clear()
                self.human_like_typing(field, answer)
                return True
                
            return False
            
        except Exception as e:
            print(f"❌ Error filling field {label}: {e}")
            return False

    def find_fields_with_errors(self):
        """Find specific form fields that have validation errors"""
        error_fields = []
        
        try:
            # Enhanced error field detection for LinkedIn forms
            error_field_selectors = [
                "input[aria-invalid='true']",
                "textarea[aria-invalid='true']", 
                "select[aria-invalid='true']",
                ".artdeco-text-input--error input",
                ".form-element--error input",
                ".form-element--error textarea",
                ".form-element--error select",
                ".form-element--error input[type='radio']",
                ".form-element--error input[type='checkbox']",
                ".jobs-easy-apply-form-element--error input",
                ".jobs-easy-apply-form-element--error textarea", 
                ".jobs-easy-apply-form-element--error select",
                ".jobs-easy-apply-form-element--error input[type='radio']",
                ".jobs-easy-apply-form-element--error input[type='checkbox']",
                "input[class*='error']",
                "select[class*='error']",
                "textarea[class*='error']",
                "input[type='radio'][class*='error']",
                "input[type='checkbox'][class*='error']"
            ]
            
            for selector in error_field_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for field in fields:
                        if field.is_displayed():
                            label = self.get_field_label(field)
                            if label:
                                error_fields.append((field, label))
                                print(f"🔍 Found error field: {label[:50]}...")
                except:
                    continue
            
            # If we detected validation errors but no error fields, find ALL form fields
            # This is a fallback when LinkedIn doesn't mark fields with error classes
            validation_errors = self.get_form_errors()
            if validation_errors and not error_fields:
                print(f"🔍 No error fields found but have {len(validation_errors)} validation errors:")
                for i, err in enumerate(validation_errors):
                    print(f"   Error {i+1}: {err[:100]}...")
                print(f"🔍 Scanning all form fields...")
                
                # Find all visible form fields when we have validation errors
                all_form_selectors = [
                    "select",  # Dropdowns are most common with "Select an option"
                    "input[type='text']",     # Text inputs (location, phone, etc.) - prioritize these
                    "input[type='number']",   # Number inputs
                    "input[type='tel']",      # Phone inputs
                    "input[type='email']",    # Email inputs
                    "textarea",               # Text areas
                    "input[type='radio']",    # Radio buttons
                    "input[type='checkbox']"  # Checkboxes
                ]
                
                for field_selector in all_form_selectors:
                    try:
                        fields = self.driver.find_elements(By.CSS_SELECTOR, field_selector)
                        for field in fields:
                            if field.is_displayed():
                                field_label = self.get_field_label(field)
                                
                                # For dropdowns, check if they need selection
                                if field.tag_name == 'select':
                                    try:
                                        select = Select(field)
                                        selected_text = select.first_selected_option.text.strip()
                                        all_options = [opt.text.strip() for opt in select.options]
                                        print(f"   🔍 Dropdown check - Selected: '{selected_text}', Options: {all_options}")
                                        
                                        # If no meaningful selection made
                                        if not selected_text or selected_text.lower() in ['select', 'choose', 'please select', '', '--', 'select an option', 'none']:
                                            if not field_label:
                                                field_label = "Dropdown selection required"
                                            error_fields.append((field, field_label))
                                            print(f"🔍 Found unselected dropdown: {field_label[:50]}...")
                                    except Exception as e:
                                        print(f"   ⚠️ Error checking dropdown: {e}")
                                        # Even if we can't check, add it if we have validation errors
                                        if not field_label:
                                            field_label = "Dropdown field needs attention"
                                        error_fields.append((field, field_label))
                                        print(f"🔍 Added problematic dropdown: {field_label[:50]}...")
                                
                                # For radio buttons, check if any in group is selected
                                elif field.get_attribute('type') == 'radio':
                                    name = field.get_attribute('name')
                                    if name:
                                        try:
                                            radio_group = self.driver.find_elements(By.CSS_SELECTOR, f"input[type='radio'][name='{name}']")
                                            if not any(radio.is_selected() for radio in radio_group if radio.is_displayed()):
                                                if not field_label:
                                                    field_label = "Radio button selection required"
                                                # Only add once per radio group
                                                if not any(name in str(existing_field) for existing_field, _ in error_fields):
                                                    error_fields.append((field, field_label))
                                                    print(f"🔍 Found unselected radio group: {field_label[:50]}...")
                                        except:
                                            pass
                                
                                # For checkboxes, check if they need to be checked
                                elif field.get_attribute('type') == 'checkbox':
                                    if not field.is_selected():
                                        if not field_label:
                                            field_label = "Checkbox agreement required"
                                        error_fields.append((field, field_label))
                                        print(f"🔍 Found unchecked checkbox: {field_label[:50]}...")
                                
                                # For other inputs, check if empty and looks required
                                elif not field.get_attribute('value') or not field.get_attribute('value').strip():
                                    if field_label and len(field_label) > 5:
                                        # Skip obvious search/navigation fields
                                        skip_labels = [
                                            'search', 'find', 'lookup', 'filter', 'keyword', 'query',
                                            'location search', 'company search', 'job search', 'global search',
                                            'search jobs', 'search companies', 'search people'
                                        ]
                                        
                                        # Check field attributes for search patterns
                                        field_id = field.get_attribute('id') or ''
                                        field_name = field.get_attribute('name') or ''
                                        field_class = field.get_attribute('class') or ''
                                        field_placeholder = field.get_attribute('placeholder') or ''
                                        field_aria_label = field.get_attribute('aria-label') or ''
                                        
                                        all_field_text = (field_id + field_name + field_class + field_placeholder + field_aria_label + field_label).lower()
                                        
                                        # Skip if it's clearly a search field
                                        if any(skip_word in all_field_text for skip_word in skip_labels):
                                            print(f"⏭️ Skipping search/nav field: {field_label[:30]}...")
                                            continue
                                            
                                        # Skip if it's the LinkedIn global search
                                        if 'search-global-typeahead' in all_field_text or 'global-nav' in all_field_text:
                                            print(f"⏭️ Skipping LinkedIn global search field")
                                            continue
                                        
                                        error_fields.append((field, field_label))
                                        print(f"🔍 Found empty required field: {field_label[:50]}...")
                    except Exception as e:
                        print(f"⚠️ Error scanning {field_selector}: {e}")
                        continue
                
                # Special case: If validation errors contain dropdown options, find matching dropdowns
                for error in validation_errors:
                    if 'select an option' in error.lower() or any(keyword in error.lower() for keyword in ['professional', 'conversational', 'native', 'bilingual']):
                        print(f"🔍 Detected dropdown-specific error: {error[:100]}...")
                        # Try to find dropdowns with matching options
                        all_selects = self.driver.find_elements(By.CSS_SELECTOR, "select")
                        for select_elem in all_selects:
                            if select_elem.is_displayed():
                                try:
                                    select = Select(select_elem)
                                    options = [opt.text.strip() for opt in select.options]
                                    # Check if this dropdown has options mentioned in the error
                                    error_words = error.lower().split()
                                    option_matches = sum(1 for opt in options if any(word in opt.lower() for word in error_words if len(word) > 3))
                                    
                                    if option_matches >= 2:  # At least 2 option words match
                                        field_label = self.get_field_label(select_elem) or "Dropdown with validation error"
                                        if (select_elem, field_label) not in error_fields:
                                            error_fields.append((select_elem, field_label))
                                            print(f"🎯 Found matching dropdown for error: {field_label[:50]}...")
                                except Exception as e:
                                    print(f"   ⚠️ Error checking dropdown options: {e}")
                                    continue
                    
                    # Special case: If validation errors mention checkboxes, find them
                    elif any(keyword in error.lower() for keyword in ['checkbox', 'check this box', 'agree', 'terms', 'privacy policy']):
                        print(f"🔍 Detected checkbox-specific error: {error[:100]}...")
                        # Try to find checkboxes that need to be checked
                        all_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                        for checkbox in all_checkboxes:
                            if checkbox.is_displayed() and not checkbox.is_selected():
                                try:
                                    field_label = self.get_field_label(checkbox)
                                    if not field_label:
                                        # Try to get label from nearby text
                                        parent = checkbox.find_element(By.XPATH, "./..")
                                        parent_text = parent.text.strip()
                                        if parent_text and len(parent_text) > 10:
                                            # Extract meaningful label from parent text
                                            lines = [line.strip() for line in parent_text.split('\n') if line.strip()]
                                            for line in lines:
                                                if any(word in line.lower() for word in ['agree', 'terms', 'privacy', 'policy', 'checkbox']):
                                                    field_label = line[:50] + "..." if len(line) > 50 else line
                                                    break
                                    
                                    if not field_label:
                                        field_label = "Checkbox agreement required"
                                    
                                    if (checkbox, field_label) not in error_fields:
                                        error_fields.append((checkbox, field_label))
                                        print(f"🎯 Found unchecked checkbox: {field_label[:50]}...")
                                except Exception as e:
                                    print(f"   ⚠️ Error checking checkbox: {e}")
                                    continue
                
                # Additional comprehensive checkbox search for agreement checkboxes
                # This is specifically for cases like "Select checkbox to proceed"
                if any('checkbox' in error.lower() for error in validation_errors):
                    print(f"🔍 Performing comprehensive checkbox search...")
                    comprehensive_checkbox_selectors = [
                        "input[type='checkbox']",
                        "input[type='checkbox']:not(:checked)",
                        "[role='checkbox']",
                        "input[type='checkbox'][required]",
                        "input[type='checkbox'][aria-required='true']"
                    ]
                    
                    for selector in comprehensive_checkbox_selectors:
                        try:
                            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for checkbox in checkboxes:
                                if checkbox.is_displayed() and not checkbox.is_selected():
                                    # Try multiple ways to get the label
                                    field_label = self.get_field_label(checkbox)
                                    
                                    if not field_label:
                                        # Try to find nearby text that looks like a label
                                        try:
                                            # Check if checkbox is inside a label
                                            parent_label = checkbox.find_element(By.XPATH, "./ancestor::label[1]")
                                            if parent_label and parent_label.text.strip():
                                                field_label = parent_label.text.strip()[:100]
                                        except:
                                            pass
                                    
                                    if not field_label:
                                        # Check for adjacent text/spans
                                        try:
                                            next_sibling = checkbox.find_element(By.XPATH, "./following-sibling::*[1]")
                                            if next_sibling and next_sibling.text.strip():
                                                field_label = next_sibling.text.strip()[:100]
                                        except:
                                            pass
                                    
                                    if not field_label:
                                        # Look at parent container text
                                        try:
                                            parent = checkbox.find_element(By.XPATH, "./..")
                                            parent_text = parent.text.strip()
                                            if parent_text and len(parent_text) > 5:
                                                field_label = parent_text[:100]
                                        except:
                                            pass
                                    
                                    if not field_label:
                                        field_label = "Agreement checkbox (no label found)"
                                    
                                    # Avoid duplicates
                                    if not any(checkbox == existing_field for existing_field, _ in error_fields):
                                        error_fields.append((checkbox, field_label))
                                        print(f"🎯 Found comprehensive checkbox: {field_label[:50]}...")
                        except Exception as e:
                            print(f"   ⚠️ Error in comprehensive checkbox search: {e}")
                            continue
            
            # Look for fields near error messages with more comprehensive selectors
            try:
                error_message_selectors = [
                    ".artdeco-inline-feedback--error",
                    ".form-element-validation-error",
                    "[role='alert']",
                    ".jobs-easy-apply-form-element__error",
                    "[class*='error'][class*='message']",
                    "[class*='validation'][class*='error']"
                ]
                
                for selector in error_message_selectors:
                    error_messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for error_msg in error_messages:
                        if error_msg.is_displayed() and error_msg.text.strip():
                            error_text = error_msg.text.strip()
                            print(f"🔍 Found error message: {error_text[:50]}...")
                            
                            # Parse the error message to understand what field is required
                            # LinkedIn often puts the full question in the error message
                            question_in_error = error_text
                            
                            # Look for input fields in the same form element or nearby
                            search_elements = []
                            try:
                                # Try to find the form element container
                                form_element = error_msg.find_element(By.XPATH, "./ancestor::*[contains(@class, 'form-element') or contains(@class, 'jobs-easy-apply-form-element')][1]")
                                search_elements.append(form_element)
                            except:
                                # Fallback to parent elements
                                try:
                                    search_elements.extend([
                                        error_msg.find_element(By.XPATH, "./.."),
                                        error_msg.find_element(By.XPATH, "./../..")
                                    ])
                                except:
                                    pass
                            
                            for search_elem in search_elements:
                                try:
                                    # Look for all types of form inputs
                                    nearby_fields = search_elem.find_elements(By.CSS_SELECTOR, 
                                        "input[type='radio'], input[type='checkbox'], select, input[type='text'], input[type='number'], textarea")
                                    
                                    for field in nearby_fields:
                                        if field.is_displayed():
                                            # Use the error message text as the question if no label found
                                            field_label = self.get_field_label(field)
                                            if not field_label:
                                                # Extract the main question from error text
                                                lines = question_in_error.split('\n')
                                                for line in lines:
                                                    if '?' in line and len(line) > 10:
                                                        field_label = line.strip()
                                                        break
                                                if not field_label:
                                                    field_label = question_in_error[:100]
                                            
                                            if field_label and (field, field_label) not in error_fields:
                                                error_fields.append((field, field_label))
                                                print(f"🔍 Found field with validation error: {field_label[:50]}...")
                                except:
                                    continue
                            
            except Exception as e:
                print(f"⚠️ Error processing error messages: {e}")
                
        except Exception as e:
            print(f"❌ Error finding error fields: {e}")
        
        print(f"🔍 Total error fields found: {len(error_fields)}")
        return error_fields
    
    def get_field_label(self, element):
        """Get label text for form element with enhanced LinkedIn form support"""
        try:
            # Try to find associated label by ID
            element_id = element.get_attribute('id')
            if element_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                    label_text = label.text.strip()
                    if label_text:
                        return label_text
                except:
                    pass
            
            # Try aria-label or aria-labelledby
            aria_label = element.get_attribute('aria-label')
            if aria_label:
                return aria_label.strip()
                
            aria_labelledby = element.get_attribute('aria-labelledby')
            if aria_labelledby:
                try:
                    label_elem = self.driver.find_element(By.ID, aria_labelledby)
                    return label_elem.text.strip()
                except:
                    pass
            
            # Try parent and ancestor elements for labels
            search_ancestors = [
                "./ancestor::*[contains(@class, 'form-element')][1]",
                "./ancestor::*[contains(@class, 'jobs-easy-apply-form-element')][1]", 
                "./..",
                "./../.."
            ]
            
            for ancestor_xpath in search_ancestors:
                try:
                    ancestor = element.find_element(By.XPATH, ancestor_xpath)
                    
                    # Look for label elements
                    label_selectors = [
                        "label",
                        ".label",
                        ".form-label", 
                        "[class*='label']",
                        ".jobs-easy-apply-form-element__label",
                        ".artdeco-text-input__label"
                    ]
                    
                    for selector in label_selectors:
                        try:
                            label_elem = ancestor.find_element(By.CSS_SELECTOR, selector)
                            label_text = label_elem.text.strip()
                            if label_text and len(label_text) < 200:
                                return label_text
                        except:
                            continue
                            
                except:
                    continue
            
            # Try sibling elements
            try:
                siblings = element.find_elements(By.XPATH, 
                    "./preceding-sibling::*[position()<=3] | ./following-sibling::*[position()<=3]")
                for sibling in siblings:
                    text = sibling.text.strip()
                    if text and 5 < len(text) < 200 and not text.isdigit():
                        return text
            except:
                pass
            
            # Try nearby text nodes
            try:
                parent = element.find_element(By.XPATH, "./..")
                all_text = parent.text.strip()
                if all_text and len(all_text) < 200:
                    # Extract meaningful text that's not just whitespace
                    lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                    for line in lines:
                        if 5 < len(line) < 100 and not line.isdigit():
                            return line
            except:
                pass
                
            # Try placeholder or name attribute as fallback
            placeholder = element.get_attribute('placeholder')
            if placeholder and placeholder.strip():
                return placeholder.strip()
                
            name = element.get_attribute('name')
            if name:
                formatted_name = name.replace('_', ' ').replace('-', ' ').title()
                return formatted_name
                
        except Exception as e:
            print(f"⚠️ Error getting field label: {e}")
            
        return ""

    def enhanced_job_application_flow(self):
        """Main job application flow with enhanced stealth and AI integration"""
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:        
            self.driver.get(url)
            self.human_like_delay(2, 4)
            
            try:
                totalJobs = self.driver.find_element(By.XPATH,'//small').text 
            except:
                print("No Matching Jobs Found")
                continue
                
            totalPages = utils.jobsToPages(totalJobs)
            urlWords = utils.urlToKeywords(url)
            
            for page in range(totalPages):
                # Add random breaks
                if random.randint(1, 10) == 1:  # 10% chance
                    print("Taking a random break...")
                    self.human_like_delay(30, 60)  # 30-60 second break
                
                currentPageJobs = constants.jobsPerPage * page
                url_with_start = url + "&start=" + str(currentPageJobs)
                self.driver.get(url_with_start)
                self.human_like_delay(3, 6)

                offersPerPage = self.driver.find_elements(By.XPATH,'//li[@data-occludable-job-id]')
                
                offerIds = []
                for offer in offersPerPage:
                    offerId = offer.get_attribute("data-occludable-job-id")
                    if offerId:
                        offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
                    self.driver.get(offerPage)
                    self.human_like_delay(3, 6)
                    
                    # Random mouse movement
                    self.random_mouse_movement()
                    
                    countJobs += 1
                    jobProperties = self.getJobProperties(countJobs)
                    
                    # Get job context for AI
                    job_context = self.extract_job_context()
                    
                    # Scroll down to see the apply button (human behavior)
                    self.driver.execute_script("window.scrollTo(0, 500);")
                    self.human_like_delay(1, 2)
                    
                    button = self.easyApplyButton()
                    
                    if button:
                        try:
                            button.click()
                            self.human_like_delay(2, 4)
                            countApplied += 1
                            
                            # Try immediate submit
                            try:
                                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
                                submit_btn.click()
                                self.human_like_delay(2, 4)
                                print(f"✅ Applied: {offerPage}")
                                
                            except:
                                # Handle multi-step application with AI
                                result = self.handle_multi_step_application_with_ai(offerPage, job_context)
                                print(f"{jobProperties} | {result}")
                                
                        except Exception as e:
                            print(f"❌ Error applying: {e}")
                    
                    # Random delay between applications
                    self.human_like_delay(5, 15)
                    
                    # Occasional longer breaks
                    if countJobs % 20 == 0:
                        print("Taking a longer break...")
                        self.human_like_delay(120, 300)  # 2-5 minute break

    def extract_job_context(self):
        """Extract job context for AI processing"""
        context = {}
        try:
            # Get job title
            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1")
            context['title'] = title_elem.text
            
            # Get company name
            company_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__company-name")
            context['company'] = company_elem.text
            
            # Get job description (first 1000 chars)
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".jobs-description__content")
                context['description'] = desc_elem.text[:1000]
            except:
                context['description'] = ""
                
        except:
            pass
            
        return context

    def handle_multi_step_application_with_ai(self, offerPage, job_context):
        """Handle multi-step application process with smart AI assistance"""
        try:
            steps_completed = 0
            max_steps = 10  # Prevent infinite loops
            
            while steps_completed < max_steps:
                print(f"📋 Processing step {steps_completed + 1}...")
                
                # CHANGED: Always analyze the form first before trying to skip
                print("🔍 Analyzing current step for form content...")
                form_handled = self.simple_form_handler(job_context)
                
                if form_handled:
                    print("✅ Form handled successfully")
                    steps_completed += 1
                    self.human_like_delay(2, 4)
                    continue
                else:
                    print("⚠️ No form content to handle, trying direct navigation...")
                    # Only try to skip if no form content was detected
                    if self.try_next_step_without_filling():
                        print("✅ Advanced to next step without filling fields")
                        steps_completed += 1
                        continue
                
                # Check if we've reached the review/submit stage
                if self.is_final_step():
                    print("📝 Reached final submission step")
                    break
                
                # If we can't proceed, try alternative buttons
                print("🔄 Trying alternative navigation...")
                if not self.try_alternative_navigation():
                    print("⚠️ Cannot find next step button, may be at final step")
                    break
                else:
                    print("✅ Found alternative navigation")
                    
                steps_completed += 1
                self.human_like_delay(2, 4)
            
            # Handle final submission
            return self.handle_final_submission(offerPage)
                
        except Exception as e:
            return f"❌ Error in multi-step application: {offerPage} - {str(e)[:50]}"

    def is_final_step(self):
        """Check if we're at the final submission step"""
        final_indicators = [
            "button[aria-label='Submit application']",
            "button[aria-label='Review your application']", 
            "//button[contains(text(), 'Submit application')]",
            "//button[contains(text(), 'Submit Application')]",
            "//button[contains(text(), 'Review')]",
            "//button[contains(text(), 'Submit')]",
            ".jobs-easy-apply-footer button[data-easy-apply-submit-button]",
            "button[data-test-modal-close-btn]", # Sometimes the X button indicates completion
            "//span[contains(text(), 'Application sent')]", # Success message
        ]
        
        for selector in final_indicators:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                if element.is_displayed():
                    print(f"📋 Found final step indicator: {element.text if hasattr(element, 'text') else selector}")
                    return True
            except:
                continue
        
        return False

    def try_alternative_navigation(self):
        """Try alternative navigation buttons including Review step"""
        alt_buttons = [
            "//button[contains(text(), 'Review')]",
            "//button[contains(text(), 'Review your application')]",
            "//button[contains(text(), 'Submit application')]", 
            "//button[contains(text(), 'Submit Application')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Apply')]",
            "//button[contains(text(), 'Send application')]",
            "//button[contains(text(), 'Skip')]",
            ".jobs-easy-apply-footer button:not([disabled])",
            "button[aria-label='Review your application']",
            "button[aria-label='Submit application']"
        ]
        
        for selector in alt_buttons:
            try:
                if selector.startswith("//"):
                    button = self.driver.find_element(By.XPATH, selector)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                if button.is_enabled() and button.is_displayed():
                    button_text = button.text.strip()
                    print(f"🔄 Trying alternative button: {button_text}")
                    button.click()
                    self.human_like_delay(2, 3)
                    return True
            except Exception as e:
                continue
        
        return False

    def handle_final_submission(self, offerPage):
        """Enhanced final submission handling with better button detection"""
        try:
            print("📝 Starting final submission process...")
            
            # First, try to find and click Review button if present
            review_selectors = [
                "//button[contains(text(), 'Review')]",
                "//button[contains(text(), 'Review your application')]",
                "button[aria-label='Review your application']"
            ]
            
            review_clicked = False
            for selector in review_selectors:
                try:
                    if selector.startswith("//"):
                        review_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        review_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                    if review_btn.is_enabled() and review_btn.is_displayed():
                        print("📋 Clicking Review button...")
                        review_btn.click()
                        self.human_like_delay(3, 5)
                        review_clicked = True
                        break
                except:
                    continue
            
            # Unfollow company if configured
            if not getattr(config, 'followCompanies', False):
                try:
                    follow_selectors = [
                        "input[id*='follow']",
                        "label[for*='follow'] input",
                        "input[type='checkbox'][id*='follow']",
                        "//label[contains(text(), 'follow')]/input",
                        "//input[@type='checkbox' and contains(@aria-label, 'follow')]"
                    ]
                    
                    for selector in follow_selectors:
                        try:
                            if selector.startswith("//"):
                                follow_elem = self.driver.find_element(By.XPATH, selector)
                            else:
                                follow_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                                
                            if follow_elem.is_selected() and follow_elem.is_displayed():
                                follow_elem.click()
                                self.human_like_delay(1, 2)
                                print("✅ Unfollowed company")
                                break
                        except:
                            continue
                except:
                    pass
            
            # Now try to submit application with comprehensive selectors
            submit_selectors = [
                "button[aria-label='Submit application']",
                "button[data-easy-apply-submit-button]",
                "//button[contains(text(), 'Submit application')]",
                "//button[contains(text(), 'Submit Application')]",
                "//button[contains(text(), 'Send application')]",
                "//button[contains(text(), 'Apply now')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Apply')]",
                ".jobs-easy-apply-footer button[type='submit']",
                "button[type='submit']:not([disabled])",
                "//button[@type='submit' and not(@disabled)]"
            ]
            
            submission_attempted = False
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                    if submit_btn.is_enabled() and submit_btn.is_displayed():
                        button_text = submit_btn.text.strip()
                        print(f"🚀 Clicking submit button: {button_text}")
                        submit_btn.click()
                        self.human_like_delay(3, 5)
                        submission_attempted = True
                        break
                except Exception as e:
                    continue
            
            if not submission_attempted:
                print("⚠️ No submit button found, trying JavaScript click on all buttons...")
                # Last resort: try clicking any enabled button in the footer
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, ".jobs-easy-apply-footer button, button[type='submit']")
                    for btn in buttons:
                        if btn.is_enabled() and btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", btn)
                            print(f"🔄 JavaScript clicked: {btn.text}")
                            self.human_like_delay(3, 5)
                            submission_attempted = True
                            break
                except:
                    pass
            
            if submission_attempted:
                # Check for success indicators
                self.human_like_delay(2, 4)
                success_indicators = [
                    "//h3[contains(text(), 'Application sent')]",
                    "//h3[contains(text(), 'Your application was sent')]", 
                    "//div[contains(text(), 'Application submitted')]",
                    "//span[contains(text(), 'Application sent')]",
                    ".jobs-easy-apply-content--success",
                    "//div[contains(text(), 'successfully')]",
                    "//div[contains(@class, 'success')]"
                ]
                
                for success_selector in success_indicators:
                    try:
                        success_elem = self.driver.find_element(By.XPATH, success_selector)
                        if success_elem.is_displayed():
                            return f"✅ Application submitted successfully: {offerPage}"
                    except:
                        continue
                
                # If no success message found, assume it worked if we got this far
                return f"✅ Application submitted: {offerPage}"
            
            return f"❌ Could not find any submit button: {offerPage}"
                
        except Exception as e:
            return f"❌ Error in final submission: {offerPage} - {str(e)[:100]}"

    def generate_job_search_urls_from_cv(self):
        """Generate job search URLs based on CV skills and experience"""
        try:
            skills = self.ai_agent.cv_data.get('skills', [])
            experience = self.ai_agent.cv_data.get('experience_years', '0')
            current_title = self.ai_agent.cv_data.get('current_title', 'Software Developer')
            location = self.ai_agent.cv_data.get('location', 'India')
            
            # Use AI to suggest relevant job titles and keywords
            search_prompt = f"""
Based on this professional profile, suggest 10 relevant job search keywords and titles for LinkedIn job search:

Skills: {', '.join(skills[:15])}  # Limit to top 15 skills
Experience: {experience} years
Current Title: {current_title}
Location: {location}

Return only a JSON array of job search terms, like:
["Software Developer", "Python Developer", "Full Stack Developer", "Backend Developer", "Data Scientist"]

Focus on the most relevant job titles based on the skills and experience.
"""
            
            response = requests.post(f"{self.ai_agent.ollama_url}/api/generate", 
                                   json={
                                       "model": self.ai_agent.model,
                                       "prompt": search_prompt,
                                       "stream": False,
                                       "options": {"temperature": 0.2}
                                   }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()['response'].strip()
                
                # Clean up and parse JSON
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0]
                elif '```' in result:
                    result = result.split('```')[1].split('```')[0]
                
                try:
                    job_keywords = json.loads(result)
                    print(f"🎯 AI suggested job keywords: {job_keywords}")
                    return job_keywords
                except:
                    pass
            
            # Fallback to skills-based keywords
            fallback_keywords = skills[:8] + [current_title]  # Top 8 skills + current title
            print(f"🎯 Using skills-based keywords: {fallback_keywords}")
            return fallback_keywords
            
        except Exception as e:
            print(f"❌ Error generating job keywords: {e}")
            return [self.ai_agent.cv_data.get('current_title', 'Software Developer')]

    def generateUrls(self):
        """Generate job URLs using config settings and existing utils"""
        if not os.path.exists('data'):
            os.makedirs('data')
        try: 
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                # Use existing URL generator with config values
                try:
                    linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                    print(f"✅ Generated {len(linkedinJobLinks)} URLs using config settings")
                    print(f"📋 Using locations: {getattr(config, 'location', ['Europe'])}")
                    print(f"📋 Using keywords: {getattr(config, 'keywords', ['Software Engineer'])[:5]}...")
                    print(f"📋 Using experience levels: {getattr(config, 'experienceLevels', ['Mid-Senior level'])}")
                    print(f"📋 Using job types: {getattr(config, 'jobType', ['Full-time'])}")
                    print(f"📋 Using remote options: {getattr(config, 'remote', ['On-site'])}")
                except Exception as e:
                    print(f"⚠️ Config URL generation failed: {e}")
                    # Fallback: get AI-suggested job keywords and generate manually
                    job_keywords = self.generate_job_search_urls_from_cv()
                    linkedinJobLinks = self.generate_linkedin_urls_from_keywords(job_keywords)
                    print(f"✅ Generated {len(linkedinJobLinks)} URLs using CV analysis fallback")
                
                for url in linkedinJobLinks:
                    file.write(url + "\n")
                    
        except Exception as e:
            print(f"❌ Could not generate URLs: {e}")
    
    def generate_linkedin_urls_from_keywords(self, keywords):
        """Generate LinkedIn job search URLs from keywords"""
        base_url = "https://www.linkedin.com/jobs/search/?keywords={}&location={}&f_TPR=r86400&f_E=2,3,4&f_AL=true"
        
        location = self.ai_agent.cv_data.get('location', 'India')
        urls = []
        
        for keyword in keywords[:10]:  # Limit to 10 searches
            formatted_keyword = keyword.replace(' ', '%20')
            formatted_location = location.replace(' ', '%20')
            url = base_url.format(formatted_keyword, formatted_location)
            urls.append(url)
        
        return urls

    def getJobProperties(self, count):
        """Extract job properties with better error handling"""
        job_data = {
            'title': 'N/A',
            'company': 'N/A', 
            'location': 'N/A',
            'workplace': 'N/A',
            'posted_date': 'N/A',
            'applications': 'N/A'
        }
        
        selectors = [
            ('title', "h1"),
            ('company', ".jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name"),
            ('location', ".jobs-unified-top-card__bullet"),
            ('workplace', ".jobs-unified-top-card__workplace-type"),
            ('posted_date', "span:contains('ago'), .jobs-unified-top-card__posted-date"),
            ('applications', ".jobs-unified-top-card__applicant-count")
        ]
        
        for key, selector in selectors:
            try:
                if ':contains' in selector:
                    # Use XPath for text-based selection
                    text = selector.split(':contains(')[1][1:-2]
                    xpath = f"//*[contains(text(), '{text}')]"
                    element = self.driver.find_element(By.XPATH, xpath)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                job_data[key] = element.text.strip() if element.text else element.get_attribute("innerHTML").strip()
                
                # Clean up the text
                if len(job_data[key]) > 100:
                    job_data[key] = job_data[key][:100] + "..."
                    
            except Exception as e:
                job_data[key] = 'N/A'
        
        return f"{count} | {job_data['title']} | {job_data['company']} | {job_data['location']} | {job_data['workplace']} | {job_data['posted_date']} | {job_data['applications']}"

    def easyApplyButton(self):
        """Find Easy Apply button with multiple selectors"""
        selectors = [
            "button[aria-label*='Easy Apply']",
            "button:contains('Easy Apply')",
            ".jobs-apply-button",
            "button[data-job-id]"
        ]
        
        for selector in selectors:
            try:
                if ':contains' in selector:
                    xpath = "//button[contains(text(), 'Easy Apply')]"
                    button = self.driver.find_element(By.XPATH, xpath)
                else:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                if button.is_enabled():
                    return button
            except:
                continue
                
        return None

# Usage
if __name__ == "__main__":
    # Required installations:
    """
    pip install PyPDF2 python-docx requests selenium
    
    # Install and setup Ollama:
    # 1. Install Ollama from https://ollama.ai
    # 2. Pull a model: ollama pull llama3
    # 3. Start the server: ollama serve
    """
    
    # CV File Setup:
    """
    Place your CV file in the same directory as this script with one of these names:
    - cv.pdf, resume.pdf, CV.pdf, Resume.pdf
    - cv.docx, resume.docx, CV.docx, Resume.docx  
    - cv.txt, resume.txt, CV.txt, Resume.txt
    
    Or specify custom path in config.py:
    cv_path = "path/to/your/cv.pdf"
    """
    
    # Optional: Minimal config.py (most data will be extracted from CV):
    """
    # config.py - Only these are required now:
    browser = ["chrome"]  # or ["firefox"]
    email = "your.linkedin.email@gmail.com"
    password = "your_linkedin_password"
    
    # Optional overrides (will use CV data if not specified):
    availability = "Immediately"
    salary_expectation = "As per company standards" 
    notice_period = "30 days"
    visa_status = "Indian Citizen"
    willing_to_relocate = True
    followCompanies = False
    cv_path = "my_resume.pdf"  # Custom CV path if needed
    """
    
    print("🚀 Starting LinkedIn Job Application Bot with AI CV Analysis...")
    bot = StealthLinkedin()
    bot.enhanced_job_application_flow()