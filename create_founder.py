import os
import sys
import bcrypt
from datetime import datetime, timezone

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from civic_desktop.users.backend import UserBackend
from civic_desktop.users.keys import generate_keypair
from civic_desktop.blockchain.blockchain import Blockchain, ValidatorRegistry

def create_founder_account():
    """
    Creates the initial founder account if no users exist.
    """
    # Check if any users already exist
    if UserBackend.load_users():
        print("Founder account already exists or users are present in the database.")
        return

    print("Creating founder account...")

    # Founder details
    founder_email = "founder@civicengagementai.org"
    founder_first_name = "Steve"
    founder_last_name = "Cornell"
    founder_password = "secure_password_123" # Use a more secure method in production

    # Generate keys
    public_key, private_key = generate_keypair()

    # Save private key
    privkey_dir = os.path.join(os.path.dirname(__file__), '..', 'civic_desktop', 'users', 'private_keys')
    os.makedirs(privkey_dir, exist_ok=True)
    privkey_path = os.path.join(privkey_dir, f"{founder_email.replace('@','_at_')}.pem")
    with open(privkey_path, 'w', encoding='utf-8') as f:
        f.write(private_key)
    print(f"Private key saved to {privkey_path}")

    # Hash password
    password_hash = UserBackend.hash_password(founder_password)

    # Create founder user data
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
        'id_document_hash': 'genesis_founder_id_hash', # Placeholder
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }

    # Add founder as a validator
    ValidatorRegistry.add_validator(founder_email, public_key)
    print(f"Founder {founder_email} added to validator registry.")

    # Create genesis block with founder info
    UserBackend.create_genesis_block({
        'first_name': founder_first_name,
        'last_name': founder_last_name,
        'email': founder_email,
        'created_at': datetime.now(timezone.utc).isoformat()
    })
    print("Genesis block created.")

    # Add the founder registration as the first page after genesis
    Blockchain.add_page(
        data=founder_data,
        validator=founder_email,
        signature='GENESIS'
    )
    print("Founder registration recorded on the blockchain.")
    print("Founder account created successfully.")

if __name__ == "__main__":
    # Ensure the blockchain is initialized before creating the founder
    Blockchain.load_chain()
    create_founder_account()
