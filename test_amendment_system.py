#!/usr/bin/env python3
"""
Simple test for the contract amendment system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from civic_desktop.contracts.amendment_system import (
    ContractAmendmentManager, JurisdictionLevel, ChangeType
)

def test_amendment_system():
    """Test the amendment system functionality"""
    print("🧪 Testing Contract Amendment System")
    print("=" * 50)
    
    # Initialize the amendment manager
    manager = ContractAmendmentManager()
    
    # Test 1: Create a new amendment proposal
    print("\n📝 Test 1: Creating Amendment Proposal")
    amendment_id = manager.propose_amendment(
        proposer_email="test_citizen@example.com",
        proposer_name="Test Citizen",
        article_section="ARTICLE I.1.A",
        change_type=ChangeType.MODIFICATION,
        current_text="The Congress shall make no law...",
        proposed_text="The Congress shall make no law restricting peaceful assembly...",
        rationale="We need to strengthen the right to peaceful assembly in our current political climate.",
        jurisdiction_level=JurisdictionLevel.CITY,
        jurisdiction_name="Springfield, Illinois"
    )
    
    print(f"✅ Amendment proposal created with ID: {amendment_id}")
    
    # Test 2: Load and display the amendment
    print("\n📋 Test 2: Loading Amendment Details")
    manager.load_amendments()
    amendment = manager.get_amendment(amendment_id)
    
    if amendment:
        print(f"✅ Amendment loaded successfully")
        print(f"   - Proposer: {amendment.proposer_name}")
        print(f"   - Article: {amendment.article_section}")
        print(f"   - Status: {amendment.status.value}")
        print(f"   - Jurisdiction: {amendment.jurisdiction_level.value} - {amendment.jurisdiction_name}")
    else:
        print("❌ Failed to load amendment")
    
    # Test 3: Start local debate
    print("\n💬 Test 3: Starting Local Debate")
    success = manager.start_local_debate(amendment_id)
    if success:
        print("✅ Local debate started successfully")
        # Reload to see status change
        manager.load_amendments()
        amendment = manager.get_amendment(amendment_id)
        print(f"   - New status: {amendment.status.value}")
    else:
        print("❌ Failed to start local debate")
    
    # Test 4: Add a comment
    print("\n💭 Test 4: Adding Comment to Debate")
    success = manager.add_comment(
        amendment_id,
        "debate_participant@example.com",
        "Debate Participant",
        "I strongly support this amendment as it clarifies an important constitutional right.",
        is_support=True
    )
    if success:
        print("✅ Comment added successfully")
        # Reload and check comments
        manager.load_amendments()
        amendment = manager.get_amendment(amendment_id)
        print(f"   - Total comments: {len(amendment.comments)}")
        if amendment.comments:
            latest_comment = amendment.comments[-1]
            print(f"   - Latest: \"{latest_comment.get('comment_text', '')}\"")
    else:
        print("❌ Failed to add comment")
    
    # Test 5: Start voting period
    print("\n🗳️ Test 5: Starting Voting Period")
    success = manager.start_voting_period(amendment_id)
    if success:
        print("✅ Voting period started successfully")
        manager.load_amendments()
        amendment = manager.get_amendment(amendment_id)
        print(f"   - New status: {amendment.status.value}")
    else:
        print("❌ Failed to start voting period")
    
    # Test 6: Cast some votes
    print("\n🗳️ Test 6: Casting Votes")
    voters = [
        ("voter1@example.com", "for"),
        ("voter2@example.com", "for"),
        ("voter3@example.com", "against"),
        ("voter4@example.com", "for"),
        ("voter5@example.com", "abstain")
    ]
    
    for email, vote in voters:
        success = manager.cast_vote(amendment_id, email, vote)
        print(f"   - {email}: {vote} {'✅' if success else '❌'}")
    
    # Check vote tally
    manager.load_amendments()
    amendment = manager.get_amendment(amendment_id)
    print(f"\n📊 Vote Results:")
    print(f"   - For: {amendment.votes_for}")
    print(f"   - Against: {amendment.votes_against}")
    print(f"   - Abstain: {amendment.votes_abstain}")
    
    total_votes = amendment.votes_for + amendment.votes_against + amendment.votes_abstain
    if total_votes > 0:
        approval_rate = (amendment.votes_for / (amendment.votes_for + amendment.votes_against)) * 100
        print(f"   - Approval Rate: {approval_rate:.1f}%")
    
    print("\n🎉 Amendment System Test Complete!")
    print(f"📁 Amendment data stored in: {manager.amendments_file}")

if __name__ == "__main__":
    test_amendment_system()