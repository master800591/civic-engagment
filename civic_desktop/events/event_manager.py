# Events Module - Backend Event Management System
"""
Events backend for comprehensive civic event management including:
- Event discovery and calendar management
- Event creation with role-based permissions
- Democratic engagement and community organizing
- RSVP management and attendance tracking
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from ..main import ENV_CONFIG
from ..blockchain.blockchain import Blockchain
from ..users.session import SessionManager

class EventManager:
    """Core event management system for civic events and community organizing"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('events_db_path', 'events/events_db.json')
        self.blockchain = Blockchain()
        
    def load_events_data(self) -> Dict[str, Any]:
        """Load events data from storage"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'events': [],
                'rsvps': [],
                'venues': [],
                'organizers': [],
                'last_updated': None
            }
    
    def save_events_data(self, data: Dict[str, Any]) -> bool:
        """Save events data to storage"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save events data: {e}")
            return False
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new civic event with constitutional review"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
        
        # Check event creation permissions
        if not self._check_event_creation_permissions(user, event_data.get('event_type', '')):
            return {'error': 'Insufficient permissions to create this type of event'}
        
        # Validate event data
        validation_result = self._validate_event_data(event_data)
        if validation_result.get('error'):
            return validation_result
        
        # Create event record
        event_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user['email'].split('@')[0]}"
        
        event_record = {
            'id': event_id,
            'title': event_data['title'],
            'description': event_data.get('description', ''),
            'event_type': event_data['event_type'],
            'organizer_email': user['email'],
            'organizer_name': user.get('name', user['email']),
            'start_datetime': event_data['start_datetime'],
            'end_datetime': event_data.get('end_datetime', ''),
            'location': event_data.get('location', ''),
            'venue_id': event_data.get('venue_id', ''),
            'max_participants': event_data.get('max_participants', 0),
            'registration_required': event_data.get('registration_required', False),
            'constitutional_review_status': 'pending' if event_data['event_type'] == 'public_meeting' else 'approved',
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'rsvp_count': 0,
            'tags': event_data.get('tags', []),
            'resources_needed': event_data.get('resources_needed', [])
        }
        
        # Save event
        events_data = self.load_events_data()
        events_data['events'].append(event_record)
        
        if self.save_events_data(events_data):
            # Record event creation on blockchain
            self.blockchain.add_page(
                action_type="event_created",
                data={
                    'event_id': event_id,
                    'event_type': event_record['event_type'],
                    'title': event_record['title'],
                    'organizer': user['email'],
                    'constitutional_approval_status': event_record['constitutional_review_status'],
                    'start_datetime': event_record['start_datetime']
                },
                user_email=user['email']
            )
            
            return {'success': True, 'event_id': event_id, 'event': event_record}
        else:
            return {'error': 'Failed to save event'}
    
    def get_events(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get events with optional filtering"""
        events_data = self.load_events_data()
        events = events_data.get('events', [])
        
        if not filters:
            return events
        
        # Apply filters
        filtered_events = []
        for event in events:
            include_event = True
            
            # Filter by event type
            if filters.get('event_type') and event.get('event_type') != filters['event_type']:
                include_event = False
            
            # Filter by date range
            if filters.get('start_date'):
                event_date = datetime.fromisoformat(event.get('start_datetime', ''))
                filter_start = datetime.fromisoformat(filters['start_date'])
                if event_date < filter_start:
                    include_event = False
            
            if filters.get('end_date'):
                event_date = datetime.fromisoformat(event.get('start_datetime', ''))
                filter_end = datetime.fromisoformat(filters['end_date'])
                if event_date > filter_end:
                    include_event = False
            
            # Filter by location/jurisdiction
            if filters.get('location') and filters['location'].lower() not in event.get('location', '').lower():
                include_event = False
            
            # Filter by organizer
            if filters.get('organizer') and event.get('organizer_email') != filters['organizer']:
                include_event = False
            
            if include_event:
                filtered_events.append(event)
        
        return filtered_events
    
    def rsvp_to_event(self, event_id: str, rsvp_status: str = 'attending') -> Dict[str, Any]:
        """RSVP to an event with capacity management"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
        
        events_data = self.load_events_data()
        
        # Find the event
        event = None
        for e in events_data['events']:
            if e['id'] == event_id:
                event = e
                break
        
        if not event:
            return {'error': 'Event not found'}
        
        # Check if event is still accepting RSVPs
        event_start = datetime.fromisoformat(event['start_datetime'])
        if event_start < datetime.now():
            return {'error': 'Event has already started'}
        
        # Check existing RSVP
        existing_rsvp = None
        for rsvp in events_data.get('rsvps', []):
            if rsvp['event_id'] == event_id and rsvp['user_email'] == user['email']:
                existing_rsvp = rsvp
                break
        
        # Check capacity if new RSVP
        if not existing_rsvp and rsvp_status == 'attending':
            if event.get('max_participants', 0) > 0:
                current_count = len([r for r in events_data.get('rsvps', []) 
                                   if r['event_id'] == event_id and r['status'] == 'attending'])
                if current_count >= event['max_participants']:
                    return {'error': 'Event is at capacity'}
        
        # Create or update RSVP
        rsvp_record = {
            'event_id': event_id,
            'user_email': user['email'],
            'user_name': user.get('name', user['email']),
            'status': rsvp_status,  # 'attending', 'not_attending', 'maybe'
            'rsvp_date': datetime.now().isoformat(),
            'notes': ''
        }
        
        if existing_rsvp:
            # Update existing RSVP
            for i, rsvp in enumerate(events_data['rsvps']):
                if rsvp['event_id'] == event_id and rsvp['user_email'] == user['email']:
                    events_data['rsvps'][i] = rsvp_record
                    break
        else:
            # Add new RSVP
            events_data['rsvps'].append(rsvp_record)
        
        # Update event RSVP count
        event['rsvp_count'] = len([r for r in events_data['rsvps'] 
                                 if r['event_id'] == event_id and r['status'] == 'attending'])
        
        if self.save_events_data(events_data):
            # Record RSVP on blockchain
            self.blockchain.add_page(
                action_type="event_rsvp",
                data={
                    'event_id': event_id,
                    'event_title': event['title'],
                    'rsvp_status': rsvp_status,
                    'participant': user['email']
                },
                user_email=user['email']
            )
            
            return {'success': True, 'rsvp': rsvp_record}
        else:
            return {'error': 'Failed to save RSVP'}
    
    def check_in_to_event(self, event_id: str, location_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check in to an event with optional location verification"""
        user = SessionManager.get_current_user()
        if not user:
            return {'error': 'User not authenticated'}
        
        events_data = self.load_events_data()
        
        # Find the event
        event = None
        for e in events_data['events']:
            if e['id'] == event_id:
                event = e
                break
        
        if not event:
            return {'error': 'Event not found'}
        
        # Verify RSVP
        has_rsvp = any(r['event_id'] == event_id and r['user_email'] == user['email'] and r['status'] == 'attending' 
                      for r in events_data.get('rsvps', []))
        
        if event.get('registration_required', False) and not has_rsvp:
            return {'error': 'RSVP required for this event'}
        
        # Check if event is happening now
        event_start = datetime.fromisoformat(event['start_datetime'])
        event_end = datetime.fromisoformat(event.get('end_datetime', event['start_datetime']))
        
        now = datetime.now()
        if now < event_start - timedelta(minutes=30):  # Allow check-in 30 minutes early
            return {'error': 'Event has not started yet'}
        if now > event_end + timedelta(hours=1):  # Allow check-in up to 1 hour after end
            return {'error': 'Event has ended'}
        
        # Record attendance
        attendance_record = {
            'event_id': event_id,
            'user_email': user['email'],
            'user_name': user.get('name', user['email']),
            'check_in_time': datetime.now().isoformat(),
            'location_data': location_data or {},
            'participation_level': 'present'
        }
        
        # Add to attendance (or update existing)
        if 'attendance' not in events_data:
            events_data['attendance'] = []
        
        # Remove existing attendance record if present
        events_data['attendance'] = [a for a in events_data['attendance'] 
                                   if not (a['event_id'] == event_id and a['user_email'] == user['email'])]
        events_data['attendance'].append(attendance_record)
        
        if self.save_events_data(events_data):
            # Record attendance on blockchain
            self.blockchain.add_page(
                action_type="event_attendance",
                data={
                    'event_id': event_id,
                    'event_title': event['title'],
                    'participant': user['email'],
                    'check_in_time': attendance_record['check_in_time'],
                    'participation_level': attendance_record['participation_level']
                },
                user_email=user['email']
            )
            
            return {'success': True, 'attendance': attendance_record}
        else:
            return {'error': 'Failed to record attendance'}
    
    def get_user_events(self, user_email: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get events organized by or attended by user"""
        if not user_email:
            user = SessionManager.get_current_user()
            if not user:
                return {'error': 'User not authenticated'}
            user_email = user['email']
        
        events_data = self.load_events_data()
        
        # Events organized by user
        organized_events = [e for e in events_data.get('events', []) 
                          if e.get('organizer_email') == user_email]
        
        # Events user has RSVP'd to
        user_rsvps = [r['event_id'] for r in events_data.get('rsvps', []) 
                     if r['user_email'] == user_email and r['status'] == 'attending']
        rsvp_events = [e for e in events_data.get('events', []) if e['id'] in user_rsvps]
        
        # Events user has attended
        user_attendance = [a['event_id'] for a in events_data.get('attendance', []) 
                         if a['user_email'] == user_email]
        attended_events = [e for e in events_data.get('events', []) if e['id'] in user_attendance]
        
        return {
            'organized': organized_events,
            'rsvp': rsvp_events,
            'attended': attended_events
        }
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event data before creation"""
        required_fields = ['title', 'event_type', 'start_datetime']
        
        for field in required_fields:
            if not event_data.get(field):
                return {'error': f'Missing required field: {field}'}
        
        # Validate event type
        valid_types = ['town_hall', 'public_meeting', 'training_session', 'election', 
                      'debate', 'community_forum', 'working_group', 'social_event']
        if event_data['event_type'] not in valid_types:
            return {'error': f'Invalid event type. Must be one of: {", ".join(valid_types)}'}
        
        # Validate datetime format
        try:
            start_time = datetime.fromisoformat(event_data['start_datetime'])
            if start_time < datetime.now():
                return {'error': 'Event start time must be in the future'}
        except ValueError:
            return {'error': 'Invalid start datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}
        
        # Validate end time if provided
        if event_data.get('end_datetime'):
            try:
                end_time = datetime.fromisoformat(event_data['end_datetime'])
                if end_time <= start_time:
                    return {'error': 'Event end time must be after start time'}
            except ValueError:
                return {'error': 'Invalid end datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}
        
        return {'success': True}
    
    def _check_event_creation_permissions(self, user: Dict[str, Any], event_type: str) -> bool:
        """Check if user has permissions to create events of this type"""
        # Basic permission checks
        user_role = user.get('role', '')
        
        # Public events - Representatives, Senators, Elders, Founders
        if event_type in ['town_hall', 'public_meeting', 'election']:
            return user_role in ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder']
        
        # Training sessions - Representatives and above, or designated trainers
        elif event_type == 'training_session':
            return user_role in ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder'] or \
                   'trainer' in user.get('additional_roles', [])
        
        # Debates - Representatives and above
        elif event_type == 'debate':
            return user_role in ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder']
        
        # Community forums, working groups, social events - any authenticated user
        elif event_type in ['community_forum', 'working_group', 'social_event']:
            return True
        
        # Default: require elected role
        return user_role in ['Contract Representative', 'Contract Senator', 'Contract Elder', 'Contract Founder']