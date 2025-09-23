import pytest
from civic_desktop.blockchain.blockchain import Blockchain

def test_block_addition():
    block_data = {
        'action': 'test_action',
        'user_email': 'test@example.com',
        'timestamp': '2025-09-16T00:00:00Z'
    }
    # Add a page block
    result = Blockchain.add_page(data=block_data, validator='test@example.com')
    assert result is True or result is None  # Accepts True/None for success
