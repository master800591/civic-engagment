import hashlib
import json
import os
import threading
from datetime import timedelta
import datetime as dt
from .signatures import BlockchainSigner

# Thread lock for blockchain operations
_blockchain_lock = threading.Lock()

try:
    from civic_desktop.main import ENV_CONFIG
    BLOCKCHAIN_DB = ENV_CONFIG.get('blockchain_path', os.path.join(os.path.dirname(__file__), 'blockchain_db.json'))
    VALIDATORS_DB = os.path.join(os.path.dirname(__file__), 'validators_db.json')
except ImportError:
    BLOCKCHAIN_DB = os.path.join(os.path.dirname(__file__), 'blockchain_db.json')
    VALIDATORS_DB = os.path.join(os.path.dirname(__file__), 'validators_db.json')


# --- Hierarchical Block Classes ---
from typing import Dict, List, Any, Optional

from typing import Dict, List, Any, Optional

class PageBlock:
    def __init__(self, index: int, previous_hash: str, timestamp: str, data: Dict[str, Any], validator: str, signature: str) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.validator = validator
        self.signature = signature
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': self.data,
            'validator': self.validator,
            'signature': self.signature
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': self.data,
            'validator': self.validator,
            'signature': self.signature,
            'hash': self.hash
        }

class ChapterBlock:
    def __init__(self, index: int, previous_hash: str, timestamp: str, pages: List[Dict[str, Any]], validator: str, signature: str) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.pages = pages  # list of PageBlock dicts
        self.validator = validator
        self.signature = signature
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'pages': [p['hash'] for p in self.pages],
            'validator': self.validator,
            'signature': self.signature
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'pages': self.pages,
            'validator': self.validator,
            'signature': self.signature,
            'hash': self.hash
        }

# Book, Part, Series blocks follow the same pattern as ChapterBlock, but aggregate lower-level blocks
class BookBlock:
    def __init__(self, index: int, previous_hash: str, timestamp: str, chapters: List[Dict[str, Any]], validator: str, signature: str) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.chapters = chapters
        self.validator = validator
        self.signature = signature
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'chapters': [c['hash'] for c in self.chapters],
            'validator': self.validator,
            'signature': self.signature
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'chapters': self.chapters,
            'validator': self.validator,
            'signature': self.signature,
            'hash': self.hash
        }

class PartBlock:
    def __init__(self, index: int, previous_hash: str, timestamp: str, books: List[Dict[str, Any]], validator: str, signature: str) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.books = books
        self.validator = validator
        self.signature = signature
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'books': [b['hash'] for b in self.books],
            'validator': self.validator,
            'signature': self.signature
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'books': self.books,
            'validator': self.validator,
            'signature': self.signature,
            'hash': self.hash
        }

class SeriesBlock:
    def __init__(self, index: int, previous_hash: str, timestamp: str, parts: List[Dict[str, Any]], validator: str, signature: str) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.parts = parts
        self.validator = validator
        self.signature = signature
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'parts': [p['hash'] for p in self.parts],
            'validator': self.validator,
            'signature': self.signature
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'parts': self.parts,
            'validator': self.validator,
            'signature': self.signature,
            'hash': self.hash
        }


