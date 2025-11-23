#!/usr/bin/env python3
"""Combine all markdown reports in a date directory into a single PDF"""
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Add TeX to PATH if BasicTeX is installed
tex_bin = "/Library/TeX/texbin"
if os.path.exists(tex_bin) and tex_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{tex_bin}:{os.environ.get('PATH', '')}"

REPORTS_DIR = Path("/Users/ndamico/Agent/builder/reports")

def generate_cover_page_html(date_str):
    """Generate HTML for a professional cover page"""
    from datetime import datetime
    
    # Parse date and format nicely
    report_date = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = report_date.strftime('%B %d, %Y')
    
    cover_html = f"""
<div class="cover-page">
  <div class="cover-content">
    <h1 class="cover-title">D'amico Construction</h1>
    <h2 class="cover-subtitle">Morning Executive Report</h2>
    <div class="cover-date">{formatted_date}</div>
    <div class="cover-divider"></div>
    <div class="cover-footer">
      <p>Paving • Milling • Sitework</p>
    </div>
  </div>
</div>
"""
    return cover_html

def combine_reports_to_pdf(date_str=None):
    """Combine all markdown reports in a date directory into a single PDF"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    date_dir = REPORTS_DIR / date_str
    
    if not date_dir.exists():
        print(f"❌ Reports directory not found: {date_dir}")
        return False
    
    # Find all markdown files in the directory
    md_files = sorted(date_dir.glob("*.md"))
    
    if not md_files:
        print(f"⚠️  No markdown reports found in {date_dir}")
        return False
    
    # Order files: timesheet first, then email, then others
    ordered_files = []
    other_files = []
    
    for md_file in md_files:
        if "kimai" in md_file.name.lower():
            ordered_files.insert(0, md_file)  # Timesheet first
        elif "email" in md_file.name.lower():
            ordered_files.append(md_file)  # Email second
        else:
            other_files.append(md_file)
    
    ordered_files.extend(other_files)  # Other reports last
    
    if not ordered_files:
        print(f"⚠️  No reports to combine")
        return False
    
    # Output PDF path
    pdf_path = date_dir / f"daily_report_{date_str}.pdf"
    
    # Check if pandoc is available
    try:
        subprocess.run(['pandoc', '--version'], 
                      capture_output=True, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pandoc not found. Install with: brew install pandoc")
        print("   For PDF support, also install: brew install --cask basictex")
        return False
    
    print(f"📄 Combining {len(ordered_files)} report(s) into PDF...")
    for md_file in ordered_files:
        print(f"   - {md_file.name}")
    
    # Use HTML → PDF approach for better table border control
    # CSS file for styling
    css_file = Path(__file__).parent / 'pdf-styles.css'
    
    # Check for HTML to PDF engines (prefer Chrome, then weasyprint, then chromium)
    pdf_engine = None
    
    # Try Chrome first (most reliable on macOS)
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if Path(chrome_path).exists():
        pdf_engine = chrome_path
    
    # Try weasyprint (Python library - requires system libs)
    if not pdf_engine:
        try:
            import weasyprint
            # Test if it actually works (not just imported)
            pdf_engine = 'weasyprint'
        except (ImportError, OSError):
            pass
    
    # Try chromium/chromium-browser
    if not pdf_engine:
        for engine in ['chromium', 'chromium-browser']:
            result = subprocess.run(['which', engine], capture_output=True)
            if result.returncode == 0:
                pdf_engine = engine
                break
    
    # Generate HTML first (for HTML→PDF engines)
    html_path = None
    if pdf_engine and pdf_engine != 'xelatex':
        html_path = date_dir / '.combined_report.html'
        
        # First, generate the main HTML content
        # Get absolute path to CSS file for font references
        css_abs_path = css_file.resolve()
        css_dir = css_file.parent.resolve()
        
        html_cmd = ['pandoc'] + [str(f) for f in ordered_files] + [
            '-s',  # Standalone HTML
            '-t', 'html5',
            '--css', str(css_abs_path),
            '--toc',
            '--toc-depth=2',
            '--metadata', 'title=Daily Report',
            '--variable', 'papersize=letter',
            '-o', str(html_path)
        ]
        try:
            subprocess.run(html_cmd, check=True)
            
            # Read the generated HTML and prepend cover page
            html_content = html_path.read_text()
            
            # Get current date for first page header
            current_date = datetime.now().strftime('%B %d, %Y')
            
            # Inject CSS to set first page header to current date
            # Find </head> or <style> tag to inject custom CSS
            head_end = html_content.find('</head>')
            if head_end != -1:
                first_page_css = f"""
