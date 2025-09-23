import pytest
from civic_desktop.moderation.backend import ModerationBackend

def test_flag_content():
    result, msg = ModerationBackend.flag_content(
        content_type='debate',
        content_id='topic123',
        reason='Test reason',
        reporter_email='citizen@example.com',
        severity='medium'
    )
    assert result is True
    assert 'flagged' in msg
