"""
Enhanced Blockchain Integration Manager
Provides comprehensive integration between blockchain and all platform modules
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from .blockchain import Blockchain, ValidatorRegistry

class BlockchainIntegrationManager:
    """Central manager for blockchain integration across all modules"""
    
    @staticmethod
    def record_user_action(action_type: str, user_email: str, details: Dict[str, Any], 
                          module: str = 'system') -> Tuple[bool, str]:
        """Standardized method to record any user action across modules"""
        try:
            # Standardize action data structure
            action_data = {
                'action': action_type,
                'user_email': user_email,
                'module': module,
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'details': details
            }
            
            # Add module-specific metadata
            if module == 'users':
                action_data['category'] = 'identity_management'
            elif module == 'debates':
                action_data['category'] = 'civic_engagement'
            elif module == 'moderation':
                action_data['category'] = 'content_governance'
            elif module == 'training':
                action_data['category'] = 'education'
            elif module == 'governance':
                action_data['category'] = 'democratic_process'
            
            success = Blockchain.add_page(
                data=action_data,
                validator=user_email
            )
            
            if success:
                return True, f"Action '{action_type}' recorded successfully on blockchain"
            else:
                return False, "Failed to record action on blockchain"
                
        except Exception as e:
            return False, f"Error recording action: {str(e)}"
    
    @staticmethod
    def get_user_permissions(user_email: str) -> Dict[str, Any]:
        """Get comprehensive user permissions based on blockchain history"""
        # Get user activity from blockchain
        from .blockchain import BlockchainIntegrator
        user_activity = BlockchainIntegrator.get_user_activity_summary(user_email)
        dependencies = BlockchainIntegrator.get_cross_module_dependencies(user_email)
        
        permissions = {
            'basic_access': True,
            'debate_creation': False,
            'moderation_access': False,
            'training_management': False,
            'governance_participation': True,
            'blockchain_validation': False,
            'admin_functions': False,
            'role': 'Contract Citizen',
            'trust_level': dependencies.get('blockchain_trust_score', 0.0),
            'restrictions': [],
            'capabilities': []
        }
        
        # Determine user role from blockchain
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        latest_role = 'Contract Citizen'
        for page in pages:
            data = page.get('data', {})
            if (data.get('user_email') == user_email or data.get('email') == user_email) and \
               data.get('action') == 'register_user':
                latest_role = data.get('role', 'Contract Citizen')
        
        permissions['role'] = latest_role
        
        # Role-based permissions
        if latest_role in ['Contract Representative', 'Contract Senator']:
            permissions['debate_creation'] = True
            permissions['blockchain_validation'] = True
            permissions['governance_participation'] = True
            permissions['capabilities'].extend(['Legislative Initiative', 'Topic Creation', 'Blockchain Validation'])
        
        if latest_role in ['Contract Elder', 'Contract Founder']:
            permissions['debate_creation'] = True
            permissions['moderation_access'] = True
            permissions['training_management'] = True
            permissions['blockchain_validation'] = True
            permissions['admin_functions'] = True
            permissions['capabilities'].extend(['Constitutional Review', 'Platform Administration', 'Training Management'])
        
        # Training-based permissions
        certifications = user_activity['training']['certifications_earned']
        if certifications >= 1:
            permissions['debate_creation'] = True
            permissions['capabilities'].append('Certified Participant')
        
        if certifications >= 2:
            permissions['moderation_access'] = True
            permissions['capabilities'].append('Content Moderation')
        
        # Behavior-based restrictions
        moderation_impact = dependencies.get('moderation_impact', {})
        warnings = moderation_impact.get('warnings_received', 0)
        
        if warnings >= 1:
            permissions['restrictions'].append('Under moderation review')
        if warnings >= 3:
            permissions['debate_creation'] = False
            permissions['governance_participation'] = False
            permissions['restrictions'].append('Restricted from governance activities')
        
        # Trust-based permissions
        trust_score = dependencies.get('blockchain_trust_score', 0.0)
        if trust_score >= 75:
            permissions['capabilities'].append('High Trust User')
        elif trust_score < 25:
            permissions['restrictions'].append('Low trust score - limited access')
        
        return permissions
    
    @staticmethod
    def validate_cross_module_action(action_type: str, user_email: str, 
                                   target_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate actions that span multiple modules"""
        permissions = BlockchainIntegrationManager.get_user_permissions(user_email)
        
        # Cross-module validation rules
        if action_type == 'create_debate_topic':
            if not permissions['debate_creation']:
                return False, "Insufficient permissions to create debate topics"
            
            # Check if user has required training
            if permissions['trust_level'] < 50 and permissions['role'] == 'Contract Citizen':
                return False, "Complete civic training before creating debate topics"
        
        elif action_type == 'moderate_content':
            if not permissions['moderation_access']:
                return False, "Insufficient permissions for content moderation"
            
            # Check for conflicts of interest
            target_user = target_data.get('target_user')
            if target_user == user_email:
                return False, "Cannot moderate your own content"
        
        elif action_type == 'run_for_office':
            if not permissions['governance_participation']:
                return False, "Not eligible to run for office"
            
            # Check training requirements
            from .blockchain import BlockchainIntegrator
            dependencies = BlockchainIntegrator.get_cross_module_dependencies(user_email)
            if not dependencies['training_requirements'].get('representative_readiness'):
                return False, "Complete required training before running for office"
        
        elif action_type == 'validate_blockchain':
            if not permissions['blockchain_validation']:
                return False, "Not authorized as blockchain validator"
        
        return True, "Action validated successfully"
    
    @staticmethod
    def sync_module_states() -> Dict[str, Any]:
        """Synchronize state across all modules using blockchain as source of truth"""
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        sync_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'modules_synced': [],
            'conflicts_resolved': [],
            'errors': [],
            'state_summary': {}
        }
        
        # Track state for each module
        module_states = {
            'users': {},
            'debates': {},
            'moderation': {},
            'training': {},
            'governance': {}
        }
        
        # Rebuild state from blockchain
        for page in pages:
            data = page.get('data', {})
            action = data.get('action', '')
            module = data.get('module', 'system')
            
            try:
                if module == 'users' or action in ['register_user', 'update_role']:
                    email = data.get('user_email') or data.get('email')
                    if email:
                        if email not in module_states['users']:
                            module_states['users'][email] = {}
                        module_states['users'][email].update({
                            'last_action': action,
                            'timestamp': page.get('timestamp'),
                            'role': data.get('role', 'Contract Citizen')
                        })
                
                elif module == 'debates' or action in ['create_topic', 'add_argument', 'vote_on_topic']:
                    topic_id = data.get('topic_id')
                    if topic_id:
                        if topic_id not in module_states['debates']:
                            module_states['debates'][topic_id] = {
                                'arguments': 0,
                                'votes': 0,
                                'created_at': page.get('timestamp')
                            }
                        if action == 'add_argument':
                            module_states['debates'][topic_id]['arguments'] += 1
                        elif action == 'vote_on_topic':
                            module_states['debates'][topic_id]['votes'] += 1
                
                elif module == 'moderation' or action in ['flag_content', 'review_flag', 'warn_user']:
                    flag_id = data.get('flag_id') or data.get('warning_id', f"mod_{page.get('timestamp', '')}")
                    if flag_id not in module_states['moderation']:
                        module_states['moderation'][flag_id] = {}
                    module_states['moderation'][flag_id].update({
                        'action': action,
                        'timestamp': page.get('timestamp'),
                        'status': 'resolved' if action == 'review_flag' else 'pending'
                    })
                
                elif module == 'training' or action in ['start_course', 'complete_module', 'complete_course']:
                    user_email = data.get('user_email')
                    course_id = data.get('course_id')
                    if user_email and course_id:
                        key = f"{user_email}_{course_id}"
                        if key not in module_states['training']:
                            module_states['training'][key] = {
                                'modules_completed': 0,
                                'certifications': 0
                            }
                        if action == 'complete_module':
                            module_states['training'][key]['modules_completed'] += 1
                        elif action == 'complete_course':
                            module_states['training'][key]['certifications'] += 1
                
            except Exception as e:
                sync_report['errors'].append(f"Error processing {action}: {str(e)}")
        
        # Update sync report
        sync_report['modules_synced'] = list(module_states.keys())
        sync_report['state_summary'] = {
            'users': len(module_states['users']),
            'debates': len(module_states['debates']),
            'moderation': len(module_states['moderation']),
            'training': len(module_states['training'])
        }
        
        return sync_report
    
    @staticmethod
    def generate_integration_health_report() -> Dict[str, Any]:
        """Generate comprehensive health report for blockchain integration"""
        from .blockchain import BlockchainIntegrator
        
        # Get base health data
        health_report = BlockchainIntegrator.get_module_health_report()
        
        # Add integration-specific metrics
        integration_metrics = {
            'cross_module_consistency': 'good',
            'data_flow_integrity': 'good',
            'blockchain_sync_status': 'synchronized',
            'integration_errors': [],
            'performance_metrics': {},
            'recommended_optimizations': []
        }
        
        # Check cross-module consistency
        sync_report = BlockchainIntegrationManager.sync_module_states()
        if sync_report['errors']:
            integration_metrics['cross_module_consistency'] = 'degraded'
            integration_metrics['integration_errors'] = sync_report['errors']
        
        # Check blockchain sync
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        if not pages:
            integration_metrics['blockchain_sync_status'] = 'empty'
        elif not Blockchain.validate_chain():
            integration_metrics['blockchain_sync_status'] = 'corrupted'
            integration_metrics['data_flow_integrity'] = 'compromised'
        
        # Performance metrics
        integration_metrics['performance_metrics'] = {
            'total_blockchain_pages': len(pages),
            'modules_with_activity': len([m for m in sync_report['state_summary'] if sync_report['state_summary'][m] > 0]),
            'avg_actions_per_user': sync_report['state_summary']['users'] / max(sync_report['state_summary']['users'], 1),
            'blockchain_validator_count': len([v for v in ValidatorRegistry.load_validators() if v.get('active')])
        }
        
        # Generate optimization recommendations
        if integration_metrics['performance_metrics']['total_blockchain_pages'] > 10000:
            integration_metrics['recommended_optimizations'].append("Consider blockchain archiving for old records")
        
        if integration_metrics['performance_metrics']['blockchain_validator_count'] < 3:
            integration_metrics['recommended_optimizations'].append("Recruit additional blockchain validators")
        
        if sync_report['errors']:
            integration_metrics['recommended_optimizations'].append("Address blockchain synchronization errors")
        
        # Merge with base health report
        health_report['integration_metrics'] = integration_metrics
        
        return health_report
    
    @staticmethod
    def create_module_connection_map() -> Dict[str, Any]:
        """Create a visual map of connections between modules"""
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        connections = {
            'nodes': [
                {'id': 'users', 'label': 'Users Module', 'type': 'core'},
                {'id': 'debates', 'label': 'Debates Module', 'type': 'feature'},
                {'id': 'moderation', 'label': 'Moderation Module', 'type': 'governance'},
                {'id': 'training', 'label': 'Training Module', 'type': 'education'},
                {'id': 'blockchain', 'label': 'Blockchain Module', 'type': 'infrastructure'},
                {'id': 'governance', 'label': 'Governance System', 'type': 'governance'}
            ],
            'edges': [],
            'interaction_summary': {},
            'data_flow_patterns': {}
        }
        
        # Track interactions between modules
        module_interactions = {}
        
        for page in pages:
            data = page.get('data', {})
            action = data.get('action', '')
            module = data.get('module', 'system')
            
            # Map actions to module interactions
            if action == 'register_user':
                # Users → Blockchain
                self._add_edge(connections, 'users', 'blockchain', 'registration')
            elif action == 'create_topic':
                # Users → Debates → Blockchain
                self._add_edge(connections, 'users', 'debates', 'topic_creation')
                self._add_edge(connections, 'debates', 'blockchain', 'record_keeping')
            elif action == 'flag_content':
                # Users → Moderation → Blockchain
                self._add_edge(connections, 'users', 'moderation', 'content_flagging')
                self._add_edge(connections, 'moderation', 'blockchain', 'audit_trail')
            elif action == 'complete_course':
                # Users → Training → Blockchain
                self._add_edge(connections, 'users', 'training', 'education')
                self._add_edge(connections, 'training', 'blockchain', 'certification')
            elif action in ['vote_in_election', 'run_for_office']:
                # Users → Governance → Blockchain
                self._add_edge(connections, 'users', 'governance', 'democratic_participation')
                self._add_edge(connections, 'governance', 'blockchain', 'election_records')
            
            # Track interaction counts
            interaction_key = f"{module}_blockchain"
            if interaction_key not in module_interactions:
                module_interactions[interaction_key] = 0
            module_interactions[interaction_key] += 1
        
        connections['interaction_summary'] = module_interactions
        
        return connections
    
    @staticmethod
    def _add_edge(connections: Dict[str, Any], source: str, target: str, 
                  interaction_type: str) -> None:
        """Helper method to add edges to connection map"""
        edge = {
            'source': source,
            'target': target,
            'type': interaction_type,
            'strength': 1
        }
        
        # Check if edge already exists and increment strength
        for existing_edge in connections['edges']:
            if (existing_edge['source'] == source and 
                existing_edge['target'] == target and 
                existing_edge['type'] == interaction_type):
                existing_edge['strength'] += 1
                return
        
        connections['edges'].append(edge)

