# Enhanced LinkedIn Job Application Bot

An enterprise-grade LinkedIn job application bot with AI integration, advanced filtering, and comprehensive configuration options.

## 🚀 Features

### Core Features
- **AI-Powered CV Analysis**: Automatically extracts and analyzes your CV to understand your profile
- **Intelligent Form Filling**: Uses AI to respond to application questions contextually
- **Advanced Job Filtering**: Filter by company, title, salary, skills, and more
- **Multi-Step Application Handling**: Handles complex multi-step application forms
- **Smart Application Strategy**: Applies strategic logic to maximize acceptance chances

### Enhanced Capabilities
- **Comprehensive Configuration**: Extensive configuration options for personalization
- **Session Management**: Tracks applications and resumes from where you left off
- **Error Recovery**: Robust error handling and retry mechanisms
- **Rate Limiting**: Respects LinkedIn's rate limits to avoid detection
- **Statistics & Reporting**: Detailed statistics and exportable reports
- **Stealth Browser**: Enhanced stealth features to avoid bot detection

### Configuration Categories
- **Personal Information**: CV-extracted or manually configured profile data
- **Job Search Criteria**: Keywords, locations, experience levels, job types
- **Application Preferences**: Relocation willingness, visa status, salary expectations
- **Filtering Options**: Company blacklists/whitelists, title filters, skill requirements
- **Browser Settings**: Stealth options, timing configurations, headless mode
- **AI Integration**: Ollama configuration, model selection, response customization

## 📋 Prerequisites

### Required Software
```bash
# Python 3.8+
python --version

# Browser drivers (Chrome recommended)
# Chrome: Download from https://chromedriver.chromium.org/
# Firefox: Download from https://github.com/mozilla/geckodriver/

# Ollama AI (for intelligent responses)
# Install from: https://ollama.ai
# Then pull a model: ollama pull qwen2.5:7b
```

### Required Python Packages
```bash
pip install selenium requests PyPDF2 python-docx
```

## 🛠️ Installation & Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd linkedin-application-bot
pip install -r requirements.txt
```

### 2. Configure CV Path
Place your CV file in the project directory or specify the path:
- Supported formats: PDF, DOCX, TXT
- Default names: `cv.pdf`, `resume.pdf`, `CV.pdf`, etc.

### 3. Setup Ollama (AI Integration)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (recommended)
ollama pull qwen2.5:7b

# Start Ollama server
ollama serve
```

### 4. Configure Settings
Copy and customize the configuration:
```bash
cp user_config_template.py user_config.py
# Edit user_config.py with your preferences
```

### 5. Set LinkedIn Credentials
**Option A: Environment Variables (Recommended)**
```bash
export LINKEDIN_EMAIL="your.email@gmail.com"
export LINKEDIN_PASSWORD="your_password"
```

**Option B: Configuration File**
Edit `user_config.py`:
```python
config.security.linkedin_email = "your.email@gmail.com" 
config.security.linkedin_password = "your_password"
```

## ⚙️ Configuration Guide

### Personal Information
```python
config.personal_info.full_name = "Your Name"
config.personal_info.email = "your.email@gmail.com"
config.personal_info.phone = "+1-XXX-XXX-XXXX"
config.personal_info.location = "Your City, Country"
config.personal_info.experience_years = 5
config.personal_info.current_salary = "80000"  # Current salary
config.personal_info.salary_expectation = "100000"  # Expected salary
config.personal_info.notice_period = "30"  # Days
config.personal_info.visa_status = "US Citizen"  # or "Requires Sponsorship"
```

### Job Search Criteria
```python
config.job_search.keywords = [
    "Software Engineer", "Full Stack Developer", "Python Developer"
]
config.job_search.locations = [
    "United States", "Canada", "Remote"
]
config.job_search.experience_levels = [
    ExperienceLevel.MID_SENIOR, ExperienceLevel.SENIOR
]
config.job_search.job_types = [JobType.FULL_TIME, JobType.CONTRACT]
config.job_search.remote_types = [RemoteType.REMOTE, RemoteType.HYBRID]
config.job_search.salary_range = "$80,000+"
```

### Application Preferences
```python
config.application_prefs.willing_to_relocate = True
config.application_prefs.requires_visa_sponsorship = False
config.application_prefs.max_applications_per_day = 50
config.application_prefs.delay_between_applications = (30, 60)  # seconds

# Smart responses to common questions
config.application_prefs.default_responses = {
    "authorized_to_work": True,
    "require_sponsorship": False, 
    "willing_to_relocate": True,
    "years_of_experience": "5",
    "notice_period": "30 days",
    "degree_completed": True,
    "english_proficiency": "Native",
    "remote_work": True
}
```

### Advanced Filtering
```python
# Companies to avoid
config.filtering.blacklisted_companies = [
    "Company A", "Company B"
]

# Only apply to these companies (empty = all companies)
config.filtering.whitelisted_companies = [
    "Preferred Company", "Dream Company"
]

# Job titles to avoid
config.filtering.blacklisted_titles = [
    "manager", "sales", "marketing", "junior"
]

# Required skills in job description
config.filtering.required_skills = ["python", "javascript"]

# Skills to avoid
config.filtering.avoided_skills = [".NET", "PHP", "Java"]

# Salary range (USD)
config.filtering.min_salary = 70000
config.filtering.max_salary = 150000
```

### Browser & Stealth Settings
```python
config.browser.browser = "chrome"  # or "firefox"
config.browser.headless = False  # True for background operation
config.browser.enable_stealth = True
config.browser.human_delay = (1, 3)  # Random delays
config.browser.typing_delay = 0.1  # Delay between keystrokes
```

