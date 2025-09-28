"""
FOUNDER KEY SETUP SCRIPT - Initialize the Founder key system for the Civic Engagement Platform
This script creates the master Founder key system and exports keys for distribution to genesis Founders
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def setup_founder_keys():
    """Initialize the Founder key system and generate genesis keys"""
    
    print("🏛️ CIVIC ENGAGEMENT PLATFORM - FOUNDER KEY SYSTEM SETUP")
    print("=" * 80)
    
    try:
        # Import the Founder key manager
        from users.founder_keys import FounderKeyManager
        from users.contract_roles import ContractRoleManager
        
        print("✅ Founder key system modules loaded")
        
        # Initialize Founder key manager
        founder_manager = FounderKeyManager()
        
        # Check if keys already exist
        success, message, existing_info = founder_manager.get_founder_keys_info()
        if success:
            print("⚠️ Founder key system already exists!")
            print(f"   Master fingerprint: {existing_info['master_fingerprint']}")
            print(f"   Total Founders: {existing_info['founder_count']}")
            print(f"   Assigned Founders: {existing_info['assigned_founders']}")
            
            user_input = input("\nDo you want to export existing keys for distribution? (y/N): ").lower().strip()
            if user_input == 'y':
                export_existing_keys(founder_manager)
            return
        
        # Generate new Founder key system
        print("\n🔐 Generating Founder Master Key System...")
        
        founder_count = 7  # Constitutional maximum
        success, message, founder_data = founder_manager.generate_founder_master_key(founder_count)
        
        if not success:
            print(f"❌ Failed to generate Founder keys: {message}")
            return
        
        print(f"\n✅ Founder Key System Created Successfully!")
        print(f"   Master Fingerprint: {founder_data['master_fingerprint']}")
        print(f"   Number of Founder Keys: {founder_data['founder_count']}")
        print(f"   Security Level: RSA-4096 (Master) / RSA-2048 (Individual)")
        
        # Initialize contract roles system
        print("\n🏛️ Initializing Contract Roles System...")
        role_manager = ContractRoleManager()
        
        # Export keys for distribution
        export_success, export_message, export_data = founder_manager.export_founder_keys_for_distribution()
        
        if export_success:
            # Save export data to secure files
            export_dir = Path('users/founder_keys/distribution')
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Create individual key files for each Founder
            for founder_id, founder_info in export_data['founder_keys'].items():
                founder_file = export_dir / f"{founder_id}_private_key.txt"
                
                powers_list = '\n'.join(['- ' + power for power in export_data['constitutional_framework']['founder_powers']])
                limits_list = '\n'.join(['- ' + limit for limit in export_data['constitutional_framework']['founder_limitations']])
                
                key_content = f"""
==============================================================================
CIVIC ENGAGEMENT PLATFORM - {founder_id} PRIVATE KEY
==============================================================================

FOUNDER ID: {founder_info['founder_id']}
KEY FINGERPRINT: {founder_info['key_fingerprint']}
MASTER FINGERPRINT: {export_data['master_fingerprint']}

CONSTITUTIONAL AUTHORITY:
{powers_list}

CONSTITUTIONAL LIMITATIONS:
{limits_list}

CRITICAL SECURITY INSTRUCTIONS:
1. Keep this private key absolutely secure and confidential
2. This key grants maximum constitutional authority on the platform
3. Loss of this key means permanent loss of Founder status
4. Create secure offline backups in multiple locations
5. Never share this key or store it in unsecured locations

USAGE INSTRUCTIONS:
1. During account registration on the Civic Engagement Platform
2. Provide this ENTIRE private key text in the "Founder Private Key" field
3. Your account will be automatically assigned Founder constitutional authority
4. Delete this file after successful registration and backup

PRIVATE KEY (PEM FORMAT):
{founder_info['private_key_pem']}

