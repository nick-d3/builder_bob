#!/usr/bin/env python3
"""
Read All Files Script

Reads every file in the repository and outputs them in an organized format.
Includes reports, source code, workflows, and configuration files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Get the repository root
REPO_ROOT = Path(__file__).parent.parent.parent

def should_read_file(filepath):
    """Determine if a file should be read"""
    # Exclude hidden files/directories (except .cursor/mcp.json)
    if any(part.startswith('.') for part in filepath.parts):
        if '.cursor' in filepath.parts and filepath.name == 'mcp.json':
            return True
        if filepath.name.startswith('.'):
            return False
    
    # Exclude common binary/ignored files
    excluded_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.tar', '.gz'}
    if filepath.suffix.lower() in excluded_extensions:
        return False
    
    # Exclude common system files
    excluded_names = {'.DS_Store', 'Thumbs.db', '__pycache__', '.git'}
    if filepath.name in excluded_names or '__pycache__' in filepath.parts:
        return False
    
    return True

def read_file_safely(filepath):
    """Safely read a file, returning content or error message"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return f"[Binary file - cannot display as text]\n"
    except PermissionError:
        return f"[Permission denied - cannot read file]\n"
    except Exception as e:
        return f"[Error reading file: {e}]\n"

def get_file_type(filepath):
    """Determine file type for syntax highlighting"""
    ext = filepath.suffix.lower()
    type_map = {
        '.py': 'python',
        '.md': 'markdown',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.sh': 'bash',
        '.bash': 'bash',
        '.css': 'css',
        '.html': 'html',
        '.txt': 'text',
        '.justfile': 'bash',  # justfile syntax is similar to bash
    }
    return type_map.get(ext, 'text')

def collect_all_files():
    """Collect all files to read"""
    files_to_read = []
    
    # Walk through all directories
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.cursor']
        
        for file in files:
            filepath = Path(root) / file
            if should_read_file(filepath):
                files_to_read.append(filepath)
    
    # Sort by path for consistent output
    files_to_read.sort(key=lambda p: str(p))
    return files_to_read

def generate_output(include_reports=True):
    """Generate output with all files"""
    output = []
    output.append("=" * 80)
    output.append("COMPLETE CODEBASE - ALL FILES")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 80)
    output.append("")
    
    if include_reports:
        output.append("This output contains ALL files in the repository, including reports.")
    else:
        output.append("This output contains source code files (reports excluded).")
    output.append("")
    output.append("=" * 80)
    output.append("")
    
    files_to_read = collect_all_files()
    
    # Filter out reports if requested
    if not include_reports:
        files_to_read = [f for f in files_to_read if 'reports' not in str(f)]
    
    # Group files by directory for better organization
    files_by_dir = {}
    for filepath in files_to_read:
        rel_path = filepath.relative_to(REPO_ROOT)
        dir_path = rel_path.parent
        if dir_path not in files_by_dir:
            files_by_dir[dir_path] = []
        files_by_dir[dir_path].append((rel_path, filepath))
    
    # Output files grouped by directory
    for dir_path in sorted(files_by_dir.keys()):
        output.append("")
        output.append("=" * 80)
        output.append(f"DIRECTORY: {dir_path}")
        output.append("=" * 80)
        output.append("")
        
        for rel_path, filepath in sorted(files_by_dir[dir_path]):
            output.append("")
            output.append("-" * 80)
            output.append(f"FILE: {rel_path}")
            output.append("-" * 80)
            output.append("")
            
            content = read_file_safely(filepath)
            file_type = get_file_type(filepath)
            
            # Output with code block if it's code
            if file_type in ['python', 'bash', 'json', 'yaml', 'css', 'html']:
                output.append(f"```{file_type}")
                output.append(content)
                output.append("```")
            else:
                # For markdown and text, output directly
                output.append(content)
            
            output.append("")
    
    output.append("=" * 80)
    output.append("END OF CODEBASE")
    output.append("=" * 80)
    
    return "\n".join(output)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Read all files in the repository')
    parser.add_argument('--no-reports', action='store_true', 
                       help='Exclude reports directory from output')
    parser.add_argument('--output', type=str, 
                       help='Output file path (default: print to stdout)')
    
    args = parser.parse_args()
    
    try:
        include_reports = not args.no_reports
        output = generate_output(include_reports=include_reports)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            print(f"✅ Output written to: {output_path}", file=sys.stderr)
        else:
            print(output)
    except Exception as e:
        print(f"Error generating output: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


