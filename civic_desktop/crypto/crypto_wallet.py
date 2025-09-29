"""
CIVIC CRYPTOCURRENCY WALLET & TRADING INTERFACE
===============================================

Comprehensive wallet interface for CivicCoin (CVC) with:
- Wallet management and transfers
- Loans and bonds trading
- Stock options and equity
- DeFi functionality
- Real-time portfolio tracking
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal

# Ensure civic_desktop is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
civic_desktop_dir = os.path.dirname(current_dir)
if civic_desktop_dir not in sys.path:
    sys.path.insert(0, civic_desktop_dir)

from .civic_coin import CivicCoin
from .loans_bonds import CivicLoansAndBonds
from .stock_options import CivicStockOptions

print(f"💼 Civic Cryptocurrency Wallet initializing...")


class CivicCryptoWallet:
    """
    Comprehensive cryptocurrency wallet interface
    
    Features:
    - CivicCoin (CVC) wallet management
    - P2P transfers and payments
    - Loans and bonds marketplace
    - Stock options trading
    - Portfolio analytics
    - DeFi protocols
    """
    
    def __init__(self):
        # Initialize core systems
        self.civic_coin = CivicCoin()
        self.loans_bonds = CivicLoansAndBonds(self.civic_coin)
        self.stock_options = CivicStockOptions(self.civic_coin)
        
        # Current user context
        self.current_user = None
        self.current_wallet = None
        
        # Portfolio tracking
        self.portfolio_cache = {}
        
        print(f"✅ Crypto Wallet ready with {len(self.civic_coin.wallets)} wallets")
    
    def login_user(self, user_email: str) -> bool:
        """Login user and set wallet context"""
        
        try:
            # Try to get user from session manager
            if self.civic_coin.session_manager:
                if self.civic_coin.session_manager.is_authenticated():
                    user = self.civic_coin.session_manager.get_current_user()
                    if user:
                        self.current_user = user
                        self.current_wallet = f"user_{user['email'].replace('@', '_').replace('.', '_')}"
                        
                        # Create wallet if it doesn't exist
                        if not self.civic_coin.get_wallet(self.current_wallet):
                            self.civic_coin.create_wallet(
                                self.current_wallet, 
                                wallet_type='user',
                                owner_name=f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                                owner_email=user['email']
                            )
                        
                        print(f"👤 User logged in: {self.current_wallet}")
                        return True
            
            # Fallback: create guest wallet
            self.current_user = {'email': 'guest@civic.platform', 'role': 'guest'}
            self.current_wallet = 'guest_wallet'
            
            if not self.civic_coin.get_wallet(self.current_wallet):
                self.civic_coin.create_wallet(self.current_wallet, wallet_type='user', owner_name='Guest User')
            
            print(f"🎭 Guest access: {self.current_wallet}")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def get_wallet_dashboard(self) -> dict:
        """Get comprehensive wallet dashboard data"""
        
        if not self.current_wallet:
            return {'error': 'No wallet selected'}
        
        try:
            # Basic wallet info
            wallet = self.civic_coin.get_wallet(self.current_wallet)
            if not wallet:
                return {'error': 'Wallet not found'}
            
            # Transaction history
            transactions = self.civic_coin.get_transaction_history(self.current_wallet, limit=20)
            
            # Loans and bonds
            user_loans = self.loans_bonds.get_user_loans(self.current_wallet)
            user_bonds = self.loans_bonds.get_user_bonds(self.current_wallet)
            
            # Stock options and equity
            equity_position = self.stock_options.get_wallet_equity_position(self.current_wallet)
            
            # Portfolio value calculation
            portfolio_value = self.calculate_portfolio_value()
            
            return {
                'wallet_info': wallet,
                'balance': str(wallet['balance']),
                'wallet_address': wallet['wallet_address'],
                'transactions': transactions,
                'loans': {
                    'active_loans': [loan for loan in user_loans if loan['status'] == 'active'],
                    'loan_requests': [loan for loan in user_loans if loan['status'] == 'pending'],
                    'completed_loans': [loan for loan in user_loans if loan['status'] == 'completed']
                },
                'bonds': {
                    'bonds_issued': [bond for bond in user_bonds if bond['issuer_wallet'] == self.current_wallet],
                    'bonds_owned': [bond for bond in user_bonds if self.current_wallet in bond.get('holders', {})]
                },
                'equity': equity_position,
                'portfolio': portfolio_value,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Dashboard error: {str(e)}'}
            def transfer_cvc(self, to_wallet: str, amount: str, memo: str = None) -> dict:\n        \"\"\"Transfer CVC to another wallet\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            amount_decimal = Decimal(str(amount))\n            success, message, tx_id = self.civic_coin.transfer(\n                from_wallet=self.current_wallet,\n                to_wallet=to_wallet,\n                amount=amount_decimal,\n                memo=memo\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'transaction_id': tx_id,\n                'amount': str(amount_decimal),\n                'from_wallet': self.current_wallet,\n                'to_wallet': to_wallet\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Transfer failed: {str(e)}'}\n    \n    def create_loan_request(self, amount: str, loan_type: str, duration_days: int, purpose: str) -> dict:\n        \"\"\"Create a loan request\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            amount_decimal = Decimal(str(amount))\n            success, message, loan_id = self.loans_bonds.create_loan_request(\n                borrower_wallet=self.current_wallet,\n                amount=amount_decimal,\n                loan_type=loan_type,\n                duration_days=duration_days,\n                purpose=purpose\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'loan_id': loan_id,\n                'amount': str(amount_decimal),\n                'loan_type': loan_type,\n                'duration_days': duration_days\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Loan request failed: {str(e)}'}\n    \n    def fund_loan(self, loan_id: str) -> dict:\n        \"\"\"Fund a loan request\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            success, message = self.loans_bonds.fund_loan(loan_id, self.current_wallet)\n            \n            return {\n                'success': success,\n                'message': message,\n                'loan_id': loan_id,\n                'lender': self.current_wallet\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Loan funding failed: {str(e)}'}\n    \n    def make_loan_payment(self, loan_id: str, payment_amount: str) -> dict:\n        \"\"\"Make a loan payment\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            amount_decimal = Decimal(str(payment_amount))\n            success, message = self.loans_bonds.make_loan_payment(\n                loan_id, amount_decimal, self.current_wallet\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'loan_id': loan_id,\n                'payment_amount': str(amount_decimal)\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Payment failed: {str(e)}'}\n    \n    def create_bond(self, bond_type: str, face_value: str, maturity_years: int, purpose: str) -> dict:\n        \"\"\"Create a bond issuance\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            face_value_decimal = Decimal(str(face_value))\n            success, message, bond_id = self.loans_bonds.create_bond(\n                issuer_wallet=self.current_wallet,\n                bond_type=bond_type,\n                face_value=face_value_decimal,\n                maturity_years=maturity_years,\n                purpose=purpose\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'bond_id': bond_id,\n                'face_value': str(face_value_decimal),\n                'bond_type': bond_type\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Bond creation failed: {str(e)}'}\n    \n    def purchase_bond(self, bond_id: str, purchase_amount: str) -> dict:\n        \"\"\"Purchase bonds\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            amount_decimal = Decimal(str(purchase_amount))\n            success, message = self.loans_bonds.purchase_bond(\n                bond_id, self.current_wallet, amount_decimal\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'bond_id': bond_id,\n                'purchase_amount': str(amount_decimal)\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Bond purchase failed: {str(e)}'}\n    \n    def issue_stock_options(self, recipient_wallet: str, num_options: str, \n                           strike_price: str, expiry_days: int) -> dict:\n        \"\"\"Issue stock options\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            num_options_decimal = Decimal(str(num_options))\n            strike_price_decimal = Decimal(str(strike_price))\n            \n            success, message, option_id = self.stock_options.issue_stock_options(\n                recipient_wallet=recipient_wallet,\n                num_options=num_options_decimal,\n                strike_price=strike_price_decimal,\n                expiry_days=expiry_days\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'option_id': option_id,\n                'recipient': recipient_wallet,\n                'num_options': str(num_options_decimal)\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Options issuance failed: {str(e)}'}\n    \n    def exercise_options(self, option_id: str, num_to_exercise: str) -> dict:\n        \"\"\"Exercise stock options\"\"\"\n        \n        if not self.current_wallet:\n            return {'success': False, 'message': 'No wallet selected'}\n        \n        try:\n            num_decimal = Decimal(str(num_to_exercise))\n            success, message = self.stock_options.exercise_options(\n                option_id, num_decimal, self.current_wallet\n            )\n            \n            return {\n                'success': success,\n                'message': message,\n                'option_id': option_id,\n                'num_exercised': str(num_decimal)\n            }\n            \n        except Exception as e:\n            return {'success': False, 'message': f'Options exercise failed: {str(e)}'}\n    \n    def calculate_portfolio_value(self) -> dict:\n        \"\"\"Calculate total portfolio value\"\"\"\n        \n        if not self.current_wallet:\n            return {'total_value': '0', 'breakdown': {}}\n        \n        try:\n            wallet = self.civic_coin.get_wallet(self.current_wallet)\n            cvc_balance = wallet['balance'] if wallet else Decimal('0')\n            \n            # Equity value\n            equity_position = self.stock_options.get_wallet_equity_position(self.current_wallet)\n            equity_value = Decimal(equity_position['market_value']) if equity_position else Decimal('0')\n            \n            # Bonds value (at face value for simplicity)\n            bonds_value = Decimal('0')\n            user_bonds = self.loans_bonds.get_user_bonds(self.current_wallet)\n            for bond in user_bonds:\n                if self.current_wallet in bond.get('holders', {}):\n                    holding = Decimal(bond['holders'][self.current_wallet])\n                    bonds_value += holding\n            \n            # Loans value (outstanding loans as assets)\n            loans_value = Decimal('0')\n            user_loans = self.loans_bonds.get_user_loans(self.current_wallet)\n            for loan in user_loans:\n                if loan['lender_wallet'] == self.current_wallet and loan['status'] == 'active':\n                    remaining = Decimal(loan['remaining_balance'])\n                    loans_value += remaining\n            \n            total_value = cvc_balance + equity_value + bonds_value + loans_value\n            \n            return {\n                'total_value': str(total_value),\n                'breakdown': {\n                    'cvc_balance': str(cvc_balance),\n                    'equity_value': str(equity_value),\n                    'bonds_value': str(bonds_value),\n                    'loans_value': str(loans_value)\n                },\n                'last_updated': datetime.now().isoformat()\n            }\n            \n        except Exception as e:\n            return {'total_value': '0', 'error': str(e)}\n    \n    def get_market_data(self) -> dict:\n        \"\"\"Get market data and statistics\"\"\"\n        \n        try:\n            # CivicCoin stats\n            cvc_stats = {\n                'total_supply': str(self.civic_coin.total_supply),\n                'circulating_supply': str(self.civic_coin.circulating_supply),\n                'total_wallets': len(self.civic_coin.wallets),\n                'total_transactions': len(self.civic_coin.transactions)\n            }\n            \n            # Platform equity stats\n            equity_stats = self.stock_options.get_platform_equity_stats()\n            \n            # Loans market stats\n            loans_stats = {\n                'active_loans': len([loan for loan in self.civic_coin.loans.values() if loan['status'] == 'active']),\n                'pending_requests': len([loan for loan in self.civic_coin.loans.values() if loan['status'] == 'pending']),\n                'total_loans_issued': len(self.civic_coin.loans)\n            }\n            \n            # Bonds market stats\n            bonds_stats = {\n                'active_bonds': len([bond for bond in self.civic_coin.bonds.values() if bond['status'] in ['available', 'sold_out']]),\n                'total_bonds_issued': len(self.civic_coin.bonds)\n            }\n            \n            return {\n                'civic_coin': cvc_stats,\n                'equity': equity_stats,\n                'loans': loans_stats,\n                'bonds': bonds_stats,\n                'last_updated': datetime.now().isoformat()\n            }\n            \n        except Exception as e:\n            return {'error': f'Market data error: {str(e)}'}\n    \n    def get_available_loan_requests(self) -> List[dict]:\n        \"\"\"Get all available loan requests for funding\"\"\"\n        \n        return [loan for loan in self.civic_coin.loans.values() \n                if loan['status'] == 'pending']\n    \n    def get_available_bonds(self) -> List[dict]:\n        \"\"\"Get all available bonds for purchase\"\"\"\n        \n        return [bond for bond in self.civic_coin.bonds.values() \n                if bond['status'] == 'available']\n    \n    def search_wallets(self, query: str) -> List[dict]:\n        \"\"\"Search for wallets by name or address\"\"\"\n        \n        results = []\n        query_lower = query.lower()\n        \n        for wallet_id, wallet in self.civic_coin.wallets.items():\n            if (query_lower in wallet.get('owner_name', '').lower() or\n                query_lower in wallet.get('wallet_address', '').lower() or\n                query_lower in wallet_id.lower()):\n                results.append({\n                    'wallet_id': wallet_id,\n                    'owner_name': wallet.get('owner_name', 'Unknown'),\n                    'wallet_address': wallet.get('wallet_address', ''),\n                    'wallet_type': wallet.get('wallet_type', 'user')\n                })\n        \n        return results[:10]  # Limit to 10 results\n\n\ndef display_wallet_interface():\n    \"\"\"Display the wallet interface\"\"\"\n    \n    wallet = CivicCryptoWallet()\n    \n    # Try to login user\n    wallet.login_user(\"\")\n    \n    print(\"\\n\" + \"=\"*80)\n    print(\"💼 CIVIC CRYPTOCURRENCY WALLET - FULL FEATURE INTERFACE\")\n    print(\"=\"*80)\n    \n    # Get dashboard data\n    dashboard = wallet.get_dashboard()\n    \n    if 'error' in dashboard:\n        print(f\"❌ Dashboard Error: {dashboard['error']}\")\n        return\n    \n    # Display wallet info\n    wallet_info = dashboard['wallet_info']\n    print(f\"\\n💳 WALLET INFORMATION\")\n    print(\"-\" * 50)\n    print(f\"Owner: {wallet_info.get('owner_name', 'Unknown')}\")\n    print(f\"Wallet ID: {wallet_info['wallet_id']}\")\n    print(f\"Address: {wallet_info['wallet_address']}\")\n    print(f\"Balance: {dashboard['balance']} CVC\")\n    print(f\"Type: {wallet_info.get('wallet_type', 'user').title()}\")\n    print(f\"Created: {wallet_info.get('created_at', 'Unknown')}\")\n    \n    # Display portfolio\n    portfolio = dashboard['portfolio']\n    if portfolio:\n        print(f\"\\n📊 PORTFOLIO VALUE\")\n        print(\"-\" * 50)\n        print(f\"Total Portfolio Value: {portfolio['total_value']} CVC\")\n        if 'breakdown' in portfolio:\n            breakdown = portfolio['breakdown']\n            print(f\"  • CVC Balance: {breakdown['cvc_balance']} CVC\")\n            print(f\"  • Equity Value: {breakdown['equity_value']} CVC\")\n            print(f\"  • Bonds Value: {breakdown['bonds_value']} CVC\")\n            print(f\"  • Loans Value: {breakdown['loans_value']} CVC\")\n    \n    # Display recent transactions\n    transactions = dashboard.get('transactions', [])\n    if transactions:\n        print(f\"\\n📋 RECENT TRANSACTIONS ({len(transactions)} total)\")\n        print(\"-\" * 50)\n        for i, tx in enumerate(transactions[:5], 1):\n            tx_type = tx.get('type', 'unknown')\n            amount = tx.get('amount', '0')\n            timestamp = tx.get('timestamp', '')[:19].replace('T', ' ')\n            print(f\"{i:2d}. {tx_type.replace('_', ' ').title()}: {amount} CVC ({timestamp})\")\n            if tx.get('memo'):\n                print(f\"    Memo: {tx['memo']}\")\n    \n    # Display loans\n    loans = dashboard.get('loans', {})\n    if loans:\n        active_loans = loans.get('active_loans', [])\n        loan_requests = loans.get('loan_requests', [])\n        \n        if active_loans or loan_requests:\n            print(f\"\\n🏦 LOANS & LENDING\")\n            print(\"-\" * 50)\n            \n            if active_loans:\n                print(f\"Active Loans: {len(active_loans)}\")\n                for loan in active_loans[:3]:\n                    amount = loan.get('amount', '0')\n                    remaining = loan.get('remaining_balance', '0')\n                    loan_type = loan.get('loan_type', 'unknown')\n                    print(f\"  • {loan_type.replace('_', ' ').title()}: {amount} CVC (Remaining: {remaining})\")\n            \n            if loan_requests:\n                print(f\"Pending Requests: {len(loan_requests)}\")\n                for request in loan_requests[:3]:\n                    amount = request.get('amount', '0')\n                    loan_type = request.get('loan_type', 'unknown')\n                    print(f\"  • {loan_type.replace('_', ' ').title()}: {amount} CVC (Pending approval)\")\n    \n    # Display bonds\n    bonds = dashboard.get('bonds', {})\n    if bonds:\n        bonds_issued = bonds.get('bonds_issued', [])\n        bonds_owned = bonds.get('bonds_owned', [])\n        \n        if bonds_issued or bonds_owned:\n            print(f\"\\n📜 BONDS & SECURITIES\")\n            print(\"-\" * 50)\n            \n            if bonds_issued:\n                print(f\"Bonds Issued: {len(bonds_issued)}\")\n                for bond in bonds_issued[:3]:\n                    face_value = bond.get('face_value', '0')\n                    bond_type = bond.get('bond_type', 'unknown')\n                    maturity_date = bond.get('maturity_date', '')[:10]\n                    print(f\"  • {bond_type.replace('_', ' ').title()}: {face_value} CVC (Maturity: {maturity_date})\")\n            \n            if bonds_owned:\n                print(f\"Bonds Owned: {len(bonds_owned)}\")\n    \n    # Display equity position\n    equity = dashboard.get('equity')\n    if equity:\n        print(f\"\\n📈 EQUITY & STOCK OPTIONS\")\n        print(\"-\" * 50)\n        print(f\"Shares Owned: {equity['shares_owned']}\")\n        print(f\"Voting Power: {equity['voting_power']}\")\n        print(f\"Market Value: {equity['market_value']} CVC\")\n        print(f\"Ownership: {equity['ownership_percentage']}%\")\n        print(f\"Dividend Earnings: {equity['dividend_earnings']} CVC\")\n        print(f\"Active Options: {equity['active_options']}\")\n    \n    # Get market data\n    market_data = wallet.get_market_data()\n    if 'error' not in market_data:\n        print(f\"\\n🌐 MARKET DATA\")\n        print(\"-\" * 50)\n        \n        cvc_stats = market_data.get('civic_coin', {})\n        print(f\"CivicCoin Supply: {cvc_stats.get('circulating_supply', '0')} / {cvc_stats.get('total_supply', '0')} CVC\")\n        print(f\"Total Wallets: {cvc_stats.get('total_wallets', 0)}\")\n        print(f\"Total Transactions: {cvc_stats.get('total_transactions', 0)}\")\n        \n        equity_stats = market_data.get('equity', {})\n        if equity_stats:\n            print(f\"Platform Shares: {equity_stats.get('issued_shares', '0')} / {equity_stats.get('total_shares', '0')}\")\n            print(f\"Share Price: {equity_stats.get('current_share_price', '0')} CVC\")\n            print(f\"Market Cap: {equity_stats.get('market_capitalization', '0')} CVC\")\n        \n        loans_stats = market_data.get('loans', {})\n        if loans_stats:\n            print(f\"Active Loans: {loans_stats.get('active_loans', 0)}\")\n            print(f\"Pending Requests: {loans_stats.get('pending_requests', 0)}\")\n        \n        bonds_stats = market_data.get('bonds', {})\n        if bonds_stats:\n            print(f\"Active Bonds: {bonds_stats.get('active_bonds', 0)}\")\n    \n    print(f\"\\n🔐 SECURITY & FEATURES\")\n    print(\"-\" * 50)\n    print(\"✅ Blockchain-backed transactions\")\n    print(\"✅ Smart contracts for loans and bonds\")\n    print(\"✅ Stock options and equity trading\")\n    print(\"✅ Real-time portfolio tracking\")\n    print(\"✅ Governance token voting rights\")\n    print(\"✅ DeFi functionality\")\n    print(\"✅ Audit trail and transparency\")\n    \n    print(\"\\n\" + \"=\"*80)\n    print(f\"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Civic Crypto Wallet Ready\")\n    print(\"=\"*80)\n    \n    return wallet\n\n\ndef test_crypto_functionality():\n    \"\"\"Test cryptocurrency functionality\"\"\"\n    \n    print(\"\\n🧪 TESTING CRYPTOCURRENCY FUNCTIONALITY\")\n    print(\"=\"*50)\n    \n    wallet = CivicCryptoWallet()\n    wallet.login_user(\"\")\n    \n    # Test transfer\n    print(\"\\n1. Testing CVC Transfer...\")\n    result = wallet.transfer_cvc('user_alice', '10.0', 'Test transfer')\n    print(f\"   Result: {result['success']} - {result['message']}\")\n    \n    # Test loan request\n    print(\"\\n2. Testing Loan Request...\")\n    result = wallet.create_loan_request('500.0', 'personal_loan', 90, 'Home improvement')\n    print(f\"   Result: {result['success']} - {result['message']}\")\n    \n    # Test bond creation\n    print(\"\\n3. Testing Bond Issuance...\")\n    result = wallet.create_bond('government_bond', '1000.0', 2, 'Infrastructure development')\n    print(f\"   Result: {result['success']} - {result['message']}\")\n    \n    # Test stock options\n    print(\"\\n4. Testing Stock Options...\")\n    result = wallet.issue_stock_options('user_alice', '100', '10.0', 365)\n    print(f\"   Result: {result['success']} - {result['message']}\")\n    \n    print(\"\\n✅ Crypto functionality testing complete!\")\n\n\ndef main():\n    \"\"\"Main function - crypto wallet interface\"\"\"\n    \n    print(\"💰 CIVIC CRYPTOCURRENCY SYSTEM\")\n    print(\"Full-featured digital currency with loans, bonds, and equity\")\n    print(\"=\"*60)\n    \n    # Display main interface\n    crypto_wallet = display_wallet_interface()\n    \n    # Test functionality\n    test_crypto_functionality()\n    \n    print(f\"\\n✅ Civic Cryptocurrency System Ready!\")\n    print(\"Features available: Transfers, Loans, Bonds, Stock Options, DeFi\")\n    \n    return crypto_wallet\n\n\nif __name__ == \"__main__\":\n    main()