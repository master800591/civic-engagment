# Civic Engagement Platform

**Repository**: https://github.com/Civic-Engagement/civic-engagment

## 📋 Latest Updates
For detailed information about recent changes, security improvements, and bug fixes, see our [**CHANGELOG.md**](CHANGELOG.md).

**Current Version**: 1.6.0 (Production Ready)  
**Latest Update**: Complete GitHub integration with update checking and version control  
**Status**: ✅ Government-grade security implemented with automated updates

---

## Business-Focused Features for Adoption

- **Verified Business Profiles**: Custom business accounts with verification and branding for organizations, companies, and civic groups.
- **Networking Tools**: Digital business cards, QR/NFC sharing, and contact management to facilitate professional connections.
- **Civic Sponsorships**: Businesses can sponsor debates, events, or community initiatives to increase visibility and support civic engagement.
- **Analytics & Insights**: Dashboards showing engagement, reach, and impact for business activities and sponsored events.
- **Integration APIs**: Connect with CRM, HR, and other business systems for seamless data exchange and workflow automation.
- **Compliance & Audit Tools**: Exportable reports for legal and regulatory needs, supporting business compliance requirements.
- **Marketplace**: Businesses can offer services, products, or job postings to the civic community, fostering economic and social collaboration.
## User-Focused Features for Adoption

- **Privacy Controls**: Granular settings for what information is public, private, or shared. Users can control visibility of their profile, participation, and contact details.
- **Rewards & Recognition**: Earn badges, reputation scores, and incentives for civic engagement, debate participation, and community contributions.
- **Secure Messaging**: Encrypted direct messaging between users for safe, private communication.
- **Event & Group Tools**: Create, join, and manage civic events or interest groups. Organize meetups, discussions, and collaborative projects within the platform.
## User ID Cards

The platform will support two types of user ID cards:

- **Public ID Card**: Can be shown or given out like a business card. Contains:
  - NFC and QR code for quick sharing and verification
  - User photo
  - Name
  - Address
  - Public key or profile link
  - Designed for networking, civic events, and public identification

- **Private ID Card**: Used for secure account recovery and identity verification. Contains:
  - Private recovery QR code or NFC tag
  - User photo
  - Name
  - Address
  - Private recovery credentials (never shared)
  - Intended for personal use only; not to be given out

These cards enhance security, privacy, and convenience for users, supporting both public engagement and private account management.
# Civic Engagement Platform

## Mission Statement
Empower communities to participate in transparent, secure, and democratic governance through a decentralized, contract-based digital platform. Our goal is to prevent tyranny, protect minority rights, and ensure every citizen has a voice in decision-making.

## Why This Project Exists
Modern governance systems often suffer from lack of transparency, concentration of power, and limited citizen participation. This platform leverages blockchain, cryptography, and contract-based roles to:
- Prevent majority or minority tyranny
- Guarantee constitutional rights and due process
- Provide immutable audit trails for all actions
- Enable direct, secure, and fair participation for all users

## Who Is This For?
- **Citizens**: Anyone seeking a voice in local, state, or national governance
- **Representatives/Senators/Elders/Founders**: Elected or appointed officials with defined powers and checks
- **Moderators**: Community members responsible for content review and platform integrity
- **Developers**: Contributors building civic technology for transparency and democracy
- **Organizations**: Civic groups, educational institutions, pilot programs

## What Does It Do?
- **User Registration & Authentication**: Secure onboarding with identity verification, password hashing, and RSA key generation
- **Contract-Based Governance**: Multi-branch system (Citizens, Representatives, Senators, Elders, Founders) with checks and balances
- **Debate Platform**: Topic creation, argument threading, voting, and blockchain logging
- **Moderation System**: Flagging, review, warnings, and constitutional appeals
- **Blockchain Integration**: Hierarchical PoA blockchain for audit trails, validator registry, and P2P networking
- **Environment Separation**: Dev, test, and prod configs for safe development and deployment
- **UI**: PyQt5 desktop application with tabbed navigation for all modules

