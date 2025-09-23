# crypto/wallet_ui.py
"""
PyQt5 Wallet UI: Shows user balance, transaction history, and claim/reward actions.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QHBoxLayout
from typing import Optional
from .ledger import TokenLedger

class WalletWidget(QWidget):
    from PyQt5.QtWidgets import QLineEdit, QHBoxLayout
    def __init__(self, user_email: str, ledger: TokenLedger, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.user_email = user_email
        self.ledger = ledger
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.balance_label = QLabel()
        layout.addWidget(self.balance_label)

        self.tx_table = QTableWidget()
        self.tx_table.setColumnCount(4)
        self.tx_table.setHorizontalHeaderLabels(["Type", "Amount", "Reason", "Timestamp"])
        layout.addWidget(self.tx_table)

        self.claim_btn = QPushButton("Claim Reward")
        self.claim_btn.clicked.connect(self.claim_reward)
        layout.addWidget(self.claim_btn)

        # Send tokens UI
        send_layout = QHBoxLayout()
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Recipient Email")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Reason")
        self.send_btn = QPushButton("Send Tokens")
        self.send_btn.clicked.connect(self.send_tokens)
        send_layout.addWidget(self.recipient_input)
        send_layout.addWidget(self.amount_input)
        send_layout.addWidget(self.reason_input)
        send_layout.addWidget(self.send_btn)
        layout.addLayout(send_layout)
    def send_tokens(self):
        recipient = self.recipient_input.text().strip()
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid number for amount.")
            return
        reason = self.reason_input.text().strip() or "Transfer"
        if not recipient:
            QMessageBox.warning(self, "Missing Recipient", "Please enter a recipient email.")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must be positive.")
            return
        if self.ledger.send_tokens(self.user_email, recipient, amount, reason):
            QMessageBox.information(self, "Tokens Sent", f"Sent {amount:.2f} Civic Tokens to {recipient}.")
            self.refresh()
        else:
            QMessageBox.warning(self, "Insufficient Balance", "You do not have enough tokens.")

    def refresh(self):
        balance = self.ledger.get_balance(self.user_email)
        self.balance_label.setText(f"Balance: {balance:.2f} Civic Tokens")
        txs = self.ledger.get_transaction_history(self.user_email)
        self.tx_table.setRowCount(len(txs))
        for row, tx in enumerate(txs):
            self.tx_table.setItem(row, 0, QTableWidgetItem(tx['type']))
            self.tx_table.setItem(row, 1, QTableWidgetItem(str(tx['amount'])))
            self.tx_table.setItem(row, 2, QTableWidgetItem(tx['reason']))
            self.tx_table.setItem(row, 3, QTableWidgetItem(tx['timestamp']))

    def claim_reward(self):
        # Example: Award 10 tokens for demonstration
        self.ledger.award_tokens(self.user_email, 10.0, "Manual claim")
        QMessageBox.information(self, "Reward Claimed", "You have claimed 10 Civic Tokens!")
        self.refresh()
