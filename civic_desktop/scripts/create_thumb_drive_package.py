#!/usr/bin/env python3
"""
FOUNDER THUMB DRIVE PACKAGE CREATOR
Creates organized founder packages ready for thumb drive distribution
"""

import os
import shutil
from pathlib import Path
import json

def create_thumb_drive_package():
    """Create organized founder packages for thumb drive distribution"""
    
    print("📁 CREATING FOUNDER THUMB DRIVE PACKAGE")
    print("=" * 60)
    
    # Source and destination paths
    source_dir = Path("founder_distributions")
    thumb_drive_dir = Path("FOUNDER_THUMB_DRIVE")
    individual_packages_dir = thumb_drive_dir / "INDIVIDUAL_FOUNDER_PACKAGES"
    
    # Ensure directories exist
    thumb_drive_dir.mkdir(exist_ok=True)
    individual_packages_dir.mkdir(exist_ok=True)
    
    # Copy main documentation to thumb drive root
    print("📋 Copying main documentation...")
    if (source_dir / "README.md").exists():
        shutil.copy2(source_dir / "README.md", thumb_drive_dir / "FOUNDER_DISTRIBUTION_README.md")
        print("✅ Main README copied")
    
    # Copy master keys file
    if (source_dir / "founder_keys_master.json").exists():
        shutil.copy2(source_dir / "founder_keys_master.json", thumb_drive_dir / "founder_keys_master.json")
        print("✅ Master keys file copied")
    
    # Create individual founder packages
    print("\n🔑 Creating individual founder packages...")
    
    keys_dir = source_dir / "keys"
    pdfs_dir = source_dir / "pdfs"
    
    for i in range(1, 11):
        founder_id = f"FOUNDER_{i:02d}"
        print(f"   📦 Creating package for {founder_id}...")
        
        # Create individual founder directory
        founder_package_dir = individual_packages_dir / founder_id
        founder_package_dir.mkdir(exist_ok=True)
        
        # Copy private key
        private_key_file = keys_dir / f"{founder_id}_private_key.pem"
        if private_key_file.exists():
            shutil.copy2(private_key_file, founder_package_dir / f"{founder_id}_PRIVATE_KEY.pem")
        
        # Copy info file
        info_file = keys_dir / f"{founder_id}_info.json"
        if info_file.exists():
            shutil.copy2(info_file, founder_package_dir / f"{founder_id}_INFO.json")
        
        # Copy PDFs if they exist
        public_pdf = pdfs_dir / f"{founder_id}_public_pdf.pdf"
        if public_pdf.exists():
            shutil.copy2(public_pdf, founder_package_dir / f"{founder_id}_PUBLIC_CERTIFICATE.pdf")
        
        private_pdf = pdfs_dir / f"{founder_id}_private_pdf.pdf"
        if private_pdf.exists():
            shutil.copy2(private_pdf, founder_package_dir / f"{founder_id}_PRIVATE_RECOVERY.pdf")
        
        # Copy QR code PDFs as well
        public_qr_pdf = pdfs_dir / f"{founder_id}_public_qr.pdf"
        if public_qr_pdf.exists():
            shutil.copy2(public_qr_pdf, founder_package_dir / f"{founder_id}_PUBLIC_QR_CODE.pdf")
            
        private_qr_pdf = pdfs_dir / f"{founder_id}_private_qr.pdf"
        if private_qr_pdf.exists():
            shutil.copy2(private_qr_pdf, founder_package_dir / f"{founder_id}_PRIVATE_QR_CODE.pdf")
        
        # Create individual README for this founder
        create_individual_readme(founder_package_dir, founder_id)
        
        print(f"   ✅ {founder_id} package complete")
    
    # Create master thumb drive README
    create_thumb_drive_readme(thumb_drive_dir)
    
    # Create security instructions
    create_security_instructions(thumb_drive_dir)
    
    print(f"\n🎉 THUMB DRIVE PACKAGE COMPLETE!")
    print(f"📁 Location: {thumb_drive_dir.absolute()}")
    print(f"📦 Contains: 10 individual founder packages")
    print(f"🔒 Ready for secure distribution")

