"""
BLOCKCHAIN CORE - Hierarchical blockchain for civic governance transparency
Implements Pages -> Chapters -> Books -> Parts -> Series structure with PoA consensus
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import uuid
import os
from dataclasses import dataclass, asdict

# Import RSA signing capability
try:
    from users.keys import RSAKeyManager
    CRYPTO_AVAILABLE = True
except ImportError:
    print("Warning: RSA key management not available")
    CRYPTO_AVAILABLE = False

@dataclass
class BlockchainPage:
    """Individual page entry - smallest blockchain unit"""
    page_id: str
    timestamp: str
    action_type: str
    user_email: str
    data: Dict[str, Any]
    signature: Optional[str] = None
    validator: Optional[str] = None
    block_hash: Optional[str] = None
    previous_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of page content"""
        content = f"{self.page_id}{self.timestamp}{self.action_type}{self.user_email}{json.dumps(self.data, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

@dataclass
class BlockchainChapter:
    """Chapter containing multiple pages - 24-hour rollup"""
    chapter_id: str
    start_time: str
    end_time: str
    pages: List[BlockchainPage]
    chapter_hash: str
    validator_signatures: List[Dict[str, str]]
    page_count: int
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'chapter_id': self.chapter_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'pages': [page.to_dict() for page in self.pages],
            'chapter_hash': self.chapter_hash,
            'validator_signatures': self.validator_signatures,
            'page_count': self.page_count,
            'summary': self.summary
        }

