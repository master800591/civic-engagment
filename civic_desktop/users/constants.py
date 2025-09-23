import os
import json

def get_users_db_path() -> str:
    try:
        from civic_desktop.main import ENV_CONFIG
        # Prefer explicit users_db_path; fallback to legacy 'db_path'
        configured = ENV_CONFIG.get('users_db_path') or ENV_CONFIG.get('db_path')
        if configured:
            # Resolve relative paths against the civic_desktop directory
            base_dir = os.path.dirname(os.path.dirname(__file__))
            return configured if os.path.isabs(configured) else os.path.join(base_dir, configured)
    except Exception:
        pass
    # Default to local users_db.json next to this file
    return os.path.join(os.path.dirname(__file__), 'users_db.json')

USERS_DB = get_users_db_path()

# Role hierarchy and permissions
USER_ROLES = {
    "Junior Contract Citizen": {
        "level": 1,
        "age_requirement": "under_18",
        "parental_consent": True,
        "training_required": ["youth_civics_basics"],
        "permissions": ["view_public", "youth_training"],
        "restrictions": ["no_voting", "no_debate_creation", "content_filtered"]
    },
    "Prospect Contract Citizen": {
        "level": 2,
        "verification_required": ["identity", "address", "email"],
        "permissions": ["view_content", "basic_training"],
        "restrictions": ["no_participation", "no_voting", "read_only"]
    },
    "Probation Contract Citizen": {
        "level": 3,
        "training_required": ["constitutional_law", "civic_responsibilities", "platform_governance"],
        "permissions": ["view_all", "training_access", "progress_tracking"],
        "restrictions": ["no_participation_until_certified"]
    },
    "Contract Citizen": {
        "level": 4,
        "permissions": ["vote", "debate", "create_topics", "moderation_reports"],
        "restrictions": []
    },
    "Contract Representative": {
        "level": 5,
        "permissions": ["legislative_initiative", "budget_authority", "impeachment_power"],
        "restrictions": []
    },
    "Contract Senator": {
        "level": 6,
        "permissions": ["legislative_review", "confirmation_authority", "elder_veto_override"],
        "restrictions": []
    },
    "Contract Elder": {
        "level": 7,
        "permissions": ["constitutional_veto", "judicial_review", "appointment_authority"],
        "restrictions": []
    },
    "Contract Founder": {
        "level": 10,
        "permissions": ["all"],
        "restrictions": []
    },
    "CEO": {
        "level": 9,
        "permissions": ["all"],
        "restrictions": []
    }
}

MANDATORY_TRAINING_PATHS = {
    "Junior_to_Prospect": ["youth_civics_completion"],
    "Prospect_to_Probation": ["identity_verification_complete"], 
    "Probation_to_Citizen": ["constitutional_law", "civic_responsibilities", "platform_governance"]
}

# Government ID types accepted for verification
ACCEPTED_ID_TYPES = [
    "passport",
    "drivers_license", 
    "state_id",
    "military_id"
]

# Age-related constants
MINIMUM_AGE_FOR_FULL_CITIZENSHIP = 18
MAXIMUM_REASONABLE_AGE = 120

# Verification status types
VERIFICATION_STATUS = {
    "pending": "Verification pending",
    "in_progress": "Verification in progress", 
    "approved": "Verification approved",
    "rejected": "Verification rejected",
    "expired": "Verification expired"
}