class Blockchain:
    """
    Hierarchical blockchain: Page (minute), Chapter (day), Book (month), Part (year), Series (10y).
    Each level aggregates the lower level. Validation occurs on rollup.
    """
    @staticmethod
    @staticmethod
    def load_chain() -> Dict[str, List[Dict[str, Any]]]:
        if not os.path.exists(BLOCKCHAIN_DB):
            return {'pages': [], 'chapters': [], 'books': [], 'parts': [], 'series': []}
        with open(BLOCKCHAIN_DB, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    @staticmethod
    def save_chain(chain: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save blockchain with atomic writes to prevent corruption"""
        import shutil
        import tempfile
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(BLOCKCHAIN_DB)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Create backup of existing chain
        backup_file = f"{BLOCKCHAIN_DB}.backup"
        if os.path.exists(BLOCKCHAIN_DB):
            try:
                shutil.copy2(BLOCKCHAIN_DB, backup_file)
            except Exception as e:
                print(f"Warning: Failed to create backup: {e}")
        
        # Write to temporary file first (atomic operation)
        temp_fd, temp_path = tempfile.mkstemp(dir=parent_dir, suffix='.tmp')
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(chain, f, indent=2)
            
            # Atomic move to final location
            if os.name == 'nt':  # Windows
                if os.path.exists(BLOCKCHAIN_DB):
                    os.remove(BLOCKCHAIN_DB)
                shutil.move(temp_path, BLOCKCHAIN_DB)
            else:  # Unix-like systems
                os.replace(temp_path, BLOCKCHAIN_DB)
                
        except Exception as e:
            # Clean up temp file on error
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Restore from backup if available
            if os.path.exists(backup_file):
                try:
                    shutil.copy2(backup_file, BLOCKCHAIN_DB)
                except:
                    pass
            
            raise Exception(f"Failed to save blockchain: {e}")
        
        # Clean up old backups (keep last 5)
        try:
            backup_files = [f for f in os.listdir(parent_dir) if f.startswith(os.path.basename(BLOCKCHAIN_DB) + '.backup')]
            backup_files.sort(key=lambda x: os.path.getctime(os.path.join(parent_dir, x)), reverse=True)
            for old_backup in backup_files[5:]:  # Keep only 5 most recent
                os.remove(os.path.join(parent_dir, old_backup))
        except Exception:
            pass  # Non-critical operation

    @staticmethod
    @staticmethod
    def get_last_block(level: str) -> Any:
        chain = Blockchain.load_chain()
        blocks = chain.get(level, [])
        return blocks[-1] if blocks else None

    @staticmethod
    def add_page(data: Dict[str, Any], validator: str, signature: Optional[str] = None) -> bool:
        """Add a new page to the blockchain with validation (thread-safe)"""
        from ..utils.validation import DataValidator
        
        # Thread-safe blockchain operations
        with _blockchain_lock:
            # Validate input data
            if not isinstance(data, dict):
                raise ValueError("Data must be a dictionary")
            
            if not validator or not isinstance(validator, str):
                raise ValueError("Validator must be a non-empty string")
            
            # Validate blockchain data format
            is_valid, error_msg = DataValidator.validate_blockchain_data(data)
            if not is_valid:
                raise ValueError(f"Invalid data for blockchain: {error_msg}")
            
            # Sanitize data before storage
            sanitized_data = DataValidator.sanitize_blockchain_data(data)
            
            try:
                chain = Blockchain.load_chain()
                pages = chain['pages']
                index = len(pages)
                previous_hash = pages[-1]['hash'] if pages else '0'*64
                timestamp = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
                
                # Generate real signature if not provided and not a system block
                if signature is None and validator not in ['SYSTEM', 'GENESIS']:
                    try:
                        block_signing_data = {
                            'index': index,
                            'previous_hash': previous_hash,
                            'timestamp': timestamp,
                            'data': sanitized_data,
                            'validator': validator
                        }
                        signature = BlockchainSigner.sign_block_data(block_signing_data, validator)
                    except Exception as e:
                        print(f"Warning: Failed to sign block for {validator}: {e}")
                        signature = 'UNSIGNED'
                elif signature is None:
                    signature = validator  # For system blocks
                
                block = PageBlock(index, previous_hash, timestamp, sanitized_data, validator, signature)
                
                # Re-validate index after block creation (double-check for thread safety)
                if block.index != len(pages):
                    print(f"Thread safety check failed: expected index {len(pages)}, got {block.index}")
                    return False
                
                pages.append(block.to_dict())
                chain['pages'] = pages
                
                # Validate chain integrity before saving
                if not Blockchain._validate_new_block(block, pages[:-1]):  # Validate against pages before adding
                    raise ValueError("Block validation failed")
                
                Blockchain.save_chain(chain)
                Blockchain._maybe_rollup(chain)
                return True
                
            except Exception as e:
                print(f"Error adding page to blockchain: {e}")
                return False
    
    @staticmethod
    def _validate_new_block(block: PageBlock, existing_pages: List[Dict[str, Any]]) -> bool:
        """Validate a new block before adding to chain"""
        try:
            # Check block structure
            if not hasattr(block, 'hash') or not hasattr(block, 'index'):
                return False
            
            # Check hash integrity
            expected_hash = block.compute_hash()
            if block.hash != expected_hash:
                print(f"Block hash mismatch: expected {expected_hash}, got {block.hash}")
                return False
            
            # Check index sequence
            if existing_pages and block.index != len(existing_pages):
                print(f"Invalid block index: expected {len(existing_pages)}, got {block.index}")
                return False
            
            # Check previous hash linkage
            if existing_pages:
                last_block = existing_pages[-1]
                if block.previous_hash != last_block['hash']:
                    print(f"Invalid previous hash: expected {last_block['hash']}, got {block.previous_hash}")
                    return False
            elif block.previous_hash != '0'*64:
                print(f"Invalid genesis block previous hash: {block.previous_hash}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Block validation error: {e}")
            return False

    @staticmethod
    def _maybe_rollup(chain: Dict[str, List[Dict[str, Any]]]) -> None:
        # Roll up to Chapter every 24h, Book every month, Part every year, Series every 10y
        Blockchain._rollup_chapter(chain)
        Blockchain._rollup_book(chain)
        Blockchain._rollup_part(chain)
        Blockchain._rollup_series(chain)
        Blockchain.save_chain(chain)

    @staticmethod
    @staticmethod
    def _rollup_chapter(chain: Dict[str, List[Dict[str, Any]]]) -> None:
        # If last chapter is >24h ago or no chapter, roll up pages
        pages = chain['pages']
        chapters = chain['chapters']
        if not pages:
            return
        last_chapter_time = dt.datetime.fromisoformat(chapters[-1]['timestamp'][:-1]) if chapters else None
        now = dt.datetime.now(dt.timezone.utc)
        # Ensure last_chapter_time is timezone-aware (UTC)
        if last_chapter_time is not None and last_chapter_time.tzinfo is None:
            last_chapter_time = last_chapter_time.replace(tzinfo=dt.timezone.utc)
        if not chapters or (last_chapter_time is None) or (now - last_chapter_time) >= timedelta(hours=24):
            # Aggregate all pages since last chapter
            start_idx = chapters[-1]['pages'][-1]['index']+1 if chapters else 0
            new_pages = [p for p in pages if p['index'] >= start_idx]
            if new_pages:
                index = len(chapters)
                previous_hash = chapters[-1]['hash'] if chapters else '0'*64
                timestamp = now.isoformat().replace('+00:00', 'Z')
                validator = new_pages[-1]['validator']
                signature = new_pages[-1]['signature']
                chapter = ChapterBlock(index, previous_hash, timestamp, new_pages, validator, signature)
                chapters.append(chapter.to_dict())
                chain['chapters'] = chapters

    @staticmethod
    @staticmethod
    def _rollup_book(chain: Dict[str, List[Dict[str, Any]]]) -> None:
        chapters = chain['chapters']
        books = chain['books']
        if not chapters:
            return
        last_book_time = dt.datetime.fromisoformat(books[-1]['timestamp'][:-1]) if books else None
        now = dt.datetime.now(dt.timezone.utc)
        # Ensure last_book_time is timezone-aware (UTC)
        if last_book_time is not None and last_book_time.tzinfo is None:
            last_book_time = last_book_time.replace(tzinfo=dt.timezone.utc)
        if not books or (last_book_time is None) or (now - last_book_time) >= timedelta(days=30):
            start_idx = books[-1]['chapters'][-1]['index']+1 if books else 0
            new_chapters = [c for c in chapters if c['index'] >= start_idx]
            if new_chapters:
                index = len(books)
                previous_hash = books[-1]['hash'] if books else '0'*64
                timestamp = now.isoformat().replace('+00:00', 'Z')
                validator = new_chapters[-1]['validator']
                signature = new_chapters[-1]['signature']
                book = BookBlock(index, previous_hash, timestamp, new_chapters, validator, signature)
                books.append(book.to_dict())
                chain['books'] = books

    @staticmethod
    @staticmethod
    def _rollup_part(chain: Dict[str, List[Dict[str, Any]]]) -> None:
        books = chain['books']
        parts = chain['parts']
        if not books:
            return
        last_part_time = dt.datetime.fromisoformat(parts[-1]['timestamp'][:-1]) if parts else None
        now = dt.datetime.now(dt.timezone.utc)
        # Ensure last_part_time is timezone-aware (UTC)
        if last_part_time is not None and last_part_time.tzinfo is None:
            last_part_time = last_part_time.replace(tzinfo=dt.timezone.utc)
        if not parts or (last_part_time is None) or (now - last_part_time) >= timedelta(days=365):
            start_idx = parts[-1]['books'][-1]['index']+1 if parts else 0
            new_books = [b for b in books if b['index'] >= start_idx]
            if new_books:
                index = len(parts)
                previous_hash = parts[-1]['hash'] if parts else '0'*64
                timestamp = now.isoformat().replace('+00:00', 'Z')
                validator = new_books[-1]['validator']
                signature = new_books[-1]['signature']
                part = PartBlock(index, previous_hash, timestamp, new_books, validator, signature)
                parts.append(part.to_dict())
                chain['parts'] = parts

    @staticmethod
    @staticmethod
    def _rollup_series(chain: Dict[str, List[Dict[str, Any]]]) -> None:
        parts = chain['parts']
        series = chain['series']
        if not parts:
            return
        last_series_time = dt.datetime.fromisoformat(series[-1]['timestamp'][:-1]) if series else None
        now = dt.datetime.now(dt.timezone.utc)
        # Ensure last_series_time is timezone-aware (UTC)
        if last_series_time is not None:
            if last_series_time.tzinfo is None:
                last_series_time = last_series_time.replace(tzinfo=dt.timezone.utc)
            elif last_series_time.tzinfo != dt.timezone.utc:
                last_series_time = last_series_time.astimezone(dt.timezone.utc)

        if not series or (last_series_time is None) or (now - last_series_time) >= timedelta(days=3650):
            start_idx = series[-1]['parts'][-1]['index']+1 if series else 0
            new_parts = [p for p in parts if p['index'] >= start_idx]
            if new_parts:
                index = len(series)
                previous_hash = series[-1]['hash'] if series else '0'*64
                timestamp = now.isoformat().replace('+00:00', 'Z')
                validator = new_parts[-1]['validator']
                signature = new_parts[-1]['signature']
                sblock = SeriesBlock(index, previous_hash, timestamp, new_parts, validator, signature)
                series.append(sblock.to_dict())
                chain['series'] = series

    @staticmethod
    @staticmethod
    def validate_chain() -> bool:
        """Validate blockchain integrity including signatures"""
        chain = Blockchain.load_chain()
        
        # Validate all levels
        for level in ['pages', 'chapters', 'books', 'parts', 'series']:
            blocks = chain.get(level, [])
            for i in range(1, len(blocks)):
                prev = blocks[i-1]
                curr = blocks[i]
                if curr['previous_hash'] != prev['hash']:
                    print(f"Hash chain broken at {level} block {i}")
                    return False
        
        # Validate signatures for page blocks
        pages = chain.get('pages', [])
        for page in pages:
            validator = page.get('validator', '')
            signature = page.get('signature', '')
            
            # Skip validation for system blocks
            if validator in ['SYSTEM', 'GENESIS'] or signature in ['GENESIS', 'PERIODIC', 'SYSTEM']:
                continue
            
            try:
                # Get validator's public key
                public_key = BlockchainSigner.get_validator_public_key(validator)
                
                # Prepare signing data (exclude signature and hash)
                signing_data = {
                    'index': page['index'],
                    'previous_hash': page['previous_hash'],
                    'timestamp': page['timestamp'],
                    'data': page['data'],
                    'validator': page['validator']
                }
                
                # Verify signature
                if not BlockchainSigner.verify_block_signature(signing_data, signature, public_key):
                    print(f"Invalid signature for block {page['index']} by validator {validator}")
                    return False
                    
            except Exception as e:
                print(f"Signature validation error for block {page['index']}: {e}")
                return False
        
        return True

class ValidatorRegistry:
    @staticmethod
    @staticmethod
    def load_validators() -> List[Dict[str, Any]]:
        if not os.path.exists(VALIDATORS_DB):
            return []
        with open(VALIDATORS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    @staticmethod
    def save_validators(validators: List[Dict[str, Any]]) -> None:
        with open(VALIDATORS_DB, 'w', encoding='utf-8') as f:
            json.dump(validators, f, indent=2)

    @staticmethod
    @staticmethod
    def add_validator(email: str, public_key: str) -> None:
        validators = ValidatorRegistry.load_validators()
        if not any(v['email'] == email for v in validators):
            import datetime as dt
            validators.append({'email': email, 'public_key': public_key, 'active': True, 'added_at': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')})
            ValidatorRegistry.save_validators(validators)

    @staticmethod
    @staticmethod
    def remove_validator(email: str) -> None:
        validators = ValidatorRegistry.load_validators()
        for v in validators:
            if v['email'] == email:
                v['active'] = False
        ValidatorRegistry.save_validators(validators)

    @staticmethod
    @staticmethod
    def is_validator(email: str) -> bool:
        validators = ValidatorRegistry.load_validators()
        return any(v['email'] == email and v['active'] for v in validators)

# --- Enhanced Module Integration Methods ---

class BlockchainIntegrator:
    """Enhanced blockchain integration for all platform modules"""
    
    @staticmethod
    def get_user_activity_summary(user_email: str) -> Dict[str, Any]:
        """Get comprehensive activity summary for a user from blockchain"""
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        activities = {
            'total_actions': 0,
            'registration_date': None,
            'debates': {'topics_created': 0, 'arguments_posted': 0, 'votes_cast': 0},
            'moderation': {'flags_submitted': 0, 'flags_reviewed': 0, 'warnings_issued': 0},
            'training': {'courses_started': 0, 'modules_completed': 0, 'certifications_earned': 0},
            'governance': {'elections_participated': 0, 'proposals_made': 0},
            'blockchain_participation': {'blocks_validated': 0, 'signatures_provided': 0},
            'first_activity': None,
            'last_activity': None,
            'activity_timeline': []
        }
        
        for page in pages:
            data = page.get('data', {})
            action = data.get('action', '')
            page_user = data.get('user_email') or data.get('email') or data.get('author_email') or data.get('creator_email')
            validator = page.get('validator', '')
            timestamp = page.get('timestamp', '')
            
            # Track activities for this user
            if page_user == user_email:
                activities['total_actions'] += 1
                
                # Track timeline
                activities['activity_timeline'].append({
                    'timestamp': timestamp,
                    'action': action,
                    'details': data
                })
                
                # Update first/last activity
                if not activities['first_activity'] or timestamp < activities['first_activity']:
                    activities['first_activity'] = timestamp
                if not activities['last_activity'] or timestamp > activities['last_activity']:
                    activities['last_activity'] = timestamp
                
                # Categorize activities
                if action == 'register_user':
                    activities['registration_date'] = timestamp
                elif action == 'create_topic':
                    activities['debates']['topics_created'] += 1
                elif action == 'add_argument':
                    activities['debates']['arguments_posted'] += 1
                elif action == 'vote_on_topic':
                    activities['debates']['votes_cast'] += 1
                elif action == 'flag_content':
                    activities['moderation']['flags_submitted'] += 1
                elif action == 'review_flag':
                    activities['moderation']['flags_reviewed'] += 1
                elif action == 'warn_user':
                    activities['moderation']['warnings_issued'] += 1
                elif action == 'start_course':
                    activities['training']['courses_started'] += 1
                elif action == 'complete_module':
                    activities['training']['modules_completed'] += 1
                elif action == 'complete_course':
                    activities['training']['certifications_earned'] += 1
                elif action in ['vote_in_election', 'run_for_office']:
                    activities['governance']['elections_participated'] += 1
                elif action in ['propose_amendment', 'create_proposal']:
                    activities['governance']['proposals_made'] += 1
            
            # Track blockchain participation
            if validator == user_email:
                activities['blockchain_participation']['blocks_validated'] += 1
                if page.get('signature') and page.get('signature') not in ['GENESIS', 'SYSTEM', 'PERIODIC']:
                    activities['blockchain_participation']['signatures_provided'] += 1
        
        # Sort timeline by timestamp
        activities['activity_timeline'].sort(key=lambda x: x['timestamp'])
        
        return activities
    
    @staticmethod
    def get_module_statistics() -> Dict[str, Any]:
        """Get comprehensive statistics for all modules from blockchain"""
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        stats = {
            'total_pages': len(pages),
            'users': {'total': 0, 'active_last_30_days': 0, 'roles': {}},
            'debates': {'topics': 0, 'arguments': 0, 'votes': 0, 'active_topics': 0},
            'moderation': {'flags': 0, 'reviews': 0, 'warnings': 0, 'avg_resolution_time': 0},
            'training': {'courses_started': 0, 'modules_completed': 0, 'certifications': 0, 'avg_score': 0},
            'governance': {'elections': 0, 'proposals': 0, 'active_representatives': 0},
            'blockchain': {'validators': 0, 'avg_block_time': 0, 'chain_integrity': True},
            'activity_by_date': {},
            'top_contributors': [],
            'system_health': {'errors': 0, 'warnings': 0, 'last_rollup': None}
        }
        
        import datetime as dt
        thirty_days_ago = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).isoformat()
        user_emails = set()
        user_activity = {}
        topic_ids = set()
        flag_times = {}
        quiz_scores = []
        
        for page in pages:
            data = page.get('data', {})
            action = data.get('action', '')
            timestamp = page.get('timestamp', '')
            page_user = data.get('user_email') or data.get('email') or data.get('author_email') or data.get('creator_email')
            
            # Track daily activity
            date_key = timestamp[:10] if timestamp else 'unknown'
            if date_key not in stats['activity_by_date']:
                stats['activity_by_date'][date_key] = 0
            stats['activity_by_date'][date_key] += 1
            
            # Track users
            if page_user:
                user_emails.add(page_user)
                if page_user not in user_activity:
                    user_activity[page_user] = 0
                user_activity[page_user] += 1
                
                if timestamp >= thirty_days_ago:
                    stats['users']['active_last_30_days'] += 1
            
            # Categorize by action
            if action == 'register_user':
                role = data.get('role', 'Contract Citizen')
                stats['users']['roles'][role] = stats['users']['roles'].get(role, 0) + 1
            elif action == 'create_topic':
                stats['debates']['topics'] += 1
                topic_ids.add(data.get('topic_id', ''))
            elif action == 'add_argument':
                stats['debates']['arguments'] += 1
            elif action == 'vote_on_topic':
                stats['debates']['votes'] += 1
            elif action == 'flag_content':
                stats['moderation']['flags'] += 1
                flag_id = data.get('flag_id', '')
                if flag_id:
                    flag_times[flag_id] = timestamp
            elif action == 'review_flag':
                stats['moderation']['reviews'] += 1
                flag_id = data.get('flag_id', '')
                if flag_id in flag_times:
                    # Calculate resolution time
                    try:
                        start_time = dt.datetime.fromisoformat(flag_times[flag_id].replace('Z', '+00:00'))
                        end_time = dt.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        resolution_hours = (end_time - start_time).total_seconds() / 3600
                        stats['moderation']['avg_resolution_time'] += resolution_hours
                    except:
                        pass
            elif action == 'warn_user':
                stats['moderation']['warnings'] += 1
            elif action == 'start_course':
                stats['training']['courses_started'] += 1
            elif action == 'complete_module':
                stats['training']['modules_completed'] += 1
                quiz_score = data.get('quiz_score', 0)
                if quiz_score > 0:
                    quiz_scores.append(quiz_score)
            elif action == 'complete_course':
                stats['training']['certifications'] += 1
            elif action in ['vote_in_election', 'run_for_office']:
                stats['governance']['elections'] += 1
            elif action in ['propose_amendment', 'create_proposal']:
                stats['governance']['proposals'] += 1
        
        # Calculate derived statistics
        stats['users']['total'] = len(user_emails)
        stats['debates']['active_topics'] = len(topic_ids)
        
        if stats['moderation']['reviews'] > 0:
            stats['moderation']['avg_resolution_time'] /= stats['moderation']['reviews']
        
        if quiz_scores:
            stats['training']['avg_score'] = sum(quiz_scores) / len(quiz_scores)
        
        # Top contributors
        sorted_contributors = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
        stats['top_contributors'] = [{'email': email, 'actions': count} for email, count in sorted_contributors[:10]]
        
        # Blockchain health
        validators = ValidatorRegistry.load_validators()
        stats['blockchain']['validators'] = len([v for v in validators if v.get('active')])
        stats['blockchain']['chain_integrity'] = Blockchain.validate_chain()
        
        return stats
    
    @staticmethod
    def get_cross_module_dependencies(user_email: str) -> Dict[str, Any]:
        """Analyze dependencies and relationships between modules for a user"""
        user_activity = BlockchainIntegrator.get_user_activity_summary(user_email)
        
        dependencies = {
            'user_role_progression': [],
            'training_requirements': {},
            'moderation_impact': {},
            'debate_participation_trends': {},
            'governance_eligibility': {},
            'blockchain_trust_score': 0.0,
            'cross_module_interactions': [],
            'recommended_actions': []
        }
        
        # Analyze role progression
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        for page in pages:
            data = page.get('data', {})
            page_user = data.get('user_email') or data.get('email')
            
            if page_user == user_email:
                action = data.get('action', '')
                timestamp = page.get('timestamp', '')
                
                if action == 'register_user':
                    dependencies['user_role_progression'].append({
                        'timestamp': timestamp,
                        'role': data.get('role', 'Contract Citizen'),
                        'trigger': 'Registration'
                    })
                elif action == 'complete_course':
                    course_id = data.get('course_id', '')
                    if 'governance' in course_id.lower():
                        dependencies['user_role_progression'].append({
                            'timestamp': timestamp,
                            'role': 'Training Qualified',
                            'trigger': f'Completed course: {course_id}'
                        })
        
        # Training requirements analysis
        certifications = user_activity['training']['certifications_earned']
        modules_completed = user_activity['training']['modules_completed']
        
        dependencies['training_requirements'] = {
            'governance_certification': certifications >= 1,
            'debate_qualification': modules_completed >= 3,
            'moderation_eligibility': certifications >= 1 and user_activity['moderation']['flags_submitted'] >= 5,
            'representative_readiness': certifications >= 2 and user_activity['debates']['topics_created'] >= 1
        }
        
        # Moderation impact analysis
        flags_submitted = user_activity['moderation']['flags_submitted']
        warnings_received = 0  # Count warnings received by this user
        
        for page in pages:
            data = page.get('data', {})
            if data.get('action') == 'warn_user' and data.get('target_email') == user_email:
                warnings_received += 1
        
        dependencies['moderation_impact'] = {
            'flags_submitted': flags_submitted,
            'warnings_received': warnings_received,
            'moderation_standing': 'good' if warnings_received == 0 else 'warning' if warnings_received < 3 else 'probation',
            'can_run_for_office': warnings_received < 2
        }
        
        # Calculate blockchain trust score
        blockchain_participation = user_activity['blockchain_participation']
        total_actions = user_activity['total_actions']
        
        trust_score = 0.0
        if total_actions > 0:
            # Base score from participation
            trust_score += min(total_actions * 0.1, 50.0)
            
            # Bonus for blockchain validation
            trust_score += blockchain_participation['blocks_validated'] * 2.0
            
            # Bonus for training completion
            trust_score += user_activity['training']['certifications_earned'] * 10.0
            
            # Penalty for warnings
            trust_score -= warnings_received * 15.0
            
            # Bonus for positive moderation activity
            trust_score += user_activity['moderation']['flags_reviewed'] * 5.0
            
            # Cap at 100
            trust_score = min(max(trust_score, 0.0), 100.0)
        
        dependencies['blockchain_trust_score'] = round(trust_score, 1)
        
        # Generate recommendations
        recommendations = []
        
        if user_activity['training']['certifications_earned'] == 0:
            recommendations.append("Complete civic governance training to unlock advanced features")
        
        if user_activity['debates']['topics_created'] == 0 and user_activity['training']['certifications_earned'] > 0:
            recommendations.append("Create your first debate topic to engage in governance")
        
        if user_activity['moderation']['flags_submitted'] < 3:
            recommendations.append("Participate in content moderation by reporting inappropriate content")
        
        if blockchain_participation['blocks_validated'] == 0 and warnings_received == 0:
            recommendations.append("Consider running for Contract Representative to become a blockchain validator")
        
        if trust_score < 50:
            recommendations.append("Increase platform participation to improve blockchain trust score")
        
        dependencies['recommended_actions'] = recommendations
        
        return dependencies
    
    @staticmethod
    def get_module_health_report() -> Dict[str, Any]:
        """Generate comprehensive health report for all modules"""
        stats = BlockchainIntegrator.get_module_statistics()
        
        health_report = {
            'overall_health': 'healthy',
            'module_status': {},
            'alerts': [],
            'recommendations': [],
            'performance_metrics': {},
            'data_integrity': {},
            'user_engagement': {}
        }
        
        # Analyze each module
        modules = ['users', 'debates', 'moderation', 'training', 'governance', 'blockchain']
        
        for module in modules:
            module_data = stats.get(module, {})
            status = 'healthy'
            issues = []
            
            if module == 'users':
                if module_data.get('total', 0) < 5:
                    status = 'warning'
                    issues.append('Low user registration')
                if module_data.get('active_last_30_days', 0) / max(module_data.get('total', 1), 1) < 0.3:
                    status = 'warning'
                    issues.append('Low user activity')
            
            elif module == 'debates':
                if module_data.get('topics', 0) == 0:
                    status = 'warning'
                    issues.append('No debate topics created')
                if module_data.get('arguments', 0) / max(module_data.get('topics', 1), 1) < 2:
                    status = 'warning'
                    issues.append('Low debate engagement')
            
            elif module == 'moderation':
                if module_data.get('flags', 0) > 0 and module_data.get('reviews', 0) == 0:
                    status = 'critical'
                    issues.append('Unreviewed content flags')
                if module_data.get('avg_resolution_time', 0) > 72:  # 72 hours
                    status = 'warning'
                    issues.append('Slow flag resolution time')
            
            elif module == 'training':
                if module_data.get('courses_started', 0) > 0 and module_data.get('certifications', 0) == 0:
                    status = 'warning'
                    issues.append('No course completions')
                if module_data.get('avg_score', 0) < 70:
                    status = 'warning'
                    issues.append('Low average quiz scores')
            
            elif module == 'blockchain':
                if not module_data.get('chain_integrity', True):
                    status = 'critical'
                    issues.append('Blockchain integrity failure')
                if module_data.get('validators', 0) < 3:
                    status = 'warning'
                    issues.append('Insufficient validators')
            
            health_report['module_status'][module] = {
                'status': status,
                'issues': issues,
                'metrics': module_data
            }
            
            # Add to alerts if critical
            if status == 'critical':
                health_report['alerts'].extend([f"{module.title()}: {issue}" for issue in issues])
        
        # Overall health assessment
        critical_modules = [m for m, data in health_report['module_status'].items() if data['status'] == 'critical']
        warning_modules = [m for m, data in health_report['module_status'].items() if data['status'] == 'warning']
        
        if critical_modules:
            health_report['overall_health'] = 'critical'
        elif len(warning_modules) > 2:
            health_report['overall_health'] = 'degraded'
        elif warning_modules:
            health_report['overall_health'] = 'warning'
        
        # Generate recommendations
        if critical_modules:
            health_report['recommendations'].append("Address critical issues immediately")
        if warning_modules:
            health_report['recommendations'].append("Monitor warning conditions and take preventive action")
        if stats['users']['total'] < 10:
            health_report['recommendations'].append("Increase user registration and onboarding")
        if stats['blockchain']['validators'] < 5:
            health_report['recommendations'].append("Recruit more blockchain validators")
        
        return health_report
