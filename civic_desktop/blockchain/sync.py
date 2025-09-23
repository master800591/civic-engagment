"""
Blockchain Synchronization Module
=================================

This module handles synchronization between P2P nodes to ensure
all nodes have the same blockchain state. It provides:
- Block downloading from peers
- Chain validation and conflict resolution
- Automatic synchronization on startup
- Periodic sync monitoring
"""

import requests
import threading
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class BlockchainSynchronizer:
    def __init__(self):
        self.sync_lock = threading.Lock()
        self.is_syncing = False
        self.last_sync_time = None
        self.sync_interval = 30  # seconds
        self.max_blocks_per_request = 50
        self.sync_thread = None
        self.running = False
        
    def start_periodic_sync(self):
        """Start periodic blockchain synchronization"""
        if self.running:
            return
            
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("Blockchain synchronization started")
    
    def stop_periodic_sync(self):
        """Stop periodic synchronization"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("Blockchain synchronization stopped")
    
    def _sync_loop(self):
        """Main synchronization loop"""
        while self.running:
            try:
                if not self.is_syncing:
                    self.sync_with_network()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def sync_with_network(self) -> bool:
        """Synchronize blockchain with network peers"""
        with self.sync_lock:
            if self.is_syncing:
                logger.debug("Sync already in progress")
                return False
                
            self.is_syncing = True
            
        try:
            logger.info("Starting blockchain synchronization")
            
            # Get current local chain state
            from .blockchain import Blockchain
            local_chain = Blockchain.load_chain()
            local_height = len(local_chain.get('pages', []))
            
            # Get list of peers
            from .p2p import load_peers
            peers = load_peers()
            
            if not peers:
                logger.warning("No peers available for synchronization")
                return False
            
            # Find the peer with highest blockchain height
            best_peer, best_height = self._find_best_peer(peers, local_height)
            
            if not best_peer:
                logger.info("No peers with higher blockchain height found")
                return True
            
            logger.info(f"Syncing with peer {best_peer} (height: {best_height}, local: {local_height})")
            
            # Download missing blocks
            success = self._download_missing_blocks(best_peer, local_height, best_height)
            
            if success:
                self.last_sync_time = datetime.now(timezone.utc)
                logger.info(f"Synchronization completed successfully. New height: {best_height}")
            else:
                logger.error("Synchronization failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Synchronization error: {e}")
            return False
        finally:
            self.is_syncing = False
    
    def _find_best_peer(self, peers: List[str], local_height: int) -> Tuple[Optional[str], int]:
        """Find peer with highest blockchain height"""
        best_peer = None
        best_height = local_height
        
        # Check peers concurrently for performance
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_peer = {
                executor.submit(self._get_peer_height, peer): peer 
                for peer in peers
            }
            
            for future in as_completed(future_to_peer):
                peer = future_to_peer[future]
                try:
                    peer_height = future.result()
                    if peer_height and peer_height > best_height:
                        best_height = peer_height
                        best_peer = peer
                        logger.debug(f"Found better peer: {peer} (height: {peer_height})")
                except Exception as e:
                    logger.debug(f"Failed to get height from peer {peer}: {e}")
        
        return best_peer, best_height
    
    def _get_peer_height(self, peer_url: str) -> Optional[int]:
        """Get blockchain height from a specific peer"""
        try:
            response = requests.get(f"{peer_url}/api/blockchain/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('height', 0)
        except Exception as e:
            logger.debug(f"Failed to get height from {peer_url}: {e}")
        return None
    
    def _download_missing_blocks(self, peer_url: str, start_height: int, end_height: int) -> bool:
        """Download missing blocks from peer"""
        try:
            current_height = start_height
            
            while current_height < end_height:
                # Calculate how many blocks to request
                remaining = end_height - current_height
                batch_size = min(self.max_blocks_per_request, remaining)
                
                logger.debug(f"Downloading blocks {current_height} to {current_height + batch_size - 1}")
                
                # Request blocks from peer
                response = requests.get(
                    f"{peer_url}/api/blockchain/blocks",
                    params={
                        'from': current_height,
                        'limit': batch_size
                    },
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to download blocks: {response.status_code}")
                    return False
                
                data = response.json()
                blocks = data.get('blocks', [])
                
                if not blocks:
                    logger.warning("No blocks returned from peer")
                    break
                
                # Validate and add blocks
                for block in blocks:
                    if not self._validate_and_add_block(block):
                        logger.error(f"Failed to validate block {block.get('index')}")
                        return False
                
                current_height += len(blocks)
                logger.debug(f"Downloaded {len(blocks)} blocks, current height: {current_height}")
                
                # Prevent tight loop
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Block download error: {e}")
            return False
    
    def _validate_and_add_block(self, block_data: Dict[str, Any]) -> bool:
        """Validate and add a single block to the local chain"""
        try:
            from .blockchain import Blockchain
            
            # Basic validation
            required_fields = ['index', 'previous_hash', 'timestamp', 'data', 'validator', 'signature', 'hash']
            if not all(field in block_data for field in required_fields):
                logger.error(f"Block missing required fields: {block_data.get('index')}")
                return False
            
            # Verify hash integrity
            computed_hash = self._compute_block_hash(block_data)
            if computed_hash != block_data.get('hash'):
                logger.error(f"Block hash mismatch for block {block_data.get('index')}")
                return False
            
            # Add block to chain
            success = Blockchain.add_page(
                data=block_data.get('data'),
                validator=block_data.get('validator'),
                signature=block_data.get('signature')
            )
            
            if not success:
                logger.error(f"Failed to add block {block_data.get('index')} to chain")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Block validation error: {e}")
            return False
    
    def _compute_block_hash(self, block_data: Dict[str, Any]) -> str:
        """Compute hash for block verification"""
        import hashlib
        import json
        
        # Create hash data excluding the hash field itself
        hash_data = {
            'index': block_data.get('index'),
            'previous_hash': block_data.get('previous_hash'),
            'timestamp': block_data.get('timestamp'),
            'data': block_data.get('data'),
            'validator': block_data.get('validator'),
            'signature': block_data.get('signature')
        }
        
        block_string = json.dumps(hash_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def manual_sync_with_peer(self, peer_url: str) -> bool:
        """Manually trigger sync with specific peer"""
        logger.info(f"Manual sync with peer: {peer_url}")
        
        try:
            # Check peer health first
            from . import check_peer_health
            if not check_peer_health(peer_url):
                logger.error(f"Peer {peer_url} is not healthy")
                return False
            
            # Get peer height
            peer_height = self._get_peer_height(peer_url)
            if not peer_height:
                logger.error(f"Could not get height from peer {peer_url}")
                return False
            
            # Get local height
            from .blockchain import Blockchain
            local_chain = Blockchain.load_chain()
            local_height = len(local_chain.get('pages', []))
            
            if peer_height <= local_height:
                logger.info(f"Peer height ({peer_height}) not greater than local ({local_height})")
                return True
            
            # Download missing blocks
            return self._download_missing_blocks(peer_url, local_height, peer_height)
            
        except Exception as e:
            logger.error(f"Manual sync error: {e}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status"""
        from .blockchain import Blockchain
        local_chain = Blockchain.load_chain()
        local_height = len(local_chain.get('pages', []))
        
        return {
            'is_syncing': self.is_syncing,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'local_height': local_height,
            'sync_interval': self.sync_interval,
            'running': self.running
        }

# Global synchronizer instance
_synchronizer: Optional[BlockchainSynchronizer] = None

def get_synchronizer() -> BlockchainSynchronizer:
    """Get global synchronizer instance"""
    global _synchronizer
    if _synchronizer is None:
        _synchronizer = BlockchainSynchronizer()
    return _synchronizer

def start_blockchain_sync():
    """Start blockchain synchronization"""
    sync = get_synchronizer()
    sync.start_periodic_sync()

def stop_blockchain_sync():
    """Stop blockchain synchronization"""
    sync = get_synchronizer()
    sync.stop_periodic_sync()

def sync_now() -> bool:
    """Trigger immediate synchronization"""
    sync = get_synchronizer()
    return sync.sync_with_network()

def sync_with_peer(peer_url: str) -> bool:
    """Manually sync with specific peer"""
    sync = get_synchronizer()
    return sync.manual_sync_with_peer(peer_url)