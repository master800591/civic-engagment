# Civic Engagement Platform Documentation

## Overview
A modular, secure, and transparent desktop application for contract-based civic governance, debate, moderation, and blockchain audit trails. Built with Python and PyQt5.

## Architecture
- **Users Module**: Registration, authentication, elections, session, key management
- **Debates Module**: Topic creation, argument threading, voting, blockchain logging
- **Moderation Module**: Flagging, review workflows, audit logging, statistics
- **Blockchain Module**: Hierarchical PoA blockchain, validator registry, P2P networking
- **Utils Module**: Input validation framework
- **Tests**: Unit tests for all modules

## Data Flow
- **User Registration**: Validates input, hashes password, generates keys, records on blockchain
- **Debate Participation**: Role-based topic creation, argument submission, voting, blockchain record
- **Moderation**: Content flagging, multi-branch review, blockchain audit
- **Blockchain**: Page→Chapter→Book→Part→Series structure, validator signatures, audit trail

## Security
- bcrypt password hashing
- RSA-2048 key pairs
- Local private key storage
- Comprehensive input validation
- Blockchain integrity and audit

## Governance Model
- Contract-based roles: Citizens, Representatives, Senators, Elders, Founders
- Multi-layered checks and balances
- Bicameral legislature, Elder veto, citizen recall
- All actions recorded on blockchain

## Setup & Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```
3. Use the GUI tabs for Users, Debates, Moderation, Blockchain

## Environment Setup

To switch environments, set the config file path before running the app:

- Development:
  ```bash
  export CIVIC_CONFIG=config/dev_config.json
  pip install -r requirements-dev.txt
  python main.py
  ```
- Testing:
  ```bash
  export CIVIC_CONFIG=config/test_config.json
  pip install -r requirements-test.txt
  pytest tests/
  ```
- Production:
  ```bash
  export CIVIC_CONFIG=config/prod_config.json
  pip install -r requirements-prod.txt
  python main.py
  ```

Update your code to read the config file from the `CIVIC_CONFIG` environment variable for dynamic environment selection.

## Testing
- Run unit tests in `tests/` with pytest:
   ```bash
   pytest tests/
   ```

## Module Details
### users/backend.py
- User registration, authentication, session, elections
- Docstrings provided for all major methods

### debates/backend.py
- Debate topic creation, argument management, voting
- Blockchain logging for transparency

### moderation/backend.py
- Content flagging, review, resolution, statistics
- Audit logging and blockchain integration

### blockchain/blockchain.py
- Hierarchical blockchain structure
- Validator registry, block signing, P2P networking

### utils/validation.py
- Input validation for all user data
- Email, password, document checks

## Error Handling
- All modules use try/except for file and blockchain operations
- Validation errors return user-friendly messages
- Static analysis and type hints throughout

## Security & Privacy
- Passwords never stored in plaintext
- Private keys stored locally, never transmitted
- Blockchain provides immutable audit trail

## Extensibility
- Modular design for easy feature addition
- Future support for web/mobile clients, REST API, advanced analytics

## License
MIT License

---
For detailed docstrings and inline documentation, see each module file.
