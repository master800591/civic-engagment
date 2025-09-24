#!/usr/bin/env python3
"""
Create test users for credit system testing - simplified version
"""

import os
import sys
import tempfile
import hashlib

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

def create_dummy_id_file():
    """Create a temporary dummy ID file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("DUMMY ID DOCUMENT FOR TESTING")
        return f.name

def create_test_users():
    """Create additional test users for credit system testing"""
    try:
        print("👥 Creating Test Users for Credit System")
        print("=" * 50)
        
        from civic_desktop.users.backend import UserBackend
        from civic_desktop.blockchain.blockchain import Blockchain
        
        # Test users to create
        test_users = [
            {
                'first_name': 'Alice',
                'last_name': 'Democracy',
                'email': 'alice@test.com',
                'password': 'test123',
                'address': '123 Democracy St',
                'city': 'TestCity',
                'state': 'TestState',
                'country': 'TestCountry',
                'birth_date': '1990-01-01',
                'id_type': 'drivers_license',
                'id_number': 'DL123456789'
            },
            {
                'first_name': 'Bob',
                'last_name': 'Citizen',
                'email': 'bob@test.com',
                'password': 'test123',
                'address': '456 Citizen Ave',
                'city': 'TestTown',
                'state': 'TestState',
                'country': 'TestCountry',
                'birth_date': '1985-05-15',
                'id_type': 'passport',
                'id_number': 'PP987654321'
            }
        ]
        
        # Create users
        for user_data in test_users:
            email = user_data['email']
            
            # Check if user already exists
            existing_user = UserBackend.get_user_by_email(email)
            if existing_user:
                print(f"   ✅ User {email} already exists")
                continue
            
            # Create dummy ID file
            id_file = create_dummy_id_file()
            
            try:
                # Register the user using the correct format
                success, message = UserBackend.register_user(user_data, id_file)
                
                if success:
                    print(f"   ✅ Created user: {user_data['first_name']} {user_data['last_name']} ({email})")
                else:
                    print(f"   ❌ Failed to create user {email}: {message}")
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(id_file)
                except:
                    pass
        
        # Show all users
        print("\n📊 Current Users:")
        users = UserBackend.load_users()
        for user in users:
            email = user.get('email', 'Unknown')
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            roles = ', '.join(user.get('roles', ['Unknown']))
            print(f"   - {name} ({email}) - {roles}")
        
        print(f"\n✅ Total users: {len(users)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if create_test_users():
        print("\n🎉 Test users created successfully!")
        print("\nNow you can run 'python test_credit_system.py' to test transactions between users.")
    else:
        print("\n❌ Failed to create test users.")