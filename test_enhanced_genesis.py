#!/usr/bin/env python3
"""
Test Enhanced Genesis Block Creation
=====================================

This script tests the enhanced genesis block creation system with:
1. Real RSA cryptographic keys
2. Enhanced metadata and constitutional framework
3. Proper blockchain positioning (genesis as block 0)
4. Production-ready genesis features
"""

import sys
import os
import json
import shutil
from datetime import datetime, timezone

# Add the civic_desktop directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'civic_desktop'))

def backup_existing_data():
    """Backup existing data before testing"""
    backup_files = [
        'civic_desktop/users/users_db.json',
        'civic_desktop/blockchain/blockchain_db.json', 
        'civic_desktop/blockchain/validators_db.json',
        'civic_desktop/blockchain/genesis_block.json'
    ]
    
    for file_path in backup_files:
        if os.path.exists(file_path):
            backup_path = f"{file_path}.test_backup"
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up: {file_path}")

def restore_data():
    """Restore original data after testing"""
    backup_files = [
        'civic_desktop/users/users_db.json',
        'civic_desktop/blockchain/blockchain_db.json',
        'civic_desktop/blockchain/validators_db.json', 
        'civic_desktop/blockchain/genesis_block.json'
    ]
    
    for file_path in backup_files:
        backup_path = f"{file_path}.test_backup"
        if os.path.exists(backup_path):
            shutil.move(backup_path, file_path)
            print(f"✅ Restored: {file_path}")

