"""
P2P HTTP Server for Civic Engagement Platform
===========================================

This module implements the HTTP API server that enables P2P communication
between blockchain nodes. It provides endpoints for:
- Receiving blocks from other nodes
- Sharing peer information
- Health checking
- Blockchain synchronization
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import json
import threading
import time
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class P2PServer:
    def __init__(self, port: int = 8000, host: str = '0.0.0.0'):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web clients
        self.port = port
        self.host = host
        self.server_thread = None
        self.running = False
        self.node_id = self._generate_node_id()
        self.startup_time = datetime.now(timezone.utc)
        
        # Initialize Flask app context
        with self.app.app_context():
            self.setup_routes()
            
        logger.info(f"P2P Server initialized on {host}:{port} with node_id: {self.node_id}")
    
    def _generate_node_id(self) -> str:
        """Generate unique node identifier"""
        import hashlib
        import socket
        hostname = socket.gethostname()
        timestamp = str(time.time())
        node_string = f"{hostname}-{timestamp}-{self.port}"
        return hashlib.sha256(node_string.encode()).hexdigest()[:16]
    
    def setup_routes(self):
        """Setup all HTTP API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            try:
                from ..blockchain.blockchain import Blockchain
                chain = Blockchain.load_chain()
                chain_height = len(chain.get('pages', []))
                
                return jsonify({
                    'status': 'healthy',
                    'node_id': self.node_id,
                    'uptime_seconds': (datetime.now(timezone.utc) - self.startup_time).total_seconds(),
                    'blockchain_height': chain_height,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'version': '1.0.0'
                })
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e),
                    'node_id': self.node_id
                }), 500
        
        @self.app.route('/api/blockchain/info', methods=['GET'])
        def blockchain_info():
            """Get blockchain information"""
            try:
                from ..blockchain.blockchain import Blockchain
                chain = Blockchain.load_chain()
                pages = chain.get('pages', [])
                
                latest_block = pages[-1] if pages else None
                
                return jsonify({
                    'height': len(pages),
                    'latest_block_hash': latest_block.get('hash') if latest_block else None,
                    'latest_block_timestamp': latest_block.get('timestamp') if latest_block else None,
                    'total_chapters': len(chain.get('chapters', [])),
                    'total_books': len(chain.get('books', [])),
                    'node_id': self.node_id
                })
            except Exception as e:
                logger.error(f"Blockchain info request failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/blockchain/blocks', methods=['GET'])
        def get_blocks():
            """Get blockchain blocks with optional range"""
            try:
                from ..blockchain.blockchain import Blockchain
                chain = Blockchain.load_chain()
                pages = chain.get('pages', [])
                
                # Parse query parameters
                start = request.args.get('from', 0, type=int)
                limit = request.args.get('limit', 100, type=int)
                end = min(start + limit, len(pages))
                
                # Validate range
                if start < 0 or start >= len(pages):
                    return jsonify({'error': 'Invalid start index'}), 400
                
                requested_blocks = pages[start:end]
                
                return jsonify({
                    'blocks': requested_blocks,
                    'start_index': start,
                    'count': len(requested_blocks),
                    'total_blocks': len(pages),
                    'has_more': end < len(pages)
                })
            except Exception as e:
                logger.error(f"Get blocks request failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/blockchain/new_block', methods=['POST'])
        def receive_block():
            """Receive and validate a new block from peer"""
            try:
                if not request.is_json:
                    return jsonify({'error': 'Content-Type must be application/json'}), 400
                
                block_data = request.get_json()
                if not block_data:
                    return jsonify({'error': 'Empty block data'}), 400
                
                # Validate required block fields
                required_fields = ['index', 'previous_hash', 'timestamp', 'data', 'validator', 'signature']
                missing_fields = [field for field in required_fields if field not in block_data]
                if missing_fields:
                    return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
                
                # Validate block before adding
                success, message = self._validate_and_add_block(block_data)
                
                if success:
                    logger.info(f"Successfully received block {block_data.get('index')} from peer")
                    return jsonify({
                        'success': True,
                        'message': message,
                        'block_index': block_data.get('index')
                    })
                else:
                    logger.warning(f"Block validation failed: {message}")
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 400
                    
            except Exception as e:
                logger.error(f"Receive block failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/blockchain/peers', methods=['GET'])
        def get_peers():
            """Get list of known peers"""
            try:
                from . import load_peers
                peers = load_peers()
                
                # Add our own endpoint if not already included
                our_endpoint = f"http://{self.host}:{self.port}"
                if our_endpoint not in peers:
                    peers.append(our_endpoint)
                
                return jsonify({
                    'peers': peers,
                    'count': len(peers),
                    'node_id': self.node_id
                })
            except Exception as e:
                logger.error(f"Get peers request failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/blockchain/peers', methods=['POST'])
        def add_peer():
            """Add a new peer to the network"""
            try:
                if not request.is_json:
                    return jsonify({'error': 'Content-Type must be application/json'}), 400
                
                data = request.get_json()
                peer_url = data.get('peer_url')
                
                if not peer_url:
                    return jsonify({'error': 'peer_url is required'}), 400
                
                # Validate peer URL format
                if not (peer_url.startswith('http://') or peer_url.startswith('https://')):
                    return jsonify({'error': 'peer_url must start with http:// or https://'}), 400
                
                # Test peer connectivity before adding
                from . import check_peer_health, add_peer as add_peer_func
                if check_peer_health(peer_url):
                    success = add_peer_func(peer_url)
                    if success:
                        logger.info(f"Successfully added peer: {peer_url}")
                        return jsonify({
                            'success': True,
                            'message': f'Peer {peer_url} added successfully'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Peer already exists'
                        })
                else:
                    return jsonify({'error': 'Peer health check failed'}), 400
                    
            except Exception as e:
                logger.error(f"Add peer failed: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/sync/request', methods=['POST'])
        def sync_request():
            """Handle blockchain synchronization request"""
            try:
                if not request.is_json:
                    return jsonify({'error': 'Content-Type must be application/json'}), 400
                
                data = request.get_json()
                peer_height = data.get('height', 0)
                
                from ..blockchain.blockchain import Blockchain
                local_chain = Blockchain.load_chain()
                local_height = len(local_chain.get('pages', []))
                
                if peer_height < local_height:
                    # Peer needs blocks from us
                    missing_blocks = local_chain['pages'][peer_height:]
                    return jsonify({
                        'blocks': missing_blocks[:50],  # Limit to 50 blocks per request
                        'local_height': local_height,
                        'has_more': len(missing_blocks) > 50
                    })
                else:
                    return jsonify({
                        'blocks': [],
                        'local_height': local_height,
                        'has_more': False
                    })
                    
            except Exception as e:
                logger.error(f"Sync request failed: {e}")
                return jsonify({'error': str(e)}), 500
    
    def _validate_and_add_block(self, block_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate received block and add to local blockchain"""
        try:
            from ..blockchain.blockchain import Blockchain
            from ..blockchain.signatures import BlockchainSigner
            
            # Load current chain
            chain = Blockchain.load_chain()
            pages = chain.get('pages', [])
            
            # Check if block already exists
            block_index = block_data.get('index')
            if any(page.get('index') == block_index for page in pages):
                return False, f"Block {block_index} already exists"
            
            # Validate block index sequence
            expected_index = len(pages)
            if block_index != expected_index:
                return False, f"Invalid block index. Expected {expected_index}, got {block_index}"
            
            # Validate previous hash
            if pages:
                expected_prev_hash = pages[-1].get('hash')
                if block_data.get('previous_hash') != expected_prev_hash:
                    return False, "Invalid previous hash"
            else:
                # First block should have previous_hash of all zeros
                if block_data.get('previous_hash') != '0' * 64:
                    return False, "Invalid genesis block previous hash"
            
            # Validate block signature with full cryptographic verification
            validator = block_data.get('validator')
            signature = block_data.get('signature')
            
            # Validate required fields first
            if not validator or not isinstance(validator, str):
                return False, "Block must have a valid validator field"
            
            # Skip signature validation for system blocks
            if validator not in ['SYSTEM', 'GENESIS']:
                try:
                    from ..blockchain.blockchain import ValidatorRegistry
                    from ..blockchain.signatures import BlockchainSigner
                    
                    # Check validator authorization (PoA validation)
                    if not ValidatorRegistry.is_validator(validator):
                        return False, f"Unauthorized validator: {validator} (not in validator registry)"
                    
                    # Require valid signature
                    if not signature or signature == 'UNSIGNED':
                        return False, "Block signature required for validator blocks"
                    
                    # Get validator's public key for signature verification
                    public_key = ValidatorRegistry.get_validator_public_key(validator)
                    if not public_key:
                        return False, f"No public key found for validator: {validator}"
                    
                    # Perform full cryptographic signature verification
                    # Create block data for signature verification (excluding signature field)
                    verification_data = {
                        'index': block_data.get('index'),
                        'previous_hash': block_data.get('previous_hash'),
                        'timestamp': block_data.get('timestamp'),
                        'data': block_data.get('data'),
                        'validator': validator
                    }
                    
                    is_signature_valid = BlockchainSigner.verify_block_signature(
                        verification_data, signature, public_key
                    )
                    
                    if not is_signature_valid:
                        return False, f"Invalid cryptographic signature for validator: {validator}"
                    
                    logger.info(f"✅ PoA validation passed for validator: {validator}")
                        
                except Exception as e:
                    logger.error(f"PoA signature validation error: {e}")
                    return False, f"PoA validation failed: {str(e)}"
            
            # Add block to chain using existing method
            block_data_field = block_data.get('data')
            if not isinstance(block_data_field, dict):
                return False, "Block data field must be a dictionary"
                
            success = Blockchain.add_page(
                data=block_data_field,
                validator=validator,
                signature=signature
            )
            
            if success:
                return True, "Block added successfully"
            else:
                return False, "Failed to add block to local chain"
                
        except Exception as e:
            logger.error(f"Block validation error: {e}")
            return False, f"Block validation failed: {str(e)}"
    
    def start(self):
        """Start the P2P server in a background thread"""
        if self.running:
            logger.warning("P2P Server is already running")
            return
        
        def run_server():
            try:
                logger.info(f"Starting P2P Server on {self.host}:{self.port}")
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    threaded=True,
                    use_reloader=False
                )
            except Exception as e:
                logger.error(f"P2P Server error: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        
        # Give server time to start
        time.sleep(1)
        logger.info(f"P2P Server started successfully on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the P2P server"""
        if not self.running:
            return
        
        self.running = False
        logger.info("P2P Server stopped")
    
    def get_server_url(self) -> str:
        """Get the full URL of this server"""
        return f"http://{self.host}:{self.port}"

# Global server instance
_p2p_server: Optional[P2PServer] = None

def start_p2p_server(port: int = 8000, host: str = '0.0.0.0') -> P2PServer:
    """Start global P2P server instance"""
    global _p2p_server
    
    if _p2p_server is None:
        _p2p_server = P2PServer(port=port, host=host)
        _p2p_server.start()
    
    return _p2p_server

def get_p2p_server() -> Optional[P2PServer]:
    """Get current P2P server instance"""
    return _p2p_server

def stop_p2p_server():
    """Stop global P2P server instance"""
    global _p2p_server
    
    if _p2p_server:
        _p2p_server.stop()
        _p2p_server = None