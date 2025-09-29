"""
FOUNDER KEY INTEGRATION TEST - Demonstrate complete Founder key workflow
Tests user registration with Founder key validation and contract role assignment
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_founder_registration_workflow():
    """Test complete Founder registration workflow"""
    
    print("🏛️ FOUNDER KEY INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Import required modules
        from civic_desktop.users.founder_keys import FounderKeyManager
        from civic_desktop.users.contract_roles import ContractRoleManager, ContractRole
        from civic_desktop.users.backend import UserBackend
        
        print("✅ All modules imported successfully")
        
        # Step 1: Initialize systems
        print("\n🔧 Initializing systems...")
        
        founder_manager = FounderKeyManager()
        role_manager = ContractRoleManager()
        user_backend = UserBackend()
        
        print("✅ Systems initialized")
        
        # Step 2: Check if Founder keys exist, create if needed
        print("\n🔑 Checking Founder key system...")
        
        success, message, keys_info = founder_manager.get_founder_keys_info()
        if not success:
            print("📝 Creating Founder key system...")
            success, message, founder_data = founder_manager.generate_founder_master_key()
            
            if success:
                print(f"✅ Founder keys created: {founder_data['founder_count']} keys")
            else:
                print(f"❌ Failed to create Founder keys: {message}")
                return
        else:
            print(f"✅ Founder key system exists: {keys_info['founder_count']} keys")
        
        # Step 3: Get a Founder private key for testing
        print("\n🔐 Getting test Founder key...")
        
        import json
        master_file = Path('civic_desktop/users/founder_keys/founder_master.json')
        if not master_file.exists():
            print("❌ Master key file not found")
            return
        
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # Use FOUNDER_01 for testing
        test_founder_key = master_data['founder_keys']['FOUNDER_01']['private_key_pem']
        test_founder_id = master_data['founder_keys']['FOUNDER_01']['founder_id']
        
        print(f"✅ Retrieved test key: {test_founder_id}")
        
        # Step 4: Test key validation
        print("\n🧪 Testing key validation...")
        
        is_valid, validation_message, founder_info = founder_manager.validate_founder_key(test_founder_key)
        
        if is_valid:
            print(f"✅ Key validation successful!")
            print(f"   Founder ID: {founder_info['founder_id']}")
            print(f"   Key fingerprint: {founder_info['key_fingerprint'][:16]}...")
        else:
            print(f"❌ Key validation failed: {validation_message}")
            return
        
        # Step 5: Test user registration with Founder key
        print("\n👤 Testing user registration with Founder key...")
        
        test_user_data = {
            'first_name': 'Genesis',
            'last_name': 'Founder',
            'email': f'founder.{test_founder_id.lower()}@civic-platform.org',
            'password': 'SecureFounderPassword123!',
            'confirm_password': 'SecureFounderPassword123!',
            'city': 'Capital City',
            'state': 'Democracy State',
            'country': 'Constitutional Republic',
            'terms_accepted': True,
            'founder_private_key': test_founder_key  # This is the key part!
        }
        
        reg_success, reg_message, user_record = user_backend.register_user(test_user_data)
        
        if reg_success:
            print(f"✅ User registration successful!")
            print(f"   User ID: {user_record['user_id']}")
            print(f"   Email: {user_record['email']}")
            print(f"   Role: {user_record['role']}")
            
            # Check if role was assigned correctly
            if user_record['role'] == 'contract_founder':
                print("🏛️ FOUNDER ROLE CONFIRMED!")
            else:
                print(f"⚠️ Unexpected role: {user_record['role']}")
        else:
            print(f"❌ User registration failed: {reg_message}")
            return
        
        # Step 6: Verify contract role assignment
        print("\n🏛️ Verifying contract role assignment...")
        
        role_success, role_message, user_role = role_manager.get_user_role(user_record['email'])
        
        if role_success:
            print(f"✅ Contract role retrieved: {user_role.value if user_role else 'None'}")
            
            if user_role == ContractRole.CONTRACT_FOUNDER:
                print("🎉 FOUNDER CONTRACT ROLE CONFIRMED!")
                
                # Test Founder permissions
                print("\n🔒 Testing Founder permissions...")
                
                test_permissions = [
                    'modify_core_governance_contracts',
                    'emergency_protocol_override',
                    'constitutional_emergency_declaration'
                ]
                
                for permission in test_permissions:
                    perm_success, perm_message, has_permission = role_manager.check_user_permission(
                        user_record['email'], permission
                    )
                    
                    if perm_success and has_permission:
                        print(f"   ✅ {permission}: GRANTED")
                    else:
                        print(f"   ❌ {permission}: DENIED")
            else:
                print(f"⚠️ Unexpected contract role: {user_role}")
        else:
            print(f"❌ Failed to get contract role: {role_message}")
        
        # Step 7: Verify Founder key assignment
        print("\n🔗 Verifying Founder key assignment...")
        
        assignment_success, assignment_message, updated_keys_info = founder_manager.get_founder_keys_info()
        
        if assignment_success:
            print(f"✅ Updated Founder key info:")
            print(f"   Total Founders: {updated_keys_info['founder_count']}")
            print(f"   Assigned Founders: {updated_keys_info['assigned_founders']}")
            
            for founder_entry in updated_keys_info['active_founders']:
                if founder_entry['founder_id'] == test_founder_id:
                    print(f"   🎯 {test_founder_id} assigned to: {founder_entry['user_email']}")
                    break
        else:
            print(f"❌ Failed to get updated key info: {assignment_message}")
        
        # Step 8: Test governance statistics
        print("\n📊 Checking governance statistics...")
        
        stats_success, stats_message, governance_stats = role_manager.get_governance_stats()
        
        if stats_success:
            print(f"✅ Governance statistics:")
            print(f"   Total Citizens: {governance_stats['total_citizens']}")
            print(f"   Total Representatives: {governance_stats['total_representatives']}")
            print(f"   Total Senators: {governance_stats['total_senators']}")
            print(f"   Total Elders: {governance_stats['total_elders']}")
            print(f"   Total Founders: {governance_stats['total_founders']}")
            print(f"   Max Founders Allowed: {governance_stats['max_founders_allowed']}")
        else:
            print(f"❌ Failed to get governance stats: {stats_message}")
        
        print("\n" + "=" * 60)
        print("🎉 FOUNDER KEY INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("🏛️ Genesis Founder has been registered with full constitutional authority")
        print("=" * 60)
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all modules are in place and cryptography is installed")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_invalid_founder_key():
    """Test registration with invalid Founder key"""
    
    print("\n🚫 Testing invalid Founder key handling...")
    
    try:
        from civic_desktop.users.backend import UserBackend
        
        user_backend = UserBackend()
        
        # Test with invalid key
        invalid_user_data = {
            'first_name': 'Invalid',
            'last_name': 'Founder',
            'email': 'invalid.founder@civic-platform.org',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
            'city': 'Test City',
            'state': 'Test State',
            'country': 'Test Country',
            'terms_accepted': True,
            'founder_private_key': 'INVALID_PRIVATE_KEY_DATA'
        }
        
        reg_success, reg_message, user_record = user_backend.register_user(invalid_user_data)
        
        if reg_success:
            print(f"✅ Registration successful with invalid key")
            print(f"   Role assigned: {user_record['role']}")
            
            # Should be regular citizen, not founder
            if user_record['role'] == 'contract_member':
                print("✅ Correctly assigned contract_member role")
            else:
                print(f"⚠️ Unexpected role: {user_record['role']}")
        else:
            print(f"❌ Registration failed: {reg_message}")
    
    except Exception as e:
        print(f"❌ Invalid key test failed: {e}")

def test_multiple_founder_registrations():
    """Test multiple Founder registrations"""
    
    print("\n👥 Testing multiple Founder registrations...")
    
    try:
        from civic_desktop.users.founder_keys import FounderKeyManager
        from civic_desktop.users.backend import UserBackend
        
        founder_manager = FounderKeyManager()
        user_backend = UserBackend()
        
        # Get master data
        import json
        master_file = Path('civic_desktop/users/founder_keys/founder_master.json')
        
        if not master_file.exists():
            print("❌ Master key file not found")
            return
        
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # Test with FOUNDER_02 and FOUNDER_03
        test_founders = ['FOUNDER_02', 'FOUNDER_03']
        
        for founder_id in test_founders:
            if founder_id in master_data['founder_keys']:
                founder_key = master_data['founder_keys'][founder_id]['private_key_pem']
                
                test_user_data = {
                    'first_name': 'Genesis',
                    'last_name': f'Founder-{founder_id[-2:]}',
                    'email': f'founder.{founder_id.lower()}@civic-platform.org',
                    'password': 'SecureFounderPassword123!',
                    'confirm_password': 'SecureFounderPassword123!',
                    'city': 'Capital City',
                    'state': 'Democracy State',
                    'country': 'Constitutional Republic',
                    'terms_accepted': True,
                    'founder_private_key': founder_key
                }
                
                reg_success, reg_message, user_record = user_backend.register_user(test_user_data)
                
                if reg_success and user_record['role'] == 'contract_founder':
                    print(f"✅ {founder_id} registered successfully")
                else:
                    print(f"⚠️ {founder_id} registration issue: {reg_message}")
        
        # Check final statistics
        success, message, keys_info = founder_manager.get_founder_keys_info()
        if success:
            print(f"\n📊 Final Founder statistics:")
            print(f"   Assigned Founders: {keys_info['assigned_founders']}")
            print(f"   Remaining slots: {7 - keys_info['assigned_founders']}")
    
    except Exception as e:
        print(f"❌ Multiple founder test failed: {e}")

if __name__ == "__main__":
    print("Choose a test:")
    print("1. Complete Founder registration workflow")
    print("2. Test invalid Founder key handling")
    print("3. Test multiple Founder registrations")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        test_founder_registration_workflow()
    elif choice == '2':
        test_invalid_founder_key()
    elif choice == '3':
        test_multiple_founder_registrations()
    elif choice == '4':
        print("🧪 Running all Founder key tests...\n")
        test_founder_registration_workflow()
        test_invalid_founder_key()
        test_multiple_founder_registrations()
        print("\n✅ All tests completed!")
    else:
        print("❌ Invalid choice")