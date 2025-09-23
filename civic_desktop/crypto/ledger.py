# crypto/ledger.py
"""
TokenLedger: Tracks user balances, transactions, rewards, and penalties.
Integrates with blockchain for audit trail.
"""
from typing import Dict, List, Any
from datetime import datetime

class TokenLedger:
    def send_tokens(self, sender_email: str, recipient_email: str, amount: float, reason: str) -> bool:
        if self.get_balance(sender_email) < amount or amount <= 0:
            return False
        self.balances[sender_email] -= amount
        self.balances[recipient_email] = self.get_balance(recipient_email) + amount
        tx: Dict[str, Any] = {
            'sender_email': sender_email,
            'recipient_email': recipient_email,
            'amount': amount,
            'type': 'transfer',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        self.transactions.append(tx)
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            Blockchain.add_page(tx, validator=sender_email)
        except Exception as e:
            print(f"Blockchain record failed: {e}")
        return True
    def __init__(self):
        self.balances: Dict[str, float] = {}
        self.transactions: List[Dict[str, Any]] = []

    def get_balance(self, user_email: str) -> float:
        return self.balances.get(user_email, 0.0)

    def award_tokens(self, user_email: str, amount: float, reason: str) -> None:
        self.balances[user_email] = self.get_balance(user_email) + amount
        tx: Dict[str, Any] = {
            'user_email': user_email,
            'amount': amount,
            'type': 'reward',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        self.transactions.append(tx)
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            # Use user_email as validator, no signature (will be auto-generated)
            Blockchain.add_page(tx, validator=user_email)
        except Exception as e:
            print(f"Blockchain record failed: {e}")

    def penalize_tokens(self, user_email: str, amount: float, reason: str) -> None:
        self.balances[user_email] = max(0.0, self.get_balance(user_email) - amount)
        tx: Dict[str, Any] = {
            'user_email': user_email,
            'amount': -amount,
            'type': 'penalty',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        self.transactions.append(tx)
        try:
            from civic_desktop.blockchain.blockchain import Blockchain
            Blockchain.add_page(tx, validator=user_email)
        except Exception as e:
            print(f"Blockchain record failed: {e}")

    def get_transaction_history(self, user_email: str) -> List[Dict[str, Any]]:
        return [tx for tx in self.transactions if tx['user_email'] == user_email]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'balances': self.balances,
            'transactions': self.transactions
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.balances = data.get('balances', {})
        self.transactions = data.get('transactions', [])
