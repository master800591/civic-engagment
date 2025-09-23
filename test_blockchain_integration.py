#!/usr/bin/env python3
"""
Test the blockchain integration for the preliminary ranks system.
This tests that all user data operations properly use blockchain as primary storage.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'civic_desktop'))

from datetime import datetime, timezone
from civic_desktop.users.backend import UserBackend
from civic_desktop.users.rank_manager import RankManager
from civic_desktop.blockchain.blockchain import Blockchain

def test_blockchain_integration():
    print("🔗 Testing Blockchain Integration for Preliminary Ranks System")
    print("=" * 60)
    
    # Test 1: Load users from blockchain
    print("\n1. Testing load_users() from blockchain...")
    users = UserBackend.load_users()
    print(f"   ✅ Loaded {len(users)} users from blockchain")
    
    if users:
        user = users[0]
        print(f"   📋 Sample user: {user.get('first_name', 'Unknown')} {user.get('last_name', 'Unknown')}")
        print(f"   🎭 Current role: {user.get('role', 'Unknown')}")
        print(f"   📚 Training completed: {len(user.get('training_completed', []))}")
        print(f"   📈 Rank history entries: {len(user.get('rank_history', []))}")
    
    # Test 2: Test rank determination
    print("\n2. Testing rank determination system...")
    
    # Test minor
    test_data = {
        'birth_date': '2010-01-01',  # Under 18
        'identity_verified': False,
        'training_completed': []
    }
    initial_rank = RankManager.determine_initial_rank(test_data)
    print(f"   ✅ Minor (age 14) gets rank: {initial_rank}")
    
    # Test unverified adult
    test_data = {
        'birth_date': '1990-01-01',  # Over 18
        'identity_verified': False,
        'training_completed': []
    }
    initial_rank = RankManager.determine_initial_rank(test_data)
    print(f"   ✅ Unverified adult gets rank: {initial_rank}")
    
    # Test verified adult (should get Probation)
    test_data = {
        'birth_date': '1990-01-01',  # Over 18
        'identity_verified': True,
        'training_completed': []
    }
    initial_rank = RankManager.determine_initial_rank(test_data)
    print(f"   ✅ Verified adult gets rank: {initial_rank}")
    
    # Test 3: Check blockchain structure
    print("\n3. Testing blockchain structure...")
    chain = Blockchain.load_chain()
    pages = chain.get('pages', [])
    print(f"   ✅ Blockchain has {len(pages)} pages")
    
    # Count different action types
    action_counts = {}
    for page in pages:
        action = page.get('data', {}).get('action', 'unknown')
        action_counts[action] = action_counts.get(action, 0) + 1
    
    print("   📊 Action distribution:")
    for action, count in action_counts.items():
        print(f"      • {action}: {count}")
    
    # Test 4: Check if preliminary rank fields are in user data
    print("\n4. Testing preliminary rank fields in user data...")
    if users:
        user = users[0]
        preliminary_fields = [
            'birth_date', 'government_id_type', 'government_id_number',
            'identity_verified', 'address_verified', 'email_verified',
            'parental_consent', 'parent_email', 'parent_name',
            'training_completed', 'verification_status', 'rank_history'
        ]
        
        for field in preliminary_fields:
            if field in user:
                print(f"   ✅ {field}: {user[field]}")
            else:
                print(f"   ❌ Missing field: {field}")
    
    print("\n🎉 Blockchain integration test completed!")
    return True

if __name__ == "__main__":
    try:
        test_blockchain_integration()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()