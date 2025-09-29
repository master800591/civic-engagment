"""
CIVIC LOANS & BONDS SYSTEM
==========================

Smart contract system for:
- Peer-to-peer loans with automated repayment
- Government bonds for civic funding
- Corporate bonds for platform development
- DeFi lending and borrowing protocols
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import uuid

from .civic_coin import CivicCoin


class CivicLoansAndBonds:
    """
    Comprehensive loans and bonds system for CivicCoin
    
    Features:
    - P2P lending with smart contracts
    - Government bonds for civic projects
    - Corporate bonds for platform funding
    - Automated interest calculations
    - Default protection and insurance
    """
    
    def __init__(self, civic_coin: CivicCoin):
        self.civic_coin = civic_coin
        
        # Loan Configuration
        self.min_loan_amount = Decimal('10.0')
        self.max_loan_amount = Decimal('100000.0')
        self.min_loan_duration = 7  # days
        self.max_loan_duration = 365 * 3  # 3 years
        
        # Interest Rates (annual percentage)
        self.interest_rates = {
            'personal_loan': Decimal('0.08'),      # 8% APR
            'business_loan': Decimal('0.12'),      # 12% APR
            'civic_project': Decimal('0.05'),      # 5% APR
            'emergency_loan': Decimal('0.15'),     # 15% APR
            'government_bond': Decimal('0.03'),    # 3% APR
            'corporate_bond': Decimal('0.06'),     # 6% APR
            'infrastructure_bond': Decimal('0.04') # 4% APR
        }
        
        # Risk Assessment Factors
        self.risk_multipliers = {
            'excellent': Decimal('0.8'),   # 20% rate reduction
            'good': Decimal('1.0'),        # Base rate
            'fair': Decimal('1.3'),        # 30% rate increase
            'poor': Decimal('1.8'),        # 80% rate increase
            'high_risk': Decimal('2.5')    # 150% rate increase
        }
        
        print("🏦 Loans & Bonds system initialized")
    
    def create_loan_request(self, borrower_wallet: str, amount: Decimal, 
                           loan_type: str, duration_days: int, 
                           purpose: str, collateral_wallet: str = None) -> Tuple[bool, str, Optional[str]]:
        """Create a new loan request"""
        
        try:
            # Validation
            amount = Decimal(str(amount))
            
            if amount < self.min_loan_amount or amount > self.max_loan_amount:
                return False, f"Loan amount must be between {self.min_loan_amount} and {self.max_loan_amount} CVC", None
            
            if duration_days < self.min_loan_duration or duration_days > self.max_loan_duration:
                return False, f"Loan duration must be between {self.min_loan_duration} and {self.max_loan_duration} days", None
            
            if loan_type not in self.interest_rates:
                return False, f"Invalid loan type. Available: {', '.join(self.interest_rates.keys())}", None
            
            # Check borrower wallet exists
            borrower = self.civic_coin.get_wallet(borrower_wallet)
            if not borrower:
                return False, f"Borrower wallet {borrower_wallet} not found", None
            
            # Calculate risk assessment
            risk_score = self.assess_credit_risk(borrower_wallet)
            risk_category = self.categorize_risk(risk_score)
            
            # Calculate interest rate
            base_rate = self.interest_rates[loan_type]
            risk_multiplier = self.risk_multipliers[risk_category]
            final_rate = base_rate * risk_multiplier
            
            # Calculate loan terms
            daily_rate = final_rate / Decimal('365')
            total_interest = amount * daily_rate * Decimal(str(duration_days))
            total_repayment = amount + total_interest
            
            # Create loan request
            loan_id = str(uuid.uuid4())
            loan_request = {
                'loan_id': loan_id,
                'borrower_wallet': borrower_wallet,
                'borrower_name': borrower.get('owner_name', 'Unknown'),
                'amount': str(amount),
                'loan_type': loan_type,
                'purpose': purpose,
                'duration_days': duration_days,
                'annual_interest_rate': str(final_rate),
                'total_interest': str(total_interest),
                'total_repayment': str(total_repayment),
                'risk_score': risk_score,
                'risk_category': risk_category,
                'collateral_wallet': collateral_wallet,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'funded_at': None,
                'lender_wallet': None,
                'repayment_schedule': self.generate_repayment_schedule(amount, final_rate, duration_days),
                'payments_made': [],
                'remaining_balance': str(total_repayment)
            }
            
            # Store loan request
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
            return True, f"Loan request created successfully. ID: {loan_id}", loan_id
            
        except Exception as e:
            return False, f"Failed to create loan request: {str(e)}", None
    
    def fund_loan(self, loan_id: str, lender_wallet: str) -> Tuple[bool, str]:\n        \"\"\"Fund a loan request\"\"\"\n        \n        try:\n            # Get loan request\n            loan = self.civic_coin.loans.get(loan_id)\n            if not loan:\n                return False, f\"Loan {loan_id} not found\"\n            \n            if loan['status'] != 'pending':\n                return False, f\"Loan {loan_id} is not available for funding (status: {loan['status']})\"\n            \n            # Check lender wallet\n            lender = self.civic_coin.get_wallet(lender_wallet)\n            if not lender:\n                return False, f\"Lender wallet {lender_wallet} not found\"\n            \n            amount = Decimal(loan['amount'])\n            \n            # Check lender has sufficient balance\n            if lender['balance'] < amount:\n                return False, f\"Insufficient balance. Need {amount} CVC, have {lender['balance']} CVC\"\n            \n            # Execute funding transfer\n            success, message, tx_id = self.civic_coin.transfer(\n                from_wallet=lender_wallet,\n                to_wallet=loan['borrower_wallet'],\n                amount=amount,\n                memo=f\"Loan funding: {loan_id}\"\n            )\n            \n            if not success:\n                return False, f\"Transfer failed: {message}\"\n            \n            # Update loan status\n            self.civic_coin.loans[loan_id].update({\n                'status': 'active',\n                'lender_wallet': lender_wallet,\n                'lender_name': lender.get('owner_name', 'Unknown'),\n                'funded_at': datetime.now().isoformat(),\n                'funding_transaction_id': tx_id\n            })\n            \n            # Log to blockchain\n            self.civic_coin.log_transaction({\n                'type': 'loan_funded',\n                'loan_id': loan_id,\n                'lender': lender_wallet,\n                'borrower': loan['borrower_wallet'],\n                'amount': loan['amount'],\n                'transaction_id': tx_id,\n                'timestamp': datetime.now().isoformat()\n            })\n            \n            self.civic_coin.save_data()\n            \n            print(f\"✅ Loan funded: {loan_id} by {lender_wallet}\")\n            return True, f\"Loan successfully funded. Transaction ID: {tx_id}\"\n            \n        except Exception as e:\n            return False, f\"Failed to fund loan: {str(e)}\"\n    \n    def make_loan_payment(self, loan_id: str, payment_amount: Decimal, \n                         payer_wallet: str) -> Tuple[bool, str]:\n        \"\"\"Make a payment towards a loan\"\"\"\n        \n        try:\n            # Get loan\n            loan = self.civic_coin.loans.get(loan_id)\n            if not loan:\n                return False, f\"Loan {loan_id} not found\"\n            \n            if loan['status'] != 'active':\n                return False, f\"Loan {loan_id} is not active (status: {loan['status']})\"\n            \n            # Validate payment\n            payment_amount = Decimal(str(payment_amount))\n            remaining_balance = Decimal(loan['remaining_balance'])\n            \n            if payment_amount <= 0:\n                return False, \"Payment amount must be positive\"\n            \n            if payment_amount > remaining_balance:\n                payment_amount = remaining_balance  # Pay exact remaining amount\n            \n            # Execute payment transfer\n            success, message, tx_id = self.civic_coin.transfer(\n                from_wallet=payer_wallet,\n                to_wallet=loan['lender_wallet'],\n                amount=payment_amount,\n                memo=f\"Loan payment: {loan_id}\"\n            )\n            \n            if not success:\n                return False, f\"Payment transfer failed: {message}\"\n            \n            # Record payment\n            payment_record = {\n                'payment_id': str(uuid.uuid4()),\n                'amount': str(payment_amount),\n                'payment_date': datetime.now().isoformat(),\n                'transaction_id': tx_id,\n                'payer_wallet': payer_wallet\n            }\n            \n            self.civic_coin.loans[loan_id]['payments_made'].append(payment_record)\n            \n            # Update remaining balance\n            new_balance = remaining_balance - payment_amount\n            self.civic_coin.loans[loan_id]['remaining_balance'] = str(new_balance)\n            \n            # Check if loan is fully paid\n            if new_balance <= Decimal('0.01'):  # Allow for rounding errors\n                self.civic_coin.loans[loan_id]['status'] = 'completed'\n                self.civic_coin.loans[loan_id]['completed_at'] = datetime.now().isoformat()\n            \n            # Log to blockchain\n            self.civic_coin.log_transaction({\n                'type': 'loan_payment',\n                'loan_id': loan_id,\n                'payer': payer_wallet,\n                'lender': loan['lender_wallet'],\n                'amount': str(payment_amount),\n                'remaining_balance': str(new_balance),\n                'transaction_id': tx_id,\n                'timestamp': datetime.now().isoformat()\n            })\n            \n            self.civic_coin.save_data()\n            \n            status_msg = \"Loan completed!\" if new_balance <= Decimal('0.01') else f\"Remaining balance: {new_balance} CVC\"\n            print(f\"💳 Loan payment processed: {payment_amount} CVC. {status_msg}\")\n            return True, f\"Payment successful. {status_msg}\"\n            \n        except Exception as e:\n            return False, f\"Failed to process payment: {str(e)}\"\n    \n    def create_bond(self, issuer_wallet: str, bond_type: str, face_value: Decimal,\n                   maturity_years: int, purpose: str) -> Tuple[bool, str, Optional[str]]:\n        \"\"\"Create a new bond issuance\"\"\"\n        \n        try:\n            # Validation\n            face_value = Decimal(str(face_value))\n            \n            if face_value < Decimal('100'):\n                return False, \"Minimum bond face value is 100 CVC\", None\n            \n            if bond_type not in ['government_bond', 'corporate_bond', 'infrastructure_bond']:\n                return False, \"Invalid bond type\", None\n            \n            if maturity_years < 1 or maturity_years > 30:\n                return False, \"Bond maturity must be between 1 and 30 years\", None\n            \n            # Check issuer wallet\n            issuer = self.civic_coin.get_wallet(issuer_wallet)\n            if not issuer:\n                return False, f\"Issuer wallet {issuer_wallet} not found\", None\n            \n            # Calculate bond terms\n            annual_rate = self.interest_rates[bond_type]\n            maturity_date = datetime.now() + timedelta(days=maturity_years * 365)\n            total_interest = face_value * annual_rate * Decimal(str(maturity_years))\n            maturity_value = face_value + total_interest\n            \n            # Create bond\n            bond_id = str(uuid.uuid4())\n            bond_data = {\n                'bond_id': bond_id,\n                'issuer_wallet': issuer_wallet,\n                'issuer_name': issuer.get('owner_name', 'Unknown'),\n                'bond_type': bond_type,\n                'face_value': str(face_value),\n                'annual_interest_rate': str(annual_rate),\n                'maturity_years': maturity_years,\n                'maturity_date': maturity_date.isoformat(),\n                'maturity_value': str(maturity_value),\n                'total_interest': str(total_interest),\n                'purpose': purpose,\n                'status': 'available',\n                'created_at': datetime.now().isoformat(),\n                'holders': {},  # wallet_id -> amount_held\n                'total_sold': '0'\n            }\n            \n            # Store bond\n            self.civic_coin.bonds[bond_id] = bond_data\n            \n            # Log to blockchain\n            self.civic_coin.log_transaction({\n                'type': 'bond_created',\n                'bond_id': bond_id,\n                'issuer': issuer_wallet,\n                'bond_type': bond_type,\n                'face_value': str(face_value),\n                'maturity_years': maturity_years,\n                'timestamp': datetime.now().isoformat()\n            })\n            \n            self.civic_coin.save_data()\n            \n            print(f\"📜 Bond created: {bond_id} - {face_value} CVC at {annual_rate*100:.1f}% APR\")\n            return True, f\"Bond created successfully. ID: {bond_id}\", bond_id\n            \n        except Exception as e:\n            return False, f\"Failed to create bond: {str(e)}\", None\n    \n    def purchase_bond(self, bond_id: str, buyer_wallet: str, \n                     purchase_amount: Decimal) -> Tuple[bool, str]:\n        \"\"\"Purchase bonds\"\"\"\n        \n        try:\n            # Get bond\n            bond = self.civic_coin.bonds.get(bond_id)\n            if not bond:\n                return False, f\"Bond {bond_id} not found\"\n            \n            if bond['status'] != 'available':\n                return False, f\"Bond {bond_id} is not available for purchase\"\n            \n            # Validate purchase\n            purchase_amount = Decimal(str(purchase_amount))\n            face_value = Decimal(bond['face_value'])\n            total_sold = Decimal(bond['total_sold'])\n            \n            if purchase_amount <= 0:\n                return False, \"Purchase amount must be positive\"\n            \n            if total_sold + purchase_amount > face_value:\n                return False, f\"Insufficient bonds available. Available: {face_value - total_sold} CVC\"\n            \n            # Execute purchase transfer\n            success, message, tx_id = self.civic_coin.transfer(\n                from_wallet=buyer_wallet,\n                to_wallet=bond['issuer_wallet'],\n                amount=purchase_amount,\n                memo=f\"Bond purchase: {bond_id}\"\n            )\n            \n            if not success:\n                return False, f\"Purchase transfer failed: {message}\"\n            \n            # Update bond holdings\n            if buyer_wallet not in self.civic_coin.bonds[bond_id]['holders']:\n                self.civic_coin.bonds[bond_id]['holders'][buyer_wallet] = '0'\n            \n            current_holding = Decimal(self.civic_coin.bonds[bond_id]['holders'][buyer_wallet])\n            new_holding = current_holding + purchase_amount\n            self.civic_coin.bonds[bond_id]['holders'][buyer_wallet] = str(new_holding)\n            \n            # Update total sold\n            new_total_sold = total_sold + purchase_amount\n            self.civic_coin.bonds[bond_id]['total_sold'] = str(new_total_sold)\n            \n            # Mark as sold out if fully purchased\n            if new_total_sold >= face_value:\n                self.civic_coin.bonds[bond_id]['status'] = 'sold_out'\n            \n            # Log to blockchain\n            self.civic_coin.log_transaction({\n                'type': 'bond_purchased',\n                'bond_id': bond_id,\n                'buyer': buyer_wallet,\n                'issuer': bond['issuer_wallet'],\n                'amount': str(purchase_amount),\n                'transaction_id': tx_id,\n                'timestamp': datetime.now().isoformat()\n            })\n            \n            self.civic_coin.save_data()\n            \n            print(f\"📈 Bond purchased: {purchase_amount} CVC of {bond_id}\")\n            return True, f\"Successfully purchased {purchase_amount} CVC of bonds\"\n            \n        except Exception as e:\n            return False, f\"Failed to purchase bond: {str(e)}\"\n    \n    def assess_credit_risk(self, wallet_id: str) -> float:\n        \"\"\"Assess credit risk for a wallet (simplified scoring)\"\"\"\n        \n        wallet = self.civic_coin.get_wallet(wallet_id)\n        if not wallet:\n            return 0.0\n        \n        # Risk factors (0-100 scale, higher is better)\n        score = 50.0  # Base score\n        \n        # Balance factor (higher balance = lower risk)\n        balance = float(wallet['balance'])\n        if balance > 1000:\n            score += 20\n        elif balance > 100:\n            score += 10\n        elif balance < 10:\n            score -= 20\n        \n        # Transaction history factor\n        tx_count = wallet.get('transaction_count', 0)\n        if tx_count > 50:\n            score += 15\n        elif tx_count > 10:\n            score += 5\n        \n        # Account age factor\n        created_at = datetime.fromisoformat(wallet['created_at'])\n        account_age_days = (datetime.now() - created_at).days\n        if account_age_days > 365:\n            score += 10\n        elif account_age_days > 90:\n            score += 5\n        \n        # Wallet type factor\n        if wallet['wallet_type'] == 'genesis':\n            score += 25\n        elif wallet['wallet_type'] == 'treasury':\n            score += 20\n        \n        return max(0.0, min(100.0, score))  # Clamp to 0-100\n    \n    def categorize_risk(self, risk_score: float) -> str:\n        \"\"\"Categorize risk score into risk levels\"\"\"\n        \n        if risk_score >= 80:\n            return 'excellent'\n        elif risk_score >= 65:\n            return 'good'\n        elif risk_score >= 45:\n            return 'fair'\n        elif risk_score >= 25:\n            return 'poor'\n        else:\n            return 'high_risk'\n    \n    def generate_repayment_schedule(self, principal: Decimal, annual_rate: Decimal, \n                                  duration_days: int) -> List[dict]:\n        \"\"\"Generate loan repayment schedule\"\"\"\n        \n        # Simple schedule: monthly payments if duration > 30 days\n        if duration_days <= 30:\n            # Single payment at end\n            total_interest = principal * annual_rate * Decimal(str(duration_days)) / Decimal('365')\n            return [{\n                'payment_number': 1,\n                'due_date': (datetime.now() + timedelta(days=duration_days)).isoformat(),\n                'amount': str(principal + total_interest),\n                'principal': str(principal),\n                'interest': str(total_interest)\n            }]\n        else:\n            # Monthly payments\n            monthly_rate = annual_rate / Decimal('12')\n            num_payments = max(1, duration_days // 30)\n            \n            # Simple equal payment calculation\n            monthly_payment = (principal + (principal * annual_rate * Decimal(str(duration_days)) / Decimal('365'))) / Decimal(str(num_payments))\n            \n            schedule = []\n            for i in range(num_payments):\n                due_date = datetime.now() + timedelta(days=30 * (i + 1))\n                schedule.append({\n                    'payment_number': i + 1,\n                    'due_date': due_date.isoformat(),\n                    'amount': str(monthly_payment),\n                    'principal': str(principal / Decimal(str(num_payments))),\n                    'interest': str(monthly_payment - (principal / Decimal(str(num_payments))))\n                })\n            \n            return schedule\n    \n    def get_loan_status(self, loan_id: str) -> Optional[dict]:\n        \"\"\"Get comprehensive loan status\"\"\"\n        \n        return self.civic_coin.loans.get(loan_id)\n    \n    def get_bond_status(self, bond_id: str) -> Optional[dict]:\n        \"\"\"Get comprehensive bond status\"\"\"\n        \n        return self.civic_coin.bonds.get(bond_id)\n    \n    def get_user_loans(self, wallet_id: str) -> List[dict]:\n        \"\"\"Get all loans for a user (as borrower or lender)\"\"\"\n        \n        user_loans = []\n        for loan in self.civic_coin.loans.values():\n            if (loan['borrower_wallet'] == wallet_id or \n                loan.get('lender_wallet') == wallet_id):\n                user_loans.append(loan)\n        \n        return sorted(user_loans, key=lambda x: x['created_at'], reverse=True)\n    \n    def get_user_bonds(self, wallet_id: str) -> List[dict]:\n        \"\"\"Get all bonds for a user (as issuer or holder)\"\"\"\n        \n        user_bonds = []\n        for bond in self.civic_coin.bonds.values():\n            if (bond['issuer_wallet'] == wallet_id or \n                wallet_id in bond.get('holders', {})):\n                user_bonds.append(bond)\n        \n        return sorted(user_bonds, key=lambda x: x['created_at'], reverse=True)\n