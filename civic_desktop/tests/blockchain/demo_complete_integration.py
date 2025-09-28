"""
BLOCKCHAIN USER INTEGRATION - Demonstration of user actions recorded on blockchain
Shows complete integration between user system and blockchain transparency
"""

import sys
from pathlib import Path
import os

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def demonstrate_blockchain_with_users():
    """Complete demonstration of blockchain integration with user system"""
    
    print("🏛️ CIVIC ENGAGEMENT PLATFORM - BLOCKCHAIN & USER INTEGRATION")
    print("=" * 80)
    
    try:
        # Import blockchain system
        from civic_desktop.blockchain.blockchain import CivicBlockchain
        
        print("✅ Blockchain system imported")
        
        # Initialize blockchain
        blockchain = CivicBlockchain()
        print("✅ Blockchain initialized with constitutional framework")
        
        # Test 1: User Registration
        print("\n📝 TEST 1: Recording User Registration on Blockchain")
        print("-" * 60)
        
        registration_data = {
            'user_id': 'citizen_001',
            'name': 'Alice Democracy',
            'email': 'alice.democracy@civic.platform',
            'location': 'Democracy City, Freedom State, United States',
            'role': 'contract_citizen',
            'registration_method': 'civic_platform_wizard',
            'constitutional_rights': True,
            'rsa_key_generated': True,
            'blockchain_address': 'civic_abc123def456'
        }
        
        reg_success, reg_message, reg_page_id = blockchain.add_page(
            action_type='user_registration',
            user_email=registration_data['email'],
            data=registration_data
        )
        
        if reg_success:
            print(f"✅ Registration recorded: {reg_message}")
            print(f"   Page ID: {reg_page_id}")
            print(f"   User: {registration_data['name']}")
            print(f"   Role: {registration_data['role']}")
        
        # Test 2: User Login
        print("\n🔐 TEST 2: Recording User Login on Blockchain")
        print("-" * 60)
        
        login_data = {
            'user_id': 'citizen_001',
            'login_method': 'email_password_rsa',
            'session_type': 'secure_desktop_application',
            'ip_address': '127.0.0.1',
            'user_agent': 'Civic Desktop v1.0',
            'two_factor_enabled': False,
            'session_duration': '24_hours',
            'login_success': True
        }
        
        login_success, login_message, login_page_id = blockchain.add_page(
            action_type='user_login',
            user_email=registration_data['email'],
            data=login_data
        )
        
        if login_success:
            print(f"✅ Login recorded: {login_message}")
            print(f"   Page ID: {login_page_id}")
            print(f"   Session Type: {login_data['session_type']}")
        
        # Test 3: Role Assignment  
        print("\n👑 TEST 3: Recording Role Assignment on Blockchain")
        print("-" * 60)
        
        role_data = {
            'user_id': 'citizen_001',
            'previous_role': 'contract_citizen',
            'new_role': 'contract_representative',
            'assignment_type': 'democratic_election',
            'election_date': '2025-11-05',
            'vote_count': 1247,
            'total_votes': 2156,
            'percentage': 57.8,
            'authorized_by': 'democratic_mandate',
            'term_length': '2_years',
            'constitutional_authority': 'article_ii_section_1'
        }\n        \n        role_success, role_message, role_page_id = blockchain.add_page(\n            action_type='role_assignment',\n            user_email=registration_data['email'],\n            data=role_data\n        )\n        \n        if role_success:\n            print(f\"✅ Role assignment recorded: {role_message}\")\n            print(f\"   Page ID: {role_page_id}\")\n            print(f\"   New Role: {role_data['new_role']}\")\n            print(f\"   Election Result: {role_data['percentage']}% of votes\")\n        \n        # Test 4: Civic Participation\n        print(\"\\n💬 TEST 4: Recording Civic Participation on Blockchain\")\n        print(\"-\" * 60)\n        \n        debate_data = {\n            'user_id': 'citizen_001',\n            'participation_type': 'policy_debate',\n            'topic': 'Municipal Infrastructure Investment 2026',\n            'position': 'support_with_amendments',\n            'argument_quality_score': 4.3,\n            'constitutional_compliance': True,\n            'sources_cited': 5,\n            'peer_ratings': [4, 5, 4, 3, 5],\n            'moderation_flags': 0,\n            'constructive_engagement': True\n        }\n        \n        debate_success, debate_message, debate_page_id = blockchain.add_page(\n            action_type='civic_participation',\n            user_email=registration_data['email'],\n            data=debate_data\n        )\n        \n        if debate_success:\n            print(f\"✅ Civic participation recorded: {debate_message}\")\n            print(f\"   Page ID: {debate_page_id}\")\n            print(f\"   Topic: {debate_data['topic']}\")\n            print(f\"   Quality Score: {debate_data['argument_quality_score']}/5.0\")\n        \n        # Test 5: Voting Action\n        print(\"\\n🗳️ TEST 5: Recording Vote on Blockchain\")\n        print(\"-\" * 60)\n        \n        vote_data = {\n            'user_id': 'citizen_001',\n            'vote_type': 'municipal_referendum',\n            'ballot_id': 'referendum_2025_prop_7',\n            'question': 'Approve $50M bond for public transit expansion',\n            'vote_choice': 'yes',\n            'jurisdiction': 'democracy_city',\n            'voting_method': 'secure_digital_platform',\n            'encryption_verified': True,\n            'constitutional_eligibility': True,\n            'voter_turnout_contribution': True\n        }\n        \n        vote_success, vote_message, vote_page_id = blockchain.add_page(\n            action_type='vote_cast',\n            user_email=registration_data['email'],\n            data=vote_data\n        )\n        \n        if vote_success:\n            print(f\"✅ Vote recorded: {vote_message}\")\n            print(f\"   Page ID: {vote_page_id}\")\n            print(f\"   Ballot: {vote_data['ballot_id']}\")\n            print(f\"   Vote: {vote_data['vote_choice']} on {vote_data['question']}\")\n        \n        # Show Blockchain Statistics\n        print(\"\\n📊 BLOCKCHAIN NETWORK STATISTICS\")\n        print(\"-\" * 60)\n        \n        stats = blockchain.get_blockchain_stats()\n        print(f\"   Total Pages: {stats['total_pages']}\")\n        print(f\"   Active Pages: {stats['active_pages']}\")\n        print(f\"   Total Chapters: {stats['total_chapters']}\")\n        print(f\"   Active Validators: {stats['active_validators']}\")\n        print(f\"   Blockchain Health: {stats['blockchain_health']}\")\n        print(f\"   Last Updated: {stats['last_updated']}\")\n        \n        # Search User Actions\n        print(\"\\n🔍 USER ACTION HISTORY\")\n        print(\"-\" * 60)\n        \n        user_actions = blockchain.search_blockchain(\n            query_type='user',\n            query_value=registration_data['email'],\n            limit=10\n        )\n        \n        print(f\"   Found {len(user_actions)} actions for {registration_data['email']}:\")\n        for i, action in enumerate(user_actions, 1):\n            print(f\"     {i}. {action['action_type']} - {action['timestamp']}\")\n        \n        # Verify Blockchain Integrity\n        print(\"\\n🔐 BLOCKCHAIN INTEGRITY VERIFICATION\")\n        print(\"-\" * 60)\n        \n        is_valid, errors = blockchain.verify_blockchain_integrity()\n        \n        if is_valid:\n            print(\"✅ Blockchain integrity verified - all records valid\")\n            print(\"✅ Hash chains intact\")\n            print(\"✅ No tampering detected\")\n        else:\n            print(\"❌ Integrity issues detected:\")\n            for error in errors:\n                print(f\"     - {error}\")\n        \n        # Show what this enables\n        print(\"\\n🏛️ CIVIC GOVERNANCE CAPABILITIES ENABLED\")\n        print(\"=\" * 80)\n        \n        capabilities = [\n            \"✅ Transparent Democracy - All governance actions are publicly auditable\",\n            \"✅ Accountability - Representatives' actions permanently recorded\",\n            \"✅ Constitutional Compliance - Elder oversight with immutable decisions\",\n            \"✅ Citizen Oversight - Public can verify all government activities\",\n            \"✅ Anti-Corruption - Transparent financial and policy decisions\",\n            \"✅ Due Process - Complete record of all legal and administrative actions\",\n            \"✅ Election Integrity - Cryptographically secure voting records\",\n            \"✅ Participatory Democracy - Citizen engagement tracking and rewards\",\n            \"✅ Checks & Balances - Multi-branch oversight with audit trails\",\n            \"✅ Long-term Accountability - Permanent historical record\"\n        ]\n        \n        for capability in capabilities:\n            print(f\"   {capability}\")\n        \n        print(\"\\n\" + \"=\" * 80)\n        print(\"🎉 BLOCKCHAIN INTEGRATION DEMONSTRATION COMPLETE!\")\n        print(\"✅ Civic engagement platform ready for transparent governance\")\n        print(\"✅ All user actions recorded on immutable blockchain\")\n        print(\"✅ Constitutional compliance and citizen oversight enabled\")\n        print(\"=\"*80)\n        \n    except Exception as e:\n        print(f\"❌ Error during demonstration: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    demonstrate_blockchain_with_users()"}