class CivicBlockchain:
    """Main blockchain class for civic governance transparency"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize blockchain with configuration"""
        
        # Set up paths
        self.base_path = Path(config_path) if config_path else Path(__file__).parent
        self.data_path = self.base_path / 'data'
        self.data_path.mkdir(exist_ok=True)
        
        # Database files
        self.blockchain_db = self.data_path / 'blockchain_db.json'
        self.validators_db = self.data_path / 'validators_db.json'
        self.genesis_block = self.data_path / 'genesis_block.json'
        self.pages_db = self.data_path / 'active_pages.json'
        
        # Initialize RSA key manager if available
        self.key_manager = RSAKeyManager() if CRYPTO_AVAILABLE else None
        
        # Load or create blockchain
        self._initialize_blockchain()
        
        # Validator management
        self.validators = self._load_validators()
        
        print(f"✅ Civic Blockchain initialized at {self.base_path}")
    
    def _initialize_blockchain(self):
        """Initialize blockchain with genesis block if needed"""
        
        if not self.genesis_block.exists():
            self._create_genesis_block()
        
        if not self.blockchain_db.exists():
            initial_data = {
                'series': [],
                'parts': [],
                'books': [],
                'chapters': [],
                'last_updated': datetime.now().isoformat(),
                'total_pages': 0,
                'network_info': {
                    'consensus_type': 'proof_of_authority',
                    'min_validators': 3,
                    'block_time_target': 300,  # 5 minutes
                    'chapter_rollup_hours': 24
                }
            }
            self._save_blockchain_data(initial_data)
        
        if not self.pages_db.exists():
            self._save_pages_data({'active_pages': [], 'pending_pages': []})
    
    def _create_genesis_block(self):
        """Create the foundational genesis block"""
        
        genesis_data = {
            'block_id': 'genesis_000000',
            'timestamp': '2025-01-01T00:00:00.000000',
            'type': 'genesis',
            'title': 'Civic Engagement Platform Genesis Block',
            'description': 'Foundational block establishing transparent democratic governance',
            'constitutional_principles': [
                'Democratic participation for all citizens',
                'Transparent governance through blockchain',
                'Constitutional protection of minority rights',
                'Checks and balances preventing tyranny',
                'Due process and appeal rights'
            ],
            'governance_framework': {
                'roles': ['contract_citizen', 'contract_representative', 'contract_senator', 'contract_elder', 'contract_founder'],
                'consensus_mechanism': 'proof_of_authority',
                'amendment_process': 'bicameral_plus_elder_review',
                'appeal_system': 'constitutional_review'
            },
            'hash': hashlib.sha256('civic_governance_genesis_2025'.encode()).hexdigest(),
            'version': '1.0.0'
        }
        
        with open(self.genesis_block, 'w') as f:
            json.dump(genesis_data, f, indent=2)
        
        print("🏛️ Genesis block created with constitutional framework")
    
    def _load_blockchain_data(self) -> Dict[str, Any]:
        """Load blockchain data from storage"""
        try:
            with open(self.blockchain_db, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'series': [], 'parts': [], 'books': [], 'chapters': [], 'total_pages': 0}
    
    def _save_blockchain_data(self, data: Dict[str, Any]):
        """Save blockchain data to storage"""
        data['last_updated'] = datetime.now().isoformat()
        with open(self.blockchain_db, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_pages_data(self) -> Dict[str, Any]:
        """Load active pages from storage"""
        try:
            with open(self.pages_db, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'active_pages': [], 'pending_pages': []}
    
    def _save_pages_data(self, data: Dict[str, Any]):
        """Save pages data to storage"""
        with open(self.pages_db, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_validators(self) -> List[Dict[str, Any]]:
        """Load validator registry"""
        try:
            with open(self.validators_db, 'r') as f:
                data = json.load(f)
                return data.get('validators', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_validators(self, validators: List[Dict[str, Any]]):
        """Save validator registry"""
        data = {
            'validators': validators,
            'last_updated': datetime.now().isoformat(),
            'total_validators': len(validators)
        }
        with open(self.validators_db, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_page(self, action_type: str, user_email: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Add a new page to the blockchain"""
        
        try:
            # Create page
            page_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Get previous hash for linking
            pages_data = self._load_pages_data()
            previous_hash = None
            if pages_data['active_pages']:
                previous_hash = pages_data['active_pages'][-1].get('block_hash')
            
            # Create page object
            page = BlockchainPage(
                page_id=page_id,
                timestamp=timestamp,
                action_type=action_type,
                user_email=user_email,
                data=data,
                previous_hash=previous_hash
            )
            
            # Calculate hash
            page.block_hash = page.calculate_hash()
            
            # Sign page if crypto available
            if self.key_manager and CRYPTO_AVAILABLE:
                # Extract user ID from email for key lookup
                user_id = data.get('user_id', user_email.split('@')[0])
                sign_success, sign_message, signature = self.key_manager.sign_message(
                    user_id, 
                    page.block_hash
                )
                if sign_success:
                    page.signature = signature
            
            # Add to active pages
            pages_data['active_pages'].append(page.to_dict())
            
            # Update blockchain totals
            blockchain_data = self._load_blockchain_data()
            blockchain_data['total_pages'] += 1
            
            # Save updates
            self._save_pages_data(pages_data)
            self._save_blockchain_data(blockchain_data)
            
            # Check if chapter rollup needed (every 100 pages or 24 hours)
            if len(pages_data['active_pages']) >= 100 or self._should_create_chapter():
                self._create_chapter_rollup()
            
            print(f"📄 Page added to blockchain: {action_type} by {user_email}")
            return True, "Page added successfully to blockchain", page_id
            
        except Exception as e:
            print(f"❌ Error adding page to blockchain: {e}")
            return False, f"Failed to add page: {str(e)}", None
    
    def _should_create_chapter(self) -> bool:
        """Check if it's time to create a new chapter"""
        pages_data = self._load_pages_data()
        
        if not pages_data['active_pages']:
            return False
        
        # Check if 24 hours have passed since first page
        first_page_time = datetime.fromisoformat(pages_data['active_pages'][0]['timestamp'])
        time_diff = datetime.now() - first_page_time
        
        return time_diff >= timedelta(hours=24)
    
    def _create_chapter_rollup(self):
        """Create chapter from active pages"""
        
        pages_data = self._load_pages_data()
        
        if not pages_data['active_pages']:
            return
        
        # Create chapter
        chapter_id = f"chapter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = pages_data['active_pages'][0]['timestamp']
        end_time = pages_data['active_pages'][-1]['timestamp']
        
        # Convert page dicts back to objects
        pages = []
        for page_dict in pages_data['active_pages']:
            page = BlockchainPage(**page_dict)
            pages.append(page)
        
        # Generate chapter summary
        summary = self._generate_chapter_summary(pages)
        
        # Calculate chapter hash
        chapter_content = f"{chapter_id}{start_time}{end_time}{len(pages)}"
        chapter_hash = hashlib.sha256(chapter_content.encode()).hexdigest()
        
        # Create chapter
        chapter = BlockchainChapter(
            chapter_id=chapter_id,
            start_time=start_time,
            end_time=end_time,
            pages=pages,
            chapter_hash=chapter_hash,
            validator_signatures=[],
            page_count=len(pages),
            summary=summary
        )
        
        # Add to blockchain
        blockchain_data = self._load_blockchain_data()
        blockchain_data['chapters'].append(chapter.to_dict())
        self._save_blockchain_data(blockchain_data)
        
        # Clear active pages
        pages_data['active_pages'] = []
        self._save_pages_data(pages_data)
        
        print(f"📚 Chapter created: {chapter_id} with {len(pages)} pages")
    
    def _generate_chapter_summary(self, pages: List[BlockchainPage]) -> Dict[str, Any]:
        """Generate summary statistics for a chapter"""
        
        action_counts = {}
        user_activity = {}
        
        for page in pages:
            # Count action types
            action_counts[page.action_type] = action_counts.get(page.action_type, 0) + 1
            
            # Count user activity
            user_activity[page.user_email] = user_activity.get(page.user_email, 0) + 1
        
        return {
            'total_pages': len(pages),
            'action_types': action_counts,
            'active_users': len(user_activity),
            'user_activity': user_activity,
            'time_span_hours': self._calculate_time_span(pages[0].timestamp, pages[-1].timestamp)
        }
    
    def _calculate_time_span(self, start_time: str, end_time: str) -> float:
        """Calculate time span between timestamps in hours"""
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds() / 3600
    
    def register_validator(self, user_email: str, public_key: str, role: str) -> Tuple[bool, str]:
        """Register a user as a blockchain validator"""
        
        # Check if user has appropriate role for validation
        if role not in ['contract_representative', 'contract_senator', 'contract_elder', 'contract_founder']:
            return False, "Only elected representatives can serve as validators"
        
        validators = self._load_validators()
        
        # Check if already registered
        for validator in validators:
            if validator['user_email'] == user_email:
                return False, "User is already registered as validator"
        
        # Add new validator
        validator_data = {
            'user_email': user_email,
            'public_key': public_key,
            'role': role,
            'registered_at': datetime.now().isoformat(),
            'status': 'active',
            'blocks_validated': 0,
            'validator_id': str(uuid.uuid4())
        }
        
        validators.append(validator_data)
        self._save_validators(validators)
        
        print(f"⚡ Validator registered: {user_email} ({role})")
        return True, "Validator registered successfully"
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get comprehensive blockchain statistics"""
        
        blockchain_data = self._load_blockchain_data()
        pages_data = self._load_pages_data()
        validators = self._load_validators()
        
        # Calculate stats
        stats = {
            'total_pages': blockchain_data.get('total_pages', 0),
            'active_pages': len(pages_data.get('active_pages', [])),
            'total_chapters': len(blockchain_data.get('chapters', [])),
            'total_books': len(blockchain_data.get('books', [])),
            'total_parts': len(blockchain_data.get('parts', [])),
            'total_series': len(blockchain_data.get('series', [])),
            'active_validators': len([v for v in validators if v.get('status') == 'active']),
            'total_validators': len(validators),
            'last_updated': blockchain_data.get('last_updated'),
            'blockchain_health': self._calculate_blockchain_health(blockchain_data, validators)
        }
        
        return stats
    
    def _calculate_blockchain_health(self, blockchain_data: Dict, validators: List[Dict]) -> str:
        """Calculate overall blockchain health status"""
        
        active_validators = len([v for v in validators if v.get('status') == 'active'])
        min_validators = blockchain_data.get('network_info', {}).get('min_validators', 3)
        
        if active_validators >= min_validators:
            return 'healthy'
        elif active_validators >= min_validators // 2:
            return 'warning'
        else:
            return 'critical'
    
    def search_blockchain(self, query_type: str = 'user', query_value: str = '', 
                         action_type: str = '', limit: int = 50) -> List[Dict[str, Any]]:
        """Search blockchain for specific records"""
        
        results = []
        
        # Search active pages
        pages_data = self._load_pages_data()
        for page in pages_data.get('active_pages', []):
            if self._matches_query(page, query_type, query_value, action_type):
                results.append(page)
        
        # Search chapters if needed
        if len(results) < limit:
            blockchain_data = self._load_blockchain_data()
            for chapter in blockchain_data.get('chapters', []):
                for page in chapter.get('pages', []):
                    if self._matches_query(page, query_type, query_value, action_type):
                        results.append(page)
                    
                    if len(results) >= limit:
                        break
        
        return results[:limit]
    
    def _matches_query(self, page: Dict[str, Any], query_type: str, query_value: str, action_type: str) -> bool:
        """Check if a page matches search criteria"""
        
        # Filter by action type if specified
        if action_type and page.get('action_type') != action_type:
            return False
        
        # Filter by query type and value
        if query_type == 'user' and query_value:
            return query_value.lower() in page.get('user_email', '').lower()
        elif query_type == 'action' and query_value:
            return query_value.lower() in page.get('action_type', '').lower()
        elif query_type == 'data' and query_value:
            data_str = json.dumps(page.get('data', {})).lower()
            return query_value.lower() in data_str
        
        return True
    
    def verify_blockchain_integrity(self) -> Tuple[bool, List[str]]:
        """Verify the integrity of the entire blockchain"""
        
        errors = []
        
        try:
            # Check genesis block
            if not self.genesis_block.exists():
                errors.append("Genesis block not found")
            
            # Verify active pages chain
            pages_data = self._load_pages_data()
            active_pages = pages_data.get('active_pages', [])
            
            previous_hash = None
            for i, page in enumerate(active_pages):
                # Verify hash chain
                if i > 0 and page.get('previous_hash') != previous_hash:
                    errors.append(f"Hash chain broken at page {i}")
                
                # Verify page hash
                page_obj = BlockchainPage(**page)
                calculated_hash = page_obj.calculate_hash()
                if page.get('block_hash') != calculated_hash:
                    errors.append(f"Invalid hash for page {page.get('page_id')}")
                
                previous_hash = page.get('block_hash')
            
            # Verify chapters
            blockchain_data = self._load_blockchain_data()
            for chapter in blockchain_data.get('chapters', []):
                if not chapter.get('chapter_hash'):
                    errors.append(f"Missing hash for chapter {chapter.get('chapter_id')}")
            
        except Exception as e:
            errors.append(f"Verification error: {str(e)}")
        
        is_valid = len(errors) == 0
        return is_valid, errors

# Global blockchain instance
_blockchain_instance = None

def get_blockchain() -> CivicBlockchain:
    """Get singleton blockchain instance"""
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = CivicBlockchain()
    return _blockchain_instance

# Convenience functions for external use
def add_user_action(action_type: str, user_email: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
    """Add user action to blockchain - main integration point"""
    blockchain = get_blockchain()
    return blockchain.add_page(action_type, user_email, data)

def search_user_actions(user_email: str, action_type: str = '', limit: int = 50) -> List[Dict[str, Any]]:
    """Search blockchain for user actions"""
    blockchain = get_blockchain()
    return blockchain.search_blockchain('user', user_email, action_type, limit)

def get_network_stats() -> Dict[str, Any]:
    """Get blockchain network statistics"""
    blockchain = get_blockchain()
    return blockchain.get_blockchain_stats()

if __name__ == "__main__":
    # Test blockchain functionality
    print("🏛️ Testing Civic Blockchain System")
    
    blockchain = CivicBlockchain()
    
    # Test adding pages
    test_data = {
        'user_id': 'test_user_123',
        'action': 'user_registration',
        'details': {'name': 'Test User', 'role': 'contract_citizen'}
    }
    
    success, message, page_id = blockchain.add_page(
        'user_registration',
        'test@civic.platform',
        test_data
    )
    
    if success:
        print(f"✅ Test page added: {page_id}")
        
        # Get stats
        stats = blockchain.get_blockchain_stats()
        print(f"📊 Blockchain stats: {stats}")
        
        # Verify integrity
        is_valid, errors = blockchain.verify_blockchain_integrity()
        if is_valid:
            print("✅ Blockchain integrity verified")
        else:
            print(f"❌ Integrity errors: {errors}")
    else:
        print(f"❌ Failed to add test page: {message}")