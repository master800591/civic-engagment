#!/usr/bin/env python3
"""
CIVIC ENGAGEMENT PLATFORM - SECURITY VALIDATION SCRIPT
Validates that all private information and keys are properly protected from git commits
"""

import os
import subprocess
import json
from pathlib import Path
import glob

def check_git_ignore_protection():
    """Check that sensitive files are properly ignored by git"""
    
    print("🔒 CIVIC ENGAGEMENT PLATFORM - SECURITY VALIDATION")
    print("=" * 60)
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    print(f"📁 Project Root: {project_root}")
    print()
    
    # List of sensitive file patterns that MUST be ignored
    sensitive_patterns = [
        # Private Keys & Cryptographic Materials
        "**/private_keys/",
        "**/*private*.pem",
        "**/*_private.pem",
        "**/master_key.pem",
        "**/founder_keys/",
        "**/*founder*.pem",
        "**/*.key",
        
        # User Data & Databases
        "**/users_db.json",
        "**/sessions_db.json", 
        "**/blockchain_db.json",
        "**/validators_db.json",
        
        # PDF Documents & User Files
        "**/user_pdfs/",
        "**/*_public_profile.pdf",
        "**/*_private_recovery.pdf",
        "**/qr_codes/",
        
        # Configuration with Secrets
        "**/config/*_secrets.json",
        "**/config/production_config.json",
        "**/secrets.json",
        "**/credentials.json"
    ]
    
    # Find files matching sensitive patterns
    print("🔍 SCANNING FOR SENSITIVE FILES...")
    print("-" * 40)
    
    found_sensitive_files = []
    
    for pattern in sensitive_patterns:
        matches = list(project_root.glob(pattern))
        if matches:
            found_sensitive_files.extend(matches)
            print(f"📂 Found {len(matches)} files matching: {pattern}")
            for match in matches[:3]:  # Show first 3 matches
                rel_path = match.relative_to(project_root)
                print(f"   • {rel_path}")
            if len(matches) > 3:
                print(f"   ... and {len(matches) - 3} more")
    
    print(f"\n📊 Total sensitive files found: {len(found_sensitive_files)}")
    
    # Check git ignore status
    print(f"\n🛡️ GIT IGNORE PROTECTION STATUS...")
    print("-" * 40)
    
    protected_count = 0
    unprotected_files = []
    
    for sensitive_file in found_sensitive_files:
        try:
            # Check if file is ignored by git
            result = subprocess.run([
                'git', 'check-ignore', str(sensitive_file)
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                protected_count += 1
            else:
                unprotected_files.append(sensitive_file)
                
        except Exception as e:
            print(f"⚠️ Error checking {sensitive_file}: {e}")
    
    # Report results
    print(f"✅ Protected files: {protected_count}")
    print(f"❌ Unprotected files: {len(unprotected_files)}")
    
    if unprotected_files:
        print(f"\n🚨 SECURITY ALERT - UNPROTECTED SENSITIVE FILES:")
        print("=" * 50)
        for unprotected in unprotected_files:
            rel_path = unprotected.relative_to(project_root)
            print(f"❌ {rel_path}")
        print(f"\n💡 These files need to be added to .gitignore!")
        return False
    else:
        print(f"\n🎉 ALL SENSITIVE FILES ARE PROPERLY PROTECTED!")
        return True

def check_git_tracked_sensitive():
    """Check if any sensitive files are currently tracked by git"""
    
    print(f"\n🔍 CHECKING FOR TRACKED SENSITIVE FILES...")
    print("-" * 45)
    
    project_root = Path(__file__).parent
    
    try:
        # Get list of all tracked files
        result = subprocess.run([
            'git', 'ls-files'
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode != 0:
            print("⚠️ Error getting git tracked files")
            return False
            
        tracked_files = result.stdout.strip().split('\n')
        
        # Check for sensitive patterns in tracked files
        sensitive_keywords = [
            'private', 'secret', 'key', 'password', 'credential', 
            'recovery', '_db.json', '.pem', 'users_db', 'sessions_db',
            'blockchain_db', 'validators_db'
        ]
        
        dangerous_files = []
        for tracked_file in tracked_files:
            for keyword in sensitive_keywords:
                if keyword.lower() in tracked_file.lower():
                    dangerous_files.append(tracked_file)
                    break
        
        if dangerous_files:
            print(f"🚨 FOUND {len(dangerous_files)} POTENTIALLY SENSITIVE TRACKED FILES:")
            for dangerous in dangerous_files:
                print(f"❌ {dangerous}")
            print(f"\n💡 These files should be removed from git tracking:")
            print(f"   git rm --cached <filename>")
            return False
        else:
            print(f"✅ No sensitive files are currently tracked by git")
            return True
            
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False

def check_gitignore_completeness():
    """Verify .gitignore has comprehensive protection"""
    
    print(f"\n📋 VERIFYING .GITIGNORE COMPLETENESS...")
    print("-" * 42)
    
    project_root = Path(__file__).parent
    gitignore_path = project_root / '.gitignore'
    
    if not gitignore_path.exists():
        print("❌ .gitignore file not found!")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        gitignore_content = f.read()
    
    # Required protection patterns
    required_patterns = [
        '**/private_keys/',
        '**/*private*.pem',
        '**/users_db.json',
        '**/user_pdfs/',
        '**/*_db.json',
        '**/*.key',
        '**/secrets.json',
        '**/credentials.json'
    ]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in gitignore_content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"❌ Missing {len(missing_patterns)} protection patterns:")
        for missing in missing_patterns:
            print(f"   • {missing}")
        return False
    else:
        print(f"✅ All required protection patterns present")
        return True

def main():
    """Main security validation function"""
    
    print("Starting security validation...\n")
    
    # Run all checks
    ignore_protection_ok = check_git_ignore_protection()
    tracked_files_ok = check_git_tracked_sensitive()
    gitignore_complete_ok = check_gitignore_completeness()
    
    # Final report
    print("\n" + "=" * 60)
    print("🔒 FINAL SECURITY VALIDATION REPORT")
    print("=" * 60)
    
    if ignore_protection_ok and tracked_files_ok and gitignore_complete_ok:
        print("✅ ALL SECURITY CHECKS PASSED")
        print("🛡️ Private information and keys are properly protected")
        print("🎉 Safe to commit and push to repository")
        return True
    else:
        print("❌ SECURITY ISSUES FOUND")
        print("🚨 DO NOT commit until issues are resolved")
        
        if not ignore_protection_ok:
            print("   • Some sensitive files are not ignored")
        if not tracked_files_ok:
            print("   • Some sensitive files are tracked by git")  
        if not gitignore_complete_ok:
            print("   • .gitignore missing required patterns")
            
        print("\n💡 Fix these issues before committing!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)