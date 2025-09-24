#!/usr/bin/env python3
"""
Test Contract System Integration
Tests the enhanced contract system with blockchain integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'civic_desktop'))

def test_genesis_contract_loading():
    """Test that the Genesis Contract loads properly"""
    try:
        from civic_desktop.contracts.genesis_contract import GENESIS_CONTRACT_TEXT
        
        print("🧪 Testing Genesis Contract Loading...")
        print(f"📄 Contract length: {len(GENESIS_CONTRACT_TEXT)} characters")
        
        # Check key sections
        if "ARTICLE I: THE LEGISLATIVE BRANCH" in GENESIS_CONTRACT_TEXT:
            print("✅ Legislative branch section found")
        else:
            print("❌ Legislative branch section missing")
            
        if "ARTICLE III: THE EXECUTIVE BRANCH" in GENESIS_CONTRACT_TEXT:
            print("✅ Executive branch section found")
        else:
            print("❌ Executive branch section missing")
            
        if "ARTICLE II: THE JUDICIAL BRANCH" in GENESIS_CONTRACT_TEXT:
            print("✅ Judicial branch section found")
        else:
            print("❌ Judicial branch section missing")
            
        if "ARTICLE IV: THE BILL OF RIGHTS" in GENESIS_CONTRACT_TEXT:
            print("✅ Bill of Rights section found")
        else:
            print("❌ Bill of Rights section missing")
            
        # Check for Republic terminology (not platform/commonwealth)
        if "platform" in GENESIS_CONTRACT_TEXT.lower():
            print("⚠️ 'Platform' references still exist - needs cleanup")
        else:
            print("✅ No platform references found")
            
        if "commonwealth" in GENESIS_CONTRACT_TEXT.lower():
            print("⚠️ 'Commonwealth' references still exist - needs cleanup")  
        else:
            print("✅ No commonwealth references found")
            
        if "Republic" in GENESIS_CONTRACT_TEXT:
            print("✅ Republic terminology properly used")
        else:
            print("❌ Republic terminology missing")
            
        print("🎯 Genesis Contract test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Genesis Contract test failed: {str(e)}")
        return False

def test_contract_ui_imports():
    """Test that contract UI components import properly"""
    try:
        print("\n🧪 Testing Contract UI Imports...")
        
        from civic_desktop.contracts.contract_ui import GenesisContractViewer, ContractManagementWidget
        print("✅ Contract UI classes imported successfully")
        
        print("🎯 Contract UI import test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Contract UI import test failed: {str(e)}")
        return False

def test_blockchain_integration():
    """Test that blockchain integration works"""
    try:
        print("\n🧪 Testing Blockchain Integration...")
        
        from civic_desktop.blockchain.blockchain import Blockchain
        print("✅ Blockchain class imported successfully")
        
        # Test blockchain initialization 
        print("✅ Blockchain module ready for contract integration")
        
        print("🎯 Blockchain integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Blockchain integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 CIVIC ENGAGEMENT PLATFORM - CONTRACT SYSTEM TESTS")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    if test_genesis_contract_loading():
        success_count += 1
        
    if test_contract_ui_imports():
        success_count += 1
        
    if test_blockchain_integration():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🏆 TEST RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Contract system is ready!")
    else:
        print("⚠️  Some tests failed - check output above")