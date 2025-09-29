#!/usr/bin/env python3
"""
CivicCoin Exchange System
Advanced cryptocurrency and currency exchange with market rates, blockchain validation, and pooled funding.
"""

import json
import uuid
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
import time
import random

try:
    from .civic_coin import CivicCoin
    from .loans_bonds import CivicLoansAndBonds
except ImportError:
    from civic_coin import CivicCoin
    from loans_bonds import CivicLoansAndBonds

try:
    from blockchain.blockchain import Blockchain
    from users.session import SessionManager
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    print("⚠️ Blockchain integration not available - using fallback mode")


class CivicExchange:
    """
    Advanced cryptocurrency exchange system with market rates, validation, and pooled funding.
    Features:
    - Multi-currency trading pairs (CVC/USD, CVC/EUR, CVC/BTC, etc.)
    - Real-time market rate simulation
    - Transaction validation and duplicate prevention
    - Reward pools from transaction fees
    - Pooled loan funding with interest distribution
    """
    
    def __init__(self, civic_coin: Optional[CivicCoin] = None):
        """Initialize the exchange system"""
        self.civic_coin = civic_coin or CivicCoin()
        
        # Exchange configuration
        self.supported_currencies = {
            'USD': {'name': 'US Dollar', 'symbol': '$', 'decimals': 2},
            'EUR': {'name': 'Euro', 'symbol': '€', 'decimals': 2},
            'GBP': {'name': 'British Pound', 'symbol': '£', 'decimals': 2},
            'BTC': {'name': 'Bitcoin', 'symbol': '₿', 'decimals': 8},
            'ETH': {'name': 'Ethereum', 'symbol': 'Ξ', 'decimals': 6},
            'CVC': {'name': 'CivicCoin', 'symbol': 'CVC', 'decimals': 8}
        }
        
        # Trading pairs
        self.trading_pairs = [
            'CVC/USD', 'CVC/EUR', 'CVC/GBP', 'CVC/BTC', 'CVC/ETH',
            'USD/EUR', 'USD/GBP', 'BTC/USD', 'ETH/USD', 'BTC/ETH'
        ]
        
        # Exchange data storage
        self.market_data = {}
        self.order_book = {}
        self.trade_history = []
        self.transaction_pool = set()  # For duplicate prevention
        self.reward_pools = {}
        self.loan_pools = {}
        
        # Exchange fees
        self.exchange_fee = Decimal('0.002')  # 0.2% exchange fee
        self.reward_pool_allocation = Decimal('0.5')  # 50% of fees to rewards
        self.loan_pool_allocation = Decimal('0.3')  # 30% of fees to loan pools
        self.platform_allocation = Decimal('0.2')  # 20% for platform
        
        # Initialize exchange
        self.initialize_exchange()
        
        print("🏛️ CivicExchange initialized successfully")
        print(f"💱 Supported currencies: {list(self.supported_currencies.keys())}")
        print(f"📈 Trading pairs: {len(self.trading_pairs)} pairs available")
    
    def initialize_exchange(self):
        """Initialize exchange with market data and order books"""
        
        # Initialize market data with realistic rates
        base_rates = {
            'CVC/USD': Decimal('0.45'),    # CVC = $0.45
            'CVC/EUR': Decimal('0.42'),    # CVC = €0.42
            'CVC/GBP': Decimal('0.36'),    # CVC = £0.36
            'CVC/BTC': Decimal('0.000011'), # CVC = 0.000011 BTC
            'CVC/ETH': Decimal('0.000156'), # CVC = 0.000156 ETH
            'USD/EUR': Decimal('0.93'),    # 1 USD = 0.93 EUR
            'USD/GBP': Decimal('0.79'),    # 1 USD = 0.79 GBP
            'BTC/USD': Decimal('41250.00'), # 1 BTC = $41,250
            'ETH/USD': Decimal('2890.00'),  # 1 ETH = $2,890
            'BTC/ETH': Decimal('14.27')    # 1 BTC = 14.27 ETH
        }
        
        # Initialize market data with simulated fluctuations
        for pair, rate in base_rates.items():
            # Add small random fluctuation (±2%)
            fluctuation = Decimal(str(random.uniform(-0.02, 0.02)))
            current_rate = rate * (Decimal('1') + fluctuation)
            
            self.market_data[pair] = {
                'current_rate': current_rate,
                'base_rate': rate,
                'last_updated': datetime.now().isoformat(),
                'volume_24h': Decimal('0'),
                'high_24h': current_rate,
                'low_24h': current_rate,
                'change_24h': Decimal('0')
            }
            
            # Initialize order book
            self.order_book[pair] = {
                'bids': [],  # Buy orders
                'asks': []   # Sell orders
            }
        
        # Initialize reward pools
        for currency in self.supported_currencies:
            self.reward_pools[currency] = {
                'total_pool': Decimal('0'),
                'distributed_rewards': Decimal('0'),
                'pending_rewards': {},  # wallet_id -> amount
                'reward_rate': Decimal('0.05')  # 5% APR base rate
            }
        
        # Initialize loan pools
        self.loan_pools = {
            'personal_loans': {
                'total_funded': Decimal('0'),
                'available_funds': Decimal('0'),
                'funders': {},  # wallet_id -> {amount, share_percentage}
                'active_loans': {},
                'interest_collected': Decimal('0')
            },
            'business_loans': {
                'total_funded': Decimal('0'),
                'available_funds': Decimal('0'),
                'funders': {},
                'active_loans': {},
                'interest_collected': Decimal('0')
            },
            'mortgages': {
                'total_funded': Decimal('0'),
                'available_funds': Decimal('0'),
                'funders': {},
                'active_loans': {},
                'interest_collected': Decimal('0')
            }
        }
    
    def generate_transaction_hash(self, transaction_data: dict) -> str:
        """Generate unique transaction hash for duplicate prevention"""
        
        # Create deterministic hash from transaction details
        hash_data = {
            'from_wallet': transaction_data.get('from_wallet'),
            'to_wallet': transaction_data.get('to_wallet'),
            'amount': str(transaction_data.get('amount')),
            'currency_pair': transaction_data.get('currency_pair'),
            'timestamp': transaction_data.get('timestamp')
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def validate_transaction(self, transaction_data: dict) -> Tuple[bool, str]:
        """Comprehensive transaction validation"""
        
        try:
            # Generate transaction hash
            tx_hash = self.generate_transaction_hash(transaction_data)
            
            # Check for duplicate transaction
            if tx_hash in self.transaction_pool:
                return False, "Duplicate transaction detected"
            
            # Validate wallet exists and has sufficient funds
            from_wallet = transaction_data.get('from_wallet')
            amount = Decimal(str(transaction_data.get('amount', '0')))
            currency = transaction_data.get('currency', 'CVC')
            
            if not from_wallet:
                return False, "Source wallet not specified"
            
            wallet = self.civic_coin.get_wallet(from_wallet)
            if not wallet:
                return False, f"Source wallet {from_wallet} not found"
            
            if wallet['frozen']:
                return False, "Source wallet is frozen"
            
            # Check balance (for CVC transactions)
            if currency == 'CVC':
                required_amount = amount + (amount * self.exchange_fee)
                if wallet['balance'] < required_amount:
                    return False, f"Insufficient balance. Need {required_amount} CVC, have {wallet['balance']} CVC"
            
            # Validate currency pair if specified
            currency_pair = transaction_data.get('currency_pair')
            if currency_pair and currency_pair not in self.trading_pairs:
                return False, f"Unsupported trading pair: {currency_pair}"
            
            # Validate amount
            if amount <= 0:
                return False, "Transaction amount must be positive"
            
            # Add to transaction pool to prevent duplicates
            self.transaction_pool.add(tx_hash)
            
            # Clean old transactions from pool (older than 1 hour)
            current_time = time.time()
            self.transaction_pool = {
                tx for tx in self.transaction_pool 
                if current_time - hash(tx) % 3600 < 3600
            }
            
            return True, "Transaction validated successfully"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def update_market_rates(self):
        """Simulate real-time market rate updates"""
        
        current_time = datetime.now()
        
        for pair in self.market_data:
            market = self.market_data[pair]
            
            # Simulate price movement (±0.5% random walk)
            change_percent = Decimal(str(random.uniform(-0.005, 0.005)))
            old_rate = market['current_rate']
            new_rate = old_rate * (Decimal('1') + change_percent)
            
            # Update market data
            market['current_rate'] = new_rate
            market['last_updated'] = current_time.isoformat()
            
            # Update 24h high/low
            if new_rate > market['high_24h']:
                market['high_24h'] = new_rate
            if new_rate < market['low_24h']:
                market['low_24h'] = new_rate
            
            # Calculate 24h change
            market['change_24h'] = ((new_rate - market['base_rate']) / market['base_rate']) * Decimal('100')
    
    def exchange_currency(self, from_wallet: str, currency_pair: str, 
                         amount: Decimal, order_type: str = 'market') -> Tuple[bool, str, Optional[dict]]:
        """Execute currency exchange with validation and fee distribution"""
        
        try:
            # Update market rates
            self.update_market_rates()
            
            # Prepare transaction data
            transaction_data = {
                'from_wallet': from_wallet,
                'currency_pair': currency_pair,
                'amount': str(amount),
                'order_type': order_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # Validate transaction
            is_valid, validation_message = self.validate_transaction(transaction_data)
            if not is_valid:
                return False, validation_message, None
            
            # Get market rate
            if currency_pair not in self.market_data:
                return False, f"Market data not available for {currency_pair}", None
            
            rate = self.market_data[currency_pair]['current_rate']
            
            # Calculate exchange amounts
            base_currency, quote_currency = currency_pair.split('/')
            
            if order_type == 'market':
                # Market order - immediate execution
                exchange_fee = amount * self.exchange_fee
                net_amount = amount - exchange_fee
                received_amount = net_amount * rate
                
                # Execute exchange (simplified - assuming CVC base)
                if base_currency == 'CVC':
                    # Selling CVC for other currency
                    success, message, tx_id = self.civic_coin.transfer(
                        from_wallet=from_wallet,
                        to_wallet='exchange_treasury',
                        amount=amount,
                        memo=f"Exchange: {amount} {base_currency} to {received_amount} {quote_currency}"
                    )
                    
                    if not success:
                        return False, f"Exchange transfer failed: {message}", None
                else:
                    # Buying CVC with other currency (simplified)
                    success, message, tx_id = self.civic_coin.transfer(
                        from_wallet='exchange_treasury',
                        to_wallet=from_wallet,
                        amount=received_amount,
                        memo=f"Exchange: {amount} {base_currency} to {received_amount} {quote_currency}"
                    )
                    
                    if not success:
                        return False, f"Exchange transfer failed: {message}", None
                
                # Distribute exchange fees
                self.distribute_exchange_fees(exchange_fee, base_currency)
                
                # Update market volume
                self.market_data[currency_pair]['volume_24h'] += amount
                
                # Create trade record
                trade_record = {
                    'trade_id': str(uuid.uuid4()),
                    'trader_wallet': from_wallet,
                    'currency_pair': currency_pair,
                    'order_type': order_type,
                    'amount_sent': str(amount),
                    'amount_received': str(received_amount),
                    'exchange_rate': str(rate),
                    'fee_paid': str(exchange_fee),
                    'transaction_id': tx_id,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
                self.trade_history.append(trade_record)
                
                # Log to blockchain
                self.log_exchange_transaction(trade_record)
                
                print(f"💱 Exchange completed: {amount} {base_currency} → {received_amount:.6f} {quote_currency}")
                return True, "Exchange completed successfully", trade_record
            
            else:
                return False, "Limit orders not yet implemented", None
                
        except Exception as e:
            return False, f"Exchange error: {str(e)}", None
    
    def distribute_exchange_fees(self, fee_amount: Decimal, currency: str):
        """Distribute exchange fees to reward pools, loan pools, and platform"""
        
        # Distribute to reward pool
        reward_amount = fee_amount * self.reward_pool_allocation
        self.reward_pools[currency]['total_pool'] += reward_amount
        
        # Distribute to loan pool
        loan_amount = fee_amount * self.loan_pool_allocation
        # Add to available funds for all loan types
        for pool_type in self.loan_pools:
            self.loan_pools[pool_type]['available_funds'] += loan_amount / Decimal('3')
        
        # Platform allocation (handled separately)
        platform_amount = fee_amount * self.platform_allocation
        
        print(f"💰 Fee distribution: {reward_amount:.6f} to rewards, {loan_amount:.6f} to loans, {platform_amount:.6f} to platform")
    
    def add_liquidity_to_loan_pool(self, wallet_id: str, pool_type: str, 
                                  amount: Decimal) -> Tuple[bool, str]:
        """Allow users to add liquidity to loan pools and earn interest"""
        
        try:
            if pool_type not in self.loan_pools:
                return False, f"Invalid loan pool type: {pool_type}"
            
            # Validate wallet and balance
            wallet = self.civic_coin.get_wallet(wallet_id)
            if not wallet or wallet['balance'] < amount:
                return False, "Insufficient balance"
            
            # Transfer to loan pool
            success, message, tx_id = self.civic_coin.transfer(
                from_wallet=wallet_id,
                to_wallet='loan_pool_treasury',
                amount=amount,
                memo=f"Liquidity provision to {pool_type} pool"
            )
            
            if not success:
                return False, f"Transfer failed: {message}"
            
            # Update loan pool
            pool = self.loan_pools[pool_type]
            pool['total_funded'] += amount
            pool['available_funds'] += amount
            
            # Track funder's contribution
            if wallet_id not in pool['funders']:
                pool['funders'][wallet_id] = {
                    'total_contributed': Decimal('0'),
                    'share_percentage': Decimal('0'),
                    'interest_earned': Decimal('0'),
                    'join_date': datetime.now().isoformat()
                }
            
            pool['funders'][wallet_id]['total_contributed'] += amount
            
            # Recalculate share percentages
            self.recalculate_pool_shares(pool_type)
            
            # Log to blockchain
            self.log_loan_pool_transaction({
                'type': 'liquidity_added',
                'wallet_id': wallet_id,
                'pool_type': pool_type,
                'amount': str(amount),
                'transaction_id': tx_id,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"💧 Added {amount} CVC liquidity to {pool_type} pool")
            return True, "Liquidity added successfully"
            
        except Exception as e:
            return False, f"Failed to add liquidity: {str(e)}"
    
    def recalculate_pool_shares(self, pool_type: str):
        """Recalculate share percentages for loan pool funders"""
        
        pool = self.loan_pools[pool_type]
        total_funded = pool['total_funded']
        
        if total_funded > 0:
            for funder_id in pool['funders']:
                funder = pool['funders'][funder_id]
                share_percentage = (funder['total_contributed'] / total_funded) * Decimal('100')
                funder['share_percentage'] = share_percentage
    
    def fund_loan_from_pool(self, loan_id: str, pool_type: str) -> Tuple[bool, str]:
        """Fund a loan from the pooled liquidity"""
        
        try:
            # Get loan details from civic_coin loans
            if not hasattr(self.civic_coin, 'loans') or loan_id not in self.civic_coin.loans:
                return False, f"Loan {loan_id} not found"
            
            loan = self.civic_coin.loans[loan_id]
            loan_amount = Decimal(loan['amount'])
            
            # Check if pool has sufficient funds
            pool = self.loan_pools[pool_type]
            if pool['available_funds'] < loan_amount:
                return False, f"Insufficient funds in {pool_type} pool. Available: {pool['available_funds']}, Needed: {loan_amount}"
            
            # Fund the loan
            success, message, tx_id = self.civic_coin.transfer(
                from_wallet='loan_pool_treasury',
                to_wallet=loan['borrower_wallet'],
                amount=loan_amount,
                memo=f"Pool-funded loan: {loan_id}"
            )
            
            if not success:
                return False, f"Loan funding failed: {message}"
            
            # Update pool and loan status
            pool['available_funds'] -= loan_amount
            pool['active_loans'][loan_id] = {
                'loan_amount': str(loan_amount),
                'funded_date': datetime.now().isoformat(),
                'expected_interest': str(Decimal(loan['total_interest'])),
                'status': 'active'
            }
            
            # Update loan with pool funding info
            self.civic_coin.loans[loan_id].update({
                'status': 'active',
                'funded_by': 'pool',
                'funding_pool': pool_type,
                'funded_at': datetime.now().isoformat(),
                'funding_transaction_id': tx_id
            })
            
            # Log to blockchain
            self.log_loan_pool_transaction({
                'type': 'loan_funded',
                'loan_id': loan_id,
                'pool_type': pool_type,
                'amount': str(loan_amount),
                'transaction_id': tx_id,
                'timestamp': datetime.now().isoformat()
            })
            
            self.civic_coin.save_data()
            
            print(f"🏦 Funded loan {loan_id} with {loan_amount} CVC from {pool_type} pool")
            return True, "Loan funded successfully from pool"
            
        except Exception as e:
            return False, f"Failed to fund loan: {str(e)}"
    
    def distribute_loan_interest(self, loan_id: str, interest_payment: Decimal):
        """Distribute loan interest payments to pool funders"""
        
        try:
            # Find which pool funded this loan
            pool_type = None
            for ptype, pool in self.loan_pools.items():
                if loan_id in pool['active_loans']:
                    pool_type = ptype
                    break
            
            if not pool_type:
                print(f"⚠️ Loan {loan_id} not found in any pool")
                return
            
            pool = self.loan_pools[pool_type]
            
            # Distribute interest based on share percentages
            for funder_id, funder_data in pool['funders'].items():
                share = funder_data['share_percentage'] / Decimal('100')
                funder_interest = interest_payment * share
                
                if funder_interest > 0:
                    # Credit interest to funder's wallet
                    success, message, tx_id = self.civic_coin.transfer(
                        from_wallet='loan_pool_treasury',
                        to_wallet=funder_id,
                        amount=funder_interest,
                        memo=f"Interest payment from loan {loan_id}"
                    )
                    
                    if success:
                        funder_data['interest_earned'] += funder_interest
                        print(f"💰 Distributed {funder_interest:.6f} CVC interest to {funder_id}")
            
            # Update pool totals
            pool['interest_collected'] += interest_payment
            
            # Log to blockchain
            self.log_loan_pool_transaction({
                'type': 'interest_distributed',
                'loan_id': loan_id,
                'pool_type': pool_type,
                'total_interest': str(interest_payment),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ Failed to distribute interest: {str(e)}")
    
    def claim_rewards(self, wallet_id: str, currency: str = 'CVC') -> Tuple[bool, str, Decimal]:
        """Allow users to claim accumulated rewards from the reward pool"""
        
        try:
            if currency not in self.reward_pools:
                return False, f"No reward pool for currency: {currency}", Decimal('0')
            
            pool = self.reward_pools[currency]
            
            # Calculate pending rewards (simplified - based on wallet activity)
            wallet = self.civic_coin.get_wallet(wallet_id)
            if not wallet:
                return False, f"Wallet {wallet_id} not found", Decimal('0')
            
            # Calculate rewards based on wallet balance and activity
            balance_factor = wallet['balance'] / Decimal('1000')  # Normalize by 1000 CVC
            activity_factor = Decimal(str(wallet.get('transaction_count', 0))) / Decimal('10')  # Normalize by 10 transactions
            
            base_reward = pool['total_pool'] * pool['reward_rate'] / Decimal('100')  # Base percentage
            wallet_reward = base_reward * (balance_factor + activity_factor) / Decimal('2')
            
            # Cap reward at 10% of available pool
            max_reward = pool['total_pool'] * Decimal('0.1')
            reward_amount = min(wallet_reward, max_reward)
            
            if reward_amount <= 0:
                return False, "No rewards available for claiming", Decimal('0')
            
            # Transfer reward
            success, message, tx_id = self.civic_coin.transfer(
                from_wallet='rewards_treasury',
                to_wallet=wallet_id,
                amount=reward_amount,
                memo=f"Reward claim for {currency} activity"
            )
            
            if not success:
                return False, f"Reward transfer failed: {message}", Decimal('0')
            
            # Update pool
            pool['total_pool'] -= reward_amount
            pool['distributed_rewards'] += reward_amount
            
            # Log to blockchain
            self.log_reward_transaction({
                'type': 'reward_claimed',
                'wallet_id': wallet_id,
                'currency': currency,
                'amount': str(reward_amount),
                'transaction_id': tx_id,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"🎁 Claimed {reward_amount:.6f} {currency} rewards for {wallet_id}")
            return True, "Rewards claimed successfully", reward_amount
            
        except Exception as e:
            return False, f"Failed to claim rewards: {str(e)}", Decimal('0')
    
    def get_market_data(self, currency_pair: str = None) -> dict:
        """Get current market data for trading pairs"""
        
        self.update_market_rates()
        
        if currency_pair:
            return self.market_data.get(currency_pair, {})
        else:
            return self.market_data
    
    def get_order_book(self, currency_pair: str) -> dict:
        """Get current order book for a trading pair"""
        
        return self.order_book.get(currency_pair, {'bids': [], 'asks': []})
    
    def get_trade_history(self, wallet_id: str = None, limit: int = 50) -> List[dict]:
        """Get trade history for a wallet or all trades"""
        
        if wallet_id:
            return [
                trade for trade in self.trade_history[-limit:]
                if trade['trader_wallet'] == wallet_id
            ]
        else:
            return self.trade_history[-limit:]
    
    def get_pool_status(self, pool_type: str = None) -> dict:
        """Get status of loan pools"""
        
        if pool_type and pool_type in self.loan_pools:
            pool = self.loan_pools[pool_type].copy()
            # Calculate APR for funders
            if pool['total_funded'] > 0:
                pool['estimated_apr'] = (
                    pool['interest_collected'] / pool['total_funded'] * Decimal('100')
                ).quantize(Decimal('0.01'))
            else:
                pool['estimated_apr'] = Decimal('0')
            return pool
        else:
            result = {}
            for ptype, pool in self.loan_pools.items():
                pool_copy = pool.copy()
                if pool_copy['total_funded'] > 0:
                    pool_copy['estimated_apr'] = (
                        pool_copy['interest_collected'] / pool_copy['total_funded'] * Decimal('100')
                    ).quantize(Decimal('0.01'))
                else:
                    pool_copy['estimated_apr'] = Decimal('0')
                result[ptype] = pool_copy
            return result
    
    def get_reward_pool_status(self, currency: str = None) -> dict:
        """Get status of reward pools"""
        
        if currency and currency in self.reward_pools:
            return self.reward_pools[currency]
        else:
            return self.reward_pools
    
    def log_exchange_transaction(self, trade_data: dict):
        """Log exchange transaction to blockchain"""
        
        if BLOCKCHAIN_AVAILABLE:
            try:
                user = SessionManager.get_current_user() if hasattr(SessionManager, 'get_current_user') else None
                user_email = user.get('email') if user else 'system@exchange.com'
                
                Blockchain.add_page(
                    action_type="currency_exchange",
                    data=trade_data,
                    user_email=user_email
                )
            except Exception as e:
                print(f"⚠️ Blockchain logging failed: {e}")
        else:
            # Fallback logging
            print(f"📝 Exchange log: {trade_data['trade_id']} - {trade_data['currency_pair']}")
    
    def log_loan_pool_transaction(self, pool_data: dict):
        """Log loan pool transaction to blockchain"""
        
        if BLOCKCHAIN_AVAILABLE:
            try:
                user = SessionManager.get_current_user() if hasattr(SessionManager, 'get_current_user') else None
                user_email = user.get('email') if user else 'system@loanpool.com'
                
                Blockchain.add_page(
                    action_type="loan_pool_activity",
                    data=pool_data,
                    user_email=user_email
                )
            except Exception as e:
                print(f"⚠️ Blockchain logging failed: {e}")
        else:
            print(f"📝 Loan pool log: {pool_data['type']} - {pool_data.get('pool_type', 'unknown')}")
    
    def log_reward_transaction(self, reward_data: dict):
        """Log reward transaction to blockchain"""
        
        if BLOCKCHAIN_AVAILABLE:
            try:
                user = SessionManager.get_current_user() if hasattr(SessionManager, 'get_current_user') else None
                user_email = user.get('email') if user else 'system@rewards.com'
                
                Blockchain.add_page(
                    action_type="reward_distribution",
                    data=reward_data,
                    user_email=user_email
                )
            except Exception as e:
                print(f"⚠️ Blockchain logging failed: {e}")
        else:
            print(f"📝 Reward log: {reward_data['type']} - {reward_data['currency']}")


def main():
    """Test the exchange system"""
    
    print("🧪 Testing CivicExchange System")
    print("=" * 50)
    
    # Initialize systems
    civic_coin = CivicCoin()
    exchange = CivicExchange(civic_coin)
    
    # Create test wallets
    civic_coin.create_wallet('trader1', owner_email='trader1@example.com')
    civic_coin.create_wallet('trader2', owner_email='trader2@example.com')
    
    # Fund test wallets
    if 'user_alice' in civic_coin.wallets:
        civic_coin.transfer('user_alice', 'trader1', Decimal('1000'), 'Test funding')
        civic_coin.transfer('user_alice', 'trader2', Decimal('1500'), 'Test funding')
    
    print("\n📈 Market Data:")
    market_data = exchange.get_market_data()
    for pair, data in list(market_data.items())[:5]:
        print(f"  {pair}: {data['current_rate']:.6f} (24h: {data['change_24h']:+.2f}%)")
    
    print("\n💱 Testing Currency Exchange:")
    success, message, trade = exchange.exchange_currency(
        from_wallet='trader1',
        currency_pair='CVC/USD',
        amount=Decimal('100')
    )
    
    if success:
        print(f"✅ Exchange successful: {trade['amount_sent']} CVC → ${float(trade['amount_received']):.2f}")
    else:
        print(f"❌ Exchange failed: {message}")
    
    print("\n💧 Testing Loan Pool Funding:")
    success, message = exchange.add_liquidity_to_loan_pool(
        wallet_id='trader2',
        pool_type='personal_loans',
        amount=Decimal('500')
    )
    
    if success:
        print(f"✅ Added liquidity to loan pool")
    else:
        print(f"❌ Liquidity addition failed: {message}")
    
    print("\n🏦 Pool Status:")
    pools = exchange.get_pool_status()
    for pool_type, pool_data in pools.items():
        print(f"  {pool_type}: {pool_data['available_funds']:.2f} CVC available, {pool_data['estimated_apr']:.2f}% APR")
    
    print("\n🎁 Reward Pools:")
    rewards = exchange.get_reward_pool_status()
    for currency, pool_data in rewards.items():
        if pool_data['total_pool'] > 0:
            print(f"  {currency}: {pool_data['total_pool']:.6f} total, {pool_data['reward_rate']}% rate")
    
    print("\n🎉 Exchange system test completed!")


if __name__ == "__main__":
    main()