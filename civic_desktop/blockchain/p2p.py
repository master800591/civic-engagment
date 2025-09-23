
import json
import requests
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PEERS_FILE = os.path.join(os.path.dirname(__file__), 'peers.json')

# Bootstrap nodes for network discovery
BOOTSTRAP_NODES = [
    "http://civic-node-1.civic.gov:8000",
    "http://civic-node-2.civic.gov:8000", 
    "http://civic-node-3.civic.gov:8000"
]

def load_peers() -> List[str]:
    """Load peer list from JSON file"""
    if not os.path.exists(PEERS_FILE):
        return []
    try:
        with open(PEERS_FILE, 'r', encoding='utf-8') as f:
            peers = json.load(f)
            # Ensure we return a list
            if isinstance(peers, list):
                return peers
            else:
                logger.warning("Peers file contains invalid format, returning empty list")
                return []
    except Exception as e:
        logger.error(f"Failed to load peers: {e}")
        return []

def save_peers(peers: List[str]) -> None:
    """Save peer list to JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(PEERS_FILE), exist_ok=True)
        
        # Remove duplicates and invalid entries
        clean_peers = list(set([peer for peer in peers if peer and isinstance(peer, str)]))
        
        with open(PEERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean_peers, f, indent=2)
        logger.debug(f"Saved {len(clean_peers)} peers to {PEERS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save peers: {e}")

def add_peer(peer_url: str) -> bool:
    """Add a new peer if not already present"""
    if not peer_url or not isinstance(peer_url, str):
        return False
        
    # Validate URL format
    if not (peer_url.startswith('http://') or peer_url.startswith('https://')):
        logger.warning(f"Invalid peer URL format: {peer_url}")
        return False
    
    peers = load_peers()
    if peer_url not in peers:
        peers.append(peer_url)
        save_peers(peers)
        logger.info(f"Added new peer: {peer_url}")
        return True
    return False

def remove_peer(peer_url: str) -> bool:
    """Remove a peer from the list"""
    peers = load_peers()
    if peer_url in peers:
        peers.remove(peer_url)
        save_peers(peers)
        logger.info(f"Removed peer: {peer_url}")
        return True
    return False

def check_peer_health(peer_url: str) -> bool:
    """Check if a peer is reachable via health endpoint"""
    try:
        if not peer_url:
            return False
            
        url = f"{peer_url}/api/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Verify it's a valid civic node
            if data.get('status') == 'healthy' and 'node_id' in data:
                return True
        
        return False
    except Exception as e:
        logger.debug(f"Health check failed for {peer_url}: {e}")
        return False

def broadcast_block(block: Dict[str, Any]) -> Dict[str, Any]:
    """Broadcast block to all known peers"""
    peers = load_peers()
    results = {
        'sent_to': [],
        'failed': [],
        'unreachable': []
    }
    
    if not peers:
        logger.warning("No peers available for broadcasting")
        return results
    
    for peer in peers:
        try:
            url = f"{peer}/api/blockchain/new_block"
            response = requests.post(url, json=block, timeout=10)
            
            if response.status_code == 200:
                results['sent_to'].append(peer)
                logger.debug(f"Block broadcast successful to {peer}")
            else:
                results['failed'].append(peer)
                logger.warning(f"Block broadcast failed to {peer}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to broadcast to {peer}: {e}")
            results['unreachable'].append(peer)
    
    # Remove unreachable peers
    if results['unreachable']:
        for peer in results['unreachable']:
            remove_peer(peer)
        logger.info(f"Removed {len(results['unreachable'])} unreachable peers")
    
    logger.info(f"Block broadcast complete: {len(results['sent_to'])} successful, {len(results['failed'])} failed")
    return results

def discover_peers(seed_peers: Optional[List[str]] = None) -> List[str]:
    """Discover new peers from known seed peers"""
    if seed_peers is None:
        seed_peers = load_peers()
        # Add bootstrap nodes if no peers exist
        if not seed_peers:
            seed_peers = BOOTSTRAP_NODES
    
    discovered = set(load_peers())
    newly_discovered = 0
    
    for peer in seed_peers:
        try:
            if not check_peer_health(peer):
                logger.debug(f"Skipping unhealthy seed peer: {peer}")
                continue
                
            url = f"{peer}/api/blockchain/peers"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                peer_list = data.get('peers', [])
                
                for discovered_peer in peer_list:
                    if (discovered_peer not in discovered and 
                        discovered_peer != peer and
                        check_peer_health(discovered_peer)):
                        discovered.add(discovered_peer)
                        newly_discovered += 1
                        logger.info(f"Discovered new peer: {discovered_peer}")
                        
        except Exception as e:
            logger.debug(f"Peer discovery failed for {peer}: {e}")
    
    # Save updated peer list
    final_peers = list(discovered)
    save_peers(final_peers)
    
    logger.info(f"Peer discovery complete: {newly_discovered} new peers found, {len(final_peers)} total")
    return final_peers

def bootstrap_network() -> bool:
    """Bootstrap network connection using known bootstrap nodes"""
    logger.info("Bootstrapping network connection...")
    
    current_peers = load_peers()
    initial_peer_count = len(current_peers)
    
    # Try to connect to bootstrap nodes
    successful_connections = 0
    for bootstrap_node in BOOTSTRAP_NODES:
        try:
            if check_peer_health(bootstrap_node):
                add_peer(bootstrap_node)
                successful_connections += 1
                logger.info(f"Connected to bootstrap node: {bootstrap_node}")
            else:
                logger.warning(f"Bootstrap node unreachable: {bootstrap_node}")
        except Exception as e:
            logger.error(f"Failed to connect to bootstrap node {bootstrap_node}: {e}")
    
    # Discover additional peers from bootstrap nodes
    if successful_connections > 0:
        discover_peers()
    
    final_peers = load_peers()
    final_peer_count = len(final_peers)
    
    logger.info(f"Network bootstrap complete: {successful_connections} bootstrap connections, "
               f"{final_peer_count - initial_peer_count} new peers discovered")
    
    return successful_connections > 0

def get_network_status() -> Dict[str, Any]:
    """Get current network status and peer information"""
    peers = load_peers()
    healthy_peers = []
    unhealthy_peers = []
    
    for peer in peers:
        if check_peer_health(peer):
            healthy_peers.append(peer)
        else:
            unhealthy_peers.append(peer)
    
    return {
        'total_peers': len(peers),
        'healthy_peers': len(healthy_peers),
        'unhealthy_peers': len(unhealthy_peers),
        'peer_list': {
            'healthy': healthy_peers,
            'unhealthy': unhealthy_peers
        },
        'bootstrap_nodes': BOOTSTRAP_NODES,
        'last_updated': datetime.now(timezone.utc).isoformat()
    }

def cleanup_peers() -> int:
    """Remove unhealthy peers from the peer list"""
    peers = load_peers()
    healthy_peers = []
    removed_count = 0
    
    for peer in peers:
        if check_peer_health(peer):
            healthy_peers.append(peer)
        else:
            removed_count += 1
            logger.info(f"Removing unhealthy peer: {peer}")
    
    save_peers(healthy_peers)
    logger.info(f"Peer cleanup complete: {removed_count} peers removed, {len(healthy_peers)} remain")
    return removed_count
