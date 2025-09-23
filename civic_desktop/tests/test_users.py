import pytest
from civic_desktop.users.backend import UserBackend

def test_password_hash_and_verify():
    password = 'TestPassword123!'
    hashed = UserBackend.hash_password(password)
    assert UserBackend.verify_password(password, hashed)
    assert not UserBackend.verify_password('WrongPassword', hashed)

def test_duplicate_id_detection(tmp_path):
    # Create a fake ID document
    id_path = tmp_path / 'id.txt'
    id_path.write_text('unique-id-content')
    hash1 = UserBackend.hash_password('unique-id-content')
    # Register first user
    data = {
        'first_name': 'Alice', 'last_name': 'Smith', 'address': '123 Main St',
        'city': 'Testville', 'state': 'TS', 'country': 'Testland',
        'email': 'alice@example.com', 'password': 'password123'
    }
    UserBackend.register_user(data, str(id_path))
    # Try registering duplicate
    result, msg = UserBackend.register_user(data, str(id_path))
    assert not result
    assert 'Duplicate ID document' in msg
