#!/usr/bin/env python3
"""
Credit System Tester and Initializer
Tests credit generation, pool management, and token distribution
"""

import os
import sys
from datetime import datetime, timezone

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

def test_credit_system():
    """Test the credit generation and pool system"""
    try:
        print("🧪 Testing Credit System")
        print("=" * 50)
        
        # Import after path setup
        from civic_desktop.blockchain.blockchain import Blockchain, BlockchainIntegrator
        from civic_desktop.users.backend import UserBackend
        from civic_desktop.crypto.ledger import TokenLedger
        from civic_desktop.blockchain.reports import NetworkReports
        
        # 1. Load existing blockchain
        print("\n📊 Step 1: Loading Blockchain")
        Blockchain.load_chain()
        
        # 2. Check existing users
        print("\n👥 Step 2: Checking Users")
        users = UserBackend.load_users()
        print(f"   Found {len(users)} registered users:")
        for user in users[:5]:  # Show first 5
            email = user.get('email', 'Unknown')
            roles = ', '.join(user.get('roles', ['Unknown']))
            print(f"   - {email} ({roles})")
        
        if len(users) > 5:
            print(f"   ... and {len(users) - 5} more users")
        
        # 3. Check current credit balances
        print("\n💰 Step 3: Current Credit Balances")
        total_credits = 0
        for user in users:
            email = user.get('email', '')
            credits = BlockchainIntegrator.get_user_credits(email)
            balance = BlockchainIntegrator.get_user_balance(email)
            total_credits += credits
            print(f"   - {email}: {credits:,} credits, {balance:.2f} tokens")
        
        print(f"   📈 Total Credits in System: {total_credits:,}")
        target_credits = len(users) * 2000
        print(f"   🎯 Target Credits (2000 per user): {target_credits:,}")
        credit_deficit = max(0, target_credits - total_credits)
        print(f"   ⚖️ Credit Deficit: {credit_deficit:,}")
        
        # 4. Test credit generation by simulating a transaction
        print("\n🔄 Step 4: Testing Credit Generation")
        if len(users) >= 2:
            sender = users[0]['email']
            receiver = users[1]['email']
            
            print(f"   Simulating transaction: {sender} → {receiver}")
            
            # Record initial credits
            initial_sender_credits = BlockchainIntegrator.get_user_credits(sender)
            print(f"   Initial {sender} credits: {initial_sender_credits:,}")
            
            # Add a test transaction to trigger credit generation
            success = BlockchainIntegrator.add_transaction(
                sender=sender,
                receiver=receiver, 
                amount=10.0,
                tx_type='test_credit_generation',
                metadata={'test': True},
                validator=sender
            )
            
            if success:
                print("   ✅ Transaction added successfully")
                
                # Check credits after transaction
                final_sender_credits = BlockchainIntegrator.get_user_credits(sender)
                credits_earned = final_sender_credits - initial_sender_credits
                print(f"   Final {sender} credits: {final_sender_credits:,}")
                print(f"   Credits earned: +{credits_earned:,}")
                
                # Check if network inflation credits were distributed
                total_credits_after = sum(BlockchainIntegrator.get_user_credits(u['email']) for u in users)
                total_credits_earned = total_credits_after - total_credits
                print(f"   Total new credits in system: +{total_credits_earned:,}")
                
            else:
                print("   ❌ Transaction failed")
        
        # 5. Generate network reports
        print("\n📊 Step 5: Network Reports")
        
        # Credit ratio report
        try:
            credit_report = NetworkReports.credit_ratio_report()
            print(f"   Credit Ratio Report:")
            target = credit_report.get('target_credits', 0)
            actual = credit_report.get('actual_credits', 0)
            print(f"   - Target Credits: {target:,}" if isinstance(target, int) else f"   - Target Credits: {target}")
            print(f"   - Actual Credits: {actual:,}" if isinstance(actual, int) else f"   - Actual Credits: {actual}")
            print(f"   - Inflation Status: {credit_report.get('inflation_status', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️ Credit ratio report error: {e}")
        
        # Network pool report
        try:
            pool_report = NetworkReports.network_pool_report()
            total = pool_report.get('total_pool', 0)
            print(f"   Network Pool: {total:,} credits" if isinstance(total, int) else f"   Network Pool: {total} credits")
        except Exception as e:
            print(f"   ⚠️ Network pool report error: {e}")
        
        # User balances
        try:
            balance_report = NetworkReports.user_balances_report()
            user_balances = balance_report.get('users', [])
            print(f"   Active Users: {len(user_balances)}")
        except Exception as e:
            print(f"   ⚠️ User balances report error: {e}")
        
        # 6. Force credit distribution if needed
        print("\n🚀 Step 6: Force Credit Distribution")
        if credit_deficit > 0:
            print(f"   Distributing {credit_deficit:,} credits to reach target...")
            
            credits_per_user = credit_deficit // len(users)
            if credits_per_user > 0:
                for user in users:
                    email = user['email']
                    credit_data = {
                        "action": "credit_reward",
                        "user": email,
                        "credits": credits_per_user,
                        "reason": "system_initialization",
                        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }
                    
                    success = Blockchain.add_page(credit_data, "SYSTEM")
                    if success:
                        print(f"   ✅ Awarded {credits_per_user:,} credits to {email}")
                    else:
                        print(f"   ❌ Failed to award credits to {email}")
                
                # Check final totals
                final_total_credits = sum(BlockchainIntegrator.get_user_credits(u['email']) for u in users)
                print(f"   📈 Final Total Credits: {final_total_credits:,}")
            else:
                print("   ⚠️ Credit deficit too small to distribute")
        else:
            print("   ✅ Credit system already properly funded")
        
        # 7. Test token ledger integration
        print("\n💰 Step 7: Testing Token Ledger")
        ledger = TokenLedger()
        
        if len(users) >= 1:
            test_user = users[0]['email']
            initial_balance = ledger.get_balance(test_user)
            print(f"   Initial balance for {test_user}: {initial_balance:.2f}")
            
            # Award test tokens
            ledger.award_tokens(test_user, 100.0, "Credit system test")
            final_balance = ledger.get_balance(test_user)
            print(f"   Final balance for {test_user}: {final_balance:.2f}")
            print(f"   Tokens awarded: {final_balance - initial_balance:.2f}")
        
        print("\n🎉 Credit System Test Complete!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Credit system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def initialize_founder_credits():
    """Initialize credits for the founder account"""
    try:
        print("\n🏛️ Initializing Founder Credits")
        print("-" * 30)
        
        from civic_desktop.blockchain.blockchain import Blockchain, BlockchainIntegrator
        
        founder_email = "founder@civicengagementai.org"
        
        # Check current founder credits
        current_credits = BlockchainIntegrator.get_user_credits(founder_email)
        print(f"Current founder credits: {current_credits:,}")
        
        # Award founder initial credits if needed
        if current_credits < 10000:  # Founders should have substantial credits
            credits_to_award = 10000 - current_credits
            
            credit_data = {
                "action": "credit_reward",
                "user": founder_email,
                "credits": credits_to_award,
                "reason": "founder_initialization",
                "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            success = Blockchain.add_page(credit_data, "SYSTEM")
            if success:
                print(f"✅ Awarded {credits_to_award:,} credits to founder")
                final_credits = BlockchainIntegrator.get_user_credits(founder_email)
                print(f"Final founder credits: {final_credits:,}")
            else:
                print("❌ Failed to award founder credits")
        else:
            print("✅ Founder already has sufficient credits")
            
    except Exception as e:
        print(f"❌ Founder credit initialization failed: {str(e)}")

if __name__ == "__main__":
    print("🎯 Credit System Diagnostic Tool")
    print("This tool will test and initialize the credit generation system")
    print()
    
    # Test the credit system
    if test_credit_system():
        # Initialize founder credits
        initialize_founder_credits()
        print("\n✅ All credit system operations completed successfully!")
    else:
        print("\n❌ Credit system test failed. Please check the error messages above.")