# Main Application Entry Point with Tasks Integration
# Updated main.py with comprehensive task management system

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Environment Configuration
def load_environment_config():
    """Load environment-specific configuration"""
    
    # Default to production config in civic_desktop/config/
    default_config_path = os.path.join(os.path.dirname(__file__), 'config', 'production_config.json')
    config_path = os.environ.get('CIVIC_CONFIG', default_config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded configuration from: {config_path}")
        return config
    except FileNotFoundError:
        print(f"Config file not found: {config_path}, using defaults")
        return get_default_config()
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}, using defaults")
        return get_default_config()

def get_default_config():
    """Get default configuration if config file not available"""
    
    base_path = Path(__file__).parent
    
    return {
        # Database paths
        'users_db_path': str(base_path / 'users' / 'users_db.json'),
        'blockchain_db_path': str(base_path / 'blockchain' / 'blockchain_db.json'),
        'debates_db_path': str(base_path / 'debates' / 'debates_db.json'),
        'moderation_db_path': str(base_path / 'moderation' / 'moderation_db.json'),
        'contracts_db_path': str(base_path / 'contracts' / 'contracts_db.json'),
        'training_db_path': str(base_path / 'training' / 'training_db.json'),
        'crypto_db_path': str(base_path / 'crypto' / 'crypto_db.json'),
        
        # NEW: Task system paths
        'tasks_db_path': str(base_path / 'tasks' / 'tasks_db.json'),
        'notifications_db_path': str(base_path / 'tasks' / 'notifications_db.json'),
        'task_integration_config_path': str(base_path / 'tasks' / 'integration_config.json'),
        
        # Extended module paths
        'analytics_db_path': str(base_path / 'analytics' / 'analytics_db.json'),
        'events_db_path': str(base_path / 'events' / 'events_db.json'),
        'communications_db_path': str(base_path / 'communications' / 'messages_db.json'),
        'surveys_db_path': str(base_path / 'surveys' / 'surveys_db.json'),
        'petitions_db_path': str(base_path / 'petitions' / 'petitions_db.json'),
        'documents_db_path': str(base_path / 'documents' / 'documents_db.json'),
        'transparency_db_path': str(base_path / 'transparency' / 'transparency_db.json'),
        'collaboration_db_path': str(base_path / 'collaboration' / 'collaboration_db.json'),
        
        # Key storage
        'private_keys_path': str(base_path / 'users' / 'private_keys'),
        
        # System settings
        'debug_mode': True,
        'auto_backup': True,
        'blockchain_auto_sync': True,
        
        # NEW: Task system settings
        'task_auto_creation': True,
        'task_notifications_enabled': True,
        'task_reminder_intervals': {
            'low': 24,      # hours
            'normal': 12,   # hours
            'high': 6,      # hours
            'urgent': 2,    # hours
            'critical': 1   # hour
        },
        'validation_thresholds': {
            'city': 0.33,
            'state': 0.25,
            'country': 0.20,
            'founder': 0.10
        }
    }

# Global configuration
ENV_CONFIG = load_environment_config()

def ensure_directories():
    """Ensure all required directories exist"""
    
    directories_to_create = [
        'users/private_keys',
        'blockchain',
        'debates',
        'moderation',
        'contracts',
        'training',
        'crypto',
        'tasks',            # NEW: Tasks directory
        'analytics',
        'events',
        'communications',
        'surveys',
        'petitions',
        'documents',
        'transparency',
        'collaboration',
        'config',
        'tests',
        'utils'
    ]
    
    base_path = Path(__file__).parent
    
    for directory in directories_to_create:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {dir_path}")

