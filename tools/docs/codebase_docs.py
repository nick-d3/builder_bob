#!/usr/bin/env python3
"""
Codebase Source Code Viewer

This tool outputs all source code in the repository so you can see
the entire project directly. Excludes reports/ directory.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Get the repository root
REPO_ROOT = Path(__file__).parent.parent

def should_include_file(filepath):
    """Determine if a file should be included in output"""
    # Exclude reports directory
    if "reports" in str(filepath):
        return False
    
    # Exclude hidden files and directories
    if any(part.startswith('.') for part in filepath.parts):
        # But include .cursor/mcp.json if it exists
        if '.cursor' in filepath.parts and filepath.name == 'mcp.json':
            return True
        if filepath.name.startswith('.'):
            return False
    
    # Include common code/documentation files
    extensions = ['.py', '.md', '.json', '.yaml', '.yml', '.txt', '.sh', '.bash']
    if filepath.suffix in extensions:
        return True
    
    # Include files without extension that might be scripts
    if not filepath.suffix and filepath.is_file():
        return True
    
    return False

def read_file_safely(filepath):
    """Safely read a file, returning content or error message"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return f"[Binary file - cannot display]\n"
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
    }
    return type_map.get(ext, 'text')

def generate_codebase_output():
    """Generate output with all source code"""
    output = []
    output.append("=" * 80)
    output.append("CODEBASE SOURCE CODE")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 80)
    output.append("")
    output.append("This output contains all source code files in the repository.")
    output.append("Reports directory is excluded.")
    output.append("")
    output.append("=" * 80)
    output.append("")
    
    # Get all files to include
    files_to_include = []
    
    # Add README
    readme = REPO_ROOT / "README.md"
    if readme.exists():
        files_to_include.append(readme)
    
    # Add all Python files in tools/ (recursively)
    tools_dir = REPO_ROOT / "tools"
    if tools_dir.exists():
        for py_file in sorted(tools_dir.rglob("*.py")):
            files_to_include.append(py_file)
    
    # Add all markdown files in workflows/
    workflows_dir = REPO_ROOT / "workflows"
    if workflows_dir.exists():
        for md_file in sorted(workflows_dir.glob("*.md")):
            files_to_include.append(md_file)
    
    # Add any other files in root (excluding reports)
    for item in sorted(REPO_ROOT.iterdir()):
        if item.is_file() and should_include_file(item):
            if item not in files_to_include:
                files_to_include.append(item)
    
    # Add .cursor/mcp.json if it exists
    mcp_json = REPO_ROOT / ".cursor" / "mcp.json"
    if mcp_json.exists():
        files_to_include.append(mcp_json)
    
    # Output each file
    for filepath in files_to_include:
        rel_path = filepath.relative_to(REPO_ROOT)
        output.append("")
        output.append("=" * 80)
        output.append(f"FILE: {rel_path}")
        output.append("=" * 80)
        output.append("")
        
        content = read_file_safely(filepath)
        file_type = get_file_type(filepath)
        
        # Output with code block if it's code
        if file_type in ['python', 'bash', 'json', 'yaml']:
            output.append(f"```{file_type}")
            output.append(content)
            output.append("```")
        else:
            # For markdown and text, output directly
            output.append(content)
        
        output.append("")
        output.append("")
    
    output.append("=" * 80)
    output.append("END OF CODEBASE")
    output.append("=" * 80)
    
    return "\n".join(output)

def main():
    """Main entry point"""
    try:
        output = generate_codebase_output()
        print(output)
    except Exception as e:
        print(f"Error generating codebase output: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
