"""
Founder Account Setup and Repair Script
This script initializes the founder account, generates keys, and creates the genesis block.
It also repairs a founder account if the user exists but the private key is missing.
"""
import os
import sys
import bcrypt
from datetime import datetime, timezone

# Ensure the project root is in the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from civic_desktop.users.backend import UserBackend
from civic_desktop.users.keys import generate_keypair
from civic_desktop.blockchain.blockchain import Blockchain, ValidatorRegistry

def setup_or_repair_founder_account():
    """
    Creates or repairs the founder account, ensuring keys and blockchain records are consistent.
    """
    print("--- Founder Account Setup & Repair ---")

    # --- 1. Define Founder Details ---
    founder_email = "founder@civicengagementai.org"
    founder_first_name = "Steve"
    founder_last_name = "Cornell"
    founder_password = "secure_password_123"

    # --- 2. Define Paths ---
    users_dir = os.path.join(project_root, 'civic_desktop', 'users')
    privkey_dir = os.path.join(users_dir, 'private_keys')
    key_filename = f"{founder_email.replace('@','_at_')}.pem"
    privkey_path = os.path.join(privkey_dir, key_filename)
    os.makedirs(privkey_dir, exist_ok=True)

    # --- 3. Check User and Key Status ---
    existing_user = UserBackend.get_user_by_email(founder_email)
    key_exists = os.path.exists(privkey_path)

    if existing_user and key_exists:
        print(f"✅ Founder account '{founder_email}' and private key exist. No action needed.")
        return

    # --- 4. Generate Keys (if needed) ---
    if not key_exists:
        print("🔑 Private key not found. Generating new key pair...")
        try:
            public_key, private_key = generate_keypair()
            with open(privkey_path, 'w', encoding='utf-8') as f:
                f.write(private_key)
            print(f"   -> Successfully saved new private key to: {privkey_path}")
        except Exception as e:
            print(f"❌ Error generating or saving keys: {e}")
            return
    else:
        # If key exists, we need to get the corresponding public key from the user record
        if existing_user:
            public_key = existing_user.get('public_key')
            print("🔑 Private key found. Using existing public key.")
        else:
            # This is an unlikely state, but we handle it.
            print("❌ Inconsistent state: Key exists but user does not. Please resolve manually.")
            return


    # --- 5. Handle User Creation or Update ---
    if existing_user:
        print(f"👤 User '{founder_email}' exists. Updating public key...")
        update_data = {'public_key': public_key}
        if UserBackend.update_user(founder_email, update_data):
            print("   -> Public key updated successfully in users database.")
        else:
            print("   -> Failed to update user's public key.")
            return
    else:
        print(f"👤 User '{founder_email}' not found. Creating new user...")
        password_hash = UserBackend.hash_password(founder_password)
        founder_data = {
            'email': founder_email,
            'first_name': founder_first_name,
            'last_name': founder_last_name,
            'roles': ['Contract Founder'],
            'password_hash': password_hash,
            'public_key': public_key,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        if UserBackend.add_user(founder_data):
             print("   -> New user created successfully.")
        else:
             print("   -> Failed to create new user.")
             return


    # --- 6. Update Validator Registry ---
    ValidatorRegistry.add_validator(founder_email, public_key)
    print(f"🏛️  Founder '{founder_email}' is now a validator with the correct public key.")

    # --- 7. Ensure Genesis Block Exists ---
    if not Blockchain.get_genesis_block():
        print("📖 Genesis block not found. Creating now...")
        founder_info_for_genesis = {
            'first_name': founder_first_name,
            'last_name': founder_last_name,
            'email': founder_email,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        UserBackend.create_genesis_block(founder_info_for_genesis)
        print("   -> Genesis block created.")
    else:
        print("📖 Genesis block already exists.")


    print("\n✅ --- Founder Account Setup/Repair Complete! ---")
    print(f"You can now log in with:\n  Email: {founder_email}\n  Password: {founder_password}")


if __name__ == "__main__":
    # Load necessary data before starting
    Blockchain.load_chain()
    setup_or_repair_founder_account()
