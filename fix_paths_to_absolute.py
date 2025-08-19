#!/usr/bin/env python3
"""
Convert all relative asset paths to absolute paths to fix browser path resolution issues.
This ensures CSS and assets load correctly regardless of directory depth.
"""

import os
import re
from pathlib import Path


def convert_relative_to_absolute_paths(file_path, dry_run=True):
    """Convert relative asset paths to absolute paths from site root."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Convert relative asset paths to absolute paths
        path_fixes = [
            # Main site assets
            (r'href="(\.\./)+assets/', r'href="/assets/'),
            (r'src="(\.\./)+assets/', r'src="/assets/'),
            
            # Apple touch icons
            (r'href="(\.\./)+apple-touch-icon', r'href="/apple-touch-icon'),
            
            # Favicon
            (r'href="(\.\./)+favicon', r'href="/favicon'),
            
            # Any other root-level files
            (r'href="(\.\./)+([^"]*\.(?:css|js|ico|png|jpg|svg))"', r'href="/\2"'),
            (r'src="(\.\./)+([^"]*\.(?:css|js|ico|png|jpg|svg))"', r'src="/\2"'),
        ]
        
        for pattern, replacement in path_fixes:
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
    blog_root = Path("D:/Dropbox/Weathermakers/blog")
    
    if not blog_root.exists():
        print(f"Blog directory not found: {blog_root}")
        return
    
    # Find all HTML files in blog subdirectories (not the main blog index)
    blog_posts = []
    for root, dirs, files in os.walk(blog_root):
        for file in files:
            if file == 'index.html':
                file_path = Path(root) / file
                # Only process files in subdirectories, not the main blog index
                if file_path != blog_root / 'index.html':
                    blog_posts.append(file_path)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Processing {len(blog_posts)} blog files...")
    
    total_fixes = 0
    files_with_fixes = 0
    
    for blog_post in blog_posts:
        fixes = convert_relative_to_absolute_paths(blog_post, dry_run)
        if fixes > 0:
            files_with_fixes += 1
            total_fixes += fixes
            relative_path = blog_post.relative_to(blog_root.parent)
            if files_with_fixes <= 20:  # Show first 20 files
                print(f"  {relative_path}: {fixes} path fixes")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files with fixes: {files_with_fixes}")
    print(f"Total path fixes: {total_fixes}")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply fixes.")
    else:
        print(f"\nFixes applied! All paths now absolute from site root.")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)