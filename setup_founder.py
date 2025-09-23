"""
Founder Account Setup Script
This script initializes the founder account, generates keys, and creates the genesis block.
"""
import os
import sys
import bcrypt
from datetime import datetime, timezone

# Ensure the project root is in the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from civic_desktop.users.backend import UserBackend
from civic_desktop.users.keys import generate_keypair
from civic_desktop.blockchain.blockchain import Blockchain, ValidatorRegistry

def setup_founder_account():
    """
    Creates the initial founder account, keys, and genesis block if they don't exist.
    """
    print("--- Founder Account Setup ---")

    # --- 1. Define Founder Details ---
    founder_email = "founder@civicengagementai.org"
    founder_first_name = "Steve"
    founder_last_name = "Cornell"
    # In a real scenario, this would be prompted securely, not hardcoded.
    founder_password = "secure_password_123" 
    
    # --- 2. Check if Founder Already Exists ---
    if UserBackend.get_user_by_email(founder_email):
        print(f"✅ Founder account for '{founder_email}' already exists. Setup is not needed.")
        return

    print(f"Founder account for '{founder_email}' not found. Proceeding with creation...")

    # --- 3. Define Paths ---
    users_dir = os.path.join(project_root, 'civic_desktop', 'users')
    privkey_dir = os.path.join(users_dir, 'private_keys')
    key_filename = f"{founder_email.replace('@','_at_')}.pem"
    privkey_path = os.path.join(privkey_dir, key_filename)

    os.makedirs(privkey_dir, exist_ok=True)
    print(f"Private key directory is: {privkey_dir}")

    # --- 4. Generate and Save Keys ---
    try:
        public_key, private_key = generate_keypair()
        with open(privkey_path, 'w', encoding='utf-8') as f:
            f.write(private_key)
        print(f"🔑 Successfully generated and saved private key to: {privkey_path}")
    except Exception as e:
        print(f"❌ Error generating or saving keys: {e}")
        return

    # --- 5. Hash Password ---
    password_hash = UserBackend.hash_password(founder_password)

    # --- 6. Prepare Founder Data for Blockchain ---
    founder_data = {
        'action': 'register_user',
        'user_email': founder_email,
        'first_name': founder_first_name,
        'last_name': founder_last_name,
        'address': '123 Founder Ave',
        'city': 'Genesis City',
        'state': 'Origin',
        'country': 'Platform Nation',
        'public_key': public_key,
        'roles': ['Contract Founder'],
        'password_hash': password_hash,
        'id_document_hash': 'genesis_founder_id_hash_placeholder',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    # --- 7. Add Founder to Validator Registry ---
    ValidatorRegistry.add_validator(founder_email, public_key)
    print(f"🏛️  Founder '{founder_email}' added to the validator registry.")

    # --- 8. Create Genesis Block ---
    # The create_genesis_block method is called within register_user for the first user.
    # We'll prepare the data it needs.
    founder_info_for_genesis = {
        'first_name': founder_first_name,
        'last_name': founder_last_name,
        'email': founder_email,
        'created_at': datetime.now(timezone.utc).isoformat()
    }

    # --- 9. Add Founder to Blockchain (which also creates Genesis) ---
    try:
        # The backend logic should handle genesis creation for the first user.
        UserBackend.create_genesis_block(founder_info_for_genesis)
        print("📖 Genesis block created successfully.")
        
        # Now, add the founder's registration as the first official page
        Blockchain.add_page(
            data=founder_data,
            validator=founder_email,
            signature='GENESIS'
        )
        print("👤 Founder registration recorded on the blockchain.")
        print("\n✅ --- Founder Account Setup Complete! ---")
        print(f"You can now log in with:\n  Email: {founder_email}\n  Password: {founder_password}")

    except Exception as e:
        print(f"❌ An error occurred during blockchain registration: {e}")

if __name__ == "__main__":
    # It's crucial to load the chain first to know the current state.
    Blockchain.load_chain()
    setup_founder_account()
