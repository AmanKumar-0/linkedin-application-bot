#!/usr/bin/env python3
"""
Enhanced LinkedIn Bot Launcher
Simple launcher with command-line options
"""

import argparse
import os
import sys
import logging
from pathlib import Path

def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Enhanced LinkedIn Job Application Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                    # Run with default settings
  python launcher.py --headless         # Run in background mode
  python launcher.py --debug            # Run with debug logging
  python launcher.py --dry-run          # Test mode (no actual applications)
  python launcher.py --max-apps 25      # Limit applications to 25
  python launcher.py --keywords "Python Developer,Data Scientist"
        """
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='user_config.py',
        help='Configuration file to use (default: user_config.py)'
    )
    
    parser.add_argument(
        '--headless', 
        action='store_true',
        help='Run browser in headless mode (background)'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Test mode - no actual job applications'
    )
    
    parser.add_argument(
        '--max-apps', 
        type=int,
        help='Maximum applications per session'
    )
    
    parser.add_argument(
        '--keywords', 
        type=str,
        help='Comma-separated job search keywords'
    )
    
    parser.add_argument(
        '--locations', 
        type=str,
        help='Comma-separated job locations'
    )
    
    parser.add_argument(
        '--setup', 
        action='store_true',
        help='Run setup wizard'
    )
    
    parser.add_argument(
        '--stats', 
        action='store_true',
        help='Show statistics from previous runs'
    )
    
    parser.add_argument(
        '--version', 
        action='version',
        version='Enhanced LinkedIn Bot v2.0'
    )
    
    return parser

def run_setup():
    """Run setup wizard"""
    try:
        import setup
        setup.main()
    except ImportError:
        print("❌ Setup module not found")
        return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    
    return True

def show_statistics():
    """Show statistics from previous runs"""
    try:
        from enhanced_utils import DataManager, ReportGenerator
        
        data_manager = DataManager()
        # Load recent application data
        # This is a simplified version - you'd implement the actual logic
        print("📊 Application Statistics")
        print("=" * 30)
        print("Feature coming soon...")
        
    except Exception as e:
        print(f"❌ Error loading statistics: {e}")

def validate_environment():
    """Validate environment and dependencies"""
    errors = []
    warnings = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append(f"Python 3.8+ required, got {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required modules
    required_modules = ['selenium', 'requests', 'PyPDF2', 'docx']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            errors.append(f"Required module '{module}' not found. Run: pip install {module}")
    
    # Check configuration
    if not os.path.exists('user_config.py'):
        warnings.append("user_config.py not found - using default configuration")
    
    # Check CV file
    cv_files = [f for f in os.listdir('.') if any(f.lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt']) and any(kw in f.lower() for kw in ['cv', 'resume'])]
    if not cv_files:
        warnings.append("No CV file found - place your CV (PDF/DOCX/TXT) in the current directory")
    
    return errors, warnings

def main():
    """Main launcher function"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Handle special commands
    if args.setup:
        return run_setup()
    
    if args.stats:
        return show_statistics()
    
    # Validate environment
    errors, warnings = validate_environment()
    
    if errors:
        print("❌ Environment Errors:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Run 'python launcher.py --setup' to fix these issues")
        return False
    
    if warnings:
        print("⚠️  Environment Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/bot.log')
        ]
    )
    
    try:
        # Import configuration
        if args.config and os.path.exists(args.config):
            # Dynamic import of custom config
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", args.config)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            config = config_module.config
        else:
            from config_enhanced import config
        
        # Apply command line overrides
        if args.headless:
            config.browser.headless = True
        
        if args.max_apps:
            config.application_prefs.max_applications_per_day = args.max_apps
        
        if args.keywords:
            config.job_search.keywords = [kw.strip() for kw in args.keywords.split(',')]
        
        if args.locations:
            config.job_search.locations = [loc.strip() for loc in args.locations.split(',')]
        
        if args.dry_run:
            print("🧪 DRY RUN MODE - No actual applications will be submitted")
            config.application_prefs.max_applications_per_day = 5  # Limit for testing
        
        # Validate configuration
        config_errors = config.validate()
        if config_errors:
            print("❌ Configuration Errors:")
            for error in config_errors:
                print(f"   - {error}")
            return False
        
        # Print startup info
        print("🚀 Enhanced LinkedIn Job Application Bot v2.0")
        print(f"👤 Profile: {config.personal_info.full_name}")
        print(f"🎯 Max Applications: {config.application_prefs.max_applications_per_day}")
        print(f"🔍 Keywords: {', '.join(config.job_search.keywords[:3])}...")
        print(f"🌍 Locations: {', '.join(config.job_search.locations[:3])}...")
        
        if args.dry_run:
            print("⚠️  DRY RUN MODE ACTIVE")
        
        print()
        
        # Import and run bot
        from linkedin_enhanced import EnhancedLinkedInBot
        
        bot = EnhancedLinkedInBot(config)
        bot.run_application_session()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Session interrupted by user")
        return False
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run 'python launcher.py --setup' to install dependencies")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)