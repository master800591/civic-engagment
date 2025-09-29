# Civic Engagement Platform

## Overview
A production-ready desktop application (v1.6.0) providing a comprehensive civic engagement platform with PyQt5-based multi-tab interface, environment-aware configuration, and blockchain audit trails.

## Quick Start
```bash
cd civic_desktop
pip install -r requirements.txt
python main.py
```

## Architecture
- **Implementation Status**: Production-ready desktop application with expanded feature set
- **Framework**: PyQt5-based multi-tab interface with 18 modules
- **Configuration**: Environment-aware system using `ENV_CONFIG`
- **Security**: Enterprise-grade bcrypt + RSA-2048, comprehensive validation
- **Blockchain**: Custom hierarchical PoA with P2P networking

## Module Structure
- `users/` - Identity & Authentication System
- `debates/` - Democratic Discussion Platform  
- `moderation/` - Constitutional Content Review
- `contracts/` - Constitutional Governance Framework
- `training/` - Civic Education System
- `crypto/` - CivicCoin DeFi Ecosystem & Rewards
- `blockchain/` - Immutable Audit & Consensus System
- `github_integration/` - Version Control & Updates
- `maps/` - Geographic Civic Engagement
- `system_guide/` - User Onboarding & Help
- `analytics/` - Data-Driven Governance Insights
- `events/` - Civic Event Management
- `communications/` - Secure Civic Messaging
- `surveys/` - Democratic Opinion Gathering
- `petitions/` - Citizen-Driven Legislative Process
- `documents/` - Official Document Management
- `transparency/` - Enhanced Accountability
- `collaboration/` - Inter-Jurisdictional Cooperation

## Environment Configuration
Switch between development, test, and production environments:
```bash
set CIVIC_CONFIG=config/test_config.json
python main.py
```

## Testing
```bash
pytest tests/
```

## Governance Model
Contract-based democracy with blockchain transparency and multi-layered protections against tyranny through:
- Multi-branch elections (Representatives, Senators, Elders)
- Constitutional safeguards and Elder oversight
- Citizen appeal rights and due process
- Blockchain audit trails for all governance actions