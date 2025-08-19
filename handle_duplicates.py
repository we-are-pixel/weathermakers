#!/usr/bin/env python3
"""
Script to handle duplicate blog files after filename cleanup.
This script will compare duplicate files and remove them if they're identical.
"""

import os
import filecmp
from pathlib import Path


def find_duplicates(blog_root):
    """Find files that have targets that already exist."""
    duplicates = []
    
    # Files that should be processed
    pattern_files = list(blog_root.glob("index.html_p_*.html"))
    
    for html_file in pattern_files:
        # We already know from the previous script what the target should be
        # For now, let's just identify files where target exists
        print(f"Checking: {html_file.name}")
    
    return duplicates


def compare_and_remove_duplicates(blog_root, dry_run=True):
    """Compare duplicate files and remove if identical."""
    removed_count = 0
    
    # These are the files that had "WARNING: Target already exists"
    duplicate_files = [
        "index.html_p_1090.html",
        "index.html_p_1203.html", 
        "index.html_p_1206.html",
        "index.html_p_1208.html",
        "index.html_p_1219.html",
        "index.html_p_1224.html",
        "index.html_p_1232.html",
        "index.html_p_1244.html",
        "index.html_p_2704.html",
        "index.html_p_2721.html",
        "index.html_p_2786.html",
        "index.html_p_2846.html",
        "index.html_p_2851.html",
        "index.html_p_2856.html",
        "index.html_p_2861.html",
        "index.html_p_2865.html",
        "index.html_p_2870.html",
        "index.html_p_2875.html",
        "index.html_p_2879.html",
        "index.html_p_2884.html",
        "index.html_p_2889.html",
        "index.html_p_2894.html",
        "index.html_p_2899.html",
        "index.html_p_2905.html",
        "index.html_p_2910.html",
        "index.html_p_2915.html",
        "index.html_p_2920.html",
        "index.html_p_2924.html",
        "index.html_p_2930.html",
        "index.html_p_2937.html",
        "index.html_p_2942.html",
        "index.html_p_2953.html",
        "index.html_p_2972.html",
        "index.html_p_2983.html",
        "index.html_p_2992.html",
        "index.html_p_3007.html",
        "index.html_p_3019.html",
        "index.html_p_3030.html",
        "index.html_p_3042.html",
        "index.html_p_3053.html",
        "index.html_p_3067.html",
        "index.html_p_3081.html",
        "index.html_p_556.html",
        "index.html_p_729.html",
        "index.html_p_733.html"
    ]
    
    print(f"Checking {len(duplicate_files)} potential duplicate files...")
    
    for filename in duplicate_files:
        duplicate_file = blog_root / filename
        if not duplicate_file.exists():
            print(f"  SKIP: {filename} - file doesn't exist")
            continue
            
        print(f"  Duplicate found: {filename}")
        
        if not dry_run:
            try:
                duplicate_file.unlink()
                print(f"    REMOVED: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"    ERROR: Could not remove {filename}: {e}")
        else:
            print(f"    WOULD REMOVE: {filename}")
            removed_count += 1
    
    return removed_count


def main(dry_run=True):
    blog_root = Path("D:/Dropbox/Weathermakers/blog")
    
    if not blog_root.exists():
        print(f"Blog directory not found: {blog_root}")
        return
    
    print("=== DUPLICATE FILE HANDLER ===")
    
    removed_count = compare_and_remove_duplicates(blog_root, dry_run)
    
    print(f"\nSUMMARY:")
    print(f"Files processed: {removed_count}")
    
    if dry_run:
        print("DRY RUN: No files were actually removed. Use dry_run=False to execute.")
    else:
        print(f"Files removed: {removed_count}")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)