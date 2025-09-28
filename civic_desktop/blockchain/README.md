# Blockchain Module - Immutable Audit & Consensus System

## Purpose
Transparent audit trail with hierarchical structure, validator consensus, and immutable record-keeping for all platform governance activities.

## Module Structure
```
blockchain/
├── blockchain.py         # Core blockchain logic and hierarchical structure
├── signatures.py         # RSA signing and verification
├── p2p.py               # Peer-to-peer networking foundation
├── blockchain_tab.py    # Blockchain UI dashboard
├── blockchain_timer.py  # Automated block creation
├── blockchain_db.json   # Blockchain data storage
├── validators_db.json   # Validator registry and management
└── genesis_block.json   # Genesis block data
```

## AI Implementation Instructions

### 1. Hierarchical Blockchain Structure
```python
# Five-Level Hierarchical System
BLOCKCHAIN_HIERARCHY = {
    'Page': {
        'contains': 'Individual user actions and transactions',
        'rollup_time': 'Real-time',
        'capacity': 'Unlimited individual actions',
        'parent': None
    },
    'Chapter': {
        'contains': 'Collection of Pages (24-hour period)',
        'rollup_time': 'Daily at midnight',
        'capacity': 'All Pages from previous 24 hours',
        'parent': 'Book'
    },
    'Book': {
        'contains': 'Collection of Chapters (monthly period)',
        'rollup_time': 'First day of each month',
        'capacity': 'All Chapters from previous month',
        'parent': 'Part'
    },
    'Part': {
        'contains': 'Collection of Books (yearly period)',
        'rollup_time': 'January 1st each year',
        'capacity': 'All Books from previous year',
        'parent': 'Series'
    },
    'Series': {
        'contains': 'Collection of Parts (10-year period)',
        'rollup_time': 'Every 10 years',
        'capacity': 'All Parts from previous decade',
        'parent': None
    }
}

class BlockchainHierarchy:
    def add_page(self, action_type, data, user_email):
        """Record individual user action as new Page"""
        page_data = {
            'id': generate_unique_id(),
            'action_type': action_type,
            'data': data,
            'user_email': user_email,
            'timestamp': datetime.now().isoformat(),
            'signature': None,
            'validator_signatures': []
        }
        
        # Cryptographic Signing
        page_data['signature'] = self.sign_page(page_data, user_email)
        
        # Validator Consensus
        validator_signatures = self.collect_validator_signatures(page_data)
        page_data['validator_signatures'] = validator_signatures
        
        # Store Page
        self.store_page(page_data)
        
        # Trigger Rollup Checks
        self.check_rollup_triggers()
        
        return page_data['id']
    
    def rollup_to_chapter(self):
        """Daily rollup: Combine all Pages from last 24 hours into Chapter"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        pages = self.get_pages_since(cutoff_time)
        
        chapter_data = {
            'id': generate_unique_id(),
            'type': 'chapter',
            'pages': [page['id'] for page in pages],
            'summary': self.generate_page_summary(pages),
            'created_at': datetime.now().isoformat(),
            'signature': None
        }
        
        # Chapter Signature by Validator Consensus
        chapter_data['signature'] = self.sign_chapter(chapter_data)
        
        # Archive Pages and Store Chapter
        self.archive_pages(pages)
        self.store_chapter(chapter_data)
        
        return chapter_data['id']
```

