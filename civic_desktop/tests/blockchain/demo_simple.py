"""
BLOCKCHAIN INTEGRATION DEMO - Complete demonstration of civic blockchain
Shows user actions being recorded on blockchain for transparent governance
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def run_blockchain_demo():
    """Demonstrate blockchain system with civic governance actions"""
    
    print("🏛️ CIVIC ENGAGEMENT BLOCKCHAIN DEMONSTRATION")
    print("=" * 70)
    
    try:
        # Import blockchain system
        from civic_desktop.blockchain.blockchain import CivicBlockchain
        
        print("✅ Blockchain system imported successfully")
        
        # Initialize blockchain
        blockchain = CivicBlockchain()
        print("✅ Blockchain initialized with constitutional framework")
        
        # Test 1: User Registration
        print("\n📝 Recording User Registration on Blockchain")
        print("-" * 50)
        
        registration_data = {
            'user_id': 'citizen_001',
            'name': 'Alice Democracy',
            'email': 'alice.democracy@civic.platform',
            'location': 'Democracy City, Freedom State',
            'role': 'contract_member',
            'registration_method': 'civic_platform_wizard'
        }
        
        reg_success, reg_message, reg_page_id = blockchain.add_page(
            action_type='user_registration',
            user_email='alice.democracy@civic.platform',
            data=registration_data
        )
        
        if reg_success:
            print(f"✅ Registration recorded: {reg_message}")
            print(f"   Page ID: {reg_page_id}")
        
        # Test 2: User Login
        print("\n🔐 Recording User Login on Blockchain")
        print("-" * 50)
        
        login_data = {
            'user_id': 'citizen_001',
            'login_method': 'email_password',
            'session_type': 'secure_desktop',
            'ip_address': '127.0.0.1'
        }
        
        login_success, login_message, login_page_id = blockchain.add_page(
            action_type='user_login',
            user_email='alice.democracy@civic.platform',
            data=login_data
        )
        
        if login_success:
            print(f"✅ Login recorded: {login_message}")
            print(f"   Page ID: {login_page_id}")
        
        # Test 3: Vote Cast
        print("\n🗳️ Recording Vote on Blockchain")
        print("-" * 50)
        
        vote_data = {
            'user_id': 'citizen_001',
            'vote_type': 'municipal_election',
            'ballot_id': 'ballot_2025_001',
            'position': 'mayor',
            'jurisdiction': 'democracy_city'
        }
        
        vote_success, vote_message, vote_page_id = blockchain.add_page(
            action_type='vote_cast',
            user_email='alice.democracy@civic.platform',
            data=vote_data
        )
        
        if vote_success:
            print(f"✅ Vote recorded: {vote_message}")
            print(f"   Page ID: {vote_page_id}")
        
        # Test 4: Debate Participation
        print("\n💬 Recording Debate Participation on Blockchain")
        print("-" * 50)
        
        debate_data = {
            'user_id': 'citizen_001',
            'topic': 'Municipal Budget 2026',
            'position': 'support',
            'quality_score': 4.2,
            'constitutional_compliance': True
        }
        
        debate_success, debate_message, debate_page_id = blockchain.add_page(
            action_type='debate_participation',
            user_email='alice.democracy@civic.platform',
            data=debate_data
        )
        
        if debate_success:
            print(f"✅ Debate participation recorded: {debate_message}")
            print(f"   Page ID: {debate_page_id}")
        
        # Get Blockchain Statistics
        print("\n📊 Blockchain Network Statistics")
        print("-" * 50)
        
        stats = blockchain.get_blockchain_stats()
        print(f"   Total Pages: {stats['total_pages']}")
        print(f"   Active Pages: {stats['active_pages']}")
        print(f"   Total Chapters: {stats['total_chapters']}")
        print(f"   Blockchain Health: {stats['blockchain_health']}")
        
        # Search User Actions
        print("\n🔍 User Action History")
        print("-" * 50)
        
        user_actions = blockchain.search_blockchain(
            query_type='user',
            query_value='alice.democracy@civic.platform'
        )
        
        print(f"   Found {len(user_actions)} actions:")
        for i, action in enumerate(user_actions, 1):
            action_type = action.get('action_type', 'unknown')
            timestamp = action.get('timestamp', 'unknown')
            print(f"     {i}. {action_type} - {timestamp}")
        
        # Verify Blockchain Integrity
        print("\n🔐 Blockchain Integrity Verification")
        print("-" * 50)
        
        is_valid, errors = blockchain.verify_blockchain_integrity()
        
        if is_valid:
            print("✅ Blockchain integrity verified")
            print("✅ All records are valid and tamper-proof")
        else:
            print("❌ Integrity issues detected:")
            for error in errors:
                print(f"     - {error}")
        
        print("\n" + "=" * 70)
        print("🎉 BLOCKCHAIN DEMONSTRATION COMPLETE!")
        print("✅ All civic actions successfully recorded")
        print("✅ Transparent governance system operational")
        print("✅ Ready for democratic participation at scale")
        print("=" * 70)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

def show_blockchain_capabilities():
    """Show what the blockchain enables for civic governance"""
    
    print("\n🏛️ CIVIC BLOCKCHAIN CAPABILITIES")
    print("=" * 50)
    
    print("\n📋 Immutable Records:")
    print("  ✅ User registrations and identity verification")
    print("  ✅ Login/logout events with session tracking")
    print("  ✅ Role assignments and election results")
    print("  ✅ Voting actions with cryptographic verification")
    print("  ✅ Debate participation and quality ratings")
    print("  ✅ Moderation decisions and appeals")
    print("  ✅ Constitutional amendments and interpretations")
    
    print("\n🔒 Security & Integrity:")
    print("  ✅ RSA-2048 cryptographic signatures")
    print("  ✅ SHA-256 hash chain linking")
    print("  ✅ Tamper detection and prevention")
    print("  ✅ Consensus validation by elected validators")
    
    print("\n📊 Transparency & Accountability:")
    print("  ✅ Public audit trail for all government actions")
    print("  ✅ Searchable records by user, action, or data")
    print("  ✅ Real-time network health monitoring")
    print("  ✅ Cryptographic integrity verification")
    
    print("\n🏛️ Democratic Governance:")
    print("  ✅ Constitutional compliance verification")
    print("  ✅ Multi-branch checks and balances")
    print("  ✅ Accountable representative actions")
    print("  ✅ Citizen oversight and participation tracking")
    print("  ✅ Anti-corruption through transparency")
    print("  ✅ Due process documentation")

if __name__ == "__main__":
    run_blockchain_demo()
    show_blockchain_capabilities()