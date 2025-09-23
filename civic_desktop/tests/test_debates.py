import pytest
from civic_desktop.debates.backend import create_topic

def test_create_topic():
    result, msg = create_topic(
        title='Test Topic',
        description='Test Description',
        creator_email='rep@example.com'
    )
    assert result is True
    assert 'created' in msg