## Technical Architecture
- **Languages**: Python 3.x
- **Frameworks**: PyQt5 (GUI), custom blockchain, bcrypt, cryptography
- **Modules**: users, debates, moderation, blockchain, contracts, utils, tests
- **Data Storage**: JSON files per environment, blockchain for audit
- **Config**: ENV_CONFIG loaded from `main.py`, with paths set in `config/dev_config.json`, `config/test_config.json`, `config/prod_config.json`
- **Security**: bcrypt password hashing, RSA-2048 keys, input validation, local private key storage

## How It Works
1. **Startup**: Loads environment config, initializes UI and blockchain timer
2. **Registration/Login**: Validates user, generates keys, saves to database, records on blockchain
3. **Governance**: Assigns roles, enables elections, enforces contract-based permissions
4. **Debates**: Allows topic creation, argument submission, voting, and blockchain logging
5. **Moderation**: Enables flagging, review, warnings, and appeals with full audit trail
6. **Blockchain**: Records all actions, supports validator registry, and P2P foundation

## Development & Deployment
- **Setup**:
  ```bash
  cd civic_engagement_platform/civic_desktop
  pip install -r requirements.txt
  python main.py
  ```
- **Environment Switching**: Change config path in `main.py` or use `reload_config()` in `main_window.py`
- **Testing**: Use separate test databases and requirements files
- **Extensibility**: Modular design for easy feature addition

## Governance Model
- **Contract Founders**: Genesis authority, emergency powers, constitutional amendments
- **Contract Elders**: Veto power, judicial review, appointment authority
- **Contract Representatives**: Legislative initiative, budget, impeachment
- **Contract Senators**: Legislative review, confirmation, override powers
- **Contract Citizens**: Electoral authority, initiative, recall, participation
- **Checks & Balances**: Multi-layered system to prevent concentration of power

## Security & Privacy
- **Password Security**: bcrypt with salt
- **Cryptography**: RSA-2048 keys
- **Session Management**: Secure, automatic logout
- **Input Validation**: Comprehensive checks
- **Audit Logging**: Immutable blockchain records

## File Structure
```
civic_desktop/
├── main.py
├── main_window.py
├── requirements.txt
├── users/
├── debates/
├── moderation/
├── blockchain/
├── contracts/
├── utils/
├── tests/
├── config/
```

## How To Contribute
- Fork the repository
- Follow environment setup instructions
- Write clear, documented code
- Ensure all changes are environment-aware
- Submit pull requests with detailed descriptions

## Missing Features & Roadmap
- Robust P2P networking and node discovery
- REST API for web/mobile integration
- Comprehensive test suite
- Advanced analytics and dashboards
- Internationalization and accessibility improvements


## Features Needed for Government Adoption

To make this platform attractive for government use, the following features and assurances should be added:

- **Official Identity Verification**: Integrate with government ID databases or third-party verification services. Support for digital signatures and eID.
- **Compliance & Legal Framework**: Meet local, state, and national data protection laws (GDPR, CCPA, etc.). Add audit logs and exportable compliance reports. Support for FOIA/public records requests.
- **Scalability & Performance**: Support large-scale deployments (millions of users), cloud and on-premise options, load balancing, and high-availability.
- **Interoperability & Integration**: RESTful API for integration with government systems, SSO with official authentication providers, data import/export tools for legacy systems.
- **Accessibility & Inclusivity**: Full WCAG 2.1 accessibility compliance, multi-language support, mobile and offline access.
- **Advanced Security**: End-to-end encryption, granular role-based access controls, security certifications (SOC 2, ISO 27001).
- **Customizable Governance Models**: Configurable for different government structures, custom workflows for elections, referendums, and legislative processes.
- **Robust Analytics & Reporting**: Dashboards for participation, voting, and engagement metrics; real-time monitoring and alerts.
- **Training & Support**: Comprehensive documentation and training modules for officials and citizens, dedicated support channels and SLAs.
- **Public Trust & Transparency**: Open-source codebase, transparent blockchain audit trails, citizen privacy guarantees.

Adding these features will help ensure the platform meets the needs of governments for security, compliance, scalability, integration, accessibility, and public trust.

---
For full technical details, see the codebase and module docstrings. Every action is recorded on the blockchain for transparency and auditability.