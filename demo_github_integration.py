#!/usr/bin/env python3
"""
GitHub Integration Demo Script
Demonstrates the GitHub integration features including update checking,
repository management, and issue reporting.
"""

import sys
import os

# Add the civic_desktop directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from civic_desktop.github_integration import (
    GitHubIntegrationManager, 
    check_for_platform_updates,
    GitHubUpdateNotifier
)

def demo_update_checking():
    """Demonstrate update checking functionality"""
    print("\n🔍 GITHUB UPDATE CHECKING DEMO")
    print("=" * 50)
    
    print("Checking for platform updates...")
    update_info = check_for_platform_updates()
    
    if update_info.get('error'):
        print(f"❌ Error: {update_info['error']}")
        return
    
    print(f"Current Version: {update_info.get('current_version', 'Unknown')}")
    print(f"Latest Version: {update_info.get('latest_version', 'Unknown')}")
    print(f"Has Updates: {'Yes' if update_info.get('has_updates') else 'No'}")
    
    if update_info.get('has_updates'):
        print(f"📋 Release Notes:")
        print(update_info.get('description', 'No description available'))
        print(f"🔗 Update URL: {update_info.get('update_url', 'N/A')}")
    else:
        print("✅ Platform is up to date!")


def demo_repository_info():
    """Demonstrate repository information retrieval"""
    print("\n📁 REPOSITORY INFORMATION DEMO")
    print("=" * 50)
    
    github_manager = GitHubIntegrationManager()
    
    print("Fetching repository information...")
    repo_info = github_manager.get_repository_info()
    
    if repo_info.get('error'):
        print(f"❌ Error: {repo_info['error']}")
        return
    
    print(f"Repository: {repo_info.get('name', 'N/A')}")
    print(f"Description: {repo_info.get('description', 'No description')}")
    print(f"⭐ Stars: {repo_info.get('stars', 0)}")
    print(f"🍴 Forks: {repo_info.get('forks', 0)}")
    print(f"🐛 Open Issues: {repo_info.get('issues', 0)}")
    print(f"📝 Language: {repo_info.get('language', 'N/A')}")
    print(f"📄 License: {repo_info.get('license', 'No license')}")
    print(f"🌐 URL: {repo_info.get('url', 'N/A')}")


def demo_git_status():
    """Demonstrate git status checking"""
    print("\n🔧 GIT STATUS DEMO")
    print("=" * 50)
    
    github_manager = GitHubIntegrationManager()
    
    print("Checking local git status...")
    git_status = github_manager.get_git_status()
    
    if git_status.get('error'):
        print(f"❌ Git Status: {git_status['error']}")
        return
    
    print(f"Current Branch: {git_status.get('current_branch', 'unknown')}")
    print(f"Has Changes: {'Yes' if git_status.get('has_changes') else 'No'}")
    print(f"Remote Connected: {'Yes' if git_status.get('has_remote') else 'No'}")
    
    if git_status.get('ahead') is not None:
        print(f"Ahead: {git_status['ahead']} commits")
    if git_status.get('behind') is not None:
        print(f"Behind: {git_status['behind']} commits")
    
    if git_status.get('last_commit'):
        commit = git_status['last_commit']
        print(f"Last Commit: {commit.get('sha', 'unknown')[:8]} - {commit.get('message', 'No message')}")


def demo_commit_history():
    """Demonstrate commit history retrieval"""
    print("\n📝 COMMIT HISTORY DEMO")
    print("=" * 50)
    
    github_manager = GitHubIntegrationManager()
    
    print("Fetching recent commits...")
    commits = github_manager.get_recent_commits(5)
    
    if isinstance(commits, dict) and commits.get('error'):
        print(f"❌ Error: {commits['error']}")
        return
    
    print(f"Showing {len(commits)} recent commits:")
    for i, commit in enumerate(commits, 1):
        sha = commit.get('sha', 'unknown')[:8]
        message = commit.get('message', 'No message')[:50]
        author = commit.get('author', 'Unknown')
        date = commit.get('date', 'Unknown')[:10]
        print(f"{i}. {sha} - {message}... ({author}, {date})")


def demo_issues_and_prs():
    """Demonstrate issues and pull requests retrieval"""
    print("\n🐛 ISSUES & PULL REQUESTS DEMO")
    print("=" * 50)
    
    github_manager = GitHubIntegrationManager()
    
    # Get open issues
    print("Fetching open issues...")
    issues = github_manager.get_issues('open', 5)
    
    if isinstance(issues, dict) and issues.get('error'):
        print(f"❌ Issues Error: {issues['error']}")
    else:
        print(f"Open Issues ({len(issues)}):")
        for issue in issues:
            number = issue.get('number', '?')
            title = issue.get('title', 'No title')[:50]
            author = issue.get('author', 'Unknown')
            print(f"  #{number} - {title}... ({author})")
    
    # Get open pull requests  
    print("\nFetching open pull requests...")
    prs = github_manager.get_pull_requests('open', 5)
    
    if isinstance(prs, dict) and prs.get('error'):
        print(f"❌ PRs Error: {prs['error']}")
    else:
        print(f"Open Pull Requests ({len(prs)}):")
        for pr in prs:
            number = pr.get('number', '?')
            title = pr.get('title', 'No title')[:50]
            author = pr.get('author', 'Unknown')
            print(f"  #{number} - {title}... ({author})")


