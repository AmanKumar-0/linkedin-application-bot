"""
User Configuration Override File
Copy this to 'user_config.py' and customize your settings
"""

from config_enhanced import *

# ============================================================================
# PERSONAL INFORMATION (Override CV data if needed)
# ============================================================================

# If you want to override any information from your CV, uncomment and modify:
config.personal_info.full_name = "Aman Kumar Huriya"
config.personal_info.email = "amanhuriya2@gmail.com"
config.personal_info.phone = "+91-7982473942"
config.personal_info.location = "Bangalore, India"
config.personal_info.current_title = "Senior Software Engineer"
config.personal_info.experience_years = 4
config.personal_info.current_salary = "18"  # LPA
config.personal_info.salary_expectation = "27"  # LPA
config.personal_info.notice_period = "30"  # Days
config.personal_info.visa_status = "Indian Citizen"

# ============================================================================
# JOB SEARCH CRITERIA
# ============================================================================

# Job search keywords (will be combined with CV analysis)
config.job_search.keywords = [
    "Software Engineer", "Full Stack Developer", "Senior Software Engineer",
    "Tech Lead", "Backend Developer", "Frontend Developer", "Python Developer",
    "JavaScript Developer", "React Developer", "Node.js Developer"
]

# Preferred locations
config.job_search.locations = [
    "India", "United States", "Canada", "United Kingdom", "Germany", 
    "Singapore", "Australia", "Netherlands", "Remote"
]

# Experience levels to apply for
config.job_search.experience_levels = [
    ExperienceLevel.MID_SENIOR,
    ExperienceLevel.ASSOCIATE,
    ExperienceLevel.DIRECTOR
]

# Job types
config.job_search.job_types = [
    JobType.FULL_TIME,
    JobType.CONTRACT
]

# Remote work preferences
config.job_search.remote_types = [
    RemoteType.REMOTE,
    RemoteType.HYBRID,
    RemoteType.ON_SITE
]

# Date posted filter
config.job_search.date_posted = DatePosted.PAST_WEEK

# Salary range
config.job_search.salary_range = "$60,000+"

# ============================================================================
# APPLICATION PREFERENCES
# ============================================================================

config.application_prefs.willing_to_relocate = True
config.application_prefs.willing_to_work_remotely = True
config.application_prefs.requires_visa_sponsorship = True  # Set to False if you don't need sponsorship
config.application_prefs.follow_companies = False
config.application_prefs.max_applications_per_day = 50
config.application_prefs.delay_between_applications = (30, 60)  # seconds
config.application_prefs.auto_skip_complex_forms = False

# Default responses to common questions
config.application_prefs.default_responses.update({
    "authorized_to_work": False,  # Change to True if you're authorized
    "require_sponsorship": True,   # Change to False if you don't need sponsorship
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

# ============================================================================
# FILTERING CRITERIA
# ============================================================================

# Companies to avoid
config.filtering.blacklisted_companies = [
    "Apple", "Google", "Microsoft", "Amazon", "Facebook", "Meta", "Netflix",
    "IBM", "Salesforce", "Oracle", "SAP", "Intel", "Cisco", "Adobe",
    "Accenture", "Capgemini", "TCS", "Cognizant", "Infosys", "Wipro", "HCL"
]

# Only apply to these companies (leave empty for all companies)
config.filtering.whitelisted_companies = [
    # "Startup Company", "Preferred Company"
]

# Job titles to avoid
config.filtering.blacklisted_titles = [
    "manager", "sales", "marketing", "hr", "recruiter", "intern", "junior",
    ".net", "c#", "java developer", "php developer"
]

# Only apply to jobs with these titles (leave empty for all titles)
config.filtering.whitelisted_titles = [
    # "senior", "lead", "architect", "principal"
]

# Skills that must be present in job description
config.filtering.required_skills = [
    # "python", "javascript", "react"
]

# Skills to avoid in job description
config.filtering.avoided_skills = [
    ".NET", "C#", "Java", "PHP", "Ruby", "COBOL", "Fortran"
]

# Salary range preferences (USD)
config.filtering.min_salary = 60000
config.filtering.max_salary = 200000

# ============================================================================
# BROWSER CONFIGURATION
# ============================================================================

config.browser.browser = "chrome"  # or "firefox"
config.browser.headless = False  # Set to True to run without GUI
config.browser.enable_stealth = True
config.browser.window_size = (1920, 1080)

# Timing configurations
config.browser.page_load_timeout = 30
config.browser.element_timeout = 10
config.browser.typing_delay = 0.1
config.browser.human_delay = (1, 3)

# ============================================================================
# AI CONFIGURATION
# ============================================================================

config.ai.ollama_url = "http://localhost:11434"
config.ai.model = "qwen2.5:7b"  # or "llama3", "mistral", etc.
config.ai.cv_path = "/Users/amankumar/Desktop/Aman Kumar Huriya CV .pdf"
config.ai.temperature = 0.1
config.ai.enable_cover_letter_generation = True

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# LinkedIn credentials (better to use environment variables)
config.security.linkedin_email = "amanhuriya2@gmail.com"
config.security.linkedin_password = "Testings@321"

# Security settings
config.security.enable_2fa_detection = True
config.security.max_requests_per_minute = 30
config.security.cooldown_on_detection = 300  # seconds

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

config.logging.log_level = "INFO"  # DEBUG, INFO, WARNING, ERROR
config.logging.save_screenshots = True
config.logging.export_applied_jobs = True
config.logging.export_format = "csv"  # csv, json, xlsx