<style>
@page:first {{
  @top-center {{
    content: "{current_date}";
    font-size: 9pt;
    color: #666;
    font-family: "Berkeley Mono", monospace;
  }}
}}
</style>
"""
                html_content = html_content[:head_end] + first_page_css + html_content[head_end:]
            
            # Find where <body> starts and insert cover page
            body_start = html_content.find('<body>')
            if body_start != -1:
                body_end = html_content.find('>', body_start) + 1
                cover_html = generate_cover_page_html(date_str)
                # Insert cover page right after <body> tag
                html_content = (html_content[:body_end] + 
                              '\n' + cover_html + '\n' + 
                              html_content[body_end:])
            
            # Remove duplicate "Daily Report" heading that appears before TOC
            # Pandoc generates this from the title metadata
            # IMPORTANT: Only match headings that are NOT inside the cover-page div
            import re
            # Find TOC element
            toc_pos = html_content.find('id="TOC"')
            if toc_pos != -1:
                # Look backwards for heading tags before TOC
                # Only match headings that are NOT inside .cover-page div
                before_toc = html_content[:toc_pos]
                # Find the end of the cover-page div to exclude it from matching
                cover_page_end = before_toc.rfind('</div>')
                if cover_page_end != -1:
                    # Only search after the cover page ends
                    search_area = before_toc[cover_page_end:]
                else:
                    search_area = before_toc
                
                # Match h1 or h2 tags with "Daily Report" content (but not in cover-page)
                pattern = r'<h[12][^>]*>.*?Daily Report.*?</h[12]>'
                matches = list(re.finditer(pattern, search_area, re.IGNORECASE | re.DOTALL))
                if matches:
                    # Remove the last match (closest to TOC)
                    last_match = matches[-1]
                    # Adjust the match position to account for the offset
                    match_start = cover_page_end + last_match.start() if cover_page_end != -1 else last_match.start()
                    match_end = cover_page_end + last_match.end() if cover_page_end != -1 else last_match.end()
                    html_content = (html_content[:match_start] + 
                                  html_content[match_end:])
            
            # Add page break before Email Analysis Report
            # Find h1 with "Email Analysis" and add page break style
            import re
            email_h1_pattern = r'(<h1[^>]*>.*?Email Analysis.*?</h1>)'
            email_matches = list(re.finditer(email_h1_pattern, html_content, re.IGNORECASE | re.DOTALL))
            for match in email_matches:
                # Check if it already has a style attribute
                h1_tag = match.group(1)
                if 'style=' not in h1_tag:
                    # Add page break style
                    h1_tag_new = h1_tag.replace('<h1', '<h1 style="page-break-before: always; break-before: page;"')
                    html_content = html_content.replace(h1_tag, h1_tag_new, 1)
            
            # Page break before first report is handled by CSS rule
            # No need to add inline styles - CSS will handle it
            
            html_path.write_text(html_content)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating HTML: {e.stderr}")
            return False
    
    # Generate PDF based on available engine
    if pdf_engine == 'weasyprint':
        # HTML → PDF using weasyprint (Python library)
        try:
            from weasyprint import HTML
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            html_path.unlink()  # Delete temp HTML file
            print(f"✅ Combined PDF saved to: {pdf_path}")
            return True
        except Exception as e:
            if html_path and html_path.exists():
                html_path.unlink()
            print(f"❌ Error generating PDF with weasyprint: {e}")
            return False
        
    elif pdf_engine and ('Chrome' in pdf_engine or pdf_engine in ['chromium', 'chromium-browser']):
        # HTML → PDF using headless Chrome/Chromium with professional print settings
        cmd = [pdf_engine,
               '--headless',
               '--disable-gpu',
               '--no-pdf-header-footer',
               '--print-to-pdf=' + str(pdf_path),
               '--print-to-pdf-no-header',
               '--run-all-compositor-stages-before-draw',
               '--virtual-time-budget=5000',
               'file://' + str(html_path.absolute())]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            html_path.unlink()  # Delete temp HTML file
            print(f"✅ Combined PDF saved to: {pdf_path}")
            return True
        except subprocess.CalledProcessError as e:
            if html_path and html_path.exists():
                html_path.unlink()
            print(f"❌ Error generating PDF with Chrome: {e.stderr.decode() if e.stderr else str(e)}")
            return False
    else:
        # Fallback to LaTeX (original approach)
        if not pdf_engine:
            print("⚠️  No HTML→PDF engine found. Using LaTeX (table borders may be limited).")
            print("   Options for better table borders:")
            print("   1. Install Chrome (already installed? Check /Applications)")
            print("   2. Install weasyprint system libs: brew install pango gdk-pixbuf libffi")
            print("   3. Use Chromium: brew install --cask chromium")
        
        # Build pandoc command to combine all files
        cmd = ['pandoc']
        
        # Add all markdown files
        for md_file in ordered_files:
            cmd.append(str(md_file))
        
        header_file = date_dir / '.pandoc_header.tex'
        header_content = r"""
\usepackage{longtable}
\usepackage{array}
\usepackage{xcolor}

\setlength{\arrayrulewidth}{0.8pt}
\renewcommand{\arraystretch}{1.2}
"""
        header_file.write_text(header_content)
        
        cmd.extend([
            '-o', str(pdf_path),
            '--pdf-engine=xelatex',
            '--variable=geometry:margin=1in',
            '--variable=fontsize:11pt',
            '--variable=colorlinks:true',
            '-H', str(header_file),
            '--toc',
            '--toc-depth=2',
        ])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Combined PDF saved to: {pdf_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating PDF:")
            print(f"   {e.stderr}")
            # Try with pdflatex if xelatex fails
            if 'xelatex' in str(e.stderr).lower():
                print("\n   Trying with pdflatex instead...")
                cmd[cmd.index('--pdf-engine=xelatex')] = '--pdf-engine=pdflatex'
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"✅ Combined PDF saved to: {pdf_path}")
                    return True
                except subprocess.CalledProcessError as e2:
                    print(f"❌ Error: {e2.stderr}")
                    return False
            return False

if __name__ == '__main__':
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    success = combine_reports_to_pdf(date_str)
    sys.exit(0 if success else 1)

