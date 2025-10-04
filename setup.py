"""
Installation and Setup Script for Enhanced LinkedIn Bot
Automates the setup process and dependency installation
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🚀 Enhanced LinkedIn Job Application Bot Setup")
    print("=" * 50)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_python_packages():
    """Install required Python packages"""
    print("\n📦 Installing Python packages...")
    
    packages = [
        "selenium",
        "requests", 
        "PyPDF2",
        "python-docx",
        "pandas",  # For data analysis
        "openpyxl"  # For Excel export
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            return False
    
    return True

def check_ollama_installation():
    """Check if Ollama is installed and running"""
    print("\n🤖 Checking Ollama AI installation...")
    
    try:
        # Check if ollama command exists
        subprocess.check_call(["ollama", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("   ✅ Ollama is installed")
        
        # Check if server is running
        import requests
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                print("   ✅ Ollama server is running")
                return True
            else:
                print("   ⚠️  Ollama server not responding")
                return False
        except requests.exceptions.RequestException:
            print("   ⚠️  Ollama server not running")
            print("   💡 Run 'ollama serve' in another terminal")
            return False
            
    except subprocess.CalledProcessError:
        print("   ❌ Ollama not found")
        print("   💡 Install from: https://ollama.ai")
        return False

def download_ollama_model():
    """Download recommended Ollama model"""
    print("\n📥 Setting up AI model...")
    
    model = "qwen2.5:7b"
    
    try:
        print(f"   Downloading {model} (this may take a while)...")
        subprocess.check_call(["ollama", "pull", model])
        print(f"   ✅ {model} downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"   ❌ Failed to download {model}")
        print("   💡 You can download it later with: ollama pull qwen2.5:7b")
        return False

def setup_browser_driver():
    """Guide user through browser driver setup"""
    print("\n🌐 Browser Driver Setup")
    
    system = platform.system().lower()
    
    print("   📋 You need to install a browser driver:")
    print()
    print("   🔹 Chrome (Recommended):")
    print("     - Download from: https://chromedriver.chromium.org/")
    print("     - Add to PATH or place in project directory")
    print()
    print("   🔹 Firefox:")
    print("     - Download from: https://github.com/mozilla/geckodriver/releases")
    print("     - Add to PATH or place in project directory")
    print()
    
    if system == "darwin":  # macOS
        print("   💡 macOS users can use Homebrew:")
        print("      brew install chromedriver")
        print("      brew install geckodriver")
    elif system == "linux":
        print("   💡 Linux users can use package managers:")
        print("      sudo apt install chromium-chromedriver  # Ubuntu/Debian")
        print("      sudo pacman -S chromedriver  # Arch")
    elif system == "windows":
        print("   💡 Windows users:")
        print("      - Download the .exe file")
        print("      - Add to PATH or place in project directory")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "data/exports", 
        "logs",
        "screenshots"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created {directory}/")

def create_user_config():
    """Create user configuration file"""
    print("\n⚙️  Setting up configuration...")
    
    if os.path.exists("user_config.py"):
        print("   ⚠️  user_config.py already exists, skipping...")
        return
    
    try:
        # Copy template to user config
        import shutil
        shutil.copy("user_config_template.py", "user_config.py")
        print("   ✅ Created user_config.py from template")
        print("   💡 Edit user_config.py to customize your settings")
    except FileNotFoundError:
        print("   ❌ user_config_template.py not found")
        return False
    
    return True

def find_cv_files():
    """Find CV files in current directory"""
    print("\n📄 Looking for CV files...")
    
    cv_extensions = ['.pdf', '.docx', '.doc', '.txt']
    cv_keywords = ['cv', 'resume', 'curriculum']
    
    found_files = []
    
    for file in os.listdir('.'):
        file_lower = file.lower()
        file_ext = os.path.splitext(file)[1].lower()
        
        if file_ext in cv_extensions:
            if any(keyword in file_lower for keyword in cv_keywords):
                found_files.append(file)
    
    if found_files:
        print("   ✅ Found CV files:")
        for file in found_files:
            print(f"      - {file}")
        print("   💡 Update cv_path in user_config.py if needed")
    else:
        print("   ⚠️  No CV files found")
        print("   💡 Place your CV file (PDF/DOCX/TXT) in this directory")
        print("   💡 Or update cv_path in user_config.py")

def setup_environment_variables():
    """Guide user through environment variable setup"""
    print("\n🔐 Security Setup (Recommended)")
    print("   For better security, set your LinkedIn credentials as environment variables:")
    print()
    
    system = platform.system().lower()
    
    if system == "windows":
        print("   Windows (Command Prompt):")
        print('   set LINKEDIN_EMAIL=your.email@gmail.com')
        print('   set LINKEDIN_PASSWORD=your_password')
        print()
        print("   Windows (PowerShell):")
        print('   $env:LINKEDIN_EMAIL="your.email@gmail.com"')
        print('   $env:LINKEDIN_PASSWORD="your_password"')
    else:  # macOS/Linux
        print("   macOS/Linux (Terminal):")
        print('   export LINKEDIN_EMAIL="your.email@gmail.com"')
        print('   export LINKEDIN_PASSWORD="your_password"')
        print()
        print("   💡 Add to ~/.bashrc or ~/.zshrc for persistence")
    
    print()
    print("   ⚠️  Alternative: Edit credentials in user_config.py (less secure)")

def run_initial_test():
    """Run initial test to verify setup"""
    print("\n🧪 Running initial test...")
    
    try:
        # Test imports
        from config_enhanced import config
        from cv_analyzer import EnhancedCVAnalyzer
        from ai_agent import EnhancedAIAgent
        print("   ✅ All modules imported successfully")
        
        # Test configuration
        errors = config.validate()
        if errors:
            print("   ⚠️  Configuration warnings:")
            for error in errors:
                print(f"      - {error}")
        else:
            print("   ✅ Configuration validated")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for user"""
    print("\n🎯 Next Steps:")
    print("=" * 30)
    print()
    print("1. 📝 Edit user_config.py with your preferences:")
    print("   - Personal information")
    print("   - Job search criteria") 
    print("   - Application preferences")
    print("   - LinkedIn credentials (or use environment variables)")
    print()
    print("2. 📄 Ensure your CV file is in place:")
    print("   - Supported formats: PDF, DOCX, TXT")
    print("   - Update cv_path in config if needed")
    print()
    print("3. 🤖 Start Ollama server (if not running):")
    print("   ollama serve")
    print()
    print("4. 🚀 Run the bot:")
    print("   python linkedin_enhanced.py")
    print()
    print("💡 For help: python linkedin_enhanced.py --help")
    print("📚 Documentation: README_enhanced.md")

def main():
    """Main setup function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Install packages
    if not install_python_packages():
        print("❌ Package installation failed")
        return False
    
    # Setup directories
    create_directories()
    
    # Setup configuration
    create_user_config()
    
    # Check for CV files
    find_cv_files()
    
    # Check Ollama
    ollama_ok = check_ollama_installation()
    if ollama_ok:
        download_ollama_model()
    
    # Browser setup guide
    setup_browser_driver()
    
    # Security setup
    setup_environment_variables()
    
    # Test setup
    if run_initial_test():
        print("\n✅ Setup completed successfully!")
    else:
        print("\n⚠️  Setup completed with warnings")
    
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)