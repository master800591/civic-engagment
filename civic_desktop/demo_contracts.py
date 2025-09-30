#!/usr/bin/env python3
"""
Demo: Hierarchical Contract System Walkthrough
Shows complete workflow from contract creation to amendment voting
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from contracts.contract_types import ContractManager, ContractLevel
from contracts.amendment_system import AmendmentManager, ConstitutionalEnforcement, VoteOption
from contracts.genesis_contract import generate_contract_from_template, get_template_list


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def demo_contract_hierarchy():
    """Demonstrate the contract hierarchy"""
    print_header("STEP 1: Understanding the Contract Hierarchy")
    
    print("""
The Civic Engagement Platform uses a 4-level hierarchical governance system:

Level 0: Master Contract (Constitutional Foundation)
  └─ Contains: Fundamental rights, governance structure, checks & balances
  └─ Authority: Contract Founders + Citizen Ratification
  └─ Amendment: 75% Founders + 60% Citizen Approval

Level 1: Country Contract (National Governance)
  └─ Contains: Federal authority and national policies
  └─ Authority: Representatives + Senators + Elder Review
  └─ Amendment: 60% Bicameral + Elder + 55% Citizen Ratification

Level 2: State Contract (Regional Governance)
  └─ Contains: State-level governance and regional authority
  └─ Authority: State Representatives + Senators + Elder Review
  └─ Amendment: 60% State Bicameral + Elder Approval