==============================================================================
Generated: {export_data['export_timestamp']}
Platform: Civic Engagement Platform - Constitutional Democracy
==============================================================================
"""
                
                with open(founder_file, 'w', encoding='utf-8') as f:
                    f.write(key_content)
                
                print(f"   📄 {founder_id} key exported to: {founder_file}")
            
            # Create master export file with all keys
            master_export_file = export_dir / 'ALL_FOUNDER_KEYS.json'
            import json
            with open(master_export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"\n📁 Master export file created: {master_export_file}")
            
            # Security warning
            print("\n" + "="*80)
            print("🚨 CRITICAL SECURITY WARNING 🚨")
            print("="*80)
            print("The Founder private keys have been generated and exported to:")
            print(f"   {export_dir.absolute()}")
            print("")
            print("IMMEDIATE ACTIONS REQUIRED:")
            print("1. Securely distribute individual key files to each genesis Founder")
            print("2. Each Founder should create offline backups in multiple secure locations")
            print("3. DELETE the distribution directory after keys are distributed")
            print("4. Founders should register accounts using their private keys")
            print("5. Monitor the platform for successful Founder registrations")
            print("")
            print("CONSTITUTIONAL FRAMEWORK:")
            print("- Maximum 7 Founders per constitutional requirement")
            print("- Founder decisions require supermajority consensus (75%)")
            print("- Founders cannot override citizen constitutional rights")
            print("- Emergency powers limited to platform-threatening situations")
            print("="*80)
        
        else:
            print(f"❌ Failed to export Founder keys: {export_message}")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure cryptography is installed: pip install cryptography")
    
    except Exception as e:
        print(f"❌ Error setting up Founder keys: {e}")

def export_existing_keys(founder_manager):
    """Export existing Founder keys for distribution"""
    print("\n📁 Exporting existing Founder keys...")
    
    success, message, export_data = founder_manager.export_founder_keys_for_distribution()
    if not success:
        print(f"❌ Export failed: {message}")
        return
    
    export_dir = Path('users/founder_keys/distribution')
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Create individual key files
    for founder_id, founder_info in export_data['founder_keys'].items():
        founder_file = export_dir / f"{founder_id}_private_key.txt"
        
        key_content = f"""
==============================================================================
CIVIC ENGAGEMENT PLATFORM - {founder_id} PRIVATE KEY
==============================================================================

FOUNDER ID: {founder_info['founder_id']}
KEY FINGERPRINT: {founder_info['key_fingerprint']}

PRIVATE KEY (PEM FORMAT):
{founder_info['private_key_pem']}

==============================================================================
"""
        
        with open(founder_file, 'w', encoding='utf-8') as f:
            f.write(key_content)
        
        print(f"   📄 {founder_id} key exported to: {founder_file}")
    
    print(f"\n✅ Keys exported to: {export_dir.absolute()}")

def test_founder_key_validation():
    """Test the Founder key validation system"""
    print("\n🧪 Testing Founder Key Validation System...")
    
    try:
        from users.founder_keys import FounderKeyManager
        
        founder_manager = FounderKeyManager()
        
        # Get keys info
        success, message, keys_info = founder_manager.get_founder_keys_info()
        if not success:
            print(f"❌ No Founder keys found: {message}")
            return
        
        print(f"✅ Founder key system loaded")
        print(f"   Master fingerprint: {keys_info['master_fingerprint']}")
        print(f"   Available Founders: {keys_info['founder_count']}")
        print(f"   Assigned Founders: {keys_info['assigned_founders']}")
        
        # Test with first available key
        import json
        master_file = Path('users/founder_keys/founder_master.json')
        if master_file.exists():
            with open(master_file, 'r') as f:
                master_data = json.load(f)
            
            # Test validation with FOUNDER_01 key
            founder_01_key = master_data['founder_keys']['FOUNDER_01']['private_key_pem']
            
            is_valid, validation_message, founder_info = founder_manager.validate_founder_key(founder_01_key)
            
            if is_valid:
                print(f"✅ Key validation successful!")
                print(f"   Founder ID: {founder_info['founder_id']}")
                print(f"   Key fingerprint: {founder_info['key_fingerprint']}")
            else:
                print(f"❌ Key validation failed: {validation_message}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Set up new Founder key system")
    print("2. Export existing keys for distribution")
    print("3. Test Founder key validation")
    print("4. View Founder key system info")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        setup_founder_keys()
    elif choice == '2':
        try:
            from users.founder_keys import FounderKeyManager
            founder_manager = FounderKeyManager()
            export_existing_keys(founder_manager)
        except Exception as e:
            print(f"❌ Error: {e}")
    elif choice == '3':
        test_founder_key_validation()
    elif choice == '4':
        try:
            from users.founder_keys import FounderKeyManager
            founder_manager = FounderKeyManager()
            success, message, info = founder_manager.get_founder_keys_info()
            if success:
                print(f"\n📊 Founder Key System Info:")
                print(f"   Master fingerprint: {info['master_fingerprint']}")
                print(f"   Total Founders: {info['founder_count']}")
                print(f"   Assigned Founders: {info['assigned_founders']}")
                print(f"   Created: {info['created_at']}")
            else:
                print(f"❌ {message}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Invalid choice")