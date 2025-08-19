#!/usr/bin/env python3
"""
Script to fix invalid Windows filenames in a Git repository.
This script handles files with characters like ? and = that are invalid on Windows.
"""

import os
import subprocess
import re
import urllib.parse
from pathlib import Path

def sanitize_filename(filename):
    """
    Sanitize a filename by replacing invalid Windows characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename safe for Windows
    """
    # Characters that are invalid in Windows filenames
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    
    # Replace invalid characters
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Handle special cases for URL-like filenames
    if '=' in sanitized:
        sanitized = sanitized.replace('=', '_')
    
    # Handle ampersands
    if '&' in sanitized:
        sanitized = sanitized.replace('&', '_and_')
    
    # URL decode if it looks like encoded content
    if '%2F' in sanitized or '%3A' in sanitized:
        try:
            decoded = urllib.parse.unquote(sanitized)
            # Re-sanitize after decoding
            for char in invalid_chars + ['=', '&']:
                decoded = decoded.replace(char, '_')
            sanitized = decoded
        except:
            pass
    
    # Remove consecutive underscores and trailing periods/spaces
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('. ')
    
    # Ensure filename isn't too long (Windows has 255 char limit)
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized

def get_problematic_files():
    """
    Get list of files with invalid Windows characters from Git.
    
    Returns:
        list: List of problematic file paths
    """
    try:
        # Get all files in the remote repository
        result = subprocess.run([
            'git', 'ls-tree', '-r', '--name-only', 'origin/main'
        ], capture_output=True, text=True, check=True)
        
        files = result.stdout.strip().split('\n')
        problematic = []
        
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '=', '&']
        
        for file_path in files:
            if any(char in file_path for char in invalid_chars):
                problematic.append(file_path)
        
        return problematic
    except subprocess.CalledProcessError as e:
        print(f"Error getting file list: {e}")
        return []

def create_rename_mapping(problematic_files):
    """
    Create a mapping of original to sanitized filenames.
    
    Args:
        problematic_files (list): List of problematic file paths
        
    Returns:
        dict: Mapping of original -> sanitized paths
    """
    mapping = {}
    
    for original_path in problematic_files:
        path_parts = original_path.split('/')
        sanitized_parts = []
        
        for part in path_parts:
            sanitized_part = sanitize_filename(part)
            sanitized_parts.append(sanitized_part)
        
        sanitized_path = '/'.join(sanitized_parts)
        
        # Avoid conflicts by ensuring unique names
        base_sanitized = sanitized_path
        counter = 1
        while sanitized_path in mapping.values():
            name, ext = os.path.splitext(base_sanitized)
            sanitized_path = f"{name}_{counter}{ext}"
            counter += 1
        
        mapping[original_path] = sanitized_path
    
    return mapping

def create_filter_branch_script(rename_mapping):
    """
    Create a git filter-branch script to rename files.
    
    Args:
        rename_mapping (dict): Mapping of original -> sanitized paths
    """
    script_content = '''#!/bin/bash
# Git filter-branch script to rename problematic files

'''
    
    for original, sanitized in rename_mapping.items():
        # Escape paths for shell
        original_escaped = original.replace("'", "'\"'\"'")
        sanitized_escaped = sanitized.replace("'", "'\"'\"'")
        
        script_content += f"""
if [ -f '{original_escaped}' ]; then
    mkdir -p "$(dirname '{sanitized_escaped}')"
    git mv '{original_escaped}' '{sanitized_escaped}' 2>/dev/null || true
fi
"""
    
    with open('rename_files.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('rename_files.sh', 0o755)
    print("Created rename_files.sh script")

def main():
    """Main function to orchestrate the filename fixing process."""
    print("🔍 Analyzing problematic filenames...")
    
    # Get problematic files
    problematic_files = get_problematic_files()
    
    if not problematic_files:
        print("✅ No problematic files found!")
        return
    
    print(f"📁 Found {len(problematic_files)} problematic files")
    
    # Show first few examples
    print("\n📋 Examples of problematic files:")
    for file_path in problematic_files[:10]:
        print(f"  - {file_path}")
    if len(problematic_files) > 10:
        print(f"  ... and {len(problematic_files) - 10} more")
    
    # Create rename mapping
    print("\n🔄 Creating rename mapping...")
    rename_mapping = create_rename_mapping(problematic_files)
    
    # Show mapping examples
    print("\n📝 Example renames:")
    count = 0
    for original, sanitized in rename_mapping.items():
        if count < 5:
            print(f"  {original} -> {sanitized}")
            count += 1
        else:
            break
    
    # Save mapping to file
    with open('rename_mapping.txt', 'w') as f:
        f.write("Original -> Sanitized\n")
        f.write("=" * 50 + "\n")
        for original, sanitized in rename_mapping.items():
            f.write(f"{original} -> {sanitized}\n")
    
    print(f"\n💾 Saved complete mapping to rename_mapping.txt")
    
    # Provide instructions
    print("\n🚀 Next steps:")
    print("1. Review the rename_mapping.txt file")
    print("2. Run the following commands to apply the fixes:")
    print("   git clone --bare https://github.com/we-are-pixel/weathermakers.git temp-repo")
    print("   cd temp-repo")
    print("   # Apply renames using git filter-repo (recommended) or manual process")
    print("   # Then push to a new clean repository")
    
    print("\n⚠️  Alternative approach:")
    print("Consider using 'git filter-repo' tool for safer history rewriting:")
    print("pip install git-filter-repo")

if __name__ == "__main__":
    main()