Level 3: City Contract (Local Governance)
  └─ Contains: Municipal authority and local services
  └─ Authority: Local Representatives + Citizen Participation
  └─ Amendment: 55% Representatives + 50% Citizen Approval
    """)


def demo_template_generation():
    """Demonstrate template generation"""
    print_header("STEP 2: Governance Contract Templates")
    
    templates = get_template_list()
    print(f"\n📋 Available Templates: {len(templates)}")
    
    for template in templates:
        print(f"\n   • {template['name']} (Level {template['level']})")
    
    print("\n📜 Generating Master Contract Template...")
    master = generate_contract_from_template('master_contract', 'global')
    
    print("\n✅ Master Contract Generated:")
    print(f"   • Preamble: {master['preamble']['text'][:100]}...")
    print(f"   • Fundamental Rights: {len(master['fundamental_rights'])} rights defined")
    print(f"   • Governance Structure: {len(master['governance_structure']['branches'])} branches")


def demo_contract_creation():
    """Demonstrate contract creation"""
    print_header("STEP 3: Creating a City Governance Contract")
    
    manager = ContractManager()
    
    # Create a city-level governance contract
    contract_content = {
        'title': 'Springfield Municipal Governance',
        'purpose': 'Establish democratic governance for Springfield municipality',
        'authority': 'Springfield City Representatives and Citizens',
        'scope': [
            'Municipal budget and finance',
            'Local ordinances and regulations',
            'City planning and zoning',
            'Public services and infrastructure'
        ],
        'provisions': {
            'budget_authority': 'City Council approval required for expenditures over $10,000',
            'citizen_participation': 'Monthly town hall meetings mandatory',
            'transparency': 'All decisions recorded on public blockchain',
            'oversight': 'State-level Elder review for constitutional compliance'
        }
    }
    
    print("\n📝 Creating contract for Springfield, Illinois...")
    success, contract_id = manager.create_contract(
        level=ContractLevel.CITY,
        title='Springfield Municipal Governance Contract',
        content=contract_content,
        jurisdiction='USA/Illinois/Springfield',
        creator_email='mayor@springfield.gov'
    )
    
    if success:
        print(f"\n✅ Contract Created Successfully!")
        print(f"   • Contract ID: {contract_id}")
        print(f"   • Level: City (3)")
        print(f"   • Status: Pending Approval")
        print(f"   • Blockchain: Recorded for transparency")
        
        contract = manager.get_contract(contract_id)
        print(f"\n📋 Hierarchical Compliance:")
        compliance = contract['hierarchical_compliance']
        print(f"   • Compliant: {compliance['compliant']}")
        if not compliance['compliant']:
            print(f"   • Conflicts: {compliance['conflicts']}")
        
        return contract_id
    else:
        print(f"❌ Failed: {contract_id}")
        return None


def demo_amendment_proposal(contract_id):
    """Demonstrate amendment proposal"""
    print_header("STEP 4: Proposing an Amendment")
    
    amendment_manager = AmendmentManager()
    
    amendment_text = """
    Amendment to Springfield Municipal Governance Contract:
    
    Add Section 5: Digital Democracy Initiative
    
    The City of Springfield shall establish a digital democracy platform enabling:
    1. Online citizen voting on local initiatives
    2. Real-time budget transparency dashboard
    3. Direct constituent feedback mechanisms
    4. Blockchain-verified voting records
    
    This amendment enhances citizen participation and government transparency.
    """
    
    print("\n📜 Proposing Amendment...")
    print(amendment_text)
    
    success, amendment_id = amendment_manager.propose_amendment(
        contract_id=contract_id,
        amendment_text=amendment_text,
        proposer_email='councilmember@springfield.gov'
    )
    
    if success:
        print(f"\n✅ Amendment Proposed Successfully!")
        print(f"   • Amendment ID: {amendment_id}")
        
        amendment = amendment_manager.get_amendment(amendment_id)
        
        print(f"\n📊 Impact Analysis:")
        impact = amendment['impact_analysis']
        print(f"   • Scope: {impact['estimated_scope']}")
        print(f"   • Jurisdictions Affected: {', '.join(impact['jurisdictions_affected'])}")
        print(f"   • Citizen Ratification Required: {impact['requires_citizen_ratification']}")
        
        print(f"\n⚖️ Constitutional Compliance:")
        const_check = amendment['constitutional_check']
        print(f"   • Compliant: {const_check['compliant']}")
        if const_check['violations']:
            print(f"   • Violations: {', '.join(const_check['violations'])}")
        
        print(f"\n🔍 Conflict Analysis:")
        conflicts = amendment['conflict_analysis']
        print(f"   • Has Conflicts: {conflicts['has_conflicts']}")
        
        print(f"\n📅 Voting Schedule:")
        schedule = amendment['voting_schedule']
        print(f"   • Public Comment Period: {schedule['public_comment_start'][:10]} to {schedule['public_comment_end'][:10]}")
        print(f"   • Voting Period: {schedule['voting_start'][:10]} to {schedule['voting_end'][:10]}")
        
        print(f"\n✅ Approval Requirements:")
        requirements = amendment['approval_requirements']
        for key, value in requirements.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        return amendment_id
    else:
        print(f"❌ Failed: {amendment_id}")
        return None


def demo_amendment_voting(amendment_id):
    """Demonstrate amendment voting"""
    print_header("STEP 5: Voting on the Amendment")
    
    amendment_manager = AmendmentManager()
    
    # Simulate votes from different city council members
    voters = [
        ('representative1@springfield.gov', VoteOption.APPROVE, 'Strong support for digital democracy'),
        ('representative2@springfield.gov', VoteOption.APPROVE, 'Will improve citizen engagement'),
        ('representative3@springfield.gov', VoteOption.REJECT, 'Concerns about implementation costs'),
        ('senator1@springfield.gov', VoteOption.APPROVE, 'Aligns with state digital governance goals'),
        ('senator2@springfield.gov', VoteOption.ABSTAIN, 'Need more technical details'),
    ]
    
    print("\n🗳️ City Council Voting:")
    
    for voter_email, vote, reasoning in voters:
        success, message = amendment_manager.vote_on_amendment(
            amendment_id=amendment_id,
            voter_email=voter_email,
            vote=vote,
            reasoning=reasoning
        )
        
        if success:
            print(f"   ✅ {voter_email}: {vote.value.upper()} - {reasoning}")
        else:
            print(f"   ❌ {voter_email}: Failed - {message}")
    
    # Show results
    amendment = amendment_manager.get_amendment(amendment_id)
    results = amendment['voting_results']
    
    print(f"\n📊 Current Voting Results:")
    print(f"   • Approve: {results['approve']:.0f} votes")
    print(f"   • Reject: {results['reject']:.0f} votes")
    print(f"   • Abstain: {results['abstain']:.0f} votes")
    
    total_votes = results['approve'] + results['reject'] + results['abstain']
    if total_votes > 0:
        approval_pct = (results['approve'] / total_votes) * 100
        print(f"   • Approval Rate: {approval_pct:.1f}%")


def demo_constitutional_enforcement(contract_id):
    """Demonstrate constitutional enforcement"""
    print_header("STEP 6: Elder Constitutional Review")
    
    enforcement = ConstitutionalEnforcement()
    
    print("\n⚖️ Performing Constitutional Review...")
    
    success, review_data = enforcement.review_constitutional_compliance(
        contract_id=contract_id,
        elder_email='elder@civic.gov'
    )
    
    if success:
        print("\n✅ Constitutional Review Complete")
        
        analysis = review_data['analysis']
        print(f"\n📋 Constitutional Analysis:")
        
        checks = {
            'fundamental_rights_check': 'Fundamental Rights Compliance',
            'separation_of_powers': 'Separation of Powers',
            'checks_and_balances': 'Checks and Balances',
            'minority_protection': 'Minority Protection',
            'due_process': 'Due Process',
            'constitutional_precedent': 'Constitutional Precedent'
        }
        
        for check_key, check_name in checks.items():
            result = analysis[check_key]
            status = "✅ PASS" if result['passes'] else "⚠️ REVIEW NEEDED"
            print(f"   {status} - {check_name}")
            if result['issues']:
                for issue in result['issues'][:2]:  # Show first 2 issues
                    print(f"           • {issue}")
        
        decision = review_data['decision']
        print(f"\n{'✅' if decision['compliant'] else '⚠️'} Overall Constitutional Compliance: {decision['compliant']}")
        
        print(f"\n📝 Precedent Value: {review_data['precedent_value'].upper()}")
        print(f"🔐 Blockchain: Constitutional review permanently recorded")


def main():
    """Run complete demo"""
    print("\n" + "="*70)
    print("  HIERARCHICAL CONTRACT SYSTEM - COMPLETE DEMONSTRATION")
    print("="*70)
    
    print("""
