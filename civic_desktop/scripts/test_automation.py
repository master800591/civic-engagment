#!/usr/bin/env python3
"""
Test script for founder package automation system
Validates that all automation components are working correctly
"""

import sys
import subprocess
from pathlib import Path

def run_test(description, command, expected_exit_code=0):
    """Run a test command and check results"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == expected_exit_code
        
        if success:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED (exit code: {result.returncode}, expected: {expected_exit_code})")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
        
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ FAILED (timeout)")
        return False
    except Exception as e:
        print(f"❌ FAILED (exception: {e})")
        return False

def main():
    """Run all automation tests"""
    print("🧪 FOUNDER PACKAGE AUTOMATION - TEST SUITE")
    print("="*60)
    
    # Change to civic_desktop directory
    civic_desktop = Path(__file__).parent.parent
    
    tests = [
        # Test automation script help
        (
            "Automation script help",
            f"cd {civic_desktop} && python scripts/automate_founder_package.py --help"
        ),
        
        # Test validation only mode (expect failure if packages not created)
        # This is intentionally commented out as it requires actual package creation
        # (
        #     "Package validation",
        #     f"cd {civic_desktop} && python scripts/automate_founder_package.py --validate-only"
        # ),
        
        # Test monitoring script help
        (
            "Monitoring script help",
            f"cd {civic_desktop} && python scripts/monitor_registrations.py --help"
        ),
        
        # Test monitoring report generation
        (
            "Generate monitoring report",
            f"cd {civic_desktop} && python scripts/monitor_registrations.py --hours 24"
        ),
        
        # Test monitoring export
        (
            "Export monitoring report",
            f"cd {civic_desktop} && python scripts/monitor_registrations.py --hours 24 --export test_report.txt"
        ),
        
        # Verify exported report exists  
        (
            "Verify exported report file",
            f"ls {civic_desktop}/logs/test_report.txt"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for description, command in tests:
        if run_test(description, command):
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {failed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
