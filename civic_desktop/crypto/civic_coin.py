"""
CIVIC COIN (CVC) - Comprehensive Cryptocurrency System
====================================================

The official cryptocurrency of the Civic Engagement Platform supporting:
- Basic transactions and transfers
- Smart contracts for loans and bonds
- Stock options and equity systems
- DeFi functionality for governance
- Blockchain-backed security and transparency
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, getcontext
import uuid
import hashlib

# Set decimal precision for financial calculations
getcontext().prec = 28

# Ensure civic_desktop is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
civic_desktop_dir = os.path.dirname(current_dir)
if civic_desktop_dir not in sys.path:
    sys.path.insert(0, civic_desktop_dir)

print(f"💰 CivicCoin (CVC) system initializing...")


class CivicCoin:
    """
    CivicCoin (CVC) - The official cryptocurrency of the Civic Platform
    
    Features:
    - Blockchain-backed transactions
    - Smart contracts for loans and bonds
    - Stock options and equity trading
    - DeFi governance functionality
    - Reward system for civic participation
    """
    
    def __init__(self):
        # Core Token Properties
        self.token_name = "CivicCoin"
        self.token_symbol = "CVC"
        self.decimals = 8  # Standard crypto decimals
        self.total_supply = Decimal('21000000')  # 21 million like Bitcoin
        self.circulating_supply = Decimal('0')
        
        # Economic Parameters
        self.inflation_rate = Decimal('0.02')  # 2% annual
        self.transaction_fee = Decimal('0.001')  # 0.1% transaction fee
        self.min_transfer = Decimal('0.00000001')  # 1 Satoshi equivalent
        
        # System Integrations
        self.blockchain = None
        self.session_manager = None
        
        # Data Storage
        self.wallets = {}
        self.transactions = []
        self.contracts = {}
        self.bonds = {}
        self.stock_options = {}
        self.loans = {}
        
        # Initialize system
        self.setup_integrations()
        self.load_all_data()
        self.initialize_genesis_distribution()
        
        print(f"✅ CivicCoin ready: {self.circulating_supply} CVC in circulation")
    
    def setup_integrations(self):
        """Setup blockchain and session integrations"""
        
        try:
            from blockchain.blockchain import Blockchain
            self.blockchain = Blockchain()
            print("✅ Blockchain integration active")
        except Exception as e:
            print(f"⚠️ Blockchain not available: {str(e)[:50]}")
        
        try:
            from users.session import SessionManager
            self.session_manager = SessionManager()
            print("✅ Session management active")
        except Exception as e:
            print(f"⚠️ Session management not available: {str(e)[:50]}")
    
    def load_all_data(self):
        """Load all cryptocurrency data from storage"""
        
        try:
            # Find database file
            db_paths = [
                os.path.join(civic_desktop_dir, 'crypto', 'civic_coin_db.json'),
                'crypto/civic_coin_db.json',
                os.path.join(os.path.dirname(__file__), 'civic_coin_db.json')
            ]
            
            db_file = None
            for path in db_paths:
                if os.path.exists(path):
                    db_file = path
                    break
            
            if db_file:
                with open(db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load data with Decimal conversion
                self.wallets = {k: {**v, 'balance': Decimal(str(v.get('balance', '0')))} 
                               for k, v in data.get('wallets', {}).items()}
                self.transactions = data.get('transactions', [])
                self.contracts = data.get('contracts', {})
                self.bonds = data.get('bonds', {})
                self.stock_options = data.get('stock_options', {})
                self.loans = data.get('loans', {})
                
                # Calculate circulating supply
                self.circulating_supply = sum(wallet.get('balance', Decimal('0')) 
                                            for wallet in self.wallets.values())
                
                print(f"📁 Loaded crypto database: {len(self.wallets)} wallets")
            else:
                print("📊 No existing database, starting fresh")
                self.create_sample_data()
        
        except Exception as e:
            print(f"❌ Error loading crypto data: {e}")
            self.create_sample_data()
    
    def save_data(self):
        """Save all cryptocurrency data to storage"""
        
        try:
            # Prepare data for JSON serialization
            save_data = {
                'token_info': {
                    'name': self.token_name,
                    'symbol': self.token_symbol,
                    'decimals': self.decimals,
                    'total_supply': str(self.total_supply),
                    'circulating_supply': str(self.circulating_supply),
                    'last_updated': datetime.now().isoformat()
                },
                'wallets': {k: {**v, 'balance': str(v['balance'])} 
                           for k, v in self.wallets.items()},
                'transactions': self.transactions,
                'contracts': self.contracts,
                'bonds': self.bonds,
                'stock_options': self.stock_options,
                'loans': self.loans
            }
            
            # Save to file
            db_file = os.path.join(os.path.dirname(__file__), 'civic_coin_db.json')
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved crypto database: {len(self.wallets)} wallets")
            return True
            
        except Exception as e:
            print(f"❌ Error saving crypto data: {e}")
            return False
    
    def initialize_genesis_distribution(self):
        """Initialize genesis token distribution"""
        
        if self.circulating_supply > 0:
            return  # Already initialized
        
        # Genesis wallets
        genesis_distribution = {
            'platform_treasury': Decimal('5000000'),     # 5M - Platform treasury
            'founder_reserve': Decimal('2000000'),       # 2M - Founder allocation
            'citizen_rewards_pool': Decimal('10000000'), # 10M - Citizen rewards
            'governance_fund': Decimal('2000000'),       # 2M - Governance operations
            'development_fund': Decimal('1000000'),      # 1M - Platform development
            'emergency_reserve': Decimal('1000000')      # 1M - Emergency fund
        }
        
        # Create genesis wallets
        for wallet_id, amount in genesis_distribution.items():
            self.create_wallet(wallet_id, wallet_type='genesis')
            self.wallets[wallet_id]['balance'] = amount
            self.circulating_supply += amount
            
            # Log to blockchain
            self.log_transaction({
                'type': 'genesis_allocation',
                'wallet': wallet_id,
                'amount': str(amount),
                'timestamp': datetime.now().isoformat()
            })
        
        print(f"🎯 Genesis distribution complete: {self.circulating_supply} CVC allocated")
        self.save_data()
    
    def create_sample_data(self):
        """Create sample cryptocurrency data for testing"""
        
        # Sample wallets
        sample_users = [
            {'id': 'user_alice', 'name': 'Alice Johnson', 'balance': '1000.50'},
            {'id': 'user_bob', 'name': 'Bob Smith', 'balance': '750.25'},
            {'id': 'user_charlie', 'name': 'Charlie Brown', 'balance': '500.00'}
        ]
        
        for user in sample_users:
            self.create_wallet(user['id'], wallet_type='user', 
                             owner_name=user['name'])
            self.wallets[user['id']]['balance'] = Decimal(user['balance'])
            self.circulating_supply += Decimal(user['balance'])
        
        # Sample transactions
        self.create_sample_transaction('user_alice', 'user_bob', '50.0', 'Payment for services')
        self.create_sample_transaction('user_bob', 'user_charlie', '25.5', 'Loan repayment')
        
        print(f"✅ Created sample crypto data: {len(self.wallets)} wallets")
    
    def create_wallet(self, wallet_id: str, wallet_type: str = 'user', 
                     owner_name: str = None, owner_email: str = None) -> bool:
        """Create a new cryptocurrency wallet"""
        
        if wallet_id in self.wallets:
            return False  # Wallet already exists
        
        self.wallets[wallet_id] = {
            'wallet_id': wallet_id,
            'owner_name': owner_name or 'Unknown User',
            'owner_email': owner_email,
            'wallet_type': wallet_type,  # user, genesis, contract, treasury
            'balance': Decimal('0'),
            'created_at': datetime.now().isoformat(),
            'last_transaction': None,
            'transaction_count': 0,
            'frozen': False,
            'wallet_address': self.generate_wallet_address(wallet_id)
        }
        
        # Log wallet creation to blockchain
        self.log_transaction({
            'type': 'wallet_created',
            'wallet_id': wallet_id,
            'owner': owner_name,
            'wallet_type': wallet_type,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"💳 Created wallet: {wallet_id} for {owner_name}")
        return True
    
    def generate_wallet_address(self, wallet_id: str) -> str:
        """Generate a unique wallet address"""
        
        # Create hash-based address
        hash_input = f"{wallet_id}{self.token_symbol}{datetime.now().isoformat()}"
        address_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:32]
        return f"CVC{address_hash}"
    
    def get_wallet(self, wallet_id: str) -> Optional[dict]:
        """Get wallet information"""
        
        return self.wallets.get(wallet_id)
    
    def get_balance(self, wallet_id: str) -> Decimal:
        """Get wallet balance"""
        
        wallet = self.get_wallet(wallet_id)
        return wallet['balance'] if wallet else Decimal('0')
    
    def transfer(self, from_wallet: str, to_wallet: str, amount: Decimal, 
                memo: str = None, fee_payer: str = None) -> Tuple[bool, str, Optional[str]]:
        """Transfer CVC between wallets"""
        
        try:
            # Input validation
            amount = Decimal(str(amount))
            
            if amount <= 0:
                return False, "Amount must be positive", None
            
            if amount < self.min_transfer:
                return False, f"Amount below minimum transfer ({self.min_transfer} CVC)", None
            
            # Get wallets
            from_wallet_data = self.get_wallet(from_wallet)
            to_wallet_data = self.get_wallet(to_wallet)
            
            if not from_wallet_data:
                return False, f"Source wallet {from_wallet} not found", None
            
            if not to_wallet_data:
                return False, f"Destination wallet {to_wallet} not found", None
            
            if from_wallet_data['frozen']:
                return False, "Source wallet is frozen", None
            
            # Calculate fees
            transaction_fee = amount * self.transaction_fee
            total_deduction = amount + transaction_fee
            
            # Check balance
            if from_wallet_data['balance'] < total_deduction:
                return False, f"Insufficient balance. Need {total_deduction} CVC, have {from_wallet_data['balance']} CVC", None
            
            # Execute transfer
            transaction_id = str(uuid.uuid4())
            
            # Deduct from source
            self.wallets[from_wallet]['balance'] -= total_deduction
            self.wallets[from_wallet]['last_transaction'] = datetime.now().isoformat()
            self.wallets[from_wallet]['transaction_count'] += 1
            
            # Add to destination
            self.wallets[to_wallet]['balance'] += amount
            self.wallets[to_wallet]['last_transaction'] = datetime.now().isoformat()
            self.wallets[to_wallet]['transaction_count'] += 1
            
            # Add fee to treasury (if not genesis transaction)
            if from_wallet != 'platform_treasury' and transaction_fee > 0:
                if 'platform_treasury' in self.wallets:
                    self.wallets['platform_treasury']['balance'] += transaction_fee
            
            # Record transaction
            transaction_data = {
                'transaction_id': transaction_id,
                'type': 'transfer',
                'from_wallet': from_wallet,
                'to_wallet': to_wallet,
                'amount': str(amount),
                'fee': str(transaction_fee),
                'memo': memo,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'block_hash': None  # Will be filled by blockchain
            }
            
            self.transactions.append(transaction_data)
            
            # Log to blockchain
            self.log_transaction(transaction_data)
            
            # Save data
            self.save_data()
            
            print(f"💸 Transfer completed: {amount} CVC from {from_wallet} to {to_wallet}")
            return True, f"Successfully transferred {amount} CVC", transaction_id
            
        except Exception as e:
            return False, f"Transfer failed: {str(e)}", None
    
    def create_sample_transaction(self, from_wallet: str, to_wallet: str, 
                                amount: str, memo: str = None):
        """Create a sample transaction (for testing)"""
        
        transaction_data = {
            'transaction_id': str(uuid.uuid4()),
            'type': 'transfer',
            'from_wallet': from_wallet,
            'to_wallet': to_wallet,
            'amount': amount,
            'fee': str(Decimal(amount) * self.transaction_fee),
            'memo': memo,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        self.transactions.append(transaction_data)
    
    def log_transaction(self, transaction_data: dict):
        """Log transaction to blockchain"""
        
        if not self.blockchain:
            return
        
        try:
            user_email = ""
            if self.session_manager and self.session_manager.is_authenticated():
                user = self.session_manager.get_current_user()
                if user:
                    user_email = user.get('email', '')
            
            success = self.blockchain.add_page(
                action_type="crypto_transaction",
                data=transaction_data,
                user_email=user_email
            )
            
            if success:
                print(f"✅ Transaction logged to blockchain")
            
        except Exception as e:
            print(f"⚠️ Blockchain logging error: {e}")
    
    def get_transaction_history(self, wallet_id: str = None, limit: int = 50) -> List[dict]:
        """Get transaction history"""
        
        if wallet_id:
            # Filter transactions for specific wallet
            filtered = [tx for tx in self.transactions 
                       if tx.get('from_wallet') == wallet_id or tx.get('to_wallet') == wallet_id]
            return sorted(filtered, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        else:
            # Return all transactions
            return sorted(self.transactions, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
    
    def get_wallet_stats(self, wallet_id: str) -> Optional[dict]:
        """Get comprehensive wallet statistics"""
        
        wallet = self.get_wallet(wallet_id)
        if not wallet:
            return None
        
        # Calculate transaction statistics
        transactions = self.get_transaction_history(wallet_id)
        
        total_sent = sum(Decimal(tx.get('amount', '0')) for tx in transactions 
                        if tx.get('from_wallet') == wallet_id)
        total_received = sum(Decimal(tx.get('amount', '0')) for tx in transactions 
                           if tx.get('to_wallet') == wallet_id)
        total_fees = sum(Decimal(tx.get('fee', '0')) for tx in transactions 
                        if tx.get('from_wallet') == wallet_id)
        
        return {
            'wallet_info': wallet,
            'balance': wallet['balance'],
            'transaction_count': len(transactions),
            'total_sent': total_sent,
            'total_received': total_received,
            'total_fees_paid': total_fees,
            'net_flow': total_received - total_sent,
            'recent_transactions': transactions[:10]
        }