This demo showcases the complete hierarchical contract system:
  • 4-level contract hierarchy with constitutional safeguards
  • Multi-stage amendment proposal workflow
  • Democratic voting with role-based permissions
  • Elder constitutional enforcement
  • Complete blockchain audit trail
    """)
    
    input("\nPress Enter to begin the demonstration...")
    
    # Step 1: Understand hierarchy
    demo_contract_hierarchy()
    input("\nPress Enter to continue...")
    
    # Step 2: Templates
    demo_template_generation()
    input("\nPress Enter to continue...")
    
    # Step 3: Create contract
    contract_id = demo_contract_creation()
    if not contract_id:
        print("Demo cannot continue without contract")
        return
    input("\nPress Enter to continue...")
    
    # Step 4: Propose amendment
    amendment_id = demo_amendment_proposal(contract_id)
    if not amendment_id:
        print("Demo cannot continue without amendment")
        return
    input("\nPress Enter to continue...")
    
    # Step 5: Vote on amendment
    demo_amendment_voting(amendment_id)
    input("\nPress Enter to continue...")
    
    # Step 6: Constitutional review
    demo_constitutional_enforcement(contract_id)
    
    # Summary
    print_header("DEMONSTRATION COMPLETE")
    print("""
✅ All Contract System Features Demonstrated:

1. ✅ Hierarchical contract structure (Master/Country/State/City)
2. ✅ Contract creation with authority validation
3. ✅ Hierarchical compliance checking
4. ✅ Amendment proposal with impact analysis
5. ✅ Constitutional compliance validation
6. ✅ Multi-branch voting system
7. ✅ Elder constitutional review
8. ✅ Blockchain audit trail for transparency

The hierarchical contract system is fully operational and ready for
democratic governance at all levels!
    """)


if __name__ == '__main__':
    main()