def initialize_task_system():
    """Initialize the task management system"""
    
    try:
        # Import task system components
        from tasks.task_manager import TaskManager
        from tasks.task_integration import TaskIntegrationManager
        from tasks.notification_system import TaskNotificationSystem
        
        print("✅ Task system components imported successfully")
        
        # Initialize task manager
        task_manager = TaskManager()
        print("✅ Task manager initialized")
        
        # Initialize integration manager
        integration_manager = TaskIntegrationManager()
        print("✅ Task integration manager initialized")
        
        # Initialize notification system
        notification_system = TaskNotificationSystem()
        print("✅ Task notification system initialized")
        
        # Process any pending notifications or scheduled tasks
        deferred_count = notification_system.process_deferred_notifications()
        scheduled_count = notification_system.process_scheduled_notifications()
        expired_count = len(task_manager.expire_overdue_tasks())
        
        if deferred_count > 0:
            print(f"📤 Processed {deferred_count} deferred notifications")
        if scheduled_count > 0:
            print(f"⏰ Processed {scheduled_count} scheduled notifications")
        if expired_count > 0:
            print(f"⚠️ Expired {expired_count} overdue tasks")
        
        print("✅ Task system initialization complete")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing task system: {e}")
        return False

def initialize_application():
    """Initialize the complete application"""
    
    print("🏛️ Civic Engagement Platform - Task Integration Release")
    print("=" * 60)
    
    # Ensure directories exist
    print("📁 Creating required directories...")
    ensure_directories()
    
    # Initialize task system (NEW)
    print("📋 Initializing task management system...")
    task_system_ready = initialize_task_system()
    
    if not task_system_ready:
        print("⚠️ Task system initialization failed, continuing with limited functionality")
    
    # Initialize other core systems
    try:
        # Import and initialize blockchain system
        from blockchain.blockchain import Blockchain
        blockchain = Blockchain()
        print("✅ Blockchain system initialized")
        
        # Initialize user system
        from users.backend import UserBackend
        user_backend = UserBackend()
        print("✅ User management system initialized")
        
        # Import session manager
        from users.session import SessionManager
        print("✅ Session management system initialized")
        
    except Exception as e:
        print(f"⚠️ Warning: Some core systems failed to initialize: {e}")
    
    # Print configuration summary
    print("\n📋 System Configuration:")
    print(f"   Task Management: {'✅ Enabled' if task_system_ready else '❌ Disabled'}")
    print(f"   Debug Mode: {'✅ Enabled' if ENV_CONFIG.get('debug_mode') else '❌ Disabled'}")
    print(f"   Auto Backup: {'✅ Enabled' if ENV_CONFIG.get('auto_backup') else '❌ Disabled'}")
    print(f"   Task Auto Creation: {'✅ Enabled' if ENV_CONFIG.get('task_auto_creation') else '❌ Disabled'}")
    print(f"   Task Notifications: {'✅ Enabled' if ENV_CONFIG.get('task_notifications_enabled') else '❌ Disabled'}")
    
    print("\n🗂️ Database Paths:")
    for key, value in ENV_CONFIG.items():
        if key.endswith('_db_path'):
            module_name = key.replace('_db_path', '').replace('_', ' ').title()
            print(f"   {module_name}: {value}")
    
    print("\n🎯 Validation Thresholds:")
    thresholds = ENV_CONFIG.get('validation_thresholds', {})
    for level, threshold in thresholds.items():
        print(f"   {level.title()}: {threshold:.1%}")
    
    print("=" * 60)

def main():
    """Main application entry point with task system integration"""
    
    # Initialize application
    initialize_application()
    
    try:
        # Import and run GUI
        from main_window import MainWindow
        
        # Check if running in GUI mode
        if len(sys.argv) > 1 and sys.argv[1] == '--cli':
            print("🖥️ Starting in CLI mode...")
            # CLI mode implementation would go here
            run_cli_mode()
        else:
            print("🖼️ Starting GUI application...")
            run_gui_mode()
            
    except ImportError as e:
        print(f"❌ Error importing GUI components: {e}")
        print("🖥️ Falling back to CLI mode...")
        run_cli_mode()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def run_gui_mode():
    """Run the application in GUI mode"""
    
    try:
        from PyQt5.QtWidgets import QApplication
        from main_window import MainWindow
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Civic Engagement Platform")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("Civic Engagement Foundation")
        
        # Create main window with task integration
        main_window = MainWindow()
        main_window.show()
        
        print("✅ GUI application started successfully")
        print("📋 Tasks tab is now the primary interface for civic duties")
        print("🔔 Task notifications are active")
        
        # Start the Qt event loop
        sys.exit(app.exec_())
        
    except ImportError:
        print("❌ PyQt5 not available, GUI mode not possible")
        run_cli_mode()
    except Exception as e:
        print(f"❌ Error running GUI: {e}")
        run_cli_mode()