## 🎯 Usage

### Basic Usage
```bash
python linkedin_enhanced.py
```

### Advanced Usage
```python
from linkedin_enhanced import EnhancedLinkedInBot
from config_enhanced import config

# Customize configuration programmatically
config.application_prefs.max_applications_per_day = 25
config.job_search.keywords = ["Python Developer", "Data Scientist"]

# Create and run bot
bot = EnhancedLinkedInBot(config)
bot.run_application_session()
```

### Command Line Options
```bash
# Run with custom config
python linkedin_enhanced.py --config my_config.py

# Headless mode
python linkedin_enhanced.py --headless

# Debug mode
python linkedin_enhanced.py --debug
```

## 📊 Output & Reports

### Session Statistics
```
📊 SESSION SUMMARY
==========================================
⏱️  Duration: 45.2 minutes
📋 Total Jobs Processed: 127
✅ Successful Applications: 23
❌ Failed Applications: 8
⏭️  Skipped Applications: 96
📈 Success Rate: 18.1%
```

### Data Exports
- **CSV Export**: `data/exports/applications_YYYYMMDD_HHMMSS.csv`
- **JSON Export**: `data/exports/applied_jobs_YYYYMMDD_HHMMSS.json`
- **Session Data**: `data/session_data.json`

### Application Tracking
```csv
Job ID,Title,Company,Location,Status,Date,Reason
123456,Software Engineer,Tech Corp,Remote,applied,2024-01-15,Success
789012,Python Developer,StartupCo,NYC,failed,2024-01-15,Form error
```

## 🤖 AI Integration

### Supported Models
- **Qwen 2.5** (Recommended): `qwen2.5:7b`, `qwen2.5:14b`
- **Llama 3**: `llama3:8b`, `llama3:70b`
- **Mistral**: `mistral:7b`, `mistral:latest`
- **CodeLlama**: `codellama:7b`, `codellama:13b`

### AI Response Categories
- **Experience Questions**: Automatically uses CV data
- **Work Authorization**: Based on visa status configuration
- **Salary Questions**: Uses configured salary ranges
- **Relocation**: Based on willingness to relocate
- **Skills Questions**: Matches against CV skills
- **Education**: Based on CV education data

### Custom AI Responses
```python
# Override AI responses for specific questions
config.application_prefs.default_responses.update({
    "management_experience": "3 years",
    "team_size_managed": "5-8 people",
    "budget_responsibility": "$500K annually",
    "security_clearance": "No",
    "overtime_availability": "Yes, when needed"
})
```

## 🔧 Troubleshooting

### Common Issues

**1. Login Issues**
```
❌ Login failed - unexpected redirect
```
- **Solution**: Check credentials, handle 2FA manually, clear browser data

**2. CV Analysis Failed**
```
❌ Error analyzing CV with AI: Connection refused
```
- **Solution**: Ensure Ollama is running (`ollama serve`)

**3. Rate Limiting**
```
⚠️ Request rate limit exceeded
```
- **Solution**: Increase delays in configuration, use different IP

**4. Form Filling Errors**
```
❌ Could not fill form field
```
- **Solution**: Check AI model, update response templates

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose logging
config.logging.log_level = "DEBUG"
```

### Browser Issues
```python
# Use different browser
config.browser.browser = "firefox"

# Disable headless mode for debugging
config.browser.headless = False

# Increase timeouts
config.browser.page_load_timeout = 60
config.browser.element_timeout = 20
```

## 🛡️ Security & Privacy

### Best Practices
- Use environment variables for credentials
- Enable 2FA on LinkedIn account
- Use VPN for IP rotation
- Monitor application patterns
- Respect rate limits

### Stealth Features
- Random delays between actions
- Human-like typing patterns
- User agent rotation
- JavaScript execution delays
- Cookie management

### Data Security
- Local data storage only
- No cloud dependencies
- Encrypted credential storage option
- Session data cleanup

## 📈 Performance Optimization

### Speed Optimization
```python
# Faster processing
config.browser.headless = True
config.browser.typing_delay = 0.05
config.application_prefs.delay_between_applications = (15, 30)

# Disable images for faster loading
config.browser.load_images = False
```

### Accuracy Optimization
```python
# Better form filling
config.ai.temperature = 0.1  # More consistent responses
config.browser.typing_delay = 0.2  # More human-like typing
config.browser.element_timeout = 15  # Wait longer for elements
```

### Resource Management
```python
# Memory optimization
config.application_prefs.max_applications_per_day = 25
config.logging.save_screenshots = False
config.browser.clear_cache_interval = 50  # Clear cache every 50 applications
```

## 🤝 Contributing

### Development Setup
```bash
git clone <repository-url>
cd linkedin-application-bot
pip install -r requirements-dev.txt
pre-commit install
```

### Testing
```bash
python -m pytest tests/
python -m pytest tests/test_cv_analyzer.py -v
```

### Code Style
```bash
black . 
isort .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and personal use only. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Respecting rate limits and usage policies  
- Ensuring accuracy of submitted information
- Following applicable laws and regulations

The authors are not responsible for any consequences arising from the use of this software.

## 🆘 Support

### Getting Help
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check the wiki

### Reporting Bugs
Include:
- Python version and OS
- Configuration (anonymized)
- Error logs and screenshots
- Steps to reproduce

### Feature Requests
- Describe the use case
- Explain expected behavior
- Provide examples if possible