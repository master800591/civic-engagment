"""
USER PDF GENERATOR - Creates public and private PDF documents for users
Generates public PDF with shareable information and private PDF for account recovery
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import hashlib
import base64

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("Warning: reportlab not available. PDF generation disabled.")
    REPORTLAB_AVAILABLE = False

try:
    import qrcode
    from PIL import Image as PILImage
    QR_AVAILABLE = True
except ImportError:
    print("Warning: qrcode/PIL not available. QR code generation disabled.")
    QR_AVAILABLE = False

class UserPDFGenerator:
    """Generates public and private PDF documents for user accounts"""
    
    def __init__(self, config_path: str = None):
        """Initialize PDF generator"""
        if config_path:
            self.config = self._load_config(config_path)
            self.pdf_output_dir = Path(self.config.get('user_pdfs_dir', 'users/user_pdfs'))
        else:
            self.pdf_output_dir = Path('users/user_pdfs')
            
        # Create output directories
        self.pdf_output_dir.mkdir(parents=True, exist_ok=True)
        self.public_pdfs_dir = self.pdf_output_dir / 'public'
        self.private_pdfs_dir = self.pdf_output_dir / 'private'
        self.qr_codes_dir = self.pdf_output_dir / 'qr_codes'
        
        self.public_pdfs_dir.mkdir(parents=True, exist_ok=True)
        self.private_pdfs_dir.mkdir(parents=True, exist_ok=True)
        self.qr_codes_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def generate_user_pdfs(self, user_data: Dict[str, Any], key_info: Dict[str, Any]) -> Tuple[bool, str, Dict[str, str]]:
        """
        Generate both public and private PDFs for a user
        
        Args:
            user_data: User registration data
            key_info: RSA key information
            
        Returns:
            Tuple of (success: bool, message: str, pdf_paths: Dict[str, str])
        """
        if not REPORTLAB_AVAILABLE:
            return False, "PDF generation not available - reportlab not installed", {}
        
        try:
            user_id = user_data['user_id']
            
            # Generate QR codes
            qr_success, qr_message, qr_paths = self._generate_qr_codes(user_data, key_info)
            if not qr_success:
                print(f"⚠️ QR code generation failed: {qr_message}")
                qr_paths = {}
            
            # Generate public PDF
            public_success, public_message, public_path = self._generate_public_pdf(
                user_data, key_info, qr_paths
            )
            
            # Generate private PDF  
            private_success, private_message, private_path = self._generate_private_pdf(
                user_data, key_info, qr_paths
            )
            
            if public_success and private_success:
                pdf_paths = {
                    'public_pdf': public_path,
                    'private_pdf': private_path,
                    **qr_paths
                }
                
                return True, "User PDFs generated successfully", pdf_paths
            else:
                error_msg = f"PDF generation partial failure - Public: {public_message}, Private: {private_message}"
                return False, error_msg, {}
        
        except Exception as e:
            return False, f"Error generating user PDFs: {str(e)}", {}
    
    def _generate_qr_codes(self, user_data: Dict[str, Any], key_info: Dict[str, Any]) -> Tuple[bool, str, Dict[str, str]]:
        """Generate QR codes for public sharing and private recovery"""
        if not QR_AVAILABLE:
            return True, "QR codes not available", {}
        
        try:
            user_id = user_data['user_id']
            
            # Public QR code data (shareable information)
            public_qr_data = {
                'platform': 'Civic Engagement Platform',
                'user_id': user_id,
                'name': f"{user_data['first_name']} {user_data['last_name']}",
                'email': user_data['email'],
                'role': user_data['role'],
                'blockchain_address': key_info['blockchain_address'],
                'public_key_fingerprint': key_info['key_fingerprint'],
                'verification_url': f"https://civic-platform.org/verify/{user_id}",
                'created': datetime.now().isoformat()
            }
            
            # Private QR code data (recovery information)
            recovery_code = self._generate_recovery_code(user_data, key_info)
            private_qr_data = {
                'platform': 'Civic Engagement Platform - PRIVATE',
                'type': 'account_recovery',
                'user_id': user_id,
                'recovery_code': recovery_code,
                'key_fingerprint': key_info['key_fingerprint'],
                'created': datetime.now().isoformat(),
                'warning': 'CONFIDENTIAL - Keep secure for account recovery'
            }
            
            # Generate public QR code
            public_qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            public_qr.add_data(json.dumps(public_qr_data, separators=(',', ':')))
            public_qr.make(fit=True)
            
            public_qr_image = public_qr.make_image(fill_color="black", back_color="white")
            public_qr_path = str(self.qr_codes_dir / f"{user_id}_public_qr.png")
            public_qr_image.save(public_qr_path)
            
            # Generate private QR code
            private_qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            private_qr.add_data(json.dumps(private_qr_data, separators=(',', ':')))
            private_qr.make(fit=True)
            
            private_qr_image = private_qr.make_image(fill_color="darkred", back_color="white")
            private_qr_path = str(self.qr_codes_dir / f"{user_id}_private_qr.png")
            private_qr_image.save(private_qr_path)
            
            qr_paths = {
                'public_qr': public_qr_path,
                'private_qr': private_qr_path
            }
            
            return True, "QR codes generated successfully", qr_paths
        
        except Exception as e:
            return False, f"QR code generation failed: {str(e)}", {}
    
    def _generate_public_pdf(self, user_data: Dict[str, Any], key_info: Dict[str, Any], 
                           qr_paths: Dict[str, str]) -> Tuple[bool, str, str]:
        """Generate public PDF with shareable user information"""
        try:
            user_id = user_data['user_id']
            public_pdf_path = str(self.public_pdfs_dir / f"{user_id}_public_profile.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(public_pdf_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkgreen
            )
            
            # Title
            story.append(Paragraph("🏛️ Civic Engagement Platform", title_style))
            story.append(Paragraph("Public User Profile", styles['Heading2']))
            story.append(Spacer(1, 0.3*inch))
            
            # User Information Section
            story.append(Paragraph("👤 User Information", header_style))
            
            user_info_data = [
                ['Full Name:', f"{user_data['first_name']} {user_data['last_name']}"],
                ['Email:', user_data['email']],
                ['User ID:', user_data['user_id']],
                ['Role:', user_data['role'].replace('_', ' ').title()],
                ['Location:', f"{user_data['city']}, {user_data['state']}, {user_data['country']}"],
                ['Registration:', datetime.fromisoformat(user_data['created_at']).strftime('%B %d, %Y at %I:%M %p')],
                ['Verification:', user_data.get('verification_status', 'Pending').title()]
            ]
            
            user_table = Table(user_info_data, colWidths=[2*inch, 4*inch])
            user_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(user_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Blockchain Information Section
            story.append(Paragraph("⛓️ Blockchain Information", header_style))
            
            blockchain_info_data = [
                ['Blockchain Address:', key_info['blockchain_address']],
                ['Public Key Fingerprint:', key_info['key_fingerprint']],
                ['Key Size:', f"{key_info['key_size']} bits"],
                ['Key Created:', datetime.fromisoformat(key_info['created_at']).strftime('%B %d, %Y at %I:%M %p')]
            ]
            
            blockchain_table = Table(blockchain_info_data, colWidths=[2*inch, 4*inch])
            blockchain_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(blockchain_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Public Key Section
            story.append(Paragraph("🔐 RSA Public Key", header_style))
            
            # Format public key for display
            public_key_lines = key_info['public_key_pem'].strip().split('\n')
            formatted_key = '<br/>'.join(public_key_lines)
            
            key_style = ParagraphStyle(
                'KeyStyle',
                parent=styles['Code'],
                fontSize=8,
                fontName='Courier',
                leading=10,
                leftIndent=20,
                rightIndent=20,
                borderWidth=1,
                borderColor=colors.grey,
                borderPadding=10,
                backColor=colors.lightgrey
            )
            
            story.append(Paragraph(formatted_key, key_style))
            story.append(Spacer(1, 0.3*inch))
            
            # QR Code Section
            if 'public_qr' in qr_paths and os.path.exists(qr_paths['public_qr']):
                story.append(Paragraph("📱 Public QR Code", header_style))
                story.append(Paragraph("Scan this QR code to verify user information:", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                # Add QR code image
                qr_image = Image(qr_paths['public_qr'], width=2*inch, height=2*inch)
                qr_image.hAlign = 'CENTER'
                story.append(qr_image)
                story.append(Spacer(1, 0.2*inch))
            
            # Verification Information
            story.append(Paragraph("✅ Verification Instructions", header_style))
            verification_text = f"""
            <b>To verify this user's identity and public key:</b><br/>
            1. Scan the QR code above or visit: https://civic-platform.org/verify/{user_id}<br/>
            2. Compare the blockchain address and key fingerprint<br/>
            3. Verify the digital signature using the provided public key<br/>
            4. Check the blockchain for user registration records<br/><br/>
            
            <b>This is a PUBLIC document - safe to share for identity verification.</b>
            """
            
            story.append(Paragraph(verification_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer_text = f"""
            <i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            Civic Engagement Platform - Constitutional Democracy<br/>
            Document Type: Public Profile - Safe to Share</i>
            """
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return True, "Public PDF generated successfully", public_pdf_path
        
        except Exception as e:
            return False, f"Public PDF generation failed: {str(e)}", ""
    
    def _generate_private_pdf(self, user_data: Dict[str, Any], key_info: Dict[str, Any], 
                            qr_paths: Dict[str, str]) -> Tuple[bool, str, str]:
        """Generate private PDF for account recovery (DO NOT SHARE)"""
        try:
            user_id = user_data['user_id']
            private_pdf_path = str(self.private_pdfs_dir / f"{user_id}_private_recovery.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(private_pdf_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'PrivateTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkred
            )
            
            warning_style = ParagraphStyle(
                'Warning',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.red,
                backColor=colors.yellow,
                borderWidth=2,
                borderColor=colors.red,
                borderPadding=10
            )
            
            header_style = ParagraphStyle(
                'PrivateHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkred
            )
            
            # Title and Warning
            story.append(Paragraph("🚨 PRIVATE ACCOUNT RECOVERY", title_style))
            story.append(Paragraph("⚠️ CONFIDENTIAL - DO NOT SHARE ⚠️", warning_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Security Notice
            security_text = """
            <b>CRITICAL SECURITY NOTICE:</b><br/>
            This document contains sensitive information for account recovery purposes only.
            Keep this document absolutely secure and confidential. Loss of this information
            may result in permanent inability to recover your account.
            """
            
            story.append(Paragraph(security_text, warning_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Account Information
            story.append(Paragraph("👤 Account Recovery Information", header_style))
            
            recovery_code = self._generate_recovery_code(user_data, key_info)
            
            recovery_info_data = [
                ['User ID:', user_data['user_id']],
                ['Full Name:', f"{user_data['first_name']} {user_data['last_name']}"],
                ['Email:', user_data['email']],
                ['Recovery Code:', recovery_code],
                ['Key Fingerprint:', key_info['key_fingerprint']],
                ['Account Created:', datetime.fromisoformat(user_data['created_at']).strftime('%B %d, %Y at %I:%M %p')],
                ['Password Hash:', user_data.get('password_hash', 'N/A')[:32] + '...']
            ]
            
            recovery_table = Table(recovery_info_data, colWidths=[2*inch, 4*inch])
            recovery_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightpink),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(recovery_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Private Key Information
            story.append(Paragraph("🔑 Private Key Information", header_style))
            
            key_location = f"users/private_keys/{user_id}_private.pem"
            
            private_key_info = f"""
            <b>Private Key File Location:</b> {key_location}<br/>
            <b>Key Size:</b> {key_info['key_size']} bits<br/>
            <b>Key Fingerprint:</b> {key_info['key_fingerprint']}<br/>
            <b>Blockchain Address:</b> {key_info['blockchain_address']}<br/><br/>
            
            <b>IMPORTANT:</b> Your private key file is stored separately and encrypted.
            You will need both this recovery document AND access to your private key file
            to fully recover your account.
            """
            
            story.append(Paragraph(private_key_info, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Recovery QR Code
            if 'private_qr' in qr_paths and os.path.exists(qr_paths['private_qr']):
                story.append(Paragraph("📱 Private Recovery QR Code", header_style))
                story.append(Paragraph("🚨 CONFIDENTIAL - Contains account recovery information", warning_style))
                story.append(Spacer(1, 0.1*inch))
                
                # Add QR code image
                qr_image = Image(qr_paths['private_qr'], width=2*inch, height=2*inch)
                qr_image.hAlign = 'CENTER'
                story.append(qr_image)
                story.append(Spacer(1, 0.2*inch))
            
            # Recovery Instructions
            story.append(Paragraph("🔧 Account Recovery Instructions", header_style))
            
            recovery_instructions = """
            <b>If you need to recover your account:</b><br/>
            1. Locate this private recovery document (keep multiple secure copies)<br/>
            2. Find your private key file in the specified location<br/>
            3. Contact platform support with your User ID and Recovery Code<br/>
            4. Provide the key fingerprint for verification<br/>
            5. Support will guide you through the secure recovery process<br/><br/>
            
            <b>Security Recommendations:</b><br/>
            • Store multiple copies of this document in secure locations<br/>
            • Keep private key file backed up separately<br/>
            • Never share this information with anyone<br/>
            • Consider using encrypted storage for additional security<br/>
            • Regularly verify you can access both this document and your private key
            """
            
            story.append(Paragraph(recovery_instructions, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Emergency Contacts
            story.append(Paragraph("📞 Emergency Recovery Contacts", header_style))
            
            emergency_info = """
            <b>Platform Support:</b> support@civic-platform.org<br/>
            <b>Security Team:</b> security@civic-platform.org<br/>
            <b>Recovery Hotline:</b> +1-800-CIVIC-HELP<br/>
            <b>Web Portal:</b> https://civic-platform.org/recovery<br/><br/>
            
            Always verify you are contacting official platform channels.
            """
            
            story.append(Paragraph(emergency_info, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Final Warning
            final_warning = """
            <b>FINAL SECURITY REMINDER:</b><br/>
            This document contains everything needed to recover your account.
            Treat it with the same security as you would your passport, birth certificate,
            or other critical identity documents. Unauthorized access to this information
            could result in complete account compromise.
            """
            
            story.append(Paragraph(final_warning, warning_style))
            
            # Footer
            footer_text = f"""
            <i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            Civic Engagement Platform - Constitutional Democracy<br/>
            Document Type: PRIVATE RECOVERY - KEEP CONFIDENTIAL</i>
            """
            
            footer_style = ParagraphStyle(
                'PrivateFooter',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.darkred
            )
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return True, "Private PDF generated successfully", private_pdf_path
        
        except Exception as e:
            return False, f"Private PDF generation failed: {str(e)}", ""
    
    def _generate_recovery_code(self, user_data: Dict[str, Any], key_info: Dict[str, Any]) -> str:
        """Generate a secure recovery code for the user"""
        # Combine user data for unique recovery code
        recovery_data = f"{user_data['user_id']}:{user_data['email']}:{key_info['key_fingerprint']}:{user_data['created_at']}"
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(recovery_data.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # Format as recovery code (groups of 4 characters)
        recovery_code = '-'.join([hash_hex[i:i+4].upper() for i in range(0, 32, 4)])
        
        return recovery_code
    
    def verify_user_pdfs(self, user_id: str) -> Tuple[bool, str, Dict[str, bool]]:
        """Verify that user PDFs exist and are accessible"""
        try:
            public_pdf_path = self.public_pdfs_dir / f"{user_id}_public_profile.pdf"
            private_pdf_path = self.private_pdfs_dir / f"{user_id}_private_recovery.pdf"
            public_qr_path = self.qr_codes_dir / f"{user_id}_public_qr.png"
            private_qr_path = self.qr_codes_dir / f"{user_id}_private_qr.png"
            
            verification_results = {
                'public_pdf_exists': public_pdf_path.exists(),
                'private_pdf_exists': private_pdf_path.exists(),
                'public_qr_exists': public_qr_path.exists(),
                'private_qr_exists': private_qr_path.exists()
            }
            
            all_exist = all(verification_results.values())
            
            if all_exist:
                return True, "All user PDFs verified successfully", verification_results
            else:
                missing = [key for key, exists in verification_results.items() if not exists]
                return False, f"Missing PDF files: {', '.join(missing)}", verification_results
        
        except Exception as e:
            return False, f"PDF verification failed: {str(e)}", {}
    
    def get_user_pdf_paths(self, user_id: str) -> Dict[str, str]:
        """Get file paths for user's PDF documents"""
        return {
            'public_pdf': str(self.public_pdfs_dir / f"{user_id}_public_profile.pdf"),
            'private_pdf': str(self.private_pdfs_dir / f"{user_id}_private_recovery.pdf"),
            'public_qr': str(self.qr_codes_dir / f"{user_id}_public_qr.png"),
            'private_qr': str(self.qr_codes_dir / f"{user_id}_private_qr.png")
        }
    
    def generate_founder_pdfs(self, founder_data: Dict[str, Any], key_info: Dict[str, Any]) -> Tuple[bool, str, Dict[str, str]]:
        """
        Generate specialized PDF documents for founder key distribution
        Creates public founder identity PDF and private founder key PDF
        
        Args:
            founder_data: Founder user information
            key_info: Founder key cryptographic data
            
        Returns:
            Tuple of (success: bool, message: str, pdf_paths: Dict[str, str])
        """
        try:
            if not REPORTLAB_AVAILABLE:
                return False, "PDF generation not available - reportlab not installed", {}
            
            founder_id = founder_data['user_id']
            pdf_paths = {}
            
            # Generate founder public PDF (for sharing)
            public_success, public_message, public_path = self._generate_founder_public_pdf(
                founder_data, key_info, founder_id
            )
            
            if public_success:
                pdf_paths['public_pdf'] = public_path
            
            # Generate founder private PDF (confidential key information)
            private_success, private_message, private_path = self._generate_founder_private_pdf(
                founder_data, key_info, founder_id
            )
            
            if private_success:
                pdf_paths['private_pdf'] = private_path
            
            # Generate founder QR codes
            qr_success, qr_message, qr_paths = self._generate_founder_qr_codes(
                founder_data, key_info, founder_id
            )
            
            if qr_success:
                pdf_paths.update(qr_paths)
            
            if public_success and private_success and qr_success:
                return True, "Founder PDFs generated successfully", pdf_paths
            else:
                failed_operations = []
                if not public_success: failed_operations.append(f"Public PDF: {public_message}")
                if not private_success: failed_operations.append(f"Private PDF: {private_message}")
                if not qr_success: failed_operations.append(f"QR codes: {qr_message}")
                
                return False, f"PDF generation partially failed: {'; '.join(failed_operations)}", pdf_paths
        
        except Exception as e:
            return False, f"Founder PDF generation failed: {str(e)}", {}
    
    def _generate_founder_public_pdf(self, founder_data: Dict[str, Any], key_info: Dict[str, Any], 
                                    founder_id: str) -> Tuple[bool, str, Optional[str]]:
        """Generate public founder identity PDF"""
        try:
            public_pdf_path = str(self.public_pdfs_dir / f"{founder_id}_public_founder.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(public_pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'], 
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkred
            )
            
            # Title
            story.append(Paragraph("🏛️ CIVIC ENGAGEMENT PLATFORM", title_style))
            story.append(Paragraph("FOUNDER AUTHORITY CERTIFICATE", title_style))
            story.append(Spacer(1, 20))
            
            # Founder Information
            story.append(Paragraph("👑 FOUNDER INFORMATION", header_style))
            
            founder_info_data = [
                ['Founder ID:', founder_data['user_id']],
                ['Name:', f"{founder_data['first_name']} {founder_data['last_name']}"],
                ['Email:', founder_data['email']],
                ['Role:', 'Constitutional Platform Founder'],
                ['Authority Level:', 'Maximum - Genesis Founder'],
                ['Created:', datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")],
                ['Status:', 'Active Founder Certificate']
            ]
            
            founder_table = Table(founder_info_data, colWidths=[2*inch, 3.5*inch])
            founder_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(founder_table)
            story.append(Spacer(1, 20))
            
            # Constitutional Authority
            story.append(Paragraph("⚖️ CONSTITUTIONAL AUTHORITY", header_style))
            
            authority_text = """
            This certificate grants the holder MAXIMUM CONSTITUTIONAL AUTHORITY within the
            Civic Engagement Platform, including:
            
            • Constitutional Amendment Authority
            • Emergency Protocol Override Powers  
            • Platform Governance Modification Rights
            • Elder Appointment Authority
            • System Integrity Protection Responsibilities
            
            This authority is subject to constitutional safeguards and supermajority consensus
            requirements as defined in the platform's governance framework.
            """
            
            story.append(Paragraph(authority_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Cryptographic Information
            story.append(Paragraph("🔐 CRYPTOGRAPHIC VERIFICATION", header_style))
            
            crypto_data = [
                ['Key Fingerprint:', key_info['key_fingerprint'][:32] + '...'],
                ['Blockchain Address:', key_info['blockchain_address']],
                ['Key Size:', '2048-bit RSA'],
                ['Key Type:', 'Founder Authority Key'],
                ['Usage:', 'Single-use Constitutional Authority']
            ]
            
            crypto_table = Table(crypto_data, colWidths=[2*inch, 3.5*inch])
            crypto_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(crypto_table)
            story.append(Spacer(1, 30))
            
            # Platform Information
            story.append(Paragraph("🔗 PLATFORM INFORMATION", header_style))
            
            platform_text = """
            Website: https://civic-engagement-platform.org
            Constitution: docs.civic-platform.org/constitution
            Founder Support: founders@civic-platform.org
            Security Team: security@civic-platform.org
            
            This document serves as official verification of founder authority within the
            Constitutional Democracy framework of the Civic Engagement Platform.
            """
            
            story.append(Paragraph(platform_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Security Notice
            story.append(Paragraph("🛡️ SECURITY NOTICE", header_style))
            
            security_text = """
            📄 DOCUMENT STATUS: ✅ SAFE TO SHARE AS IDENTITY VERIFICATION
            
            This public founder certificate contains no sensitive information and may be
            shared for identity verification purposes. The private key required for founder
            authority is stored separately in the confidential founder key document.
            """
            
            story.append(Paragraph(security_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            return True, "Founder public PDF generated successfully", public_pdf_path
            
        except Exception as e:
            return False, f"Error generating founder public PDF: {str(e)}", None
    
    def _generate_founder_private_pdf(self, founder_data: Dict[str, Any], key_info: Dict[str, Any], 
                                     founder_id: str) -> Tuple[bool, str, Optional[str]]:
        """Generate private founder key PDF"""
        try:
            private_pdf_path = str(self.private_pdfs_dir / f"{founder_id}_private_founder.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(private_pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'PrivateTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.darkred
            )
            
            warning_style = ParagraphStyle(
                'Warning',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=12,
                alignment=TA_CENTER,
                textColor=colors.red,
                fontName='Helvetica-Bold'
            )
            
            # Title with warnings
            story.append(Paragraph("🚨 CONFIDENTIAL FOUNDER KEY DOCUMENT 🚨", title_style))
            story.append(Paragraph("⚠️ MAXIMUM SECURITY - NEVER SHARE ⚠️", warning_style))
            story.append(Spacer(1, 20))
            
            # Founder key information
            story.append(Paragraph("🔑 FOUNDER PRIVATE KEY", styles['Heading2']))
            
            # Include the full private key
            key_text = f"""
FOUNDER ID: {founder_id}
KEY TYPE: Constitutional Founder Authority
USAGE: Single-use platform promotion

RSA PRIVATE KEY (2048-bit):
{key_info['private_key_pem']}

KEY FINGERPRINT: {key_info['key_fingerprint']}
BLOCKCHAIN ADDRESS: {key_info['blockchain_address']}
            """
            
            story.append(Paragraph('<pre>' + key_text + '</pre>', styles['Code']))
            story.append(Spacer(1, 20))
            
            # Usage instructions
            story.append(Paragraph("🎯 USAGE INSTRUCTIONS", styles['Heading2']))
            
            usage_text = """
            1. ACCOUNT REGISTRATION: Register normally on the Civic Engagement Platform
            2. FOUNDER PROMOTION: During registration, provide the complete private key above
            3. VALIDATION: System will validate key and grant founder authority
            4. SINGLE USE: This key becomes permanently unusable after first use
            5. SECURE STORAGE: Store this document in maximum security location
            """
            
            story.append(Paragraph(usage_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Critical security warnings
            story.append(Paragraph("🚨 CRITICAL SECURITY WARNINGS", styles['Heading2']))
            
            warning_text = """
            ❌ NEVER email, transmit, or store this document electronically
            ❌ NEVER share with anyone - this grants maximum platform authority
            ❌ NEVER photograph or screenshot this document
            ❌ NEVER store in cloud services or online locations
            
            ✅ DO store in secure, encrypted, offline location only
            ✅ DO create physical backup in separate secure location  
            ✅ DO destroy after successful founder registration
            ✅ DO contact security@civic-platform.org if compromised
            
            This key grants CONSTITUTIONAL FOUNDER AUTHORITY with maximum platform powers.
            Loss or theft could compromise the entire platform governance system.
            """
            
            story.append(Paragraph(warning_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            return True, "Founder private PDF generated successfully", private_pdf_path
            
        except Exception as e:
            return False, f"Error generating founder private PDF: {str(e)}", None
    
    def _generate_founder_qr_codes(self, founder_data: Dict[str, Any], key_info: Dict[str, Any], 
                                  founder_id: str) -> Tuple[bool, str, Dict[str, str]]:
        """Generate QR codes for founder"""
        try:
            if not QR_AVAILABLE:
                return False, "QR code generation not available", {}
            
            qr_paths = {}
            
            # Public QR (founder verification)
            public_qr_data = json.dumps({
                'type': 'founder_verification',
                'founder_id': founder_id,
                'fingerprint': key_info['key_fingerprint'],
                'blockchain_address': key_info['blockchain_address'],
                'authority': 'constitutional_founder'
            })
            
            public_qr = qrcode.QRCode(version=1, box_size=10, border=5)
            public_qr.add_data(public_qr_data)
            public_qr.make(fit=True)
            
            public_qr_path = str(self.qr_codes_dir / f"{founder_id}_public_qr.png")
            public_qr_img = public_qr.make_image(fill_color="black", back_color="white")
            public_qr_img.save(public_qr_path)
            qr_paths['public_qr'] = public_qr_path
            
            # Private QR (founder key data)
            private_qr_data = json.dumps({
                'type': 'founder_authority_key',
                'founder_id': founder_id,
                'key_fingerprint': key_info['key_fingerprint'],
                'blockchain_address': key_info['blockchain_address'],
                'created_at': key_info['created_at']
            })
            
            private_qr = qrcode.QRCode(version=1, box_size=10, border=5)
            private_qr.add_data(private_qr_data)
            private_qr.make(fit=True)
            
            private_qr_path = str(self.qr_codes_dir / f"{founder_id}_private_qr.png")
            private_qr_img = private_qr.make_image(fill_color="darkred", back_color="white")
            private_qr_img.save(private_qr_path)
            qr_paths['private_qr'] = private_qr_path
            
            return True, "Founder QR codes generated successfully", qr_paths
            
        except Exception as e:
            return False, f"Error generating founder QR codes: {str(e)}", {}