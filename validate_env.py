#!/usr/bin/env python3
"""
Environment Configuration Validator for Stash Project
This script checks if all required environment variables are properly configured.
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load .env file if it exists."""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
    else:
        print("❌ .env file not found. Please create one from .env.example")
        return False
    return True

def check_required_vars():
    """Check if all required environment variables are set."""
    required_vars = {
        'GENAI_API_KEY': 'Google AI API key for Gemini model access',
        'FIRESTORE_PROJECT_ID': 'Google Cloud Project ID for Firestore',
        'GCLOUD_STORAGE_BUCKET': 'Google Cloud Storage bucket name',
        'SECRET_KEY': 'Application secret key for security'
    }
    
    missing_vars = []
    placeholder_vars = []
    
    print("🔍 Checking required environment variables...")
    print("=" * 50)
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Missing")
        elif value.startswith('your-') or 'your' in value.lower():
            placeholder_vars.append(var)
            print(f"⚠️  {var}: Still using placeholder value")
        else:
            print(f"✅ {var}: Configured")
    
    return missing_vars, placeholder_vars

def check_optional_vars():
    """Check optional but recommended environment variables."""
    optional_vars = {
        'GOOGLE_APPLICATION_CREDENTIALS': 'Path to service account JSON key',
        'HOST': 'Server host address',
        'PORT': 'Server port number',
        'LOG_LEVEL': 'Application log level',
        'FLASK_ENV': 'Flask environment mode'
    }
    
    print("\n🔧 Checking optional environment variables...")
    print("=" * 50)
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if value.startswith('your-') or 'your' in value.lower():
                print(f"⚠️  {var}: Using placeholder value")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"➖ {var}: Not set (using defaults)")

def check_file_paths():
    """Check if file paths in environment variables exist."""
    print("\n📁 Checking file paths...")
    print("=" * 50)
    
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path:
        if os.path.exists(credentials_path):
            print(f"✅ Service account key file found: {credentials_path}")
        else:
            print(f"❌ Service account key file not found: {credentials_path}")
    else:
        print("➖ GOOGLE_APPLICATION_CREDENTIALS not set")

def test_imports():
    """Test if required Python packages can be imported."""
    print("\n📦 Testing Python package imports...")
    print("=" * 50)
    
    packages = [
        ('fastapi', 'FastAPI web framework'),
        ('google.cloud.firestore', 'Google Cloud Firestore'),
        ('google.cloud.vision', 'Google Cloud Vision API'),
        ('google.cloud.storage', 'Google Cloud Storage'),
        ('google.generativeai', 'Google Generative AI'),
    ]
    
    failed_imports = []
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {package}: Available")
        except ImportError:
            failed_imports.append(package)
            print(f"❌ {package}: Not available - {description}")
    
    return failed_imports

def main():
    """Main validation function."""
    print("🚀 Stash Environment Configuration Validator")
    print("=" * 50)
    
    # Load .env file
    if not load_env_file():
        sys.exit(1)
    
    # Check required variables
    missing_vars, placeholder_vars = check_required_vars()
    
    # Check optional variables
    check_optional_vars()
    
    # Check file paths
    check_file_paths()
    
    # Test imports
    failed_imports = test_imports()
    
    # Summary
    print("\n📊 Configuration Summary")
    print("=" * 50)
    
    issues = len(missing_vars) + len(placeholder_vars) + len(failed_imports)
    
    if missing_vars:
        print(f"❌ Missing required variables: {', '.join(missing_vars)}")
    
    if placeholder_vars:
        print(f"⚠️  Variables with placeholder values: {', '.join(placeholder_vars)}")
    
    if failed_imports:
        print(f"❌ Missing Python packages: {', '.join(failed_imports)}")
        print("💡 Install with: pip install -r requirements.txt")
    
    if issues == 0:
        print("🎉 All checks passed! Your environment is properly configured.")
        print("\n🚀 You can now run the application with:")
        print("   python main.py")
        sys.exit(0)
    else:
        print(f"\n⚠️  Found {issues} configuration issues.")
        print("\n🔧 Next steps:")
        
        if missing_vars or placeholder_vars:
            print("1. Edit your .env file with actual configuration values")
            print("2. See .env.example for guidance on required values")
        
        if failed_imports:
            print("3. Install missing Python packages:")
            print("   source .venv/bin/activate")
            print("   pip install -r requirements.txt")
        
        print("4. Run this validator again to verify fixes")
        sys.exit(1)

if __name__ == '__main__':
    main()
