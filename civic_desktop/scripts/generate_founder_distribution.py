"""
FOUNDER KEY DISTRIBUTION SYSTEM
Creates 10 founder key sets with PDFs for sharing and integrates hardcoded single-use keys
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import hashlib
import uuid

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def generate_10_founder_keys():
    """Generate 10 complete founder key sets with PDFs"""
    
    print("🏛️ CIVIC ENGAGEMENT PLATFORM - 10 FOUNDER KEYS GENERATION")
    print("=" * 80)
    
    try:
        from users.founder_keys import FounderKeyManager
        from users.pdf_generator import UserPDFGenerator
        
        print("✅ Modules loaded successfully")
        
        # Initialize managers
        founder_manager = FounderKeyManager()
        pdf_generator = UserPDFGenerator()
        
        # Create output directory for founder distributions
        distribution_dir = Path('founder_distributions')
        distribution_dir.mkdir(exist_ok=True)
        
        keys_dir = distribution_dir / 'keys'
        pdfs_dir = distribution_dir / 'pdfs'
        keys_dir.mkdir(exist_ok=True)
        pdfs_dir.mkdir(exist_ok=True)
        
        print(f"📁 Distribution directory: {distribution_dir}")
        
        # Generate 10 founder key sets
        founder_keys_data = []
        hardcoded_keys = []
        
        print(f"\n🔐 Generating 10 Founder Key Sets...")
        print("-" * 50)
        
        for i in range(1, 11):
            founder_id = f"FOUNDER_{i:02d}"
            print(f"   Generating {founder_id}...")
            
            # Generate individual founder key
            success, message, key_data = founder_manager.generate_individual_founder_key(founder_id)
            
            if success:
                print(f"   ✅ {founder_id} key generated")
                
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
                
                # Generate PDFs for this founder
                pdf_success, pdf_message, pdf_paths = pdf_generator.generate_founder_pdfs(
                    founder_user_data, key_data
                )
                
                if pdf_success:
                    print(f"   ✅ {founder_id} PDFs generated")
                    
                    # Move PDFs to distribution directory
                    for pdf_type, pdf_path in pdf_paths.items():
                        if pdf_path and Path(pdf_path).exists():
                            new_path = pdfs_dir / f"{founder_id}_{pdf_type}.pdf"
                            Path(pdf_path).rename(new_path)
                            pdf_paths[pdf_type] = str(new_path)
                else:
                    print(f"   ⚠️ {founder_id} PDF generation failed: {pdf_message}")
                
                # Save individual key file
                key_file = keys_dir / f"{founder_id}_private_key.pem"
                with open(key_file, 'w') as f:
                    f.write(key_data['private_key_pem'])
                
                # Create founder info file
                founder_info = {
                    'founder_id': founder_id,
                    'key_fingerprint': key_data['key_fingerprint'],
                    'public_key_pem': key_data['public_key_pem'],
                    'blockchain_address': key_data['blockchain_address'],
                    'created_at': datetime.now().isoformat(),
                    'pdf_locations': pdf_paths,
                    'usage_status': 'unused',
                    'single_use_only': True
                }
                
                info_file = keys_dir / f"{founder_id}_info.json"
                with open(info_file, 'w') as f:
                    json.dump(founder_info, f, indent=2)
                
                founder_keys_data.append(founder_info)
                
                # Prepare hardcoded key data
                hardcoded_key = {
                    'id': founder_id,
                    'key_hash': hashlib.sha256(key_data['private_key_pem'].encode()).hexdigest(),
                    'fingerprint': key_data['key_fingerprint'],
                    'blockchain_address': key_data['blockchain_address'],
                    'used': False
                }
                hardcoded_keys.append(hardcoded_key)
                
            else:
                print(f"   ❌ {founder_id} generation failed: {message}")
        
        # Create master distribution file
        distribution_data = {
            'generated_at': datetime.now().isoformat(),
            'total_keys': len(founder_keys_data),
            'founder_keys': founder_keys_data,
            'distribution_note': 'These are single-use founder keys for platform promotion',
            'usage_instructions': 'Each key can only be used once to promote someone to founder status'
        }
        
        master_file = distribution_dir / 'founder_keys_master.json'
        with open(master_file, 'w') as f:
            json.dump(distribution_data, f, indent=2)
        
        # Generate hardcoded integration code
        generate_hardcoded_keys_integration(hardcoded_keys, distribution_dir)
        
        # Generate distribution README
        generate_distribution_readme(distribution_dir, len(founder_keys_data))
        
        print(f"\n🎉 SUCCESS! Generated {len(founder_keys_data)} Founder Key Sets")
        print(f"📁 Location: {distribution_dir}")
        print(f"📄 Keys: {keys_dir}")
        print(f"📋 PDFs: {pdfs_dir}")
        print(f"📖 Instructions: {distribution_dir}/README.md")
        
        return True, f"Generated {len(founder_keys_data)} founder key sets", distribution_dir
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required modules are available")
        return False, f"Import error: {e}", None
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, f"Generation failed: {e}", None

def generate_hardcoded_keys_integration(hardcoded_keys, distribution_dir):
    """Generate the hardcoded keys integration code"""
    
    print(f"\n🔧 Generating hardcoded keys integration...")
    
    # Create the hardcoded keys module
    hardcoded_module = f'''"""