### 2. Proof of Authority (PoA) Consensus
```python
# Validator Management System
class ValidatorManager:
    def __init__(self):
        self.validators = self.load_validators()
    
    def register_validator(self, user_email, public_key):
        """Register elected representative as validator"""
        user = load_user(user_email)
        
        # Only elected representatives can be validators
        if user['role'] not in ['Contract Representative', 'Contract Senator']:
            return False, "Only elected representatives can become validators"
        
        # Check election status
        if not user.get('elected_status', {}).get('active'):
            return False, "Must be currently elected to serve as validator"
        
        validator_data = {
            'user_email': user_email,
            'public_key': public_key,
            'role': user['role'],
            'jurisdiction': user['jurisdiction'],
            'registered_at': datetime.now().isoformat(),
            'status': 'active',
            'blocks_signed': 0,
            'reputation_score': 100
        }
        
        self.validators[user_email] = validator_data
        self.save_validators()
        
        # Record validator registration
        Blockchain.add_page(
            action_type="validator_registered",
            data=validator_data,
            user_email=user_email
        )
        
        return True, "Validator registered successfully"
    
    def collect_signatures(self, block_data):
        """Collect validator signatures for new block"""
        signatures = []
        required_signatures = self.calculate_required_signatures()
        
        for validator_email, validator in self.validators.items():
            if validator['status'] != 'active':
                continue
            
            # Auto-signing with override capability
            if validator.get('auto_sign', True):
                signature = self.create_validator_signature(block_data, validator)
                signatures.append(signature)
            
            # Stop when we have enough signatures
            if len(signatures) >= required_signatures:
                break
        
        return signatures
    
    def calculate_required_signatures(self):
        """Require majority of active validators"""
        active_validators = len([v for v in self.validators.values() if v['status'] == 'active'])
        return (active_validators // 2) + 1
```

### 3. Cryptographic Security Implementation
```python
# RSA Signature System
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class CryptographicSecurity:
    def sign_block(self, block_data, private_key):
        """Create cryptographic signature for block integrity"""
        # Convert block data to canonical format
        canonical_data = self.canonicalize_block_data(block_data)
        
        # Create signature
        signature = private_key.sign(
            canonical_data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, block_data, signature, public_key):
        """Verify block signature integrity"""
        try:
            canonical_data = self.canonicalize_block_data(block_data)
            signature_bytes = base64.b64decode(signature)
            
            public_key.verify(
                signature_bytes,
                canonical_data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def verify_chain_integrity(self):
        """Verify entire blockchain integrity"""
        issues = []
        
        # Verify all blocks in sequence
        for block in self.load_all_blocks():
            # Check block signature
            if not self.verify_block_signature(block):
                issues.append(f"Invalid signature for block {block['id']}")
            
            # Check validator consensus
            if not self.verify_validator_consensus(block):
                issues.append(f"Insufficient validator consensus for block {block['id']}")
            
            # Check chronological order
            if not self.verify_chronological_order(block):
                issues.append(f"Chronological order violation in block {block['id']}")
        
        return len(issues) == 0, issues
```

### 4. Blockchain Explorer Interface
```python
# Transparent Audit Trail Browser
class BlockchainExplorer:
    def search_by_user(self, user_email, start_date=None, end_date=None):
        """Find all actions by specific user"""
        user_actions = []
        
        # Search across all hierarchy levels
        pages = self.search_pages(user_email=user_email, start_date=start_date, end_date=end_date)
        
        for page in pages:
            action_summary = {
                'action_type': page['action_type'],
                'timestamp': page['timestamp'],
                'data_summary': self.summarize_action_data(page['data']),
                'block_id': page['id'],
                'verification_status': self.verify_page_integrity(page)
            }
            user_actions.append(action_summary)
        
        return sorted(user_actions, key=lambda x: x['timestamp'], reverse=True)
    
    def search_by_action_type(self, action_type, limit=100):
        """Search for specific types of actions"""
        matching_actions = []
        
        # Search recent Pages first
        recent_pages = self.get_recent_pages(limit=limit * 2)  # Get more to filter
        
        for page in recent_pages:
            if page['action_type'] == action_type:
                matching_actions.append({
                    'user_email': page['user_email'],
                    'timestamp': page['timestamp'],
                    'data': page['data'],
                    'block_id': page['id']
                })
            
            if len(matching_actions) >= limit:
                break
        
        return matching_actions
    
    def get_governance_timeline(self, jurisdiction=None):
        """Get chronological governance activity"""
        governance_actions = [
            'user_registration', 'role_assignment', 'topic_created', 
            'argument_submitted', 'topic_voted', 'moderation_review',
            'constitutional_review', 'contract_amended'
        ]
        
        timeline = []
        for action_type in governance_actions:
            actions = self.search_by_action_type(action_type, limit=50)
            
            # Filter by jurisdiction if specified
            if jurisdiction:
                actions = [a for a in actions if self.matches_jurisdiction(a, jurisdiction)]
            
            timeline.extend(actions)
        
        return sorted(timeline, key=lambda x: x['timestamp'], reverse=True)
```

