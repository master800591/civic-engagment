#!/usr/bin/env python3
"""
Advanced CivicCoin Wallet with Exchange Integration
Comprehensive wallet interface with exchange, market data, pooled loans, and rewards.
"""

import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from .civic_coin import CivicCoin
    from .loans_bonds import CivicLoansAndBonds
    from .stock_options import CivicStockOptions
    from .exchange_system import CivicExchange
except ImportError:
    from civic_coin import CivicCoin
    from loans_bonds import CivicLoansAndBonds
    from stock_options import CivicStockOptions
    from exchange_system import CivicExchange


class AdvancedCivicWallet:
    """
    Advanced cryptocurrency wallet with exchange integration, market data,
    pooled loan funding, and comprehensive portfolio management.
    """
    
    def __init__(self):
        """Initialize the advanced wallet system"""
        
        # Initialize core systems
        self.civic_coin = CivicCoin()
        self.loans_bonds = CivicLoansAndBonds(self.civic_coin)
        self.stock_options = CivicStockOptions(self.civic_coin)
        self.exchange = CivicExchange(self.civic_coin)
        
        # Current user context
        self.current_wallet = None
        
        print("🚀 Advanced CivicWallet initialized with full exchange integration")
    
    def set_current_wallet(self, wallet_id: str) -> bool:
        """Set the current active wallet"""
        
        wallet = self.civic_coin.get_wallet(wallet_id)
        if wallet:
            self.current_wallet = wallet_id
            print(f"👤 Active wallet: {wallet_id}")
            return True
        else:
            print(f"❌ Wallet {wallet_id} not found")
            return False
    
    def get_comprehensive_dashboard(self) -> dict:
        """Get comprehensive wallet dashboard with all financial data"""
        
        if not self.current_wallet:
            return {'error': 'No active wallet selected'}
        
        try:
            # Basic wallet info
            wallet = self.civic_coin.get_wallet(self.current_wallet)
            if not wallet:
                return {'error': 'Wallet not found'}
            
            # Portfolio summary
            portfolio = self.calculate_portfolio_value()
            
            # Exchange data
            market_data = self.exchange.get_market_data()
            trade_history = self.exchange.get_trade_history(self.current_wallet, limit=10)
            
            # Loan pool investments
            pool_investments = self.get_pool_investments()
            
            # Rewards status
            rewards_status = self.get_rewards_status()
            
            # Recent transactions
            transactions = self.civic_coin.get_transaction_history(self.current_wallet, limit=20)
            
            return {
                'wallet_info': {
                    'wallet_id': wallet['wallet_id'],
                    'owner_name': wallet['owner_name'],
                    'balance': str(wallet['balance']),
                    'wallet_address': wallet['wallet_address'],
                    'created_at': wallet['created_at'],
                    'transaction_count': wallet.get('transaction_count', 0)
                },
                'portfolio': portfolio,
                'market_data': {
                    'cvc_usd_rate': str(market_data.get('CVC/USD', {}).get('current_rate', '0')),
                    'cvc_eur_rate': str(market_data.get('CVC/EUR', {}).get('current_rate', '0')),
                    'cvc_btc_rate': str(market_data.get('CVC/BTC', {}).get('current_rate', '0')),
                    'market_summary': self.get_market_summary()
                },
                'exchange': {
                    'recent_trades': trade_history,
                    'supported_pairs': self.exchange.trading_pairs
                },
                'loan_pools': pool_investments,
                'rewards': rewards_status,
                'transactions': transactions,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Dashboard error: {str(e)}'}
    
    def calculate_portfolio_value(self) -> dict:
        """Calculate comprehensive portfolio value including all assets"""
        
        if not self.current_wallet:
            return {}
        
        try:
            portfolio = {
                'total_value_cvc': Decimal('0'),
                'total_value_usd': Decimal('0'),
                'assets': {}
            }
            
            # CVC balance
            wallet = self.civic_coin.get_wallet(self.current_wallet)
            cvc_balance = wallet['balance']
            portfolio['assets']['cvc'] = {
                'amount': str(cvc_balance),
                'value_cvc': str(cvc_balance),
                'percentage': Decimal('0')
            }
            portfolio['total_value_cvc'] += cvc_balance
            
            # Convert to USD
            market_data = self.exchange.get_market_data('CVC/USD')
            cvc_usd_rate = market_data.get('current_rate', Decimal('0'))
            portfolio['total_value_usd'] = cvc_balance * cvc_usd_rate
            
            # Loan investments (from loan pools)
            pool_investments = self.get_pool_investments()
            total_pool_investment = Decimal('0')
            for pool_type, investment in pool_investments.items():
                if investment['total_contributed'] > 0:
                    total_pool_investment += Decimal(investment['total_contributed'])
            
            if total_pool_investment > 0:
                portfolio['assets']['loan_pools'] = {
                    'amount': str(total_pool_investment),
                    'value_cvc': str(total_pool_investment),
                    'percentage': Decimal('0')
                }
                portfolio['total_value_cvc'] += total_pool_investment
            
            # Stock options
            equity_position = self.stock_options.get_wallet_equity_position(self.current_wallet)
            if equity_position and equity_position['total_value'] > 0:
                equity_value = Decimal(str(equity_position['total_value']))
                portfolio['assets']['equity'] = {
                    'amount': str(equity_position['total_shares']),
                    'value_cvc': str(equity_value),
                    'percentage': Decimal('0')
                }
                portfolio['total_value_cvc'] += equity_value
            
            # Calculate percentages
            if portfolio['total_value_cvc'] > 0:
                for asset_type in portfolio['assets']:
                    asset_value = Decimal(portfolio['assets'][asset_type]['value_cvc'])
                    percentage = (asset_value / portfolio['total_value_cvc']) * Decimal('100')
                    portfolio['assets'][asset_type]['percentage'] = str(percentage.quantize(Decimal('0.01')))
            
            # Update USD values
            total_cvc = portfolio['total_value_cvc']
            portfolio['total_value_usd'] = str((total_cvc * cvc_usd_rate).quantize(Decimal('0.01')))
            portfolio['total_value_cvc'] = str(total_cvc)
            
            return portfolio
            
        except Exception as e:
            return {'error': f'Portfolio calculation error: {str(e)}'}
    
    def get_pool_investments(self) -> dict:
        """Get current loan pool investments for the wallet"""
        
        if not self.current_wallet:
            return {}
        
        investments = {}
        pools = self.exchange.get_pool_status()
        
        for pool_type, pool_data in pools.items():
            funders = pool_data.get('funders', {})
            if self.current_wallet in funders:
                funder_data = funders[self.current_wallet]
                investments[pool_type] = {
                    'total_contributed': str(funder_data['total_contributed']),
                    'share_percentage': str(funder_data['share_percentage']),
                    'interest_earned': str(funder_data['interest_earned']),
                    'join_date': funder_data['join_date'],
                    'estimated_apr': str(pool_data['estimated_apr'])
                }
            else:
                investments[pool_type] = {
                    'total_contributed': '0',
                    'share_percentage': '0',
                    'interest_earned': '0',
                    'join_date': None,
                    'estimated_apr': str(pool_data['estimated_apr'])
                }
        
        return investments
    
    def get_rewards_status(self) -> dict:
        """Get current rewards status for all currencies"""
        
        rewards = {}
        reward_pools = self.exchange.get_reward_pool_status()
        
        for currency, pool_data in reward_pools.items():
            # Estimate claimable rewards
            wallet = self.civic_coin.get_wallet(self.current_wallet)
            if wallet and pool_data['total_pool'] > 0:
                balance_factor = wallet['balance'] / Decimal('1000')
                activity_factor = Decimal(str(wallet.get('transaction_count', 0))) / Decimal('10')
                
                base_reward = pool_data['total_pool'] * pool_data['reward_rate'] / Decimal('100')
                estimated_reward = base_reward * (balance_factor + activity_factor) / Decimal('2')
                max_reward = pool_data['total_pool'] * Decimal('0.1')
                claimable = min(estimated_reward, max_reward)
                
                rewards[currency] = {
                    'pool_total': str(pool_data['total_pool']),
                    'reward_rate': str(pool_data['reward_rate']),
                    'estimated_claimable': str(claimable.quantize(Decimal('0.000001'))),
                    'distributed_total': str(pool_data['distributed_rewards'])
                }
            else:
                rewards[currency] = {
                    'pool_total': '0',
                    'reward_rate': str(pool_data['reward_rate']),
                    'estimated_claimable': '0',
                    'distributed_total': str(pool_data['distributed_rewards'])
                }
        
        return rewards
    
    def get_market_summary(self) -> dict:
        """Get market summary with key trading pairs"""
        
        market_data = self.exchange.get_market_data()
        summary = {}
        
        key_pairs = ['CVC/USD', 'CVC/EUR', 'CVC/BTC', 'BTC/USD', 'ETH/USD']
        
        for pair in key_pairs:
            if pair in market_data:
                data = market_data[pair]
                summary[pair] = {
                    'rate': str(data['current_rate']),
                    'change_24h': str(data['change_24h']),
                    'volume_24h': str(data['volume_24h']),
                    'high_24h': str(data['high_24h']),
                    'low_24h': str(data['low_24h'])
                }
        
        return summary
    
    def exchange_currency(self, currency_pair: str, amount: str, order_type: str = 'market') -> dict:
        """Execute currency exchange through the integrated exchange"""
        
        if not self.current_wallet:
            return {'success': False, 'message': 'No active wallet selected'}
        
        try:
            amount_decimal = Decimal(str(amount))
            success, message, trade_data = self.exchange.exchange_currency(
                from_wallet=self.current_wallet,
                currency_pair=currency_pair,
                amount=amount_decimal,
                order_type=order_type
            )
            
            return {
                'success': success,
                'message': message,
                'trade_data': trade_data
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Exchange error: {str(e)}'}
    
    def invest_in_loan_pool(self, pool_type: str, amount: str) -> dict:
        """Invest in a loan pool to earn interest from funded loans"""
        
        if not self.current_wallet:
            return {'success': False, 'message': 'No active wallet selected'}
        
        try:
            amount_decimal = Decimal(str(amount))
            success, message = self.exchange.add_liquidity_to_loan_pool(
                wallet_id=self.current_wallet,
                pool_type=pool_type,
                amount=amount_decimal
            )
            
            return {'success': success, 'message': message}
            
        except Exception as e:
            return {'success': False, 'message': f'Investment error: {str(e)}'}
    
    def claim_all_rewards(self) -> dict:
        """Claim rewards from all available reward pools"""
        
        if not self.current_wallet:
            return {'success': False, 'message': 'No active wallet selected'}
        
        results = {}
        total_claimed = Decimal('0')
        
        for currency in self.exchange.supported_currencies:
            success, message, amount = self.exchange.claim_rewards(self.current_wallet, currency)
            results[currency] = {
                'success': success,
                'message': message,
                'amount_claimed': str(amount)
            }
            
            if success:
                total_claimed += amount
        
        return {
            'success': total_claimed > 0,
            'message': f'Claimed {total_claimed:.6f} CVC total rewards',
            'details': results,
            'total_claimed': str(total_claimed)
        }
    
    def create_loan_request_with_pool_option(self, amount: str, purpose: str, 
                                           duration_months: int, loan_type: str = 'personal_loan',
                                           prefer_pool_funding: bool = True) -> dict:
        """Create a loan request with option for pool funding"""
        
        if not self.current_wallet:
            return {'success': False, 'message': 'No active wallet selected'}
        
        try:
            # Create loan request
            loan_request = self.loans_bonds.create_loan_request(
                borrower_wallet=self.current_wallet,
                amount=amount,
                purpose=purpose,
                duration_months=duration_months
            )
            
            if not loan_request:
                return {'success': False, 'message': 'Failed to create loan request'}
            
            loan_id = loan_request['loan_id']
            
            # Try pool funding if preferred
            if prefer_pool_funding:
                pool_type_map = {
                    'personal_loan': 'personal_loans',
                    'business_loan': 'business_loans', 
                    'mortgage': 'mortgages'
                }
                
                pool_type = pool_type_map.get(loan_type, 'personal_loans')
                pool_success, pool_message = self.exchange.fund_loan_from_pool(loan_id, pool_type)
                
                if pool_success:
                    return {
                        'success': True,
                        'message': 'Loan request created and funded from pool',
                        'loan_id': loan_id,
                        'funding_source': 'pool',
                        'loan_data': loan_request
                    }
                else:
                    return {
                        'success': True,
                        'message': f'Loan request created. Pool funding failed: {pool_message}. Available for individual funding.',
                        'loan_id': loan_id,
                        'funding_source': 'pending',
                        'loan_data': loan_request
                    }
            else:
                return {
                    'success': True,
                    'message': 'Loan request created, available for individual funding',
                    'loan_id': loan_id,
                    'funding_source': 'pending',
                    'loan_data': loan_request
                }
                
        except Exception as e:
            return {'success': False, 'message': f'Loan request error: {str(e)}'}
    
    def get_available_loan_requests(self) -> List[dict]:
        """Get loan requests available for funding (not pool-funded)"""
        
        try:
            if not hasattr(self.civic_coin, 'loans'):
                return []
            
            available_loans = []
            for loan_id, loan_data in self.civic_coin.loans.items():
                if (loan_data['status'] == 'pending' and 
                    loan_data.get('funded_by') != 'pool'):
                    available_loans.append(loan_data)
            
            return sorted(available_loans, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            print(f"Error getting available loans: {str(e)}")
            return []
    
    def display_wallet_interface(self):
        """Display comprehensive wallet interface"""
        
        print("\n" + "="*80)
        print("🚀 ADVANCED CIVICCOIN WALLET WITH EXCHANGE")
        print("="*80)
        
        if not self.current_wallet:
            print("❌ No wallet selected. Please select a wallet first.")
            return
        
        # Get dashboard data
        dashboard = self.get_comprehensive_dashboard()
        
        if 'error' in dashboard:
            print(f"❌ Dashboard error: {dashboard['error']}")
            return
        
        # Wallet info
        wallet_info = dashboard['wallet_info']
        print(f"\n👤 Wallet: {wallet_info['owner_name']} ({wallet_info['wallet_id']})")
        print(f"💰 Balance: {float(wallet_info['balance']):,.6f} CVC")
        print(f"📊 Transactions: {wallet_info['transaction_count']}")
        
        # Portfolio summary
        portfolio = dashboard['portfolio']
        print(f"\n📈 Portfolio Value:")
        if 'total_value_cvc' in portfolio:
            print(f"   Total: {float(portfolio['total_value_cvc']):,.6f} CVC (${float(portfolio['total_value_usd']):,.2f})")
        else:
            print(f"   Portfolio calculation error - see debug info")
        
        if 'assets' in portfolio:
            print(f"   Asset Breakdown:")
            for asset_type, asset_data in portfolio['assets'].items():
                print(f"     {asset_type.upper()}: {float(asset_data['value_cvc']):,.6f} CVC ({asset_data['percentage']}%)")
        
        # Market data
        market = dashboard['market_data']
        print(f"\n💱 Current Exchange Rates:")
        print(f"   CVC/USD: ${float(market['cvc_usd_rate']):,.6f}")
        print(f"   CVC/EUR: €{float(market['cvc_eur_rate']):,.6f}")
        print(f"   CVC/BTC: ₿{float(market['cvc_btc_rate']):,.8f}")
        
        # Pool investments
        pools = dashboard['loan_pools']
        print(f"\n🏦 Loan Pool Investments:")
        total_pool_investment = Decimal('0')
        total_interest_earned = Decimal('0')
        
        for pool_type, investment in pools.items():
            contributed = Decimal(investment['total_contributed'])
            interest = Decimal(investment['interest_earned'])
            apr = investment['estimated_apr']
            
            if contributed > 0:
                print(f"   {pool_type}: {contributed:,.6f} CVC invested, {interest:,.6f} CVC earned ({apr}% APR)")
                total_pool_investment += contributed
                total_interest_earned += interest
            else:
                print(f"   {pool_type}: Available for investment ({apr}% estimated APR)")
        
        if total_pool_investment > 0:
            print(f"   Total Invested: {total_pool_investment:,.6f} CVC")
            print(f"   Total Interest Earned: {total_interest_earned:,.6f} CVC")
        
        # Rewards status
        rewards = dashboard['rewards']
        print(f"\n🎁 Rewards Status:")
        for currency, reward_data in rewards.items():
            claimable = Decimal(reward_data['estimated_claimable'])
            if claimable > 0:
                print(f"   {currency}: {claimable:,.6f} claimable (from {reward_data['pool_total']} total pool)")
            elif Decimal(reward_data['pool_total']) > 0:
                print(f"   {currency}: {reward_data['pool_total']} total pool ({reward_data['reward_rate']}% rate)")
        
        # Recent trades
        trades = dashboard['exchange']['recent_trades']
        if trades:
            print(f"\n💹 Recent Trades (last {len(trades)}):")
            for trade in trades[-5:]:  # Show last 5 trades
                print(f"   {trade['currency_pair']}: {trade['amount_sent']} → {trade['amount_received']} (fee: {trade['fee_paid']})")
        
        # Available actions
        print(f"\n⚡ Available Actions:")
        print(f"   1. Exchange currencies")
        print(f"   2. Invest in loan pools")
        print(f"   3. Claim rewards") 
        print(f"   4. Create loan request")
        print(f"   5. Fund available loans")
        print(f"   6. View detailed market data")
        print(f"   7. View transaction history")
        
        print(f"\n✅ Wallet interface ready - Advanced features available!")


def main():
    """Test the advanced wallet system"""
    
    print("🧪 Testing Advanced CivicWallet with Exchange Integration")
    print("=" * 60)
    
    # Initialize wallet
    wallet = AdvancedCivicWallet()
    
    # Set up test scenario
    if 'user_alice' in wallet.civic_coin.wallets:
        wallet.set_current_wallet('user_alice')
        
        # Display wallet interface
        wallet.display_wallet_interface()
        
        print("\n" + "="*60)
        print("🧪 Testing Exchange Features")
        
        # Test currency exchange
        print("\n💱 Testing currency exchange...")
        exchange_result = wallet.exchange_currency('CVC/USD', '50')
        if exchange_result['success']:
            print(f"✅ Exchange successful: {exchange_result['message']}")
        else:
            print(f"❌ Exchange failed: {exchange_result['message']}")
        
        # Test loan pool investment
        print("\n🏦 Testing loan pool investment...")
        investment_result = wallet.invest_in_loan_pool('personal_loans', '200')
        if investment_result['success']:
            print(f"✅ Investment successful: {investment_result['message']}")
        else:
            print(f"❌ Investment failed: {investment_result['message']}")
        
        # Test loan request with pool funding
        print("\n📋 Testing loan request with pool funding...")
        loan_result = wallet.create_loan_request_with_pool_option(
            amount='300',
            purpose='Home improvement project',
            duration_months=12,
            loan_type='personal_loan',
            prefer_pool_funding=True
        )
        
        if loan_result['success']:
            print(f"✅ Loan request successful: {loan_result['message']}")
            print(f"   Funding source: {loan_result['funding_source']}")
        else:
            print(f"❌ Loan request failed: {loan_result['message']}")
        
        # Test rewards claiming
        print("\n🎁 Testing rewards claiming...")
        rewards_result = wallet.claim_all_rewards()
        if rewards_result['success']:
            print(f"✅ Rewards claimed: {rewards_result['message']}")
        else:
            print(f"ℹ️ No rewards available: {rewards_result['message']}")
        
        # Final dashboard display
        print("\n" + "="*60)
        print("📊 FINAL WALLET STATE")
        wallet.display_wallet_interface()
    
    else:
        print("❌ No test wallets available. Please run CivicCoin initialization first.")
    
    print("\n🎉 Advanced wallet system test completed!")


if __name__ == "__main__":
    main()