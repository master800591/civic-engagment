

import json
import requests
import os
from typing import Dict, Any, Optional


PEERS_FILE = os.path.join(os.path.dirname(__file__), 'peers.json')

def load_peers() -> list[str]:
    if not os.path.exists(PEERS_FILE):
        return []
    with open(PEERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_peers(peers: list[str]) -> None:
    with open(PEERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(peers, f, indent=2)

def add_peer(peer_url: str) -> bool:
    """Add a new peer if not already present"""
    peers = load_peers()
    if peer_url not in peers:
        peers.append(peer_url)
        save_peers(peers)
        return True
    return False

def remove_peer(peer_url: str) -> bool:
    """Remove a peer from the list"""
    peers = load_peers()
    if peer_url in peers:
        peers.remove(peer_url)
        save_peers(peers)
        return True
    return False

def broadcast_block(block: Dict[str, Any]) -> None:
    peers = load_peers()
    unreachable: list[str] = []
    for peer in peers:
        try:
            url = f"{peer}/api/blockchain/new_block"
            resp = requests.post(url, json=block, timeout=2)
            if resp.status_code != 200:
                print(f"Peer {peer} responded with status {resp.status_code}")
        except Exception as e:
            print(f"Failed to broadcast to {peer}: {e}")
            unreachable.append(peer)
    # Remove unreachable peers
    if unreachable:
        for peer in unreachable:
            remove_peer(peer)
        print(f"Removed unreachable peers: {unreachable}")

def check_peer_health(peer_url: str) -> bool:
    """Check if a peer is reachable via health endpoint"""
    try:
        url = f"{peer_url}/api/health"
        resp = requests.get(url, timeout=2)
        return resp.status_code == 200
    except Exception:
        return False

def discover_peers(seed_peers: Optional[list[str]] = None) -> list[str]:
    """Discover new peers from known seed peers"""
    if seed_peers is None:
        seed_peers = load_peers()
    discovered = set(load_peers())
    for peer in seed_peers:
        try:
            url = f"{peer}/api/blockchain/peers"
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                peer_list = resp.json().get('peers', [])
                for p in peer_list:
                    if p not in discovered:
                        discovered.add(p)
        except Exception as e:
            print(f"Peer discovery failed for {peer}: {e}")
    save_peers(list(discovered))
    return list(discovered)
