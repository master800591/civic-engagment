"""
USERS CRYPTOCURRENCY INTEGRATION
================================

Integrates the advanced CivicCoin cryptocurrency system into the user module.
Handles automatic wallet creation, crypto operations, and portfolio management
for authenticated users.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal

# Add crypto module to path
current_dir = Path(__file__).parent
crypto_dir = current_dir.parent / 'crypto'
sys.path.insert(0, str(crypto_dir))

try:
    from civic_coin import CivicCoin
    from advanced_wallet import AdvancedCivicWallet
    from exchange_system import CivicExchange
    from loans_bonds import CivicLoansAndBonds
    from stock_options import CivicStockOptions
    CRYPTO_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Crypto system not available: {e}")
    CRYPTO_SYSTEM_AVAILABLE = False


class UserCryptoIntegration:
    """
    Manages cryptocurrency integration for users including:
    - Automatic wallet creation during registration
    - User crypto operations and transactions
    - Portfolio management and analytics
    - Exchange and trading functionality
    """
    
    def __init__(self):
        if CRYPTO_SYSTEM_AVAILABLE:
            # Initialize crypto systems
            self.civic_coin = CivicCoin()
            self.exchange = CivicExchange(self.civic_coin)
            self.loans_bonds = CivicLoansAndBonds(self.civic_coin)
            self.stock_options = CivicStockOptions(self.civic_coin)
            self.advanced_wallet = AdvancedCivicWallet()
            
            print("✅ User crypto integration initialized successfully")
        else:
            print("❌ Crypto system not available - integration disabled")
    
    def is_available(self) -> bool:
        """Check if crypto system is available"""
        return CRYPTO_SYSTEM_AVAILABLE
    
    def create_user_wallet(self, user_email: str, user_name: str, 
                          initial_balance: Decimal = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a cryptocurrency wallet for a new user
        
        Args:
            user_email: User's email address (used as wallet ID)
            user_name: User's full name
            initial_balance: Optional initial CVC balance (for testing/founders)
        
        Returns:
            Tuple of (success, message, wallet_id)
        """
        
        if not CRYPTO_SYSTEM_AVAILABLE:
            return False, "Crypto system not available", None
        
        try:
            # Use email as wallet ID (sanitized)
            wallet_id = f"user_{user_email.lower().replace('@', '_at_').replace('.', '_')}"
            
            # Create wallet
            success = self.civic_coin.create_wallet(
                wallet_id=wallet_id,
                wallet_type='user',
                owner_name=user_name,
                owner_email=user_email
            )
            
            if success:
                # Add initial balance if specified (for founders/testing)
                if initial_balance and initial_balance > 0:
                    # Transfer from genesis pool or create new tokens for founders
                    self._fund_new_wallet(wallet_id, initial_balance, "Initial user allocation")
                
                print(f"✅ Created crypto wallet for {user_name}: {wallet_id}")
                return True, f"Crypto wallet created successfully", wallet_id
            else:
                return False, "Failed to create crypto wallet", None
                
        except Exception as e:
            print(f"❌ Error creating wallet for {user_email}: {e}")
            return False, f"Wallet creation error: {str(e)}", None
    
    def _fund_new_wallet(self, wallet_id: str, amount: Decimal, memo: str):
        """Fund a new wallet with initial balance"""
        
        try:
            # For founders, give them substantial initial balance
            # For regular users, give them a small welcome bonus
            
            # Try to use treasury funds first
            treasury_wallets = ['platform_treasury', 'genesis_wallet', 'user_alice']
            funded = False
            
            for treasury in treasury_wallets:
                if treasury in self.civic_coin.wallets:
                    treasury_balance = self.civic_coin.wallets[treasury]['balance']
                    if treasury_balance >= amount:
                        success, message, tx_id = self.civic_coin.transfer(
                            from_wallet=treasury,
                            to_wallet=wallet_id,
                            amount=amount,
                            memo=memo
                        )
                        if success:
                            funded = True
                            print(f"💰 Funded {wallet_id} with {amount} CVC from {treasury}")
                            break
            
            if not funded:
                print(f"⚠️ Could not fund wallet {wallet_id} - no treasury funds available")
                
        except Exception as e:
            print(f"❌ Error funding wallet {wallet_id}: {e}")
    
    def get_user_wallet_id(self, user_email: str) -> str:
        """Generate consistent wallet ID from user email"""
        return f"user_{user_email.lower().replace('@', '_at_').replace('.', '_')}"
    
    def get_user_crypto_dashboard(self, user_email: str) -> Dict[str, Any]:
        """
        Get comprehensive crypto dashboard data for a user
        
        Args:
            user_email: User's email address
        
        Returns:
            Dictionary containing wallet balance, portfolio, transactions, etc.
        """
        
        if not CRYPTO_SYSTEM_AVAILABLE:
            return {'error': 'Crypto system not available'}
        
        try:
            wallet_id = self.get_user_wallet_id(user_email)
            
            # Check if wallet exists
            wallet = self.civic_coin.get_wallet(wallet_id)
            if not wallet:
                return {'error': 'User wallet not found'}
            
            # Set active wallet in advanced wallet system
            self.advanced_wallet.set_current_wallet(wallet_id)
            
            # Get comprehensive dashboard
            dashboard = self.advanced_wallet.get_comprehensive_dashboard()
            
            return dashboard
            
        except Exception as e:
            return {'error': f'Dashboard error: {str(e)}'}
    
    def execute_user_transaction(self, user_email: str, transaction_type: str, 
                                **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """
        Execute cryptocurrency transaction for a user
        
        Args:
            user_email: User's email address
            transaction_type: Type of transaction (transfer, exchange, invest, etc.)
            **kwargs: Transaction-specific parameters
        
        Returns:
            Tuple of (success, message, transaction_data)
        """
        
        if not CRYPTO_SYSTEM_AVAILABLE:
            return False, "Crypto system not available", None
        
        try:
            wallet_id = self.get_user_wallet_id(user_email)
            
            # Verify wallet exists
            if not self.civic_coin.get_wallet(wallet_id):
                return False, "User wallet not found", None
            
            # Set active wallet
            self.advanced_wallet.set_current_wallet(wallet_id)
            
            # Execute transaction based on type
            if transaction_type == 'transfer':
                return self._execute_transfer(wallet_id, **kwargs)
            elif transaction_type == 'exchange':
                return self._execute_exchange(wallet_id, **kwargs)
            elif transaction_type == 'invest_pool':
                return self._execute_pool_investment(wallet_id, **kwargs)
            elif transaction_type == 'loan_request':
                return self._execute_loan_request(wallet_id, **kwargs)
            elif transaction_type == 'claim_rewards':
                return self._execute_claim_rewards(wallet_id, **kwargs)
            else:
                return False, f"Unknown transaction type: {transaction_type}", None
                
        except Exception as e:
            return False, f"Transaction error: {str(e)}", None
    
    def _execute_transfer(self, wallet_id: str, **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """Execute CVC transfer"""
        
        to_email = kwargs.get('to_email')
        amount = Decimal(str(kwargs.get('amount', 0)))
        memo = kwargs.get('memo', '')
        
        if not to_email or amount <= 0:
            return False, "Invalid transfer parameters", None
        
        # Get recipient wallet ID
        to_wallet_id = self.get_user_wallet_id(to_email)
        
        # Execute transfer
        success, message, tx_id = self.civic_coin.transfer(
            from_wallet=wallet_id,
            to_wallet=to_wallet_id,
            amount=amount,
            memo=memo
        )
        
        if success:
            tx_data = {
                'transaction_id': tx_id,
                'type': 'transfer',
                'from_wallet': wallet_id,
                'to_wallet': to_wallet_id,
                'amount': str(amount),
                'memo': memo
            }
            return True, f"Transfer completed: {amount} CVC to {to_email}", tx_data
        else:
            return False, message, None
    
    def _execute_exchange(self, wallet_id: str, **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """Execute currency exchange"""
        
        currency_pair = kwargs.get('currency_pair')
        amount = kwargs.get('amount')
        order_type = kwargs.get('order_type', 'market')
        
        if not currency_pair or not amount:
            return False, "Invalid exchange parameters", None
        
        # Execute exchange
        result = self.advanced_wallet.exchange_currency(currency_pair, amount, order_type)
        
        if result['success']:
            return True, result['message'], result.get('trade_data')
        else:
            return False, result['message'], None
    
    def _execute_pool_investment(self, wallet_id: str, **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """Execute loan pool investment"""
        
        pool_type = kwargs.get('pool_type')
        amount = kwargs.get('amount')
        
        if not pool_type or not amount:
            return False, "Invalid investment parameters", None
        
        # Execute investment
        result = self.advanced_wallet.invest_in_loan_pool(pool_type, amount)
        
        if result['success']:
            return True, result['message'], {'pool_type': pool_type, 'amount': amount}
        else:
            return False, result['message'], None
    
    def _execute_loan_request(self, wallet_id: str, **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """Execute loan request"""
        
        amount = kwargs.get('amount')
        purpose = kwargs.get('purpose')
        duration_months = kwargs.get('duration_months', 12)
        loan_type = kwargs.get('loan_type', 'personal_loan')
        
        if not amount or not purpose:
            return False, "Invalid loan parameters", None
        
        # Execute loan request
        result = self.advanced_wallet.create_loan_request_with_pool_option(
            amount=amount,
            purpose=purpose,
            duration_months=duration_months,
            loan_type=loan_type,
            prefer_pool_funding=True
        )
        
        if result['success']:
            return True, result['message'], result
        else:
            return False, result['message'], None
    
    def _execute_claim_rewards(self, wallet_id: str, **kwargs) -> Tuple[bool, str, Optional[Dict]]:
        """Execute reward claiming"""
        
        # Execute reward claiming
        result = self.advanced_wallet.claim_all_rewards()
        
        if result['success']:
            return True, result['message'], result
        else:
            return False, result['message'], None
    
    def get_user_crypto_summary(self, user_email: str) -> Dict[str, Any]:
        """Get quick crypto summary for user dashboard"""
        
        if not CRYPTO_SYSTEM_AVAILABLE:
            return {'balance': '0', 'transactions': 0, 'portfolio_value': '0'}
        
        try:
            wallet_id = self.get_user_wallet_id(user_email)
            wallet = self.civic_coin.get_wallet(wallet_id)
            
            if not wallet:
                return {'balance': '0', 'transactions': 0, 'portfolio_value': '0'}
            
            # Get basic wallet info
            balance = wallet['balance']
            transaction_count = wallet.get('transaction_count', 0)
            
            # Get portfolio value from advanced wallet
            self.advanced_wallet.set_current_wallet(wallet_id)
            dashboard = self.advanced_wallet.get_comprehensive_dashboard()
            
            portfolio_value = '0'
            if 'portfolio' in dashboard and 'total_value_cvc' in dashboard['portfolio']:
                portfolio_value = dashboard['portfolio']['total_value_cvc']
            
            return {
                'balance': str(balance),
                'transactions': transaction_count,
                'portfolio_value': portfolio_value,
                'wallet_id': wallet_id
            }
            
        except Exception as e:
            print(f"❌ Error getting crypto summary for {user_email}: {e}")
            return {'balance': '0', 'transactions': 0, 'portfolio_value': '0'}


# Global instance for easy access
user_crypto = UserCryptoIntegration()


def get_user_crypto_integration() -> UserCryptoIntegration:
    """Get the global user crypto integration instance"""
    return user_crypto