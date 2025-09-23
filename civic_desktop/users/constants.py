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
