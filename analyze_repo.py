#!/usr/bin/env python3
"""
Simple script to analyze and fix Git repository filename issues on Windows.
"""

import subprocess
import urllib.parse
import re
import os

def sanitize_filename(filename):
    """Sanitize a filename for Windows compatibility."""
    # Replace invalid Windows characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '=', '&']
    sanitized = filename
    
    for char in invalid_chars:
        if char == '&':
            sanitized = sanitized.replace(char, '_and_')
        else:
            sanitized = sanitized.replace(char, '_')
    
    # Handle URL encoding
    if '%' in sanitized and any(c in sanitized for c in ['2F', '3A']):
        try:
            decoded = urllib.parse.unquote(sanitized)
            # Re-sanitize after decoding
            for char in invalid_chars:
                if char == '&':
                    decoded = decoded.replace(char, '_and_')
                else:
                    decoded = decoded.replace(char, '_')
            sanitized = decoded
        except:
            pass
    
    # Clean up multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('. ')
    
    # Truncate if too long
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized

def main():
    print("Git Repository Filename Analyzer")
    print("=================================")
    
    # Get list of files from remote
    try:
        result = subprocess.run([
            'git', 'ls-tree', '-r', '--name-only', 'origin/main'
        ], capture_output=True, text=True, check=True)
        all_files = result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        print("Could not get file list. Make sure remote is configured:")
        print("   git remote add origin https://github.com/we-are-pixel/weathermakers.git")
        return
    
    # Find problematic files
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '=', '&']
    problematic_files = []
    
    for file_path in all_files:
        if any(char in file_path for char in invalid_chars):
            problematic_files.append(file_path)
    
    print(f"Total files: {len(all_files)}")
    print(f"Problematic files: {len(problematic_files)}")
    
    if not problematic_files:
        print("No problematic files found!")
        return
    
    # Show examples
    print("\nExamples of problematic files:")
    for file_path in problematic_files[:10]:
        print(f"  {file_path}")
    if len(problematic_files) > 10:
        print(f"  ... and {len(problematic_files) - 10} more")
    
    # Create rename mapping
    print("\nCreating rename mapping...")
    rename_mapping = {}
    used_names = set()
    
    for original_path in problematic_files:
        path_parts = original_path.split('/')
        sanitized_parts = [sanitize_filename(part) for part in path_parts]
        sanitized_path = '/'.join(sanitized_parts)
        
        # Ensure unique names
        base_sanitized = sanitized_path
        counter = 1
        while sanitized_path in used_names:
            name, ext = os.path.splitext(base_sanitized)
            sanitized_path = f"{name}_{counter}{ext}"
            counter += 1
        
        rename_mapping[original_path] = sanitized_path
        used_names.add(sanitized_path)
    
    # Save mapping
    with open('rename_mapping.txt', 'w', encoding='utf-8') as f:
        f.write("Original -> Sanitized\n")
        f.write("=" * 50 + "\n")
        for original, sanitized in rename_mapping.items():
            f.write(f"{original} -> {sanitized}\n")
    
    print("Saved rename mapping to rename_mapping.txt")
    
    # Show examples
    print("\nExample renames:")
    count = 0
    for original, sanitized in rename_mapping.items():
        if count < 5:
            print(f"  {original} -> {sanitized}")
            count += 1
    
    # Create git-filter-repo script
    print("\nCreating fix script...")
    
    with open('fix_repository.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('# Script to fix repository using git-filter-repo\n\n')
        f.write('echo "Cloning repository..."\n')
        f.write('git clone --bare https://github.com/we-are-pixel/weathermakers.git weathermakers-temp\n')
        f.write('cd weathermakers-temp\n\n')
        f.write('echo "Applying filename fixes..."\n')
        
        for original, sanitized in rename_mapping.items():
            # Escape single quotes for bash
            original_escaped = original.replace("'", "'\"'\"'")
            sanitized_escaped = sanitized.replace("'", "'\"'\"'")
            f.write(f"git filter-repo --path-rename '{original_escaped}':'{sanitized_escaped}' --force\n")
        
        f.write('\necho "Repository fixed! Clone with:"\n')
        f.write('echo "git clone $(pwd) ../weathermakers-clean"\n')
    
    # Make script executable on Unix systems
    try:
        os.chmod('fix_repository.sh', 0o755)
    except:
        pass
    
    print("Created fix_repository.sh")
    
    # Create instructions
    instructions = f"""INSTRUCTIONS FOR FIXING THE REPOSITORY
=========================================

Problem: The repository contains {len(problematic_files)} files with invalid Windows characters.

SOLUTION:

1. Install git-filter-repo:
   pip install git-filter-repo

2. Run the fix script:
   bash fix_repository.sh

3. Clone the cleaned repository:
   git clone weathermakers-temp weathermakers-clean

The script will:
- Clone the repository as a bare repo
- Apply {len(rename_mapping)} filename fixes
- Create a clean repository you can use on Windows

See rename_mapping.txt for all file renames.
"""
    
    with open('INSTRUCTIONS.txt', 'w') as f:
        f.write(instructions)
    
    print("Created INSTRUCTIONS.txt")
    
    print("\nAnalysis complete!")
    print("Next steps:")
    print("   1. pip install git-filter-repo")
    print("   2. bash fix_repository.sh")

if __name__ == "__main__":
    main()