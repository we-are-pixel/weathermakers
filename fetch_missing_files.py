#!/usr/bin/env python3
"""
Script to fetch missing files with problematic names from GitHub repository.
Uses GitHub API to download files that couldn't be pulled due to Windows filename restrictions.
"""

import requests
import os
import urllib.parse
from pathlib import Path
import base64

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
    import re
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('. ')
    
    # Truncate if too long
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized

def get_github_file_content(repo_owner, repo_name, file_path, branch='main'):
    """Download file content from GitHub API."""
    # URL encode the file path for the API
    encoded_path = urllib.parse.quote(file_path, safe='/')
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{encoded_path}?ref={branch}"
    
    print(f"Fetching: {file_path}")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('encoding') == 'base64':
            content = base64.b64decode(data['content'])
            return content
        else:
            return data['content'].encode('utf-8')
    else:
        print(f"Failed to fetch {file_path}: {response.status_code}")
        return None

def load_rename_mapping():
    """Load the rename mapping from our previous analysis."""
    mapping = {}
    try:
        with open('rename_mapping.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[2:]:  # Skip header lines
                if ' -> ' in line:
                    original, sanitized = line.strip().split(' -> ')
                    mapping[original] = sanitized
    except FileNotFoundError:
        print("rename_mapping.txt not found. Please run analyze_repo.py first.")
        return {}
    
    return mapping

def main():
    print("Fetching missing files from GitHub repository...")
    
    # Load our rename mapping
    mapping = load_rename_mapping()
    if not mapping:
        return
    
    repo_owner = "we-are-pixel"
    repo_name = "weathermakers"
    
    downloaded_count = 0
    failed_count = 0
    
    for original_path, sanitized_path in mapping.items():
        # Check if the sanitized file already exists
        if os.path.exists(sanitized_path):
            print(f"Already exists: {sanitized_path}")
            continue
        
        # Download the original file from GitHub
        content = get_github_file_content(repo_owner, repo_name, original_path)
        
        if content is not None:
            # Create directory if needed
            sanitized_dir = os.path.dirname(sanitized_path)
            if sanitized_dir:
                os.makedirs(sanitized_dir, exist_ok=True)
            
            # Write the file with the sanitized name
            try:
                with open(sanitized_path, 'wb') as f:
                    f.write(content)
                print(f"Downloaded: {original_path} -> {sanitized_path}")
                downloaded_count += 1
            except Exception as e:
                print(f"Failed to write {sanitized_path}: {e}")
                failed_count += 1
        else:
            print(f"Failed to download: {original_path}")
            failed_count += 1
    
    print(f"\nSummary:")
    print(f"Downloaded: {downloaded_count} files")
    print(f"Failed: {failed_count} files")
    print(f"Total problematic files: {len(mapping)}")

if __name__ == "__main__":
    main()