# Entry point for the Civic Engagement Platform Desktop GUI

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.environ.get('CIVIC_CONFIG', os.path.join(BASE_DIR, 'config/dev_config.json'))
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    ENV_CONFIG = json.load(f)

def main():
    from civic_desktop.main_window import run_gui
    run_gui()

if __name__ == "__main__":
    main()
