"""
Enhanced Utilities for LinkedIn Job Application Bot
Provides helper functions and data management
"""

import os
import json
import csv
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus, unquote_plus

class DataManager:
    """Manages application data and session persistence"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/exports", exist_ok=True)
        os.makedirs(f"{self.data_dir}/logs", exist_ok=True)
    
    def save_job_urls(self, urls: List[str], filename: str = "job_urls.txt"):
        """Save job URLs to file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
            self.logger.info(f"💾 Saved {len(urls)} URLs to {filepath}")
        except Exception as e:
            self.logger.error(f"❌ Error saving URLs: {e}")
    
    def load_job_urls(self, filename: str = "job_urls.txt") -> List[str]:
        """Load job URLs from file"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"📂 Loaded {len(urls)} URLs from {filepath}")
            return urls
        except Exception as e:
            self.logger.error(f"❌ Error loading URLs: {e}")
            return []
    
    def save_applied_jobs(self, jobs: List[Dict], filename: str = None):
        """Save applied jobs data"""
        if filename is None:
            filename = f"applied_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            filepath = os.path.join(self.data_dir, "exports", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, default=str, ensure_ascii=False)
            self.logger.info(f"💾 Saved {len(jobs)} job applications to {filepath}")
        except Exception as e:
            self.logger.error(f"❌ Error saving job applications: {e}")
    
    def export_to_csv(self, jobs: List[Dict], filename: str = None):
        """Export job applications to CSV"""
        if not jobs:
            return
        
        if filename is None:
            filename = f"applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            filepath = os.path.join(self.data_dir, "exports", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
            
            self.logger.info(f"📊 Exported {len(jobs)} applications to CSV: {filepath}")
        except Exception as e:
            self.logger.error(f"❌ Error exporting to CSV: {e}")
    
    def load_previous_applications(self, days: int = 7) -> List[str]:
        """Load job IDs from previous applications within specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            applied_job_ids = set()
            
            # Look for recent application files
            exports_dir = os.path.join(self.data_dir, "exports")
            if os.path.exists(exports_dir):
                for file in os.listdir(exports_dir):
                    if file.startswith("applied_jobs_") and file.endswith(".json"):
                        try:
                            file_date_str = file.replace("applied_jobs_", "").replace(".json", "")
                            file_date = datetime.strptime(file_date_str[:8], "%Y%m%d")
                            
                            if file_date >= cutoff_date:
                                filepath = os.path.join(exports_dir, file)
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                    for job in data:
                                        if isinstance(job, dict) and 'job_id' in job:
                                            applied_job_ids.add(job['job_id'])
                        except:
                            continue
            
            self.logger.info(f"📋 Loaded {len(applied_job_ids)} previously applied job IDs")
            return list(applied_job_ids)
        
        except Exception as e:
            self.logger.error(f"❌ Error loading previous applications: {e}")
            return []