### 5. P2P Networking Foundation
```python
# Peer-to-Peer Network for Future Decentralization
class P2PNetwork:
    def __init__(self, port=8333):
        self.port = port
        self.peers = []
        self.local_blockchain = None
    
    def start_node(self):
        """Start P2P node for blockchain synchronization"""
        # Initialize Flask server for P2P communication
        self.app = Flask(__name__)
        self.setup_p2p_endpoints()
        
        # Start peer discovery
        self.discover_peers()
        
        # Begin blockchain synchronization
        self.sync_blockchain()
    
    def setup_p2p_endpoints(self):
        """Setup REST endpoints for P2P communication"""
        @self.app.route('/blockchain/latest', methods=['GET'])
        def get_latest_blocks():
            latest_blocks = self.local_blockchain.get_latest_blocks(100)
            return jsonify(latest_blocks)
        
        @self.app.route('/blockchain/sync', methods=['POST'])
        def sync_blockchain():
            peer_blocks = request.json.get('blocks', [])
            sync_result = self.synchronize_with_peer(peer_blocks)
            return jsonify(sync_result)
        
        @self.app.route('/validators/status', methods=['GET'])
        def validator_status():
            validator_info = self.get_validator_status()
            return jsonify(validator_info)
    
    def synchronize_with_peer(self, peer_blocks):
        """Synchronize blockchain with peer node"""
        local_blocks = self.local_blockchain.get_all_blocks()
        
        # Identify missing or conflicting blocks
        missing_blocks = self.identify_missing_blocks(local_blocks, peer_blocks)
        conflicts = self.identify_conflicts(local_blocks, peer_blocks)
        
        # Resolve conflicts using validator consensus
        for conflict in conflicts:
            resolution = self.resolve_blockchain_conflict(conflict)
            self.apply_conflict_resolution(resolution)
        
        # Add missing blocks after validation
        for block in missing_blocks:
            if self.validate_block(block):
                self.local_blockchain.add_block(block)
        
        return {'synchronized': True, 'blocks_added': len(missing_blocks)}
```

## UI/UX Requirements

### Blockchain Explorer Interface
- **Recent Activity Feed**: Real-time display of platform actions
- **Search Functionality**: Search by user, action type, date range
- **Hierarchical Visualization**: Show Pages → Chapters → Books → Parts → Series
- **Verification Status**: Display cryptographic verification results

### Validator Dashboard
- **Validator Status**: Active/inactive, performance metrics
- **Auto-Signing Controls**: Enable/disable automatic block signing
- **Network Health**: Peer connections, consensus status
- **Block Creation**: Manual block creation and validation tools

## Blockchain Data Schema
```json
{
  "pages": [
    {
      "id": "string",
      "action_type": "string",
      "data": "object",
      "user_email": "string", 
      "timestamp": "ISO timestamp",
      "signature": "base64 encoded signature",
      "validator_signatures": ["array of signatures"]
    }
  ],
  "chapters": [
    {
      "id": "string",
      "type": "chapter",
      "pages": ["array of page IDs"],
      "summary": "object",
      "created_at": "ISO timestamp",
      "signature": "string"
    }
  ]
}
```

## Integration Points
- **All Modules**: Every action recorded via `Blockchain.add_page()`
- **Users Module**: Validator registration for elected representatives
- **Security**: Cryptographic integrity for all governance actions
- **Transparency**: Public audit trail for democratic accountability

## Testing Requirements
- Hierarchical rollup process validation
- Cryptographic signature verification
- Validator consensus mechanism testing
- P2P synchronization accuracy
- Blockchain integrity verification
- Performance testing for large datasets