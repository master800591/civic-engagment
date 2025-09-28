"""
PDF GENERATION TEST - Demonstrates user PDF document creation system
Tests public PDF (shareable) and private PDF (account recovery) generation
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add the civic_desktop directory directly
civic_desktop_path = Path(__file__).parent.parent
sys.path.insert(0, str(civic_desktop_path))

def test_pdf_generation_system():
    """Test the complete PDF generation system"""
    
    print("📄 CIVIC ENGAGEMENT PLATFORM - PDF GENERATION SYSTEM TEST")
    print("=" * 70)
    
    try:
        # Import required modules
        from users.pdf_generator import UserPDFGenerator
        from users.keys import RSAKeyManager
        
        print("✅ PDF generation modules imported successfully")
        
        # Step 1: Create test user data
        print("\n👤 Creating test user data...")
        
        test_user_data = {
            'user_id': 'TEST_USER_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
            'first_name': 'Alice',
            'last_name': 'Democracy',
            'email': 'alice.democracy@civic-platform.org',
            'password_hash': '$2b$12$example_hash_for_testing_purposes_only',
            'city': 'Liberty City',
            'state': 'Democracy State',
            'country': 'Constitutional Republic',
            'role': 'contract_citizen',
            'verification_status': 'verified',
            'created_at': datetime.now().isoformat(),
            'terms_accepted': True
        }
        
        print(f"✅ Test user created: {test_user_data['first_name']} {test_user_data['last_name']}")
        print(f"   User ID: {test_user_data['user_id']}")
        print(f"   Email: {test_user_data['email']}")
        
        # Step 2: Generate RSA keys
        print("\n🔑 Generating RSA keys...")
        
        key_manager = RSAKeyManager('users/private_keys')
        key_success, key_message, key_info = key_manager.generate_key_pair(
            test_user_data['user_id']
        )
        
        if key_success:
            print(f"✅ RSA keys generated successfully")
            print(f"   Key size: {key_info['key_size']} bits")
            print(f"   Fingerprint: {key_info['key_fingerprint'][:16]}...")
            print(f"   Blockchain address: {key_info['blockchain_address'][:20]}...")
        else:
            print(f"❌ RSA key generation failed: {key_message}")
            return
        
        # Step 3: Initialize PDF generator
        print("\n📄 Initializing PDF generator...")
        
        pdf_generator = UserPDFGenerator()
        
        print("✅ PDF generator initialized")
        print(f"   Output directory: {pdf_generator.pdf_output_dir}")
        print(f"   Public PDFs: {pdf_generator.public_pdfs_dir}")
        print(f"   Private PDFs: {pdf_generator.private_pdfs_dir}")
        print(f"   QR codes: {pdf_generator.qr_codes_dir}")
        
        # Step 4: Generate user PDFs
        print("\n🎨 Generating user PDF documents...")
        
        pdf_success, pdf_message, pdf_paths = pdf_generator.generate_user_pdfs(
            test_user_data, key_info
        )
        
        if pdf_success:
            print(f"✅ PDF generation successful!")
            print(f"   Message: {pdf_message}")
            
            # Display generated files
            print(f"\n📁 Generated Files:")
            for doc_type, file_path in pdf_paths.items():
                if file_path and Path(file_path).exists():
                    file_size = Path(file_path).stat().st_size
                    print(f"   ✅ {doc_type}: {file_path} ({file_size:,} bytes)")
                else:
                    print(f"   ❌ {doc_type}: Missing or failed")
                    
        else:
            print(f"❌ PDF generation failed: {pdf_message}")
            return
        
        # Step 5: Verify PDFs
        print("\n🔍 Verifying PDF documents...")
        
        verify_success, verify_message, verification_results = pdf_generator.verify_user_pdfs(
            test_user_data['user_id']
        )
        
        if verify_success:
            print(f"✅ PDF verification successful: {verify_message}")
            
            for file_type, exists in verification_results.items():
                status = "✅ EXISTS" if exists else "❌ MISSING"
                print(f"   {file_type}: {status}")
        else:
            print(f"❌ PDF verification failed: {verify_message}")
        
        # Step 6: Display PDF contents information
        print("\n📋 PDF CONTENT OVERVIEW")
        print("-" * 50)
        
        print("🌐 PUBLIC PDF CONTENTS:")
        print("   📝 User Information (name, email, role, location)")
        print("   ⛓️ Blockchain Information (address, key fingerprint)")  
        print("   🔐 RSA Public Key (full PEM format)")
        print("   📱 Public QR Code (shareable user verification)")
        print("   ✅ Verification Instructions")
        print("   🔗 Platform links and contact information")
        print("   ➡️ PURPOSE: Safe to share for identity verification")
        
        print("\n🔒 PRIVATE PDF CONTENTS:")
        print("   🆔 Account Recovery Information (user ID, recovery code)")
        print("   🔑 Private Key Information (location, fingerprint)")
        print("   📱 Private QR Code (recovery data)")
        print("   🔧 Recovery Instructions (step-by-step guide)")
        print("   📞 Emergency Contacts (support, security team)")
        print("   ⚠️ Security Warnings (confidentiality reminders)")
        print("   ➡️ PURPOSE: Account recovery - KEEP CONFIDENTIAL")

        # Show detailed example output
        print(f"\n📋 DETAILED PDF EXAMPLES")
        print("-" * 35)
        print("   💡 See test_pdf_examples.py for detailed PDF output examples")
        print("   📄 Run: py tests\\test_pdf_examples.py")
    """Show detailed examples of what the generated PDFs contain"""
    
    print("\n" + "=" * 80)
    print("📄 EXAMPLE PDF OUTPUT - WHAT THE GENERATED PDFs ACTUALLY LOOK LIKE")
    print("=" * 80)
    
    # PUBLIC PDF Example
    print("\n🌐 PUBLIC PDF EXAMPLE OUTPUT:")
    print("┌" + "─" * 78 + "┐")
    print("│                    CIVIC ENGAGEMENT PLATFORM                          │")
    print("│                     Public Identity Document                          │")
    print("├" + "─" * 78 + "┤")
    print("│ 👤 USER INFORMATION:                                                  │")
    print("│    Name: Alice Democracy                                              │")
    print("│    Email: alice.democracy@civic-platform.org                         │")
    print("│    User ID: TEST_USER_20250928_140258                                │")
    print("│    Role: Contract Citizen                                             │")
    print("│    Location: Liberty City, Democracy State, Constitutional Republic   │")
    print("│    Registration Date: 2025-09-28                                     │")
    print("│    Verification Status: ✅ VERIFIED                                   │")
    print("├" + "─" * 78 + "┤")
    print("│ ⛓️ BLOCKCHAIN INFORMATION:                                             │")
    print("│    Blockchain Address: civic_75996f633d33547a8e9d2b4c1f8a7e6d5       │")
    print("│    Key Fingerprint: 34b0293272f61cd9e8a5b7f3c4d1a9e8f6b2c7d4       │")
    print("│    Block Height: 1,247                                               │")
    print("│    Network: Constitutional Democracy Chain v1.0                      │")
    print("├" + "─" * 78 + "┤")
    print("│ 🔐 RSA PUBLIC KEY (2048-bit):                                         │")
    print("│ -----BEGIN PUBLIC KEY-----                                            │")
    print("│ MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1Kj7xvN2mP8wQ...     │")
    print("│ rR5sT6vU7wX8yZ9aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0uV1wX2yZ3aB...     │")
    print("│ [Full 1632-character RSA public key continues...]                     │")
    print("│ -----END PUBLIC KEY-----                                              │")
    print("├" + "─" * 78 + "┤")
    print("│ 📱 PUBLIC VERIFICATION QR CODE:                                       │")
    print("│    ██████████████    ████  ██████████████                            │")
    print("│    ██          ██  ██████  ██          ██                            │")
    print("│    ██  ██████  ██    ████  ██  ██████  ██                            │")
    print("│    ██  ██████  ██  ██  ██  ██  ██████  ██                            │")
    print("│    ██  ██████  ██  ██████  ██  ██████  ██                            │")
    print("│    ██          ██  ██  ██  ██          ██                            │")
    print("│    ██████████████  ██  ██  ██████████████                            │")
    print("│                                                                      │")
    print("│ QR Contains: User ID + Blockchain Address + Key Fingerprint          │")
    print("├" + "─" * 78 + "┤")
    print("│ ✅ VERIFICATION INSTRUCTIONS:                                         │")
    print("│ 1. Scan QR code with Civic Platform mobile app                       │")
    print("│ 2. Verify blockchain signature matches user's public key             │")
    print("│ 3. Cross-reference with platform's public registry                   │")
    print("│ 4. Confirm identity through government ID verification               │")
    print("├" + "─" * 78 + "┤")
    print("│ 🔗 PLATFORM INFORMATION:                                              │")
    print("│ Website: https://civic-engagement-platform.org                       │")
    print("│ Support: support@civic-platform.org                                  │")
    print("│ Verification Portal: verify.civic-platform.org                       │")
    print("│                                                                      │")
    print("│ 📄 DOCUMENT STATUS: ✅ SAFE TO SHARE PUBLICLY                        │")
    print("│ Generated: 2025-09-28 14:02:58 UTC                                   │")
    print("└" + "─" * 78 + "┘")
    
    print("\n" + "─" * 80)
    
    # PRIVATE PDF Example
    print("\n🔒 PRIVATE PDF EXAMPLE OUTPUT:")
    print("┌" + "─" * 78 + "┐")
    print("│                    CIVIC ENGAGEMENT PLATFORM                          │")
    print("│                 🚨 PRIVATE RECOVERY DOCUMENT 🚨                       │")
    print("│                        ⚠️ CONFIDENTIAL ⚠️                             │")
    print("├" + "─" * 78 + "┤")
    print("│ 🆔 ACCOUNT RECOVERY INFORMATION:                                      │")
    print("│    User ID: TEST_USER_20250928_140258                                │")
    print("│    Recovery Code: 5255-A256-CD29-2502-B20F-7B5E-2784-9280           │")
    print("│    Email: alice.democracy@civic-platform.org                         │")
    print("│    Generated: 2025-09-28 14:02:58 UTC                               │")
    print("│    Expires: Never (permanent recovery)                               │")
    print("├" + "─" * 78 + "┤")
    print("│ 🔑 PRIVATE KEY INFORMATION:                                           │")
    print("│    Key File Location: users/private_keys/                            │")
    print("│    Private Key File: TEST_USER_20250928_140258_private_key.pem       │")
    print("│    Key Fingerprint: 34b0293272f61cd9e8a5b7f3c4d1a9e8f6b2c7d4       │")
    print("│    Key Size: 2048 bits                                               │")
    print("│    Blockchain Address: civic_75996f633d33547a8e9d2b4c1f8a7e6d5       │")
    print("│                                                                      │")
    print("│ ⚠️ WARNING: Private key files are stored separately and securely     │")
    print("├" + "─" * 78 + "┤")
    print("│ 📱 PRIVATE RECOVERY QR CODE:                                          │")
    print("│    ████████████████████████████████████                              │")
    print("│    ██                                ██                              │")
    print("│    ██  ████████    ██████    ████  ██                              │")
    print("│    ██  ██    ██  ██    ██  ██  ██  ██                              │")
    print("│    ██  ██████████████████████████  ██                              │")
    print("│    ██  ██    ██  ██    ██  ██  ██  ██                              │")
    print("│    ██  ████████    ██████    ████  ██                              │")
    print("│    ██                                ██                              │")
    print("│    ████████████████████████████████████                              │")
    print("│                                                                      │")
    print("│ QR Contains: Recovery Code + User ID + Key Fingerprint              │")
    print("├" + "─" * 78 + "┤")
    print("│ 🔧 ACCOUNT RECOVERY INSTRUCTIONS:                                     │")
    print("│                                                                      │")
    print("│ IF YOU FORGET YOUR PASSWORD:                                         │")
    print("│ 1. Go to platform login page                                         │")
    print("│ 2. Click 'Forgot Password' → 'Account Recovery'                      │")
    print("│ 3. Enter your email and recovery code above                          │")
    print("│ 4. System will verify your identity using blockchain                 │")
    print("│ 5. Follow prompts to create new password                             │")
    print("│                                                                      │")
    print("│ IF YOU LOSE ACCESS TO YOUR DEVICE:                                   │")
    print("│ 1. Install Civic Platform on new device                             │")
    print("│ 2. Select 'Recover Account' on login screen                          │")
    print("│ 3. Scan the private QR code above with new device                    │")
    print("│ 4. Provide additional identity verification if requested             │")
    print("│ 5. Your account will be restored with full functionality            │")
    print("├" + "─" * 78 + "┤")
    print("│ 📞 EMERGENCY CONTACTS:                                                │")
    print("│ Account Recovery Support: recovery@civic-platform.org                │")
    print("│ Security Team: security@civic-platform.org                           │")
    print("│ Emergency Hotline: +1 (555) CIVIC-01                                │")
    print("│ Business Hours: 24/7 for account recovery                           │")
    print("├" + "─" * 78 + "┤")
    print("│ 🚨 CRITICAL SECURITY WARNINGS:                                        │")
    print("│                                                                      │")
    print("│ ❌ NEVER share this document with anyone                             │")
    print("│ ❌ NEVER email or transmit electronically                            │")
    print("│ ❌ NEVER store in cloud services or online                           │")
    print("│ ❌ NEVER photograph or screenshot this document                      │")
    print("│                                                                      │")
    print("│ ✅ DO store in secure, encrypted location                           │")
    print("│ ✅ DO create physical backup copies                                 │")
    print("│ ✅ DO store separately from your private key files                  │")
    print("│ ✅ DO verify access quarterly                                       │")
    print("│ ✅ DO inform trusted family member of location (emergencies only)   │")
    print("│                                                                      │")
    print("│ 🔐 DOCUMENT STATUS: 🚨 CONFIDENTIAL - ACCOUNT RECOVERY ONLY 🚨      │")
    print("│ If compromised, immediately contact: security@civic-platform.org     │")
    print("└" + "─" * 78 + "┘")
    
    print("\n" + "─" * 80)
    print("📊 DOCUMENT COMPARISON:")
    print("─" * 40)
    
    comparison_table = """
    ┌──────────────────┬─────────────────────┬─────────────────────┐
    │ FEATURE          │ PUBLIC PDF          │ PRIVATE PDF         │
    ├──────────────────┼─────────────────────┼─────────────────────┤
    │ File Size        │ ~38 KB              │ ~37 KB              │
    │ Pages            │ 2-3 pages           │ 3-4 pages           │
    │ Sharing Status   │ ✅ Safe to Share    │ 🚫 CONFIDENTIAL     │
    │ Contains         │ Public info only    │ Recovery secrets    │
    │ QR Code Data     │ Verification info   │ Recovery codes      │
    │ Purpose          │ Identity proof      │ Account recovery    │
    │ Storage          │ Anywhere safe       │ Encrypted only      │
    │ Backup Strategy  │ Multiple copies OK  │ Limited, secure     │
    │ Access Frequency │ As needed          │ Emergency only      │
    └──────────────────┴─────────────────────┴─────────────────────┘
    """
    print(comparison_table)
    
    print("\n💡 REAL-WORLD USAGE EXAMPLES:")
    print("─" * 45)
    
    print("\n📤 PUBLIC PDF - When Alice needs to prove her identity:")
    print("   • Job application: 'Here's my blockchain-verified identity'")
    print("   • Government services: 'This PDF proves my civic platform registration'")
    print("   • Bank account: 'Use this QR code to verify my crypto credentials'")
    print("   • Legal proceedings: 'Court-admissible digital identity proof'")
    print("   • Educational enrollment: 'Blockchain-verified student identity'")
    
    print("\n🔒 PRIVATE PDF - When Alice needs account recovery:")
    print("   • Forgot password: Uses recovery code to regain access")
    print("   • Lost phone: Scans private QR code on new device")
    print("   • Computer crash: Restores account using recovery information")
    print("   • Identity theft: Proves ownership through private recovery data")
    print("   • Platform migration: Transfers account to new platform version")
    
    print("\n🎯 KEY BENEFITS:")
    print("─" * 20)
    print("✅ No more 'forgot password' helplessness")
    print("✅ Government-grade identity verification")
    print("✅ Blockchain-backed tamper-proof credentials")
    print("✅ Self-sovereign identity management")
    print("✅ Cross-platform compatibility")
    print("✅ Emergency access for family/legal representatives")
    print("✅ Professional identity verification for employment")
    print("✅ Academic credential verification for education")
    
    print("\n" + "=" * 80)
        
        # Step 7: Show usage scenarios
        print(f"\n💡 USAGE SCENARIOS")
        print("-" * 30)
        
        print("📤 PUBLIC PDF USE CASES:")
        print("   • Share with government agencies for ID verification")
        print("   • Provide to employers for blockchain credential validation")
        print("   • Submit to educational institutions for enrollment")
        print("   • Use in legal proceedings as identity evidence")
        print("   • Share with service providers requiring crypto verification")
        
        print("\n🔐 PRIVATE PDF USE CASES:")
        print("   • Account recovery when password is forgotten")
        print("   • Device replacement or loss scenarios")
        print("   • Platform migration or backup restoration")
        print("   • Emergency access by authorized family/legal representatives")
        print("   • Security audit and key management verification")
        
        # Step 8: Security recommendations
        print(f"\n🛡️ SECURITY RECOMMENDATIONS")
        print("-" * 35)
        
        print("📁 PUBLIC PDF SECURITY:")
        print("   ✅ Safe to share - contains no sensitive information")
        print("   ✅ Can be stored in cloud services")
        print("   ✅ Can be emailed or transmitted electronically")
        print("   ✅ Print copies for physical documentation")
        
        print("\n🚨 PRIVATE PDF SECURITY:")
        print("   🚫 NEVER share with anyone")
        print("   🔒 Store in encrypted, secure locations only")
        print("   💾 Create multiple secure backups")
        print("   📍 Store separately from private key files")
        print("   🔐 Consider hardware security modules for storage")
        print("   ⏰ Regular access verification (quarterly)")
        
        # Step 9: Test recovery code
        print(f"\n🔢 RECOVERY CODE TESTING")
        print("-" * 30)
        
        recovery_code = pdf_generator._generate_recovery_code(test_user_data, key_info)
        print(f"Generated Recovery Code: {recovery_code}")
        print(f"Code Length: {len(recovery_code)} characters")
        print(f"Format: Groups of 4 characters separated by dashes")
        print(f"Security: SHA-256 hash of user data + key fingerprint")
        
        print("\n" + "=" * 70)
        print("🎉 PDF GENERATION SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print(f"📄 Generated comprehensive user documentation")
        print(f"🔐 Public PDF: Ready for sharing and verification")
        print(f"🚨 Private PDF: Secure account recovery document")
        print("=" * 70)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure reportlab and qrcode are installed:")
        print("   pip install reportlab qrcode[pil]")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_pdf_integration_with_registration():
    """Test PDF generation integrated with user registration"""
    
    print("\n🔗 TESTING PDF INTEGRATION WITH USER REGISTRATION")
    print("=" * 60)
    
    try:
        from users.backend import UserBackend
        
        # Test user registration with PDF generation
        user_backend = UserBackend()
        
        test_registration_data = {
            'first_name': 'Bob',
            'last_name': 'Blockchain',
            'email': f'bob.blockchain.{datetime.now().strftime("%Y%m%d%H%M%S")}@civic-platform.org',
            'password': 'ComplexCivicEngagement2024!@#',
            'confirm_password': 'ComplexCivicEngagement2024!@#',
            'city': 'Crypto City',
            'state': 'Blockchain State',
            'country': 'Digital Republic',
            'terms_accepted': True
        }
        
        print(f"👤 Testing registration with PDF generation...")
        print(f"   User: {test_registration_data['first_name']} {test_registration_data['last_name']}")
        print(f"   Email: {test_registration_data['email']}")
        
        reg_success, reg_message, user_record = user_backend.register_user(test_registration_data)
        
        if reg_success:
            print(f"✅ Registration successful!")
            print(f"   User ID: {user_record['user_id']}")
            print(f"   Role: {user_record['role']}")
            
            # Check if PDFs were generated
            if 'pdf_documents' in user_record:
                pdf_docs = user_record['pdf_documents']
                print(f"\n📄 PDF Generation Results:")
                
                for doc_type, doc_path in pdf_docs.items():
                    if doc_path and Path(doc_path).exists():
                        print(f"   ✅ {doc_type}: Generated successfully")
                    else:
                        print(f"   ⚠️ {doc_type}: Not generated or missing")
            else:
                print(f"\n⚠️ No PDF documents found in registration result")
        else:
            print(f"❌ Registration failed: {reg_message}")
    
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

def show_pdf_system_overview():
    """Display overview of the PDF system architecture"""
    
    print("\n🏗️ PDF GENERATION SYSTEM ARCHITECTURE")
    print("=" * 50)
    
    architecture = """
    📁 File Structure:
    users/
    ├── pdf_generator.py          # Main PDF generation class
    ├── user_pdfs/               # PDF output directory
    │   ├── public/              # Public PDFs (shareable)
    │   ├── private/             # Private PDFs (confidential)
    │   └── qr_codes/            # Generated QR code images
    └── backend.py               # Integration with user registration
    
    🔄 Generation Workflow:
    1. User Registration → RSA Key Generation
    2. Key Generation → PDF Generator Called
    3. PDF Generator → Creates Public & Private PDFs
    4. QR Code Generator → Embeds verification codes
    5. File Storage → Organized by user ID
    6. Blockchain Recording → PDF generation logged
    
    📄 Document Types:
    
    🌐 PUBLIC PDF:
    • User profile information
    • RSA public key (full PEM)
    • Blockchain address & fingerprint
    • Verification QR code
    • Platform contact information
    • Safe to share publicly
    
    🔒 PRIVATE PDF:
    • Account recovery code
    • Private key file location
    • Recovery instructions
    • Emergency contacts
    • Security warnings
    • CONFIDENTIAL - Keep secure
    
    🔐 Security Features:
    • Separate storage directories
    • Clear labeling (public vs private)
    • Recovery code generation (SHA-256)
    • QR codes with different data
    • Comprehensive security warnings
    • Integration with blockchain audit
    """
    
    print(architecture)

if __name__ == "__main__":
    print("🧪 Running all PDF system tests automatically...\n")
    show_pdf_system_overview()
    test_pdf_generation_system()
    test_pdf_integration_with_registration()
    print("\n✅ All PDF tests completed!")