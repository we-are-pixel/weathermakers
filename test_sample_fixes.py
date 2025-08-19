#!/usr/bin/env python3
"""
Test fixes on a small sample to verify they look correct.
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
    fixes = []
    
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
            fixes.append(f"Replaced {encoded} with {decoded}")
    
    return content, fixes


def fix_wordpress_paths(content):
    """Fix WordPress-specific paths that don't exist in static site."""
    fixes = []
    
    # Remove or replace WordPress-specific links
    wordpress_fixes = [
        # Remove WordPress API links
        (r'<link[^>]*rel=["\']EditURI["\'][^>]*>', '', 'Remove EditURI links'),
        (r'<link[^>]*href=[^"\']*xmlrpc\.php[^>]*>', '', 'Remove xmlrpc links'),
        
        # Fix wp-content paths to local paths
        (r'href=["\']([^"\']*)/wp-content/uploads/([^"\']*)["\']', r'href="blog/wp-content/uploads/\2"', 'Fix wp-content href paths'),
        (r'src=["\']([^"\']*)/wp-content/uploads/([^"\']*)["\']', r'src="blog/wp-content/uploads/\2"', 'Fix wp-content src paths'),
    ]
    
    for pattern, replacement, description in wordpress_fixes:
        old_content = content
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if content != old_content:
            fixes.append(description)
    
    return content, fixes


def test_file_fixes(file_path, site_root):
    """Test fixes on a single file and show what changes would be made."""
    print(f"\nTesting fixes for: {file_path.relative_to(site_root)}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        all_fixes = []
        
        # Test URL encoding fixes
        content, fixes = fix_url_encoded_links(content)
        all_fixes.extend([f"URL_ENCODED: {fix}" for fix in fixes])
        
        # Test WordPress path fixes
        content, fixes = fix_wordpress_paths(content)
        all_fixes.extend([f"WORDPRESS: {fix}" for fix in fixes])
        
        if all_fixes:
            print("Changes that would be made:")
            for fix in all_fixes[:10]:  # Show first 10 fixes
                print(f"  - {fix}")
            if len(all_fixes) > 10:
                print(f"  ... and {len(all_fixes) - 10} more fixes")
        else:
            print("No fixes needed for this file.")
        
        # Show a before/after sample if there are changes
        if content != original_content:
            print("\nSample before/after (first 500 chars where changes occur):")
            
            # Find first difference
            for i, (old_char, new_char) in enumerate(zip(original_content, content)):
                if old_char != new_char:
                    start = max(0, i - 100)
                    end = min(len(content), i + 400)
                    
                    print("BEFORE:")
                    print(repr(original_content[start:end]))
                    print("\nAFTER:")
                    print(repr(content[start:end]))
                    break
        
        return len(all_fixes)
    
    except Exception as e:
        print(f"Error testing {file_path}: {e}")
        return 0


def main():
    site_root = Path("D:/Dropbox/Weathermakers")
    
    # Test on a few sample files
    test_files = [
        site_root / "index.html",
        site_root / "blog" / "index.html",
        site_root / "blog" / "air-conditioning-service" / "5-signs-it-might-be-time-to-retire-your-ac" / "index.html"
    ]
    
    total_fixes = 0
    for test_file in test_files:
        if test_file.exists():
            fixes = test_file_fixes(test_file, site_root)
            total_fixes += fixes
        else:
            print(f"\nSkipping: {test_file.relative_to(site_root)} (doesn't exist)")
    
    print(f"\n{'='*60}")
    print(f"TOTAL FIXES TESTED: {total_fixes}")
    print("These are examples of the types of fixes that will be applied.")


if __name__ == "__main__":
    main()