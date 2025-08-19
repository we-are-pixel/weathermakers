#!/usr/bin/env python3
"""
Fix WordPress filename references to match the actual downloaded filenames.
Query parameters like ?ver=6.0.9 were converted to _ver_6.0.9 during wget.
"""

import os
import re
from pathlib import Path


def fix_wordpress_filename_references(file_path, dry_run=True):
    """Fix WordPress filename references to match actual downloaded files."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Fix WordPress CSS and JS filename patterns
        wp_filename_fixes = [
            # Fix CSS files - convert ?ver=X.X.X to _ver_X.X.X
            (r'style\.min\.css\?ver=([0-9\.]+)\.css', r'style.min.css_ver_\1.css'),
            (r'style\.min\.css\?ver=([0-9\.]+)', r'style.min.css_ver_\1.css'),
            
            # Fix JS files - convert ?ver=X.X.X to _ver_X.X.X
            (r'comment-reply\.min\.js\?ver=([0-9\.]+)', r'comment-reply.min.js_ver_\1'),
            
            # Fix other common WordPress files that might have version parameters
            (r'wp-emoji-release\.min\.js\?ver=([0-9\.]+)', r'wp-emoji-release.min.js_ver_\1'),
            (r'jquery\.js\?ver=([0-9\.]+)', r'jquery.js_ver_\1'),
            (r'jquery-migrate\.min\.js\?ver=([0-9\.]+)', r'jquery-migrate.min.js_ver_\1'),
        ]
        
        for pattern, replacement in wp_filename_fixes:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                fixes_made += 1
        
        # Write back if changes were made and not dry run
        if content != original_content and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return fixes_made
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main(dry_run=True):
    site_root = Path("D:/Dropbox/Weathermakers")
    
    if not site_root.exists():
        print(f"Site directory not found: {site_root}")
        return
    
    # Find all HTML files in the entire site
    html_files = []
    for root, dirs, files in os.walk(site_root):
        for file in files:
            if file.endswith('.html') and not file.endswith('.backup'):
                html_files.append(Path(root) / file)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Processing {len(html_files)} HTML files...")
    
    total_fixes = 0
    files_with_fixes = 0
    
    for html_file in html_files:
        fixes = fix_wordpress_filename_references(html_file, dry_run)
        if fixes > 0:
            files_with_fixes += 1
            total_fixes += fixes
            relative_path = html_file.relative_to(site_root)
            if files_with_fixes <= 20:  # Show first 20 files
                print(f"  {relative_path}: {fixes} filename fixes")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files with fixes: {files_with_fixes}")
    print(f"Total WordPress filename fixes: {total_fixes}")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply fixes.")
    else:
        print(f"\nFixes applied!")
    
    # Show what files are expected to exist
    print(f"\nExpected WordPress files:")
    expected_files = [
        "blog/wp-includes/css/dist/block-library/style.min.css_ver_6.0.9.css",
        "blog/wp-includes/js/comment-reply.min.js_ver_6.0.9"
    ]
    
    for expected_file in expected_files:
        file_path = site_root / expected_file
        exists = "EXISTS" if file_path.exists() else "MISSING"
        print(f"  {exists} {expected_file}")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)