#!/usr/bin/env python3
"""
Comprehensive script to fix broken links in the Weathermakers website.
"""

import os
import re
from pathlib import Path
from urllib.parse import unquote
import shutil


def url_decode_string(text):
    """Decode URL-encoded strings like %3F to ?"""
    return unquote(text)


def fix_url_encoded_links(content):
    """Fix URL-encoded links like %3F, %3D, etc."""
    fixes = 0
    
    # Common URL encoding fixes
    replacements = [
        ('%3F', '?'),
        ('%3D', '='),
        ('%3A', ':'),
        ('%2F', '/'),
        ('%26', '&'),
        ('%25', '%'),
        ('%20', ' '),
        ('%22', '"'),
        ('%27', "'"),
    ]
    
    for encoded, decoded in replacements:
        old_content = content
        content = content.replace(encoded, decoded)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def fix_wordpress_paths(content):
    """Fix WordPress-specific paths that don't exist in static site."""
    fixes = 0
    
    # Remove or replace WordPress-specific links
    wordpress_fixes = [
        # Remove WordPress API links
        (r'<link[^>]*rel=["\']EditURI["\'][^>]*>', ''),
        (r'<link[^>]*href=["\'][^"\']*xmlrpc\.php[^"\']*["\'][^>]*>', ''),
        
        # Fix wp-content paths to local paths
        (r'href=["\']([^"\']*)/wp-content/uploads/([^"\']*)["\']', r'href="blog/wp-content/uploads/\2"'),
        (r'src=["\']([^"\']*)/wp-content/uploads/([^"\']*)["\']', r'src="blog/wp-content/uploads/\2"'),
        
        # Fix wp-includes paths
        (r'href=["\']([^"\']*)/wp-includes/([^"\']*)["\']', r'href="blog/wp-includes/\2"'),
        (r'src=["\']([^"\']*)/wp-includes/([^"\']*)["\']', r'src="blog/wp-includes/\2"'),
        
        # Remove WordPress JSON API links
        (r'<link[^>]*href=["\'][^"\']*wp-json[^"\']*["\'][^>]*>', ''),
    ]
    
    for pattern, replacement in wordpress_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def fix_malformed_index_links(content):
    """Fix remaining malformed index.html?p=XXX links."""
    fixes = 0
    
    # Fix index.html?p=XXX.html links (these should be removed or fixed)
    pattern = r'href=["\']([^"\']*index\.html\?p=\d+\.html)["\']'
    matches = re.findall(pattern, content)
    
    for match in matches:
        # These are malformed links, replace with proper blog index
        content = content.replace(f'href="{match}"', 'href="index.html"')
        fixes += 1
    
    return content, fixes


def fix_relative_paths(content, current_file_path, site_root):
    """Fix relative paths that go too deep or are incorrect."""
    fixes = 0
    
    # Calculate the depth of current file
    try:
        relative_path = current_file_path.relative_to(site_root)
        depth = len(relative_path.parts) - 1  # -1 because we don't count the file itself
    except ValueError:
        depth = 0
    
    # Fix deep relative paths like ../../../../
    if depth > 0:
        # Replace excessive ../ with proper paths
        excessive_pattern = r'href=["\'](\.\./){3,}([^"\']*)["\']'
        
        def replace_excessive_relative(match):
            full_match = match.group(0)
            target_path = match.group(2)
            
            # Replace with absolute path from site root
            return f'href="/{target_path}"'
        
        old_content = content
        content = re.sub(excessive_pattern, replace_excessive_relative, content)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def fix_missing_extensions(content):
    """Add missing .html extensions to paths that need them."""
    fixes = 0
    
    # Find href links that look like they should have .html
    pattern = r'href=["\']([^"\']*)/([^/\."\']*)["\']'
    
    def add_extension_if_needed(match):
        full_match = match.group(0)
        path_part = match.group(1)
        file_part = match.group(2)
        
        # Skip if it already has an extension or is clearly not a page
        if '.' in file_part or file_part in ['feed', 'trackback']:
            return full_match
        
        # Add .html extension
        return f'href="{path_part}/{file_part}.html"'
    
    old_content = content
    content = re.sub(pattern, add_extension_if_needed, content)
    if content != old_content:
        fixes += 1
    
    return content, fixes


def fix_absolute_urls(content):
    """Fix absolute URLs that should be relative."""
    fixes = 0
    
    # Convert absolute URLs to relative for local files
    absolute_patterns = [
        (r'href=["\']https://www\.weathermakerscomfort\.com/([^"\']*)["\']', r'href="/\1"'),
        (r'src=["\']https://www\.weathermakerscomfort\.com/([^"\']*)["\']', r'src="/\1"'),
        (r'href=["\']https://www\.weathermakerscomfort\.com/blog/([^"\']*)["\']', r'href="/blog/\1"'),
        (r'src=["\']https://www\.weathermakerscomfort\.com/blog/([^"\']*)["\']', r'src="/blog/\1"'),
    ]
    
    for pattern, replacement in absolute_patterns:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def process_html_file(file_path, site_root, dry_run=True):
    """Process a single HTML file to fix broken links."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        total_fixes = 0
        
        # Apply all fixes
        content, fixes = fix_url_encoded_links(content)
        total_fixes += fixes
        
        content, fixes = fix_wordpress_paths(content)
        total_fixes += fixes
        
        content, fixes = fix_malformed_index_links(content)
        total_fixes += fixes
        
        content, fixes = fix_relative_paths(content, file_path, site_root)
        total_fixes += fixes
        
        content, fixes = fix_missing_extensions(content)
        total_fixes += fixes
        
        content, fixes = fix_absolute_urls(content)
        total_fixes += fixes
        
        # Write back if changes were made and not dry run
        if content != original_content and not dry_run:
            # Create backup
            backup_path = file_path.with_suffix('.html.backup')
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return total_fixes
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main(dry_run=True):
    site_root = Path("D:/Dropbox/Weathermakers")
    
    if not site_root.exists():
        print(f"Site directory not found: {site_root}")
        return
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(site_root):
        for file in files:
            if file.endswith('.html'):
                html_files.append(Path(root) / file)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Processing {len(html_files)} HTML files...")
    
    total_files_processed = 0
    total_fixes_made = 0
    files_with_fixes = 0
    
    for html_file in html_files:
        relative_path = html_file.relative_to(site_root)
        fixes = process_html_file(html_file, site_root, dry_run)
        
        if fixes > 0:
            files_with_fixes += 1
            total_fixes_made += fixes
            if files_with_fixes <= 10:  # Show first 10 files with fixes
                print(f"  {relative_path}: {fixes} fixes")
        
        total_files_processed += 1
        
        # Progress indicator
        if total_files_processed % 50 == 0:
            print(f"  Progress: {total_files_processed}/{len(html_files)} files processed...")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files processed: {total_files_processed}")
    print(f"Files with fixes: {files_with_fixes}")
    print(f"Total fixes made: {total_fixes_made}")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply fixes.")
    else:
        print(f"\nFixes applied! Backup files created with .backup extension.")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)