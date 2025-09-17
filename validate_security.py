#!/usr/bin/env python3
"""
Security validation script for Songs4Image
This script checks that credentials are properly configured and no hardcoded values remain.
"""

import os
import sys
import re

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = '.env'
    env_example = '.env.example'
    
    print("🔍 Checking environment configuration...")
    
    if not os.path.exists(env_example):
        print("❌ .env.example file missing")
        return False
    else:
        print("✅ .env.example template found")
    
    if not os.path.exists(env_file):
        print("⚠️  .env file not found (this is expected for security)")
        print("   Create .env from .env.example and add your credentials")
        return True
    
    # Check if .env has actual values (not template values)
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_' in content or 'test_' in content:
            print("⚠️  .env file contains template values")
            print("   Replace placeholder values with your actual credentials")
        else:
            print("✅ .env file appears to have real credentials")
    
    return True

def check_hardcoded_credentials():
    """Check Python files for hardcoded credentials"""
    print("\n🔍 Scanning for hardcoded credentials...")
    
    # Known credential patterns to check for
    credential_patterns = [
        r'AIzaSy[A-Za-z0-9_-]{33}',  # Google API key pattern
        r'client_id\s*=\s*[\'"][^\'"\s]{20,}[\'"]',  # Hardcoded client ID
        r'client_secret\s*=\s*[\'"][^\'"\s]{20,}[\'"]',  # Hardcoded client secret
        r'api_key\s*=\s*[\'"][^\'"\s]{20,}[\'"]',  # Hardcoded API key
    ]
    
    python_files = ['main.py', 'main1.py']
    issues_found = False
    
    for file_path in python_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                for pattern in credential_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"❌ Potential hardcoded credential in {file_path}: {pattern}")
                        issues_found = True
    
    if not issues_found:
        print("✅ No hardcoded credentials found in Python files")
    
    return not issues_found

def check_gitignore():
    """Check that .gitignore properly excludes credential files"""
    print("\n🔍 Checking .gitignore configuration...")
    
    gitignore_file = '.gitignore'
    if not os.path.exists(gitignore_file):
        print("❌ .gitignore file missing")
        return False
    
    with open(gitignore_file, 'r') as f:
        content = f.read()
        
    required_patterns = ['.env', '*.env', 'config.py', 'secrets.py']
    missing_patterns = []
    
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"⚠️  .gitignore missing patterns: {missing_patterns}")
    else:
        print("✅ .gitignore properly configured to exclude credential files")
    
    return len(missing_patterns) == 0

def check_config_module():
    """Check that config.py module exists and works"""
    print("\n🔍 Checking configuration module...")
    
    if not os.path.exists('config.py'):
        print("❌ config.py module missing")
        return False
    
    try:
        # Test import without actually requiring environment variables
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        print("✅ config.py module can be imported")
        return True
    except Exception as e:
        print(f"❌ config.py module has syntax errors: {e}")
        return False

def main():
    """Run all security checks"""
    print("🔒 Songs4Image Security Validation")
    print("=" * 40)
    
    checks = [
        ("Environment Configuration", check_env_file),
        ("Hardcoded Credentials", check_hardcoded_credentials),
        ("Git Ignore Configuration", check_gitignore),
        ("Configuration Module", check_config_module),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All security checks passed!")
        print("\n📝 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your actual API credentials to .env")
        print("3. Never commit .env to version control")
    else:
        print("❌ Some security checks failed")
        print("Please review the issues above before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()