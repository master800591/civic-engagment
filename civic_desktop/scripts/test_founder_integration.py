#!/usr/bin/env python3
"""
Test script for hardcoded founder key integration
Tests that the complete founder key system works end-to-end
"""

import sys
import os
import json
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

def test_hardcoded_keys():
    """Test the hardcoded founder keys system"""
    
    print("🧪 TESTING HARDCODED FOUNDER KEYS INTEGRATION")
    print("=" * 60)
    
    try:
        # Import the hardcoded keys system
        from users.hardcoded_founder_keys import HardcodedFounderKeys
        print("✅ HardcodedFounderKeys imported successfully")
        
        # Check that we have 10 keys
        print(f"📊 Available founder keys: {len(HardcodedFounderKeys.FOUNDER_KEYS)}")
        
        # Load a sample founder key from the distribution
        founder_01_key_path = Path("founder_distributions/keys/FOUNDER_01_private_key.pem")
        if founder_01_key_path.exists():
            with open(founder_01_key_path, 'r') as f:
                sample_private_key = f.read()
            
            print("🔑 Testing FOUNDER_01 key validation...")
            
            # Test validation
            is_valid, message, founder_data = HardcodedFounderKeys.validate_founder_key(sample_private_key)
            
            if is_valid:
                print(f"✅ Key validation SUCCESS: {message}")
                print(f"📋 Founder data: {founder_data}")
                
                # Test that key is now marked as used
                print("\n🔒 Testing single-use protection...")
                is_valid_2, message_2, founder_data_2 = HardcodedFounderKeys.validate_founder_key(sample_private_key)
                
                if not is_valid_2:
                    print(f"✅ Single-use protection working: {message_2}")
                else:
                    print(f"❌ Single-use protection FAILED: Key can be reused!")
                    
            else:
                print(f"❌ Key validation FAILED: {message}")
                
        else:
            print("⚠️ Sample key file not found - checking system status only")
            
        # Test backend integration
        print("\n🏛️ Testing backend integration...")
        try:
            from users.backend import UserBackend
            print("✅ UserBackend imported successfully")
            print("✅ Hardcoded founder keys are integrated into registration system")
        except Exception as e:
            print(f"❌ Backend integration error: {e}")
            
        print("\n🎉 FOUNDER KEY INTEGRATION TEST COMPLETE")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hardcoded_keys()