def clean_test_environment():
    """Clean test environment for fresh genesis creation"""
    files_to_remove = [
        'civic_desktop/users/users_db.json',
        'civic_desktop/blockchain/blockchain_db.json',
        'civic_desktop/blockchain/validators_db.json',
        'civic_desktop/blockchain/genesis_block.json'
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Removed: {file_path}")

def test_enhanced_genesis_creation():
    """Test the enhanced genesis block creation process"""
    print("\n🧪 TESTING ENHANCED GENESIS BLOCK CREATION")
    print("=" * 60)
    
    try:
        # Import after path setup
        from users.backend import UserBackend
        from blockchain.blockchain import Blockchain, ValidatorRegistry
        from blockchain.signatures import BlockchainSigner
        
        # Create test founder user
        test_founder = {
            'first_name': 'Genesis',
            'last_name': 'Founder',
            'email': 'genesis.founder@civic.test',
            'password': 'GenesisPassword123!',
            'city': 'Capital City',
            'state': 'Genesis State',
            'country': 'Test Nation',
            'id_document': 'GENESIS001'
        }
        
        print(f"👤 Creating test founder: {test_founder['email']}")
        
        # Test user registration (should trigger enhanced genesis creation)
        result = UserBackend.register_user(test_founder)
        
        if result[0]:  # Success
            print(f"✅ User registration successful: {result[1]}")
        else:
            print(f"❌ User registration failed: {result[1]}")
            return False
            
        # Verify enhanced genesis block file
        genesis_path = 'civic_desktop/blockchain/genesis_block.json'
        if os.path.exists(genesis_path):
            with open(genesis_path, 'r') as f:
                genesis_data = json.load(f)
                
            print(f"\n📄 Genesis Block File Analysis:")
            print(f"   Type: {genesis_data.get('type')}")
            print(f"   Version: {genesis_data.get('version')}")
            print(f"   Platform: {genesis_data.get('platform')}")
            print(f"   Consensus: {genesis_data.get('consensus')}")
            print(f"   Governance: {genesis_data.get('governance')}")
            print(f"   Founder: {genesis_data.get('founder', {}).get('first_name')} {genesis_data.get('founder', {}).get('last_name')}")
            print(f"   Public Key: {'Real RSA Key' if 'BEGIN PUBLIC KEY' in genesis_data.get('founder', {}).get('public_key', '') else 'Placeholder'}")
            print(f"   Constitution: {'Present' if genesis_data.get('constitution') else 'Missing'}")
            print(f"   Network Config: {'Present' if genesis_data.get('network_parameters') else 'Missing'}")
            print(f"   Genesis Hash: {'Present' if genesis_data.get('genesis_hash') else 'Missing'}")
        else:
            print("❌ Genesis block file not found")
            return False
            
        # Verify blockchain contains genesis block as first block
        chain = Blockchain.load_chain()
        pages = chain.get('pages', [])
        
        print(f"\n⛓️ Blockchain Analysis:")
        print(f"   Total blocks: {len(pages)}")
        
        if pages:
            first_block = pages[0]
            print(f"   First block action: {first_block.get('data', {}).get('action')}")
            print(f"   First block validator: {first_block.get('validator')}")
            print(f"   First block signature: {first_block.get('signature')}")
            
            if first_block.get('data', {}).get('action') == 'genesis_creation':
                print("   ✅ Genesis block is correctly positioned as first block")
            else:
                print("   ⚠️ First block is not genesis")
                
        # Verify validator registry
        validators = ValidatorRegistry.load_validators()
        print(f"\n👥 Validator Registry Analysis:")
        print(f"   Total validators: {len(validators)}")
        
        if validators:
            genesis_validator = validators[0]
            print(f"   Genesis validator email: {genesis_validator.get('email')}")
            print(f"   Genesis validator active: {genesis_validator.get('active')}")
            public_key = genesis_validator.get('public_key', '')
            if 'BEGIN PUBLIC KEY' in public_key:
                print("   ✅ Real RSA public key found")
            else:
                print(f"   ⚠️ Placeholder key: {public_key}")
                
        # Calculate quality score
        score = calculate_enhanced_genesis_quality(genesis_data, pages, validators)
        print(f"\n📊 Enhanced Genesis Quality Score: {score}/100")
        
        if score >= 95:
            print("🏆 EXCELLENT - Production ready!")
        elif score >= 85:
            print("✅ GOOD - Minor improvements needed")
        elif score >= 70:
            print("⚠️ ACCEPTABLE - Several improvements needed")
        else:
            print("❌ POOR - Major fixes required")
            
        return score >= 85
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_enhanced_genesis_quality(genesis_data, blockchain_pages, validators):
    """Calculate quality score for enhanced genesis block"""
    score = 0
    max_score = 100
    
    # File structure and metadata (40 points)
    if genesis_data.get('type') == 'genesis':
        score += 5
    if genesis_data.get('version'):
        score += 5
    if genesis_data.get('platform'):
        score += 5
    if genesis_data.get('consensus') == 'proof_of_authority':
        score += 5
    if genesis_data.get('governance') == 'contract_based_democracy':
        score += 5
    if genesis_data.get('founder', {}).get('email'):
        score += 5
    if genesis_data.get('constitution'):
        score += 5
    if genesis_data.get('network_parameters'):
        score += 5
        
    # Cryptographic security (25 points)
    public_key = genesis_data.get('founder', {}).get('public_key', '')
    if 'BEGIN PUBLIC KEY' in public_key and len(public_key) > 100:
        score += 15  # Real RSA key
    elif public_key and public_key != 'GENESIS_PLACEHOLDER':
        score += 5   # Some key present
        
    if genesis_data.get('genesis_hash'):
        score += 10  # Genesis integrity hash
        
    # Blockchain integration (25 points)
    if blockchain_pages:
        first_block = blockchain_pages[0]
        if first_block.get('data', {}).get('action') == 'genesis_creation':
            score += 15  # Genesis is first block
        if first_block.get('signature') == 'GENESIS':
            score += 5   # Proper genesis signature
        if first_block.get('validator') == genesis_data.get('founder', {}).get('email'):
            score += 5   # Correct validator
            
    # Validator setup (10 points)
    if validators:
        genesis_validator = next((v for v in validators if v['email'] == genesis_data.get('founder', {}).get('email')), None)
        if genesis_validator:
            score += 5
            if genesis_validator.get('active'):
                score += 5
                
    return min(score, max_score)

def main():
    """Main test execution"""
    print("🏛️ ENHANCED GENESIS BLOCK TESTING SUITE")
    print("=" * 60)
    
    # Backup existing data
    print("\n📁 Backing up existing data...")
    backup_existing_data()
    
    try:
        # Clean environment for fresh test
        print("\n🧹 Cleaning test environment...")
        clean_test_environment()
        
        # Run enhanced genesis test
        success = test_enhanced_genesis_creation()
        
        if success:
            print("\n🎉 ENHANCED GENESIS BLOCK TEST PASSED!")
            print("   Your genesis system is production-ready!")
        else:
            print("\n❌ ENHANCED GENESIS BLOCK TEST FAILED!")
            print("   Review the issues above and fix them.")
            
    finally:
        # Restore original data
        print("\n🔄 Restoring original data...")
        restore_data()
        
    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()