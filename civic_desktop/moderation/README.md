# Moderation Module - Constitutional Content Review

## Purpose
Community-driven content moderation with constitutional appeals, due process protection, and multi-branch oversight system.

## Module Structure
```
moderation/
├── backend.py            # Moderation logic and workflows
├── ui.py                 # Moderation dashboard UI
└── moderation_db.json    # Flags, reviews, appeals, and decisions
```

## AI Implementation Instructions

### 1. Content Flagging System
```python
# Universal Content Flagging (Any Citizen Can Flag)
def flag_content(content_type, content_id, reason, severity, reporter_email, details=None):
    # Content Types: 'argument', 'topic', 'comment', 'user_profile'
    # Severity: 'low', 'medium', 'high', 'critical', 'constitutional'
    
    # Validate Reporter
    if not SessionManager.is_authenticated():
        return False, "Must be logged in to flag content"
    
    reporter = SessionManager.get_current_user()
    if reporter['role'] not in ['Contract Citizen', 'Contract Representative', 'Contract Senator', 'Contract Elder']:
        return False, "Insufficient permissions to flag content"
    
    # Flag Categories and Validation
    VALID_FLAG_REASONS = {
        'spam': 'Unsolicited or repetitive content',
        'harassment': 'Personal attacks or intimidation',
        'constitutional_violation': 'Violates platform governance principles',
        'misinformation': 'False or misleading information',
        'inappropriate': 'Violates community standards',
        'off_topic': 'Not relevant to civic discussion'
    }
    
    if reason not in VALID_FLAG_REASONS:
        return False, f"Invalid flag reason. Must be one of: {list(VALID_FLAG_REASONS.keys())}"
    
    # Create Flag Record
    flag_data = {
        'id': generate_unique_id(),
        'content_type': content_type,
        'content_id': content_id,
        'reason': reason,
        'severity': severity,
        'reporter_email': reporter_email,
        'details': details,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'jurisdiction': determine_flag_jurisdiction(content_id),
        'assigned_moderators': []
    }
    
    # Automatic Assignment Based on Severity and Jurisdiction
    flag_data['assigned_moderators'] = assign_moderators(flag_data)
    
    # Constitutional Flag Special Handling
    if reason == 'constitutional_violation' or severity == 'constitutional':
        flag_data['requires_elder_review'] = True
        notify_elders_of_constitutional_flag(flag_data)
    
    # Store and Record
    save_flag(flag_data)
    Blockchain.add_page(
        action_type="content_flagged",
        data=flag_data,
        user_email=reporter_email
    )
    
    return True, "Content flagged for review"
```

### 2. Bicameral Moderation Review Process
```python
# Multi-Branch Review System
def review_flagged_content(flag_id, reviewer_email, decision, reasoning):
    # Load Flag and Validate Reviewer
    flag = load_flag(flag_id)
    reviewer = load_user(reviewer_email)
    
    # Permission Validation
    if not can_moderate_content(reviewer_email, flag):
        return False, "Insufficient moderation permissions for this content"
    
    # Reviewer Role Requirements
    MODERATION_PERMISSIONS = {
        'Contract Representative': ['local', 'state'],
        'Contract Senator': ['state', 'federal'],
        'Contract Elder': ['constitutional', 'appeals'],
        'Contract Founder': ['emergency', 'all']
    }
    
    if flag['jurisdiction'] not in MODERATION_PERMISSIONS.get(reviewer['role'], []):
        return False, f"Cannot moderate {flag['jurisdiction']} content with {reviewer['role']} role"
    
    # Decision Types
    VALID_DECISIONS = ['dismiss', 'warning', 'temporary_restriction', 'permanent_ban', 'constitutional_review']
    if decision not in VALID_DECISIONS:
        return False, f"Invalid decision. Must be one of: {VALID_DECISIONS}"
    
    # Create Review Record
    review_data = {
        'flag_id': flag_id,
        'reviewer_email': reviewer_email,
        'reviewer_role': reviewer['role'],
        'decision': decision,
        'reasoning': reasoning,
        'evidence_collected': [],
        'timestamp': datetime.now().isoformat(),
        'requires_second_review': False
    }
    
    # Bicameral Review Requirements
    if flag['severity'] in ['high', 'critical', 'constitutional']:
        review_data['requires_second_review'] = True
        request_second_reviewer(flag, review_data)
    
    # Constitutional Review Trigger
    if decision == 'constitutional_review' or flag.get('requires_elder_review'):
        escalate_to_elder_review(flag, review_data)
    
    # Update Flag Status
    update_flag_status(flag_id, review_data)
    
    # Blockchain Recording
    Blockchain.add_page(
        action_type="moderation_review",
        data=review_data,
        user_email=reviewer_email
    )
    
    return True, "Review completed successfully"
```