class URLGenerator:
    """Generates LinkedIn job search URLs with various filters"""
    
    BASE_URL = "https://www.linkedin.com/jobs/search/?"
    
    @staticmethod
    def generate_search_url(keyword: str, location: str, filters: Dict = None) -> str:
        """Generate a LinkedIn job search URL with filters"""
        params = {
            'keywords': keyword,
            'location': location,
            'f_AL': 'true'  # Easy Apply only
        }
        
        if filters:
            # Date posted filter
            date_map = {
                'Past 24 hours': 'r86400',
                'Past Week': 'r604800', 
                'Past Month': 'r2592000',
                'Any Time': ''
            }
            if 'date_posted' in filters:
                date_filter = date_map.get(filters['date_posted'])
                if date_filter:
                    params['f_TPR'] = date_filter
            
            # Experience level filter
            exp_map = {
                'Internship': '1',
                'Entry level': '2',
                'Associate': '3', 
                'Mid-Senior level': '4',
                'Director': '5',
                'Executive': '6'
            }
            if 'experience_levels' in filters:
                exp_codes = [exp_map.get(level) for level in filters['experience_levels'] if level in exp_map]
                if exp_codes:
                    params['f_E'] = ','.join(exp_codes)
            
            # Job type filter
            jt_map = {
                'Full-time': '1',
                'Part-time': '2',
                'Contract': '3',
                'Temporary': '4',
                'Volunteer': '5',
                'Internship': '6',
                'Other': '7'
            }
            if 'job_types' in filters:
                jt_codes = [jt_map.get(jtype) for jtype in filters['job_types'] if jtype in jt_map]
                if jt_codes:
                    params['f_JT'] = ','.join(jt_codes)
            
            # Remote work filter
            wt_map = {
                'On-site': '1',
                'Remote': '2', 
                'Hybrid': '3'
            }
            if 'remote_types' in filters:
                wt_codes = [wt_map.get(rtype) for rtype in filters['remote_types'] if rtype in wt_map]
                if wt_codes:
                    params['f_WT'] = ','.join(wt_codes)
            
            # Salary filter
            salary_map = {
                '$40,000+': '1', '$60,000+': '2', '$80,000+': '3', '$100,000+': '4',
                '$120,000+': '5', '$140,000+': '6', '$160,000+': '7', '$180,000+': '8', '$200,000+': '9'
            }
            if 'salary_range' in filters and filters['salary_range'] in salary_map:
                params['f_SB2'] = salary_map[filters['salary_range']]
            
            # Sort filter
            if 'sort_by' in filters:
                if filters['sort_by'] == 'Recent':
                    params['sortBy'] = 'DD'  # Date Descending
                elif filters['sort_by'] == 'Relevant':
                    params['sortBy'] = 'R'   # Relevance
        
        # Build URL
        url_params = '&'.join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        return f"{URLGenerator.BASE_URL}{url_params}"

