# Document Manager - Comprehensive Document Management Backend
# Document storage, versioning, FOIA processing, and legislative tracking

import json
import os
import uuid
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Import application components
try:
    from main import ENV_CONFIG
    from blockchain.blockchain import Blockchain
    from utils.validation import DataValidator
except ImportError as e:
    print(f"Warning: Import error in document manager: {e}")
    ENV_CONFIG = {}


class DocumentManager:
    """Comprehensive document management system with versioning and transparency"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('documents_db_path', 'documents/documents_db.json')
        self.storage_path = ENV_CONFIG.get('documents_storage_path', 'documents/storage')
        self.ensure_database()
        self.ensure_storage_directory()
        
        # Initialize document type configurations
        self.document_types = self.load_document_type_configurations()
        self.retention_policies = self.load_retention_policies()
    
    def ensure_database(self):
        """Ensure documents database exists"""
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initial_data = {
                'documents': [],
                'document_versions': [],
                'foia_requests': [],
                'legislative_tracking': [],
                'access_logs': [],
                'retention_schedules': [],
                'document_relationships': [],
                'search_index': {}
            }
            
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def ensure_storage_directory(self):
        """Ensure document storage directory exists"""
        
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Create subdirectories for organization
        subdirs = [
            'public', 'internal', 'confidential', 'restricted',
            'legislative', 'policies', 'contracts', 'reports',
            'archive', 'versions', 'temp'
        ]
        
        for subdir in subdirs:
            os.makedirs(os.path.join(self.storage_path, subdir), exist_ok=True)
    
    def load_document_type_configurations(self) -> Dict[str, Dict]:
        """Load configuration for different document types"""
        
        return {
            'legislative_bill': {
                'description': 'Legislative bills and ordinances',
                'required_fields': ['sponsor', 'bill_number', 'reading_stage'],
                'approval_workflow': True,
                'public_access': True,
                'versioning_required': True,
                'retention_category': 'permanent',
                'search_priority': 'high'
            },
            'policy_document': {
                'description': 'Policy documents and procedures',
                'required_fields': ['policy_area', 'effective_date'],
                'approval_workflow': True,
                'public_access': True,
                'versioning_required': True,
                'retention_category': 'long_term',
                'search_priority': 'high'
            },
            'meeting_minutes': {
                'description': 'Meeting minutes and records',
                'required_fields': ['meeting_date', 'attendees', 'agenda'],
                'approval_workflow': True,
                'public_access': True,
                'versioning_required': False,
                'retention_category': 'permanent',
                'search_priority': 'medium'
            },
            'budget_document': {
                'description': 'Budget and financial documents',
                'required_fields': ['fiscal_year', 'budget_category'],
                'approval_workflow': True,
                'public_access': True,
                'versioning_required': True,
                'retention_category': 'permanent',
                'search_priority': 'high'
            },
            'contract_agreement': {
                'description': 'Contracts and legal agreements',
                'required_fields': ['parties', 'contract_value', 'term'],
                'approval_workflow': True,
                'public_access': 'limited',  # Some contract details may be confidential
                'versioning_required': True,
                'retention_category': 'long_term',
                'search_priority': 'medium'
            },
            'legal_opinion': {
                'description': 'Legal opinions and advice',
                'required_fields': ['legal_issue', 'attorney'],
                'approval_workflow': True,
                'public_access': 'limited',
                'versioning_required': True,
                'retention_category': 'long_term',
                'search_priority': 'medium'
            },
            'research_report': {
                'description': 'Research reports and studies',
                'required_fields': ['research_topic', 'methodology'],
                'approval_workflow': False,
                'public_access': True,
                'versioning_required': True,
                'retention_category': 'medium_term',
                'search_priority': 'medium'
            },
            'public_notice': {
                'description': 'Public notices and announcements',
                'required_fields': ['notice_type', 'publication_date'],
                'approval_workflow': False,
                'public_access': True,
                'versioning_required': False,
                'retention_category': 'medium_term',
                'search_priority': 'low'
            },
            'correspondence': {
                'description': 'Official correspondence',
                'required_fields': ['sender', 'recipient', 'subject'],
                'approval_workflow': False,
                'public_access': 'limited',
                'versioning_required': False,
                'retention_category': 'medium_term',
                'search_priority': 'low'
            },
            'administrative_record': {
                'description': 'Administrative records and forms',
                'required_fields': ['record_type', 'processing_date'],
                'approval_workflow': False,
                'public_access': 'limited',
                'versioning_required': False,
                'retention_category': 'variable',
                'search_priority': 'low'
            }
        }
    
    def load_retention_policies(self) -> Dict[str, Dict]:
        """Load document retention policies"""
        
        return {
            'permanent': {
                'retention_period': 'indefinite',
                'review_cycle': 'annual',
                'destruction_authorized': False,
                'archive_after_years': 25,
                'digital_preservation': True
            },
            'long_term': {
                'retention_period': '25_years',
                'review_cycle': 'every_5_years',
                'destruction_authorized': True,
                'archive_after_years': 10,
                'digital_preservation': True
            },
            'medium_term': {
                'retention_period': '10_years',
                'review_cycle': 'every_3_years',
                'destruction_authorized': True,
                'archive_after_years': 5,
                'digital_preservation': True
            },
            'short_term': {
                'retention_period': '5_years',
                'review_cycle': 'annual',
                'destruction_authorized': True,
                'archive_after_years': 3,
                'digital_preservation': False
            },
            'variable': {
                'retention_period': 'case_by_case',
                'review_cycle': 'as_needed',
                'destruction_authorized': 'case_by_case',
                'archive_after_years': 'variable',
                'digital_preservation': 'case_by_case'
            }
        }
    
    def upload_document(self, document_data: Dict, file_path: str) -> Tuple[bool, str]:
        """Upload and process a new document"""
        
        try:
            # Validate document data
            validation_result = self.validate_document_data(document_data)
            if not validation_result['valid']:
                return False, f"Validation failed: {validation_result['errors']}"
            
            # Generate document ID and storage paths
            document_id = str(uuid.uuid4())
            file_hash = self.calculate_file_hash(file_path)
            
            # Check for duplicate documents
            duplicate_check = self.check_for_duplicates(file_hash)
            if duplicate_check['is_duplicate']:
                return False, f"Duplicate document detected: {duplicate_check['existing_document_id']}"
            
            # Determine storage location based on classification
            storage_subdir = self.get_storage_subdirectory(document_data['classification'])
            file_extension = os.path.splitext(file_path)[1]
            stored_filename = f"{document_id}{file_extension}"
            stored_path = os.path.join(self.storage_path, storage_subdir, stored_filename)
            
            # Copy file to storage location
            shutil.copy2(file_path, stored_path)
            
            # Get file metadata
            file_stats = os.stat(stored_path)
            file_size = file_stats.st_size
            
            # Create document record
            document = {
                'id': document_id,
                'title': document_data['title'],
                'type': document_data['type'],
                'description': document_data['description'],
                'author': document_data['author'],
                'department': document_data['department'],
                'classification': document_data['classification'],
                'jurisdiction': document_data['jurisdiction'],
                'tags': document_data.get('tags', []),
                'public_access': document_data.get('public_access', True),
                'searchable': document_data.get('searchable', True),
                'retention_period': document_data.get('retention_period', 'permanent'),
                'uploaded_by': document_data['uploaded_by'],
                'file_info': {
                    'original_filename': os.path.basename(file_path),
                    'stored_filename': stored_filename,
                    'stored_path': stored_path,
                    'file_size': file_size,
                    'file_hash': file_hash,
                    'mime_type': self.get_mime_type(file_path)
                },
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_modified': datetime.now().isoformat(),
                    'version': '1.0',
                    'status': 'active',
                    'access_count': 0,
                    'last_accessed': None
                },
                'workflow': {
                    'approval_required': self.requires_approval(document_data['type']),
                    'approval_status': 'pending_review' if self.requires_approval(document_data['type']) else 'approved',
                    'approved_by': None,
                    'approval_date': None
                },
                'compliance': {
                    'retention_policy': self.get_retention_policy(document_data['type']),
                    'destruction_date': self.calculate_destruction_date(document_data),
                    'archive_date': self.calculate_archive_date(document_data),
                    'legal_holds': []
                }
            }
            
            # Save document record
            self.save_document(document)
            
            # Create initial version record
            version_record = self.create_version_record(document, 'Initial upload', document_data['uploaded_by'])
            self.save_version(version_record)
            
            # Update search index
            self.update_search_index(document)
            
            # Record document upload on blockchain
            try:
                Blockchain.add_page(
                    action_type="document_uploaded",
                    data={
                        'document_id': document_id,
                        'title': document['title'],
                        'type': document['type'],
                        'classification': document['classification'],
                        'uploaded_by': document['uploaded_by'],
                        'file_hash': file_hash
                    },
                    user_email=document['uploaded_by']
                )
            except Exception as e:
                print(f"Warning: Failed to record document upload on blockchain: {e}")
            
            # Process document based on type
            self.process_document_by_type(document)
            
            return True, f"Document uploaded successfully with ID: {document_id}"
            
        except Exception as e:
            return False, f"Error uploading document: {e}"
    
    def validate_document_data(self, document_data: Dict) -> Dict:
        """Validate document data before processing"""
        
        errors = []
        
        # Required fields
        required_fields = ['title', 'type', 'description', 'uploaded_by']
        for field in required_fields:
            if not document_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate document type
        doc_type = document_data.get('type', '').lower().replace(' ', '_')
        if doc_type not in self.document_types:
            errors.append(f"Invalid document type: {document_data.get('type')}")
        else:
            # Check type-specific required fields
            type_config = self.document_types[doc_type]
            for field in type_config.get('required_fields', []):
                if not document_data.get(field):
                    errors.append(f"Missing required field for {document_data['type']}: {field}")
        
        # Validate classification
        valid_classifications = ['public', 'internal', 'confidential', 'restricted']
        if document_data.get('classification', '').lower() not in valid_classifications:
            errors.append("Invalid classification level")
        
        # Validate email format for uploader
        if document_data.get('uploaded_by'):
            try:
                # Basic email validation
                email = document_data['uploaded_by']
                if '@' not in email or '.' not in email.split('@')[1]:
                    errors.append("Invalid uploader email format")
            except:
                errors.append("Invalid uploader email")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for duplicate detection"""
        
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def check_for_duplicates(self, file_hash: str) -> Dict:
        """Check if document already exists based on file hash"""
        
        try:
            data = self.load_data()
            
            for document in data['documents']:
                if document.get('file_info', {}).get('file_hash') == file_hash:
                    return {
                        'is_duplicate': True,
                        'existing_document_id': document['id'],
                        'existing_title': document['title']
                    }
            
            return {'is_duplicate': False}
            
        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return {'is_duplicate': False}
    
    def get_storage_subdirectory(self, classification: str) -> str:
        """Determine storage subdirectory based on classification"""
        
        classification_map = {
            'public': 'public',
            'internal': 'internal',
            'confidential': 'confidential',
            'restricted': 'restricted'
        }
        
        return classification_map.get(classification.lower(), 'internal')
    
    def get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file"""
        
        extension = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.xml': 'application/xml',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        
        return mime_types.get(extension, 'application/octet-stream')
    
    def requires_approval(self, document_type: str) -> bool:
        """Check if document type requires approval workflow"""
        
        doc_type = document_type.lower().replace(' ', '_')
        type_config = self.document_types.get(doc_type, {})
        return type_config.get('approval_workflow', False)
    
    def get_retention_policy(self, document_type: str) -> str:
        """Get retention policy for document type"""
        
        doc_type = document_type.lower().replace(' ', '_')
        type_config = self.document_types.get(doc_type, {})
        return type_config.get('retention_category', 'medium_term')
    
    def calculate_destruction_date(self, document_data: Dict) -> Optional[str]:
        """Calculate document destruction date based on retention policy"""
        
        retention_category = self.get_retention_policy(document_data['type'])
        retention_policy = self.retention_policies.get(retention_category, {})
        
        if retention_policy.get('destruction_authorized') == False:
            return None  # Permanent retention
        
        retention_period = retention_policy.get('retention_period')
        if retention_period and retention_period.endswith('_years'):
            years = int(retention_period.split('_')[0])
            destruction_date = datetime.now() + timedelta(days=years * 365)
            return destruction_date.isoformat()
        
        return None
    
    def calculate_archive_date(self, document_data: Dict) -> Optional[str]:
        """Calculate document archive date"""
        
        retention_category = self.get_retention_policy(document_data['type'])
        retention_policy = self.retention_policies.get(retention_category, {})
        
        archive_years = retention_policy.get('archive_after_years')
        if archive_years and isinstance(archive_years, int):
            archive_date = datetime.now() + timedelta(days=archive_years * 365)
            return archive_date.isoformat()
        
        return None
    
    def create_version_record(self, document: Dict, changes_description: str, modified_by: str) -> Dict:
        """Create version record for document"""
        
        return {
            'id': str(uuid.uuid4()),
            'document_id': document['id'],
            'version_number': document['metadata']['version'],
            'created_at': datetime.now().isoformat(),
            'modified_by': modified_by,
            'changes_description': changes_description,
            'file_hash': document['file_info']['file_hash'],
            'file_size': document['file_info']['file_size'],
            'stored_path': document['file_info']['stored_path']
        }
    
    def update_search_index(self, document: Dict):
        """Update search index for document"""
        
        try:
            data = self.load_data()
            
            if 'search_index' not in data:
                data['search_index'] = {}
            
            # Create searchable text from document metadata
            searchable_text = ' '.join([
                document['title'],
                document['description'],
                document['author'],
                document['department'],
                ' '.join(document.get('tags', []))
            ]).lower()
            
            # Simple keyword indexing
            words = searchable_text.split()
            for word in words:
                if len(word) > 2:  # Skip very short words
                    if word not in data['search_index']:
                        data['search_index'][word] = []
                    
                    if document['id'] not in data['search_index'][word]:
                        data['search_index'][word].append(document['id'])
            
            self.save_data(data)
            
        except Exception as e:
            print(f"Error updating search index: {e}")
    
    def process_document_by_type(self, document: Dict):
        """Process document based on its type"""
        
        doc_type = document['type'].lower().replace(' ', '_')
        
        if doc_type == 'legislative_bill':
            self.process_legislative_bill(document)
        elif doc_type == 'budget_document':
            self.process_budget_document(document)
        elif doc_type == 'contract_agreement':
            self.process_contract_agreement(document)
        # Add more type-specific processing as needed
    
    def process_legislative_bill(self, document: Dict):
        """Process legislative bill for tracking"""
        
        # Create legislative tracking record
        tracking_record = {
            'id': str(uuid.uuid4()),
            'document_id': document['id'],
            'bill_number': document.get('bill_number', 'TBD'),
            'title': document['title'],
            'sponsor': document.get('sponsor', 'Unknown'),
            'status': 'introduced',
            'stage': document.get('reading_stage', 'first_reading'),
            'actions': [
                {
                    'date': datetime.now().isoformat(),
                    'action': 'Bill introduced and uploaded',
                    'actor': document['uploaded_by']
                }
            ],
            'committees': [],
            'votes': [],
            'amendments': [],
            'created_at': datetime.now().isoformat()
        }
        
        data = self.load_data()
        data['legislative_tracking'].append(tracking_record)
        self.save_data(data)
    
    def process_budget_document(self, document: Dict):
        """Process budget document"""
        
        # Special handling for budget documents
        # Could include automatic categorization, financial data extraction, etc.
        pass
    
    def process_contract_agreement(self, document: Dict):
        """Process contract agreement"""
        
        # Special handling for contracts
        # Could include vendor tracking, contract value monitoring, etc.
        pass
    
    def search_documents(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search documents by query and filters"""
        
        try:
            data = self.load_data()
            search_results = []
            
            # Simple keyword search using search index
            query_words = query.lower().split()
            matching_document_ids = set()
            
            for word in query_words:
                if word in data.get('search_index', {}):
                    matching_document_ids.update(data['search_index'][word])
            
            # Get matching documents
            for document in data['documents']:
                if document['id'] in matching_document_ids:
                    # Apply filters if provided
                    if self.document_matches_filters(document, filters):
                        search_results.append(document)
            
            # Sort by relevance (simple scoring based on title matches)
            search_results.sort(key=lambda d: self.calculate_relevance_score(d, query), reverse=True)
            
            return search_results[:50]  # Limit to 50 results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def document_matches_filters(self, document: Dict, filters: Dict) -> bool:
        """Check if document matches provided filters"""
        
        if not filters:
            return True
        
        # Check type filter
        if filters.get('type') and filters['type'] != 'All Types':
            if document['type'] != filters['type']:
                return False
        
        # Check classification filter
        if filters.get('classification') and filters['classification'] != 'All Classifications':
            if document['classification'] != filters['classification']:
                return False
        
        # Check jurisdiction filter
        if filters.get('jurisdiction') and filters['jurisdiction'] != 'All Jurisdictions':
            if document['jurisdiction'] != filters['jurisdiction']:
                return False
        
        # Check public access filter
        if filters.get('public_access_only') and not document.get('public_access'):
            return False
        
        return True
    
    def calculate_relevance_score(self, document: Dict, query: str) -> float:
        """Calculate relevance score for search result"""
        
        score = 0.0
        query_lower = query.lower()
        
        # Title match gets highest score
        if query_lower in document['title'].lower():
            score += 10.0
        
        # Description match gets medium score
        if query_lower in document['description'].lower():
            score += 5.0
        
        # Tag match gets medium score
        for tag in document.get('tags', []):
            if query_lower in tag.lower():
                score += 3.0
        
        # Department/author match gets low score
        if query_lower in document.get('department', '').lower():
            score += 1.0
        
        if query_lower in document.get('author', '').lower():
            score += 1.0
        
        return score
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document by ID"""
        
        try:
            data = self.load_data()
            
            for document in data['documents']:
                if document['id'] == document_id:
                    # Update access count and last accessed
                    document['metadata']['access_count'] += 1
                    document['metadata']['last_accessed'] = datetime.now().isoformat()
                    
                    # Record access on blockchain
                    try:
                        Blockchain.add_page(
                            action_type="document_accessed",
                            data={
                                'document_id': document_id,
                                'title': document['title'],
                                'access_timestamp': document['metadata']['last_accessed']
                            },
                            user_email="system"  # Could be actual user if provided
                        )
                    except Exception as e:
                        print(f"Warning: Failed to record document access on blockchain: {e}")
                    
                    self.save_data(data)
                    return document
            
            return None
            
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    def create_new_version(self, document_id: str, new_file_path: str, changes_description: str, modified_by: str) -> Tuple[bool, str]:
        """Create new version of existing document"""
        
        try:
            document = self.get_document(document_id)
            if not document:
                return False, "Document not found"
            
            # Calculate new file hash
            new_file_hash = self.calculate_file_hash(new_file_path)
            
            # Check if this is actually a new version
            if new_file_hash == document['file_info']['file_hash']:
                return False, "File content is identical to current version"
            
            # Generate new version number
            current_version = document['metadata']['version']
            version_parts = current_version.split('.')
            new_minor = int(version_parts[1]) + 1
            new_version = f"{version_parts[0]}.{new_minor}"
            
            # Store new version file
            file_extension = os.path.splitext(new_file_path)[1]
            versioned_filename = f"{document_id}_v{new_version}{file_extension}"
            storage_subdir = self.get_storage_subdirectory(document['classification'])
            versioned_path = os.path.join(self.storage_path, 'versions', versioned_filename)
            
            shutil.copy2(new_file_path, versioned_path)
            
            # Create version record
            version_record = {
                'id': str(uuid.uuid4()),
                'document_id': document_id,
                'version_number': new_version,
                'created_at': datetime.now().isoformat(),
                'modified_by': modified_by,
                'changes_description': changes_description,
                'file_hash': new_file_hash,
                'file_size': os.path.getsize(versioned_path),
                'stored_path': versioned_path
            }
            
            # Update document with new version info
            document['metadata']['version'] = new_version
            document['metadata']['last_modified'] = datetime.now().isoformat()
            document['file_info']['file_hash'] = new_file_hash
            document['file_info']['file_size'] = version_record['file_size']
            
            # Save version record and update document
            self.save_version(version_record)
            self.save_document(document, update=True)
            
            # Record version creation on blockchain
            try:
                Blockchain.add_page(
                    action_type="document_version_created",
                    data={
                        'document_id': document_id,
                        'version': new_version,
                        'modified_by': modified_by,
                        'changes': changes_description
                    },
                    user_email=modified_by
                )
            except Exception as e:
                print(f"Warning: Failed to record version creation on blockchain: {e}")
            
            return True, f"New version {new_version} created successfully"
            
        except Exception as e:
            return False, f"Error creating new version: {e}"
    
    def get_document_versions(self, document_id: str) -> List[Dict]:
        """Get all versions of a document"""
        
        try:
            data = self.load_data()
            
            versions = [v for v in data.get('document_versions', []) if v['document_id'] == document_id]
            versions.sort(key=lambda v: v['created_at'], reverse=True)
            
            return versions
            
        except Exception as e:
            print(f"Error getting document versions: {e}")
            return []
    
    def get_documents_by_type(self, document_type: str) -> List[Dict]:
        """Get all documents of a specific type"""
        
        try:
            data = self.load_data()
            
            return [d for d in data['documents'] if d['type'] == document_type]
            
        except Exception as e:
            print(f"Error getting documents by type: {e}")
            return []
    
    def get_public_documents(self) -> List[Dict]:
        """Get all publicly accessible documents"""
        
        try:
            data = self.load_data()
            
            return [d for d in data['documents'] if d.get('public_access', False)]
            
        except Exception as e:
            print(f"Error getting public documents: {e}")
            return []
    
    def save_document(self, document: Dict, update: bool = False):
        """Save document to database"""
        
        try:
            data = self.load_data()
            
            if update:
                # Update existing document
                for i, existing_doc in enumerate(data['documents']):
                    if existing_doc['id'] == document['id']:
                        data['documents'][i] = document
                        break
            else:
                # Add new document
                data['documents'].append(document)
            
            self.save_data(data)
            
        except Exception as e:
            print(f"Error saving document: {e}")
    
    def save_version(self, version_record: Dict):
        """Save version record to database"""
        
        try:
            data = self.load_data()
            
            if 'document_versions' not in data:
                data['document_versions'] = []
            
            data['document_versions'].append(version_record)
            self.save_data(data)
            
        except Exception as e:
            print(f"Error saving version record: {e}")
    
    def load_data(self) -> Dict:
        """Load documents database"""
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.ensure_database()
            return self.load_data()
        except json.JSONDecodeError:
            self.ensure_database()
            return self.load_data()
    
    def save_data(self, data: Dict):
        """Save documents database"""
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving documents data: {e}")


class FOIARequestProcessor:
    """Freedom of Information Act request processing system"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('documents_db_path', 'documents/documents_db.json')
        self.processing_timeframes = self.load_processing_timeframes()
    
    def load_processing_timeframes(self) -> Dict[str, int]:
        """Load FOIA processing timeframes by request type"""
        
        return {
            'simple_request': 20,      # Business days
            'complex_request': 30,     # Business days
            'voluminous_request': 45,  # Business days
            'consultation_required': 60, # Business days
            'expedited_request': 10    # Business days
        }
    
    def submit_request(self, request_data: Dict) -> Tuple[bool, str]:
        """Submit new FOIA request"""
        
        try:
            # Validate request data
            validation_result = self.validate_foia_request(request_data)
            if not validation_result['valid']:
                return False, f"Validation failed: {validation_result['errors']}"
            
            # Generate request ID
            request_id = self.generate_foia_request_id()
            
            # Classify request complexity
            complexity = self.classify_request_complexity(request_data)
            
            # Calculate due date
            due_date = self.calculate_due_date(complexity)
            
            # Create FOIA request record
            foia_request = {
                'id': str(uuid.uuid4()),
                'request_id': request_id,
                'requester_info': {
                    'name': request_data['requester_name'],
                    'email': request_data['requester_email'],
                    'phone': request_data.get('requester_phone', ''),
                    'address': request_data.get('requester_address', '')
                },
                'request_details': {
                    'subject': request_data['subject'],
                    'description': request_data['description'],
                    'date_range_start': request_data.get('date_range_start'),
                    'date_range_end': request_data.get('date_range_end'),
                    'department': request_data.get('department', ''),
                    'delivery_method': request_data.get('delivery_method', 'Electronic (Email)'),
                    'format_preference': request_data.get('format_preference', 'Digital Copy (PDF)')
                },
                'processing_info': {
                    'status': 'received',
                    'complexity': complexity,
                    'estimated_hours': self.estimate_processing_hours(request_data),
                    'estimated_cost': 0.0,  # Will be calculated during processing
                    'assigned_processor': None,
                    'priority': 'normal'
                },
                'timeline': {
                    'submitted_date': datetime.now().isoformat(),
                    'acknowledgment_date': datetime.now().isoformat(),
                    'due_date': due_date.isoformat(),
                    'estimated_completion': due_date.isoformat(),
                    'actual_completion': None
                },
                'documents_found': [],
                'exemptions_applied': [],
                'processing_log': [
                    {
                        'date': datetime.now().isoformat(),
                        'action': 'Request submitted and acknowledged',
                        'processor': 'system',
                        'notes': 'Automatic acknowledgment'
                    }
                ],
                'communications': [],
                'appeals': [],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'submitted_by': request_data.get('submitted_by', 'public')
                }
            }
            
            # Save FOIA request
            self.save_foia_request(foia_request)
            
            # Record FOIA submission on blockchain
            try:
                Blockchain.add_page(
                    action_type="foia_request_submitted",
                    data={
                        'request_id': request_id,
                        'subject': request_data['subject'],
                        'requester': request_data['requester_name'],
                        'complexity': complexity,
                        'due_date': due_date.isoformat()
                    },
                    user_email=request_data.get('submitted_by', 'public')
                )
            except Exception as e:
                print(f"Warning: Failed to record FOIA request on blockchain: {e}")
            
            # Send acknowledgment (in real implementation, send email)
            self.send_acknowledgment(foia_request)
            
            return True, request_id
            
        except Exception as e:
            return False, f"Error submitting FOIA request: {e}"
    
    def validate_foia_request(self, request_data: Dict) -> Dict:
        """Validate FOIA request data"""
        
        errors = []
        
        # Required fields
        required_fields = ['requester_name', 'requester_email', 'subject', 'description']
        for field in required_fields:
            if not request_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate email format
        if request_data.get('requester_email'):
            email = request_data['requester_email']
            if '@' not in email or '.' not in email.split('@')[1]:
                errors.append("Invalid email format")
        
        # Validate date range
        if request_data.get('date_range_start') and request_data.get('date_range_end'):
            try:
                start_date = datetime.fromisoformat(request_data['date_range_start'])
                end_date = datetime.fromisoformat(request_data['date_range_end'])
                if start_date > end_date:
                    errors.append("Start date cannot be after end date")
            except ValueError:
                errors.append("Invalid date format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def generate_foia_request_id(self) -> str:
        """Generate unique FOIA request ID"""
        
        year = datetime.now().year
        
        try:
            data = self.load_data()
            foia_requests = data.get('foia_requests', [])
            
            # Count requests for current year
            year_requests = [r for r in foia_requests if r['timeline']['submitted_date'].startswith(str(year))]
            next_number = len(year_requests) + 1
            
            return f"FOIA-{year}-{next_number:03d}"
            
        except Exception as e:
            print(f"Error generating FOIA request ID: {e}")
            return f"FOIA-{year}-001"
    
    def classify_request_complexity(self, request_data: Dict) -> str:
        """Classify FOIA request complexity"""
        
        description = request_data['description'].lower()
        
        # Simple heuristics for classification
        if len(description) < 100:
            return 'simple_request'
        elif 'email' in description or 'correspondence' in description:
            return 'complex_request'
        elif 'all documents' in description or 'comprehensive' in description:
            return 'voluminous_request'
        elif any(dept in description for dept in ['legal', 'law enforcement', 'confidential']):
            return 'consultation_required'
        else:
            return 'complex_request'
    
    def calculate_due_date(self, complexity: str) -> datetime:
        """Calculate FOIA request due date"""
        
        business_days = self.processing_timeframes.get(complexity, 30)
        
        # Calculate business days (excluding weekends)
        current_date = datetime.now()
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                days_added += 1
        
        return current_date
    
    def estimate_processing_hours(self, request_data: Dict) -> float:
        """Estimate processing hours for FOIA request"""
        
        base_hours = 2.0  # Base processing time
        
        description_length = len(request_data['description'])
        if description_length > 200:
            base_hours += 2.0
        
        if request_data.get('date_range_start') and request_data.get('date_range_end'):
            try:
                start_date = datetime.fromisoformat(request_data['date_range_start'])
                end_date = datetime.fromisoformat(request_data['date_range_end'])
                days_range = (end_date - start_date).days
                if days_range > 365:
                    base_hours += 4.0
                elif days_range > 30:
                    base_hours += 2.0
            except ValueError:
                pass
        
        return base_hours
    
    def send_acknowledgment(self, foia_request: Dict):
        """Send acknowledgment to requester"""
        
        # In real implementation, this would send an email
        print(f"FOIA acknowledgment sent to {foia_request['requester_info']['email']}")
        print(f"Request ID: {foia_request['request_id']}")
        print(f"Due date: {foia_request['timeline']['due_date']}")
    
    def process_foia_request(self, request_id: str, processor_email: str) -> Tuple[bool, str]:
        """Process FOIA request - search for documents and prepare response"""
        
        try:
            foia_request = self.get_foia_request(request_id)
            if not foia_request:
                return False, "FOIA request not found"
            
            # Update status to processing
            foia_request['processing_info']['status'] = 'processing'
            foia_request['processing_info']['assigned_processor'] = processor_email
            
            # Add processing log entry
            foia_request['processing_log'].append({
                'date': datetime.now().isoformat(),
                'action': 'Processing started',
                'processor': processor_email,
                'notes': 'Document search and review initiated'
            })
            
            # Search for responsive documents
            search_results = self.search_responsive_documents(foia_request)
            foia_request['documents_found'] = search_results
            
            # Apply exemptions if necessary
            exemptions = self.apply_exemptions(search_results, foia_request)
            foia_request['exemptions_applied'] = exemptions
            
            # Calculate final cost
            final_cost = self.calculate_processing_cost(foia_request)
            foia_request['processing_info']['estimated_cost'] = final_cost
            
            # Update status based on results
            if len(search_results) == 0:
                foia_request['processing_info']['status'] = 'no_records_found'
            elif final_cost > 0:
                foia_request['processing_info']['status'] = 'pending_payment'
            else:
                foia_request['processing_info']['status'] = 'ready_for_release'
            
            foia_request['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save updated request
            self.save_foia_request(foia_request, update=True)
            
            # Record processing on blockchain
            try:
                Blockchain.add_page(
                    action_type="foia_request_processed",
                    data={
                        'request_id': request_id,
                        'processor': processor_email,
                        'documents_found': len(search_results),
                        'status': foia_request['processing_info']['status']
                    },
                    user_email=processor_email
                )
            except Exception as e:
                print(f"Warning: Failed to record FOIA processing on blockchain: {e}")
            
            return True, f"FOIA request processed. Status: {foia_request['processing_info']['status']}"
            
        except Exception as e:
            return False, f"Error processing FOIA request: {e}"
    
    def search_responsive_documents(self, foia_request: Dict) -> List[Dict]:
        """Search for documents responsive to FOIA request"""
        
        # This would integrate with DocumentManager to search documents
        # For now, return mock results
        
        return [
            {
                'document_id': 'doc-123',
                'title': 'Sample Document',
                'relevance_score': 0.8,
                'exemptions_applicable': [],
                'pages': 5
            }
        ]
    
    def apply_exemptions(self, documents: List[Dict], foia_request: Dict) -> List[Dict]:
        """Apply FOIA exemptions to responsive documents"""
        
        # Mock exemption application
        # In real implementation, this would analyze documents for applicable exemptions
        
        exemptions = []
        
        for doc in documents:
            # Example exemption logic
            if 'confidential' in doc['title'].lower():
                exemptions.append({
                    'document_id': doc['document_id'],
                    'exemption': '5 USC 552(b)(5)',
                    'description': 'Deliberative process privilege',
                    'pages_withheld': 2
                })
        
        return exemptions
    
    def calculate_processing_cost(self, foia_request: Dict) -> float:
        """Calculate FOIA processing cost"""
        
        # Basic cost calculation
        base_cost = 0.0
        
        processing_hours = foia_request['processing_info']['estimated_hours']
        documents_found = len(foia_request['documents_found'])
        
        # Fee schedule (example rates)
        if processing_hours > 2:
            base_cost += (processing_hours - 2) * 25.00  # $25/hour after first 2 hours
        
        if documents_found > 10:
            base_cost += (documents_found - 10) * 0.25  # $0.25 per page after first 10 pages
        
        return round(base_cost, 2)
    
    def get_foia_request(self, request_id: str) -> Optional[Dict]:
        """Get FOIA request by request ID"""
        
        try:
            data = self.load_data()
            
            for request in data.get('foia_requests', []):
                if request['request_id'] == request_id:
                    return request
            
            return None
            
        except Exception as e:
            print(f"Error getting FOIA request: {e}")
            return None
    
    def save_foia_request(self, foia_request: Dict, update: bool = False):
        """Save FOIA request to database"""
        
        try:
            data = self.load_data()
            
            if 'foia_requests' not in data:
                data['foia_requests'] = []
            
            if update:
                # Update existing request
                for i, existing_request in enumerate(data['foia_requests']):
                    if existing_request['id'] == foia_request['id']:
                        data['foia_requests'][i] = foia_request
                        break
            else:
                # Add new request
                data['foia_requests'].append(foia_request)
            
            self.save_data(data)
            
        except Exception as e:
            print(f"Error saving FOIA request: {e}")
    
    def load_data(self) -> Dict:
        """Load documents database"""
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Initialize if doesn't exist
            return {'foia_requests': []}
        except json.JSONDecodeError:
            return {'foia_requests': []}
    
    def save_data(self, data: Dict):
        """Save documents database"""
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving FOIA data: {e}")


# Export the main classes
__all__ = ['DocumentManager', 'FOIARequestProcessor']