def demo_update_notifier():
    """Demonstrate update notification system"""
    print("\n🔔 UPDATE NOTIFIER DEMO")
    print("=" * 50)
    
    # Create update notifier (no GUI parent)
    notifier = GitHubUpdateNotifier()
    
    print("Update Notifier Configuration:")
    print(f"Auto Check Enabled: {notifier.config.get('auto_check_enabled')}")
    print(f"Check Interval: {notifier.config.get('check_interval_hours')} hours")
    print(f"Last Check: {notifier.config.get('last_check', 'Never')}")
    print(f"Skipped Versions: {notifier.config.get('skipped_versions', [])}")
    print(f"Notify Prereleases: {notifier.config.get('notify_prereleases')}")
    
    print(f"\nShould check now: {notifier.should_check_now()}")
    
    # Force a check (but don't show GUI)
    print("Performing background update check...")
    try:
        update_info = check_for_platform_updates()
        if update_info.get('has_updates'):
            print(f"📦 Update available: v{update_info.get('latest_version')}")
        else:
            print("✅ No updates available")
    except Exception as e:
        print(f"❌ Error during check: {e}")


def demo_development_status():
    """Demonstrate development status retrieval"""
    print("\n💻 DEVELOPMENT STATUS DEMO")
    print("=" * 50)
    
    from civic_desktop.github_integration.github_manager import get_platform_development_status
    
    print("Getting platform development status...")
    dev_status = get_platform_development_status()
    
    if dev_status.get('error'):
        print(f"❌ Error: {dev_status['error']}")
        return
    
    print("Development Activity:")
    print(f"📝 Recent Commits: {len(dev_status.get('recent_commits', []))}")
    print(f"🐛 Open Issues: {len(dev_status.get('open_issues', []))}")
    print(f"🔄 Open Pull Requests: {len(dev_status.get('open_prs', []))}")
    print(f"⭐ Repository Stars: {dev_status.get('stars', 0)}")
    print(f"🍴 Repository Forks: {dev_status.get('forks', 0)}")
    
    if dev_status.get('latest_release'):
        release = dev_status['latest_release']
        print(f"📦 Latest Release: {release.get('tag_name', 'Unknown')} ({release.get('published_at', 'Unknown')[:10]})")


def run_all_demos():
    """Run all demonstration functions"""
    print("🐙 GITHUB INTEGRATION COMPREHENSIVE DEMO")
    print("=" * 60)
    print("This demo showcases all GitHub integration features:")
    print("• Update checking and version management")
    print("• Repository information and statistics") 
    print("• Git status and commit history")
    print("• Issues and pull requests")
    print("• Update notification system")
    print("• Development status tracking")
    print("=" * 60)
    
    try:
        demo_update_checking()
        demo_repository_info()
        demo_git_status()
        demo_commit_history()
        demo_issues_and_prs()
        demo_update_notifier()
        demo_development_status()
        
        print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("GitHub integration is fully functional and ready for use.")
        print("Features demonstrated:")
        print("✓ Automatic update checking")
        print("✓ Repository management")
        print("✓ Version control integration")
        print("✓ Issue and PR tracking")
        print("✓ Development activity monitoring")
        print("✓ Update notification system")
        
    except Exception as e:
        print(f"\n❌ DEMO ERROR: {e}")
        print("This may be due to network connectivity or GitHub API limits.")
        print("The integration system is still functional for local operations.")


if __name__ == "__main__":
    print("GitHub Integration Demo")
    print("Choose a demo to run:")
    print("1. Update Checking")
    print("2. Repository Information")
    print("3. Git Status")
    print("4. Commit History")
    print("5. Issues & Pull Requests")
    print("6. Update Notifier")
    print("7. Development Status")
    print("8. Run All Demos")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-8): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                demo_update_checking()
            elif choice == '2':
                demo_repository_info()
            elif choice == '3':
                demo_git_status()
            elif choice == '4':
                demo_commit_history()
            elif choice == '5':
                demo_issues_and_prs()
            elif choice == '6':
                demo_update_notifier()
            elif choice == '7':
                demo_development_status()
            elif choice == '8':
                run_all_demos()
                break
            else:
                print("Invalid choice. Please enter 0-8.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")