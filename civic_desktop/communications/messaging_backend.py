# Communications Backend - Secure Civic Messaging & Announcements System
"""
Communications backend providing:
- Direct messaging between citizens and representatives
- Official announcements with distribution management
- Group communications for committees and working groups
- Notification management with user preferences
- End-to-end encryption and message authenticity verification
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from civic_desktop.main import ENV_CONFIG
from civic_desktop.users.session import SessionManager
from civic_desktop.blockchain.blockchain import Blockchain
from civic_desktop.users.backend import UserBackend

class MessagingBackend:
    """Comprehensive secure messaging backend for civic communications"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('communications_db_path', 'civic_desktop/communications/messages_db.json')
        self.ensure_database_exists()
        self.user_backend = UserBackend()
    
    def ensure_database_exists(self):
        """Ensure messages database exists with proper structure"""
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            default_data = {
                'messages': [],
                'announcements': [],
                'group_chats': [],
                'notifications': [],
                'settings': {
                    'message_encryption': True,
                    'read_receipts_enabled': True,
                    'notification_sound': True,
                    'auto_archive_days': 90,
                    'max_message_length': 10000,
                    'file_upload_max_size': 10485760  # 10MB
                },
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'total_messages': 0,
                    'total_announcements': 0
                }
            }
            self.save_data(default_data)
    
    def load_data(self) -> Dict[str, Any]:
        """Load communications data from JSON database"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_database_exists()
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save communications data to JSON database"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving communications data: {e}")
            return False
    
    def generate_encryption_key(self, user_email: str, password: str = None) -> bytes:
        """Generate encryption key for user messages"""
        # Use user email and optional password for key derivation
        password_bytes = (password or user_email).encode()
        salt = user_email.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt_message(self, message: str, user_email: str) -> str:
        """Encrypt a message for secure storage"""
        try:
            key = self.generate_encryption_key(user_email)
            cipher_suite = Fernet(key)
            encrypted_message = cipher_suite.encrypt(message.encode())
            return base64.urlsafe_b64encode(encrypted_message).decode()
        except Exception as e:
            print(f"Error encrypting message: {e}")
            return message  # Fallback to plain text if encryption fails
    
    def decrypt_message(self, encrypted_message: str, user_email: str) -> str:
        """Decrypt a message for display"""
        try:
            key = self.generate_encryption_key(user_email)
            cipher_suite = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_message.encode())
            decrypted_message = cipher_suite.decrypt(encrypted_bytes)
            return decrypted_message.decode()
        except Exception as e:
            print(f"Error decrypting message: {e}")
            return encrypted_message  # Fallback to showing encrypted text
    
    def send_message(self, sender_email: str, recipient_email: str, subject: str, content: str, 
                    message_type: str = 'direct', priority: str = 'normal', 
                    attachments: List[str] = None) -> Tuple[bool, str]:
        """Send a secure message between users"""
        
        # Validate sender authentication
        if not SessionManager.is_authenticated():
            return False, "Authentication required to send messages"
        
        current_user = SessionManager.get_current_user()
        if current_user['email'] != sender_email:
            return False, "Cannot send messages on behalf of other users"
        
        # Validate recipient exists
        if not self.user_backend.user_exists(recipient_email):
            return False, f"Recipient {recipient_email} not found"
        
        # Create message
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Encrypt message content for privacy
        encrypted_content = self.encrypt_message(content, sender_email)
        
        message_data = {
            'id': message_id,
            'type': message_type,
            'sender_email': sender_email,
            'recipient_email': recipient_email,
            'subject': subject,
            'content': encrypted_content,
            'priority': priority,
            'attachments': attachments or [],
            'timestamp': timestamp,
            'read': False,
            'archived': False,
            'thread_id': None,  # For message threading
            'reply_to': None,   # For reply chains
            'status': 'sent'
        }
        
        # Save to database
        try:
            data = self.load_data()
            data['messages'].append(message_data)
            data['metadata']['total_messages'] += 1
            data['metadata']['last_updated'] = timestamp
            
            if self.save_data(data):
                # Record on blockchain for transparency (message hash only, not content)
                blockchain_data = {
                    'message_id': message_id,
                    'sender': sender_email,
                    'recipient': recipient_email,
                    'subject_hash': hash(subject),
                    'timestamp': timestamp,
                    'message_type': message_type,
                    'priority': priority
                }
                
                # Add action_type to blockchain data
                blockchain_data['action_type'] = "message_sent"
                Blockchain.add_page(blockchain_data, sender_email)
                
                # Create notification for recipient
                self.create_notification(
                    recipient_email,
                    'new_message',
                    f"New message from {sender_email}: {subject}",
                    {'message_id': message_id, 'sender': sender_email}
                )
                
                return True, f"Message sent successfully to {recipient_email}"
            else:
                return False, "Failed to save message to database"
                
        except Exception as e:
            print(f"Error sending message: {e}")
            return False, f"Error sending message: {str(e)}"
    
    def get_messages(self, user_email: str, message_type: str = None, 
                    unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get messages for a user with optional filtering"""
        try:
            data = self.load_data()
            messages = data.get('messages', [])
            
            # Filter messages for this user (sent or received)
            user_messages = [
                msg for msg in messages
                if msg['sender_email'] == user_email or msg['recipient_email'] == user_email
            ]
            
            # Apply additional filters
            if message_type:
                user_messages = [msg for msg in user_messages if msg.get('type') == message_type]
            
            if unread_only:
                user_messages = [msg for msg in user_messages if not msg.get('read', False)]
            
            # Decrypt message content for display
            for message in user_messages:
                try:
                    # Decrypt using sender's key for consistent decryption
                    sender_email = message['sender_email']
                    message['content'] = self.decrypt_message(message['content'], sender_email)
                except:
                    # If decryption fails, leave content encrypted
                    pass
            
            # Sort by timestamp (newest first)
            user_messages.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return user_messages
            
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []
    
    def mark_message_read(self, message_id: str, user_email: str) -> bool:
        """Mark a message as read"""
        try:
            data = self.load_data()
            messages = data.get('messages', [])
            
            for message in messages:
                if (message['id'] == message_id and 
                    message['recipient_email'] == user_email):
                    message['read'] = True
                    message['read_timestamp'] = datetime.now().isoformat()
                    
                    # Record read receipt on blockchain
                    # Create blockchain data for message read
                    read_data = {
                        'action_type': 'message_read',
                        'message_id': message_id,
                        'reader': user_email,
                        'timestamp': message['read_timestamp']
                    }
                    Blockchain.add_page(read_data, user_email)
                    
                    return self.save_data(data)
            
            return False
            
        except Exception as e:
            print(f"Error marking message as read: {e}")
            return False
    
    def create_official_announcement(self, sender_email: str, title: str, content: str,
                                  target_audience: List[str], announcement_type: str = 'general',
                                  priority: str = 'normal', expiry_date: str = None) -> Tuple[bool, str]:
        """Create an official announcement with distribution management"""
        
        # Verify sender has authority to make announcements
        current_user = SessionManager.get_current_user()
        if not current_user or current_user['email'] != sender_email:
            return False, "Authentication required"
        
        user_role = current_user.get('role', '')
        authorized_roles = ['Contract Elder', 'Contract Representative', 'Contract Senator', 
                           'Contract Founder', 'CEO', 'Admin']
        
        if user_role not in authorized_roles:
            return False, f"Role '{user_role}' not authorized to create official announcements"
        
        # Create announcement
        announcement_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        announcement_data = {
            'id': announcement_id,
            'type': announcement_type,
            'sender_email': sender_email,
            'sender_role': user_role,
            'title': title,
            'content': content,
            'target_audience': target_audience,
            'priority': priority,
            'timestamp': timestamp,
            'expiry_date': expiry_date,
            'views': [],
            'acknowledgments': [],
            'status': 'active'
        }
        
        try:
            data = self.load_data()
            data['announcements'].append(announcement_data)
            data['metadata']['total_announcements'] += 1
            data['metadata']['last_updated'] = timestamp
            
            if self.save_data(data):
                # Record on blockchain for transparency
                # Create blockchain data for announcement
                announcement_blockchain_data = {
                    'action_type': 'announcement_published',
                    'announcement_id': announcement_id,
                    'sender': sender_email,
                    'sender_role': user_role,
                    'title': title,
                    'target_audience': target_audience,
                    'timestamp': timestamp,
                    'priority': priority
                }
                Blockchain.add_page(announcement_blockchain_data, sender_email)
                
                # Create notifications for target audience
                for audience_member in target_audience:
                    if audience_member != sender_email:  # Don't notify sender
                        self.create_notification(
                            audience_member,
                            'official_announcement',
                            f"Official Announcement: {title}",
                            {
                                'announcement_id': announcement_id,
                                'sender': sender_email,
                                'priority': priority
                            }
                        )
                
                return True, f"Official announcement created and distributed to {len(target_audience)} recipients"
            else:
                return False, "Failed to save announcement"
                
        except Exception as e:
            print(f"Error creating announcement: {e}")
            return False, f"Error creating announcement: {str(e)}"
    
    def get_announcements(self, user_email: str, include_expired: bool = False) -> List[Dict[str, Any]]:
        """Get announcements targeted to a user"""
        try:
            data = self.load_data()
            announcements = data.get('announcements', [])
            
            # Filter announcements for this user
            user_announcements = []
            for announcement in announcements:
                target_audience = announcement.get('target_audience', [])
                
                # Check if user is in target audience or if it's a public announcement
                if (user_email in target_audience or 
                    'all_citizens' in target_audience or
                    'public' in target_audience):
                    
                    # Check expiry if not including expired
                    if not include_expired:
                        expiry_date = announcement.get('expiry_date')
                        if expiry_date and expiry_date < datetime.now().isoformat():
                            continue
                    
                    user_announcements.append(announcement)
            
            # Sort by timestamp (newest first)
            user_announcements.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return user_announcements
            
        except Exception as e:
            print(f"Error retrieving announcements: {e}")
            return []
    
    def create_notification(self, user_email: str, notification_type: str, message: str,
                          metadata: Dict[str, Any] = None) -> bool:
        """Create a notification for a user"""
        try:
            notification_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            notification_data = {
                'id': notification_id,
                'user_email': user_email,
                'type': notification_type,
                'message': message,
                'metadata': metadata or {},
                'timestamp': timestamp,
                'read': False,
                'action_taken': False
            }
            
            data = self.load_data()
            data['notifications'].append(notification_data)
            
            return self.save_data(data)
            
        except Exception as e:
            print(f"Error creating notification: {e}")
            return False
    
    def get_notifications(self, user_email: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        try:
            data = self.load_data()
            notifications = data.get('notifications', [])
            
            # Filter notifications for this user
            user_notifications = [
                notif for notif in notifications
                if notif['user_email'] == user_email
            ]
            
            if unread_only:
                user_notifications = [
                    notif for notif in user_notifications
                    if not notif.get('read', False)
                ]
            
            # Sort by timestamp (newest first)
            user_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return user_notifications
            
        except Exception as e:
            print(f"Error retrieving notifications: {e}")
            return []
    
    def get_user_contacts(self, user_email: str) -> List[Dict[str, Any]]:
        """Get contact directory for messaging (representatives, officials, etc.)"""
        try:
            # Get all users who can receive official communications
            all_users = self.user_backend.get_all_users()
            
            contacts = []
            current_user = SessionManager.get_current_user()
            current_role = current_user.get('role', '') if current_user else ''
            
            for user in all_users:
                if user['email'] == user_email:
                    continue  # Skip self
                
                user_role = user.get('role', 'Contract Citizen')
                
                # Determine if this user should be in contacts based on roles
                contact_info = {
                    'email': user['email'],
                    'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    'role': user_role,
                    'can_message': True,
                    'category': self.categorize_contact(user_role)
                }
                
                contacts.append(contact_info)
            
            # Sort by category and then by name
            contacts.sort(key=lambda x: (x['category'], x['name']))
            
            return contacts
            
        except Exception as e:
            print(f"Error retrieving contacts: {e}")
            return []
    
    def categorize_contact(self, role: str) -> str:
        """Categorize a contact by their role"""
        if 'Founder' in role:
            return 'Platform Leadership'
        elif 'Elder' in role:
            return 'Constitutional Council'
        elif 'Senator' in role:
            return 'Senate'
        elif 'Representative' in role:
            return 'House of Representatives'
        elif role in ['CEO', 'Admin', 'Moderator']:
            return 'Administration'
        else:
            return 'Citizens'
    
    def get_message_statistics(self, user_email: str) -> Dict[str, Any]:
        """Get messaging statistics for a user"""
        try:
            data = self.load_data()
            messages = data.get('messages', [])
            announcements = data.get('announcements', [])
            notifications = data.get('notifications', [])
            
            # Calculate statistics
            sent_messages = len([m for m in messages if m['sender_email'] == user_email])
            received_messages = len([m for m in messages if m['recipient_email'] == user_email])
            unread_messages = len([m for m in messages 
                                 if m['recipient_email'] == user_email and not m.get('read', False)])
            
            user_announcements = len([a for a in announcements 
                                    if user_email in a.get('target_audience', [])])
            unread_notifications = len([n for n in notifications 
                                      if n['user_email'] == user_email and not n.get('read', False)])
            
            return {
                'sent_messages': sent_messages,
                'received_messages': received_messages,
                'unread_messages': unread_messages,
                'announcements': user_announcements,
                'unread_notifications': unread_notifications,
                'total_communications': sent_messages + received_messages + user_announcements
            }
            
        except Exception as e:
            print(f"Error retrieving message statistics: {e}")
            return {
                'sent_messages': 0,
                'received_messages': 0,
                'unread_messages': 0,
                'announcements': 0,
                'unread_notifications': 0,
                'total_communications': 0
            }