### 3. Constitutional Appeals Process
```python
# Due Process Protection System
def submit_appeal(original_decision_id, appellant_email, grounds, evidence, constitutional_claim=None):
    # Load Original Decision
    decision = load_moderation_decision(original_decision_id)
    if not decision:
        return False, "Original decision not found"
    
    # Validate Appellant (Must be affected party or have standing)
    if not has_appeal_standing(appellant_email, decision):
        return False, "No legal standing to appeal this decision"
    
    # Appeal Grounds Validation
    VALID_APPEAL_GROUNDS = [
        'procedural_error',
        'insufficient_evidence', 
        'constitutional_violation',
        'bias_or_conflict',
        'disproportionate_penalty',
        'new_evidence'
    ]
    
    if grounds not in VALID_APPEAL_GROUNDS:
        return False, f"Invalid appeal grounds. Must be one of: {VALID_APPEAL_GROUNDS}"
    
    # Constitutional Claims Special Handling
    if constitutional_claim:
        if not validate_constitutional_claim(constitutional_claim):
            return False, "Invalid constitutional claim format"
    
    # Create Appeal Record
    appeal_data = {
        'id': generate_unique_id(),
        'original_decision_id': original_decision_id,
        'appellant_email': appellant_email,
        'grounds': grounds,
        'evidence': evidence,
        'constitutional_claim': constitutional_claim,
        'status': 'submitted',
        'created_at': datetime.now().isoformat(),
        'assigned_reviewers': [],
        'timeline': calculate_appeal_timeline()
    }
    
    # Assign Appeal Reviewers (Higher Authority Required)
    if grounds == 'constitutional_violation' or constitutional_claim:
        appeal_data['assigned_reviewers'] = assign_elder_reviewers(appeal_data)
        appeal_data['priority'] = 'constitutional'
    else:
        appeal_data['assigned_reviewers'] = assign_appeal_reviewers(appeal_data)
    
    # Store and Record
    save_appeal(appeal_data)
    Blockchain.add_page(
        action_type="appeal_submitted",
        data=appeal_data,
        user_email=appellant_email
    )
    
    # Notify Assigned Reviewers
    notify_appeal_reviewers(appeal_data)
    
    return True, "Appeal submitted successfully"
```

### 4. Elder Constitutional Review
```python
# Constitutional Interpretation and Final Authority
def elder_constitutional_review(appeal_id, elder_email, interpretation, decision, precedent_value=None):
    # Validate Elder Authority
    elder = load_user(elder_email)
    if elder['role'] != 'Contract Elder':
        return False, "Only Contract Elders can perform constitutional review"
    
    # Load Appeal Context
    appeal = load_appeal(appeal_id)
    if not appeal.get('constitutional_claim') and appeal.get('priority') != 'constitutional':
        return False, "Constitutional review only available for constitutional claims"
    
    # Constitutional Analysis Framework
    constitutional_analysis = {
        'claim_evaluated': appeal.get('constitutional_claim'),
        'constitutional_provisions': identify_relevant_provisions(appeal),
        'precedent_review': analyze_existing_precedents(appeal),
        'interpretation': interpretation,
        'decision_rationale': decision.get('reasoning'),
        'future_guidance': decision.get('guidance', '')
    }
    
    # Decision Types for Constitutional Review
    CONSTITUTIONAL_DECISIONS = [
        'uphold_original',      # Original decision was constitutional
        'overturn_violation',   # Original decision violated constitution
        'modify_penalty',       # Penalty adjustment required
        'establish_precedent',  # Set new constitutional precedent
        'remand_for_review'    # Send back for proper process
    ]
    
    if decision['type'] not in CONSTITUTIONAL_DECISIONS:
        return False, f"Invalid constitutional decision type"
    
    # Create Constitutional Review Record
    review_data = {
        'appeal_id': appeal_id,
        'elder_email': elder_email,
        'constitutional_analysis': constitutional_analysis,
        'decision': decision,
        'precedent_value': precedent_value,
        'binding_authority': True,  # Elder decisions are binding
        'timestamp': datetime.now().isoformat()
    }
    
    # Precedent Management
    if precedent_value and decision['type'] == 'establish_precedent':
        create_constitutional_precedent(review_data)
    
    # Final Resolution
    resolve_appeal(appeal_id, review_data)
    notify_all_parties(appeal_id, review_data)
    
    # Blockchain Recording (Constitutional Decisions)
    Blockchain.add_page(
        action_type="constitutional_review",
        data=review_data,
        user_email=elder_email
    )
    
    return True, "Constitutional review completed"
```

