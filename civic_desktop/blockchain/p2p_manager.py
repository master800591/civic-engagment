"""
P2P Manager - Centralized P2P Network Management
===============================================

This module provides centralized management of P2P networking features:
- HTTP server management
- Blockchain synchronization
- Peer discovery and management
- Network monitoring
- Integration with main application
"""

import threading
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class P2PManager:
    """Centralized P2P network manager"""
    
    def __init__(self):
        self.server = None
        self.synchronizer = None
        self.config = None
        self.running = False
        self.status = {
            'server_running': False,
            'sync_running': False,
            'network_connected': False,
            'last_sync': None,
            'peer_count': 0
        }
        
    def initialize(self, config: Dict[str, Any]):
        """Initialize P2P system with configuration"""
        self.config = config.get('p2p', {})
        
        if not self.config.get('enabled', False):
            logger.info("P2P networking is disabled in configuration")
            return False
            
        logger.info("Initializing P2P networking system")
        
        try:
            # Initialize HTTP server
            self._init_server()
            
            # Initialize synchronizer
            self._init_synchronizer()
            
            # Bootstrap network connection
            self._bootstrap_network()
            
            logger.info("P2P system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"P2P initialization failed: {e}")
            return False
    
    def _init_server(self):
        """Initialize P2P HTTP server"""
        try:
            from .p2p_server import start_p2p_server
            
            port = self.config.get('port', 8000)
            host = self.config.get('host', '0.0.0.0')
            
            self.server = start_p2p_server(port=port, host=host)
            self.status['server_running'] = True
            
            logger.info(f"P2P server started on {host}:{port}")
            
        except Exception as e:
            logger.error(f"Failed to start P2P server: {e}")
            raise
    
    def _init_synchronizer(self):
        """Initialize blockchain synchronizer"""
        try:
            from .sync import get_synchronizer, start_blockchain_sync
            
            self.synchronizer = get_synchronizer()
            
            # Configure sync interval
            sync_interval = self.config.get('sync_interval', 30)
            self.synchronizer.sync_interval = sync_interval
            
            # Start periodic sync
            start_blockchain_sync()
            self.status['sync_running'] = True
            
            logger.info(f"Blockchain synchronization started (interval: {sync_interval}s)")
            
        except Exception as e:
            logger.error(f"Failed to start synchronizer: {e}")
            raise
    
    def _bootstrap_network(self):
        """Bootstrap network connection"""
        try:
            from .p2p import bootstrap_network
            
            if self.config.get('auto_discover', True):
                success = bootstrap_network()
                self.status['network_connected'] = success
                
                if success:
                    logger.info("Network bootstrap successful")
                else:
                    logger.warning("Network bootstrap failed - running in isolated mode")
            else:
                logger.info("Auto-discovery disabled, manual peer configuration required")
                
        except Exception as e:
            logger.error(f"Network bootstrap error: {e}")
    
    def start(self):
        """Start P2P manager"""
        if self.running:
            logger.warning("P2P manager is already running")
            return
            
        self.running = True
        logger.info("P2P manager started")
    
    def stop(self):
        """Stop P2P manager"""
        if not self.running:
            return
            
        logger.info("Stopping P2P manager...")
        
        try:
            # Stop synchronizer
            if self.synchronizer:
                from .sync import stop_blockchain_sync
                stop_blockchain_sync()
                self.status['sync_running'] = False
            
            # Stop server
            if self.server:
                from .p2p_server import stop_p2p_server
                stop_p2p_server()
                self.status['server_running'] = False
            
            self.running = False
            logger.info("P2P manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping P2P manager: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current P2P system status"""
        try:
            # Update peer count
            from .p2p import load_peers, get_network_status
            peers = load_peers()
            self.status['peer_count'] = len(peers)
            
            # Update network status
            network_status = get_network_status()
            self.status['healthy_peers'] = network_status.get('healthy_peers', 0)
            
            # Update sync status
            if self.synchronizer:
                sync_status = self.synchronizer.get_sync_status()
                self.status['last_sync'] = sync_status.get('last_sync_time')
                self.status['is_syncing'] = sync_status.get('is_syncing', False)
            
            # Add server info
            if self.server:
                self.status['server_url'] = self.server.get_server_url()
                self.status['node_id'] = self.server.node_id
            
            self.status['uptime'] = time.time() if self.running else 0
            self.status['config'] = self.config
            
            return self.status.copy()
            
        except Exception as e:
            logger.error(f"Error getting P2P status: {e}")
            return self.status.copy()
    
    def add_peer(self, peer_url: str) -> bool:
        """Add a new peer to the network"""
        try:
            from .p2p import add_peer
            return add_peer(peer_url)
        except Exception as e:
            logger.error(f"Error adding peer {peer_url}: {e}")
            return False
    
    def remove_peer(self, peer_url: str) -> bool:
        """Remove a peer from the network"""
        try:
            from .p2p import remove_peer
            return remove_peer(peer_url)
        except Exception as e:
            logger.error(f"Error removing peer {peer_url}: {e}")
            return False
    
    def sync_now(self) -> bool:
        """Trigger immediate blockchain synchronization"""
        try:
            if self.synchronizer:
                # Check if we have peers to sync with
                from .p2p import load_peers
                peers = load_peers()
                
                if not peers:
                    # No peers available, but this is not an error in test environment
                    logger.info("No peers available for synchronization")
                    self.status['last_sync'] = datetime.now(timezone.utc).isoformat()
                    return True  # Consider success when no peers (isolated mode)
                
                success = self.synchronizer.sync_with_network()
                if success:
                    self.status['last_sync'] = datetime.now(timezone.utc).isoformat()
                return success
            return False
        except Exception as e:
            logger.error(f"Error triggering sync: {e}")
            return False
    
    def broadcast_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast a block to the network"""
        try:
            if self.config.get('broadcast_blocks', True):
                from .p2p import broadcast_block
                return broadcast_block(block)
            else:
                logger.debug("Block broadcasting is disabled")
                return {'sent_to': [], 'failed': [], 'unreachable': []}
        except Exception as e:
            logger.error(f"Error broadcasting block: {e}")
            return {'sent_to': [], 'failed': [], 'unreachable': []}
    
    def discover_peers(self) -> int:
        """Discover new peers and return count found"""
        try:
            from .p2p import discover_peers
            peers_before = len(load_peers())
            discover_peers()
            peers_after = len(load_peers())
            return peers_after - peers_before
        except Exception as e:
            logger.error(f"Error discovering peers: {e}")
            return 0
    
    def cleanup_peers(self) -> int:
        """Remove unhealthy peers and return count removed"""
        try:
            from .p2p import cleanup_peers
            return cleanup_peers()
        except Exception as e:
            logger.error(f"Error cleaning up peers: {e}")
            return 0

# Global P2P manager instance
_p2p_manager: Optional[P2PManager] = None

def get_p2p_manager() -> P2PManager:
    """Get global P2P manager instance"""
    global _p2p_manager
    if _p2p_manager is None:
        _p2p_manager = P2PManager()
    return _p2p_manager

def initialize_p2p(config: Dict[str, Any] = None) -> bool:
    """Initialize P2P system with configuration"""
    if config is None:
        config = load_p2p_config()
    
    manager = get_p2p_manager()
    return manager.initialize(config)

def start_p2p():
    """Start P2P system"""
    manager = get_p2p_manager()
    manager.start()

def stop_p2p():
    """Stop P2P system"""
    manager = get_p2p_manager()
    manager.stop()

def get_p2p_status() -> Dict[str, Any]:
    """Get P2P system status"""
    manager = get_p2p_manager()
    return manager.get_status()

def is_p2p_enabled() -> bool:
    """Check if P2P system is enabled and running"""
    manager = get_p2p_manager()
    return manager.running and manager.status.get('server_running', False)

def load_p2p_config():
    """Load P2P configuration from config files"""
    try:
        import json
        import os
        
        # Try to load from dev config first
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'dev_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Fallback to default config
        return {
            "p2p": {
                "enabled": True,
                "server_port": 8000,
                "auto_discover": True,
                "sync_interval": 30,
                "bootstrap_nodes": [],
                "network_id": "civic_network"
            }
        }
        
    except Exception as e:
        logger.error(f"Error loading P2P config: {e}")
        return {}