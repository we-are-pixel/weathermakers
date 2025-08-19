#!/usr/bin/env python3
"""
Fix remaining broken links after the initial cleanup.
Focus on blog-specific issues, relative paths, and missing files.
"""

import os
import re
from pathlib import Path
import shutil


def fix_blog_relative_paths(content, current_file_path, site_root):
    """Fix blog-specific relative paths like ../../tag/edmonton/"""
    fixes = 0
    
    try:
        # Check if we're in a blog subdirectory
        relative_path = current_file_path.relative_to(site_root)
        if not str(relative_path).startswith('blog'):
            return content, fixes
        
        # Fix common blog relative path patterns
        blog_fixes = [
            # Fix tag links
            (r'href=["\'](\.\./)*tag/([^"\']*)["\']', r'href="/blog/tag/\2"'),
            (r'href=["\'](\.\./)*category/([^"\']*)["\']', r'href="/blog/category/\2"'),
            
            # Fix comments/feed links
            (r'href=["\'](\.\./)*comments/feed/["\']', r'href="/blog/comments/feed/"'),
            (r'href=["\'](\.\./)*feed/["\']', r'href="/blog/feed/"'),
            
            # Fix blog navigation
            (r'href=["\'](\.\./)+index\.html["\']', r'href="/blog/"'),
        ]
        
        for pattern, replacement in blog_fixes:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                fixes += 1
        
    except ValueError:
        # File not in site root
        pass
    
    return content, fixes


def fix_missing_assets(content):
    """Fix or remove references to missing assets."""
    fixes = 0
    
    # Remove or fix problematic asset links
    asset_fixes = [
        # Remove IE-specific CSS that likely doesn't exist
        (r'<!--\[if[^>]*\]>.*?<link[^>]*ie\.css[^>]*>.*?<!\[endif\]-->', ''),
        
        # Remove HTML5 shiv references if they don't exist
        (r'<!--\[if[^>]*\]>.*?html5shiv\.js.*?<!\[endif\]-->', ''),
        
        # Fix master.css path if it exists
        (r'href=["\']([^"\']*)/assets/templates/main/css/master\.css["\']', 
         r'href="/assets/templates/main/css/responsive.min.css"'),
    ]
    
    for pattern, replacement in asset_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def fix_wordpress_content_links(content):
    """Fix WordPress content links to point to existing files or remove them."""
    fixes = 0
    
    # Fix wp-content upload paths
    wp_fixes = [
        # Try to fix wp-content upload paths to use relative paths
        (r'src=["\']wp-content/uploads/([^"\']*)["\']', r'src="/blog/wp-content/uploads/\1"'),
        (r'href=["\']wp-content/uploads/([^"\']*)["\']', r'href="/blog/wp-content/uploads/\1"'),
        
        # Remove theme CSS links that likely don't exist
        (r'<link[^>]*wp-content/themes/[^>]*>', ''),
    ]
    
    for pattern, replacement in wp_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def fix_index_html_links(content):
    """Fix bare index.html links to be more specific."""
    fixes = 0
    
    # Fix standalone index.html links
    patterns = [
        # In blog context, index.html should go to blog home
        (r'href=["\']index\.html["\']', r'href="/blog/"'),
    ]
    
    for pattern, replacement in patterns:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def fix_feed_extensions(content):
    """Fix feed links that have incorrect extensions."""
    fixes = 0
    
    # Fix feed links with wrong extensions
    feed_fixes = [
        (r'href=["\']([^"\']*)/feed/\.html["\']', r'href="\1/feed/"'),
        (r'href=["\']([^"\']*)/feed\.html["\']', r'href="\1/feed/"'),
    ]
    
    for pattern, replacement in feed_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            fixes += 1
    
    return content, fixes


def process_html_file(file_path, site_root, dry_run=True):
    """Process a single HTML file to fix remaining broken links."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        total_fixes = 0
        
        # Apply all remaining fixes
        content, fixes = fix_blog_relative_paths(content, file_path, site_root)
        total_fixes += fixes
        
        content, fixes = fix_missing_assets(content)
        total_fixes += fixes
        
        content, fixes = fix_wordpress_content_links(content)
        total_fixes += fixes
        
        content, fixes = fix_index_html_links(content)
        total_fixes += fixes
        
        content, fixes = fix_feed_extensions(content)
        total_fixes += fixes
        
        # Write back if changes were made and not dry run
        if content != original_content and not dry_run:
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
            if file.endswith('.html') and not file.endswith('.backup'):
                html_files.append(Path(root) / file)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Processing {len(html_files)} HTML files for remaining link fixes...")
    
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
    print(f"Total additional fixes made: {total_fixes_made}")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply these additional fixes.")
    else:
        print(f"\nAdditional fixes applied!")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)