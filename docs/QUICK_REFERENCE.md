# 🚀 Founder Package Automation - Quick Reference

## One-Line Commands

### Package Creation
```bash
# Full automation
cd civic_desktop/scripts && python automate_founder_package.py --auto

# Interactive
cd civic_desktop/scripts && python automate_founder_package.py

# Validate only
cd civic_desktop/scripts && python automate_founder_package.py --validate-only
```

### Monitoring
```bash
# Quick check
cd civic_desktop && python scripts/monitor_registrations.py

# Last 7 days
cd civic_desktop && python scripts/monitor_registrations.py --hours 168

# Export report
cd civic_desktop && python scripts/monitor_registrations.py --export reports/daily.txt

# Continuous monitoring
cd civic_desktop && nohup python scripts/monitor_registrations.py --continuous --interval 3600 &
```

### Security Validation
```bash
# Check security
cd /home/runner/work/civic-engagment/civic-engagment && python validate_security.py

# Verify package
cd civic_desktop && python scripts/automate_founder_package.py --validate-only
```

---

## Common Workflows

### 1. Initial Setup
```bash
cd civic_desktop/scripts
python automate_founder_package.py --auto
python automate_founder_package.py --validate-only
cd ../..
python validate_security.py
```

### 2. Daily Monitoring
```bash
cd civic_desktop
python scripts/monitor_registrations.py --hours 24 --export logs/daily_$(date +%Y%m%d).txt
```

### 3. Weekly Review
```bash
cd civic_desktop
python scripts/monitor_registrations.py --hours 168 --export reports/weekly_$(date +%Y%m%d).txt
```

### 4. Package Distribution
```bash
# 1. Validate package before distribution
cd civic_desktop/scripts
python automate_founder_package.py --validate-only

# 2. Copy to thumb drive (replace /media/thumbdrive with actual path)
cp -r ../FOUNDER_THUMB_DRIVE/* /media/thumbdrive/

# 3. Update tracking
nano ../FOUNDER_THUMB_DRIVE/DISTRIBUTION_SUMMARY.md

# 4. Monitor for registration
cd ..
python scripts/monitor_registrations.py --continuous --interval 3600 &
```

---

## File Locations

### Generated Files
```
civic_desktop/
├── FOUNDER_THUMB_DRIVE/              # Complete thumb drive package
├── founder_distributions/            # Source distribution files
│   ├── keys/                        # Private keys
│   ├── pdfs/                        # PDF documents
│   └── founder_keys_master.json     # Master registry
└── logs/
    ├── founder_package_automation.log   # Automation logs
    └── registration_monitor.log         # Monitoring logs
```

### Documentation
```
docs/
├── DEPLOYMENT_GUIDE.md              # Complete deployment guide
└── SECURITY_AUDIT_CHECKLIST.md     # Security audit checklist

civic_desktop/scripts/
└── README_AUTOMATION.md             # Automation documentation

SECURITY.md                          # Main security document
```

---

## Status Checks

### Quick Health Check
```bash
# Check all systems
cd civic_desktop
echo "=== Users ===" && ls -la users/users_db.json 2>&1 | head -1
echo "=== Blockchain ===" && ls -la blockchain/blockchain_db.json 2>&1 | head -1
echo "=== Packages ===" && ls -la FOUNDER_THUMB_DRIVE/ 2>&1 | head -1
python scripts/monitor_registrations.py --hours 1
```

### Detailed Status
```bash
cd civic_desktop
python scripts/automate_founder_package.py --validate-only
python scripts/monitor_registrations.py --hours 168
cd ..
python validate_security.py
```

---

## Troubleshooting

### Package Creation Issues
```bash
# Check dependencies
pip install -r requirements.txt

# Verify modules
python -c "from users.founder_keys import FounderKeyManager; print('OK')"
python -c "from users.pdf_generator import UserPDFGenerator; print('OK')"

# Check permissions
ls -la founder_distributions/
chmod -R 755 founder_distributions/
```

### Monitoring Issues
```bash
# Check database files
ls -la users/users_db.json blockchain/blockchain_db.json

# Run with verbose output
python scripts/monitor_registrations.py --hours 24 2>&1 | tee debug.log
```

### Validation Failures
```bash
# Check structure
ls -R FOUNDER_THUMB_DRIVE/ | head -50

# Regenerate if needed
python scripts/automate_founder_package.py --auto
```

---

## Automation Setup

### Cron Jobs
```bash
# Edit crontab
crontab -e

# Add these lines:
# Hourly monitoring
0 * * * * cd /path/to/civic_desktop && python scripts/monitor_registrations.py --hours 24 >> logs/cron_monitor.log 2>&1

# Daily report
0 8 * * * cd /path/to/civic_desktop && python scripts/monitor_registrations.py --hours 24 --export reports/daily_$(date +\%Y\%m\%d).txt

# Weekly summary
0 9 * * 1 cd /path/to/civic_desktop && python scripts/monitor_registrations.py --hours 168 --export reports/weekly_$(date +\%Y\%m\%d).txt
```

### Service Setup (systemd)
```bash
# Create service file
sudo nano /etc/systemd/system/civic-monitor.service

# Add content from DEPLOYMENT_GUIDE.md

# Enable and start
sudo systemctl enable civic-monitor
sudo systemctl start civic-monitor
sudo systemctl status civic-monitor
```

---

## Security Reminders

### ✅ ALWAYS
- Validate packages before distribution
- Verify recipient identity
- Use secure transfer methods
- Update distribution tracking
- Monitor for registration
- Run security audits
- Keep logs for audit trail

### ❌ NEVER
- Email or transmit packages electronically
- Share packages without verification
- Store thumb drive unsecured
- Skip validation steps
- Ignore security alerts
- Forget to update tracking

---

## Quick Commands Cheat Sheet

```bash
# Navigate to scripts
cd civic_desktop/scripts

# Create package
./automate_founder_package.py --auto

# Validate package
./automate_founder_package.py --validate-only

# Monitor (24h)
cd .. && ./scripts/monitor_registrations.py

# Monitor (7d)
./scripts/monitor_registrations.py --hours 168

# Export report
./scripts/monitor_registrations.py --export report.txt

# Continuous monitoring
nohup ./scripts/monitor_registrations.py --continuous --interval 3600 > logs/monitor.log 2>&1 &

# Check security
cd .. && python validate_security.py

# View logs
tail -f civic_desktop/logs/registration_monitor.log
tail -f civic_desktop/founder_package_automation.log
```

---

## Help Commands

```bash
# Get help for automation
python automate_founder_package.py --help

# Get help for monitoring
python monitor_registrations.py --help

# Check version
python --version

# List dependencies
pip freeze | grep -E "(PyQt5|cryptography|bcrypt)"
```

---

## Support Resources

- **Full Documentation**: `docs/DEPLOYMENT_GUIDE.md`
- **Automation Guide**: `civic_desktop/scripts/README_AUTOMATION.md`
- **Security Audit**: `docs/SECURITY_AUDIT_CHECKLIST.md`
- **Main README**: `README.md`

**Contact**:
- Security: security@civic-platform.org
- Support: tech@civic-platform.org
- Issues: https://github.com/master800591/civic-engagment/issues

---

**Quick Reference Version**: 1.0  
**Last Updated**: 2024-12-19
