"""
Document Manager Backend - Democratic Transparency & Records Management
Handles official document management, public records, and transparency requirements.
Supports comprehensive document management with version control and access logging.
"""

import json
import hashlib
import datetime
import os
import uuid
import shutil
import mimetypes
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DocumentCategory(Enum):
    """Document categories for organization"""
    LEGISLATIVE = "legislative"
    JUDICIAL = "judicial"
    EXECUTIVE = "executive" 
    CONSTITUTIONAL = "constitutional"
    BUDGET_FINANCIAL = "budget_financial"
    CONTRACTS_AGREEMENTS = "contracts_agreements"
    PUBLIC_RECORDS = "public_records"
    MEETING_MINUTES = "meeting_minutes"
    REPORTS_STUDIES = "reports_studies"
    CORRESPONDENCE = "correspondence"

class AccessLevel(Enum):
    """Document access classification levels"""
    PUBLIC = 0          # Publicly accessible
    RESTRICTED = 1      # Requires authentication
    CONFIDENTIAL = 2    # Special permissions required
    CLASSIFIED = 3      # Highest security level

class DocumentStatus(Enum):
    """Document lifecycle status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    CLASSIFIED = "classified"

@dataclass
class DocumentVersion:
    """Individual document version with metadata"""
    version_id: str
    version_number: str
    file_path: str
    file_hash: str
    created_at: str
    created_by: str
    changes_summary: str
    file_size: int

class DocumentManager:
    """
    Comprehensive document management and archive system
    Supports transparency requirements and official record keeping
    """
    
    def __init__(self):
        """Initialize document management system with database and storage"""
        self.db_path = self._get_db_path()
        self.storage_path = self._get_storage_path()
        self.data = self._load_data()
        self._ensure_storage_directories()
        
    def _get_db_path(self) -> str:
        """Get environment-specific database path"""
        try:
            from civic_desktop.main import ENV_CONFIG
            return ENV_CONFIG.get('documents_db_path', 'civic_desktop/documents/documents_db.json')
        except:
            return 'civic_desktop/documents/documents_db.json'
    
    def _get_storage_path(self) -> str:
        """Get document storage directory path"""
        try:
            from civic_desktop.main import ENV_CONFIG
            return ENV_CONFIG.get('documents_storage_path', 'civic_desktop/documents/storage')
        except:
            return 'civic_desktop/documents/storage'
    
    def _load_data(self) -> Dict[str, Any]:
        """Load documents data from JSON database"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_structure()
        except Exception as e:
            print(f"Error loading documents data: {e}")
            return self._create_default_structure()
    
    def _create_default_structure(self) -> Dict[str, Any]:
        """Create default documents database structure"""
        return {
            "documents": [],
            "collections": [],
            "access_logs": [],
            "foia_requests": [],
            "settings": {
                "document_categories": [cat.value for cat in DocumentCategory],
                "classification_levels": {
                    "public": {"description": "Publicly accessible", "access_level": 0},
                    "restricted": {"description": "Authentication required", "access_level": 1},
                    "confidential": {"description": "Special permissions", "access_level": 2},
                    "classified": {"description": "Highest security", "access_level": 3}
                },
                "retention_policies": {
                    "permanent": "Permanent retention",
                    "long_term": "50+ years retention",
                    "medium_term": "10-50 years retention", 
                    "short_term": "1-10 years retention"
                },
                "transparency_settings": {
                    "automatic_disclosure": True,
                    "foia_processing_days": 20,
                    "public_portal_enabled": True,
                    "audit_trail_required": True
                }
            }
        }
    
    def _save_data(self) -> bool:
        """Save documents data to JSON database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving documents data: {e}")
            return False
    
    def _ensure_storage_directories(self):
        """Ensure document storage directories exist"""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Create category subdirectories
            for category in DocumentCategory:
                category_path = os.path.join(self.storage_path, category.value)
                os.makedirs(category_path, exist_ok=True)
                
        except Exception as e:
            print(f"Error creating storage directories: {e}")
    
    def _log_to_blockchain(self, action_type: str, data: Dict[str, Any], user_email: str):
        """Log document actions to blockchain for transparency"""
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            Blockchain.add_page(action_type, data, user_email)
        except Exception as e:
            print(f"Blockchain logging error: {e}")
    
    def upload_document(self, uploader_email: str, title: str, description: str,
                       category: str, classification: str, file_path: str,
                       metadata: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Upload new document with metadata and version control"""
        try:
            # Validate inputs
            if not all([uploader_email, title, category, file_path]):
                return False, "Missing required document information"
            
            # Validate uploader permissions
            if not self._validate_uploader(uploader_email, classification):
                return False, "Insufficient permissions to upload documents at this classification level"
            
            # Validate file
            if not os.path.exists(file_path):
                return False, "Source file does not exist"
            
            # Generate document ID and storage paths
            doc_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file_path)[1]
            
            # Create storage structure
            storage_dir = os.path.join(
                self.storage_path, 
                category.lower().replace(' ', '_'),
                doc_id
            )
            os.makedirs(storage_dir, exist_ok=True)
            
            # Copy file to storage with version
            version_id = str(uuid.uuid4())
            stored_file_path = os.path.join(storage_dir, f"v1{file_extension}")
            shutil.copy2(file_path, stored_file_path)
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(stored_file_path)
            file_size = os.path.getsize(stored_file_path)
            
            # Get file mime type
            mime_type, _ = mimetypes.guess_type(stored_file_path)
            
            # Create document record
            document_data = {
                'id': doc_id,
                'title': title,
                'description': description,
                'category': category,
                'classification': classification,
                'status': DocumentStatus.DRAFT.value,
                'uploader_email': uploader_email,
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat(),
                'current_version': '1.0',
                'mime_type': mime_type,
                'metadata': metadata or {},
                'versions': [
                    {
                        'version_id': version_id,
                        'version_number': '1.0',
                        'file_path': stored_file_path,
                        'file_hash': file_hash,
                        'created_at': datetime.datetime.now().isoformat(),
                        'created_by': uploader_email,
                        'changes_summary': 'Initial upload',
                        'file_size': file_size
                    }
                ],
                'access_history': [],
                'tags': [],
                'retention_policy': self._determine_retention_policy(category),
                'digital_signature': None,
                'approval_chain': [],
                'public_access': classification == 'public'
            }
            
            # Automatic classification review
            auto_review = self._automatic_classification_review(
                title, description, category, classification
            )
            document_data['classification_review'] = auto_review
            
            # Add to database
            self.data['documents'].append(document_data)
            self._save_data()
            
            # Log to blockchain
            self._log_to_blockchain(
                "document_uploaded",
                {
                    'document_id': doc_id,
                    'title': title,
                    'category': category,
                    'classification': classification,
                    'file_hash': file_hash
                },
                uploader_email
            )
            
            return True, f"Document uploaded successfully with ID: {doc_id}"
            
        except Exception as e:
            return False, f"Error uploading document: {str(e)}"
    
    def get_documents(self, category_filter: Optional[str] = None,
                     classification_filter: Optional[str] = None,
                     status_filter: Optional[str] = None,
                     requester_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get documents with filtering and access control"""
        try:
            documents = self.data.get('documents', [])
            
            # Apply access control filtering
            accessible_docs = []
            for doc in documents:
                if self._can_access_document(doc, requester_email):
                    accessible_docs.append(doc)
            
            # Apply filters
            if category_filter and category_filter != "All Categories":
                accessible_docs = [d for d in accessible_docs 
                                 if d.get('category', '').lower() == category_filter.lower()]
            
            if classification_filter and classification_filter != "All Classifications":
                accessible_docs = [d for d in accessible_docs 
                                 if d.get('classification', '').lower() == classification_filter.lower()]
            
            if status_filter and status_filter != "All Status":
                accessible_docs = [d for d in accessible_docs 
                                 if d.get('status', '').lower() == status_filter.lower()]
            
            # Sort by updated date, newest first
            return sorted(accessible_docs, key=lambda x: x.get('updated_at', ''), reverse=True)
            
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def search_documents(self, query: str, requester_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """Full-text search across documents with access control"""
        try:
            documents = self.get_documents(requester_email=requester_email)
            
            if not query.strip():
                return documents
            
            query_lower = query.lower()
            matching_docs = []
            
            for doc in documents:
                # Search in title, description, and metadata
                searchable_text = ' '.join([
                    doc.get('title', ''),
                    doc.get('description', ''),
                    str(doc.get('metadata', {})),
                    ' '.join(doc.get('tags', []))
                ]).lower()
                
                if query_lower in searchable_text:
                    # Calculate relevance score (simple)
                    title_matches = doc.get('title', '').lower().count(query_lower)
                    desc_matches = doc.get('description', '').lower().count(query_lower)
                    
                    doc['_search_score'] = (title_matches * 3) + (desc_matches * 2) + 1
                    matching_docs.append(doc)
            
            # Sort by relevance score
            return sorted(matching_docs, key=lambda x: x.get('_search_score', 0), reverse=True)
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def access_document(self, document_id: str, accessor_email: str) -> Tuple[bool, str, Optional[str]]:
        """Access a document with logging and permission checking"""
        try:
            document = self._find_document_by_id(document_id)
            if not document:
                return False, "Document not found", None
            
            # Check access permissions
            if not self._can_access_document(document, accessor_email):
                # Log access attempt
                self._log_access_attempt(document_id, accessor_email, False, "Access denied")
                return False, "Access denied - insufficient permissions", None
            
            # Get current version file path
            versions = document.get('versions', [])
            if not versions:
                return False, "No document versions available", None
            
            current_version = versions[-1]  # Latest version
            file_path = current_version.get('file_path', '')
            
            if not os.path.exists(file_path):
                return False, "Document file not found in storage", None
            
            # Log successful access
            self._log_access_attempt(document_id, accessor_email, True, "Document accessed")
            
            # Update access history
            document.setdefault('access_history', []).append({
                'accessed_by': accessor_email,
                'accessed_at': datetime.datetime.now().isoformat(),
                'version_accessed': current_version.get('version_number', '1.0'),
                'access_method': 'direct_download'
            })
            self._save_data()
            
            # Log to blockchain
            self._log_to_blockchain(
                "document_accessed",
                {
                    'document_id': document_id,
                    'title': document.get('title', ''),
                    'classification': document.get('classification', ''),
                    'version': current_version.get('version_number', '1.0')
                },
                accessor_email
            )
            
            return True, "Access granted", file_path
            
        except Exception as e:
            return False, f"Error accessing document: {str(e)}", None
    
    def create_new_version(self, document_id: str, editor_email: str, 
                          file_path: str, changes_summary: str) -> Tuple[bool, str]:
        """Create new version of existing document"""
        try:
            document = self._find_document_by_id(document_id)
            if not document:
                return False, "Document not found"
            
            # Check edit permissions
            if not self._can_edit_document(document, editor_email):
                return False, "Insufficient permissions to edit document"
            
            # Validate file
            if not os.path.exists(file_path):
                return False, "New version file does not exist"
            
            # Calculate next version number
            versions = document.get('versions', [])
            current_version = float(versions[-1]['version_number']) if versions else 0.0
            new_version_number = f"{current_version + 0.1:.1f}"
            
            # Get document storage directory
            category = document.get('category', '').lower().replace(' ', '_')
            storage_dir = os.path.join(self.storage_path, category, document_id)
            
            # Store new version
            version_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file_path)[1]
            stored_file_path = os.path.join(
                storage_dir, 
                f"v{new_version_number.replace('.', '_')}{file_extension}"
            )
            
            shutil.copy2(file_path, stored_file_path)
            
            # Calculate file hash and size
            file_hash = self._calculate_file_hash(stored_file_path)
            file_size = os.path.getsize(stored_file_path)
            
            # Create version record
            version_data = {
                'version_id': version_id,
                'version_number': new_version_number,
                'file_path': stored_file_path,
                'file_hash': file_hash,
                'created_at': datetime.datetime.now().isoformat(),
                'created_by': editor_email,
                'changes_summary': changes_summary,
                'file_size': file_size
            }
            
            # Add version to document
            document['versions'].append(version_data)
            document['current_version'] = new_version_number
            document['updated_at'] = datetime.datetime.now().isoformat()
            
            self._save_data()
            
            # Log to blockchain
            self._log_to_blockchain(
                "document_modified",
                {
                    'document_id': document_id,
                    'new_version': new_version_number,
                    'changes_summary': changes_summary,
                    'file_hash': file_hash
                },
                editor_email
            )
            
            return True, f"New version {new_version_number} created successfully"
            
        except Exception as e:
            return False, f"Error creating new version: {str(e)}"
    
    def submit_foia_request(self, requester_email: str, request_description: str,
                           document_keywords: List[str], 
                           date_range: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """Submit Freedom of Information Act request"""
        try:
            # Validate requester
            if not self._validate_foia_requester(requester_email):
                return False, "Invalid requester - must be authenticated citizen"
            
            # Create FOIA request
            request_id = str(uuid.uuid4())
            request_data = {
                'id': request_id,
                'requester_email': requester_email,
                'description': request_description,
                'keywords': document_keywords,
                'date_range': date_range or {},
                'status': 'submitted',
                'submitted_at': datetime.datetime.now().isoformat(),
                'processing_deadline': self._calculate_foia_deadline(),
                'assigned_to': None,
                'response_documents': [],
                'processing_notes': [],
                'fee_estimate': 0.0,
                'exemptions_claimed': []
            }
            
            # Add to database
            self.data['foia_requests'].append(request_data)
            self._save_data()
            
            # Auto-assign if possible
            self._auto_assign_foia_request(request_id)
            
            # Log to blockchain
            self._log_to_blockchain(
                "foia_request",
                {
                    'request_id': request_id,
                    'description': request_description[:100],
                    'keywords': document_keywords
                },
                requester_email
            )
            
            return True, f"FOIA request submitted with ID: {request_id}"
            
        except Exception as e:
            return False, f"Error submitting FOIA request: {str(e)}"
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """Get comprehensive document system statistics"""
        documents = self.data.get('documents', [])
        access_logs = self.data.get('access_logs', [])
        foia_requests = self.data.get('foia_requests', [])
        
        # Calculate statistics
        stats = {
            'total_documents': len(documents),
            'documents_by_category': {},
            'documents_by_classification': {},
            'documents_by_status': {},
            'total_versions': 0,
            'storage_usage': self._calculate_storage_usage(),
            'access_trends': self._calculate_access_trends(),
            'foia_statistics': {
                'total_requests': len(foia_requests),
                'pending_requests': len([r for r in foia_requests if r.get('status') == 'submitted']),
                'processed_requests': len([r for r in foia_requests if r.get('status') == 'completed']),
                'average_processing_time': self._calculate_avg_processing_time()
            },
            'transparency_metrics': self._calculate_transparency_metrics()
        }
        
        # Group documents by category
        for doc in documents:
            category = doc.get('category', 'Unknown')
            stats['documents_by_category'][category] = stats['documents_by_category'].get(category, 0) + 1
        
        # Group by classification
        for doc in documents:
            classification = doc.get('classification', 'Unknown')
            stats['documents_by_classification'][classification] = stats['documents_by_classification'].get(classification, 0) + 1
        
        # Group by status
        for doc in documents:
            status = doc.get('status', 'Unknown')
            stats['documents_by_status'][status] = stats['documents_by_status'].get(status, 0) + 1
        
        # Count total versions
        stats['total_versions'] = sum(len(doc.get('versions', [])) for doc in documents)
        
        return stats
    
    def _validate_uploader(self, uploader_email: str, classification: str) -> bool:
        """Validate if user can upload documents at given classification level"""
        try:
            from civic_desktop.users.session import SessionManager
            
            if not SessionManager.is_authenticated():
                return False
            
            user = SessionManager.get_current_user()
            if not user or user.get('email') != uploader_email:
                return False
            
            # Check role-based permissions for classification levels
            user_role = user.get('role', 'Contract Citizen')
            
            classification_permissions = {
                'public': ['Contract Citizen', 'Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'],
                'restricted': ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'],
                'confidential': ['Contract Senator', 'Contract Elder', 'Contract Founder'],
                'classified': ['Contract Elder', 'Contract Founder']
            }
            
            allowed_roles = classification_permissions.get(classification.lower(), [])
            return user_role in allowed_roles
            
        except:
            return False
    
    def _can_access_document(self, document: Dict[str, Any], requester_email: Optional[str]) -> bool:
        """Check if user can access document based on classification"""
        try:
            classification = document.get('classification', 'public').lower()
            
            # Public documents accessible to everyone
            if classification == 'public':
                return True
            
            # Other classifications require authentication
            if not requester_email:
                return False
            
            from civic_desktop.users.session import SessionManager
            
            if not SessionManager.is_authenticated():
                return False
            
            user = SessionManager.get_current_user()
            if not user or user.get('email') != requester_email:
                return False
            
            # Check role-based access
            user_role = user.get('role', 'Contract Citizen')
            
            access_permissions = {
                'restricted': ['Contract Citizen', 'Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'],
                'confidential': ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'],
                'classified': ['Contract Senator', 'Contract Elder', 'Contract Founder']
            }
            
            allowed_roles = access_permissions.get(classification, [])
            return user_role in allowed_roles
            
        except:
            return False
    
    def _can_edit_document(self, document: Dict[str, Any], editor_email: str) -> bool:
        """Check if user can edit document"""
        try:
            from civic_desktop.users.session import SessionManager
            
            user = SessionManager.get_current_user()
            if not user or user.get('email') != editor_email:
                return False
            
            # Document creator can always edit (unless classified)
            if document.get('uploader_email') == editor_email and document.get('classification') != 'classified':
                return True
            
            # Role-based edit permissions
            user_role = user.get('role', 'Contract Citizen')
            classification = document.get('classification', 'public').lower()
            
            edit_permissions = {
                'public': ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'],
                'restricted': ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'],
                'confidential': ['Contract Senator', 'Contract Elder', 'Contract Founder'],
                'classified': ['Contract Elder', 'Contract Founder']
            }
            
            allowed_roles = edit_permissions.get(classification, [])
            return user_role in allowed_roles
            
        except:
            return False
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for integrity verification"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return ""
    
    def _determine_retention_policy(self, category: str) -> str:
        """Determine retention policy based on document category"""
        permanent_categories = ['constitutional', 'legislative', 'judicial']
        long_term_categories = ['contracts_agreements', 'budget_financial']
        
        if category.lower() in permanent_categories:
            return 'permanent'
        elif category.lower() in long_term_categories:
            return 'long_term'
        else:
            return 'medium_term'
    
    def _automatic_classification_review(self, title: str, description: str,
                                       category: str, classification: str) -> Dict[str, Any]:
        """Perform automatic classification review"""
        review = {
            'reviewed_at': datetime.datetime.now().isoformat(),
            'suggested_classification': classification,
            'confidence': 0.8,
            'flags': [],
            'recommendations': []
        }
        
        # Basic keyword-based classification checking
        sensitive_keywords = ['classified', 'confidential', 'secret', 'restricted']
        public_keywords = ['public', 'announcement', 'press release', 'minutes']
        
        content = f"{title} {description}".lower()
        
        for keyword in sensitive_keywords:
            if keyword in content and classification == 'public':
                review['flags'].append(f"Contains sensitive keyword '{keyword}' but classified as public")
                review['suggested_classification'] = 'restricted'
        
        for keyword in public_keywords:
            if keyword in content and classification in ['confidential', 'classified']:
                review['flags'].append(f"Contains public keyword '{keyword}' but highly classified")
        
        return review
    
    def _find_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        documents = self.data.get('documents', [])
        return next((d for d in documents if d['id'] == document_id), None)
    
    def _log_access_attempt(self, document_id: str, accessor_email: str, 
                           success: bool, reason: str):
        """Log document access attempt"""
        log_entry = {
            'id': str(uuid.uuid4()),
            'document_id': document_id,
            'accessor_email': accessor_email,
            'timestamp': datetime.datetime.now().isoformat(),
            'success': success,
            'reason': reason,
            'ip_address': None,  # Could be added for web access
            'user_agent': None   # Could be added for web access
        }
        
        self.data.setdefault('access_logs', []).append(log_entry)
        # Keep only recent logs (last 10000 entries)
        if len(self.data['access_logs']) > 10000:
            self.data['access_logs'] = self.data['access_logs'][-10000:]
    
    def _validate_foia_requester(self, requester_email: str) -> bool:
        """Validate FOIA request requester"""
        try:
            from civic_desktop.users.backend import UserBackend
            
            users = UserBackend().get_users()
            user = next((u for u in users if u.get('email') == requester_email), None)
            
            return user is not None  # Any registered user can submit FOIA requests
            
        except:
            return False
    
    def _calculate_foia_deadline(self) -> str:
        """Calculate FOIA processing deadline"""
        processing_days = self.data['settings']['transparency_settings']['foia_processing_days']
        deadline = datetime.datetime.now() + datetime.timedelta(days=processing_days)
        return deadline.isoformat()
    
    def _auto_assign_foia_request(self, request_id: str):
        """Auto-assign FOIA request to appropriate processor"""
        # Placeholder for automatic assignment logic
        # Would integrate with user roles and workload balancing
        pass
    
    def _calculate_storage_usage(self) -> Dict[str, Any]:
        """Calculate storage usage statistics"""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            return {
                'total_bytes': total_size,
                'total_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'storage_path': self.storage_path
            }
            
        except:
            return {'total_bytes': 0, 'total_mb': 0, 'file_count': 0}
    
    def _calculate_access_trends(self) -> Dict[str, Any]:
        """Calculate document access trends"""
        access_logs = self.data.get('access_logs', [])
        
        # Group access by date
        daily_access = {}
        for log in access_logs:
            try:
                date = datetime.datetime.fromisoformat(log['timestamp']).date().isoformat()
                daily_access[date] = daily_access.get(date, 0) + 1
            except:
                continue
        
        # Calculate trend
        if len(daily_access) < 2:
            trend = "insufficient_data"
        else:
            recent_avg = sum(list(daily_access.values())[-7:]) / min(7, len(daily_access))
            older_avg = sum(list(daily_access.values())[:-7]) / max(1, len(daily_access) - 7)
            
            if recent_avg > older_avg * 1.1:
                trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        
        return {
            'daily_access_counts': daily_access,
            'trend': trend,
            'total_accesses_last_30_days': sum(
                count for date, count in daily_access.items()
                if (datetime.datetime.now().date() - datetime.date.fromisoformat(date)).days <= 30
            )
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average FOIA processing time"""
        foia_requests = self.data.get('foia_requests', [])
        
        processing_times = []
        for request in foia_requests:
            if request.get('status') == 'completed':
                try:
                    submitted = datetime.datetime.fromisoformat(request['submitted_at'])
                    # Would need completed_at field - using placeholder
                    completed = submitted + datetime.timedelta(days=15)  # Placeholder
                    processing_time = (completed - submitted).days
                    processing_times.append(processing_time)
                except:
                    continue
        
        return sum(processing_times) / len(processing_times) if processing_times else 0.0
    
    def _calculate_transparency_metrics(self) -> Dict[str, Any]:
        """Calculate transparency and compliance metrics"""
        documents = self.data.get('documents', [])
        
        public_docs = len([d for d in documents if d.get('classification') == 'public'])
        total_docs = len(documents)
        
        transparency_ratio = (public_docs / total_docs * 100) if total_docs > 0 else 0
        
        # Automatic disclosure compliance
        auto_disclosure_enabled = self.data['settings']['transparency_settings']['automatic_disclosure']
        
        return {
            'transparency_ratio': round(transparency_ratio, 2),
            'public_documents': public_docs,
            'total_documents': total_docs,
            'automatic_disclosure_enabled': auto_disclosure_enabled,
            'compliance_score': min(100, transparency_ratio + (20 if auto_disclosure_enabled else 0))
        }