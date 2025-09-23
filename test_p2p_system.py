"""
P2P Network Testing Suite
========================

Comprehensive testing suite for the P2P networking system:
- Server startup and API endpoints
- Peer management and discovery
- Blockchain synchronization
- Configuration validation
- Integration testing
"""

import sys
import os
import time
import requests
import threading
import json
from datetime import datetime
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class P2PNetworkTester:
    """Comprehensive P2P network testing"""
    
    def __init__(self):
        self.test_results = []
        self.server_thread = None
        self.test_config = {
            "p2p": {
                "enabled": True,
                "server_port": 8001,  # Different port for testing
                "auto_discover": False,  # Disable for testing
                "sync_interval": 10,
                "bootstrap_nodes": [],
                "network_id": "test_network"
            }
        }
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
    
    def test_p2p_manager_initialization(self):
        """Test P2P manager initialization"""
        try:
            from civic_desktop.blockchain.p2p_manager import P2PManager
            
            manager = P2PManager()
            success = manager.initialize(self.test_config)
            
            self.log_test("P2P Manager Initialization", 
                         success, "Manager initialized successfully")
            return manager
            
        except Exception as e:
            self.log_test("P2P Manager Initialization", 
                         False, f"Initialization failed: {e}")
            return None
    
    def test_http_server_startup(self, manager):
        """Test HTTP server startup"""
        if not manager:
            self.log_test("HTTP Server Startup", False, "No manager available")
            return False
            
        try:
            # Check if server is running
            status = manager.get_status()
            server_running = status.get('server_running', False)
            
            if server_running:
                # Test server health endpoint - check actual running port from status
                server_url = status.get('server_url')
                if server_url:
                    response = requests.get(f"{server_url}/api/health", timeout=5)
                else:
                    # Fallback to localhost:8000 (default)
                    response = requests.get("http://localhost:8000/api/health", timeout=5)
                
                if response.status_code == 200:
                    self.log_test("HTTP Server Startup", True, 
                                 f"Server responding at {server_url or 'http://localhost:8000'}")
                    return True
                else:
                    self.log_test("HTTP Server Startup", False, 
                                 f"Server not responding: {response.status_code}")
            else:
                self.log_test("HTTP Server Startup", False, "Server not running")
                
        except Exception as e:
            self.log_test("HTTP Server Startup", False, f"Server test failed: {e}")
        
        return False
    
    def test_peer_management(self, manager):
        """Test peer management functions"""
        if not manager:
            self.log_test("Peer Management", False, "No manager available")
            return
            
        try:
            # Test adding a peer
            test_peer = "http://test-peer:8000"
            add_success = manager.add_peer(test_peer)
            
            # Test getting status with peer count
            status = manager.get_status()
            peer_count = status.get('peer_count', 0)
            
            # Test removing the peer
            remove_success = manager.remove_peer(test_peer)
            
            if add_success and remove_success:
                self.log_test("Peer Management", True, 
                             f"Add/remove peer operations successful")
            else:
                self.log_test("Peer Management", False, 
                             f"Peer operations failed: add={add_success}, remove={remove_success}")
                
        except Exception as e:
            self.log_test("Peer Management", False, f"Peer management error: {e}")
    
    def test_blockchain_integration(self):
        """Test blockchain integration"""
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            from civic_desktop.blockchain.p2p import broadcast_to_peers
            
            # Test creating a test block with proper format
            test_data = {
                "action": "test_action", 
                "details": "p2p_integration_test",
                "timestamp": datetime.now().isoformat(),
                "user": "test@example.com"
            }
            
            # Try to add a page to blockchain
            success = Blockchain.add_page(test_data, "test@example.com")
            
            if success:
                self.log_test("Blockchain Integration", True, 
                             "Blockchain operations working")
            else:
                self.log_test("Blockchain Integration", False, 
                             "Failed to add blockchain page")
                
        except Exception as e:
            self.log_test("Blockchain Integration", False, 
                         f"Blockchain integration error: {e}")
    
    def test_configuration_system(self):
        """Test configuration system"""
        try:
            from civic_desktop.blockchain.p2p_manager import load_p2p_config
            
            # Test loading configuration
            config = load_p2p_config()
            
            if config and 'p2p' in config:
                self.log_test("Configuration System", True, 
                             "Configuration loaded successfully")
            else:
                self.log_test("Configuration System", False, 
                             "Configuration not found or invalid")
                
        except Exception as e:
            self.log_test("Configuration System", False, 
                         f"Configuration error: {e}")
    
    def test_api_endpoints(self, manager):
        """Test P2P API endpoints"""
        if not manager:
            self.log_test("API Endpoints", False, "No manager available")
            return
            
        try:
            status = manager.get_status()
            if not status.get('server_running', False):
                self.log_test("API Endpoints", False, "Server not running")
                return
                
            server_url = status.get('server_url', f"http://localhost:{self.test_config['p2p']['server_port']}")
            
            # Test health endpoint
            response = requests.get(f"{server_url}/api/health", timeout=5)
            health_ok = response.status_code == 200
            
            # Test blockchain info endpoint
            response = requests.get(f"{server_url}/api/blockchain/info", timeout=5)
            info_ok = response.status_code == 200
            
            if health_ok and info_ok:
                self.log_test("API Endpoints", True, "All API endpoints responding")
            else:
                self.log_test("API Endpoints", False, 
                             f"API failures: health={health_ok}, info={info_ok}")
                
        except Exception as e:
            self.log_test("API Endpoints", False, f"API test error: {e}")
    
    def test_synchronization_system(self, manager):
        """Test blockchain synchronization"""
        if not manager:
            self.log_test("Synchronization System", False, "No manager available")
            return
            
        try:
            # Test sync trigger
            sync_success = manager.sync_now()
            
            # Check sync status
            status = manager.get_status()
            sync_running = status.get('sync_running', False)
            
            if sync_success and sync_running:
                self.log_test("Synchronization System", True, 
                             "Synchronization system operational")
            else:
                self.log_test("Synchronization System", False, 
                             f"Sync issues: trigger={sync_success}, running={sync_running}")
                
        except Exception as e:
            self.log_test("Synchronization System", False, 
                         f"Synchronization error: {e}")
    
    def test_p2p_tab_integration(self):
        """Test P2P tab integration"""
        try:
            from civic_desktop.blockchain.p2p_tab import P2PNetworkTab
            
            # This would normally require a QApplication, but we can test import
            # and basic instantiation
            tab_class = P2PNetworkTab
            
            if tab_class:
                self.log_test("P2P Tab Integration", True, 
                             "P2P tab module imports successfully")
            else:
                self.log_test("P2P Tab Integration", False, 
                             "P2P tab import failed")
                
        except Exception as e:
            self.log_test("P2P Tab Integration", False, 
                         f"P2P tab integration error: {e}")
    
    def run_all_tests(self):
        """Run complete P2P testing suite"""
        print("🧪 Starting P2P Network Testing Suite")
        print("=" * 50)
        
        # Test 1: Configuration
        self.test_configuration_system()
        
        # Test 2: P2P Manager
        manager = self.test_p2p_manager_initialization()
        
        # Test 3: HTTP Server
        server_ok = self.test_http_server_startup(manager)
        
        # Test 4: API Endpoints (if server is running)
        if server_ok:
            self.test_api_endpoints(manager)
        
        # Test 5: Peer Management
        self.test_peer_management(manager)
        
        # Test 6: Synchronization
        self.test_synchronization_system(manager)
        
        # Test 7: Blockchain Integration
        self.test_blockchain_integration()
        
        # Test 8: P2P Tab Integration
        self.test_p2p_tab_integration()
        
        # Clean up
        if manager:
            try:
                manager.stop()
            except:
                pass
        
        # Print results
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("🏁 P2P Testing Suite Results")
        print("=" * 50)
        
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
        
        # Overall assessment
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! P2P system is fully operational.")
        elif passed_tests >= total_tests * 0.75:
            print("\n⚠️ Most tests passed. P2P system is mostly functional with minor issues.")
        elif passed_tests >= total_tests * 0.5:
            print("\n🔧 Some tests failed. P2P system needs attention.")
        else:
            print("\n🚨 Many tests failed. P2P system requires significant fixes.")

def main():
    """Main testing function"""
    print("Starting P2P Network Test Suite...")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    
    # Run tests
    tester = P2PNetworkTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()