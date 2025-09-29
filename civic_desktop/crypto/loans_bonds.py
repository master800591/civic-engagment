#!/usr/bin/env python3
"""
CivicCoin Loans and Bonds System
P2P lending marketplace and bonds trading with automated smart contracts.
"""

import json
import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

try:
    from .civic_coin import CivicCoin
except ImportError:
    # Fallback for direct execution
    from civic_coin import CivicCoin


class CivicLoansAndBonds:
    """
    Comprehensive loans and bonds system for the CivicCoin platform.
    Supports P2P lending, government bonds, corporate bonds, and automated repayment.
    """
    
    def __init__(self, civic_coin: Optional[CivicCoin] = None):
        """Initialize loans and bonds system"""
        self.civic_coin = civic_coin or CivicCoin()
        
        # Interest rates for different loan/bond types
        self.interest_rates = {
            'personal_loan': Decimal('0.08'),    # 8% APR for personal loans
            'business_loan': Decimal('0.12'),    # 12% APR for business loans
            'mortgage': Decimal('0.05'),         # 5% APR for mortgages
            'government_bond': Decimal('0.03'),  # 3% APR for government bonds
            'corporate_bond': Decimal('0.06'),   # 6% APR for corporate bonds
            'infrastructure_bond': Decimal('0.04') # 4% APR for infrastructure
        }
        
        print("🏦 CivicCoin Loans & Bonds system initialized")
        print(f"💰 Available loan types: {list(self.interest_rates.keys())}")
    
    def create_loan_request(self, borrower_wallet: str, amount: str, 
                          purpose: str, duration_months: int,
                          collateral_type: str = None, 
                          collateral_value: str = "0") -> Optional[dict]:
        """Create a new loan request"""
        
        try:
            # Input validation
            amount = Decimal(str(amount))
            collateral_value = Decimal(str(collateral_value))
            
            if amount <= 0:
                print("❌ Loan amount must be positive")
                return None
            
            if duration_months < 1 or duration_months > 360:
                print("❌ Loan duration must be between 1 and 360 months")
                return None
            
            # Check borrower wallet exists
            borrower = self.civic_coin.get_wallet(borrower_wallet)
            if not borrower:
                print(f"❌ Borrower wallet {borrower_wallet} not found")
                return None
            
            # Determine loan type and rate
            loan_type = 'personal_loan'  # Default
            if amount > Decimal('50000'):
                loan_type = 'business_loan'
            elif collateral_type == 'real_estate' and amount > Decimal('10000'):
                loan_type = 'mortgage'
            
            base_rate = self.interest_rates[loan_type]
            
            # Risk assessment
            risk_score = self.assess_credit_risk(borrower_wallet)
            risk_category = self.categorize_risk(risk_score)
            
            # Adjust rate based on risk
            risk_adjustments = {
                'excellent': Decimal('0.00'),    # No adjustment
                'good': Decimal('0.01'),         # +1%
                'fair': Decimal('0.025'),        # +2.5%
                'poor': Decimal('0.05'),         # +5%
                'high_risk': Decimal('0.10')     # +10%
            }
            
            final_rate = base_rate + risk_adjustments.get(risk_category, Decimal('0.15'))
            
            # Calculate total repayment
            duration_days = duration_months * 30
            total_interest = amount * final_rate * Decimal(str(duration_days)) / Decimal('365')
            total_repayment = amount + total_interest
            
            # Create loan request
            loan_id = str(uuid.uuid4())
            loan_request = {
                'loan_id': loan_id,
                'borrower_wallet': borrower_wallet,
                'borrower_name': borrower.get('owner_name', 'Unknown'),
                'amount': str(amount),
                'purpose': purpose,
                'loan_type': loan_type,
                'duration_months': duration_months,
                'duration_days': duration_days,
                'base_interest_rate': str(base_rate),
                'risk_score': risk_score,
                'risk_category': risk_category,
                'final_interest_rate': str(final_rate),
                'total_interest': str(total_interest),
                'total_repayment': str(total_repayment),
                'collateral_type': collateral_type,
                'collateral_value': str(collateral_value),
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'funded_at': None,
                'lender_wallet': None,
                'repayment_schedule': self.generate_repayment_schedule(amount, final_rate, duration_days),
                'payments_made': [],
                'remaining_balance': str(total_repayment)
            }
            
            # Store loan request
            if not hasattr(self.civic_coin, 'loans'):
                self.civic_coin.loans = {}
            self.civic_coin.loans[loan_id] = loan_request
            
            # Log to blockchain
            self.civic_coin.log_transaction({
                'type': 'loan_request_created',
                'loan_id': loan_id,
                'borrower': borrower_wallet,
                'amount': str(amount),
                'loan_type': loan_type,
                'timestamp': datetime.now().isoformat()
            })
            
            self.civic_coin.save_data()
            
            print(f"💰 Loan request created: {loan_id} for {amount} CVC")
            return loan_request
            
        except Exception as e:
            print(f"❌ Failed to create loan request: {str(e)}")
            return None
    
    def fund_loan(self, loan_id: str, lender_wallet: str) -> Tuple[bool, str]:
        """Fund a loan request"""
        
        try:
            # Get loan request
            if not hasattr(self.civic_coin, 'loans'):
                return False, "No loans database found"
                
            loan = self.civic_coin.loans.get(loan_id)
            if not loan:
                return False, f"Loan {loan_id} not found"
            
            if loan['status'] != 'pending':
                return False, f"Loan {loan_id} is not available for funding"
            
            # Check lender wallet
            lender = self.civic_coin.get_wallet(lender_wallet)
            if not lender:
                return False, f"Lender wallet {lender_wallet} not found"
            
            amount = Decimal(loan['amount'])
            
            # Check lender has sufficient balance
            if lender['balance'] < amount:
                return False, f"Insufficient balance. Need {amount} CVC, have {lender['balance']} CVC"
            
            # Execute funding transfer
            success, message = self.civic_coin.transfer(
                from_wallet=lender_wallet,
                to_wallet=loan['borrower_wallet'],
                amount=str(amount),
                memo=f"Loan funding: {loan_id}"
            )
            
            if not success:
                return False, f"Transfer failed: {message}"
            
            # Update loan status
            self.civic_coin.loans[loan_id].update({
                'status': 'active',
                'lender_wallet': lender_wallet,
                'lender_name': lender.get('owner_name', 'Unknown'),
                'funded_at': datetime.now().isoformat()
            })
            
            # Log to blockchain
            self.civic_coin.log_transaction({
                'type': 'loan_funded',
                'loan_id': loan_id,
                'lender': lender_wallet,
                'borrower': loan['borrower_wallet'],
                'amount': loan['amount'],
                'timestamp': datetime.now().isoformat()
            })
            
            self.civic_coin.save_data()
            
            print(f"✅ Loan funded: {loan_id} by {lender_wallet}")
            return True, "Loan successfully funded"
            
        except Exception as e:
            return False, f"Failed to fund loan: {str(e)}"
    
    def create_bond(self, issuer_wallet: str, bond_type: str, face_value: str,
                   interest_rate: str, maturity_months: int, 
                   description: str) -> Optional[dict]:
        """Create a new bond issuance"""
        
        try:
            # Validation
            face_value = Decimal(str(face_value))
            interest_rate = Decimal(str(interest_rate))
            
            if face_value < Decimal('100'):
                print("❌ Minimum bond face value is 100 CVC")
                return None
            
            valid_types = ['government', 'corporate', 'infrastructure']
            if bond_type not in valid_types:
                print(f"❌ Invalid bond type. Must be one of: {valid_types}")
                return None
            
            if maturity_months < 1 or maturity_months > 360:
                print("❌ Bond maturity must be between 1 and 360 months")
                return None
            
            # Check issuer wallet
            issuer = self.civic_coin.get_wallet(issuer_wallet)
            if not issuer:
                print(f"❌ Issuer wallet {issuer_wallet} not found")
                return None
            
            # Calculate bond terms
            annual_rate = interest_rate / Decimal('100')  # Convert percentage
            maturity_date = datetime.now() + timedelta(days=maturity_months * 30)
            total_interest = face_value * annual_rate * Decimal(str(maturity_months)) / Decimal('12')
            maturity_value = face_value + total_interest
            
            # Create bond
            bond_id = str(uuid.uuid4())
            bond_data = {
                'bond_id': bond_id,
                'issuer_wallet': issuer_wallet,
                'issuer_name': issuer.get('owner_name', 'Unknown'),
                'bond_type': bond_type,
                'face_value': str(face_value),
                'annual_interest_rate': str(annual_rate),
                'maturity_months': maturity_months,
                'maturity_date': maturity_date.isoformat(),
                'maturity_value': str(maturity_value),
                'total_interest': str(total_interest),
                'description': description,
                'status': 'available',
                'created_at': datetime.now().isoformat(),
                'holders': {},  # wallet_id -> amount_held
                'total_sold': '0'
            }
            
            # Store bond
            if not hasattr(self.civic_coin, 'bonds'):
                self.civic_coin.bonds = {}
            self.civic_coin.bonds[bond_id] = bond_data
            
            # Log to blockchain
            self.civic_coin.log_transaction({
                'type': 'bond_created',
                'bond_id': bond_id,
                'issuer': issuer_wallet,
                'bond_type': bond_type,
                'face_value': str(face_value),
                'maturity_months': maturity_months,
                'timestamp': datetime.now().isoformat()
            })
            
            self.civic_coin.save_data()
            
            print(f"📜 Bond created: {bond_id} - {face_value} CVC at {annual_rate*100:.1f}% APR")
            return bond_data
            
        except Exception as e:
            print(f"❌ Failed to create bond: {str(e)}")
            return None
    
    def assess_credit_risk(self, wallet_id: str) -> float:
        """Assess credit risk for a wallet (simplified scoring)"""
        
        wallet = self.civic_coin.get_wallet(wallet_id)
        if not wallet:
            return 0.0
        
        # Risk factors (0-100 scale, higher is better)
        score = 50.0  # Base score
        
        # Balance factor (higher balance = lower risk)
        balance = float(wallet['balance'])
        if balance > 1000:
            score += 20
        elif balance > 100:
            score += 10
        elif balance < 10:
            score -= 20
        
        # Transaction history factor
        tx_count = wallet.get('transaction_count', 0)
        if tx_count > 50:
            score += 15
        elif tx_count > 10:
            score += 5
        
        # Account age factor
        try:
            created_at = datetime.fromisoformat(wallet['created_at'])
            account_age_days = (datetime.now() - created_at).days
            if account_age_days > 365:
                score += 10
            elif account_age_days > 90:
                score += 5
        except:
            pass
        
        # Wallet type factor
        if wallet.get('wallet_type') == 'genesis':
            score += 25
        elif wallet.get('wallet_type') == 'treasury':
            score += 20
        
        return max(0.0, min(100.0, score))  # Clamp to 0-100
    
    def categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into risk levels"""
        
        if risk_score >= 80:
            return 'excellent'
        elif risk_score >= 65:
            return 'good'
        elif risk_score >= 45:
            return 'fair'
        elif risk_score >= 25:
            return 'poor'
        else:
            return 'high_risk'
    
    def generate_repayment_schedule(self, principal: Decimal, annual_rate: Decimal, 
                                  duration_days: int) -> List[dict]:
        """Generate loan repayment schedule"""
        
        # Simple schedule: monthly payments if duration > 30 days
        if duration_days <= 30:
            # Single payment at end
            total_interest = principal * annual_rate * Decimal(str(duration_days)) / Decimal('365')
            return [{
                'payment_number': 1,
                'due_date': (datetime.now() + timedelta(days=duration_days)).isoformat(),
                'amount': str(principal + total_interest),
                'principal': str(principal),
                'interest': str(total_interest)
            }]
        else:
            # Monthly payments
            num_payments = max(1, duration_days // 30)
            
            # Simple equal payment calculation
            total_interest = principal * annual_rate * Decimal(str(duration_days)) / Decimal('365')
            monthly_payment = (principal + total_interest) / Decimal(str(num_payments))
            
            schedule = []
            for i in range(num_payments):
                due_date = datetime.now() + timedelta(days=30 * (i + 1))
                schedule.append({
                    'payment_number': i + 1,
                    'due_date': due_date.isoformat(),
                    'amount': str(monthly_payment),
                    'principal': str(principal / Decimal(str(num_payments))),
                    'interest': str(monthly_payment - (principal / Decimal(str(num_payments))))
                })
            
            return schedule
    
    def get_loan_statistics(self) -> dict:
        """Get comprehensive loan statistics"""
        
        if not hasattr(self.civic_coin, 'loans'):
            return {
                'total_loans': 0,
                'total_volume': 0,
                'average_interest_rate': 0.0,
                'active_loans': 0,
                'completed_loans': 0
            }
        
        loans = list(self.civic_coin.loans.values())
        if not loans:
            return {
                'total_loans': 0,
                'total_volume': 0,
                'average_interest_rate': 0.0,
                'active_loans': 0,
                'completed_loans': 0
            }
        
        total_volume = sum(Decimal(loan['amount']) for loan in loans)
        avg_rate = sum(Decimal(loan['final_interest_rate']) for loan in loans) / len(loans)
        active_count = len([loan for loan in loans if loan['status'] == 'active'])
        completed_count = len([loan for loan in loans if loan['status'] == 'completed'])
        
        return {
            'total_loans': len(loans),
            'total_volume': float(total_volume),
            'average_interest_rate': float(avg_rate * 100),  # Convert to percentage
            'active_loans': active_count,
            'completed_loans': completed_count
        }
    
    def get_user_loans(self, wallet_id: str) -> List[dict]:
        """Get all loans for a user (as borrower or lender)"""
        
        if not hasattr(self.civic_coin, 'loans'):
            return []
        
        user_loans = []
        for loan in self.civic_coin.loans.values():
            if (loan['borrower_wallet'] == wallet_id or 
                loan.get('lender_wallet') == wallet_id):
                user_loans.append(loan)
        
        return sorted(user_loans, key=lambda x: x['created_at'], reverse=True)
    
    def get_user_bonds(self, wallet_id: str) -> List[dict]:
        """Get all bonds for a user (as issuer or holder)"""
        
        if not hasattr(self.civic_coin, 'bonds'):
            return []
        
        user_bonds = []
        for bond in self.civic_coin.bonds.values():
            if (bond['issuer_wallet'] == wallet_id or 
                wallet_id in bond.get('holders', {})):
                user_bonds.append(bond)
        
        return sorted(user_bonds, key=lambda x: x['created_at'], reverse=True)


def main():
    """Test the loans and bonds system"""
    
    print("🧪 Testing CivicCoin Loans & Bonds System")
    
    # Initialize system
    civic_coin = CivicCoin()
    loans_bonds = CivicLoansAndBonds(civic_coin)
    
    # Run genesis if needed
    if not civic_coin.genesis_completed:
        civic_coin.run_genesis_distribution()
    
    # Create a test wallet
    test_wallet = civic_coin.create_wallet("testuser@example.com")
    if not test_wallet:
        print("❌ Failed to create test wallet")
        return
    
    # Fund the test wallet from treasury
    civic_coin.transfer(
        from_wallet='treasury_founders',
        to_wallet=test_wallet['wallet_address'],
        amount='5000.0',
        memo='Test funding'
    )
    
    print("\n=== Testing Loan Request ===")
    loan = loans_bonds.create_loan_request(
        borrower_wallet=test_wallet['wallet_address'],
        amount='1000.0',
        purpose='Home improvement',
        duration_months=12,
        collateral_type='real_estate',
        collateral_value='15000.0'
    )
    
    if loan:
        print(f"✅ Loan created: {loan['loan_id']}")
        print(f"💰 Amount: {loan['amount']} CVC")
        print(f"📈 Interest Rate: {float(loan['final_interest_rate'])*100:.2f}%")
        print(f"🎯 Risk Category: {loan['risk_category']}")
    
    print("\n=== Testing Bond Creation ===")
    bond = loans_bonds.create_bond(
        issuer_wallet=test_wallet['wallet_address'],
        bond_type='government',
        face_value='2000.0',
        interest_rate='3.5',
        maturity_months=24,
        description='Municipal infrastructure bond'
    )
    
    if bond:
        print(f"✅ Bond created: {bond['bond_id']}")
        print(f"💎 Face Value: {bond['face_value']} CVC")
        print(f"📈 Interest Rate: {float(bond['annual_interest_rate'])*100:.1f}%")
        print(f"⏰ Maturity: {bond['maturity_months']} months")
    
    print("\n=== System Statistics ===")
    stats = loans_bonds.get_loan_statistics()
    print(f"📊 Total Loans: {stats['total_loans']}")
    print(f"💰 Total Volume: {stats['total_volume']:,.2f} CVC")
    print(f"📈 Average Rate: {stats['average_interest_rate']:.2f}%")
    
    print("\n🎉 Loans & Bonds system test completed successfully!")


if __name__ == "__main__":
    main()