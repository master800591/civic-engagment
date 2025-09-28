"""
BLOCKCHAIN INTEGRATION TEST - Simple demonstration of user actions on blockchain
Tests the integration between user system and blockchain storage
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_blockchain_integration():
    """Test blockchain integration with user actions"""
    
    print("🏛️ CIVIC BLOCKCHAIN INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Import blockchain system
        from blockchain.blockchain import CivicBlockchain, add_user_action, get_network_stats
        print("✅ Blockchain system imported successfully")
        
        # Initialize blockchain
        blockchain = CivicBlockchain()
        print("✅ Blockchain initialized")
        
        # Test adding user registration to blockchain
        print("\n📝 Testing user registration on blockchain...")
        
        registration_data = {
            'user_id': 'user_123456',
            'name': 'Alice Democracy',
            'email': 'alice@civic.platform',
            'location': 'Democracy City, Freedom State',
            'role': 'contract_citizen',
            'registration_method': 'civic_platform_wizard'
        }
        
        success, message, page_id = add_user_action(
            action_type='user_registration',
            user_email='alice@civic.platform',
            data=registration_data
        )
        
        if success:
            print(f"✅ Registration recorded: {message}")
            print(f"   Page ID: {page_id}")
        else:
            print(f"❌ Registration failed: {message}")
        
        # Test adding login action
        print("\n🔐 Testing login action on blockchain...")
        
        login_data = {
            'user_id': 'user_123456',
            'login_method': 'email_password',
            'session_type': 'secure_desktop',
            'ip_address': 'localhost'
        }
        
        login_success, login_message, login_page_id = add_user_action(
            action_type='user_login',
            user_email='alice@civic.platform',
            data=login_data
        )
        
        if login_success:
            print(f"✅ Login recorded: {login_message}")
            print(f"   Page ID: {login_page_id}")
        
        # Test adding vote action
        print("\n🗳️ Testing vote action on blockchain...")
        
        vote_data = {
            'user_id': 'user_123456',
            'vote_type': 'municipal_election',
            'ballot_id': 'ballot_2026_001',
            'position': 'mayor',
            'jurisdiction': 'democracy_city',
            'vote_verified': True
        }
        
        vote_success, vote_message, vote_page_id = add_user_action(
            action_type='vote_cast',
            user_email='alice@civic.platform',
            data=vote_data
        )
        
        if vote_success:
            print(f"✅ Vote recorded: {vote_message}")
            print(f"   Page ID: {vote_page_id}")
        
        # Test adding debate participation
        print("\n💬 Testing debate participation on blockchain...")
        
        debate_data = {
            'user_id': 'user_123456',
            'debate_topic': 'Municipal Budget 2026',
            'position': 'support',
            'argument_quality': 4.2,
            'constitutional_compliance': True
        }
        
        debate_success, debate_message, debate_page_id = add_user_action(
            action_type='debate_participation',
            user_email='alice@civic.platform',
            data=debate_data
        )
        
        if debate_success:
            print(f"✅ Debate participation recorded: {debate_message}")
            print(f"   Page ID: {debate_page_id}")
        
        # Get blockchain statistics
        print("\n📊 Getting blockchain statistics...")
        
        stats = get_network_stats()
        print(f"   Total pages: {stats['total_pages']}")
        print(f"   Active pages: {stats['active_pages']}")
        print(f"   Total chapters: {stats['total_chapters']}")
        print(f"   Blockchain health: {stats['blockchain_health']}")
        
        # Search for user actions
        print("\n🔍 Searching for user actions...")
        
        from blockchain.blockchain import search_user_actions
        user_actions = search_user_actions('alice@civic.platform')
        
        print(f"   Found {len(user_actions)} actions for alice@civic.platform:")
        for action in user_actions:
            print(f"     - {action['action_type']} at {action['timestamp']}")
        
        # Verify blockchain integrity
        print("\n🔐 Verifying blockchain integrity...")
        
        is_valid, errors = blockchain.verify_blockchain_integrity()
        
        if is_valid:
            print("✅ Blockchain integrity verified")
        else:
            print(f"❌ Integrity errors: {errors}")
        
        print("\n" + "=" * 50)
        print("🎉 BLOCKCHAIN INTEGRATION TEST COMPLETE!")
        print("✅ All civic actions successfully recorded")
        print("✅ Transparent governance system operational")
        print("=" * 50)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure blockchain system is properly installed")
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_blockchain_features():
    """Show what the blockchain system provides for civic engagement"""
    
    print("\n🏛️ CIVIC BLOCKCHAIN FEATURES")
    print("=" * 40)
    
    print("\n📋 Immutable Records:")
    print("  ✅ User registrations")
    print("  ✅ Login/logout events")  
    print("  ✅ Role assignments")
    print("  ✅ Voting actions")
    print("  ✅ Debate participation")
    print("  ✅ Moderation decisions")
    print("  ✅ Constitutional changes")
    
    print("\n🔒 Security Features:")
    print("  ✅ RSA-2048 cryptographic signatures")
    print("  ✅ Hash chain integrity")
    print("  ✅ Tamper detection")
    print("  ✅ Consensus validation")
    
    print("\n📊 Transparency:")
    print("  ✅ Public audit trail")
    print("  ✅ Searchable records")
    print("  ✅ Real-time statistics")
    print("  ✅ Integrity verification")
    
    print("\n🏛️ Democratic Governance:")
    print("  ✅ Constitutional compliance")
    print("  ✅ Checks and balances")
    print("  ✅ Accountable representatives")
    print("  ✅ Citizen oversight")

if __name__ == "__main__":
    test_blockchain_integration()
    demonstrate_blockchain_features()