# 🚀 Civic Engagement Platform - Deployment Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Founder Package Creation](#founder-package-creation)
5. [Platform Configuration](#platform-configuration)
6. [Security Setup](#security-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive instructions for deploying the Civic Engagement Platform, including founder package creation, platform setup, security configuration, and ongoing maintenance.

### Deployment Types

- **Development**: Local testing and development
- **Staging**: Pre-production testing environment
- **Production**: Live platform deployment

---

## Prerequisites

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Stable internet connection for P2P networking

#### Software Dependencies
```bash
# Core dependencies
python3 --version  # Should be 3.10+
pip3 --version
git --version

# Optional but recommended
virtualenv --version
```

### Access Requirements
- Administrative access to deployment server
- GitHub repository access (for updates)
- Email server configuration (for notifications)
- Database backup storage location

---

## Installation Steps

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/master800591/civic-engagment.git
cd civic-engagment/civic_desktop

# Verify structure
ls -la
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import PyQt5; print('PyQt5 installed successfully')"
```

### 3. Configure Environment

```bash
# Copy example configuration
cp config/dev_config.json.example config/dev_config.json

# Edit configuration
nano config/dev_config.json
```

**Key Configuration Settings:**
```json
{
  "environment": "production",
  "db_path": "data/users_db.json",
  "blockchain_path": "data/blockchain_db.json",
  "p2p_enabled": true,
  "p2p_port": 8765,
  "security_level": "maximum"
}
```

### 4. Initialize Database

```bash
# Run database initialization
python scripts/initialize_database.py

# Verify database creation
ls -la data/
```

### 5. Test Installation

```bash
# Run basic tests
cd tests
pytest test_users.py
pytest test_blockchain.py

# Run platform in test mode
cd ..
python main.py --test-mode
```

---

## Founder Package Creation

### Automated Package Generation

The platform includes an automated script for creating founder packages:

```bash
# Navigate to scripts directory
cd civic_desktop/scripts

# Run automated package creation
python automate_founder_package.py --auto

# Or run interactively
python automate_founder_package.py
```

### Manual Package Generation (Advanced)

If you need manual control over the process:

#### Step 1: Generate Founder Keys
```bash
python setup_founder_keys.py
# Follow prompts to generate 7 founder keys
```

#### Step 2: Create Distribution Package
```bash
python generate_founder_distribution.py
# Select option to generate 10 founder key sets
```

#### Step 3: Create Thumb Drive Package
```bash
python create_thumb_drive_package.py
# Creates organized FOUNDER_THUMB_DRIVE directory
```

### Package Validation

```bash
# Validate package completeness
python automate_founder_package.py --validate-only

# Check security protection
cd ../..
python validate_security.py
```

### Package Structure

After creation, you should have:

```
FOUNDER_THUMB_DRIVE/
├── INDIVIDUAL_FOUNDER_PACKAGES/
│   ├── FOUNDER_01/
│   │   ├── FOUNDER_01_PRIVATE_KEY.pem
│   │   ├── FOUNDER_01_INFO.json
│   │   ├── FOUNDER_01_PUBLIC_CERTIFICATE.pdf
│   │   ├── FOUNDER_01_PRIVATE_RECOVERY.pdf
│   │   └── README.md
│   └── ... (FOUNDER_02 through FOUNDER_10)
├── README.md
├── SECURITY_INSTRUCTIONS.md
├── DISTRIBUTION_SUMMARY.md
└── founder_keys_master.json
```

---

## Platform Configuration

### 1. Security Configuration

#### Generate Platform Keys
```bash
cd civic_desktop
python -c "from users.keys import KeyManager; km = KeyManager(); km.generate_platform_keys()"
```

#### Configure Blockchain
```bash
# Initialize blockchain with genesis block
python -c "from blockchain.blockchain import Blockchain; bc = Blockchain(); bc.initialize_genesis_block()"
```

#### Set Up Validators
```bash
# Configure initial validators (typically founders)
python scripts/setup_validators.py
```

### 2. Network Configuration

#### P2P Network Setup
```python
# config/production_config.json
{
  "p2p_settings": {
    "enabled": true,
    "port": 8765,
    "bootstrap_nodes": [
      "node1.civic-platform.org:8765",
      "node2.civic-platform.org:8765"
    ],
    "max_peers": 50
  }
}
```

### 3. Email Configuration

```python
# config/email_config.json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "use_tls": true,
  "sender_email": "noreply@civic-platform.org",
  "sender_name": "Civic Engagement Platform"
}
```

### 4. Storage Configuration

```bash
# Create necessary directories
mkdir -p data/backups
mkdir -p data/logs
mkdir -p data/uploads

# Set permissions
chmod 700 data/private_keys
chmod 755 data/backups
```

---

## Security Setup

### 1. File System Security

#### Protect Sensitive Files
```bash
# Set restrictive permissions on sensitive directories
chmod 700 civic_desktop/users/private_keys
chmod 700 civic_desktop/users/founder_keys
chmod 600 config/*_secrets.json

# Verify security
python validate_security.py
```

#### Configure Backups
```bash
# Create backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/secure/backups/civic-platform"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup databases
cp -r data/ "$BACKUP_DIR/data_$TIMESTAMP/"

# Backup configuration
cp -r config/ "$BACKUP_DIR/config_$TIMESTAMP/"

# Keep only last 7 days
find "$BACKUP_DIR" -mtime +7 -delete
EOF

chmod +x scripts/backup.sh

# Set up cron job
crontab -e
# Add: 0 2 * * * /path/to/civic_desktop/scripts/backup.sh
```

### 2. Network Security

#### Firewall Configuration
```bash
# Allow P2P port (8765)
sudo ufw allow 8765/tcp

# Allow web interface if using
sudo ufw allow 8080/tcp

# Enable firewall
sudo ufw enable
```

#### SSL/TLS Setup (if web interface)
```bash
# Generate SSL certificate
sudo certbot certonly --standalone -d civic-platform.org

# Configure in application
# config/ssl_config.json
{
  "ssl_enabled": true,
  "cert_file": "/etc/letsencrypt/live/civic-platform.org/fullchain.pem",
  "key_file": "/etc/letsencrypt/live/civic-platform.org/privkey.pem"
}
```

### 3. Access Control

#### Create Admin Accounts
```bash
# Use secure founder key to create admin
python scripts/create_admin.py --founder-key FOUNDER_01_PRIVATE_KEY.pem
```

#### Configure Role-Based Access
```python
# In users/contract_roles.py
ROLE_PERMISSIONS = {
    'contract_founder': ['all'],
    'contract_elder': ['constitutional_review', 'veto_power'],
    'contract_senator': ['legislation_review', 'confirmation'],
    'contract_representative': ['legislation_initiation', 'budget_authority'],
    'contract_member': ['vote', 'debate', 'petition']
}
```

---

## Monitoring and Maintenance

### 1. Platform Monitoring

#### Registration Monitoring Script
```bash
# Create monitoring script
cd civic_desktop/scripts
```

Create `monitor_registrations.py`:
```python
#!/usr/bin/env python3
"""Monitor platform registration and onboarding"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from users.backend import UserBackend

def monitor_registrations():
    """Monitor recent registrations"""
    backend = UserBackend()
    
    # Get users registered in last 24 hours
    now = datetime.now()
    recent_threshold = now - timedelta(hours=24)
    
    users_data = backend._load_users_db()
    recent_users = [
        u for u in users_data['users']
        if datetime.fromisoformat(u['created_at']) > recent_threshold
    ]
    
    print(f"📊 REGISTRATION MONITORING REPORT")
    print(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 60)
    print(f"Recent Registrations (24h): {len(recent_users)}")
    
    if recent_users:
        print(f"\nRecent Users:")
        for user in recent_users:
            print(f"- {user['first_name']} {user['last_name']} ({user['email']})")
            print(f"  Role: {user['role']}")
            print(f"  Registered: {user['created_at']}")
    
    # Check founder key usage
    print(f"\n🔑 Founder Key Usage:")
    founder_users = [u for u in users_data['users'] if u['role'] == 'contract_founder']
    print(f"Total Founders: {len(founder_users)}")
    
    # Onboarding completion tracking
    print(f"\n✅ Onboarding Status:")
    incomplete = [u for u in recent_users if not u.get('onboarding_complete', False)]
    print(f"Incomplete Onboarding: {len(incomplete)}")

if __name__ == "__main__":
    monitor_registrations()
```

```bash
chmod +x monitor_registrations.py

# Set up monitoring cron job
crontab -e
# Add: 0 * * * * cd /path/to/civic_desktop/scripts && python monitor_registrations.py >> ../logs/registration_monitor.log
```

#### System Health Monitoring
```bash
# Create health check script
cat > scripts/health_check.sh << 'EOF'
#!/bin/bash
echo "🏥 PLATFORM HEALTH CHECK - $(date)"
echo "======================================"

# Check Python process
if pgrep -f "main.py" > /dev/null; then
    echo "✅ Platform process running"
else
    echo "❌ Platform process not running"
fi

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%"
else
    echo "⚠️ Disk usage high: ${DISK_USAGE}%"
fi

# Check database files
if [ -f "data/users_db.json" ]; then
    USER_COUNT=$(python -c "import json; data=json.load(open('data/users_db.json')); print(len(data['users']))")
    echo "✅ Users database: $USER_COUNT users"
else
    echo "❌ Users database missing"
fi

# Check blockchain
if [ -f "data/blockchain_db.json" ]; then
    echo "✅ Blockchain database present"
else
    echo "❌ Blockchain database missing"
fi

# Check logs for errors
ERROR_COUNT=$(tail -100 logs/platform.log 2>/dev/null | grep -c ERROR || echo "0")
echo "📋 Recent errors: $ERROR_COUNT"

echo "======================================"
EOF

chmod +x scripts/health_check.sh

# Run every 15 minutes
crontab -e
# Add: */15 * * * * /path/to/civic_desktop/scripts/health_check.sh >> logs/health_check.log
```

### 2. Log Management

```bash
# Create log rotation configuration
cat > /etc/logrotate.d/civic-platform << 'EOF'
/path/to/civic_desktop/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 civic civic
    sharedscripts
}
EOF
```

### 3. Database Maintenance

```bash
# Create maintenance script
cat > scripts/database_maintenance.py << 'EOF'
#!/usr/bin/env python3
"""Database maintenance and optimization"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

def compact_blockchain():
    """Compact blockchain by creating chapters from old pages"""
    from blockchain.blockchain import Blockchain
    bc = Blockchain()
    bc.create_chapters_from_old_pages()
    print("✅ Blockchain compacted")

def cleanup_old_sessions():
    """Remove expired sessions"""
    from users.session import SessionManager
    SessionManager.cleanup_expired_sessions()
    print("✅ Old sessions cleaned up")

def backup_databases():
    """Create database backups"""
    backup_dir = Path('data/backups') / datetime.now().strftime('%Y%m%d')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    import shutil
    for db_file in Path('data').glob('*_db.json'):
        shutil.copy2(db_file, backup_dir / db_file.name)
    
    print(f"✅ Databases backed up to {backup_dir}")

if __name__ == "__main__":
    print("🔧 DATABASE MAINTENANCE")
    print("=" * 60)
    compact_blockchain()
    cleanup_old_sessions()
    backup_databases()
    print("=" * 60)
    print("✅ Maintenance complete")
EOF

chmod +x scripts/database_maintenance.py

# Run weekly maintenance
crontab -e
# Add: 0 3 * * 0 cd /path/to/civic_desktop && python scripts/database_maintenance.py
```

### 4. Update Management

```bash
# Check for updates
cd civic_desktop
python -c "from github_integration.update_notifier import UpdateNotifier; un = UpdateNotifier(); un.check_for_updates()"

# Apply updates (with backup)
scripts/backup.sh
git pull origin main
pip install -r requirements.txt
python scripts/run_migrations.py
```

---

## Troubleshooting

### Common Issues

#### 1. Installation Issues

**Problem**: Missing dependencies
```bash
# Solution: Install all required packages
pip install --upgrade -r requirements.txt

# For system-level dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-cryptography
```

**Problem**: Permission denied errors
```bash
# Solution: Fix directory permissions
chmod 755 civic_desktop
chmod 700 civic_desktop/users/private_keys
sudo chown -R $USER:$USER civic_desktop
```

#### 2. Database Issues

**Problem**: Corrupted database
```bash
# Solution: Restore from backup
cp data/backups/latest/users_db.json data/users_db.json

# Or reinitialize
python scripts/initialize_database.py
```

**Problem**: Database lock
```bash
# Solution: Check for running processes
ps aux | grep main.py
# Kill if necessary
kill -9 <PID>
```

#### 3. Blockchain Issues

**Problem**: Blockchain synchronization failure
```bash
# Solution: Clear and resync
mv data/blockchain_db.json data/blockchain_db.json.backup
python -c "from blockchain.blockchain import Blockchain; Blockchain().initialize_genesis_block()"
```

**Problem**: Validator signature verification failure
```bash
# Solution: Check validator keys
python scripts/verify_validators.py

# Regenerate if needed
python scripts/setup_validators.py --regenerate
```

#### 4. Network Issues

**Problem**: P2P connection failure
```bash
# Check port availability
netstat -an | grep 8765

# Test connectivity
telnet node1.civic-platform.org 8765

# Check firewall
sudo ufw status
```

**Problem**: High latency
```bash
# Check P2P peer count
python -c "from blockchain.p2p import P2PNetwork; p2p = P2PNetwork(); print(p2p.get_peer_count())"

# Optimize peer connections
# Edit config/production_config.json
# Set "max_peers": 20 (lower number)
```

#### 5. Security Issues

**Problem**: Unauthorized access attempts
```bash
# Check access logs
grep "FAILED LOGIN" logs/platform.log

# Review user accounts
python scripts/audit_users.py

# Revoke suspicious accounts
python -c "from users.backend import UserBackend; UserBackend().revoke_user('suspicious@email.com')"
```

**Problem**: Founder key compromise
```bash
# Immediate actions:
# 1. Revoke compromised key
python scripts/revoke_founder_key.py --key-id FOUNDER_XX

# 2. Notify security team
# 3. Generate incident report
python scripts/security_incident_report.py --type key_compromise

# 4. Review blockchain for unauthorized actions
python scripts/audit_blockchain.py --since "2024-01-01"
```

### Getting Help

#### Support Channels
- **Documentation**: Check README.md and module-specific docs
- **Email**: tech@civic-platform.org
- **Security Issues**: security@civic-platform.org (confidential)
- **GitHub Issues**: https://github.com/master800591/civic-engagment/issues

#### Diagnostic Information

When reporting issues, include:
```bash
# System information
python --version
pip freeze > requirements_current.txt

# Platform status
python scripts/health_check.sh > diagnostic_report.txt

# Recent logs
tail -100 logs/platform.log >> diagnostic_report.txt
tail -100 logs/error.log >> diagnostic_report.txt

# Configuration (redact sensitive info)
cat config/production_config.json | grep -v password | grep -v secret >> diagnostic_report.txt
```

---

## Best Practices

### Security
- ✅ Regular security audits (monthly)
- ✅ Timely updates and patches
- ✅ Secure backup storage (offsite)
- ✅ Access control reviews (quarterly)
- ✅ Incident response plan testing

### Performance
- ✅ Monitor resource usage
- ✅ Optimize database queries
- ✅ Regular blockchain compaction
- ✅ Cache configuration
- ✅ Load testing before major events

### Maintenance
- ✅ Automated backups (daily)
- ✅ Log rotation and archiving
- ✅ Database optimization (weekly)
- ✅ Update management (tested staging first)
- ✅ Documentation updates

### Monitoring
- ✅ Registration tracking
- ✅ System health checks (hourly)
- ✅ Error rate monitoring
- ✅ Performance metrics
- ✅ Security event logging

---

## Appendix

### A. Environment Variables

```bash
# .env file example
CIVIC_ENVIRONMENT=production
CIVIC_DB_PATH=/var/civic/data
CIVIC_LOG_LEVEL=INFO
CIVIC_P2P_PORT=8765
CIVIC_BACKUP_DIR=/secure/backups/civic
```

### B. Configuration Files

All configuration files should be in `config/` directory:
- `production_config.json` - Production settings
- `staging_config.json` - Staging environment
- `dev_config.json` - Development settings
- `email_config.json` - Email server settings
- `ssl_config.json` - SSL/TLS configuration

### C. Service Management

#### Systemd Service (Linux)
```ini
# /etc/systemd/system/civic-platform.service
[Unit]
Description=Civic Engagement Platform
After=network.target

[Service]
Type=simple
User=civic
WorkingDirectory=/opt/civic_desktop
ExecStart=/opt/civic_desktop/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable civic-platform
sudo systemctl start civic-platform
sudo systemctl status civic-platform
```

### D. Migration Guide

When updating between major versions:

1. **Backup Everything**
   ```bash
   scripts/backup.sh
   ```

2. **Review Change Log**
   ```bash
   git log --oneline v1.0.0..v2.0.0
   ```

3. **Test in Staging**
   ```bash
   # Deploy to staging first
   # Run full test suite
   pytest
   ```

4. **Run Migration Scripts**
   ```bash
   python scripts/migrate_v1_to_v2.py
   ```

5. **Verify Data Integrity**
   ```bash
   python scripts/verify_database_integrity.py
   ```

---

## Conclusion

This deployment guide provides comprehensive instructions for setting up and maintaining the Civic Engagement Platform. For additional support or questions, please contact the development team or refer to the project documentation.

**Last Updated**: 2024-12-19  
**Version**: 1.0  
**Maintained By**: Civic Engagement Platform Development Team
