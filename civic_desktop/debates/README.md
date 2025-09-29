# Debates Module - Democratic Discussion Platform

## Purpose
Structured civic debate with constitutional oversight, transparent voting, and democratic discourse facilitation.

## Module Structure
```
debates/
├── backend.py            # Debate logic and data management
├── ui.py                 # Debate UI components and interface
└── debates_db.json       # Debate topics, arguments, and votes storage
```

## AI Implementation Instructions

### 1. Topic Creation Workflow (Constitutional Process)
```python
# Topic Creation with Elder Review
def create_debate_topic(title, description, category, creator_email):
    # Step 1: Validate Creator Permissions
    user = SessionManager.get_current_user()
    if not can_create_topic(user['email']):
        return False, "Only Contract Representatives can create topics"
    
    # Step 2: Constitutional Compliance Check
    constitutional_review = check_constitutional_compliance(title, description)
    if not constitutional_review['compliant']:
        return False, f"Constitutional issue: {constitutional_review['reason']}"
    
    # Step 3: Category Assignment and Jurisdiction
    jurisdiction = determine_jurisdiction(category, creator_location)
    
    # Step 4: Elder Constitutional Review
    if category in ['constitutional', 'federal']:
        elder_approval = request_elder_review(topic_data)
        if not elder_approval['approved']:
            return False, f"Elder review required: {elder_approval['reason']}"
    
    # Step 5: Create and Store Topic
    topic_data = {
        'id': generate_unique_id(),
        'title': title,
        'description': description,
        'category': category,
        'jurisdiction': jurisdiction,
        'creator_email': creator_email,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'constitutional_review': constitutional_review,
        'elder_approval': elder_approval if 'elder_approval' in locals() else None
    }
    
    # Step 6: Blockchain Recording
    Blockchain.add_page(
        action_type="topic_created",
        data=topic_data,
        user_email=creator_email
    )
    
    return True, "Topic created successfully"
```

### 2. Argument Submission System
```python
# Structured Argument Framework
def submit_argument(topic_id, position, argument_text, sources, author_email):
    # Validation
    if not validate_argument_format(argument_text, sources):
        return False, "Argument must meet quality standards"
    
    # Position Validation
    if position not in ['for', 'against', 'neutral']:
        return False, "Invalid position"
    
    # User Permission Check
    user = SessionManager.get_current_user()
    if user['role'] not in ['Contract Citizen', 'Contract Representative', 'Contract Senator']:
        return False, "Insufficient permissions for debate participation"
    
    # Create Argument Record
    argument_data = {
        'id': generate_unique_id(),
        'topic_id': topic_id,
        'position': position,
        'text': argument_text,
        'sources': sources,
        'author_email': author_email,
        'quality_score': 0,
        'votes': {'helpful': 0, 'unhelpful': 0},
        'created_at': datetime.now().isoformat()
    }
    
    # Constitutional Review for Sensitive Topics
    if requires_constitutional_review(topic_id):
        review_result = constitutional_argument_review(argument_data)
        if not review_result['approved']:
            return False, f"Constitutional review failed: {review_result['reason']}"
    
    # Store and Record to Blockchain
    save_argument(argument_data)
    Blockchain.add_page(
        action_type="argument_submitted",
        data=argument_data,
        user_email=author_email
    )
    
    return True, "Argument submitted successfully"
```

### 3. Voting System Implementation
```python
# Two-Tier Voting: Argument Quality + Final Position
def vote_on_argument(argument_id, vote_type, voter_email):
    # Vote Types: 'helpful', 'unhelpful', 'quality_high', 'quality_low'
    
    # Validate Voter Eligibility
    if not can_vote_on_arguments(voter_email):
        return False, "Voting requires Contract Member status or higher"
    
    # Prevent Self-Voting
    argument = load_argument(argument_id)
    if argument['author_email'] == voter_email:
        return False, "Cannot vote on your own argument"
    
    # Record Vote
    vote_data = {
        'argument_id': argument_id,
        'voter_email': voter_email,
        'vote_type': vote_type,
        'timestamp': datetime.now().isoformat()
    }
    
    # Update Argument Scores
    update_argument_quality_score(argument_id, vote_type)
    
    # Blockchain Recording
    Blockchain.add_page(
        action_type="argument_voted",
        data=vote_data,
        user_email=voter_email
    )

def vote_on_topic_position(topic_id, position, voter_email):
    # Final Position Voting: 'for', 'against', 'abstain'
    
    # Eligibility and Constitutional Compliance
    if not eligible_for_final_vote(topic_id, voter_email):
        return False, "Not eligible for final voting on this topic"
    
    # Prevent Double Voting
    if has_already_voted(topic_id, voter_email):
        return False, "You have already voted on this topic"
    
    # Constitutional Safeguards
    constitutional_check = verify_constitutional_voting_rights(topic_id, voter_email)
    if not constitutional_check['valid']:
        return False, f"Constitutional restriction: {constitutional_check['reason']}"
    
    # Record Final Vote
    final_vote_data = {
        'topic_id': topic_id,
        'voter_email': voter_email,
        'position': position,
        'voter_role': SessionManager.get_current_user()['role'],
        'jurisdiction': get_voter_jurisdiction(voter_email),
        'timestamp': datetime.now().isoformat()
    }
    
    # Blockchain Recording
    Blockchain.add_page(
        action_type="topic_voted",
        data=final_vote_data,
        user_email=voter_email
    )
```

