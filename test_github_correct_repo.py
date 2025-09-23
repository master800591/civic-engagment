#!/usr/bin/env python3
"""
Test GitHub Integration with Correct Repository
Quick test to verify the GitHub integration works with the correct repository URL
"""

import sys
import os

# Add the civic_desktop directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
civic_desktop_dir = os.path.join(current_dir, 'civic_desktop')
sys.path.insert(0, civic_desktop_dir)
sys.path.insert(0, current_dir)

def test_github_integration():
    """Test GitHub integration with the correct repository"""
    print("🧪 Testing GitHub Integration with Correct Repository")
    print("=" * 60)
    
    try:
        from civic_desktop.github_integration import GitHubIntegrationManager
        
        # Create manager with default settings (should use correct repo now)
        manager = GitHubIntegrationManager()
        
        print(f"Repository Owner: {manager.repo_owner}")
        print(f"Repository Name: {manager.repo_name}")
        print(f"Repository URL: {manager.repo_url}")
        print(f"API URL: {manager.api_repo_url}")
        
        # Test basic repository access
        print("\n🔍 Testing Repository Access...")
        repo_info = manager.get_repository_info()
        
        if repo_info.get('error'):
            print(f"❌ Repository Access Error: {repo_info['error']}")
            print("This may be because:")
            print("1. The repository doesn't exist yet")
            print("2. It's private and requires authentication")
            print("3. Network connectivity issues")
        else:
            print("✅ Repository Access Successful!")
            print(f"Repository Name: {repo_info.get('name', 'N/A')}")
            print(f"Description: {repo_info.get('description', 'No description')}")
            print(f"Stars: {repo_info.get('stars', 0)}")
            print(f"Forks: {repo_info.get('forks', 0)}")
            print(f"Language: {repo_info.get('language', 'N/A')}")
        
        # Test update checking
        print("\n📦 Testing Update Checking...")
        from civic_desktop.github_integration import check_for_platform_updates
        
        update_info = check_for_platform_updates()
        if update_info.get('error'):
            print(f"❌ Update Check Error: {update_info['error']}")
        else:
            print("✅ Update Check Successful!")
            print(f"Current Version: {update_info.get('current_version', 'Unknown')}")
            print(f"Latest Version: {update_info.get('latest_version', 'Unknown')}")
            print(f"Has Updates: {'Yes' if update_info.get('has_updates') else 'No'}")
        
        print(f"\n✅ GitHub Integration Configuration Complete!")
        print(f"Repository: https://github.com/{manager.repo_owner}/{manager.repo_name}")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the correct directory")
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_github_integration()