def run_cli_mode():
    """Run the application in CLI mode for testing/administration"""
    
    print("🖥️ Civic Engagement Platform - CLI Mode")
    print("📋 Task Management System Active")
    
    while True:
        print("\n" + "=" * 50)
        print("Available Commands:")
        print("1. 📋 View Task Statistics")
        print("2. 👤 List Users")
        print("3. 🔍 Check System Status")
        print("4. 📊 View Integration Statistics")
        print("5. 🔔 Process Notifications")
        print("6. ⚙️ Show Configuration")
        print("0. 🚪 Exit")
        
        try:
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                show_task_statistics()
            elif choice == "2":
                list_users()
            elif choice == "3":
                check_system_status()
            elif choice == "4":
                show_integration_statistics()
            elif choice == "5":
                process_notifications()
            elif choice == "6":
                show_configuration()
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_task_statistics():
    """Show task system statistics"""
    
    try:
        from tasks.task_manager import TaskManager
        
        task_manager = TaskManager()
        stats = task_manager.get_task_statistics()
        
        print("\n📊 Task Statistics:")
        print(f"   Total Tasks: {stats['total_tasks']}")
        print(f"   Completion Rate: {stats['completion_rate']:.1f}%")
        print(f"   Average Completion Time: {stats['average_completion_hours']:.1f} hours")
        
        print("\n📋 Status Breakdown:")
        for status, count in stats['status_breakdown'].items():
            print(f"   {status.title()}: {count}")
        
        print("\n⚡ Priority Breakdown:")
        for priority, count in stats['priority_breakdown'].items():
            print(f"   {priority.title()}: {count}")
        
        print("\n📁 Category Breakdown:")
        for category, count in stats['category_breakdown'].items():
            print(f"   {category.title()}: {count}")
            
    except Exception as e:
        print(f"❌ Error getting task statistics: {e}")

def list_users():
    """List registered users"""
    
    try:
        from users.backend import UserBackend
        
        users = UserBackend.get_all_users()
        
        print(f"\n👥 Registered Users ({len(users)} total):")
        for user in users[:10]:  # Show first 10 users
            email = user.get('email', 'Unknown')
            role = user.get('role', 'Unknown').replace('_', ' ').title()
            name = user.get('name', 'Unnamed')
            print(f"   📧 {email} - {name} ({role})")
        
        if len(users) > 10:
            print(f"   ... and {len(users) - 10} more users")
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")

def check_system_status():
    """Check overall system status"""
    
    print("\n🔍 System Status Check:")
    
    # Check database files
    db_paths = [
        ('Users', ENV_CONFIG.get('users_db_path')),
        ('Tasks', ENV_CONFIG.get('tasks_db_path')),
        ('Blockchain', ENV_CONFIG.get('blockchain_db_path')),
        ('Notifications', ENV_CONFIG.get('notifications_db_path'))
    ]
    
    print("\n💾 Database Files:")
    for name, path in db_paths:
        if path and Path(path).exists():
            size = Path(path).stat().st_size
            print(f"   ✅ {name}: {path} ({size} bytes)")
        else:
            print(f"   ❌ {name}: {path} (missing)")
    
    # Check core systems
    print("\n⚙️ Core Systems:")
    
    try:
        from tasks.task_manager import TaskManager
        TaskManager()
        print("   ✅ Task Management System")
    except Exception as e:
        print(f"   ❌ Task Management System: {e}")
    
    try:
        from blockchain.blockchain import Blockchain
        Blockchain()
        print("   ✅ Blockchain System")
    except Exception as e:
        print(f"   ❌ Blockchain System: {e}")
    
    try:
        from users.backend import UserBackend
        UserBackend()
        print("   ✅ User Management System")
    except Exception as e:
        print(f"   ❌ User Management System: {e}")

