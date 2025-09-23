# Entry point for the Civic Engagement Platform Desktop GUI

import os
import sys
import json

# Add the parent directory to the Python path to enable absolute imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

CONFIG_PATH = os.environ.get('CIVIC_CONFIG', os.path.join(BASE_DIR, 'config/dev_config.json'))
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    ENV_CONFIG = json.load(f)

def main():
    from civic_desktop.main_window import run_gui
    run_gui()

if __name__ == "__main__":
    main()