class TextProcessor:
    """Processes and analyzes text content"""
    
    @staticmethod
    def extract_skills_from_text(text: str, skill_database: List[str]) -> List[str]:
        """Extract skills from text using skill database"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_database:
            skill_lower = skill.lower()
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def extract_experience_years(text: str) -> int:
        """Extract years of experience from text"""
        text_lower = text.lower()
        
        # Look for patterns like "5 years", "3+ years", "2-4 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s+)?(?:experience|exp)',
            r'(\d+)\s*to\s*\d+\s*years?',
            r'(\d+)-\d+\s*years?',
            r'(\d+)\s*yrs?'
        ]
        
        max_years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = [int(match) for match in matches if match.isdigit()]
                if years:
                    max_years = max(max_years, max(years))
        
        return max_years
    
    @staticmethod
    def extract_salary_range(text: str) -> str:
        """Extract salary information from text"""
        # Look for salary patterns
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?',
            r'(\d+)\s*-?\s*(\d+)?\s*(?:k|thousand)',
            r'(\d+)\s*lpa',  # Indian LPA format
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lpa|lakhs?)'
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return text  # Return original text for now
        
        return ""
    
    @staticmethod
    def clean_company_name(company_name: str) -> str:
        """Clean and normalize company name"""
        if not company_name:
            return ""
        
        # Remove common suffixes
        suffixes = [' Inc', ' Inc.', ' LLC', ' Ltd', ' Ltd.', ' Corp', ' Corp.', 
                   ' Company', ' Co.', ' Co', ' Private Limited', ' Pvt Ltd']
        
        cleaned = company_name.strip()
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
        
        return cleaned
    
    @staticmethod
    def normalize_job_title(title: str) -> str:
        """Normalize job title for comparison"""
        if not title:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = ' '.join(title.lower().split())
        
        # Remove common variations
        variations = {
            'sr.': 'senior',
            'sr': 'senior', 
            'jr.': 'junior',
            'jr': 'junior',
            'dev': 'developer',
            'eng': 'engineer',
            'mgr': 'manager'
        }
        
        for abbrev, full in variations.items():
            normalized = normalized.replace(abbrev, full)
        
        return normalized

class StatisticsCalculator:
    """Calculates various statistics for job applications"""
    
    @staticmethod
    def calculate_success_rate(applications: List[Dict]) -> float:
        """Calculate application success rate"""
        if not applications:
            return 0.0
        
        successful = len([app for app in applications if app.get('status') == 'applied'])
        return (successful / len(applications)) * 100
    
    @staticmethod
    def get_top_companies(applications: List[Dict], top_n: int = 10) -> List[tuple]:
        """Get top companies by application count"""
        company_counts = {}
        
        for app in applications:
            company = app.get('company', 'Unknown')
            company_counts[company] = company_counts.get(company, 0) + 1
        
        return sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    @staticmethod
    def get_application_trends(applications: List[Dict]) -> Dict:
        """Get application trends by date"""
        trends = {}
        
        for app in applications:
            app_date = app.get('application_date', '')
            if isinstance(app_date, str):
                try:
                    date_obj = datetime.fromisoformat(app_date.replace('Z', '+00:00'))
                    date_key = date_obj.strftime('%Y-%m-%d')
                    trends[date_key] = trends.get(date_key, 0) + 1
                except:
                    continue
        
        return trends
    
    @staticmethod
    def calculate_avg_fields_filled(applications: List[Dict]) -> float:
        """Calculate average form fields filled per application"""
        if not applications:
            return 0.0
        
        total_fields = sum(app.get('form_fields_filled', 0) for app in applications)
        return total_fields / len(applications)

class ReportGenerator:
    """Generates various reports from application data"""
    
    @staticmethod
    def generate_summary_report(applications: List[Dict]) -> str:
        """Generate a comprehensive summary report"""
        if not applications:
            return "No application data available."
        
        stats = StatisticsCalculator()
        
        total_apps = len(applications)
        success_rate = stats.calculate_success_rate(applications)
        top_companies = stats.get_top_companies(applications, 5)
        avg_fields = stats.calculate_avg_fields_filled(applications)
        
        # Status breakdown
        status_counts = {}
        for app in applications:
            status = app.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report = f"""
📊 JOB APPLICATION SUMMARY REPORT
{'='*50}

📈 OVERALL STATISTICS:
  • Total Applications: {total_apps}
  • Success Rate: {success_rate:.1f}%
  • Average Fields Filled: {avg_fields:.1f}

📋 STATUS BREAKDOWN:
"""
        
        for status, count in status_counts.items():
            percentage = (count / total_apps) * 100
            report += f"  • {status.title()}: {count} ({percentage:.1f}%)\n"
        
        report += f"""
🏢 TOP COMPANIES APPLIED TO:
"""
        for i, (company, count) in enumerate(top_companies, 1):
            report += f"  {i}. {company}: {count} applications\n"
        
        return report

# Utility functions for backward compatibility
def getUrlDataFile():
    """Get URL data from file (backward compatibility)"""
    data_manager = DataManager()
    return data_manager.load_job_urls()

def jobsToPages(total_jobs: str) -> int:
    """Convert total jobs to pages (backward compatibility)"""
    try:
        # Extract number from string like "1,234 results"
        numbers = re.findall(r'\d+', total_jobs.replace(',', ''))
        if numbers:
            job_count = int(numbers[0])
            return min(job_count // 25 + 1, 10)  # 25 jobs per page, max 10 pages
    except:
        pass
    return 5  # Default

def urlToKeywords(url: str) -> str:
    """Extract keywords from URL (backward compatibility)"""
    try:
        if 'keywords=' in url:
            keyword_part = url.split('keywords=')[1].split('&')[0]
            return unquote_plus(keyword_part)
    except:
        pass
    return "Unknown"

# Additional utility functions
def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it contains only digits and + (for country code)
    return re.match(r'^\+?\d{10,15}$', cleaned) is not None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for file system"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    return filename[:100]