#!/usr/bin/env python3
"""
Quick wallet checker
"""

from civic_coin import CivicCoin

cc = CivicCoin()
print('Available wallets:')
for k, v in cc.wallets.items():
    print(f'  {k}: {v.get("balance", 0)} CVC ({v.get("wallet_type", "unknown")})')

print(f'\nTotal circulation: {cc.circulating_supply} CVC')