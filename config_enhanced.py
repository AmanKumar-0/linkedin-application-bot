"""
Enhanced Configuration for LinkedIn Job Application Bot
All settings in one place for better maintainability
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum

class ExperienceLevel(Enum):
    INTERNSHIP = "Internship"
    ENTRY_LEVEL = "Entry level"
    ASSOCIATE = "Associate"
    MID_SENIOR = "Mid-Senior level"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"

class JobType(Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    VOLUNTEER = "Volunteer"
    INTERNSHIP = "Internship"
    OTHER = "Other"

class RemoteType(Enum):
    ON_SITE = "On-site"
    REMOTE = "Remote"
    HYBRID = "Hybrid"

class DatePosted(Enum):
    ANY_TIME = "Any Time"
    PAST_MONTH = "Past Month"
    PAST_WEEK = "Past Week"
    PAST_24_HOURS = "Past 24 hours"

class SortBy(Enum):
    RECENT = "Recent"
    RELEVANT = "Relevant"

@dataclass
class PersonalInfo:
    """Personal information extracted from CV or manual input"""
    full_name: str = "Aman Kumar Huriya"
    email: str = "amanhuriya2@gmail.com"
    phone: str = "+91-7982473942"
    country_code: str = "IN"
    location: str = "Bangalore, India"
    current_title: str = "Senior Software Engineer"
    experience_years: int = 4
    education: str = "Bachelor in Computer Science"
    current_salary: str = "18"  # LPA
    salary_expectation: str = "27"  # LPA
    notice_period: str = "30"  # Days
    visa_status: str = "Indian Citizen"
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    skills: List[str] = field(default_factory=lambda: [
        "Python", "JavaScript", "React", "Node.js", "SQL", "AWS", "Docker", "Git"
    ])
    languages: List[str] = field(default_factory=lambda: ["English", "Hindi"])
    certifications: List[str] = field(default_factory=list)

@dataclass
class JobSearchCriteria:
    """Job search preferences and filters"""
    keywords: List[str] = field(default_factory=lambda: [
        "Software Engineer", "Full Stack Developer", "Senior Software Engineer",
        "Tech Lead", "Backend Developer", "Frontend Developer", "Python Developer"
    ])
    locations: List[str] = field(default_factory=lambda: [
        "India", "United States", "Canada", "United Kingdom", "Germany", "Singapore"
    ])
    experience_levels: List[ExperienceLevel] = field(default_factory=lambda: [
        ExperienceLevel.MID_SENIOR, ExperienceLevel.ASSOCIATE, ExperienceLevel.DIRECTOR
    ])
    job_types: List[JobType] = field(default_factory=lambda: [
        JobType.FULL_TIME, JobType.CONTRACT
    ])
    remote_types: List[RemoteType] = field(default_factory=lambda: [
        RemoteType.REMOTE, RemoteType.HYBRID, RemoteType.ON_SITE
    ])
    date_posted: DatePosted = DatePosted.PAST_WEEK
    sort_by: SortBy = SortBy.RECENT
    salary_range: Optional[str] = "$60,000+"
    company_size: List[str] = field(default_factory=lambda: ["51-200", "201-500", "501-1000", "1001-5000"])

@dataclass
class ApplicationPreferences:
    """Application behavior preferences"""
    willing_to_relocate: bool = True
    willing_to_work_remotely: bool = True
    requires_visa_sponsorship: bool = True
    follow_companies: bool = False
    max_applications_per_day: int = 50
    delay_between_applications: tuple = (30, 60)  # seconds
    auto_skip_complex_forms: bool = False
    save_application_data: bool = True
    
    # Question-specific responses
    default_responses: Dict[str, Union[str, bool]] = field(default_factory=lambda: {
        "authorized_to_work": False,  # Need sponsorship
        "require_sponsorship": True,
        "willing_to_relocate": True,
        "years_of_experience": "4",
        "notice_period": "30 days",
        "current_salary": "18 LPA",
        "expected_salary": "27 LPA",
        "degree_completed": True,
        "english_proficiency": "Professional",
        "available_for_interview": True,
        "start_date": "30 days",
        "remote_work": True,
        "travel_percentage": "25%",
        "management_experience": "2 years"
    })

@dataclass
class FilteringCriteria:
    """Advanced filtering options"""
    # Companies to avoid
    blacklisted_companies: List[str] = field(default_factory=lambda: [
        "Apple", "Google", "Microsoft", "Amazon", "Facebook", "Meta", "Netflix",
        "IBM", "Salesforce", "Oracle", "SAP", "Intel", "Cisco", "Adobe"
    ])
    
    # Only apply to these companies (empty = all companies)
    whitelisted_companies: List[str] = field(default_factory=list)
    
    # Job titles to avoid
    blacklisted_titles: List[str] = field(default_factory=lambda: [
        "manager", "sales", "marketing", "hr", "recruiter", "intern"
    ])
    
    # Only apply to jobs with these titles (empty = all titles)
    whitelisted_titles: List[str] = field(default_factory=list)
    
    # Skills that must be present in job description
    required_skills: List[str] = field(default_factory=list)
    
    # Skills to avoid in job description
    avoided_skills: List[str] = field(default_factory=lambda: [
        ".NET", "C#", "Java", "PHP", "Ruby"
    ])
    
    # Minimum and maximum salary expectations
    min_salary: Optional[int] = 60000  # USD
    max_salary: Optional[int] = 200000  # USD
    
    # Company size preferences
    preferred_company_sizes: List[str] = field(default_factory=lambda: [
        "51-200", "201-500", "501-1000"  # Avoid very small or very large companies
    ])

@dataclass
class BrowserConfig:
    """Browser and automation settings"""
    browser: str = "chrome"  # chrome or firefox
    headless: bool = False
    user_data_dir: str = ""
    firefox_profile_dir: str = ""
    window_size: tuple = (1920, 1080)
    enable_stealth: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Delays and timing
    page_load_timeout: int = 30
    element_timeout: int = 10
    typing_delay: float = 0.1
    human_delay: tuple = (1, 3)  # min, max seconds

@dataclass
class AIConfig:
    """AI integration settings"""
    ollama_url: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    cv_path: str = "cv.pdf"
    temperature: float = 0.1
    max_tokens: int = 1000
    timeout: int = 30
    
    # AI response customization
    response_style: str = "professional"  # professional, casual, enthusiastic
    cover_letter_template: str = ""
    enable_cover_letter_generation: bool = True

@dataclass
class LoggingConfig:
    """Logging and data persistence settings"""
    log_level: str = "INFO"
    log_file: str = "linkedin_bot.log"
    save_screenshots: bool = True
    screenshot_dir: str = "screenshots"
    data_dir: str = "data"
    
    # Export settings
    export_applied_jobs: bool = True
    export_format: str = "csv"  # csv, json, xlsx
    include_job_descriptions: bool = True

@dataclass
class SecurityConfig:
    """Security and privacy settings"""
    linkedin_email: str = "amanhuriya2@gmail.com"
    linkedin_password: str = "Testings@321"
    enable_2fa_detection: bool = True
    proxy_url: str = ""
    rotate_user_agents: bool = True
    clear_cookies_on_start: bool = False
    
    # Rate limiting
    max_requests_per_minute: int = 30
    cooldown_on_detection: int = 300  # seconds

class EnhancedConfig:
    """Main configuration class combining all settings"""
    
    def __init__(self):
        self.personal_info = PersonalInfo()
        self.job_search = JobSearchCriteria()
        self.application_prefs = ApplicationPreferences()
        self.filtering = FilteringCriteria()
        self.browser = BrowserConfig()
        self.ai = AIConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        
        # Load from environment variables if available
        self._load_from_env()
        
        # Load from file if exists
        self._load_from_file()
    
    def _load_from_env(self):
        """Load sensitive data from environment variables"""
        if os.getenv("LINKEDIN_EMAIL"):
            self.security.linkedin_email = os.getenv("LINKEDIN_EMAIL")
        if os.getenv("LINKEDIN_PASSWORD"):
            self.security.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        if os.getenv("OLLAMA_URL"):
            self.ai.ollama_url = os.getenv("OLLAMA_URL")
    
    def _load_from_file(self):
        """Load configuration from external file if exists"""
        config_file = "user_config.py"
        if os.path.exists(config_file):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("user_config", config_file)
                user_config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(user_config)
                
                # Update configuration with user overrides
                for attr_name in dir(user_config):
                    if not attr_name.startswith('_'):
                        setattr(self, attr_name, getattr(user_config, attr_name))
            except Exception as e:
                print(f"Warning: Could not load user config: {e}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.security.linkedin_email:
            errors.append("LinkedIn email is required")
        if not self.security.linkedin_password:
            errors.append("LinkedIn password is required")
        if not self.personal_info.full_name:
            errors.append("Full name is required")
        if not self.job_search.keywords:
            errors.append("At least one job keyword is required")
        if not self.job_search.locations:
            errors.append("At least one location is required")
        
        return errors
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary for serialization"""
        return {
            "personal_info": self.personal_info.__dict__,
            "job_search": {
                **self.job_search.__dict__,
                "experience_levels": [e.value for e in self.job_search.experience_levels],
                "job_types": [jt.value for jt in self.job_search.job_types],
                "remote_types": [rt.value for rt in self.job_search.remote_types],
                "date_posted": self.job_search.date_posted.value,
                "sort_by": self.job_search.sort_by.value
            },
            "application_prefs": self.application_prefs.__dict__,
            "filtering": self.filtering.__dict__,
            "browser": self.browser.__dict__,
            "ai": self.ai.__dict__,
            "logging": self.logging.__dict__
        }

