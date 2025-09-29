# Civic Engagement Platform - Test Suite

This directory contains all test files organized by module and functionality.

## Directory Structure

### `/tests/blockchain/`
Blockchain system tests and demonstrations:
- `demo_simple.py` - Basic blockchain functionality demonstration
- `demo_complete_integration.py` - Complete user-blockchain integration demo
- `test_blockchain_demo.py` - Blockchain unit tests
- `test_integration.py` - Blockchain integration tests

### `/tests/users/`
User management system tests:
- `test_users_demo.py` - User registration, authentication, and key management tests
- `test_integration.py` - User-blockchain integration tests

### `/tests/integration/`
Cross-module integration tests (reserved for future expansion)

## Running Tests

From the `civic_desktop/` directory:

```bash
# Run specific test files
python tests/blockchain/demo_simple.py
python tests/users/test_users_demo.py

# Run all tests (future pytest integration)
pytest tests/
```

## Test Coverage

### ✅ Implemented Tests
- Blockchain core functionality (Pages → Chapters → Books hierarchy)
- Constitutional governance framework
- User registration with blockchain integration
- Cryptographic signing and validation
- Proof of Authority consensus
- User-blockchain data flow

### 🔧 Future Test Expansion
- Debate system integration
- Moderation workflow tests
- Contract-based governance tests
- Election system validation
- P2P networking tests
- Cross-module integration suites

## Test Data

All tests use isolated test data and do not affect production databases. Each test creates temporary data structures for validation.

## Dependencies

Tests require the same dependencies as the main application:
- PyQt5 (for UI components)
- cryptography (for RSA operations)
- bcrypt (for password hashing)
- Additional dependencies as specified in `requirements.txt`