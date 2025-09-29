#!/usr/bin/env python3
"""
PDF Generation Script for Contract Governance Guide

This script converts the Contract Governance Guide from markdown to a professional,
beautifully formatted PDF document suitable for distribution and presentation.

Dependencies:
- reportlab: For PDF generation
- markdown: For parsing markdown content
- Pillow: For image handling (if needed)

Installation:
    pip install reportlab markdown Pillow

Usage:
    python generate_governance_pdf.py

Output:
    CONTRACT_GOVERNANCE_GUIDE.pdf - Professional PDF document
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import Color, HexColor
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
        Table, TableStyle, Image, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    import markdown
except ImportError as e:
    print(f"Error: Required library not installed: {e}")
    print("\nTo install required dependencies, run:")
    print("pip install reportlab markdown Pillow")
    sys.exit(1)


class GovernancePDFGenerator:
    """Generate professional PDF documentation for the Contract Governance System."""
    
    def __init__(self, markdown_file: str, output_file: str):
        """
        Initialize the PDF generator.
        
        Args:
            markdown_file: Path to the markdown source file
            output_file: Path for the generated PDF file
        """
        self.markdown_file = Path(markdown_file)
        self.output_file = Path(output_file)
        
        # Color scheme - Professional blue theme
        self.primary_color = HexColor('#1f4e79')     # Deep blue
        self.secondary_color = HexColor('#2e75b6')   # Medium blue  
        self.accent_color = HexColor('#70ad47')      # Green accent
        self.text_color = HexColor('#2d2d2d')        # Dark gray
        self.light_bg = HexColor('#f8f9fa')          # Light background
        
        # Initialize styles
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Create custom paragraph styles for the PDF."""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            spaceAfter=30,
            spaceBefore=20,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=25,
            textColor=self.secondary_color,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=self.primary_color,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=4,
            textColor=self.text_color,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Bullet point style
        styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=2,
            leftIndent=20,
            bulletIndent=10,
            textColor=self.text_color,
            fontName='Helvetica'
        ))
        
        # Quote/highlight style
        styles.add(ParagraphStyle(
            name='CustomQuote',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            spaceBefore=15,
            leftIndent=30,
            rightIndent=30,
            textColor=self.primary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        return styles
    
    def _create_header_footer(self, canvas_obj, doc):
        """Create header and footer for each page."""
        canvas_obj.saveState()
        
        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(self.primary_color)
        canvas_obj.drawString(
            inch, 
            doc.pagesize[1] - 0.5 * inch, 
            "Contract Governance Elections Guide"
        )
        
        # Footer  
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.text_color)
        canvas_obj.drawRightString(
            doc.pagesize[0] - inch,
            0.5 * inch,
            f"Page {canvas_obj.getPageNumber()}"
        )
        
        canvas_obj.drawString(
            inch,
            0.5 * inch, 
            f"Generated: {datetime.now().strftime('%B %d, %Y')}"
        )
        
        canvas_obj.restoreState()
    
    def _parse_markdown_content(self):
        """Parse the markdown file and extract content sections."""
        if not self.markdown_file.exists():
            raise FileNotFoundError(f"Markdown file not found: {self.markdown_file}")
        
        with open(self.markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into sections for better processing
        sections = []
        current_section = {"title": "", "content": []}
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('# '):
                # Main title
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": line[2:].strip(),
                    "content": [],
                    "type": "main_title"
                }
                
            elif line.startswith('## '):
                # Section heading
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": line[3:].strip(),
                    "content": [],
                    "type": "section"
                }
                
            elif line.startswith('### '):
                # Subsection heading
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": line[4:].strip(),
                    "content": [],
                    "type": "subsection"
                }
                
            else:
                current_section["content"].append(line)
        
        # Add the last section
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
    
    def _clean_text(self, text):
        """Clean text for PDF generation, removing markdown formatting."""
        # Remove emoji and clean up formatting
        text = text.replace('🗳️', '[Vote]').replace('🌟', '[Star]')
        text = text.replace('🤔', '').replace('📱', '').replace('🔒', '')
        text = text.replace('🌍', '').replace('⚖️', '').replace('🏛️', '')
        text = text.replace('🗳️', '').replace('🌎', '').replace('📊', '')
        text = text.replace('🚀', '').replace('📝', '').replace('🎯', '')
        text = text.replace('🔄', '').replace('🏆', '').replace('✅', '• ')
        text = text.replace('📅', '').replace('📢', '').replace('🎉', '')
        text = text.replace('🔗', '').replace('🛡️', '').replace('💪', '')
        text = text.replace('❓', '').replace('📞', '').replace('📚', '')
        text = text.replace('💬', '').replace('📧', '').replace('📖', '')
        text = text.replace('🎥', '').replace('**', '').replace('*', '')
        
        # Clean up multiple spaces and newlines
        text = ' '.join(text.split())
        return text
    
    def _create_table_example(self, title, data):
        """Create a formatted table for election examples."""
        table_data = [['Attribute', 'Value']]
        for key, value in data.items():
            table_data.append([key, str(value)])
        
        table = Table(table_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return [
            Paragraph(title, self.styles['CustomHeading2']),
            table,
            Spacer(1, 12)
        ]
    
    def generate_pdf(self):
        """Generate the complete PDF document."""
        print(f"Generating PDF from {self.markdown_file}...")
        
        # Create document
        doc = SimpleDocTemplate(
            str(self.output_file),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Parse markdown content
        sections = self._parse_markdown_content()
        
        # Add title page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Add table of contents
        story.extend(self._create_table_of_contents(sections))
        story.append(PageBreak())
        
        # Process sections
        for section in sections:
            if section["type"] == "main_title":
                continue  # Skip main title, already in title page
            
            story.extend(self._process_section(section))
        
        # Add examples and data tables
        story.extend(self._create_examples_section())
        
        # Build PDF with custom header/footer
        doc.build(
            story, 
            onFirstPage=self._create_header_footer,
            onLaterPages=self._create_header_footer
        )
        
        print(f"✅ PDF generated successfully: {self.output_file}")
        return self.output_file
    
    def _create_title_page(self):
        """Create an attractive title page."""
        return [
            Spacer(1, 2*inch),
            Paragraph(
                "Contract Governance Elections", 
                self.styles['CustomTitle']
            ),
            Spacer(1, 0.5*inch),
            Paragraph(
                "Your Complete Guide to Digital Democracy", 
                self.styles['CustomSubtitle']
            ),
            Spacer(1, 1*inch),
            Paragraph(
                "From Local Communities to Global Governance:<br/>How You Can Make a Real Difference", 
                self.styles['CustomBody']
            ),
            Spacer(1, 2*inch),
            Paragraph(
                f"Published: {datetime.now().strftime('%B %d, %Y')}", 
                self.styles['CustomBody']
            )
        ]
    
    def _create_table_of_contents(self, sections):
        """Create a table of contents."""
        toc = [
            Paragraph("Table of Contents", self.styles['CustomTitle']),
            Spacer(1, 20)
        ]
        
        for i, section in enumerate(sections):
            if section["type"] in ["section", "subsection"]:
                title = self._clean_text(section["title"])
                if section["type"] == "section":
                    toc.append(Paragraph(f"{i}. {title}", self.styles['CustomHeading2']))
                else:
                    toc.append(Paragraph(f"    {title}", self.styles['CustomBody']))
                toc.append(Spacer(1, 6))
        
        return toc
    
    def _process_section(self, section):
        """Process a content section into PDF elements."""
        elements = []
        
        # Section title
        title = self._clean_text(section["title"])
        if section["type"] == "section":
            elements.append(Paragraph(title, self.styles['CustomSubtitle']))
        else:
            elements.append(Paragraph(title, self.styles['CustomHeading2']))
        
        elements.append(Spacer(1, 12))
        
        # Process content
        content_text = ""
        for line in section["content"]:
            if line.strip():
                if line.startswith('- ') or line.startswith('* '):
                    # Bullet point
                    if content_text:
                        elements.append(Paragraph(
                            self._clean_text(content_text), 
                            self.styles['CustomBody']
                        ))
                        content_text = ""
                    
                    bullet_text = self._clean_text(line[2:])
                    elements.append(Paragraph(
                        f"• {bullet_text}", 
                        self.styles['CustomBullet']
                    ))
                else:
                    content_text += f" {line}"
            else:
                if content_text:
                    elements.append(Paragraph(
                        self._clean_text(content_text), 
                        self.styles['CustomBody']
                    ))
                    elements.append(Spacer(1, 8))
                    content_text = ""
        
        # Add remaining content
        if content_text:
            elements.append(Paragraph(
                self._clean_text(content_text), 
                self.styles['CustomBody']
            ))
        
        elements.append(Spacer(1, 20))
        return elements
    
    def _create_examples_section(self):
        """Create examples and data tables section."""
        elements = [
            PageBreak(),
            Paragraph("Representation Examples", self.styles['CustomTitle']),
            Spacer(1, 20)
        ]
        
        # City example
        elements.extend(self._create_table_example(
            "Springfield, Illinois Example (200,000 people)",
            {
                "Contract Senators": "2",
                "Base Representatives": "2", 
                "Population Representatives": "0 (under 200K threshold)",
                "Total City Representatives": "4",
                "Election Trigger (1%)": "2,000 citizens",
                "Full Participation (50%)": "100,000 citizens"
            }
        ))
        
        # State example
        elements.extend(self._create_table_example(
            "Illinois State Example (12.6 million people)",
            {
                "Contract Senators": "2",
                "Base Representatives": "2",
                "Population Representatives": "25 (12.6M ÷ 500K)",
                "Total State Representatives": "27",
                "Electoral College": "Cities vote for candidates",
                "Term Length": "1 year (renewable)"
            }
        ))
        
        # Country example
        elements.extend(self._create_table_example(
            "United States Example (330 million people)",
            {
                "Contract Senators": "2", 
                "Base Representatives": "2",
                "Population Representatives": "330 (330M ÷ 1M)",
                "Total Country Representatives": "332",
                "Electoral College": "States vote for candidates",
                "Eligibility": "Former State Rep/Senator"
            }
        ))
        
        # World example
        elements.extend(self._create_table_example(
            "Global Example (8 billion people)",
            {
                "Contract Senators": "2",
                "Base Representatives": "2", 
                "Population Representatives": "2,000 (8B ÷ 4M)",
                "Total World Representatives": "2,002",
                "Electoral College": "Countries vote for candidates", 
                "Eligibility": "Former Country Rep/Senator"
            }
        ))
        
        return elements


def main():
    """Main function to generate the PDF."""
    # Define file paths
    script_dir = Path(__file__).parent
    markdown_file = script_dir / "CONTRACT_GOVERNANCE_GUIDE.md"
    pdf_file = script_dir / "CONTRACT_GOVERNANCE_GUIDE.pdf"
    
    # Check if markdown file exists
    if not markdown_file.exists():
        print(f"❌ Error: Markdown file not found: {markdown_file}")
        print("\nPlease ensure CONTRACT_GOVERNANCE_GUIDE.md exists in the same directory.")
        return 1
    
    try:
        # Generate PDF
        generator = GovernancePDFGenerator(str(markdown_file), str(pdf_file))
        output_path = generator.generate_pdf()
        
        print(f"\n🎉 Success! PDF generated at: {output_path}")
        print(f"📄 File size: {pdf_file.stat().st_size / 1024:.1f} KB")
        print("\n📖 Your professional Contract Governance Guide is ready!")
        print("   Share it with friends, family, and anyone interested in digital democracy!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure all dependencies are installed: pip install reportlab markdown Pillow")
        print("2. Check that the markdown file is properly formatted")
        print("3. Verify you have write permissions in the output directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())