#!/usr/bin/env python3
"""
Test Session Management and Tab Refreshing
This script tests that all tabs properly refresh when login/logout occurs.
"""
import os
import sys
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from civic_desktop.main_window import CivicEngagementApp
from civic_desktop.users.session import SessionManager
from civic_desktop.users.backend import UserBackend

def test_session_refreshing():
    """Test that tabs refresh properly during login/logout"""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = CivicEngagementApp()
    main_window.show()
    
    def simulate_login():
        """Simulate a user login"""
        print("\n=== Testing Login Session Refresh ===")
        
        # Try to get founder user
        founder_user = UserBackend.get_user_by_email("founder@civicengagementai.org")
        
        if founder_user:
            print(f"✅ Found founder user: {founder_user['email']}")
            
            # Simulate login
            main_window.handle_login(founder_user)
            print("🔐 Login handled - all tabs should refresh")
            
            # Check session state
            current_user = SessionManager.get_current_user()
            if current_user:
                print(f"✅ Session established for: {current_user['email']}")
                print(f"   Role: {current_user.get('role', 'Unknown')}")
            else:
                print("❌ Login failed - no session established")
                
        else:
            print("❌ Founder user not found - run force_create_founder.py first")
    
    def simulate_logout():
        """Simulate a user logout"""
        print("\n=== Testing Logout Session Refresh ===")
        
        # Check if logged in
        current_user = SessionManager.get_current_user()
        if current_user:
            print(f"🔐 Currently logged in as: {current_user['email']}")
            
            # Simulate logout
            main_window.handle_logout()
            print("🔓 Logout handled - all tabs should refresh")
            
            # Check session state
            if not SessionManager.is_authenticated():
                print("✅ Successfully logged out - session cleared")
            else:
                print("❌ Logout failed - session still active")
        else:
            print("ℹ️  Not currently logged in")
    
    def run_test_sequence():
        """Run the full test sequence"""
        print("🚀 Starting Session Management Test")
        print("=" * 50)
        
        # Test initial state
        print("📊 Initial authentication state:")
        if SessionManager.is_authenticated():
            user = SessionManager.get_current_user()
            print(f"   Logged in as: {user['email'] if user else 'Unknown'}")
        else:
            print("   Not authenticated")
        
        # Test login
        QTimer.singleShot(2000, simulate_login)
        
        # Test logout after login
        QTimer.singleShot(6000, simulate_logout)
        
        # Show completion message
        def show_completion():
            print("\n✅ Session management test completed!")
            print("Check the application UI to verify that tabs properly refreshed")
            print("during login and logout operations.")
            
        QTimer.singleShot(10000, show_completion)
    
    # Start test sequence
    QTimer.singleShot(1000, run_test_sequence)
    
    # Run application
    print("🖥️  Civic Desktop Application launched")
    print("   The test will automatically simulate login/logout")
    print("   Watch for UI changes in the tab content")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_session_refreshing()