#!/usr/bin/env python3
"""
Simple PDF Generator for Contract Governance Guide
Creates a professional PDF using built-in libraries and simple formatting
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import textwrap

def create_simple_pdf():
    """Create a simple text-based PDF using basic HTML to PDF conversion."""
    
    # Read the README content
    readme_path = Path(__file__).parent / "README.md"
    guide_path = Path(__file__).parent / "civic_desktop" / "CONTRACT_GOVERNANCE_GUIDE.md"
    
    # Choose the source file
    if guide_path.exists():
        source_file = guide_path
    elif readme_path.exists():
        source_file = readme_path
    else:
        print("❌ No source file found. Please ensure README.md or CONTRACT_GOVERNANCE_GUIDE.md exists.")
        return False
    
    print(f"📖 Reading content from: {source_file}")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create HTML version for better formatting
    html_content = create_html_document(content, source_file.name)
    
    # Save HTML file
    html_path = Path(__file__).parent / "CONTRACT_GOVERNANCE_GUIDE.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML version created: {html_path}")
    
    # Create formatted text version
    text_content = create_formatted_text(content)
    text_path = Path(__file__).parent / "CONTRACT_GOVERNANCE_GUIDE.txt"
    
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print(f"✅ Text version created: {text_path}")
    
    # Try to create PDF using weasyprint if available
    try:
        import weasyprint
        pdf_path = Path(__file__).parent / "CONTRACT_GOVERNANCE_GUIDE.pdf"
        weasyprint.HTML(string=html_content).write_pdf(str(pdf_path))
        print(f"🎉 PDF created successfully: {pdf_path}")
        return True
    except ImportError:
        print("📄 weasyprint not available. Install with: pip install weasyprint")
        print("🌐 You can still use the HTML file in any browser and print to PDF!")
        return True

def create_html_document(markdown_content, filename):
    """Convert markdown content to a beautifully formatted HTML document."""
    
    # Clean up markdown formatting for HTML
    content = markdown_content.replace('**', '<strong>').replace('**', '</strong>')
    content = content.replace('*', '<em>').replace('*', '</em>')
    
    # Remove emojis for cleaner text
    emoji_replacements = {
        '🗳️': '[VOTE]', '🌟': '[STAR]', '🤔': '', '📱': '[MOBILE]',
        '🔒': '[SECURE]', '🌍': '[WORLD]', '⚖️': '[BALANCE]', '🏛️': '[GOVERNMENT]',
        '🗺️': '[MAP]', '🇺🇸': '[USA]', '🏘️': '[CITY]', '📊': '[CHART]',
        '🚀': '[ROCKET]', '📝': '[DOCUMENT]', '🎯': '[TARGET]', '🔄': '[REFRESH]',
        '🏆': '[TROPHY]', '✅': '[CHECK]', '📅': '[CALENDAR]', '📢': '[ANNOUNCE]',
        '🎉': '[CELEBRATE]', '🔗': '[LINK]', '🛡️': '[SHIELD]', '💪': '[STRONG]',
        '❓': '[QUESTION]', '📞': '[PHONE]', '📚': '[BOOKS]', '💬': '[CHAT]',
        '📧': '[EMAIL]', '📖': '[BOOK]', '🎥': '[VIDEO]', '💡': '[IDEA]',
        '🔮': '[CRYSTAL]', '🎊': '[CONFETTI]', '✨': '[SPARKLES]', '🔧': '[TOOLS]',
        '🌎': '[EARTH]', '📄': '[PAGE]', '🌐': '[WEB]', '📈': '[GROWTH]',
        '🎓': '[EDUCATION]'
    }
    
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Convert markdown headers to HTML
    lines = content.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            html_lines.append(f'<h1 class="main-title">{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2 class="section-title">{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3 class="subsection-title">{line[4:]}</h3>')
        elif line.startswith('- ') or line.startswith('* '):
            html_lines.append(f'<li>{line[2:]}</li>')
        elif line.startswith('```'):
            if 'example' in line.lower():
                html_lines.append('<div class="example-box">')
            else:
                html_lines.append('<pre class="code-block">')
        elif line == '```':
            html_lines.append('</pre>')
        elif line.startswith('**') and line.endswith('**'):
            html_lines.append(f'<p class="highlight">{line[2:-2]}</p>')
        elif line:
            html_lines.append(f'<p>{line}</p>')
        else:
            html_lines.append('<br>')
    
    html_body = '\n'.join(html_lines)
    
    # Create complete HTML document
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contract Governance Elections Guide</title>
        <style>
            body {{
                font-family: 'Georgia', 'Times New Roman', serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                color: #2c3e50;
                background-color: #ffffff;
            }}
            
            .main-title {{
                color: #1f4e79;
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 30px;
                border-bottom: 3px solid #2e75b6;
                padding-bottom: 20px;
            }}
            
            .section-title {{
                color: #2e75b6;
                font-size: 1.8em;
                margin-top: 40px;
                margin-bottom: 20px;
                border-left: 5px solid #70ad47;
                padding-left: 15px;
            }}
            
            .subsection-title {{
                color: #1f4e79;
                font-size: 1.4em;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: bold;
            }}
            
            p {{
                margin-bottom: 15px;
                text-align: justify;
                font-size: 1.1em;
            }}
            
            .highlight {{
                background-color: #e8f4f8;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2e75b6;
                font-weight: bold;
                margin: 20px 0;
            }}
            
            .example-box {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #dee2e6;
                margin: 20px 0;
                font-family: 'Courier New', monospace;
            }}
            
            .code-block {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-family: 'Courier New', monospace;
                overflow-x: auto;
            }}
            
            li {{
                margin-bottom: 8px;
                padding-left: 10px;
            }}
            
            ul {{
                margin: 15px 0;
                padding-left: 30px;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 60px;
                padding-top: 30px;
                border-top: 2px solid #2e75b6;
                font-style: italic;
                color: #7f8c8d;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            @media print {{
                body {{
                    font-size: 12pt;
                    line-height: 1.4;
                }}
                .main-title {{
                    font-size: 24pt;
                }}
                .section-title {{
                    font-size: 18pt;
                }}
                .subsection-title {{
                    font-size: 14pt;
                }}
            }}
        </style>
    </head>
    <body>
        {html_body}
        
        <div class="footer">
            <p>Contract Governance Elections Guide</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
            <p>Your Voice • Your Democracy • Your Future</p>
        </div>
    </body>
    </html>
    """