### 5. Moderation Workflow Management
```python
# Comprehensive Workflow Orchestration
def process_moderation_queue():
    # Load Pending Items by Priority
    flags = load_pending_flags()
    appeals = load_pending_appeals()
    
    # Priority Order: Constitutional > Critical > High > Medium > Low
    priority_order = sort_by_priority(flags + appeals)
    
    for item in priority_order:
        # Auto-assignment based on complexity and jurisdiction
        if item['type'] == 'flag':
            assign_flag_reviewers(item)
        elif item['type'] == 'appeal':
            assign_appeal_reviewers(item)
        
        # Timeline Management
        update_review_timeline(item)
        
        # Escalation Triggers
        if is_overdue(item):
            escalate_moderation_item(item)

def assign_moderators(flag_data):
    # Geographic and Role-Based Assignment
    moderators = []
    
    # Jurisdiction Matching
    if flag_data['jurisdiction'] == 'local':
        moderators = find_local_representatives(flag_data['location'])
    elif flag_data['jurisdiction'] == 'state':
        moderators = find_state_senators(flag_data['location'])
    elif flag_data['jurisdiction'] == 'federal':
        moderators = find_federal_authorities()
    elif flag_data['jurisdiction'] == 'constitutional':
        moderators = find_available_elders()
    
    # Workload Balancing
    return balance_moderator_workload(moderators)
```

## UI/UX Requirements

### Flagging Interface
- **One-Click Flagging**: Prominent flag button on all content
- **Guided Categories**: Clear flag reasons with descriptions
- **Severity Selection**: Visual severity indicators with explanations
- **Evidence Upload**: Support for screenshots and documentation

### Moderation Dashboard
- **Queue Management**: Organized by priority, age, jurisdiction
- **Case Details**: Complete context and history view
- **Evidence Collection**: Tools for gathering and organizing evidence
- **Decision Interface**: Clear decision options with reasoning fields

### Appeals Interface  
- **Appeal Submission**: Step-by-step appeal filing process
- **Status Tracking**: Real-time updates on appeal progress
- **Document Upload**: Evidence and legal brief submission
- **Timeline Display**: Clear deadlines and process steps

## Blockchain Data Requirements
ALL moderation activities recorded with these action types:
- `content_flagged`: Flag details, reporter, content reference, severity
- `moderation_review`: Reviewer actions, evidence, decision rationale  
- `appeal_submitted`: Appeal details, evidence, constitutional claims
- `constitutional_review`: Elder decisions, constitutional interpretation
- `resolution_final`: Final decision, enforcement actions, precedent value

## Database Schema
```json
{
  "flags": [
    {
      "id": "string",
      "content_type": "string",
      "content_id": "string", 
      "reason": "string",
      "severity": "low|medium|high|critical|constitutional",
      "reporter_email": "string",
      "status": "pending|under_review|resolved|appealed",
      "jurisdiction": "string",
      "assigned_moderators": ["array"],
      "created_at": "ISO timestamp"
    }
  ],
  "reviews": [
    {
      "flag_id": "string",
      "reviewer_email": "string",
      "decision": "string",
      "reasoning": "string",
      "evidence": ["array"],
      "timestamp": "ISO timestamp"
    }
  ],
  "appeals": [
    {
      "id": "string",
      "original_decision_id": "string",
      "appellant_email": "string",
      "grounds": "string",
      "constitutional_claim": "string",
      "status": "submitted|under_review|decided",
      "timeline": "object"
    }
  ]
}
```

## Integration Points
- **Users Module**: Authentication, role verification, permissions
- **Debates Module**: Content flagging, topic moderation
- **Contracts Module**: Constitutional compliance, governance rules
- **Blockchain Module**: Immutable audit trail for transparency

## Testing Requirements
- Flag submission and assignment workflow
- Bicameral review process validation
- Constitutional appeals process accuracy
- Elder authority and precedent system
- Due process timeline compliance
- Blockchain audit trail completeness