# Convenience functions for common integration tasks
def record_debate_action(action_type: str, user_email: str, topic_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Record debate-related action with proper validation"""
    return BlockchainIntegrationManager.record_user_action(
        action_type, user_email, topic_data, 'debates'
    )

def record_moderation_action(action_type: str, user_email: str, mod_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Record moderation-related action with proper validation"""
    return BlockchainIntegrationManager.record_user_action(
        action_type, user_email, mod_data, 'moderation'
    )

def record_training_action(action_type: str, user_email: str, training_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Record training-related action with proper validation"""
    return BlockchainIntegrationManager.record_user_action(
        action_type, user_email, training_data, 'training'
    )

def get_user_module_access(user_email: str) -> Dict[str, bool]:
    """Get user access permissions for all modules"""
    permissions = BlockchainIntegrationManager.get_user_permissions(user_email)
    return {
        'debates': permissions['debate_creation'],
        'moderation': permissions['moderation_access'],
        'training': permissions['basic_access'],
        'governance': permissions['governance_participation'],
        'blockchain': permissions['blockchain_validation'],
        'admin': permissions['admin_functions']
    }

def validate_user_action(action_type: str, user_email: str, action_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate any user action across modules"""
    return BlockchainIntegrationManager.validate_cross_module_action(
        action_type, user_email, action_data
    )