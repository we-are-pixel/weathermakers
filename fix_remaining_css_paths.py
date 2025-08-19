#!/usr/bin/env python3
"""
Fix remaining CSS and JS path issues in blog posts that weren't caught by the first script.
This handles WordPress-specific paths that don't start with /.
"""

import os
import re
from pathlib import Path


def calculate_relative_depth(blog_post_path, blog_root):
    """Calculate how many levels deep a blog post is from the blog root."""
    try:
        relative_path = blog_post_path.relative_to(blog_root)
        return len(relative_path.parts) - 1  # -1 because the last part is index.html
    except ValueError:
        return 0


def fix_wordpress_asset_paths(file_path, blog_root, dry_run=True):
    """Fix WordPress asset paths that are relative to blog root."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Calculate how deep this post is from the blog root
        depth = calculate_relative_depth(file_path, blog_root)
        
        if depth > 0:
            # Create the relative path prefix to get back to site root
            site_root_prefix = '../' * depth
            
            # Fix WordPress paths that are relative to blog root
            wp_patterns = [
                # Fix blog/wp-includes/css paths
                (r'href="blog/wp-includes/([^"]*)"', f'href="{site_root_prefix}blog/wp-includes/\\1"'),
                (r"href='blog/wp-includes/([^']*)'", f"href='{site_root_prefix}blog/wp-includes/\\1'"),
                
                # Fix blog/wp-includes/js paths
                (r'src="blog/wp-includes/([^"]*)"', f'src="{site_root_prefix}blog/wp-includes/\\1"'),
                (r"src='blog/wp-includes/([^']*)'", f"src='{site_root_prefix}blog/wp-includes/\\1'"),
                
                # Fix blog/wp-content paths
                (r'href="blog/wp-content/([^"]*)"', f'href="{site_root_prefix}blog/wp-content/\\1"'),
                (r"href='blog/wp-content/([^']*)'", f"href='{site_root_prefix}blog/wp-content/\\1'"),
                (r'src="blog/wp-content/([^"]*)"', f'src="{site_root_prefix}blog/wp-content/\\1"'),
                (r"src='blog/wp-content/([^']*)'", f"src='{site_root_prefix}blog/wp-content/\\1'"),
                
                # Fix any other blog/ prefixed paths
                (r'href="blog/([^"]*)"', f'href="{site_root_prefix}blog/\\1"'),
                (r"href='blog/([^']*)'", f"href='{site_root_prefix}blog/\\1'"),
                (r'src="blog/([^"]*)"', f'src="{site_root_prefix}blog/\\1"'),
                (r"src='blog/([^']*)'", f"src='{site_root_prefix}blog/\\1'"),
            ]
            
            for pattern, replacement in wp_patterns:
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
    
    # Find all blog post index.html files in subdirectories (not the main blog index)
    blog_posts = []
    for root, dirs, files in os.walk(blog_root):
        for file in files:
            if file == 'index.html':
                file_path = Path(root) / file
                # Skip the main blog index and page indexes
                if (file_path != blog_root / 'index.html' and 
                    '/page/' not in str(file_path)):
                    blog_posts.append(file_path)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Processing {len(blog_posts)} blog post files...")
    
    total_fixes = 0
    files_with_fixes = 0
    
    for blog_post in blog_posts:
        fixes = fix_wordpress_asset_paths(blog_post, blog_root, dry_run)
        if fixes > 0:
            files_with_fixes += 1
            total_fixes += fixes
            relative_path = blog_post.relative_to(blog_root.parent)
            if files_with_fixes <= 20:  # Show first 20 files
                print(f"  {relative_path}: {fixes} fixes")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files with fixes: {files_with_fixes}")
    print(f"Total WordPress asset path fixes: {total_fixes}")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply fixes.")
    else:
        print(f"\nFixes applied!")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)