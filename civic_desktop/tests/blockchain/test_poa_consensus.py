"""
PROOF OF AUTHORITY (PoA) CONSENSUS TESTS
Tests the blockchain PoA consensus mechanism, validator management, and signature collection
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_validator_registration():
    """Test validator registration with PoA requirements"""
    
    print("\n" + "=" * 60)
    print("🔐 TEST: Validator Registration (PoA Requirements)")
    print("=" * 60)
    
    try:
        from blockchain.blockchain import CivicBlockchain
        
        blockchain = CivicBlockchain()
        print("✅ Blockchain initialized")
        
        # Test 1: Register an elected representative as validator
        print("\n📝 Test 1: Register elected representative as validator")
        success, message = blockchain.register_validator(
            user_email="rep@civic.platform",
            public_key="test_public_key_123",
            role="contract_representative",
            elected_status=True
        )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ Failed: {message}")
            return False
        
        # Test 2: Try to register non-elected member (should fail)
        print("\n📝 Test 2: Try to register regular member (should fail)")
        success, message = blockchain.register_validator(
            user_email="member@civic.platform",
            public_key="test_public_key_456",
            role="contract_member",
            elected_status=False
        )
        
        if not success:
            print(f"✅ Correctly rejected: {message}")
        else:
            print(f"❌ Should have failed but succeeded")
            return False
        
        # Test 3: Try to register non-elected representative (should fail)
        print("\n📝 Test 3: Try to register non-elected representative (should fail)")
        success, message = blockchain.register_validator(
            user_email="notelected@civic.platform",
            public_key="test_public_key_789",
            role="contract_representative",
            elected_status=False
        )
        
        if not success:
            print(f"✅ Correctly rejected: {message}")
        else:
            print(f"❌ Should have failed but succeeded")
            return False
        
        # Test 4: Register a senator
        print("\n📝 Test 4: Register elected senator as validator")
        success, message = blockchain.register_validator(
            user_email="senator@civic.platform",
            public_key="test_public_key_sen",
            role="contract_senator",
            elected_status=True
        )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ Failed: {message}")
            return False
        
        # Test 5: Register an elder
        print("\n📝 Test 5: Register elder as validator")
        success, message = blockchain.register_validator(
            user_email="elder@civic.platform",
            public_key="test_public_key_elder",
            role="contract_elder",
            elected_status=False  # Elders don't need elected status
        )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ Failed: {message}")
            return False
        
        # Test 6: Try to register duplicate validator
        print("\n📝 Test 6: Try to register duplicate validator (should fail)")
        success, message = blockchain.register_validator(
            user_email="rep@civic.platform",
            public_key="test_public_key_123",
            role="contract_representative",
            elected_status=True
        )
        
        if not success:
            print(f"✅ Correctly rejected: {message}")
        else:
            print(f"❌ Should have failed but succeeded")
            return False
        
        print("\n✅ All validator registration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signature_collection():
    """Test validator signature collection for PoA consensus"""
    
    print("\n" + "=" * 60)
    print("✍️ TEST: Validator Signature Collection")
    print("=" * 60)
    
    try:
        from blockchain.blockchain import CivicBlockchain
        
        blockchain = CivicBlockchain()
        
        # Register multiple validators
        print("\n📝 Setting up validators...")
        validators = [
            ("val1@civic.platform", "contract_representative", True),
            ("val2@civic.platform", "contract_senator", True),
            ("val3@civic.platform", "contract_elder", False),
        ]
        
        for email, role, elected in validators:
            success, msg = blockchain.register_validator(
                email, f"key_{email}", role, elected
            )
            if success:
                print(f"✅ Registered: {email}")
            else:
                print(f"❌ Failed to register {email}: {msg}")
        
        # Test signature collection
        print("\n📝 Testing signature collection...")
        test_hash = "test_block_hash_12345"
        signatures = blockchain.collect_validator_signatures(test_hash, 'page')
        
        print(f"✅ Collected {len(signatures)} signatures")
        print(f"   Required: {blockchain._calculate_required_signatures(3)}")
        
        if len(signatures) >= blockchain._calculate_required_signatures(3):
            print("✅ Consensus reached!")
        else:
            print("❌ Insufficient signatures for consensus")
            return False
        
        # Verify signature structure
        print("\n📝 Verifying signature structure...")
        for sig in signatures:
            required_fields = ['validator_id', 'validator_email', 'block_hash', 'timestamp']
            for field in required_fields:
                if field not in sig:
                    print(f"❌ Missing field: {field}")
                    return False
        
        print("✅ All signatures have required fields")
        
        print("\n✅ Signature collection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validator_lifecycle():
    """Test validator deactivation and reactivation"""
    
    print("\n" + "=" * 60)
    print("🔄 TEST: Validator Lifecycle Management")
    print("=" * 60)
    
    try:
        from blockchain.blockchain import CivicBlockchain
        
        blockchain = CivicBlockchain()
        
        # Register a validator
        print("\n📝 Registering validator...")
        success, msg = blockchain.register_validator(
            "lifecycle_test@civic.platform",
            "test_key",
            "contract_representative",
            True
        )
        print(f"{'✅' if success else '❌'} {msg}")
        
        # Get validator info
        print("\n📝 Getting validator info...")
        success, msg, info = blockchain.get_validator_info("lifecycle_test@civic.platform")
        if success and info:
            print(f"✅ Found validator: {info['validator_id']}")
            print(f"   Status: {info['status']}")
        else:
            print(f"❌ Could not get validator info")
            return False
        
        # Deactivate validator
        print("\n📝 Deactivating validator (term ended)...")
        success, msg = blockchain.deactivate_validator(
            "lifecycle_test@civic.platform",
            "Term ended"
        )
        print(f"{'✅' if success else '❌'} {msg}")
        
        # Verify deactivation
        success, msg, info = blockchain.get_validator_info("lifecycle_test@civic.platform")
        if info['status'] == 'inactive':
            print(f"✅ Validator correctly deactivated")
        else:
            print(f"❌ Validator status incorrect: {info['status']}")
            return False
        
        # Reactivate validator
        print("\n📝 Reactivating validator (re-elected)...")
        success, msg = blockchain.reactivate_validator("lifecycle_test@civic.platform")
        print(f"{'✅' if success else '❌'} {msg}")
        
        # Verify reactivation
        success, msg, info = blockchain.get_validator_info("lifecycle_test@civic.platform")
        if info['status'] == 'active':
            print(f"✅ Validator correctly reactivated")
        else:
            print(f"❌ Validator status incorrect: {info['status']}")
            return False
        
        print("\n✅ Validator lifecycle tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_poa_page_creation():
    """Test that pages are created with validator signatures"""
    
    print("\n" + "=" * 60)
    print("📄 TEST: PoA Page Creation with Signatures")
    print("=" * 60)
    
    try:
        from blockchain.blockchain import CivicBlockchain
        
        blockchain = CivicBlockchain()
        
        # Register validators first
        print("\n📝 Setting up validators...")
        validators = [
            ("poa1@civic.platform", "contract_representative", True),
            ("poa2@civic.platform", "contract_senator", True),
        ]
        
        for email, role, elected in validators:
            blockchain.register_validator(email, f"key_{email}", role, elected)
        
        # Create a page
        print("\n📝 Creating page with PoA consensus...")
        success, message, page_id = blockchain.add_page(
            action_type="test_action",
            user_email="testuser@civic.platform",
            data={"test": "data"}
        )
        
        print(f"{'✅' if success else '❌'} {message}")
        if not success:
            return False
        
        # Verify page has validator signatures
        print("\n📝 Verifying page has validator signatures...")
        pages_data = blockchain._load_pages_data()
        active_pages = pages_data.get('active_pages', [])
        
        if not active_pages:
            print("❌ No pages found")
            return False
        
        last_page = active_pages[-1]
        
        if 'validator_signatures' not in last_page:
            print("❌ Page missing validator_signatures field")
            return False
        
        validator_sigs = last_page['validator_signatures']
        print(f"✅ Page has {len(validator_sigs)} validator signatures")
        
        required = blockchain._calculate_required_signatures(2)
        if len(validator_sigs) >= required:
            print(f"✅ Consensus reached ({len(validator_sigs)}/{required} required)")
        else:
            print(f"⚠️ Warning: Only {len(validator_sigs)}/{required} signatures")
        
        print("\n✅ PoA page creation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_consensus_requirements():
    """Test that consensus requirements are correctly calculated"""
    
    print("\n" + "=" * 60)
    print("🔢 TEST: Consensus Requirements Calculation")
    print("=" * 60)
    
    try:
        from blockchain.blockchain import CivicBlockchain
        
        blockchain = CivicBlockchain()
        
        # Test different validator counts
        test_cases = [
            (0, 0),  # No validators
            (1, 1),  # 1 validator needs 1 signature
            (2, 2),  # 2 validators need 2 (majority)
            (3, 2),  # 3 validators need 2 (majority)
            (4, 3),  # 4 validators need 3 (majority)
            (5, 3),  # 5 validators need 3 (majority)
            (6, 4),  # 6 validators need 4 (majority)
            (7, 4),  # 7 validators need 4 (majority)
        ]
        
        print("\n📝 Testing consensus calculations...")
        all_passed = True
        
        for total, expected in test_cases:
            required = blockchain._calculate_required_signatures(total)
            status = "✅" if required == expected else "❌"
            print(f"{status} {total} validators → {required} required (expected {expected})")
            
            if required != expected:
                all_passed = False
        
        if all_passed:
            print("\n✅ All consensus calculations correct!")
            return True
        else:
            print("\n❌ Some consensus calculations incorrect")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_poa_tests():
    """Run all PoA consensus tests"""
    
    print("\n" + "=" * 70)
    print("🏛️  CIVIC BLOCKCHAIN - PROOF OF AUTHORITY (PoA) TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Validator Registration", test_validator_registration),
        ("Signature Collection", test_signature_collection),
        ("Validator Lifecycle", test_validator_lifecycle),
        ("PoA Page Creation", test_poa_page_creation),
        ("Consensus Requirements", test_consensus_requirements),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! PoA consensus system working correctly.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review output above.")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_poa_tests()
    sys.exit(0 if success else 1)
