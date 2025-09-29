#!/usr/bin/env python3
"""
Comprehensive PDF Generator for Contract Governance Documentation

Creates professional PDF documents from all governance guides and places them
in the documents folder for easy distribution and reference.

This script generates:
1. Contract_Governance_Complete_Guide.pdf - Main comprehensive guide
2. Contract_Governance_Quick_Reference.pdf - Executive summary
3. Four_Tier_Election_System.pdf - Technical election documentation
4. Getting_Started_Guide.pdf - New user onboarding guide

Dependencies:
- weasyprint: pip install weasyprint
- Pillow: pip install Pillow
- reportlab: pip install reportlab (fallback)

Usage: python generate_pdf_documents.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import textwrap

# Try to import advanced PDF libraries
try:
    import weasyprint
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠️  WeasyPrint not available. Install with: pip install weasyprint")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab not available. Install with: pip install reportlab")


class GovernancePDFGenerator:
    """Generate professional PDF documentation for Contract Governance system."""
    
    def __init__(self, output_dir: str):
        """Initialize the PDF generator with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Color scheme
        self.primary_color = "#1f4e79"
        self.secondary_color = "#2e75b6"
        self.accent_color = "#70ad47"
        self.light_bg = "#f8f9fa"
        
    def generate_all_documents(self):
        """Generate all PDF documents."""
        print("🚀 Generating Contract Governance PDF Documentation...")
        print("=" * 70)
        
        documents = [
            ("Contract_Governance_Complete_Guide.pdf", self._create_complete_guide),
            ("Contract_Governance_Quick_Reference.pdf", self._create_quick_reference),
            ("Four_Tier_Election_System.pdf", self._create_election_system_guide),
            ("Getting_Started_Guide.pdf", self._create_getting_started_guide),
        ]
        
        generated_files = []
        
        for filename, generator_func in documents:
            try:
                print(f"📄 Generating {filename}...")
                content = generator_func()
                
                if WEASYPRINT_AVAILABLE:
                    self._generate_pdf_weasyprint(content, filename)
                else:
                    self._generate_pdf_basic(content, filename)
                
                generated_files.append(filename)
                print(f"✅ Created: {filename}")
                
            except Exception as e:
                print(f"❌ Error generating {filename}: {e}")
        
        print("\n" + "=" * 70)
        print(f"🎉 PDF Generation Complete! Generated {len(generated_files)} documents")
        print(f"📁 Location: {self.output_dir}")
        
        for filename in generated_files:
            file_path = self.output_dir / filename
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   • {filename} ({size_mb:.1f} MB)")
        
        return generated_files
    
    def _generate_pdf_weasyprint(self, html_content: str, filename: str):
        """Generate PDF using WeasyPrint (high quality)."""
        css_content = self._get_pdf_css()
        output_path = self.output_dir / filename
        
        HTML(string=html_content).write_pdf(
            str(output_path),
            stylesheets=[CSS(string=css_content)]
        )
    
    def _generate_pdf_basic(self, html_content: str, filename: str):
        """Generate PDF using basic HTML to text conversion."""
        # Strip HTML tags and create formatted text
        import re
        
        # Simple HTML tag removal
        text_content = re.sub('<[^<]+?>', '', html_content)
        text_content = text_content.replace('&nbsp;', ' ')
        text_content = text_content.replace('&lt;', '<')
        text_content = text_content.replace('&gt;', '>')
        text_content = text_content.replace('&amp;', '&')
        
        # Save as formatted text file (fallback)
        output_path = self.output_dir / filename.replace('.pdf', '.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    def _get_pdf_css(self):
        """Get CSS styles optimized for PDF generation."""
        return f"""
        @page {{
            size: A4;
            margin: 1in 0.8in;
            @top-center {{
                content: "Contract Governance Elections Guide";
                font-size: 10pt;
                color: {self.primary_color};
            }}
            @bottom-right {{
                content: "Page " counter(page);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.5;
            color: #2c3e50;
            margin: 0;
            padding: 0;
        }}
        
        .main-title {{
            color: {self.primary_color};
            font-size: 24pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 30pt;
            border-bottom: 3pt solid {self.secondary_color};
            padding-bottom: 15pt;
        }}
        
        .section-title {{
            color: {self.secondary_color};
            font-size: 16pt;
            font-weight: bold;
            margin-top: 25pt;
            margin-bottom: 15pt;
            border-left: 4pt solid {self.accent_color};
            padding-left: 12pt;
            page-break-after: avoid;
        }}
        
        .subsection-title {{
            color: {self.primary_color};
            font-size: 13pt;
            font-weight: bold;
            margin-top: 20pt;
            margin-bottom: 10pt;
            page-break-after: avoid;
        }}
        
        .highlight-box {{
            background-color: {self.light_bg};
            border-left: 4pt solid {self.secondary_color};
            padding: 12pt;
            margin: 15pt 0;
            border-radius: 5pt;
            page-break-inside: avoid;
        }}
        
        .example-box {{
            background-color: #f4f4f4;
            border: 1pt solid #ddd;
            padding: 12pt;
            margin: 15pt 0;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            border-radius: 5pt;
            page-break-inside: avoid;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150pt, 1fr));
            gap: 10pt;
            margin: 15pt 0;
        }}
        
        .stat-box {{
            background-color: {self.light_bg};
            padding: 12pt;
            text-align: center;
            border-radius: 5pt;
            border-left: 3pt solid {self.secondary_color};
        }}
        
        .stat-number {{
            font-size: 18pt;
            font-weight: bold;
            color: {self.primary_color};
            display: block;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        ul, ol {{
            margin: 10pt 0;
            padding-left: 25pt;
        }}
        
        li {{
            margin-bottom: 6pt;
            line-height: 1.4;
        }}
        
        p {{
            margin-bottom: 8pt;
            text-align: justify;
        }}
        
        .toc {{
            background-color: {self.light_bg};
            padding: 20pt;
            margin: 20pt 0;
            border-radius: 8pt;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30pt;
            padding-top: 20pt;
            border-top: 2pt solid {self.secondary_color};
            font-style: italic;
            color: #666;
        }}
        """
    
    def _create_complete_guide(self):
        """Create the complete governance guide."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contract Governance Complete Guide</title>
        </head>
        <body>
            <h1 class="main-title">Contract Governance Elections<br>Complete Implementation Guide</h1>
            
            <div class="highlight-box">
                <p><strong>Your Comprehensive Guide to Four-Tier Digital Democracy</strong></p>
                <p>From Local Communities to Global Governance: How Every Member Can Make a Real Difference</p>
                <p>Published: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="toc">
                <h2>Table of Contents</h2>
                <ol>
                    <li>System Overview & Philosophy</li>
                    <li>The Four Pillars of Democratic Participation</li>
                    <li>Mathematical Representation Formulas</li>
                    <li>Election Process: Step-by-Step Guide</li>
                    <li>Democratic Safeguards & Protections</li>
                    <li>Getting Started: Your Democratic Journey</li>
                    <li>Real-World Examples & Case Studies</li>
                    <li>Frequently Asked Questions</li>
                </ol>
            </div>
            
            <div class="page-break"></div>
            
            <h2 class="section-title">1. System Overview & Philosophy</h2>
            
            <p>The Contract Governance System represents a revolutionary approach to digital democracy, operating on four interconnected levels designed to ensure every member's voice is heard from local communities to global decisions.</p>
            
            <div class="highlight-box">
                <p><strong>Core Principle:</strong> This is NOT traditional government. Our Contract Governance system is completely separate from traditional government structures. These are platform governance roles that manage how our digital democracy system operates, makes decisions, and serves its community members.</p>
            </div>
            
            <h3 class="subsection-title">Key Benefits</h3>
            <ul>
                <li><strong>Easy Participation:</strong> Vote and engage through our user-friendly desktop application</li>
                <li><strong>Secure & Transparent:</strong> Every vote and decision recorded on blockchain for complete transparency</li>
                <li><strong>From Local to Global:</strong> Your voice matters at every level of decision-making</li>
                <li><strong>Fair Representation:</strong> Population-based scaling ensures everyone gets heard</li>
            </ul>
            
            <h2 class="section-title">2. The Four Pillars of Democratic Participation</h2>
            
            <h3 class="subsection-title">Level 1: City Contract Elections - Where Democracy Begins</h3>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">2+2</span>
                    <div>Base Representatives</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">100K</span>
                    <div>People per Additional Rep</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">1%</span>
                    <div>Initial Election Trigger</div>
                </div>
            </div>
            
            <div class="example-box">
                <strong>Springfield, Illinois Example (200,000 people)</strong><br>
                Contract Senators: 2<br>
                Contract Representatives: 2 (base) + 0 (under threshold) = 2<br>
                Total Representatives: 4<br>
                Election Trigger: 2,000 members (1%) / 100,000 members (50%)
            </div>
            
            <h3 class="subsection-title">Level 2: State Contract Elections - Regional Voice Amplification</h3>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">2+2</span>
                    <div>Base Representatives</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">500K</span>
                    <div>People per Additional Rep</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Electoral College</span>
                    <div>Cities Vote for Candidates</div>
                </div>
            </div>
            
            <div class="example-box">
                <strong>Illinois Example (12.6 million people)</strong><br>
                Contract Senators: 2<br>
                Contract Representatives: 2 (base) + 25 (12.6M ÷ 500K) = 27<br>
                Total Representatives: 29<br>
                Electoral Process: Cities cast votes based on population
            </div>
            
            <h3 class="subsection-title">Level 3: Country Contract Elections - National Democratic Leadership</h3>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">2+2</span>
                    <div>Base Representatives</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">1M</span>
                    <div>People per Additional Rep</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Electoral College</span>
                    <div>States Vote for Candidates</div>
                </div>
            </div>
            
            <div class="example-box">
                <strong>United States Example (330 million people)</strong><br>
                Contract Senators: 2<br>
                Contract Representatives: 2 (base) + 330 (330M ÷ 1M) = 332<br>
                Total Representatives: 334<br>
                Electoral Process: States cast votes based on representation
            </div>
            
            <h3 class="subsection-title">Level 4: World Contract Elections - Global Democratic Governance</h3>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">2+2</span>
                    <div>Base Representatives</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">4M</span>
                    <div>People per Additional Rep</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Electoral College</span>
                    <div>Countries Vote for Candidates</div>
                </div>
            </div>
            
            <div class="example-box">
                <strong>Earth Example (8 billion people)</strong><br>
                Contract Senators: 2<br>
                Contract Representatives: 2 (base) + 2,000 (8B ÷ 4M) = 2,002<br>
                Total Representatives: 2,004<br>
                Electoral Process: Countries cast votes based on representation
            </div>
            
            <div class="page-break"></div>
            
            <h2 class="section-title">3. Mathematical Representation Formulas</h2>
            
            <p>Our representation system uses carefully calculated formulas to ensure fair representation while maintaining manageable governance structures:</p>
            
            <div class="example-box">
                <strong>City Level Formula:</strong><br>
                Total Reps = 2 Senators + max(2, 2 + floor((Population - 200,000) / 100,000))<br><br>
                
                <strong>State Level Formula:</strong><br>
                Total Reps = 2 Senators + max(2, 2 + floor(Population / 500,000))<br><br>
                
                <strong>Country Level Formula:</strong><br>
                Total Reps = 2 Senators + max(2, 2 + floor(Population / 1,000,000))<br><br>
                
                <strong>World Level Formula:</strong><br>
                Total Reps = 2 Senators + max(2, 2 + floor(Population / 4,000,000))
            </div>
            
            <h2 class="section-title">4. Election Process: Step-by-Step Guide</h2>
            
            <h3 class="subsection-title">Phase 1: Registration & Eligibility (30 days)</h3>
            
            <div class="highlight-box">
                <p><strong>City Level Candidates:</strong></p>
                <ul>
                    <li>Requirements: Active platform member</li>
                    <li>Process: Submit platform statement and campaign materials</li>
                    <li>Review: Community verification and platform approval</li>
                    <li>Campaigning: Begin voter outreach and engagement</li>
                </ul>
            </div>
            
            <div class="highlight-box">
                <p><strong>Higher Level Candidates:</strong></p>
                <ul>
                    <li>Requirements: Previous experience at lower level</li>
                    <li>Process: Submit advanced platform statement</li>
                    <li>Review: Eligibility verification and experience validation</li>
                    <li>Campaigning: Multi-jurisdiction outreach and coalition building</li>
                </ul>
            </div>
            
            <h3 class="subsection-title">Phase 2: Campaign Period (60 days)</h3>
            <p>Candidates engage in platform presentation, community engagement, coalition building, and transparent campaigning with all activities recorded on blockchain.</p>
            
            <h3 class="subsection-title">Phase 3: Voting Period (7 days)</h3>
            <p>Secure, transparent voting through our platform with real-time results tracking and electoral college processes at higher levels.</p>
            
            <h3 class="subsection-title">Phase 4: Results & Installation</h3>
            <p>Transparent results, peaceful transition, and new representatives begin their 1-year terms with full accountability.</p>
            
            <h2 class="section-title">5. Democratic Safeguards & Protections</h2>
            
            <h3 class="subsection-title">Term Limits & Power Rotation</h3>
            <ul>
                <li><strong>Term Length:</strong> 1 year (responsive governance)</li>
                <li><strong>Maximum Terms:</strong> 4 consecutive terms</li>
                <li><strong>Cooling Off:</strong> 1 term wait after maximum</li>
                <li><strong>Fresh Leadership:</strong> Regular new opportunities</li>
            </ul>
            
            <h3 class="subsection-title">Checks & Balances System</h3>
            <ul>
                <li><strong>Bicameral Structure:</strong> Representatives + Senators</li>
                <li><strong>Electoral College:</strong> Geographic protection</li>
                <li><strong>Experience Requirements:</strong> Progressive advancement</li>
                <li><strong>Constitutional Review:</strong> Elder oversight</li>
            </ul>
            
            <div class="footer">
                <p><strong>Contract Governance Elections - Complete Guide</strong></p>
                <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
                <p><em>"Democracy is participation in power, and the cornerstone of that participation is the vote."</em></p>
            </div>
        </body>
        </html>
        """
    
    def _create_quick_reference(self):
        """Create a quick reference guide."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Contract Governance Quick Reference</title>
        </head>
        <body>
            <h1 class="main-title">Contract Governance Elections<br>Quick Reference Guide</h1>
            
            <div class="highlight-box">
                <p><strong>Fast Facts About Four-Tier Digital Democracy</strong></p>
                <p>Essential information for new members and quick reference</p>
                <p>Published: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <h2 class="section-title">Four Levels at a Glance</h2>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">City</span>
                    <div>Local Democracy<br>Anyone Can Run</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">State</span>
                    <div>Regional Voice<br>City Experience Required</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Country</span>
                    <div>National Leadership<br>State Experience Required</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">World</span>
                    <div>Global Governance<br>Country Experience Required</div>
                </div>
            </div>
            
            <h2 class="section-title">Representation Quick Calculator</h2>
            
            <div class="example-box">
                <strong>City:</strong> 2 Senators + (2 + extra reps for every 100K above 200K)<br>
                <strong>State:</strong> 2 Senators + (2 + 1 per 500K people)<br>
                <strong>Country:</strong> 2 Senators + (2 + 1 per 1M people)<br>
                <strong>World:</strong> 2 Senators + (2 + 1 per 4M people)
            </div>
            
            <h2 class="section-title">Election Timeline</h2>
            
            <div class="highlight-box">
                <ul>
                    <li><strong>Registration:</strong> 30 days (candidates register)</li>
                    <li><strong>Campaign:</strong> 60 days (public engagement)</li>
                    <li><strong>Voting:</strong> 7 days (secure elections)</li>
                    <li><strong>Installation:</strong> Immediate (new terms begin)</li>
                </ul>
            </div>
            
            <h2 class="section-title">Key Safeguards</h2>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">1 Year</span>
                    <div>Term Length</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">4 Terms</span>
                    <div>Maximum Consecutive</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Blockchain</span>
                    <div>Transparent Records</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Electoral College</span>
                    <div>Geographic Balance</div>
                </div>
            </div>
            
            <h2 class="section-title">Getting Started</h2>
            
            <div class="highlight-box">
                <ol>
                    <li><strong>Join Platform:</strong> Download app and register</li>
                    <li><strong>Learn System:</strong> Complete civic education</li>
                    <li><strong>Participate:</strong> Vote in elections</li>
                    <li><strong>Consider Leadership:</strong> Run for city office</li>
                </ol>
            </div>
            
            <h2 class="section-title">Common Questions</h2>
            
            <div class="example-box">
                <strong>Q: Is this a replacement for my government?</strong><br>
                A: No! This is separate platform governance. You keep all regular rights.<br><br>
                
                <strong>Q: Can anyone really run for office?</strong><br>
                A: Yes at city level! Higher levels require progressive experience.<br><br>
                
                <strong>Q: How secure is my vote?</strong><br>
                A: Bank-level cryptographic security with blockchain verification.
            </div>
            
            <div class="footer">
                <p><strong>Contract Governance Elections - Quick Reference</strong></p>
                <p>For complete information, see the Full Implementation Guide</p>
                <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </body>
        </html>
        """
    
    def _create_election_system_guide(self):
        """Create technical election system documentation."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Four-Tier Election System Technical Guide</title>
        </head>
        <body>
            <h1 class="main-title">Four-Tier Election System<br>Technical Implementation Guide</h1>
            
            <div class="highlight-box">
                <p><strong>Detailed Technical Documentation</strong></p>
                <p>Mathematical formulas, election mechanics, and system architecture</p>
                <p>Published: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <h2 class="section-title">Population Scaling Mathematics</h2>
            
            <h3 class="subsection-title">City Level Calculations</h3>
            <div class="example-box">
                def calculate_city_representation(population):<br>
                &nbsp;&nbsp;&nbsp;&nbsp;senators = 2<br>
                &nbsp;&nbsp;&nbsp;&nbsp;base_reps = 2<br>
                &nbsp;&nbsp;&nbsp;&nbsp;if population > 200000:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;extra_reps = (population - 200000) // 100000<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;total_reps = base_reps + extra_reps<br>
                &nbsp;&nbsp;&nbsp;&nbsp;else:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;total_reps = base_reps<br>
                &nbsp;&nbsp;&nbsp;&nbsp;return senators, total_reps
            </div>
            
            <h3 class="subsection-title">State Level Calculations</h3>
            <div class="example-box">
                def calculate_state_representation(population):<br>
                &nbsp;&nbsp;&nbsp;&nbsp;senators = 2<br>
                &nbsp;&nbsp;&nbsp;&nbsp;representatives = max(2, 2 + population // 500000)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;return senators, representatives
            </div>
            
            <h3 class="subsection-title">Country Level Calculations</h3>
            <div class="example-box">
                def calculate_country_representation(population):<br>
                &nbsp;&nbsp;&nbsp;&nbsp;senators = 2<br>
                &nbsp;&nbsp;&nbsp;&nbsp;representatives = max(2, 2 + population // 1000000)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;return senators, representatives
            </div>
            
            <h3 class="subsection-title">World Level Calculations</h3>
            <div class="example-box">
                def calculate_world_representation(population):<br>
                &nbsp;&nbsp;&nbsp;&nbsp;senators = 2<br>
                &nbsp;&nbsp;&nbsp;&nbsp;representatives = max(2, 2 + population // 4000000)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;return senators, representatives
            </div>
            
            <h2 class="section-title">Electoral College Mathematics</h2>
            
            <h3 class="subsection-title">State Elections (Cities Vote)</h3>
            <div class="example-box">
                def calculate_city_electoral_weight(city_population, state_population):<br>
                &nbsp;&nbsp;&nbsp;&nbsp;# Cities get electoral votes proportional to representation<br>
                &nbsp;&nbsp;&nbsp;&nbsp;city_senators, city_reps = calculate_city_representation(city_population)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;total_city_representation = city_senators + city_reps<br>
                &nbsp;&nbsp;&nbsp;&nbsp;return total_city_representation
            </div>
            
            <h2 class="section-title">Election Triggers & Thresholds</h2>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">1%</span>
                    <div>Initial Election Trigger<br>First democratic milestone</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">50%</span>
                    <div>Ongoing Elections<br>Full participation threshold</div>
                </div>
            </div>
            
            <h3 class="subsection-title">Trigger Calculation Examples</h3>
            
            <div class="example-box">
                <strong>Springfield, IL (200,000 people):</strong><br>
                First Election: 2,000 members (1%)<br>
                Regular Elections: 100,000 members (50%)<br><br>
                
                <strong>Chicago, IL (2.7 million people):</strong><br>
                First Election: 27,000 members (1%)<br>
                Regular Elections: 1,350,000 members (50%)<br><br>
                
                <strong>Illinois State (12.6 million people):</strong><br>
                Triggered when 1% of cities have representatives<br>
                Regular when 50% of cities participate
            </div>
            
            <h2 class="section-title">Term Limits & Rotation System</h2>
            
            <div class="highlight-box">
                <ul>
                    <li><strong>Term Duration:</strong> Exactly 1 year from installation date</li>
                    <li><strong>Maximum Service:</strong> 4 consecutive terms (4 years)</li>
                    <li><strong>Mandatory Break:</strong> 1 full term before re-eligibility</li>
                    <li><strong>Experience Ladder:</strong> Must serve lower level before advancing</li>
                </ul>
            </div>
            
            <h2 class="section-title">Blockchain Integration</h2>
            
            <h3 class="subsection-title">Election Data Recording</h3>
            <div class="example-box">
                election_data = {<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"election_id": unique_identifier,<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"level": "city|state|country|world",<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"jurisdiction": "Springfield, IL",<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"candidates": [candidate_list],<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"votes": encrypted_vote_data,<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"results": final_tallies,<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"timestamp": election_completion_time<br>
                }
            </div>
            
            <div class="footer">
                <p><strong>Four-Tier Election System - Technical Guide</strong></p>
                <p>For implementation details, see the complete system documentation</p>
                <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </body>
        </html>
        """
    
    def _create_getting_started_guide(self):
        """Create new user onboarding guide."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Getting Started Guide</title>
        </head>
        <body>
            <h1 class="main-title">Getting Started Guide<br>Your Journey to Digital Democracy</h1>
            
            <div class="highlight-box">
                <p><strong>New Member Onboarding</strong></p>
                <p>Everything you need to know to participate in Contract Governance</p>
                <p>Published: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
            
            <h2 class="section-title">Welcome to Contract Governance!</h2>
            
            <p>You're about to join a revolutionary digital democracy system that gives you real power to influence decisions from your local community to global issues. This guide will walk you through everything you need to know.</p>
            
            <h2 class="section-title">Step 1: Understanding the System</h2>
            
            <div class="highlight-box">
                <p><strong>What is Contract Governance?</strong></p>
                <p>It's a four-tier digital democracy system that's completely separate from traditional government. You participate as a Contract Member with rights to vote, debate, and even run for office at multiple levels.</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">City</span>
                    <div>Your Local Voice<br>Start Here!</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">State</span>
                    <div>Regional Influence<br>Gain Experience</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Country</span>
                    <div>National Impact<br>Build Leadership</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">World</span>
                    <div>Global Change<br>Ultimate Goal</div>
                </div>
            </div>
            
            <h2 class="section-title">Step 2: Your Rights as a Contract Member</h2>
            
            <div class="highlight-box">
                <h3>Your Democratic Powers:</h3>
                <ul>
                    <li><strong>Vote in Elections:</strong> Choose representatives at all levels</li>
                    <li><strong>Participate in Debates:</strong> Share your views on important issues</li>
                    <li><strong>Run for Office:</strong> Start at city level, advance through experience</li>
                    <li><strong>Appeal Decisions:</strong> Challenge unfair treatment through due process</li>
                    <li><strong>Propose Changes:</strong> Submit ideas for platform improvements</li>
                </ul>
            </div>
            
            <h2 class="section-title">Step 3: How Elections Work</h2>
            
            <h3 class="subsection-title">City Elections - Your Starting Point</h3>
            <div class="example-box">
                <strong>Who Can Run:</strong> Any registered Contract Member<br>
                <strong>Who Votes:</strong> All members in your city<br>
                <strong>When:</strong> When 1% of city population joins (first) or 50% participate (ongoing)<br>
                <strong>Term:</strong> 1 year, renewable up to 4 consecutive terms
            </div>
            
            <h3 class="subsection-title">Higher Level Elections</h3>
            <div class="example-box">
                <strong>State Level:</strong> Must have city experience, cities vote via electoral college<br>
                <strong>Country Level:</strong> Must have state experience, states vote via electoral college<br>
                <strong>World Level:</strong> Must have country experience, countries vote via electoral college
            </div>
            
            <h2 class="section-title">Step 4: Getting Involved Today</h2>
            
            <div class="highlight-box">
                <h3>Immediate Actions You Can Take:</h3>
                <ol>
                    <li><strong>Explore the Platform:</strong> Familiarize yourself with all features</li>
                    <li><strong>Find Your Representatives:</strong> See who currently represents your city/state/country</li>
                    <li><strong>Join Debates:</strong> Participate in discussions on issues you care about</li>
                    <li><strong>Follow Elections:</strong> Watch upcoming elections and learn about candidates</li>
                    <li><strong>Consider Running:</strong> Think about running for city office when you're ready</li>
                </ol>
            </div>
            
            <h2 class="section-title">Step 5: Building Your Democratic Career</h2>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-number">Volunteer</span>
                    <div>Help campaigns you believe in</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Learn</span>
                    <div>Complete civic education modules</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Engage</span>
                    <div>Participate actively in community</div>
                </div>
                <div class="stat-box">
                    <span class="stat-number">Lead</span>
                    <div>Run for office when ready</div>
                </div>
            </div>
            
            <h2 class="section-title">Step 6: Understanding Safeguards</h2>
            
            <div class="highlight-box">
                <h3>Your Protections:</h3>
                <ul>
                    <li><strong>Term Limits:</strong> No one can accumulate too much power</li>
                    <li><strong>Electoral College:</strong> Small communities get fair representation</li>
                    <li><strong>Blockchain Transparency:</strong> All votes and decisions are public</li>
                    <li><strong>Appeal Process:</strong> Challenge unfair treatment</li>
                    <li><strong>Constitutional Review:</strong> Elder oversight prevents abuse</li>
                </ul>
            </div>
            
            <h2 class="section-title">Frequently Asked Questions</h2>
            
            <div class="example-box">
                <strong>Q: How much time does participation require?</strong><br>
                A: As little or as much as you want! Voting takes minutes, running for office is more involved.<br><br>
                
                <strong>Q: What if I make a mistake?</strong><br>
                A: The system is forgiving. You can learn as you go, and there are safeguards in place.<br><br>
                
                <strong>Q: Can I really make a difference?</strong><br>
                A: Absolutely! The system is designed so every member's voice matters at every level.
            </div>
            
            <h2 class="section-title">Your Next Steps</h2>
            
            <div class="highlight-box">
                <p><strong>Ready to Begin?</strong></p>
                <ol>
                    <li>Complete your platform registration if you haven't already</li>
                    <li>Explore the four governance levels</li>
                    <li>Find and connect with your local representatives</li>
                    <li>Participate in your first debate or discussion</li>
                    <li>Vote in the next election in your area</li>
                </ol>
                <p><strong>Welcome to your democracy!</strong></p>
            </div>
            
            <div class="footer">
                <p><strong>Getting Started Guide - Contract Governance Elections</strong></p>
                <p>Your journey to meaningful democratic participation begins now</p>
                <p>Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            </div>
        </body>
        </html>
        """


def main():
    """Main function to generate all PDF documents."""
    print("🚀 Starting Contract Governance PDF Generation...")
    
    # Set up paths
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent / "documents"
    
    # Create PDF generator
    generator = GovernancePDFGenerator(str(docs_dir))
    
    try:
        # Generate all documents
        generated_files = generator.generate_all_documents()
        
        if generated_files:
            print(f"\n🎉 Success! Generated {len(generated_files)} documents")
            print(f"📁 Location: {docs_dir}")
            print("\n💡 Tip: If you have WeasyPrint installed (pip install weasyprint),")
            print("   you'll get high-quality PDF files. Otherwise, formatted text files are created.")
            
            return 0
        else:
            print("❌ No documents were generated")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())