#!/usr/bin/env python3
"""
Script to clean up blog filenames by extracting canonical URLs from HTML files
and renaming them to proper paths.
"""

import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse


def extract_canonical_url(html_file):
    """Extract canonical URL from HTML file."""
    try:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # First try og:url (more reliable for these files)
        og_url_match = re.search(r'<meta property=["\']og:url["\'] content=["\']([^"\']+)["\']', content)
        if og_url_match:
            og_url = og_url_match.group(1)
            # Check if it's a valid URL (not encoded)
            if 'index.html%3Fp=' not in og_url:
                return og_url
        
        # Fallback: look for canonical URL in meta tags
        canonical_match = re.search(r'<link rel=["\']canonical["\'] href=["\']([^"\']+)["\']', content)
        if canonical_match:
            canonical_url = canonical_match.group(1)
            # Skip malformed encoded URLs
            if 'index.html%3Fp=' not in canonical_url:
                return canonical_url
            
        return None
    except Exception as e:
        print(f"Error reading {html_file}: {e}")
        return None


def url_to_filepath(url, blog_root):
    """Convert a canonical URL to a file path relative to blog root."""
    try:
        parsed = urlparse(url)
        path = parsed.path
        
        # Remove /blog/ prefix if present
        if path.startswith('/blog/'):
            path = path[6:]  # Remove '/blog/'
        elif path.startswith('/'):
            path = path[1:]  # Remove leading '/'
        
        # Handle special cases
        if not path or path == '/':
            return 'index.html'
        
        # If path doesn't end with .html, add index.html
        if not path.endswith('.html') and not path.endswith('/'):
            path = path + '/index.html'
        elif path.endswith('/'):
            path = path + 'index.html'
        
        return path
    except Exception as e:
        print(f"Error converting URL {url}: {e}")
        return None


def create_directory_structure(filepath, blog_root):
    """Create the directory structure for the target file."""
    full_path = blog_root / filepath
    directory = full_path.parent
    directory.mkdir(parents=True, exist_ok=True)
    return full_path


def main(dry_run=True):
    blog_root = Path("D:/Dropbox/Weathermakers/blog")
    
    if not blog_root.exists():
        print(f"Blog directory not found: {blog_root}")
        return
    
    # Find all files matching the pattern
    pattern_files = list(blog_root.glob("index.html_p_*.html"))
    
    if not pattern_files:
        print("No files matching pattern 'index.html_p_*.html' found")
        return
    
    print(f"Found {len(pattern_files)} files to process")
    
    # Track rename operations
    rename_operations = []
    failed_operations = []
    
    for html_file in pattern_files:
        print(f"\nProcessing: {html_file.name}")
        
        # Extract canonical URL
        canonical_url = extract_canonical_url(html_file)
        if not canonical_url:
            print(f"  ERROR: Could not extract canonical URL from {html_file.name}")
            failed_operations.append(html_file.name)
            continue
        
        print(f"  Canonical URL: {canonical_url}")
        
        # Convert URL to file path
        target_path = url_to_filepath(canonical_url, blog_root)
        if not target_path:
            print(f"  ERROR: Could not convert URL to file path")
            failed_operations.append(html_file.name)
            continue
        
        target_full_path = blog_root / target_path
        print(f"  Target path: {target_path}")
        
        # Check if target already exists
        if target_full_path.exists():
            print(f"  WARNING: Target already exists: {target_full_path}")
            # You might want to handle this case differently
            continue
        
        # Create directory structure
        try:
            create_directory_structure(target_path, blog_root)
            rename_operations.append((html_file, target_full_path, target_path))
            print(f"  SUCCESS: Ready to rename")
        except Exception as e:
            print(f"  ERROR: Error creating directory structure: {e}")
            failed_operations.append(html_file.name)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Files to rename: {len(rename_operations)}")
    print(f"Failed to process: {len(failed_operations)}")
    
    if failed_operations:
        print(f"\nFailed files:")
        for failed in failed_operations:
            print(f"  - {failed}")
    
    # Show planned operations
    if rename_operations:
        print(f"\nPlanned rename operations:")
        for source, target, target_path in rename_operations:
            print(f"  {source.name} -> {target_path}")
        
        if not dry_run:
            print("\nPerforming renames...")
            for source, target, target_path in rename_operations:
                try:
                    shutil.move(str(source), str(target))
                    print(f"  SUCCESS: {source.name} -> {target_path}")
                except Exception as e:
                    print(f"  ERROR: Error renaming {source.name}: {e}")
        else:
            print(f"\nDRY RUN: {len(rename_operations)} files would be renamed. Use dry_run=False to execute.")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)