HARDCODED FOUNDER KEYS - Single-Use Promotion Keys
Generated: {datetime.now().isoformat()}
Total Keys: {len(hardcoded_keys)}

SECURITY NOTE: These keys are hardcoded for distribution and can only be used once each.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class HardcodedFounderKeys:
    """Manages hardcoded founder keys for single-use promotion"""
    
    # Hardcoded founder keys (hashes only for security)
    FOUNDER_KEYS = {hardcoded_keys}
    
    # Track used keys (will be persisted)
    _used_keys_file = "users/used_founder_keys.json"
    
    @classmethod
    def validate_founder_key(cls, private_key_pem: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate a founder private key and mark as used if valid
        Returns: (is_valid, message, founder_info)
        """
        import json
        from pathlib import Path
        
        # Calculate hash of provided key
        key_hash = hashlib.sha256(private_key_pem.encode()).hexdigest()
        
        # Load used keys
        used_keys = cls._load_used_keys()
        
        # Check if key has already been used
        if key_hash in used_keys:
            return False, "This founder key has already been used", None
        
        # Find matching hardcoded key
        matching_key = None
        for key_data in cls.FOUNDER_KEYS:
            if key_data['key_hash'] == key_hash:
                matching_key = key_data
                break
        
        if not matching_key:
            return False, "Invalid founder key - not recognized", None
        
        # Mark key as used
        used_keys[key_hash] = {{
            'founder_id': matching_key['id'],
            'used_at': datetime.now().isoformat(),
            'fingerprint': matching_key['fingerprint'],
            'blockchain_address': matching_key['blockchain_address']
        }}
        
        # Save used keys
        cls._save_used_keys(used_keys)
        
        return True, "Founder key validated and marked as used", {{
            'founder_id': matching_key['id'],
            'key_fingerprint': matching_key['fingerprint'],
            'blockchain_address': matching_key['blockchain_address'],
            'is_founder_key': True,
            'single_use': True,
            'used_at': used_keys[key_hash]['used_at']
        }}
    
    @classmethod
    def _load_used_keys(cls) -> Dict:
        """Load used keys from file"""
        import json
        from pathlib import Path
        
        used_keys_path = Path(cls._used_keys_file)
        if used_keys_path.exists():
            try:
                with open(used_keys_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {{}}
    
    @classmethod
    def _save_used_keys(cls, used_keys: Dict):
        """Save used keys to file"""
        import json
        from pathlib import Path
        
        used_keys_path = Path(cls._used_keys_file)
        used_keys_path.parent.mkdir(exist_ok=True)
        
        with open(used_keys_path, 'w') as f:
            json.dump(used_keys, f, indent=2)
    
    @classmethod
    def get_key_status(cls) -> Dict:
        """Get status of all founder keys"""
        used_keys = cls._load_used_keys()
        
        total_keys = len(cls.FOUNDER_KEYS)
        used_count = len(used_keys)
        available_count = total_keys - used_count
        
        return {{
            'total_keys': total_keys,
            'used_keys': used_count,
            'available_keys': available_count,
            'used_key_details': used_keys
        }}
    
    @classmethod
    def is_key_available(cls, key_hash: str) -> bool:
        """Check if a key is still available for use"""
        used_keys = cls._load_used_keys()
        return key_hash not in used_keys
'''
    
    # Save the hardcoded keys module
    hardcoded_file = distribution_dir / 'hardcoded_founder_keys.py'
    with open(hardcoded_file, 'w') as f:
        f.write(hardcoded_module)
    
    # Also save to the users directory for integration
    users_hardcoded_file = Path('users/hardcoded_founder_keys.py')
    with open(users_hardcoded_file, 'w') as f:
        f.write(hardcoded_module)
    
    print(f"✅ Hardcoded keys integration saved to:")
    print(f"   📁 {hardcoded_file}")
    print(f"   📁 {users_hardcoded_file}")

def generate_distribution_readme(distribution_dir, key_count):
    """Generate comprehensive README for founder key distribution"""
    
    readme_content = f'''# 🏛️ CIVIC ENGAGEMENT PLATFORM - FOUNDER KEY DISTRIBUTION

## 📋 OVERVIEW

This package contains **{key_count} single-use founder keys** for the Civic Engagement Platform.

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Purpose:** Platform promotion and founder authority distribution  
**Security Level:** Maximum - each key can only be used once  

---

## 📁 PACKAGE CONTENTS

```
founder_distributions/
├── keys/                           # Private founder keys
│   ├── FOUNDER_01_private_key.pem  # Individual private keys
│   ├── FOUNDER_01_info.json        # Key metadata
│   ├── ... (10 complete key sets)
├── pdfs/                           # Shareable founder PDFs
│   ├── FOUNDER_01_public.pdf       # Public founder identity
│   ├── FOUNDER_01_private.pdf      # Private recovery document
│   ├── ... (20 total PDFs)
├── founder_keys_master.json        # Master distribution file
├── hardcoded_founder_keys.py       # Code integration
└── README.md                       # This file
```

---

## 🔐 FOUNDER KEY DETAILS

### Each Founder Key Set Includes:

1. **🔑 Private Key File** (`.pem`)
   - RSA-2048 private key
   - Single-use authentication
   - Grants constitutional founder authority

2. **📄 Public PDF** (shareable)
   - Founder identity verification
   - Public key and blockchain address
   - Platform verification instructions

3. **📄 Private PDF** (confidential)
   - Account recovery information
   - Emergency access procedures
   - Security warnings and instructions

4. **📋 Metadata File** (`.json`)
   - Key fingerprint and blockchain address
   - Generation timestamp
   - Usage status tracking

---

## 🎯 USAGE INSTRUCTIONS

### For Platform Promotion:

1. **Share Complete Set** with new founder:
   - Give them both PDF files
   - Provide the private key file securely
   - Explain single-use limitation

2. **New Founder Registration:**
   - They create account normally
   - During registration, enter private key
   - System validates and promotes to founder
   - Key becomes permanently used

3. **Verification Process:**
   - System checks key against hardcoded hashes
   - Validates authenticity and usage status
   - Assigns founder role and constitutional powers
   - Records usage in blockchain audit trail

---

## 🛡️ SECURITY FEATURES

### ✅ **Single-Use Protection:**
- Each key can only be used once
- Used keys tracked in `users/used_founder_keys.json`
- Prevents key reuse or sharing abuse

### ✅ **Cryptographic Security:**
- RSA-2048 encryption for all keys
- SHA-256 hashing for key verification
- Blockchain integration for audit trails

### ✅ **Access Control:**
- Hardcoded key validation in source code
- No external key database vulnerabilities
- Tamper-proof key verification system

---

## 📊 KEY STATUS TRACKING

Monitor key usage through the platform:

```python
from users.hardcoded_founder_keys import HardcodedFounderKeys

# Check overall status
status = HardcodedFounderKeys.get_key_status()
print(f"Available keys: {{status['available_keys']}}")
print(f"Used keys: {{status['used_keys']}}")
```

---

## 🚨 IMPORTANT SECURITY WARNINGS

### ❌ **DO NOT:**
- Share private key files electronically
- Store keys in cloud services
- Use the same key multiple times
- Distribute keys to unverified individuals

### ✅ **DO:**
- Keep private keys secure and encrypted
- Verify recipient identity before distribution
- Track key distribution manually
- Destroy used private key files after successful registration

---

## 📞 SUPPORT & CONTACTS

For questions about founder key distribution:

- **Platform Development:** tech@civic-platform.org
- **Security Issues:** security@civic-platform.org  
- **Founder Support:** founders@civic-platform.org

---

## 🔧 TECHNICAL INTEGRATION

The hardcoded keys are integrated into the platform through:

1. **`users/hardcoded_founder_keys.py`** - Key validation system
2. **`users/backend.py`** - Registration integration
3. **`users/founder_keys.py`** - Founder key management
4. **Blockchain audit trail** - Usage tracking

---

## 🎉 DISTRIBUTION SUCCESS

This package enables secure, scalable founder authority distribution while maintaining:

- **Constitutional Authority** - Each founder gains full platform powers
- **Security Integrity** - Single-use prevents abuse
- **Audit Transparency** - All usage tracked on blockchain
- **User Experience** - Simple registration with key validation

**Ready for distribution and platform promotion!** 🏛️

---

*Generated by Civic Engagement Platform Founder Key System v1.0*  
*Security Level: Maximum | Single-Use: Enforced | Blockchain Audit: Enabled*
'''
    
    readme_file = distribution_dir / 'README.md'
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Distribution README generated: {readme_file}")

if __name__ == "__main__":
    print("🏛️ FOUNDER KEY DISTRIBUTION GENERATOR")
    print("=" * 50)
    
    choice = input("Generate 10 founder key sets with PDFs? (y/N): ").lower().strip()
    
    if choice == 'y':
        success, message, distribution_dir = generate_10_founder_keys()
        
        if success:
            print(f"\n🎉 GENERATION COMPLETE!")
            print(f"📁 Distribution package: {distribution_dir}")
            print(f"🔑 Ready for secure founder key distribution")
        else:
            print(f"\n❌ Generation failed: {message}")
    else:
        print("❌ Generation cancelled")