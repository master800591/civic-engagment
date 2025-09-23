"""
Founder Account Repair Script
This script repairs the founder account if the user exists on the blockchain but the private key file is missing.
"""
import os
import sys
from datetime import datetime, timezone

# Ensure the project root is in the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from civic_desktop.users.backend import UserBackend
from civic_desktop.users.keys import generate_keypair
from civic_desktop.blockchain.blockchain import Blockchain, ValidatorRegistry

def repair_founder_account():
    """
    Repairs the founder account by creating a missing private key and updating the blockchain.
    """
    print("--- Founder Account Repair ---")

    # --- 1. Define Founder Details ---
    founder_email = "founder@civicengagementai.org"
    founder_first_name = "Steve"
    founder_last_name = "Cornell"

    # --- 2. Define Paths ---
    users_dir = os.path.join(project_root, 'civic_desktop', 'users')
    privkey_dir = os.path.join(users_dir, 'private_keys')
    key_filename = f"{founder_email.replace('@','_at_')}.pem"
    privkey_path = os.path.join(privkey_dir, key_filename)
    os.makedirs(privkey_dir, exist_ok=True)

    # --- 3. Check User and Key Status ---
    existing_user = UserBackend.get_user_by_email(founder_email)
    key_exists = os.path.exists(privkey_path)

    if not existing_user:
        print(f"❌ User '{founder_email}' does not exist on the blockchain. Please run the initial setup first.")
        return

    if key_exists:
        print(f"✅ Private key for '{founder_email}' already exists. No repair needed.")
        return

    print(f"👤 User '{founder_email}' found, but private key is missing. Starting repair...")

    # --- 4. Generate New Keys ---
    print("🔑 Generating new key pair...")
    try:
        public_key, private_key = generate_keypair()
        with open(privkey_path, 'w', encoding='utf-8') as f:
            f.write(private_key)
        print(f"   -> Successfully saved new private key to: {privkey_path}")
    except Exception as e:
        print(f"❌ Error generating or saving keys: {e}")
        return

    # --- 5. Record Public Key Update on Blockchain ---
    print("🔗 Recording public key update on the blockchain...")
    success = UserBackend.update_profile(founder_email, {'public_key': public_key})
    if success:
        print("   -> Public key update recorded successfully.")
    else:
        print("   -> Failed to record public key update. Aborting.")
        return

    # --- 6. Update Validator Registry ---
    ValidatorRegistry.add_validator(founder_email, public_key)
    print(f"🏛️  Founder '{founder_email}' is now a validator with the correct public key.")

    # --- 7. Verify Genesis Block ---
    # The genesis block should already exist if the user does. This is just a check.
    genesis_path = os.path.join(project_root, 'civic_desktop', 'blockchain', 'genesis_block.json')
    if not os.path.exists(genesis_path):
        print("⚠️ Warning: Genesis block file is missing. The blockchain may be in an inconsistent state.")
    else:
        print("📖 Genesis block file found.")

    print("\n✅ --- Founder Account Repair Complete! ---")
    print(f"You should now be able to log in with the email '{founder_email}'.")


if __name__ == "__main__":
    # Load necessary data before starting
    Blockchain.load_chain()
    repair_founder_account()