def create_individual_readme(package_dir: Path, founder_id: str):
    """Create README for individual founder package"""
    
    readme_content = f"""# 🏛️ CIVIC ENGAGEMENT PLATFORM - {founder_id} PACKAGE

## 📋 FOUNDER IDENTITY
- **Founder ID**: {founder_id}
- **Authority Level**: Constitutional Founder (Maximum)
- **Usage**: Single-use promotion key
- **Status**: Ready for distribution

## 📁 PACKAGE CONTENTS

### 🔑 **{founder_id}_PRIVATE_KEY.pem**
- **CONFIDENTIAL**: Never share or email this file
- **Purpose**: Constitutional founder authentication
- **Usage**: Enter during platform registration
- **Security**: Single-use only - becomes unusable after first use

### 📄 **{founder_id}_PUBLIC_CERTIFICATE.pdf**
- **SHAREABLE**: Safe to share for identity verification
- **Contents**: Founder identity, blockchain address, QR codes
- **Purpose**: Verification and platform introduction

### 📄 **{founder_id}_PRIVATE_RECOVERY.pdf**
- **CONFIDENTIAL**: Account recovery information
- **Contents**: Private key backup, security instructions
- **Purpose**: Emergency access and key recovery

### � **{founder_id}_PUBLIC_QR_CODE.pdf**
- **SHAREABLE**: QR codes for identity verification
- **Contents**: Machine-readable founder verification data
- **Purpose**: Quick verification and blockchain lookup

### 📄 **{founder_id}_PRIVATE_QR_CODE.pdf**
- **CONFIDENTIAL**: QR codes for key data
- **Contents**: Machine-readable key fingerprint data
- **Purpose**: Technical verification and backup

### �📋 **{founder_id}_INFO.json**
- **Metadata**: Key fingerprint, blockchain address, timestamps
- **Purpose**: Technical verification and audit trail

## 🎯 USAGE INSTRUCTIONS

### **Step 1: Share This Package**
Give the complete folder to the intended founder recipient.

### **Step 2: Founder Registration**
1. Go to Civic Engagement Platform
2. Create new account (normal registration)
3. When prompted for "Founder Key", enter the complete private key
4. System will validate and promote to Constitutional Founder

### **Step 3: Key Security**
- Private key becomes permanently used after registration
- Keep recovery documents in secure location
- Public certificate can be shared for verification

## 🛡️ SECURITY WARNINGS

❌ **NEVER email or transmit the private key electronically**  
❌ **NEVER share private key with multiple people**  
❌ **NEVER store in cloud services or online locations**  

✅ **DO store in secure, offline location**  
✅ **DO verify recipient identity before sharing**  
✅ **DO destroy after successful registration (optional)**  

## 📞 SUPPORT

- **Platform**: Civic Engagement Platform
- **Documentation**: See main README.md
- **Security**: Report any issues immediately

---
**This package grants MAXIMUM CONSTITUTIONAL AUTHORITY**  
**Handle with appropriate security measures**
"""
    
    with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_thumb_drive_readme(thumb_drive_dir: Path):
    """Create master README for thumb drive"""
    
    readme_content = """# 🏛️ CIVIC ENGAGEMENT PLATFORM - FOUNDER DISTRIBUTION THUMB DRIVE

## 📋 OVERVIEW

This thumb drive contains **10 complete founder packages** for the Civic Engagement Platform.

**Purpose**: Secure distribution of constitutional founder authority  
**Security Level**: Maximum - each package grants full platform powers  
**Usage**: Single-use keys for trusted founder promotion  

---

## 📁 THUMB DRIVE CONTENTS

```
FOUNDER_THUMB_DRIVE/
├── INDIVIDUAL_FOUNDER_PACKAGES/     # 10 complete founder packages
│   ├── FOUNDER_01/                  # Individual founder package
│   │   ├── FOUNDER_01_PRIVATE_KEY.pem
│   │   ├── FOUNDER_01_PUBLIC_CERTIFICATE.pdf
│   │   ├── FOUNDER_01_PRIVATE_RECOVERY.pdf
│   │   ├── FOUNDER_01_INFO.json
│   │   └── README.md
│   ├── FOUNDER_02/ ... FOUNDER_10/  # 9 more complete packages
├── FOUNDER_DISTRIBUTION_README.md   # Technical documentation
├── SECURITY_INSTRUCTIONS.md         # Critical security guidelines
├── founder_keys_master.json         # Master distribution record
└── README.md                        # This file
```

---

## 🎯 DISTRIBUTION WORKFLOW

### **For Each Founder Promotion:**

1. **Select Package**: Choose unused founder package (FOUNDER_01 through FOUNDER_10)
2. **Verify Recipient**: Confirm identity and trustworthiness of recipient
3. **Secure Transfer**: Give complete package folder via secure method
4. **Track Usage**: Record which packages have been distributed
5. **Monitor Registration**: Verify successful founder promotion

### **Recipient Instructions:**
Each package contains complete instructions for the recipient.

---

## 🛡️ CRITICAL SECURITY GUIDELINES

### ✅ **DO:**
- Verify recipient identity before distribution
- Transfer complete packages via secure, offline methods
- Keep master record of which packages are distributed
- Store thumb drive in maximum security location
- Destroy or secure unused packages after distribution

### ❌ **NEVER:**
- Email or transmit packages electronically
- Share single package with multiple people
- Store thumb drive in unsecured locations
- Allow unauthorized access to package contents
- Distribute packages without proper verification

---

## 📊 PACKAGE TRACKING

### **Distribution Record:**
- **FOUNDER_01**: ⏳ Available
- **FOUNDER_02**: ⏳ Available  
- **FOUNDER_03**: ⏳ Available
- **FOUNDER_04**: ⏳ Available
- **FOUNDER_05**: ⏳ Available
- **FOUNDER_06**: ⏳ Available
- **FOUNDER_07**: ⏳ Available
- **FOUNDER_08**: ⏳ Available
- **FOUNDER_09**: ⏳ Available
- **FOUNDER_10**: ⏳ Available

**Update this record as packages are distributed.**

---

## 🚨 SECURITY BREACH PROTOCOL

If this thumb drive is lost, stolen, or compromised:

1. **Immediate Action**: Contact platform security team
2. **Key Revocation**: Disable unused founder keys
3. **Investigation**: Determine scope of potential breach
4. **Mitigation**: Implement security countermeasures
5. **Documentation**: Record incident and lessons learned

---

## 📞 CONTACT INFORMATION

- **Platform**: Civic Engagement Platform
- **Security Team**: security@civic-platform.org
- **Technical Support**: support@civic-platform.org
- **Emergency Contact**: [Add emergency contact information]

---

## ⚖️ CONSTITUTIONAL AUTHORITY

Each founder package grants **MAXIMUM CONSTITUTIONAL AUTHORITY** including:

- Constitutional amendment powers
- Emergency protocol override
- Platform governance modification
- Elder appointment authority  
- System integrity protection

**Handle with appropriate constitutional responsibility.**

---

**🔒 This thumb drive contains the keys to constitutional democracy 🔒**  
**Distribute responsibly and with maximum security precautions**
"""
    
    with open(thumb_drive_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_security_instructions(thumb_drive_dir: Path):
    """Create detailed security instructions"""
    
    security_content = """# 🛡️ FOUNDER PACKAGE SECURITY INSTRUCTIONS

## 🚨 CRITICAL SECURITY REQUIREMENTS

### **BEFORE DISTRIBUTION**

#### ✅ **Recipient Verification**
- [ ] Verify recipient identity with government-issued ID
- [ ] Confirm recipient understanding of constitutional responsibilities
- [ ] Ensure recipient has secure storage capabilities
- [ ] Document recipient information for audit trail
- [ ] Obtain signed acknowledgment of security responsibilities

#### ✅ **Package Preparation**
- [ ] Verify package contents are complete and uncorrupted
- [ ] Test that private key file is valid and readable
- [ ] Confirm all PDFs display correctly
- [ ] Create backup record of distribution
- [ ] Prepare secure transfer method

### **DURING DISTRIBUTION**

#### ✅ **Secure Transfer Methods**
- **✅ RECOMMENDED**: In-person handoff with signature confirmation
- **✅ ACCEPTABLE**: Secure courier with tracking and signature
- **✅ ACCEPTABLE**: Encrypted portable media with secure key exchange
- **❌ NEVER**: Email, cloud storage, or electronic transmission
- **❌ NEVER**: Unencrypted postal mail or standard shipping

#### ✅ **Transfer Protocol**
1. Meet recipient in secure, private location
2. Verify recipient identity again
3. Explain package contents and security requirements
4. Demonstrate registration process if possible
5. Obtain signed receipt with timestamp
6. Record transfer in master distribution log

### **AFTER DISTRIBUTION**

#### ✅ **Follow-up Requirements**
- [ ] Monitor for successful founder registration within 30 days
- [ ] Verify key usage in platform blockchain records
- [ ] Update distribution tracking records
- [ ] Secure or destroy any temporary copies
- [ ] Document lessons learned for future distributions

---

## 🔐 PRIVATE KEY SECURITY

### **Critical Private Key Protection:**

#### **The Private Key (.pem file) is MAXIMUM SECURITY:**
- Grants complete constitutional authority
- Cannot be revoked once used
- Becomes permanently attached to user account
- Provides emergency override powers

#### **Private Key Handling Rules:**
❌ **ABSOLUTELY NEVER:**
- Email or send via any electronic communication
- Store in cloud services (Google Drive, Dropbox, etc.)
- Save on internet-connected devices
- Share with multiple people
- Photograph or screenshot
- Print on shared printers
- Leave unattended in any location

✅ **REQUIRED SECURITY MEASURES:**
- Store on encrypted, offline media only
- Limit access to verified recipient only
- Use secure deletion for any temporary copies
- Maintain physical custody until transfer
- Verify recipient has secure storage plan

---

## 📋 PDF DOCUMENT SECURITY

### **Public Certificate PDF (Shareable):**
- ✅ Safe to share for identity verification
- ✅ Can be emailed or posted publicly
- ✅ Contains no sensitive authentication data
- ✅ Used for founder identity confirmation

### **Private Recovery PDF (Confidential):**
- 🚨 Contains backup of private key
- 🚨 Must be treated with same security as private key
- 🚨 Never transmit electronically
- 🚨 Store in maximum security location

---

## 🎯 RECIPIENT EDUCATION

### **Before Giving Package, Ensure Recipient Understands:**

#### **Constitutional Responsibilities:**
- Founder authority includes emergency powers
- Decisions affect entire platform governance
- Constitutional compliance is mandatory
- Transparency and accountability requirements

#### **Technical Requirements:**
- How to register account and use founder key
- Importance of secure key storage
- Single-use nature of the key
- Blockchain transparency of all actions

#### **Security Obligations:**
- Protect private key with maximum security
- Report any security incidents immediately
- Follow platform governance procedures
- Maintain confidentiality of sensitive operations

---

## 🚨 EMERGENCY PROCEDURES

### **If Package is Lost or Stolen:**

#### **Immediate Actions (Within 1 Hour):**
1. Contact platform security team immediately
2. Identify which specific package was compromised
3. Document circumstances of loss/theft
4. Initiate key revocation if possible
5. Report to appropriate authorities if criminal activity

#### **Investigation Phase (Within 24 Hours):**
1. Determine scope of potential compromise
2. Assess risk to platform security
3. Identify any other potentially affected packages
4. Implement additional security measures
5. Notify relevant stakeholders

#### **Mitigation Phase (Within 48 Hours):**
1. Revoke compromised keys if not yet used
2. Monitor blockchain for unauthorized usage
3. Implement enhanced security for remaining packages
4. Update security procedures based on incident
5. Document complete incident response

### **If Unauthorized Usage Detected:**

#### **Detection Indicators:**
- Founder registration with untracked key
- Blockchain records show unexpected founder actions
- Reports of unauthorized constitutional authority
- Security anomalies in platform governance

#### **Response Protocol:**
1. Immediately freeze affected founder account
2. Investigate source of unauthorized key
3. Audit all distributed packages
4. Implement emergency constitutional safeguards
5. Report to platform governance council

---

## 📞 EMERGENCY CONTACTS

### **Security Incidents:**
- **Primary**: security@civic-platform.org
- **Phone**: [Add emergency phone number]
- **Backup**: [Add backup contact]

### **Technical Support:**
- **Primary**: support@civic-platform.org  
- **Documentation**: docs.civic-platform.org
- **Platform Status**: status.civic-platform.org

### **Constitutional Issues:**
- **Elder Council**: elders@civic-platform.org
- **Constitutional Hotline**: [Add constitutional contact]
- **Legal Support**: legal@civic-platform.org

---

## 📋 SECURITY CHECKLIST

### **Pre-Distribution Security Verification:**
- [ ] Recipient identity verified with documentation
- [ ] Secure transfer method confirmed
- [ ] Package contents verified complete
- [ ] Backup distribution record created
- [ ] Security briefing completed with recipient
- [ ] Signed acknowledgment obtained
- [ ] Emergency contact information exchanged

### **Post-Distribution Follow-up:**
- [ ] Registration completion confirmed within 30 days
- [ ] Key usage verified in blockchain records
- [ ] Distribution tracking updated
- [ ] Security incident monitoring active
- [ ] Follow-up contact completed
- [ ] Lessons learned documented

---

**🔒 Remember: Each package contains the constitutional keys to democratic governance**  
**Security failures could compromise the entire platform**  
**When in doubt, choose maximum security over convenience**
"""
    
    with open(thumb_drive_dir / "SECURITY_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(security_content)

if __name__ == "__main__":
    create_thumb_drive_package()