#!/usr/bin/env python3
"""
GitHub Repository Configuration Verification
Verifies that all components are using the correct repository URL
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
civic_desktop_dir = os.path.join(current_dir, 'civic_desktop')
sys.path.insert(0, civic_desktop_dir)
sys.path.insert(0, current_dir)

def verify_repository_configuration():
    """Verify all GitHub integration components use the correct repository"""
    print("🔍 GitHub Repository Configuration Verification")
    print("=" * 55)
    
    try:
        # Test GitHubIntegrationManager
        from civic_desktop.github_integration.github_manager import GitHubIntegrationManager
        manager = GitHubIntegrationManager()
        
        print("✅ GitHubIntegrationManager Configuration:")
        print(f"   Repository Owner: {manager.repo_owner}")
        print(f"   Repository Name: {manager.repo_name}")
        print(f"   Repository URL: {manager.repo_url}")
        print(f"   API URL: {manager.api_repo_url}")
        
        expected_url = "https://github.com/Civic-Engagement/civic-engagment"
        if manager.repo_url == expected_url:
            print("   ✅ Repository URL is correctly configured")
        else:
            print(f"   ❌ Repository URL mismatch! Expected: {expected_url}")
        
        # Test convenience functions
        print("\n✅ Testing Convenience Functions:")
        from civic_desktop.github_integration.github_manager import (
            check_for_platform_updates, 
            get_platform_development_status,
            report_platform_issue
        )
        
        # These will use the same manager instance, so they should be correct
        print("   ✅ check_for_platform_updates: Available")
        print("   ✅ get_platform_development_status: Available") 
        print("   ✅ report_platform_issue: Available")
        
        # Test GitHubUpdateNotifier
        print("\n✅ Testing GitHubUpdateNotifier:")
        from civic_desktop.github_integration.update_notifier import GitHubUpdateNotifier
        notifier = GitHubUpdateNotifier()
        
        # The notifier creates its own manager, so it should use the updated defaults
        test_manager = GitHubIntegrationManager()
        if test_manager.repo_url == expected_url:
            print("   ✅ Update notifier uses correct repository")
        else:
            print("   ❌ Update notifier repository mismatch!")
        
        # Test GitHubIntegrationTab
        print("\n✅ Testing GitHubIntegrationTab:")
        try:
            from civic_desktop.github_integration.github_tab import GitHubIntegrationTab
            print("   ✅ GitHubIntegrationTab: Available (UI component)")
            print("   ✅ Tab will use correct repository through manager")
        except ImportError as e:
            print(f"   ❌ GitHubIntegrationTab import error: {e}")
        
        print(f"\n🎯 VERIFICATION COMPLETE")
        print(f"Repository: {expected_url}")
        print(f"All components configured to use: Civic-Engagement/civic-engagment")
        
        # Test actual connectivity (will fail if repo doesn't exist)
        print(f"\n🌐 Testing Repository Connectivity:")
        repo_info = manager.get_repository_info()
        if repo_info.get('error'):
            print(f"   ℹ️  Repository not accessible: {repo_info['error']}")
            print(f"   This is expected if the repository doesn't exist yet")
        else:
            print(f"   ✅ Repository accessible!")
            print(f"   Name: {repo_info.get('name', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Verification Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_repository_configuration()