#!/usr/bin/env python3
"""
Convert individual project markdown reports to PDF and combine into one file
"""
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add TeX to PATH if BasicTeX is installed
tex_bin = "/Library/TeX/texbin"
if os.path.exists(tex_bin) and tex_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{tex_bin}:{os.environ.get('PATH', '')}"

REPORTS_DIR = Path("/Users/ndamico/Agent/builder/reports")


def check_pandoc():
    """Check if pandoc is available"""
    try:
        subprocess.run(['pandoc', '--version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pandoc not found. Install with: brew install pandoc")
        return False


def find_pdf_engine():
    """Find available PDF engine"""
    # Try Chrome first (most reliable on macOS)
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if Path(chrome_path).exists():
        return chrome_path
    
    # Try weasyprint
    try:
        import weasyprint
        return 'weasyprint'
    except (ImportError, OSError):
        pass
    
    # Try chromium
    for engine in ['chromium', 'chromium-browser']:
        result = subprocess.run(['which', engine], capture_output=True)
        if result.returncode == 0:
            return engine
    
    return None


def markdown_to_pdf(md_file, pdf_file, pdf_engine, css_file=None):
    """Convert a single markdown file to PDF"""
    # Generate HTML first
    html_file = md_file.parent / f".{md_file.stem}.html"
    
    cmd = ['pandoc', str(md_file), '-s', '-t', 'html5']
    if css_file and css_file.exists():
        cmd.extend(['--css', str(css_file)])
    cmd.extend(['-o', str(html_file)])
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {md_file.name} to HTML: {e.stderr.decode()}")
        return False
    
    # Convert HTML to PDF
    if pdf_engine == 'weasyprint':
        try:
            from weasyprint import HTML
            HTML(filename=str(html_file)).write_pdf(str(pdf_file))
            html_file.unlink()
            return True
        except Exception as e:
            print(f"❌ Error converting {md_file.name} to PDF with weasyprint: {e}")
            html_file.unlink()
            return False
    
    elif pdf_engine and ('Chrome' in pdf_engine or pdf_engine in ['chromium', 'chromium-browser']):
        cmd = [pdf_engine,
               '--headless',
               '--disable-gpu',
               '--no-pdf-header-footer',
               '--print-to-pdf=' + str(pdf_file),
               '--print-to-pdf-no-header',
               '--run-all-compositor-stages-before-draw',
               '--virtual-time-budget=5000',
               'file://' + str(html_file.absolute())]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            html_file.unlink()
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error converting {md_file.name} to PDF with Chrome: {e.stderr.decode() if e.stderr else str(e)}")
            html_file.unlink()
            return False
    else:
        # Fallback to LaTeX
        cmd = ['pandoc', str(md_file), '-o', str(pdf_file),
               '--pdf-engine=xelatex',
               '--variable=geometry:margin=1in',
               '--variable=fontsize:11pt']
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error converting {md_file.name} to PDF: {e.stderr.decode() if e.stderr else str(e)}")
            return False


def combine_pdfs(pdf_files, output_file):
    """Combine multiple PDF files into one"""
    # Try PyPDF2 first
    try:
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        for pdf_file in pdf_files:
            if pdf_file.exists():
                merger.append(str(pdf_file))
        merger.write(str(output_file))
        merger.close()
        return True
    except ImportError:
        pass
    
    # Try pdfunite (poppler-utils)
    try:
        cmd = ['pdfunite'] + [str(f) for f in pdf_files if f.exists()] + [str(output_file)]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try gs (ghostscript)
    try:
        cmd = ['gs', '-dBATCH', '-dNOPAUSE', '-q', '-sDEVICE=pdfwrite',
               f'-sOutputFile={output_file}'] + [str(f) for f in pdf_files if f.exists()]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("❌ No PDF merging tool found. Install one of:")
    print("   - PyPDF2: pip install PyPDF2")
    print("   - poppler-utils: brew install poppler")
    print("   - ghostscript: brew install ghostscript")
    return False


def combine_project_reports_pdf(date_str=None):
    """Convert all project markdown reports to PDF and combine"""
    if date_str is None:
        date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    project_reports_dir = REPORTS_DIR / today_str / f"project_reports_{date_str}"
    
    if not project_reports_dir.exists():
        print(f"❌ Project reports directory not found: {project_reports_dir}")
        return False
    
    # Find all markdown files (excluding README.md)
    md_files = sorted([f for f in project_reports_dir.glob("*.md") if f.name != "README.md"])
    
    if not md_files:
        print(f"⚠️  No project markdown files found in {project_reports_dir}")
        return False
    
    print(f"📄 Found {len(md_files)} project report(s) to convert...")
    
    # Check dependencies
    if not check_pandoc():
        return False
    
    pdf_engine = find_pdf_engine()
    if not pdf_engine:
        print("⚠️  No HTML→PDF engine found. Will use LaTeX (table borders may be limited).")
    
    # CSS file for styling
    css_file = Path(__file__).parent / 'pdf-styles.css'
    
    # Convert each markdown file to PDF
    pdf_files = []
    for md_file in md_files:
        pdf_file = project_reports_dir / f"{md_file.stem}.pdf"
        print(f"   Converting {md_file.name}...")
        
        if markdown_to_pdf(md_file, pdf_file, pdf_engine, css_file):
            pdf_files.append(pdf_file)
            print(f"   ✅ {pdf_file.name}")
        else:
            print(f"   ❌ Failed to convert {md_file.name}")
    
    if not pdf_files:
        print("❌ No PDFs were successfully created")
        return False
    
    # Combine all PDFs
    output_pdf = project_reports_dir / f"all_projects_{date_str}.pdf"
    print(f"\n📚 Combining {len(pdf_files)} PDF(s) into one file...")
    
    if combine_pdfs(pdf_files, output_pdf):
        print(f"✅ Combined PDF saved to: {output_pdf}")
        
        # Optionally clean up individual PDFs (comment out if you want to keep them)
        # for pdf_file in pdf_files:
        #     pdf_file.unlink()
        #     print(f"   Deleted {pdf_file.name}")
        
        return True
    else:
        print("❌ Failed to combine PDFs")
        return False


if __name__ == '__main__':
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    success = combine_project_reports_pdf(date_str)
    sys.exit(0 if success else 1)

