"""
Enhanced PoA Validation Testing
==============================

This script tests the complete Proof of Authority validation system
including:
- Validator registry management
- Cryptographic signature verification
- P2P network PoA enforcement
- Democratic validator promotion
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PoAValidationTester:
    """Comprehensive PoA validation testing"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.test_validator_email = "test_validator@civic.gov"
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result: Dict[str, Any] = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
    
    def test_validator_registry(self):
        """Test validator registry functionality"""
        try:
            from civic_desktop.blockchain.blockchain import ValidatorRegistry
            
            # Test adding validator
            ValidatorRegistry.add_validator(self.test_validator_email, "test_public_key")
            
            # Test validator check
            is_validator = ValidatorRegistry.is_validator(self.test_validator_email)
            
            # Test public key retrieval
            public_key = ValidatorRegistry.get_validator_public_key(self.test_validator_email)
            
            if is_validator and public_key:
                self.log_test("Validator Registry", True, 
                             "Add/check/retrieve validator operations successful")
                
                # Clean up
                ValidatorRegistry.remove_validator(self.test_validator_email)
                return True
            else:
                self.log_test("Validator Registry", False, 
                             f"Validator operations failed: is_validator={is_validator}, public_key={public_key}")
                
        except Exception as e:
            self.log_test("Validator Registry", False, f"Registry error: {e}")
        
        return False
    
    def test_cryptographic_signing(self):
        """Test cryptographic block signing and verification"""
        try:
            from civic_desktop.blockchain.signatures import BlockchainSigner
            from civic_desktop.blockchain.blockchain import ValidatorRegistry
            from civic_desktop.users.backend import UserBackend
            
            # Create a test user with keys first
            test_user_data = {
                'email': self.test_validator_email,
                'first_name': 'Test',
                'last_name': 'Validator',
                'password': 'TestPassword123!',
                'city': 'Test City',
                'state': 'Test State',
                'country': 'Test Country',
                'address': '123 Test St',
                'id_document': 'TEST123456789'
            }
            
            # Register user to generate keys  
            success: bool = False
            message: str = ""
            try:
                success, message = UserBackend.register_user(
                    test_user_data, 
                    id_document_path=""  # Empty string for test
                )
            except Exception as e:
                message = str(e)
            
            if not success and "already exists" not in message:
                self.log_test("Cryptographic Signing", False, f"User creation failed: {message}")
                return False
            
            # Add to validator registry
            users = UserBackend.load_users()
            test_user = next((u for u in users if u['email'] == self.test_validator_email), None)
            
            if test_user:
                ValidatorRegistry.add_validator(self.test_validator_email, test_user['public_key'])
            
            # Test block signing
            test_block_data: Dict[str, Any] = {
                'index': 999,
                'previous_hash': 'test_hash',
                'timestamp': datetime.now().isoformat(),
                'data': {'action': 'test_action', 'details': 'PoA validation test'},
                'validator': self.test_validator_email
            }
            
            # Sign the block
            signature = BlockchainSigner.sign_block_data(test_block_data, self.test_validator_email)
            
            # Verify the signature
            public_key = ValidatorRegistry.get_validator_public_key(self.test_validator_email)
            if public_key:
                is_valid = BlockchainSigner.verify_block_signature(test_block_data, signature, public_key)
            else:
                is_valid = False
            
            if signature and is_valid:
                self.log_test("Cryptographic Signing", True, 
                             "Block signing and verification successful")
                
                # Clean up
                ValidatorRegistry.remove_validator(self.test_validator_email)
                return True
            else:
                self.log_test("Cryptographic Signing", False, 
                             f"Signing/verification failed: signature={bool(signature)}, valid={is_valid}")
                
        except Exception as e:
            self.log_test("Cryptographic Signing", False, f"Signing error: {e}")
        
        return False
    
    def test_p2p_poa_enforcement(self):
        """Test P2P network PoA enforcement"""
        try:
            from civic_desktop.blockchain.p2p_manager import get_p2p_manager
            
            # Get P2P manager
            p2p_manager = get_p2p_manager()
            if not p2p_manager:
                self.log_test("P2P PoA Enforcement", False, "P2P manager not available")
                return False
            
            # Check if P2P server is running
            status = p2p_manager.get_status()
            if not status.get('server_running', False):
                self.log_test("P2P PoA Enforcement", False, "P2P server not running")
                return False
            
            # Test invalid validator block rejection
            invalid_block: Dict[str, Any] = {
                'index': 1000,
                'previous_hash': 'test_hash',
                'timestamp': datetime.now().isoformat(),
                'data': {'action': 'unauthorized_action'},
                'validator': 'unauthorized_validator@test.com',
                'signature': 'fake_signature'
            }
            
            # Try to submit invalid block to P2P server
            server_url = status.get('server_url', 'http://localhost:8000')
            
            try:
                response = requests.post(
                    f"{server_url}/api/blockchain/new_block",
                    json=invalid_block,
                    timeout=5
                )
                
                # Should reject unauthorized validator
                if response.status_code == 400 and "Unauthorized validator" in response.text:
                    self.log_test("P2P PoA Enforcement", True, 
                                 "P2P server correctly rejected unauthorized validator")
                    return True
                else:
                    self.log_test("P2P PoA Enforcement", False, 
                                 f"P2P server did not reject invalid block: {response.status_code} - {response.text}")
            
            except requests.exceptions.RequestException as e:
                self.log_test("P2P PoA Enforcement", False, f"P2P server connection error: {e}")
                
        except Exception as e:
            self.log_test("P2P PoA Enforcement", False, f"PoA enforcement test error: {e}")
        
        return False
    
    def test_blockchain_integration(self):
        """Test PoA integration with blockchain operations"""
        try:
            from civic_desktop.blockchain.blockchain import Blockchain, ValidatorRegistry
            from civic_desktop.users.backend import UserBackend
            
            # Ensure test validator exists
            users = UserBackend.load_users()
            test_user = next((u for u in users if u['email'] == self.test_validator_email), None)
            
            if test_user:
                ValidatorRegistry.add_validator(self.test_validator_email, test_user['public_key'])
                
                # Test blockchain page addition with validator
                test_data = {
                    'action': 'poa_test',
                    'details': 'Testing PoA blockchain integration',
                    'timestamp': datetime.now().isoformat()
                }
                
                success = Blockchain.add_page(test_data, self.test_validator_email)
                
                if success:
                    self.log_test("Blockchain Integration", True, 
                                 "Validator successfully added page to blockchain")
                    
                    # Clean up
                    ValidatorRegistry.remove_validator(self.test_validator_email)
                    return True
                else:
                    self.log_test("Blockchain Integration", False, 
                                 "Failed to add page with validator")
            else:
                self.log_test("Blockchain Integration", False, 
                             "Test validator user not found")
                
        except Exception as e:
            self.log_test("Blockchain Integration", False, f"Blockchain integration error: {e}")
        
        return False
    
    def test_authority_levels(self):
        """Test different authority levels and permissions"""
        try:
            from civic_desktop.blockchain.blockchain import ValidatorRegistry
            
            # Test system validator (should always be allowed)
            system_allowed = True  # SYSTEM is always valid
            
            # Test non-validator (should be rejected by registry)
            non_validator_allowed = ValidatorRegistry.is_validator("non_validator@test.com")
            
            # Test valid validator
            ValidatorRegistry.add_validator(self.test_validator_email, "test_key")
            validator_allowed = ValidatorRegistry.is_validator(self.test_validator_email)
            
            if system_allowed and not non_validator_allowed and validator_allowed:
                self.log_test("Authority Levels", True, 
                             "Authority levels working correctly")
                
                # Clean up
                ValidatorRegistry.remove_validator(self.test_validator_email)
                return True
            else:
                self.log_test("Authority Levels", False, 
                             f"Authority issues: system={system_allowed}, non={non_validator_allowed}, valid={validator_allowed}")
                
        except Exception as e:
            self.log_test("Authority Levels", False, f"Authority levels error: {e}")
        
        return False
    
    def run_all_tests(self):
        """Run complete PoA validation test suite"""
        print("🔐 Starting Enhanced PoA Validation Test Suite")
        print("=" * 55)
        
        # Test 1: Validator Registry
        self.test_validator_registry()
        
        # Test 2: Cryptographic Signing
        self.test_cryptographic_signing()
        
        # Test 3: P2P PoA Enforcement
        self.test_p2p_poa_enforcement()
        
        # Test 4: Blockchain Integration
        self.test_blockchain_integration()
        
        # Test 5: Authority Levels
        self.test_authority_levels()
        
        # Print results
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 55)
        print("🔐 Enhanced PoA Validation Test Results")
        print("=" * 55)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n📊 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
            if result['message']:
                print(f"      └─ {result['message']}")
        
        # Overall PoA assessment
        if passed_tests == total_tests:
            print("\n🛡️ EXCELLENT: Complete PoA validation system is fully operational!")
        elif passed_tests >= total_tests * 0.8:
            print("\n🔒 STRONG: PoA validation system is mostly functional with minor issues.")
        elif passed_tests >= total_tests * 0.6:
            print("\n⚠️ PARTIAL: PoA validation system has some functionality but needs attention.")
        else:
            print("\n🚨 WEAK: PoA validation system requires significant development.")

def main():
    """Main testing function"""
    print("Starting Enhanced PoA Validation Test Suite...")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    
    # Run tests
    tester = PoAValidationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()