# Global configuration instance
config = EnhancedConfig()

# Backward compatibility - expose old config format
browser = [config.browser.browser]
email = config.security.linkedin_email
password = config.security.linkedin_password
location = config.job_search.locations
keywords = config.job_search.keywords
experienceLevels = [e.value for e in config.job_search.experience_levels]
datePosted = [config.job_search.date_posted.value]
jobType = [jt.value for jt in config.job_search.job_types]
remote = [rt.value for rt in config.job_search.remote_types]
salary = [config.job_search.salary_range] if config.job_search.salary_range else []
sort = [config.job_search.sort_by.value]
blacklist = config.filtering.blacklisted_companies
blackListTitles = config.filtering.blacklisted_titles
onlyApply = config.filtering.whitelisted_companies
onlyApplyTitles = config.filtering.whitelisted_titles
followCompanies = config.application_prefs.follow_companies
country_code = config.personal_info.country_code
phone_number = config.personal_info.phone.replace("+", "").replace("-", "")
headless = config.browser.headless
firefoxProfileRootDir = config.browser.firefox_profile_dir

# AI and personal info for backward compatibility
notice_period = config.personal_info.notice_period
visa_status = config.personal_info.visa_status
willing_to_relocate = config.application_prefs.willing_to_relocate
cv_path = config.ai.cv_path
current_salary = config.personal_info.current_salary
salary_expectation = config.personal_info.salary_expectation
experience_years = str(config.personal_info.experience_years)
full_name = config.personal_info.full_name
phone = config.personal_info.phone
current_title = config.personal_info.current_title
education = config.personal_info.education
skills = config.personal_info.skills