def show_integration_statistics():
    """Show task integration statistics"""
    
    try:
        from tasks.task_integration import TaskIntegrationManager
        
        integration_manager = TaskIntegrationManager()
        stats = integration_manager.get_integration_statistics()
        
        print("\n🔗 Integration Statistics:")
        print(f"   Auto Tasks Created Today: {stats['auto_tasks_created_today']}")
        print(f"   Integration Success Rate: {stats['integration_success_rate']:.1f}%")
        print(f"   Average Response Time: {stats['average_task_response_time']:.1f}s")
        print(f"   Cross-Module Efficiency: {stats['cross_module_efficiency']:.1f}%")
        
        print("\n👥 User Engagement Metrics:")
        engagement = stats['user_engagement_metrics']
        print(f"   Task Completion Rate: {engagement['task_completion_rate']:.1f}%")
        print(f"   Average Completion Time: {engagement['average_completion_time_hours']:.1f}h")
        print(f"   User Satisfaction Score: {engagement['user_satisfaction_score']:.1f}/5.0")
        print(f"   Repeat Engagement Rate: {engagement['repeat_engagement_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Error getting integration statistics: {e}")

def process_notifications():
    """Process pending notifications"""
    
    try:
        from tasks.notification_system import TaskNotificationSystem
        
        notification_system = TaskNotificationSystem()
        
        # Process deferred notifications
        deferred_count = notification_system.process_deferred_notifications()
        print(f"📤 Processed {deferred_count} deferred notifications")
        
        # Process scheduled notifications
        scheduled_count = notification_system.process_scheduled_notifications()
        print(f"⏰ Processed {scheduled_count} scheduled notifications")
        
        # Get notification statistics
        stats = notification_system.get_notification_statistics()
        print(f"\n📊 Notification Statistics:")
        print(f"   Total Notifications: {stats['total_notifications']}")
        print(f"   Unread Notifications: {stats['unread_notifications']}")
        print(f"   Delivery Success Rate: {stats['delivery_success_rate']:.1f}%")
        print(f"   Deferred Notifications: {stats['deferred_notifications']}")
        print(f"   Scheduled Notifications: {stats['scheduled_notifications']}")
        
    except Exception as e:
        print(f"❌ Error processing notifications: {e}")

def show_configuration():
    """Show current configuration"""
    
    print("\n⚙️ Current Configuration:")
    
    # Core settings
    print("\n🎛️ Core Settings:")
    core_settings = [
        ('Debug Mode', 'debug_mode'),
        ('Auto Backup', 'auto_backup'),
        ('Blockchain Auto Sync', 'blockchain_auto_sync'),
        ('Task Auto Creation', 'task_auto_creation'),
        ('Task Notifications', 'task_notifications_enabled')
    ]
    
    for name, key in core_settings:
        value = ENV_CONFIG.get(key, False)
        status = "✅ Enabled" if value else "❌ Disabled"
        print(f"   {name}: {status}")
    
    # Validation thresholds
    print("\n🎯 Validation Thresholds:")
    thresholds = ENV_CONFIG.get('validation_thresholds', {})
    for level, threshold in thresholds.items():
        print(f"   {level.title()}: {threshold:.1%}")
    
    # Reminder intervals
    print("\n⏰ Task Reminder Intervals (hours):")
    intervals = ENV_CONFIG.get('task_reminder_intervals', {})
    for priority, hours in intervals.items():
        print(f"   {priority.title()}: {hours}h")

if __name__ == '__main__':
    main()

# Export configuration and main function
__all__ = ['ENV_CONFIG', 'main', 'initialize_application']