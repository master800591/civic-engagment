#!/usr/bin/env python3
"""
Quick Genesis Block Validation
===============================

Simple validation script to check genesis block improvements without full app execution.
"""

import os
import json
from datetime import datetime

def validate_genesis_file():
    """Validate the enhanced genesis block file"""
    print("🔍 VALIDATING GENESIS BLOCK FILE")
    print("=" * 50)
    
    genesis_path = 'civic_desktop/blockchain/genesis_block.json'
    
    if not os.path.exists(genesis_path):
        print("❌ Genesis block file not found")
        return False
        
    try:
        with open(genesis_path, 'r') as f:
            genesis = json.load(f)
            
        print(f"📄 Genesis Block Structure:")
        print(f"   Type: {genesis.get('type', 'MISSING')}")
        print(f"   Version: {genesis.get('version', 'MISSING')}")
        print(f"   Platform: {genesis.get('platform', 'MISSING')}")
        print(f"   Consensus: {genesis.get('consensus', 'MISSING')}")
        print(f"   Governance: {genesis.get('governance', 'MISSING')}")
        
        founder = genesis.get('founder', {})
        print(f"   Founder Name: {founder.get('first_name', 'MISSING')} {founder.get('last_name', 'MISSING')}")
        print(f"   Founder Email: {founder.get('email', 'MISSING')}")
        
        public_key = founder.get('public_key', '')
        if 'BEGIN PUBLIC KEY' in public_key:
            print("   ✅ Real RSA Public Key Found")
        elif public_key == 'GENESIS_PLACEHOLDER':
            print("   ⚠️ Placeholder Public Key")
        else:
            print(f"   ❓ Unknown Key Format: {public_key[:50]}...")
            
        constitution = genesis.get('constitution', {})
        if constitution:
            print("   ✅ Constitution Present")
            voting_thresholds = constitution.get('voting_thresholds', {})
            print(f"      Elder Veto: {voting_thresholds.get('contract_elder_veto', 'MISSING')}")
            print(f"      Founder Consensus: {voting_thresholds.get('founder_consensus', 'MISSING')}")
        else:
            print("   ❌ Constitution Missing")
            
        network_params = genesis.get('network_parameters', {})
        if network_params:
            print("   ✅ Network Parameters Present")
            print(f"      Consensus: {network_params.get('consensus_mechanism', 'MISSING')}")
            print(f"      Validator Selection: {network_params.get('validator_selection', 'MISSING')}")
        else:
            print("   ❌ Network Parameters Missing")
            
        genesis_hash = genesis.get('genesis_hash')
        if genesis_hash:
            print(f"   ✅ Genesis Hash: {genesis_hash[:16]}...")
        else:
            print("   ❌ Genesis Hash Missing")
            
        # Calculate basic quality score
        score = 0
        
        # Basic structure (40 points)
        if genesis.get('type') == 'genesis': score += 5
        if genesis.get('version'): score += 5
        if genesis.get('platform'): score += 5
        if genesis.get('consensus'): score += 5
        if genesis.get('governance'): score += 5
        if founder.get('email'): score += 5
        if constitution: score += 5
        if network_params: score += 5
        
        # Cryptographic features (30 points)
        if 'BEGIN PUBLIC KEY' in public_key: score += 20
        elif public_key and public_key != 'GENESIS_PLACEHOLDER': score += 10
        if genesis_hash: score += 10
        
        # Completeness (30 points)
        if constitution.get('voting_thresholds'): score += 10
        if constitution.get('authority_hierarchy'): score += 10
        if network_params.get('consensus_mechanism'): score += 10
        
        print(f"\n📊 Genesis File Quality Score: {score}/100")
        
        if score >= 90:
            print("🏆 EXCELLENT - Production ready!")
        elif score >= 75:
            print("✅ GOOD - Minor improvements needed")
        elif score >= 60:
            print("⚠️ ACCEPTABLE - Several improvements needed")
        else:
            print("❌ POOR - Major fixes required")
            
        return score >= 75
        
    except Exception as e:
        print(f"❌ Error reading genesis file: {e}")
        return False

def validate_blockchain_db():
    """Validate blockchain database structure"""
    print("\n⛓️ VALIDATING BLOCKCHAIN DATABASE")
    print("=" * 50)
    
    blockchain_path = 'civic_desktop/blockchain/blockchain_db.json'
    
    if not os.path.exists(blockchain_path):
        print("❌ Blockchain database not found")
        return False
        
    try:
        with open(blockchain_path, 'r') as f:
            chain = json.load(f)
            
        pages = chain.get('pages', [])
        print(f"📊 Blockchain Statistics:")
        print(f"   Total pages: {len(pages)}")
        
        if pages:
            first_block = pages[0]
            print(f"   First block action: {first_block.get('data', {}).get('action', 'UNKNOWN')}")
            print(f"   First block validator: {first_block.get('validator', 'UNKNOWN')}")
            print(f"   First block signature: {first_block.get('signature', 'UNKNOWN')}")
            
            if first_block.get('data', {}).get('action') == 'genesis_creation':
                print("   ✅ Genesis block is correctly positioned as first block")
                return True
            else:
                print("   ⚠️ First block is not genesis")
                return False
        else:
            print("   ℹ️ Blockchain is empty")
            return True
            
    except Exception as e:
        print(f"❌ Error reading blockchain: {e}")
        return False

def validate_validators_db():
    """Validate validator registry"""
    print("\n👥 VALIDATING VALIDATOR REGISTRY")
    print("=" * 50)
    
    validators_path = 'civic_desktop/blockchain/validators_db.json'
    
    if not os.path.exists(validators_path):
        print("❌ Validator registry not found")
        return False
        
    try:
        with open(validators_path, 'r') as f:
            validators = json.load(f)
            
        print(f"📊 Validator Statistics:")
        print(f"   Total validators: {len(validators)}")
        
        if validators:
            genesis_validator = validators[0]
            print(f"   Genesis validator: {genesis_validator.get('email', 'UNKNOWN')}")
            print(f"   Active: {genesis_validator.get('active', False)}")
            
            public_key = genesis_validator.get('public_key', '')
            if 'BEGIN PUBLIC KEY' in public_key:
                print("   ✅ Real RSA public key")
            elif public_key == 'GENESIS_PLACEHOLDER':
                print("   ⚠️ Placeholder public key")
            else:
                print(f"   ❓ Unknown key: {public_key[:30]}...")
                
            return True
        else:
            print("   ℹ️ No validators registered")
            return False
            
    except Exception as e:
        print(f"❌ Error reading validators: {e}")
        return False

def main():
    """Main validation"""
    print("🏛️ GENESIS BLOCK VALIDATION SUITE")
    print("=" * 60)
    
    results = []
    
    # Test each component
    results.append(validate_genesis_file())
    results.append(validate_blockchain_db())
    results.append(validate_validators_db())
    
    # Overall result
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 OVERALL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Genesis system is ready!")
    elif passed >= total * 0.66:
        print("✅ MOSTLY READY - Minor issues to address")
    else:
        print("❌ NEEDS WORK - Several issues found")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()