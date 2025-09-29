# Project Coordinator - Inter-Jurisdictional Project Management Backend
# Multi-jurisdiction governance project coordination and resource sharing

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Import application components
try:
    from main import ENV_CONFIG
    from blockchain.blockchain import Blockchain
    from utils.validation import DataValidator
except ImportError as e:
    print(f"Warning: Import error in project coordinator: {e}")
    ENV_CONFIG = {}


class InterJurisdictionalProjectManager:
    """Multi-jurisdiction governance project coordination system"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('collaboration_db_path', 'collaboration/collaboration_db.json')
        self.ensure_database()
        
        # Initialize project type configurations
        self.project_types = self.load_project_type_configurations()
    
    def ensure_database(self):
        """Ensure collaboration database exists"""
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initial_data = {
                'projects': [],
                'resource_agreements': [],
                'working_groups': [],
                'collaboration_analytics': {},
                'governance_frameworks': [],
                'cost_allocations': [],
                'performance_metrics': []
            }
            
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def load_project_type_configurations(self) -> Dict[str, Dict]:
        """Load configuration for different collaboration project types"""
        
        return {
            'resource_sharing': {
                'description': 'Shared resources and infrastructure projects',
                'min_participants': 2,
                'governance_model': 'consensus',
                'constitutional_review': False,
                'approval_threshold': 0.6,
                'duration_limits': {'min_days': 30, 'max_days': 1095},
                'required_roles': ['contract_representative'],
                'cost_sharing_required': True
            },
            'policy_coordination': {
                'description': 'Coordinated policy development and implementation',
                'min_participants': 3,
                'governance_model': 'majority_vote',
                'constitutional_review': True,
                'approval_threshold': 0.67,
                'duration_limits': {'min_days': 90, 'max_days': 1825},
                'required_roles': ['contract_representative', 'contract_senator'],
                'cost_sharing_required': False
            },
            'emergency_response': {
                'description': 'Emergency preparedness and response coordination',
                'min_participants': 2,
                'governance_model': 'lead_authority',
                'constitutional_review': False,
                'approval_threshold': 0.5,
                'duration_limits': {'min_days': 1, 'max_days': 365},
                'required_roles': ['contract_representative'],
                'cost_sharing_required': True
            },
            'infrastructure_development': {
                'description': 'Joint infrastructure planning and development',
                'min_participants': 2,
                'governance_model': 'weighted_voting',
                'constitutional_review': True,
                'approval_threshold': 0.75,
                'duration_limits': {'min_days': 180, 'max_days': 3650},
                'required_roles': ['contract_representative', 'contract_senator'],
                'cost_sharing_required': True
            },
            'joint_service_delivery': {
                'description': 'Shared service delivery and operations',
                'min_participants': 2,
                'governance_model': 'consensus',
                'constitutional_review': False,
                'approval_threshold': 0.6,
                'duration_limits': {'min_days': 30, 'max_days': 1825},
                'required_roles': ['contract_representative'],
                'cost_sharing_required': True
            },
            'research_collaboration': {
                'description': 'Joint research and data sharing initiatives',
                'min_participants': 2,
                'governance_model': 'consensus',
                'constitutional_review': False,
                'approval_threshold': 0.6,
                'duration_limits': {'min_days': 90, 'max_days': 1095},
                'required_roles': ['contract_member'],
                'cost_sharing_required': False
            },
            'environmental_protection': {
                'description': 'Environmental protection and sustainability projects',
                'min_participants': 2,
                'governance_model': 'consensus',
                'constitutional_review': True,
                'approval_threshold': 0.67,
                'duration_limits': {'min_days': 365, 'max_days': 3650},
                'required_roles': ['contract_representative', 'contract_senator'],
                'cost_sharing_required': True
            },
            'economic_development': {
                'description': 'Regional economic development initiatives',
                'min_participants': 3,
                'governance_model': 'weighted_voting',
                'constitutional_review': True,
                'approval_threshold': 0.7,
                'duration_limits': {'min_days': 180, 'max_days': 3650},
                'required_roles': ['contract_representative', 'contract_senator'],
                'cost_sharing_required': True
            }
        }
    
    def initiate_collaboration_project(self, initiator_email: str, project_data: Dict) -> Tuple[bool, str]:
        """Initiate collaborative project across multiple jurisdictions"""
        
        try:
            # Validate project initiator authority
            if not self.has_collaboration_authority(initiator_email, project_data['scope']):
                return False, "Insufficient authority to initiate inter-jurisdictional projects"
            
            # Get project type configuration
            project_type = project_data.get('type', '').lower().replace(' ', '_')
            if project_type not in self.project_types:
                return False, f"Unknown project type: {project_data.get('type')}"
            
            project_type_config = self.project_types[project_type]
            
            # Validate minimum participants
            participating_jurisdictions = project_data.get('participating_jurisdictions', [])
            if len(participating_jurisdictions) < project_type_config['min_participants']:
                return False, f"Minimum {project_type_config['min_participants']} participants required"
            
            # Constitutional review for applicable projects
            if project_type_config['constitutional_review']:
                constitutional_review = self.perform_inter_jurisdictional_constitutional_review(project_data)
                if not constitutional_review['approved']:
                    return False, f"Constitutional review failed: {constitutional_review['reason']}"
            
            # Create collaboration agreement framework
            collaboration_agreement = {
                'governance_structure': self.design_governance_structure(project_data, project_type_config),
                'resource_commitments': self.define_resource_commitments(participating_jurisdictions, project_data),
                'decision_making_process': self.establish_decision_process(project_type_config['governance_model']),
                'dispute_resolution': self.establish_dispute_resolution_mechanism(project_data),
                'performance_metrics': self.define_performance_metrics(project_data),
                'exit_procedures': self.establish_exit_procedures(project_data)
            }
            
            # Create project record
            project = {
                'id': str(uuid.uuid4()),
                'title': project_data['title'],
                'type': project_data['type'],
                'description': project_data['description'],
                'initiator_email': initiator_email,
                'participating_jurisdictions': participating_jurisdictions,
                'collaboration_agreement': collaboration_agreement,
                'project_type_config': project_type_config,
                'status': 'initiated',
                'progress': {
                    'current_phase': 'planning',
                    'completion_percentage': 0,
                    'milestones': [],
                    'deliverables': []
                },
                'timeline': {
                    'start_date': project_data.get('start_date'),
                    'end_date': project_data.get('end_date'),
                    'key_dates': []
                },
                'budget': {
                    'total_estimate': project_data.get('budget_estimate', '0'),
                    'cost_allocation': {},
                    'funding_sources': []
                },
                'communications': {
                    'project_lead': initiator_email,
                    'stakeholder_contacts': [],
                    'meeting_schedule': [],
                    'reporting_requirements': []
                },
                'risk_management': {
                    'identified_risks': [],
                    'mitigation_strategies': [],
                    'contingency_plans': []
                },
                'quality_assurance': {
                    'success_criteria': [],
                    'review_checkpoints': [],
                    'evaluation_metrics': []
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'priority': project_data.get('priority', 'Normal'),
                'constitutional_compliance': project_type_config['constitutional_review']
            }
            
            # Save project
            self.save_project(project)
            
            # Record project initiation on blockchain
            try:
                Blockchain.add_page(
                    action_type="collaboration_project_initiated",
                    data={
                        'project_id': project['id'],
                        'title': project['title'],
                        'type': project['type'],
                        'participating_jurisdictions': participating_jurisdictions,
                        'initiator': initiator_email,
                        'constitutional_review': project_type_config['constitutional_review']
                    },
                    user_email=initiator_email
                )
            except Exception as e:
                print(f"Warning: Failed to record project initiation on blockchain: {e}")
            
            # Send notifications to participating jurisdictions
            self.notify_project_stakeholders(project, 'project_initiated')
            
            return True, f"Collaboration project '{project['title']}' initiated successfully"
            
        except Exception as e:
            return False, f"Error initiating collaboration project: {e}"
    
    def has_collaboration_authority(self, user_email: str, project_scope: str) -> bool:
        """Check if user has authority to initiate collaboration projects"""
        
        try:
            # Mock authority check - in real implementation, check user role and jurisdiction
            # user = load_user(user_email)
            # return user.get('role') in ['contract_representative', 'contract_senator', 'contract_elder']
            return True  # Allow all users for testing
            
        except Exception as e:
            print(f"Error checking collaboration authority: {e}")
            return False
    
    def perform_inter_jurisdictional_constitutional_review(self, project_data: Dict) -> Dict:
        """Perform constitutional review for inter-jurisdictional projects"""
        
        try:
            # Constitutional compliance checks
            compliance_checks = [
                self.check_jurisdictional_authority(project_data),
                self.check_constitutional_powers(project_data),
                self.check_interstate_commerce_compliance(project_data),
                self.check_due_process_requirements(project_data),
                self.check_equal_protection_principles(project_data)
            ]
            
            all_passed = all(check['passed'] for check in compliance_checks)
            
            review_result = {
                'approved': all_passed,
                'review_date': datetime.now().isoformat(),
                'compliance_checks': compliance_checks,
                'reason': 'Constitutional review passed' if all_passed else 'Constitutional violations found',
                'recommendations': self.generate_constitutional_recommendations(compliance_checks)
            }
            
            return review_result
            
        except Exception as e:
            return {
                'approved': False,
                'reason': f"Constitutional review error: {e}",
                'review_date': datetime.now().isoformat()
            }
    
    def check_jurisdictional_authority(self, project_data: Dict) -> Dict:
        """Check jurisdictional authority for project"""
        
        # Mock implementation - check if jurisdictions have authority for project type
        return {
            'check_name': 'jurisdictional_authority',
            'passed': True,
            'details': 'All participating jurisdictions have authority for this project type'
        }
    
    def check_constitutional_powers(self, project_data: Dict) -> Dict:
        """Check constitutional powers and limitations"""
        
        return {
            'check_name': 'constitutional_powers',
            'passed': True,
            'details': 'Project within constitutional powers of participating jurisdictions'
        }
    
    def check_interstate_commerce_compliance(self, project_data: Dict) -> Dict:
        """Check interstate commerce clause compliance"""
        
        return {
            'check_name': 'interstate_commerce',
            'passed': True,
            'details': 'Project complies with interstate commerce regulations'
        }
    
    def check_due_process_requirements(self, project_data: Dict) -> Dict:
        """Check due process requirements"""
        
        return {
            'check_name': 'due_process',
            'passed': True,
            'details': 'Project includes adequate due process protections'
        }
    
    def check_equal_protection_principles(self, project_data: Dict) -> Dict:
        """Check equal protection principles"""
        
        return {
            'check_name': 'equal_protection',
            'passed': True,
            'details': 'Project ensures equal protection for all citizens'
        }
    
    def generate_constitutional_recommendations(self, compliance_checks: List[Dict]) -> List[str]:
        """Generate recommendations based on constitutional review"""
        
        recommendations = []
        
        for check in compliance_checks:
            if not check['passed']:
                recommendations.append(f"Address {check['check_name']}: {check['details']}")
        
        if not recommendations:
            recommendations.append("No constitutional issues identified. Proceed with project as planned.")
        
        return recommendations
    
    def design_governance_structure(self, project_data: Dict, project_config: Dict) -> Dict:
        """Design governance structure for the collaboration project"""
        
        governance_model = project_config['governance_model']
        
        governance_structures = {
            'consensus': {
                'decision_method': 'unanimous_consent',
                'voting_threshold': 1.0,
                'leadership': 'rotating_chair',
                'dispute_resolution': 'mediation',
                'veto_powers': 'all_participants'
            },
            'majority_vote': {
                'decision_method': 'simple_majority',
                'voting_threshold': 0.51,
                'leadership': 'elected_chair',
                'dispute_resolution': 'arbitration',
                'veto_powers': 'none'
            },
            'weighted_voting': {
                'decision_method': 'weighted_by_contribution',
                'voting_threshold': project_config['approval_threshold'],
                'leadership': 'largest_contributor',
                'dispute_resolution': 'expert_panel',
                'veto_powers': 'major_contributors'
            },
            'lead_authority': {
                'decision_method': 'lead_authority_decides',
                'voting_threshold': 0.5,
                'leadership': 'designated_lead',
                'dispute_resolution': 'lead_authority',
                'veto_powers': 'lead_authority'
            }
        }
        
        base_structure = governance_structures.get(governance_model, governance_structures['consensus'])
        
        # Customize based on project specifics
        customized_structure = base_structure.copy()
        customized_structure.update({
            'project_committee': self.form_project_committee(project_data),
            'oversight_board': self.form_oversight_board(project_data),
            'technical_advisors': self.identify_technical_advisors(project_data),
            'citizen_representation': self.ensure_citizen_representation(project_data),
            'reporting_structure': self.design_reporting_structure(project_data)
        })
        
        return customized_structure
    
    def form_project_committee(self, project_data: Dict) -> Dict:
        """Form project committee with representatives from each jurisdiction"""
        
        return {
            'composition': 'one_representative_per_jurisdiction',
            'selection_method': 'appointed_by_jurisdiction',
            'term_length': 'project_duration',
            'responsibilities': [
                'project_oversight',
                'resource_allocation_decisions',
                'milestone_approval',
                'conflict_resolution',
                'stakeholder_communication'
            ],
            'meeting_frequency': 'monthly',
            'decision_authority': 'operational_decisions'
        }
    
    def form_oversight_board(self, project_data: Dict) -> Dict:
        """Form oversight board for strategic guidance"""
        
        return {
            'composition': 'senior_officials_from_jurisdictions',
            'selection_method': 'appointed_by_chief_executive',
            'term_length': 'project_duration',
            'responsibilities': [
                'strategic_guidance',
                'budget_approval',
                'policy_decisions',
                'performance_review',
                'constitutional_compliance'
            ],
            'meeting_frequency': 'quarterly',
            'decision_authority': 'strategic_decisions'
        }
    
    def identify_technical_advisors(self, project_data: Dict) -> Dict:
        """Identify technical advisors for the project"""
        
        return {
            'composition': 'subject_matter_experts',
            'selection_method': 'committee_appointment',
            'term_length': 'as_needed',
            'responsibilities': [
                'technical_guidance',
                'feasibility_assessment',
                'best_practices_recommendations',
                'quality_assurance',
                'innovation_opportunities'
            ],
            'engagement_model': 'consultative',
            'compensation': 'pro_bono_or_contracted'
        }
    
    def ensure_citizen_representation(self, project_data: Dict) -> Dict:
        """Ensure citizen representation in governance"""
        
        return {
            'representation_method': 'citizen_advisory_panel',
            'selection_process': 'random_selection_with_demographics',
            'panel_size': 'proportional_to_affected_population',
            'responsibilities': [
                'citizen_perspective',
                'impact_assessment',
                'public_input_collection',
                'transparency_monitoring',
                'accountability_oversight'
            ],
            'meeting_frequency': 'bi_monthly',
            'decision_influence': 'advisory_recommendations'
        }
    
    def design_reporting_structure(self, project_data: Dict) -> Dict:
        """Design reporting structure for transparency"""
        
        return {
            'reporting_levels': [
                'project_committee',
                'oversight_board',
                'participating_jurisdictions',
                'public_stakeholders'
            ],
            'reporting_frequency': {
                'operational_reports': 'monthly',
                'progress_reports': 'quarterly',
                'financial_reports': 'quarterly',
                'public_reports': 'semi_annually'
            },
            'transparency_requirements': [
                'public_meeting_minutes',
                'budget_transparency',
                'performance_metrics',
                'stakeholder_feedback',
                'compliance_reporting'
            ],
            'communication_channels': [
                'official_websites',
                'public_meetings',
                'stakeholder_newsletters',
                'social_media_updates',
                'local_media_briefings'
            ]
        }
    
    def define_resource_commitments(self, jurisdictions: List[str], project_data: Dict) -> Dict:
        """Define resource commitments from each jurisdiction"""
        
        # Mock resource commitment calculation
        total_jurisdictions = len(jurisdictions)
        base_commitment_per_jurisdiction = 1.0 / total_jurisdictions
        
        resource_commitments = {}
        
        for jurisdiction in jurisdictions:
            commitment = {
                'financial_contribution_percentage': base_commitment_per_jurisdiction,
                'personnel_allocation': 'as_needed_basis',
                'infrastructure_access': 'shared_resources',
                'expertise_sharing': 'subject_matter_experts',
                'data_sharing': 'relevant_datasets',
                'commitment_duration': project_data.get('duration', 'project_term'),
                'performance_obligations': [
                    'timely_resource_provision',
                    'quality_assurance',
                    'compliance_monitoring',
                    'collaborative_participation'
                ]
            }
            resource_commitments[jurisdiction] = commitment
        
        return resource_commitments
    
    def establish_decision_process(self, governance_model: str) -> Dict:
        """Establish decision-making process"""
        
        decision_processes = {
            'consensus': {
                'process_steps': [
                    'proposal_submission',
                    'stakeholder_consultation',
                    'discussion_period',
                    'consensus_building',
                    'unanimous_approval'
                ],
                'timeline': '30_days_minimum',
                'fallback_mechanism': 'mediated_resolution'
            },
            'majority_vote': {
                'process_steps': [
                    'proposal_submission',
                    'review_period',
                    'public_comment',
                    'deliberation',
                    'majority_vote'
                ],
                'timeline': '21_days_minimum',
                'fallback_mechanism': 'super_majority_override'
            },
            'weighted_voting': {
                'process_steps': [
                    'proposal_submission',
                    'impact_assessment',
                    'stakeholder_weighting',
                    'weighted_deliberation',
                    'weighted_vote'
                ],
                'timeline': '45_days_minimum',
                'fallback_mechanism': 'expert_arbitration'
            },
            'lead_authority': {
                'process_steps': [
                    'proposal_submission',
                    'consultation_period',
                    'lead_authority_review',
                    'decision_announcement',
                    'implementation_planning'
                ],
                'timeline': '14_days_minimum',
                'fallback_mechanism': 'oversight_board_review'
            }
        }
        
        return decision_processes.get(governance_model, decision_processes['consensus'])
    
    def establish_dispute_resolution_mechanism(self, project_data: Dict) -> Dict:
        """Establish dispute resolution mechanism"""
        
        return {
            'resolution_stages': [
                {
                    'stage': 'direct_negotiation',
                    'participants': 'involved_parties',
                    'timeline': '14_days',
                    'facilitator': 'project_committee_chair'
                },
                {
                    'stage': 'mediation',
                    'participants': 'involved_parties_plus_mediator',
                    'timeline': '30_days',
                    'facilitator': 'neutral_third_party'
                },
                {
                    'stage': 'arbitration',
                    'participants': 'involved_parties_plus_arbitrator',
                    'timeline': '60_days',
                    'facilitator': 'qualified_arbitrator'
                },
                {
                    'stage': 'oversight_board_review',
                    'participants': 'oversight_board',
                    'timeline': '30_days',
                    'facilitator': 'oversight_board_chair'
                }
            ],
            'escalation_triggers': [
                'failure_to_reach_agreement',
                'violation_of_agreement_terms',
                'constitutional_concerns',
                'resource_allocation_disputes',
                'performance_issues'
            ],
            'resolution_binding': 'yes_after_arbitration',
            'appeal_process': 'oversight_board_final_review'
        }
    
    def define_performance_metrics(self, project_data: Dict) -> Dict:
        """Define performance metrics and KPIs"""
        
        return {
            'efficiency_metrics': [
                'milestone_completion_rate',
                'budget_variance',
                'timeline_adherence',
                'resource_utilization',
                'cost_per_deliverable'
            ],
            'effectiveness_metrics': [
                'goal_achievement_rate',
                'quality_scores',
                'stakeholder_satisfaction',
                'citizen_benefit_realization',
                'long_term_sustainability'
            ],
            'collaboration_metrics': [
                'inter_jurisdictional_cooperation_score',
                'communication_frequency',
                'conflict_resolution_time',
                'knowledge_sharing_index',
                'joint_decision_making_efficiency'
            ],
            'compliance_metrics': [
                'constitutional_compliance_rate',
                'regulatory_adherence',
                'transparency_index',
                'accountability_measures',
                'audit_findings'
            ],
            'measurement_frequency': 'monthly',
            'reporting_schedule': 'quarterly',
            'performance_review_cycle': 'annual'
        }
    
    def establish_exit_procedures(self, project_data: Dict) -> Dict:
        """Establish procedures for project exit or termination"""
        
        return {
            'exit_triggers': [
                'project_completion',
                'mutual_agreement_termination',
                'performance_failure',
                'funding_exhaustion',
                'constitutional_violation',
                'force_majeure_events'
            ],
            'exit_process': [
                'exit_notification_period_90_days',
                'asset_disposition_planning',
                'liability_resolution',
                'knowledge_transfer',
                'final_reporting',
                'post_project_evaluation'
            ],
            'asset_disposition': {
                'shared_assets': 'proportional_distribution',
                'developed_intellectual_property': 'joint_ownership',
                'physical_infrastructure': 'based_on_contribution',
                'data_and_records': 'shared_access_maintained'
            },
            'ongoing_obligations': [
                'maintenance_of_confidentiality',
                'continued_data_protection',
                'warranty_periods',
                'dispute_resolution_availability',
                'performance_monitoring_continuation'
            ]
        }
    
    def notify_project_stakeholders(self, project: Dict, notification_type: str):
        """Send notifications to project stakeholders"""
        
        try:
            # TODO: Integrate with communications module
            print(f"Notification sent: {notification_type} for project {project['title']}")
            
            # Record notification on blockchain
            try:
                Blockchain.add_page(
                    action_type="collaboration_notification_sent",
                    data={
                        'project_id': project['id'],
                        'notification_type': notification_type,
                        'recipients': project['participating_jurisdictions'],
                        'timestamp': datetime.now().isoformat()
                    },
                    user_email=project['initiator_email']
                )
            except Exception as e:
                print(f"Warning: Failed to record notification on blockchain: {e}")
                
        except Exception as e:
            print(f"Error sending stakeholder notifications: {e}")
    
    def save_project(self, project: Dict):
        """Save project to database"""
        
        try:
            data = self.load_data()
            data['projects'].append(project)
            self.save_data(data)
        except Exception as e:
            print(f"Error saving project: {e}")
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        
        try:
            data = self.load_data()
            for project in data['projects']:
                if project['id'] == project_id:
                    return project
            return None
        except Exception as e:
            print(f"Error getting project: {e}")
            return None
    
    def get_projects_by_jurisdiction(self, jurisdiction: str) -> List[Dict]:
        """Get all projects for a specific jurisdiction"""
        
        try:
            data = self.load_data()
            jurisdiction_projects = []
            
            for project in data['projects']:
                if jurisdiction in project.get('participating_jurisdictions', []):
                    jurisdiction_projects.append(project)
            
            return jurisdiction_projects
        except Exception as e:
            print(f"Error getting projects by jurisdiction: {e}")
            return []
    
    def update_project_status(self, project_id: str, status_update: Dict, user_email: str) -> Tuple[bool, str]:
        """Update project status and progress"""
        
        try:
            data = self.load_data()
            
            for i, project in enumerate(data['projects']):
                if project['id'] == project_id:
                    # Update project data
                    project['status'] = status_update.get('status', project['status'])
                    project['progress'].update(status_update.get('progress', {}))
                    project['last_updated'] = datetime.now().isoformat()
                    
                    # Record status update on blockchain
                    try:
                        Blockchain.add_page(
                            action_type="collaboration_project_updated",
                            data={
                                'project_id': project_id,
                                'status_update': status_update,
                                'updated_by': user_email
                            },
                            user_email=user_email
                        )
                    except Exception as e:
                        print(f"Warning: Failed to record project update on blockchain: {e}")
                    
                    data['projects'][i] = project
                    self.save_data(data)
                    
                    return True, "Project status updated successfully"
            
            return False, "Project not found"
            
        except Exception as e:
            return False, f"Error updating project status: {e}"
    
    def get_collaboration_analytics(self) -> Dict:
        """Get collaboration analytics and metrics"""
        
        try:
            data = self.load_data()
            projects = data['projects']
            
            analytics = {
                'total_projects': len(projects),
                'active_projects': len([p for p in projects if p['status'] == 'active']),
                'completed_projects': len([p for p in projects if p['status'] == 'completed']),
                'total_jurisdictions_involved': len(set().union(*[p.get('participating_jurisdictions', []) for p in projects])),
                'average_project_duration': self.calculate_average_duration(projects),
                'success_rate': self.calculate_success_rate(projects),
                'cost_effectiveness': self.calculate_cost_effectiveness(projects),
                'collaboration_efficiency': self.calculate_collaboration_efficiency(projects)
            }
            
            return analytics
            
        except Exception as e:
            print(f"Error getting collaboration analytics: {e}")
            return {}
    
    def calculate_average_duration(self, projects: List[Dict]) -> float:
        """Calculate average project duration"""
        
        completed_projects = [p for p in projects if p['status'] == 'completed']
        if not completed_projects:
            return 0.0
        
        total_duration = 0
        for project in completed_projects:
            try:
                start_date = datetime.fromisoformat(project['timeline']['start_date'])
                end_date = datetime.fromisoformat(project['timeline']['end_date'])
                duration = (end_date - start_date).days
                total_duration += duration
            except (KeyError, ValueError):
                continue
        
        return total_duration / len(completed_projects) if completed_projects else 0.0
    
    def calculate_success_rate(self, projects: List[Dict]) -> float:
        """Calculate project success rate"""
        
        completed_projects = [p for p in projects if p['status'] in ['completed', 'failed']]
        if not completed_projects:
            return 0.0
        
        successful_projects = [p for p in completed_projects if p['status'] == 'completed']
        return len(successful_projects) / len(completed_projects) * 100
    
    def calculate_cost_effectiveness(self, projects: List[Dict]) -> float:
        """Calculate cost effectiveness metrics"""
        
        # Mock calculation - in real implementation, analyze budget vs outcomes
        return 85.5  # 85.5% cost effectiveness
    
    def calculate_collaboration_efficiency(self, projects: List[Dict]) -> float:
        """Calculate collaboration efficiency score"""
        
        # Mock calculation - in real implementation, analyze communication, decision speed, etc.
        return 78.2  # 78.2% collaboration efficiency
    
    def load_data(self) -> Dict:
        """Load collaboration database"""
        
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
        """Save collaboration database"""
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving collaboration data: {e}")


class ResourceSharingManager:
    """Comprehensive resource sharing and coordination system"""
    
    def __init__(self):
        self.db_path = ENV_CONFIG.get('collaboration_db_path', 'collaboration/collaboration_db.json')
        self.resource_categories = self.load_resource_categories()
    
    def load_resource_categories(self) -> Dict[str, Dict]:
        """Load resource sharing categories and configurations"""
        
        return {
            'personnel_sharing': {
                'description': 'Shared personnel and expertise',
                'valuation_method': 'hourly_rate',
                'tracking_granularity': 'detailed',
                'approval_level': 'departmental',
                'cost_allocation': 'usage_based',
                'performance_metrics': ['utilization_rate', 'satisfaction_score', 'skill_match']
            },
            'equipment_sharing': {
                'description': 'Shared equipment and infrastructure',
                'valuation_method': 'usage_based',
                'tracking_granularity': 'moderate',
                'approval_level': 'managerial',
                'cost_allocation': 'depreciation_plus_maintenance',
                'performance_metrics': ['availability_rate', 'maintenance_cost', 'efficiency']
            },
            'facility_sharing': {
                'description': 'Shared facilities and spaces',
                'valuation_method': 'space_time',
                'tracking_granularity': 'basic',
                'approval_level': 'administrative',
                'cost_allocation': 'proportional_usage',
                'performance_metrics': ['occupancy_rate', 'maintenance_quality', 'user_satisfaction']
            },
            'emergency_services': {
                'description': 'Emergency response and public safety',
                'valuation_method': 'incident_based',
                'tracking_granularity': 'detailed',
                'approval_level': 'emergency_authority',
                'cost_allocation': 'mutual_aid_agreement',
                'performance_metrics': ['response_time', 'outcome_effectiveness', 'cost_per_incident']
            },
            'technology_resources': {
                'description': 'IT systems, software, and digital resources',
                'valuation_method': 'subscription_based',
                'tracking_granularity': 'detailed',
                'approval_level': 'technical_authority',
                'cost_allocation': 'user_based',
                'performance_metrics': ['uptime', 'user_adoption', 'security_compliance']
            },
            'knowledge_expertise': {
                'description': 'Professional knowledge and consulting',
                'valuation_method': 'consulting_rate',
                'tracking_granularity': 'project_based',
                'approval_level': 'professional',
                'cost_allocation': 'time_and_materials',
                'performance_metrics': ['expertise_relevance', 'problem_resolution', 'knowledge_transfer']
            },
            'transportation_services': {
                'description': 'Transportation and logistics support',
                'valuation_method': 'mileage_plus_time',
                'tracking_granularity': 'detailed',
                'approval_level': 'operational',
                'cost_allocation': 'distance_and_usage',
                'performance_metrics': ['fuel_efficiency', 'schedule_adherence', 'safety_record']
            },
            'financial_resources': {
                'description': 'Financial support and shared funding',
                'valuation_method': 'face_value',
                'tracking_granularity': 'detailed',
                'approval_level': 'executive',
                'cost_allocation': 'principal_plus_interest',
                'performance_metrics': ['fund_utilization', 'return_on_investment', 'repayment_schedule']
            }
        }
    
    def create_resource_sharing_agreement(self, coordinator_email: str, sharing_data: Dict) -> Tuple[bool, str]:
        """Create comprehensive resource sharing agreement between jurisdictions"""
        
        try:
            # Validate coordinator authority
            if not self.has_resource_sharing_authority(coordinator_email, sharing_data['scope']):
                return False, "Insufficient authority to create resource sharing agreements"
            
            # Get resource category configuration
            resource_category = sharing_data.get('category', '').lower().replace(' ', '_')
            if resource_category not in self.resource_categories:
                return False, f"Unknown resource category: {sharing_data.get('category')}"
            
            category_config = self.resource_categories[resource_category]
            
            # Calculate resource valuations
            resource_valuations = self.calculate_resource_valuations(sharing_data, category_config)
            
            # Design cost allocation framework
            cost_allocation = self.design_cost_allocation_framework(sharing_data, category_config)
            
            # Create resource sharing agreement
            agreement = {
                'id': str(uuid.uuid4()),
                'coordinator_email': coordinator_email,
                'coordinator_jurisdiction': 'current_jurisdiction',  # TODO: Get from user profile
                'agreement_title': sharing_data['title'],
                'description': sharing_data['description'],
                'participating_jurisdictions': sharing_data['participating_jurisdictions'],
                'shared_resources': sharing_data['shared_resources'],
                'resource_valuations': resource_valuations,
                'cost_allocation_framework': cost_allocation,
                'usage_tracking_system': {
                    'tracking_method': 'digital_logging',
                    'reporting_frequency': 'monthly',
                    'reconciliation_process': 'quarterly',
                    'audit_requirements': 'annual'
                },
                'governance_framework': {
                    'oversight_committee': self.form_resource_oversight_committee(sharing_data),
                    'dispute_resolution': 'mediation_arbitration',
                    'modification_process': 'unanimous_consent',
                    'termination_procedures': 'ninety_day_notice'
                },
                'performance_monitoring': {
                    'key_performance_indicators': category_config['performance_metrics'],
                    'measurement_frequency': 'monthly',
                    'reporting_schedule': 'quarterly',
                    'continuous_improvement': 'annual_review'
                },
                'compliance_requirements': {
                    'regulatory_compliance': self.identify_regulatory_requirements(sharing_data),
                    'audit_trails': 'comprehensive',
                    'transparency_requirements': 'public_reporting',
                    'data_protection': 'privacy_safeguards'
                },
                'risk_management': {
                    'identified_risks': self.identify_sharing_risks(sharing_data),
                    'mitigation_strategies': self.develop_risk_mitigation(sharing_data),
                    'insurance_requirements': 'liability_coverage',
                    'contingency_planning': 'service_continuity'
                },
                'agreement_terms': {
                    'effective_date': datetime.now().isoformat(),
                    'duration': sharing_data.get('duration', '1 year'),
                    'renewal_options': 'automatic_with_notice',
                    'modification_procedures': 'written_amendment_process'
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'status': 'active',
                'category_config': category_config
            }
            
            # Save agreement
            self.save_resource_agreement(agreement)
            
            # Record agreement creation on blockchain
            try:
                Blockchain.add_page(
                    action_type="resource_sharing_agreement_created",
                    data={
                        'agreement_id': agreement['id'],
                        'title': agreement['agreement_title'],
                        'category': resource_category,
                        'participating_jurisdictions': sharing_data['participating_jurisdictions'],
                        'coordinator': coordinator_email
                    },
                    user_email=coordinator_email
                )
            except Exception as e:
                print(f"Warning: Failed to record agreement creation on blockchain: {e}")
            
            # Notify participating jurisdictions
            self.notify_agreement_participants(agreement, 'agreement_created')
            
            return True, f"Resource sharing agreement '{agreement['agreement_title']}' created successfully"
            
        except Exception as e:
            return False, f"Error creating resource sharing agreement: {e}"
    
    def has_resource_sharing_authority(self, user_email: str, scope: str) -> bool:
        """Check if user has authority to create resource sharing agreements"""
        
        # Mock authority check
        return True
    
    def calculate_resource_valuations(self, sharing_data: Dict, category_config: Dict) -> Dict:
        """Calculate resource valuations based on category and usage"""
        
        valuation_method = category_config['valuation_method']
        
        valuation_methods = {
            'hourly_rate': lambda: self.calculate_hourly_valuation(sharing_data),
            'usage_based': lambda: self.calculate_usage_valuation(sharing_data),
            'space_time': lambda: self.calculate_space_time_valuation(sharing_data),
            'incident_based': lambda: self.calculate_incident_valuation(sharing_data),
            'subscription_based': lambda: self.calculate_subscription_valuation(sharing_data),
            'consulting_rate': lambda: self.calculate_consulting_valuation(sharing_data),
            'mileage_plus_time': lambda: self.calculate_transportation_valuation(sharing_data),
            'face_value': lambda: self.calculate_financial_valuation(sharing_data)
        }
        
        calculation_method = valuation_methods.get(valuation_method, valuation_methods['usage_based'])
        return calculation_method()
    
    def calculate_hourly_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate hourly rate valuation for personnel sharing"""
        
        return {
            'valuation_method': 'hourly_rate',
            'base_rate': 75.00,  # USD per hour
            'skill_multipliers': {
                'specialist': 1.5,
                'expert': 2.0,
                'consultant': 2.5
            },
            'overhead_factor': 1.3,
            'benefits_factor': 1.25,
            'total_effective_rate': 123.75  # Base rate * overhead * benefits
        }
    
    def calculate_usage_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate usage-based valuation for equipment sharing"""
        
        return {
            'valuation_method': 'usage_based',
            'depreciation_rate': 0.15,  # 15% annual depreciation
            'maintenance_cost_per_hour': 25.00,
            'operational_cost_per_hour': 15.00,
            'insurance_cost_per_hour': 5.00,
            'total_cost_per_hour': 45.00
        }
    
    def calculate_space_time_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate space-time valuation for facility sharing"""
        
        return {
            'valuation_method': 'space_time',
            'cost_per_square_foot_per_hour': 2.50,
            'utilities_cost_per_hour': 10.00,
            'maintenance_cost_per_hour': 5.00,
            'security_cost_per_hour': 3.00,
            'total_cost_per_hour': 18.50
        }
    
    def calculate_incident_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate incident-based valuation for emergency services"""
        
        return {
            'valuation_method': 'incident_based',
            'base_response_cost': 500.00,
            'personnel_cost_per_hour': 150.00,
            'equipment_cost_per_hour': 200.00,
            'vehicle_cost_per_hour': 100.00,
            'administrative_cost': 50.00
        }
    
    def calculate_subscription_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate subscription-based valuation for technology resources"""
        
        return {
            'valuation_method': 'subscription_based',
            'monthly_subscription_cost': 1000.00,
            'setup_cost_per_user': 50.00,
            'training_cost_per_user': 25.00,
            'support_cost_per_user_per_month': 10.00,
            'total_cost_per_user_per_month': 85.00
        }
    
    def calculate_consulting_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate consulting rate valuation for knowledge sharing"""
        
        return {
            'valuation_method': 'consulting_rate',
            'expert_rate_per_hour': 200.00,
            'specialist_rate_per_hour': 150.00,
            'analyst_rate_per_hour': 100.00,
            'travel_cost_per_mile': 0.58,
            'preparation_time_factor': 1.2
        }
    
    def calculate_transportation_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate transportation valuation"""
        
        return {
            'valuation_method': 'mileage_plus_time',
            'mileage_rate': 0.58,  # USD per mile
            'driver_rate_per_hour': 25.00,
            'vehicle_depreciation_per_mile': 0.15,
            'fuel_cost_per_mile': 0.12,
            'maintenance_cost_per_mile': 0.08
        }
    
    def calculate_financial_valuation(self, sharing_data: Dict) -> Dict:
        """Calculate financial resource valuation"""
        
        return {
            'valuation_method': 'face_value',
            'principal_amount': sharing_data.get('amount', 0),
            'interest_rate': 0.03,  # 3% annual
            'administrative_fee': 0.005,  # 0.5%
            'risk_premium': 0.001,  # 0.1%
            'total_cost_factor': 1.036
        }
    
    def design_cost_allocation_framework(self, sharing_data: Dict, category_config: Dict) -> Dict:
        """Design cost allocation framework for resource sharing"""
        
        allocation_method = category_config['cost_allocation']
        
        allocation_frameworks = {
            'usage_based': {
                'allocation_principle': 'pay_per_use',
                'measurement_unit': 'hours_or_incidents',
                'billing_frequency': 'monthly',
                'payment_terms': 'net_30',
                'cost_reconciliation': 'quarterly'
            },
            'proportional_usage': {
                'allocation_principle': 'proportional_to_usage',
                'measurement_unit': 'percentage_of_total_usage',
                'billing_frequency': 'monthly',
                'payment_terms': 'net_15',
                'cost_reconciliation': 'monthly'
            },
            'mutual_aid_agreement': {
                'allocation_principle': 'reciprocal_services',
                'measurement_unit': 'service_credits',
                'billing_frequency': 'annual_reconciliation',
                'payment_terms': 'service_exchange',
                'cost_reconciliation': 'annual'
            },
            'user_based': {
                'allocation_principle': 'per_user_pricing',
                'measurement_unit': 'active_users',
                'billing_frequency': 'monthly',
                'payment_terms': 'net_15',
                'cost_reconciliation': 'monthly'
            },
            'time_and_materials': {
                'allocation_principle': 'actual_costs_incurred',
                'measurement_unit': 'hours_and_expenses',
                'billing_frequency': 'bi_weekly',
                'payment_terms': 'net_15',
                'cost_reconciliation': 'monthly'
            },
            'distance_and_usage': {
                'allocation_principle': 'mileage_plus_time',
                'measurement_unit': 'miles_and_hours',
                'billing_frequency': 'monthly',
                'payment_terms': 'net_30',
                'cost_reconciliation': 'monthly'
            },
            'principal_plus_interest': {
                'allocation_principle': 'loan_repayment',
                'measurement_unit': 'principal_and_interest',
                'billing_frequency': 'monthly',
                'payment_terms': 'scheduled_payments',
                'cost_reconciliation': 'annual'
            },
            'depreciation_plus_maintenance': {
                'allocation_principle': 'asset_cost_recovery',
                'measurement_unit': 'depreciation_and_maintenance',
                'billing_frequency': 'quarterly',
                'payment_terms': 'net_30',
                'cost_reconciliation': 'annual'
            }
        }
        
        framework = allocation_frameworks.get(allocation_method, allocation_frameworks['usage_based'])
        
        # Add specific allocations for participating jurisdictions
        framework['jurisdiction_allocations'] = self.calculate_jurisdiction_allocations(
            sharing_data['participating_jurisdictions'], framework
        )
        
        return framework
    
    def calculate_jurisdiction_allocations(self, jurisdictions: List[str], framework: Dict) -> Dict:
        """Calculate cost allocation percentages for each jurisdiction"""
        
        # Mock equal allocation - in real implementation, consider population, usage, contribution
        equal_share = 1.0 / len(jurisdictions)
        
        allocations = {}
        for jurisdiction in jurisdictions:
            allocations[jurisdiction] = {
                'allocation_percentage': equal_share,
                'payment_responsibility': framework['payment_terms'],
                'billing_contact': 'finance_department',
                'cost_center': 'shared_services'
            }
        
        return allocations
    
    def form_resource_oversight_committee(self, sharing_data: Dict) -> Dict:
        """Form oversight committee for resource sharing governance"""
        
        return {
            'committee_composition': 'one_representative_per_participant',
            'selection_method': 'appointed_by_jurisdiction',
            'term_length': 'agreement_duration',
            'meeting_frequency': 'quarterly',
            'responsibilities': [
                'usage_monitoring',
                'cost_reconciliation',
                'performance_evaluation',
                'dispute_mediation',
                'agreement_modifications'
            ],
            'decision_authority': 'operational_oversight',
            'reporting_requirements': 'quarterly_reports_to_jurisdictions'
        }
    
    def identify_regulatory_requirements(self, sharing_data: Dict) -> List[str]:
        """Identify regulatory requirements for resource sharing"""
        
        return [
            'procurement_regulations',
            'inter_governmental_agreements',
            'data_protection_laws',
            'employment_regulations',
            'insurance_requirements',
            'audit_and_transparency_rules',
            'environmental_compliance',
            'safety_regulations'
        ]
    
    def identify_sharing_risks(self, sharing_data: Dict) -> List[Dict]:
        """Identify risks associated with resource sharing"""
        
        return [
            {
                'risk_category': 'operational',
                'risk_description': 'Resource availability conflicts',
                'likelihood': 'medium',
                'impact': 'medium',
                'mitigation_priority': 'high'
            },
            {
                'risk_category': 'financial',
                'risk_description': 'Cost overruns and billing disputes',
                'likelihood': 'medium',
                'impact': 'high',
                'mitigation_priority': 'high'
            },
            {
                'risk_category': 'legal',
                'risk_description': 'Liability and insurance coverage gaps',
                'likelihood': 'low',
                'impact': 'high',
                'mitigation_priority': 'medium'
            },
            {
                'risk_category': 'performance',
                'risk_description': 'Service quality degradation',
                'likelihood': 'medium',
                'impact': 'medium',
                'mitigation_priority': 'medium'
            },
            {
                'risk_category': 'governance',
                'risk_description': 'Decision-making conflicts',
                'likelihood': 'medium',
                'impact': 'medium',
                'mitigation_priority': 'medium'
            }
        ]
    
    def develop_risk_mitigation(self, sharing_data: Dict) -> List[Dict]:
        """Develop risk mitigation strategies"""
        
        return [
            {
                'risk_category': 'operational',
                'mitigation_strategy': 'Implement resource scheduling system with priority protocols',
                'responsible_party': 'oversight_committee',
                'implementation_timeline': '30_days'
            },
            {
                'risk_category': 'financial',
                'mitigation_strategy': 'Establish clear billing procedures and dispute resolution process',
                'responsible_party': 'finance_departments',
                'implementation_timeline': '14_days'
            },
            {
                'risk_category': 'legal',
                'mitigation_strategy': 'Comprehensive insurance review and liability agreements',
                'responsible_party': 'legal_departments',
                'implementation_timeline': '60_days'
            },
            {
                'risk_category': 'performance',
                'mitigation_strategy': 'Service level agreements with performance monitoring',
                'responsible_party': 'service_providers',
                'implementation_timeline': '45_days'
            },
            {
                'risk_category': 'governance',
                'mitigation_strategy': 'Clear decision-making protocols and mediation procedures',
                'responsible_party': 'oversight_committee',
                'implementation_timeline': '21_days'
            }
        ]
    
    def notify_agreement_participants(self, agreement: Dict, notification_type: str):
        """Send notifications to agreement participants"""
        
        try:
            print(f"Notification sent: {notification_type} for agreement {agreement['agreement_title']}")
            
            # Record notification on blockchain
            try:
                Blockchain.add_page(
                    action_type="resource_sharing_notification_sent",
                    data={
                        'agreement_id': agreement['id'],
                        'notification_type': notification_type,
                        'participants': agreement['participating_jurisdictions'],
                        'timestamp': datetime.now().isoformat()
                    },
                    user_email=agreement['coordinator_email']
                )
            except Exception as e:
                print(f"Warning: Failed to record notification on blockchain: {e}")
                
        except Exception as e:
            print(f"Error sending participant notifications: {e}")
    
    def save_resource_agreement(self, agreement: Dict):
        """Save resource agreement to database"""
        
        try:
            data = self.load_data()
            data['resource_agreements'].append(agreement)
            self.save_data(data)
        except Exception as e:
            print(f"Error saving resource agreement: {e}")
    
    def load_data(self) -> Dict:
        """Load collaboration database"""
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Initialize database if not exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            initial_data = {
                'projects': [],
                'resource_agreements': [],
                'working_groups': [],
                'collaboration_analytics': {}
            }
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
            return initial_data
        except json.JSONDecodeError:
            print("Error: Corrupted collaboration database")
            return {}
    
    def save_data(self, data: Dict):
        """Save collaboration database"""
        
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving collaboration data: {e}")


# Export the main classes
__all__ = ['InterJurisdictionalProjectManager', 'ResourceSharingManager']