#!/usr/bin/env python3
"""
Initialize Treasury Wallets and Test Complete Crypto System
"""

from civic_coin import CivicCoin
from loans_bonds import CivicLoansAndBonds
from stock_options_clean import CivicStockOptions
from exchange_system import CivicExchange
from advanced_wallet import AdvancedCivicWallet
from decimal import Decimal


def initialize_treasury_system():
    """Initialize all treasury wallets and funding"""
    
    print("🏛️ Initializing Treasury System for Advanced Crypto Platform")
    print("=" * 60)
    
    # Initialize core system
    civic_coin = CivicCoin()
    
    # Create treasury wallets (reduced amounts for testing)
    treasury_wallets = [
        ('platform_treasury', 'Platform Operations Treasury', Decimal('100')),
        ('exchange_treasury', 'Exchange Operations Treasury', Decimal('100')),
        ('loan_pool_treasury', 'Loan Pool Management Treasury', Decimal('200')),
        ('reward_pool_treasury', 'Reward Distribution Treasury', Decimal('50')),
        ('insurance_treasury', 'Platform Insurance Fund', Decimal('50')),
    ]
    
    for wallet_id, owner_name, initial_funding in treasury_wallets:
        if wallet_id not in civic_coin.wallets:
            print(f"\n💼 Creating treasury wallet: {wallet_id}")
            
            # Create wallet
            success = civic_coin.create_wallet(
                wallet_id=wallet_id,
                wallet_type='treasury',
                owner_name=owner_name
            )
            
            if success:
                # Fund from user_alice (temporary for testing)
                transfer_success, transfer_message, tx_id = civic_coin.transfer(
                    from_wallet='user_alice',
                    to_wallet=wallet_id,
                    amount=initial_funding,
                    memo=f"Treasury initialization for {owner_name}"
                )
                
                if transfer_success:
                    print(f"✅ {owner_name}: {initial_funding} CVC")
                else:
                    print(f"❌ Funding failed: {transfer_message}")
            else:
                print(f"❌ Wallet creation failed")
    
    # Initialize exchange system
    exchange = CivicExchange(civic_coin)
    
    # Seed exchange pools with initial liquidity
    print(f"\n💧 Seeding Exchange Pools...")
    
    # Add liquidity to loan pools
    loan_pools = ['personal_loans', 'business_loans', 'mortgages']
    for pool_type in loan_pools:
        success, message = exchange.add_liquidity_to_loan_pool(
            wallet_id='loan_pool_treasury',
            pool_type=pool_type,
            amount=Decimal('50')
        )
        
        if success:
            print(f"✅ {pool_type}: 50 CVC added")
        else:
            print(f"❌ {pool_type}: {message}")
    
    # Reward pools are automatically managed by the exchange system
    print(f"\n🎁 Reward pools initialized automatically by exchange system")
    
    # Test comprehensive wallet system
    print(f"\n🧪 Testing Complete Crypto Ecosystem")
    print("=" * 40)
    
    # Initialize advanced wallet
    wallet = AdvancedCivicWallet()
    
    # Test with Alice's wallet
    if 'user_alice' in civic_coin.wallets:
        wallet.set_current_wallet('user_alice')
        
        print(f"\n👤 Testing Alice's Advanced Wallet")
        
        # Test currency exchange (should work now)
        print(f"\n💱 Testing currency exchange...")
        exchange_result = wallet.exchange_currency('CVC/USD', '10')
        if exchange_result['success']:
            print(f"✅ Exchange successful: {exchange_result['message']}")
        else:
            print(f"❌ Exchange failed: {exchange_result['message']}")
        
        # Test loan pool investment (should work now)
        print(f"\n🏦 Testing loan pool investment...")
        investment_result = wallet.invest_in_loan_pool('personal_loans', '50')
        if investment_result['success']:
            print(f"✅ Investment successful: {investment_result['message']}")
        else:
            print(f"❌ Investment failed: {investment_result['message']}")
        
        # Test loan request with pool funding (should work now)
        print(f"\n📋 Testing loan request with pool funding...")
        loan_result = wallet.create_loan_request_with_pool_option(
            amount='200',
            purpose='Home improvement with pool funding',
            duration_months=12,
            loan_type='personal_loan',
            prefer_pool_funding=True
        )
        
        if loan_result['success']:
            print(f"✅ Loan request: {loan_result['message']}")
            print(f"   Funding source: {loan_result['funding_source']}")
        else:
            print(f"❌ Loan failed: {loan_result['message']}")
        
        # Display final comprehensive wallet
        print(f"\n" + "="*60)
        print(f"📊 FINAL COMPREHENSIVE WALLET DASHBOARD")
        wallet.display_wallet_interface()
    
    # Display system statistics
    print(f"\n" + "="*60)
    print(f"🏛️ PLATFORM TREASURY STATUS")
    print("="*60)
    
    total_treasury = Decimal('0')
    for wallet_id, owner_name, _ in treasury_wallets:
        if wallet_id in civic_coin.wallets:
            balance = civic_coin.wallets[wallet_id]['balance']
            total_treasury += balance
            print(f"💼 {owner_name}: {balance:,.6f} CVC")
    
    print(f"\n💰 Total Treasury Holdings: {total_treasury:,.6f} CVC")
    print(f"👥 Total User Wallets: {len([w for w in civic_coin.wallets.keys() if w.startswith('user_')])}")
    print(f"🔄 Total Transactions: {len(civic_coin.transactions)}")
    
    # Exchange statistics
    pool_status = exchange.get_pool_status()
    print(f"\n📊 EXCHANGE POOL STATUS")
    for pool_type, data in pool_status.items():
        total_pool = data.get('total_pool', '0')
        estimated_apr = data.get('estimated_apr', '0')
        print(f"   {pool_type}: {total_pool} CVC pool, {estimated_apr}% APR")
    
    print(f"\n🎉 Advanced Crypto Ecosystem Fully Operational!")
    return civic_coin, exchange, wallet


if __name__ == "__main__":
    initialize_treasury_system()