def create_formatted_text(markdown_content):
    """Create a well-formatted text version of the document."""
    
    lines = markdown_content.split('\n')
    formatted_lines = []
    
    # Add header
    formatted_lines.extend([
        "=" * 80,
        "CONTRACT GOVERNANCE ELECTIONS: COMPLETE GUIDE".center(80),
        "=" * 80,
        "",
        f"Generated: {datetime.now().strftime('%B %d, %Y')}".center(80),
        "",
        "=" * 80,
        ""
    ])
    
    for line in lines:
        line = line.strip()
        
        # Remove emojis
        emoji_chars = ['🗳️', '🌟', '🤔', '📱', '🔒', '🌍', '⚖️', '🏛️', '🗺️', '🇺🇸', 
                      '🏘️', '📊', '🚀', '📝', '🎯', '🔄', '🏆', '✅', '📅', '📢', 
                      '🎉', '🔗', '🛡️', '💪', '❓', '📞', '📚', '💬', '📧', '📖', 
                      '🎥', '💡', '🔮', '🎊', '✨', '🔧', '🌎', '📄', '🌐', '📈', '🎓']
        
        for emoji in emoji_chars:
            line = line.replace(emoji, '')
        
        # Clean up formatting
        line = line.replace('**', '').replace('*', '')
        
        if line.startswith('# '):
            # Main title
            title = line[2:].strip()
            formatted_lines.extend([
                "",
                "=" * 80,
                title.center(80),
                "=" * 80,
                ""
            ])
        elif line.startswith('## '):
            # Section title  
            title = line[3:].strip()
            formatted_lines.extend([
                "",
                "-" * 60,
                title.upper(),
                "-" * 60,
                ""
            ])
        elif line.startswith('### '):
            # Subsection title
            title = line[4:].strip()
            formatted_lines.extend([
                "",
                title.upper(),
                "~" * len(title),
                ""
            ])
        elif line.startswith('- ') or line.startswith('* '):
            # Bullet point
            bullet_text = line[2:].strip()
            wrapped = textwrap.fill(bullet_text, width=75, initial_indent='  • ', subsequent_indent='    ')
            formatted_lines.append(wrapped)
        elif line.startswith('```'):
            formatted_lines.append("\n" + "─" * 60)
        elif line == '```':
            formatted_lines.append("─" * 60 + "\n")
        elif line:
            # Regular paragraph
            wrapped = textwrap.fill(line, width=78)
            formatted_lines.append(wrapped)
            formatted_lines.append("")
        else:
            formatted_lines.append("")
    
    # Add footer
    formatted_lines.extend([
        "",
        "=" * 80,
        "END OF DOCUMENT",
        "=" * 80,
        "",
        "Your Voice • Your Democracy • Your Future".center(80),
        ""
    ])
    
    return '\n'.join(formatted_lines)

def main():
    """Main function to generate documentation files."""
    print("🚀 Generating Contract Governance Documentation...")
    print("=" * 60)
    
    try:
        success = create_simple_pdf()
        
        if success:
            print("\n🎉 Documentation Generation Complete!")
            print("=" * 60)
            print("📁 Files Created:")
            print("  • CONTRACT_GOVERNANCE_GUIDE.html (Web version)")
            print("  • CONTRACT_GOVERNANCE_GUIDE.txt (Text version)")
            print("  • CONTRACT_GOVERNANCE_GUIDE.pdf (if weasyprint installed)")
            print("\n💡 To create PDF:")
            print("  1. Open the HTML file in your browser")
            print("  2. Press Ctrl+P (or Cmd+P)")
            print("  3. Choose 'Save as PDF'")
            print("  4. Enjoy your professional documentation!")
            
        return 0
        
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())