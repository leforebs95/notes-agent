#!/usr/bin/env python3
"""
Syntax checker script for the notes-agent project
Compiles all Python files to check for syntax errors
"""

import py_compile
import sys
from pathlib import Path

def check_file_syntax(file_path: Path) -> bool:
    """Check syntax of a single Python file"""
    try:
        py_compile.compile(file_path, doraise=True)
        print(f"✅ {file_path}")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ {file_path}: {e}")
        return False

def main():
    """Check syntax of all Python files in the project"""
    project_root = Path(__file__).parent
    python_files = list(project_root.glob("*.py"))
    
    print("Checking syntax of Python files...")
    print("-" * 40)
    
    failed_files = []
    for file_path in python_files:
        if not check_file_syntax(file_path):
            failed_files.append(file_path)
    
    print("-" * 40)
    if failed_files:
        print(f"❌ {len(failed_files)} files failed syntax check:")
        for file_path in failed_files:
            print(f"  - {file_path}")
        sys.exit(1)
    else:
        print(f"✅ All {len(python_files)} Python files passed syntax check")

if __name__ == "__main__":
    main()