### 4. Constitutional Oversight System
```python
# Elder Review and Constitutional Compliance
def elder_constitutional_review(topic_id, reviewer_email):
    # Only Contract Elders can perform constitutional review
    reviewer = load_user(reviewer_email)
    if reviewer['role'] != 'Contract Elder':
        return False, "Only Contract Elders can perform constitutional review"
    
    topic = load_topic(topic_id)
    
    # Constitutional Analysis
    review_data = {
        'topic_id': topic_id,
        'reviewer_email': reviewer_email,
        'constitutional_analysis': {
            'compliant': True,  # Default, analyze against governance contracts
            'issues': [],
            'recommendations': []
        },
        'decision': 'approved',  # 'approved', 'rejected', 'needs_modification'
        'reasoning': '',
        'timestamp': datetime.now().isoformat()
    }
    
    # Apply Constitutional Tests
    if violates_citizen_rights(topic):
        review_data['constitutional_analysis']['compliant'] = False
        review_data['constitutional_analysis']['issues'].append('Violates fundamental citizen rights')
    
    if exceeds_jurisdiction_authority(topic):
        review_data['constitutional_analysis']['compliant'] = False
        review_data['constitutional_analysis']['issues'].append('Exceeds jurisdictional authority')
    
    # Record Elder Review
    Blockchain.add_page(
        action_type="elder_review",
        data=review_data,
        user_email=reviewer_email
    )
    
    return review_data
```

### 5. Topic Categories and Jurisdictions
```python
# Hierarchical Topic Organization
TOPIC_CATEGORIES = {
    'local': {
        'jurisdiction': 'city',
        'required_approvals': ['Contract Representatives'],
        'elder_review': False
    },
    'state': {
        'jurisdiction': 'state',
        'required_approvals': ['Contract Representatives', 'Contract Senators'],
        'elder_review': True
    },
    'federal': {
        'jurisdiction': 'country',
        'required_approvals': ['Contract Representatives', 'Contract Senators'],
        'elder_review': True
    },
    'constitutional': {
        'jurisdiction': 'platform',
        'required_approvals': ['Contract Representatives', 'Contract Senators', 'Contract Elders'],
        'elder_review': True,
        'supermajority_required': True
    }
}

def determine_topic_jurisdiction(category, creator_location):
    # Match topic category to appropriate governance level
    # Ensure creator has authority in jurisdiction
    # Apply constitutional requirements
    pass
```

## UI/UX Requirements

### Topic Browser Interface
- **Filter System**: Category, jurisdiction, participation status
- **Search Functionality**: Full-text search with relevance ranking
- **Visual Indicators**: User participation, constitutional status
- **Trending Topics**: Popular and urgent discussions highlighted

### Debate Participation Interface
- **Threaded Arguments**: Clear organization by position (For/Against/Neutral)
- **Quality Indicators**: Community-driven quality scores and helpfulness
- **Source Integration**: Easy citation and reference management
- **Constitutional Context**: Display relevant constitutional provisions

### Voting Interfaces
- **Argument Quality Voting**: Simple helpful/unhelpful with quality metrics
- **Final Position Voting**: Clear ballot interface with constitutional safeguards
- **Vote Verification**: Transparent vote counting and blockchain verification
- **Results Display**: Real-time results with demographic breakdowns

## Blockchain Data Requirements
ALL debate activities must be recorded with these action types:
- `topic_created`: Full topic data, creator, constitutional review status
- `argument_submitted`: Argument text, author, position, references
- `argument_voted`: Vote details, voter role, quality rating
- `topic_voted`: Final position votes, voter eligibility verification
- `elder_review`: Constitutional review decisions and reasoning

## Database Schema
```json
{
  "topics": [
    {
      "id": "string",
      "title": "string",
      "description": "string", 
      "category": "local|state|federal|constitutional",
      "jurisdiction": "string",
      "creator_email": "string",
      "status": "active|closed|under_review",
      "created_at": "ISO timestamp",
      "arguments": ["argument_id"],
      "votes": {
        "for": 0,
        "against": 0, 
        "abstain": 0
      },
      "constitutional_review": "object"
    }
  ],
  "arguments": [
    {
      "id": "string",
      "topic_id": "string",
      "position": "for|against|neutral",
      "text": "string",
      "sources": ["array of citations"],
      "author_email": "string",
      "quality_score": "number",
      "votes": {"helpful": 0, "unhelpful": 0},
      "created_at": "ISO timestamp"
    }
  ]
}
```

## Integration Points
- **Users Module**: Authentication, role checking, permissions
- **Moderation Module**: Content flagging, constitutional review
- **Contracts Module**: Constitutional compliance, governance rules
- **Blockchain Module**: Immutable audit trail for all actions

## Testing Requirements
- Topic creation workflow validation
- Constitutional compliance checking
- Voting system integrity
- Elder review process accuracy
- Permission enforcement testing
- Blockchain integration verification