"""
CIVIC STOCK OPTIONS & EQUITY SYSTEM
===================================

Advanced equity and options trading system for CivicCoin including:
- Stock options for platform equity
- Employee stock ownership plans (ESOP)
- Governance tokens with voting rights
- Dividend distributions
- Options contracts and derivatives
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import uuid

try:
    from .civic_coin import CivicCoin
except ImportError:
    from civic_coin import CivicCoin


class CivicStockOptions:
    """
    Comprehensive stock options and equity system
    
    Features:
    - Platform equity tokens
    - Employee stock options
    - Governance voting rights
    - Dividend distributions
    - Options contracts trading
    """
    
    def __init__(self, civic_coin: CivicCoin):
        self.civic_coin = civic_coin
        
        # Stock Configuration
        self.platform_shares_total = Decimal('1000000')  # 1 million shares
        self.platform_shares_issued = Decimal('0')
        self.share_price = Decimal('10.0')  # 10 CVC per share initially
        
        # Options Configuration
        self.min_option_duration = 30  # days
        self.max_option_duration = 365 * 5  # 5 years
        self.min_strike_price = Decimal('1.0')
        self.option_fee = Decimal('0.05')  # 5% of option value
        
        # Governance Configuration
        self.voting_threshold = Decimal('1000')  # Min shares for voting
        self.dividend_pool = Decimal('0')
        
        # Initialize storage structures
        if 'stock_options' not in self.civic_coin.contracts:
            self.civic_coin.contracts['stock_options'] = {}
        if 'platform_shares' not in self.civic_coin.contracts:
            self.civic_coin.contracts['platform_shares'] = {}
            
        print("💼 CivicStock Options & Equity system initialized")
    
    def create_stock_option(self, recipient_wallet: str, num_shares: Decimal,
                          strike_price: Decimal, duration_days: int,
                          vesting_period: int = 90) -> str:
        """Create a new stock option contract"""
        
        try:
            # Validate inputs
            if duration_days < self.min_option_duration or duration_days > self.max_option_duration:
                print(f"⚠️ Duration must be between {self.min_option_duration} and {self.max_option_duration} days")
                return ""
            
            if strike_price < self.min_strike_price:
                print(f"⚠️ Strike price must be at least {self.min_strike_price} CVC")
                return ""
            
            # Check recipient wallet exists
            recipient = self.civic_coin.get_wallet(recipient_wallet)
            if not recipient:
                print(f"⚠️ Recipient wallet {recipient_wallet} not found")
                return ""
            
            # Calculate option value and fee
            current_price = self.get_current_share_price()
            intrinsic_value = max(Decimal('0'), current_price - strike_price)
            time_value = (Decimal(str(duration_days)) / Decimal('365')) * current_price * Decimal('0.2')
            option_value = intrinsic_value + time_value
            
            fee = option_value * self.option_fee
            
            # Create option record
            option_id = str(uuid.uuid4())
            grant_date = datetime.now()
            expiry_date = grant_date + timedelta(days=duration_days)
            vesting_date = grant_date + timedelta(days=vesting_period)
            
            option_data = {
                'option_id': option_id,
                'recipient_wallet': recipient_wallet,
                'num_shares': str(num_shares),
                'strike_price': str(strike_price),
                'option_value': str(option_value),
                'fee_paid': str(fee),
                'grant_date': grant_date.isoformat(),
                'expiry_date': expiry_date.isoformat(),
                'vesting_date': vesting_date.isoformat(),
                'status': 'active',
                'exercised_date': None,
                'created_at': datetime.now().isoformat()
            }
            
            # Store option
            self.civic_coin.contracts['stock_options'][option_id] = option_data
            
            # Log transaction
            self.civic_coin.log_transaction({
                'type': 'stock_option_created',
                'option_id': option_id,
                'recipient': recipient_wallet,
                'num_shares': str(num_shares),
                'strike_price': str(strike_price),
                'expiry_date': expiry_date.isoformat(),
                'timestamp': datetime.now().isoformat()
            })
            
            self.civic_coin.save_data()
            
            print(f"📜 Stock option created: {num_shares} shares at {strike_price} CVC strike")
            print(f"   Option ID: {option_id}")
            print(f"   Expires: {expiry_date.strftime('%Y-%m-%d')}")
            print(f"   Vests: {vesting_date.strftime('%Y-%m-%d')}")
            
            return option_id
            
        except Exception as e:
            print(f"❌ Failed to create stock option: {e}")
            return ""
    
    def exercise_option(self, option_id: str, num_to_exercise: int = None) -> Tuple[bool, str]:
        """Exercise stock options to convert to shares"""
        
        try:
            if option_id not in self.civic_coin.contracts['stock_options']:
                return False, "Option not found"
            
            option = self.civic_coin.contracts['stock_options'][option_id]
            
            # Validate option status
            if option['status'] != 'active':
                return False, f"Option is {option['status']}, cannot exercise"
            
            # Check if vested
            vesting_date = datetime.fromisoformat(option['vesting_date'])
            if datetime.now() < vesting_date:
                return False, f"Option not yet vested (vests on {vesting_date.strftime('%Y-%m-%d')})"
            
            # Check if expired
            expiry_date = datetime.fromisoformat(option['expiry_date'])
            if datetime.now() > expiry_date:
                return False, f"Option expired on {expiry_date.strftime('%Y-%m-%d')}"
            
            # Determine number of shares to exercise
            total_shares = Decimal(option['num_shares'])
            if num_to_exercise is None:
                shares_to_exercise = total_shares
            else:
                shares_to_exercise = min(Decimal(str(num_to_exercise)), total_shares)
            
            # Calculate cost
            strike_price = Decimal(option['strike_price'])
            total_cost = shares_to_exercise * strike_price
            
            # Check wallet balance
            wallet = self.civic_coin.get_wallet(option['recipient_wallet'])
            if wallet['balance'] < total_cost:
                return False, f"Insufficient funds. Need {total_cost} CVC, have {wallet['balance']}"
            
            # Execute option exercise
            # Deduct payment
            success, message, tx_id = self.civic_coin.transfer(
                from_wallet=option['recipient_wallet'],
                to_wallet='platform_treasury',
                amount=total_cost,
                memo=f"Exercise stock option {option_id}"
            )
            
            if not success:
                return False, f"Payment failed: {message}"
            
            # Issue shares
            share_success = self.issue_shares(
                recipient_wallet=option['recipient_wallet'],
                num_shares=shares_to_exercise,
                issuance_type='option_exercise'
            )
            
            if not share_success:
                # Rollback payment if share issuance fails
                self.civic_coin.transfer(
                    from_wallet='platform_treasury',
                    to_wallet=option['recipient_wallet'],
                    amount=total_cost,
                    memo=f"Rollback failed exercise {option_id}"
                )
                return False, "Failed to issue shares"
            
            # Update or close option
            if shares_to_exercise == total_shares:
                # Full exercise
                option['status'] = 'exercised'
                option['exercised_date'] = datetime.now().isoformat()
            else:
                # Partial exercise - reduce remaining shares
                remaining_shares = total_shares - shares_to_exercise
                option['num_shares'] = str(remaining_shares)
            
            # Log exercise
            self.civic_coin.log_transaction({
                'type': 'stock_option_exercised',
                'option_id': option_id,
                'wallet': option['recipient_wallet'],
                'shares_exercised': str(shares_to_exercise),
                'cost': str(total_cost),
                'payment_tx': tx_id,
                'timestamp': datetime.now().isoformat()
            })
            
            self.civic_coin.save_data()
            
            print(f"🚀 Options exercised: {shares_to_exercise} options for {total_cost} CVC")
            return True, f"Successfully exercised {shares_to_exercise} options for {total_cost} CVC"
            
        except Exception as e:
            return False, f"Failed to exercise options: {str(e)}"
    
    def issue_shares(self, recipient_wallet: str, num_shares: Decimal, 
                    issuance_type: str = 'direct') -> bool:
        """Issue platform shares to a wallet"""
        
        try:
            num_shares = Decimal(str(num_shares))
            
            # Check share availability
            if self.platform_shares_issued + num_shares > self.platform_shares_total:
                print(f"⚠️ Cannot issue {num_shares} shares. Would exceed total supply.")
                return False
            
            # Create or update share record
            if recipient_wallet not in self.civic_coin.contracts['platform_shares']:
                self.civic_coin.contracts['platform_shares'][recipient_wallet] = {
                    'shares_owned': '0',
                    'voting_power': '0',
                    'dividend_earnings': '0',
                    'first_acquired': datetime.now().isoformat(),
                    'last_transaction': datetime.now().isoformat()
                }
            
            # Add shares
            current_shares = Decimal(self.civic_coin.contracts['platform_shares'][recipient_wallet]['shares_owned'])
            new_total = current_shares + num_shares
            
            self.civic_coin.contracts['platform_shares'][recipient_wallet]['shares_owned'] = str(new_total)
            self.civic_coin.contracts['platform_shares'][recipient_wallet]['voting_power'] = str(new_total)
            self.civic_coin.contracts['platform_shares'][recipient_wallet]['last_transaction'] = datetime.now().isoformat()
            
            # Update issued shares
            self.platform_shares_issued += num_shares
            
            # Log to blockchain
            self.civic_coin.log_transaction({
                'type': 'shares_issued',
                'recipient': recipient_wallet,
                'num_shares': str(num_shares),
                'issuance_type': issuance_type,
                'total_owned': str(new_total),
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"💹 Shares issued: {num_shares} to {recipient_wallet}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to issue shares: {e}")
            return False
    
    def get_current_share_price(self) -> Decimal:
        """Get current share price (simplified pricing model)"""
        
        # Simple pricing based on platform treasury and activity
        treasury_balance = Decimal('0')
        if 'platform_treasury' in self.civic_coin.wallets:
            treasury_balance = self.civic_coin.wallets['platform_treasury']['balance']
        
        # Base price + treasury value / total shares + activity multiplier
        activity_multiplier = Decimal('1.0') + (Decimal(str(len(self.civic_coin.transactions))) / Decimal('1000'))
        
        if self.platform_shares_issued > 0:
            treasury_value_per_share = treasury_balance / self.platform_shares_issued
            return (self.share_price + treasury_value_per_share) * activity_multiplier
        else:
            return self.share_price
    
    def get_wallet_equity_position(self, wallet_id: str) -> Optional[dict]:
        """Get comprehensive equity position for a wallet"""
        
        share_data = self.civic_coin.contracts['platform_shares'].get(wallet_id)
        if not share_data:
            return None
        
        shares_owned = Decimal(share_data['shares_owned'])
        current_price = self.get_current_share_price()
        market_value = shares_owned * current_price
        
        # Get options
        user_options = [opt for opt in self.civic_coin.contracts['stock_options'].values() 
                       if opt['recipient_wallet'] == wallet_id and opt['status'] == 'active']
        
        return {
            'wallet_id': wallet_id,
            'shares_owned': str(shares_owned),
            'voting_power': share_data['voting_power'],
            'dividend_earnings': share_data['dividend_earnings'],
            'current_share_price': str(current_price),
            'market_value': str(market_value),
            'ownership_percentage': str((shares_owned / self.platform_shares_issued * Decimal('100')) if self.platform_shares_issued > 0 else Decimal('0')),
            'active_options': len(user_options),
            'first_acquired': share_data['first_acquired'],
            'last_transaction': share_data['last_transaction'],
            'total_value': float(market_value)
        }


def main():
    """Test the stock options system"""
    
    print("🧪 Testing CivicStock Options & Equity System")
    print("=" * 50)
    
    # Initialize systems
    from civic_coin import CivicCoin
    
    civic_coin = CivicCoin()
    stock_options = CivicStockOptions(civic_coin)
    
    print("\n💼 Testing stock options functionality...")
    
    # Create option for Alice
    if 'user_alice' in civic_coin.wallets:
        option_id = stock_options.create_stock_option(
            recipient_wallet='user_alice',
            num_shares=Decimal('100'),
            strike_price=Decimal('8.0'),
            duration_days=180
        )
        
        if option_id:
            print(f"✅ Stock option created: {option_id}")
            
            # Try to exercise (should fail - not vested yet)
            success, message = stock_options.exercise_option(option_id, 50)
            if not success:
                print(f"⏳ Exercise blocked (as expected): {message}")
        
        # Get equity position
        equity = stock_options.get_wallet_equity_position('user_alice')
        if equity:
            print(f"📊 Alice's equity position:")
            for key, value in equity.items():
                print(f"   {key}: {value}")
    
    print("\n🎉 Stock options system test completed!")


if __name__ == "__main__":
    main()