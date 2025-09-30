#!/usr/bin/env python3
"""
AUTOMATED FOUNDER PACKAGE CREATION AND DISTRIBUTION SYSTEM
Complete automation for thumb drive package generation with validation and monitoring
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('founder_package_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FounderPackageAutomation:
    """Automated founder package creation with validation and monitoring"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path('founder_distributions')
        self.thumb_drive_dir = Path('FOUNDER_THUMB_DRIVE')
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def validate_prerequisites(self) -> Tuple[bool, str]:
        """Validate that all prerequisites are met"""
        logger.info("Validating prerequisites...")
        
        try:
            # Check for required modules
            from users.founder_keys import FounderKeyManager
            from users.pdf_generator import UserPDFGenerator
            logger.info("✅ Required modules available")
            
            # Check for write permissions
            if not os.access('.', os.W_OK):
                return False, "No write permission in current directory"
            
            logger.info("✅ Prerequisites validated")
            return True, "All prerequisites met"
            
        except ImportError as e:
            return False, f"Missing required module: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def generate_founder_keys(self, count: int = 10) -> Tuple[bool, str, Optional[Path]]:
        """Generate founder keys with PDFs"""
        logger.info(f"Generating {count} founder key sets...")
        
        try:
            from users.founder_keys import FounderKeyManager
            from users.pdf_generator import UserPDFGenerator
            
            founder_manager = FounderKeyManager()
            pdf_generator = UserPDFGenerator()
            
            # Create output directories
            self.output_dir.mkdir(exist_ok=True)
            keys_dir = self.output_dir / 'keys'
            pdfs_dir = self.output_dir / 'pdfs'
            keys_dir.mkdir(exist_ok=True)
            pdfs_dir.mkdir(exist_ok=True)
            
            founder_keys_data = []
            hardcoded_keys = []
            
            for i in range(1, count + 1):
                founder_id = f"FOUNDER_{i:02d}"
                logger.info(f"Generating {founder_id}...")
                
                # Generate individual founder key
                success, message, key_data = founder_manager.generate_individual_founder_key(founder_id)
                
                if not success:
                    logger.error(f"Failed to generate {founder_id}: {message}")
                    continue
                
                # Create founder user data for PDF generation
                founder_user_data = {
                    'user_id': founder_id,
                    'first_name': 'Platform',
                    'last_name': f'Founder {i:02d}',
                    'email': f'founder.{i:02d}@civic-platform.org',
                    'role': 'contract_founder',
                    'city': 'Genesis City',
                    'state': 'Constitutional State',
                    'country': 'Civic Republic',
                    'verification_status': 'founder_verified',
                    'created_at': datetime.now().isoformat(),
                    'terms_accepted': True,
                    'founder_authority': True,
                    'constitutional_power': True
                }
                
                # Generate PDFs
                pdf_success, pdf_message, pdf_paths = pdf_generator.generate_founder_pdfs(
                    founder_user_data, key_data
                )
                
                if pdf_success:
                    # Move PDFs to distribution directory
                    for pdf_type, pdf_path in pdf_paths.items():
                        if pdf_path and Path(pdf_path).exists():
                            new_path = pdfs_dir / f"{founder_id}_{pdf_type}.pdf"
                            Path(pdf_path).rename(new_path)
                            pdf_paths[pdf_type] = str(new_path)
                
                # Save individual key file
                key_file = keys_dir / f"{founder_id}_private_key.pem"
                with open(key_file, 'w') as f:
                    f.write(key_data['private_key_pem'])
                
                # Save info file
                info_file = keys_dir / f"{founder_id}_info.json"
                with open(info_file, 'w') as f:
                    json.dump({
                        'founder_id': founder_id,
                        'key_fingerprint': key_data['key_fingerprint'],
                        'blockchain_address': key_data['blockchain_address'],
                        'created_at': key_data['created_at'],
                        'pdf_paths': pdf_paths
                    }, f, indent=2)
                
                founder_keys_data.append({
                    'founder_id': founder_id,
                    'key_fingerprint': key_data['key_fingerprint'],
                    'status': 'available'
                })
                
                # Create hardcoded key entry
                hardcoded_keys.append({
                    'founder_id': founder_id,
                    'key_hash': key_data.get('key_hash', ''),
                    'key_fingerprint': key_data['key_fingerprint']
                })
                
                logger.info(f"✅ {founder_id} complete")
            
            # Save master keys file
            master_file = self.output_dir / 'founder_keys_master.json'
            with open(master_file, 'w') as f:
                json.dump({
                    'created_at': datetime.now().isoformat(),
                    'total_keys': len(founder_keys_data),
                    'founder_keys': founder_keys_data,
                    'hardcoded_keys': hardcoded_keys,
                    'usage_instructions': 'Each key can only be used once to promote someone to founder status'
                }, f, indent=2)
            
            logger.info(f"✅ Generated {len(founder_keys_data)} founder key sets")
            return True, "Founder keys generated successfully", self.output_dir
            
        except Exception as e:
            logger.error(f"Error generating founder keys: {str(e)}")
            return False, str(e), None
    
    def create_thumb_drive_package(self) -> Tuple[bool, str]:
        """Create organized thumb drive package"""
        logger.info("Creating thumb drive package...")
        
        try:
            import shutil
            
            # Ensure directories exist
            self.thumb_drive_dir.mkdir(exist_ok=True)
            individual_packages_dir = self.thumb_drive_dir / "INDIVIDUAL_FOUNDER_PACKAGES"
            individual_packages_dir.mkdir(exist_ok=True)
            
            # Copy main documentation
            if (self.output_dir / "README.md").exists():
                shutil.copy2(
                    self.output_dir / "README.md",
                    self.thumb_drive_dir / "FOUNDER_DISTRIBUTION_README.md"
                )
            
            # Copy master keys file
            if (self.output_dir / "founder_keys_master.json").exists():
                shutil.copy2(
                    self.output_dir / "founder_keys_master.json",
                    self.thumb_drive_dir / "founder_keys_master.json"
                )
            
            # Create individual founder packages
            keys_dir = self.output_dir / "keys"
            pdfs_dir = self.output_dir / "pdfs"
            
            for i in range(1, 11):
                founder_id = f"FOUNDER_{i:02d}"
                
                # Create individual founder directory
                founder_package_dir = individual_packages_dir / founder_id
                founder_package_dir.mkdir(exist_ok=True)
                
                # Copy files
                files_to_copy = [
                    (keys_dir / f"{founder_id}_private_key.pem", f"{founder_id}_PRIVATE_KEY.pem"),
                    (keys_dir / f"{founder_id}_info.json", f"{founder_id}_INFO.json"),
                    (pdfs_dir / f"{founder_id}_public_pdf.pdf", f"{founder_id}_PUBLIC_CERTIFICATE.pdf"),
                    (pdfs_dir / f"{founder_id}_private_pdf.pdf", f"{founder_id}_PRIVATE_RECOVERY.pdf"),
                    (pdfs_dir / f"{founder_id}_public_qr.pdf", f"{founder_id}_PUBLIC_QR_CODE.pdf"),
                    (pdfs_dir / f"{founder_id}_private_qr.pdf", f"{founder_id}_PRIVATE_QR_CODE.pdf"),
                ]
                
                for src, dst in files_to_copy:
                    if src.exists():
                        shutil.copy2(src, founder_package_dir / dst)
                
                # Create individual README
                self._create_individual_readme(founder_package_dir, founder_id)
                
                logger.info(f"✅ {founder_id} package complete")
            
            # Create master README
            self._create_thumb_drive_readme()
            
            # Create security instructions
            self._create_security_instructions()
            
            # Create distribution summary
            self._create_distribution_summary()
            
            logger.info("✅ Thumb drive package complete")
            return True, "Thumb drive package created successfully"
            
        except Exception as e:
            logger.error(f"Error creating thumb drive package: {str(e)}")
            return False, str(e)
    
    def _create_individual_readme(self, package_dir: Path, founder_id: str):
        """Create README for individual founder package"""
        readme_content = f"""# 🏛️ CIVIC ENGAGEMENT PLATFORM - {founder_id} PACKAGE

## 📋 PACKAGE CONTENTS

This package contains everything needed for **{founder_id}** registration:

- **{founder_id}_PRIVATE_KEY.pem** - Private founder key (CONFIDENTIAL)
- **{founder_id}_PUBLIC_CERTIFICATE.pdf** - Public founder certificate (shareable)
- **{founder_id}_PRIVATE_RECOVERY.pdf** - Private recovery document (CONFIDENTIAL)
- **{founder_id}_INFO.json** - Founder metadata and blockchain address

## 🚀 REGISTRATION INSTRUCTIONS

### Step 1: Access Platform
1. Download Civic Engagement Platform
2. Launch application
3. Click "Register New Account"

### Step 2: Complete Registration
1. Enter personal information
2. When prompted for "Founder Key", upload **{founder_id}_PRIVATE_KEY.pem**
3. Complete remaining registration steps

### Step 3: Verification
- You will be automatically promoted to **Contract Founder** status
- Constitutional authority will be granted immediately
- All actions will be recorded on blockchain

## 🔒 CRITICAL SECURITY

### ⚠️ PRIVATE KEY SECURITY
- **NEVER share the private key file**
- **NEVER store online or in cloud storage**
- **NEVER photograph or scan the private key**
- **This key can only be used ONCE**

### ✅ AFTER REGISTRATION
- Securely destroy or store the private key file
- Keep the public certificate for reference
- Save the recovery document in a secure location

## 📞 SUPPORT

For registration assistance:
- **Email**: founders@civic-platform.org
- **Security**: security@civic-platform.org

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Package**: {founder_id} Constitutional Founder Authority  
**Security Level**: Maximum
"""
        with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_thumb_drive_readme(self):
        """Create master thumb drive README"""
        readme_content = f"""# 🏛️ CIVIC ENGAGEMENT PLATFORM - FOUNDER DISTRIBUTION THUMB DRIVE

## 📋 OVERVIEW

This thumb drive contains **10 complete founder packages** for the Civic Engagement Platform.

**Purpose**: Secure distribution of constitutional founder authority  
**Security Level**: Maximum - each package grants full platform powers  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📁 CONTENTS

```
FOUNDER_THUMB_DRIVE/
├── INDIVIDUAL_FOUNDER_PACKAGES/     # 10 complete founder packages
│   ├── FOUNDER_01/ ... FOUNDER_10/  # Individual packages
├── FOUNDER_DISTRIBUTION_README.md   # Technical documentation
├── SECURITY_INSTRUCTIONS.md         # Security guidelines
├── DISTRIBUTION_SUMMARY.md          # Distribution tracking
├── founder_keys_master.json         # Master registry
└── README.md                        # This file
```

---

## 🎯 DISTRIBUTION WORKFLOW

### For Each Founder Promotion:

1. **Select Package**: Choose unused founder package (FOUNDER_01 through FOUNDER_10)
2. **Verify Recipient**: Confirm identity and trustworthiness
3. **Secure Transfer**: Give complete package folder
4. **Track Usage**: Record distribution in DISTRIBUTION_SUMMARY.md
5. **Monitor Registration**: Verify successful completion

---

## 🛡️ SECURITY GUIDELINES

### ✅ DO:
- Verify recipient identity with documentation
- Transfer complete packages via secure, offline methods
- Keep master record of distributions
- Store thumb drive in maximum security location

### ❌ NEVER:
- Email or transmit packages electronically
- Share single package with multiple people
- Store thumb drive in unsecured locations
- Allow unauthorized access to contents

---

## 📊 DISTRIBUTION TRACKING

See `DISTRIBUTION_SUMMARY.md` for complete tracking log.

---

## 🚨 SECURITY BREACH PROTOCOL

If thumb drive or packages are compromised:

1. **Immediate Actions**:
   - Revoke all unused founder keys
   - Notify platform security team
   - Document incident details

2. **Contact**:
   - **Emergency**: security@civic-platform.org
   - **Phone**: [SECURITY HOTLINE]

---

**🔒 Each package contains constitutional authority - handle with maximum security**
"""
        with open(self.thumb_drive_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_security_instructions(self):
        """Create detailed security instructions"""
        security_content = """# 🔒 FOUNDER PACKAGE SECURITY INSTRUCTIONS

## ⚠️ CRITICAL SECURITY OVERVIEW

Each founder package contains **constitutional authority keys** that grant maximum platform powers. Security failures could compromise the entire democratic system.

---

## 🛡️ PHYSICAL SECURITY

### Storage Requirements
- **Location**: Locked safe or secure facility
- **Access**: Limited to authorized personnel only
- **Monitoring**: Video surveillance recommended
- **Backup**: Secure offsite copy of master registry

### Transportation Security
- **Method**: Hand-delivered by trusted personnel
- **Container**: Tamper-evident packaging
- **Escort**: Two-person escort recommended
- **Documentation**: Chain of custody log required

---

## 🔐 DIGITAL SECURITY

### File Handling
- **Never** store on cloud services (Dropbox, Google Drive, etc.)
- **Never** transmit via email or messaging
- **Never** copy to unsecured USB drives
- **Always** verify file integrity before distribution

### Access Control
- **Authentication**: Multi-factor authentication required
- **Audit Logs**: All access attempts logged
- **Encryption**: Files encrypted at rest
- **Destruction**: Secure deletion after use

---

## 👤 RECIPIENT VERIFICATION

### Identity Verification Requirements
1. **Government ID**: Valid photo identification
2. **Background Check**: Professional background verification
3. **References**: Multiple professional references
4. **Interview**: In-person or secure video interview
5. **Documentation**: Written verification record

### Red Flags - DO NOT DISTRIBUTE
- Unable to provide valid identification
- Refuses in-person verification
- Requests remote/electronic delivery
- Cannot provide verifiable references
- Evasive about intended platform use

---

## 📋 DISTRIBUTION CHECKLIST

### Pre-Distribution
- [ ] Recipient identity verified with government ID
- [ ] Background check completed
- [ ] References confirmed
- [ ] Security briefing completed
- [ ] Distribution tracking updated
- [ ] Chain of custody documented

### During Distribution
- [ ] Package integrity verified
- [ ] Complete package contents confirmed
- [ ] Security instructions reviewed with recipient
- [ ] Recipient acknowledges responsibilities
- [ ] Emergency contact information exchanged
- [ ] Signed receipt obtained

### Post-Distribution
- [ ] Registration completion monitored (30-day window)
- [ ] Key usage verified in blockchain
- [ ] Distribution summary updated
- [ ] Package marked as distributed
- [ ] Follow-up contact scheduled
- [ ] Security monitoring active

---

## 🚨 INCIDENT RESPONSE

### Security Incident Types
1. **Lost Package**: Package cannot be located
2. **Unauthorized Access**: Package accessed by unauthorized person
3. **Compromised Key**: Private key potentially exposed
4. **Theft**: Package stolen
5. **Misuse**: Key used improperly

### Immediate Response Steps
1. **Document**: Record all incident details
2. **Notify**: Contact security team immediately
3. **Assess**: Evaluate extent of compromise
4. **Mitigate**: Revoke compromised keys if possible
5. **Report**: File formal incident report
6. **Review**: Update security procedures

### Emergency Contacts
- **Security Team**: security@civic-platform.org
- **Technical Support**: tech@civic-platform.org
- **Emergency Hotline**: [24/7 SECURITY HOTLINE]

---

## 📊 AUDIT AND COMPLIANCE

### Required Documentation
- Distribution log with timestamps
- Recipient verification records
- Chain of custody documentation
- Security briefing confirmations
- Incident reports (if any)
- Periodic security audits

### Review Schedule
- **Weekly**: Distribution log review
- **Monthly**: Security procedure audit
- **Quarterly**: Comprehensive security assessment
- **Annual**: Full security system review

---

## ✅ SECURITY BEST PRACTICES

1. **Principle of Least Access**: Only authorized personnel
2. **Defense in Depth**: Multiple security layers
3. **Need to Know**: Information shared on need-to-know basis
4. **Continuous Monitoring**: Active security monitoring
5. **Regular Updates**: Security procedures kept current
6. **Training**: All personnel properly trained
7. **Documentation**: Complete audit trail maintained

---

**🔒 Security is everyone's responsibility**  
**When in doubt, choose maximum security over convenience**  
**Report all security concerns immediately**
"""
        with open(self.thumb_drive_dir / "SECURITY_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
            f.write(security_content)
    
    def _create_distribution_summary(self):
        """Create distribution tracking summary"""
        summary_content = f"""# 📊 FOUNDER PACKAGE DISTRIBUTION SUMMARY

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Packages**: 10  
**Status**: Ready for Distribution

---

## 📋 DISTRIBUTION LOG

| Package ID | Status | Distributed To | Date | Registration Status | Notes |
|-----------|---------|---------------|------|-------------------|-------|
| FOUNDER_01 | ⏳ Available | - | - | - | - |
| FOUNDER_02 | ⏳ Available | - | - | - | - |
| FOUNDER_03 | ⏳ Available | - | - | - | - |
| FOUNDER_04 | ⏳ Available | - | - | - | - |
| FOUNDER_05 | ⏳ Available | - | - | - | - |
| FOUNDER_06 | ⏳ Available | - | - | - | - |
| FOUNDER_07 | ⏳ Available | - | - | - | - |
| FOUNDER_08 | ⏳ Available | - | - | - | - |
| FOUNDER_09 | ⏳ Available | - | - | - | - |
| FOUNDER_10 | ⏳ Available | - | - | - | - |

**Legend**:
- ⏳ Available - Ready for distribution
- 📦 Distributed - Package given to recipient
- ✅ Registered - Successfully registered on platform
- ⚠️ Pending - Awaiting registration completion
- ❌ Revoked - Package revoked for security reasons

---

## 📈 DISTRIBUTION STATISTICS

- **Total Packages**: 10
- **Available**: 10
- **Distributed**: 0
- **Registered**: 0
- **Pending**: 0
- **Revoked**: 0

---

## 📝 DISTRIBUTION INSTRUCTIONS

### To Record Distribution:
1. Update the distribution log table above
2. Change status from "⏳ Available" to "📦 Distributed"
3. Fill in recipient name, date, and notes
4. Keep original for audit trail
5. Monitor for registration completion

### To Record Registration:
1. Update status to "✅ Registered"
2. Add registration date to notes
3. Verify blockchain record
4. Update statistics section

---

## 🔒 SECURITY NOTES

- Keep this document secure and confidential
- Update immediately after each distribution
- Create backup copies in secure location
- Review regularly for accuracy
- Report any discrepancies immediately

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Maintained By**: Platform Security Team
"""
        with open(self.thumb_drive_dir / "DISTRIBUTION_SUMMARY.md", 'w', encoding='utf-8') as f:
            f.write(summary_content)
    
    def validate_package(self) -> Tuple[bool, str]:
        """Validate created package completeness"""
        logger.info("Validating package...")
        
        issues = []
        
        # Check thumb drive structure
        if not self.thumb_drive_dir.exists():
            issues.append("Thumb drive directory missing")
        
        # Check master files
        required_files = [
            'README.md',
            'SECURITY_INSTRUCTIONS.md',
            'DISTRIBUTION_SUMMARY.md',
            'founder_keys_master.json'
        ]
        
        for filename in required_files:
            if not (self.thumb_drive_dir / filename).exists():
                issues.append(f"Missing master file: {filename}")
        
        # Check individual packages
        individual_dir = self.thumb_drive_dir / "INDIVIDUAL_FOUNDER_PACKAGES"
        if not individual_dir.exists():
            issues.append("Individual packages directory missing")
        else:
            for i in range(1, 11):
                founder_id = f"FOUNDER_{i:02d}"
                founder_dir = individual_dir / founder_id
                
                if not founder_dir.exists():
                    issues.append(f"Missing package directory: {founder_id}")
                    continue
                
                # Check required files in package
                required_package_files = [
                    f"{founder_id}_PRIVATE_KEY.pem",
                    f"{founder_id}_INFO.json",
                    "README.md"
                ]
                
                for filename in required_package_files:
                    if not (founder_dir / filename).exists():
                        issues.append(f"Missing file in {founder_id}: {filename}")
        
        if issues:
            error_msg = "Validation failed:\n" + "\n".join(f"- {issue}" for issue in issues)
            logger.error(error_msg)
            return False, error_msg
        
        logger.info("✅ Package validation successful")
        return True, "Package validated successfully"
    
    def run_full_automation(self) -> Tuple[bool, str]:
        """Run complete automated package creation process"""
        logger.info("=" * 80)
        logger.info("AUTOMATED FOUNDER PACKAGE CREATION SYSTEM")
        logger.info("=" * 80)
        
        # Step 1: Validate prerequisites
        success, message = self.validate_prerequisites()
        if not success:
            return False, f"Prerequisites validation failed: {message}"
        
        # Step 2: Generate founder keys
        success, message, output_dir = self.generate_founder_keys(count=10)
        if not success:
            return False, f"Founder key generation failed: {message}"
        
        # Step 3: Create thumb drive package
        success, message = self.create_thumb_drive_package()
        if not success:
            return False, f"Thumb drive package creation failed: {message}"
        
        # Step 4: Validate package
        success, message = self.validate_package()
        if not success:
            return False, f"Package validation failed: {message}"
        
        logger.info("=" * 80)
        logger.info("🎉 AUTOMATION COMPLETE!")
        logger.info(f"📁 Output: {self.thumb_drive_dir.absolute()}")
        logger.info(f"📦 Packages: 10 founder packages ready")
        logger.info(f"🔒 Security: Maximum security level")
        logger.info(f"📋 Log: founder_package_automation.log")
        logger.info("=" * 80)
        
        return True, "Complete automation successful"


def main():
    """Main entry point for automation script"""
    parser = argparse.ArgumentParser(
        description='Automated Founder Package Creation and Distribution System'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Run full automation without prompts'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing package'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('founder_distributions'),
        help='Output directory for founder distributions'
    )
    
    args = parser.parse_args()
    
    automation = FounderPackageAutomation(output_dir=args.output_dir)
    
    if args.validate_only:
        success, message = automation.validate_package()
        print(message)
        return 0 if success else 1
    
    if args.auto:
        success, message = automation.run_full_automation()
        if not success:
            print(f"❌ Automation failed: {message}")
            return 1
        return 0
    
    # Interactive mode
    print("🏛️ FOUNDER PACKAGE AUTOMATION SYSTEM")
    print("=" * 60)
    print()
    print("This will create a complete founder distribution package:")
    print("- 10 founder key sets with cryptographic keys")
    print("- PDF certificates and recovery documents")
    print("- Organized thumb drive structure")
    print("- Security instructions and tracking")
    print()
    
    choice = input("Proceed with automation? (y/N): ").lower().strip()
    
    if choice == 'y':
        success, message = automation.run_full_automation()
        if not success:
            print(f"❌ Automation failed: {message}")
            return 1
        return 0
    else:
        print("❌ Automation cancelled")
        return 1


if __name__ == "__main__":
    sys.exit(main())
