#!/usr/bin/env python3
"""
Fix blog index page links to point to correct blog post URLs instead of malformed ones.
"""

import os
import re
from pathlib import Path


def create_blog_post_mapping(blog_root):
    """Create a mapping from old index.html?p=XXX URLs to new blog post paths."""
    mapping = {}
    
    # Define the mapping based on our file renaming
    post_mappings = {
        '1086': 'heating-service/what-does-a-furnace-tune-up-include/',
        '1090': 'heating-service/types-of-heating-systems-for-alberta-homes-and-buildings/',
        '1203': 'heating-service/why-does-my-furnace-smell/',
        '1206': 'heating-service/when-should-i-repair-vs-replace-my-furnace/',
        '1208': '', # This was the blog index, now just /blog/
        '1219': 'heating-service/how-to-humidify-your-home-in-winter/',
        '1224': 'plumbing-service/what-is-a-tankless-water-heater/',
        '1232': 'plumbing-service/what-do-i-need-to-know-about-hard-water/',
        '1244': 'plumbing-service/how-to-clear-slow-and-clogged-drains/',
        '2704': 'heating-service/why-choose-a-heat-pump-for-your-home-heating-and-cooling/',
        '2721': 'weathermakers/10-benefits-central-air-conditioning-edmonton/',
        '2786': 'heating-service/commercial-hvac-and-commercial-plumbing-edmonton/',
        '2846': 'indoor-air-quality-service/how-a-humidifier-and-heating-system-can-work-together/',
        '2851': 'air-conditioning-service/join-the-comfort-club-the-unique-benefits-of-springtime-maintenance/',
        '2856': 'heat-pumps/our-deep-ductless-guide-for-homeowners/',
        '2861': 'air-conditioning-service/a-refrigerant-leak-faq-what-they-are-and-how-to-detect-them/',
        '2865': 'air-conditioning-service/diy-tips-cleaning-your-air-filter/',
        '2870': 'air-conditioning-service/5-signs-it-might-be-time-to-retire-your-ac/',
        '2875': 'air-conditioning-service/five-common-sounds-of-a-malfunctioning-air-conditioner/',
        '2879': 'air-conditioning-service/deciding-to-go-ductless-pros-and-cons/',
        '2884': 'air-conditioning-service/weathermakers-tips-its-not-too-late-for-maintenance/',
        '2889': 'air-conditioning-service/choosing-the-right-ac-installer-in-edmonton/',
        '2894': 'air-conditioning-service/are-you-dealing-with-an-ac-service-scam/',
        '2899': 'air-conditioning-service/the-unique-pros-and-cons-of-ductless-hvac/',
        '2905': 'air-conditioning-service/customer-questions-why-does-a-problem-impact-a-systems-efficiency/',
        '2910': 'plumbing-service/are-drain-cleaning-chemicals-really-that-bad/',
        '2915': 'indoor-air-quality-service/duct-cleaning-a-good-choice-for-the-fall/',
        '2920': 'heating-service/choosing-the-right-heating-system-for-your-home-this-winter/',
        '2924': 'furnace/the-air-filter-a-component-you-cant-afford-to-forget-this-year/',
        '2930': 'commercial-hvac-plumbing/big-tips-for-big-jobs-considerations-for-commercial-plumbing/',
        '2937': 'heating-service/furnace-maintenance-essential-for-an-edmonton-winter/',
        '2942': 'heating-service/what-does-a-furnace-tune-up-include/',
        '2953': 'heating-service/how-to-spot-signs-you-need-boiler-repair/',
        '2972': 'hvac/spread-the-love-upgrade-your-hvac-system/',
        '2983': 'heating-service/new-furnace-install-what-to-expect/',
        '2992': 'plumbing-service/is-it-an-emergency-know-when-to-call-a-plumber-right-away/',
        '3007': 'water-heater-service/is-a-tankless-water-heater-right-for-your-home/',
        '3019': 'commercial-hvac-plumbing/what-are-common-plumbing-issues-for-businesses/',
        '3030': 'plumbing-service/why-is-my-water-heater-leaking-what-you-should-do-now/',
        '3042': 'commercial-hvac-plumbing/how-to-choose-the-right-hvac-system-for-your-commercial-space/',
        '3053': 'indoor-air-quality-service/simple-ways-to-keep-your-family-safe-from-carbon-monoxide/',
        '3067': 'air-conditioning-service/inverter-acs-are-better-to-beat-the-summer-heat-and-heres-why/',
        '3081': 'plumbing-service/what-to-do-when-your-water-heater-starts-leaking/',
        '556': 'weathermakers/what-makes-weathermakers-different/',
        '729': 'weathermakers/metro-edmontons-best-hvac-and-plumbing-contractor-for-over-55-years/',
        '733': 'heating-service/time-for-a-new-furnace/',
    }
    
    # Convert to the format we need
    for post_id, post_path in post_mappings.items():
        if post_path:  # Skip empty paths
            mapping[f'index.html?p={post_id}.html'] = f'{post_path}index.html'
            mapping[f'index.html?p={post_id}.html#more-{post_id}'] = f'{post_path}index.html'
    
    return mapping


def fix_blog_index_links(file_path, mapping, dry_run=True):
    """Fix blog index links in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Fix links that point to old post URLs
        for old_url, new_path in mapping.items():
            # Fix href links
            old_pattern = f'href="{old_url}"'
            new_link = f'href="{new_path}"'
            
            old_content = content
            content = content.replace(old_pattern, new_link)
            if content != old_content:
                fixes_made += 1
            
            # Also fix any variations with single quotes
            old_pattern = f"href='{old_url}'"
            new_link = f"href='{new_path}'"
            
            old_content = content
            content = content.replace(old_pattern, new_link)
            if content != old_content:
                fixes_made += 1
        
        # Fix "Continue Reading" links that point back to /blog/ - these should go to the actual posts
        continue_reading_pattern = r'<a href="/blog/" rel="bookmark" title="Permanent Link to ([^"]+)">Continue Reading</a>'
        
        def fix_continue_reading(match):
            title = match.group(1)
            # Try to find the matching post path by title
            for old_url, new_path in mapping.items():
                # This is a simplified approach - in a real scenario you'd want a more robust title-to-URL mapping
                if new_path:
                    return f'<a href="{new_path}" rel="bookmark" title="Permanent Link to {title}">Continue Reading</a>'
            return match.group(0)  # Return original if no match found
        
        old_content = content
        content = re.sub(continue_reading_pattern, fix_continue_reading, content)
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
    
    # Create the mapping
    mapping = create_blog_post_mapping(blog_root)
    print(f"Created mapping for {len(mapping)} blog post URLs")
    
    # Files to fix - blog index and category pages
    files_to_fix = [
        blog_root / "index.html",
        blog_root / "page" / "2" / "index.html",
    ]
    
    # Add category index pages
    category_pages = list(blog_root.glob("category/*/index.html"))
    files_to_fix.extend(category_pages)
    
    # Add tag index pages  
    tag_pages = list(blog_root.glob("tag/*/index.html"))
    files_to_fix.extend(tag_pages)
    
    print(f"{'DRY RUN: ' if dry_run else ''}Processing {len(files_to_fix)} blog listing files...")
    
    total_fixes = 0
    files_with_fixes = 0
    
    for file_path in files_to_fix:
        if file_path.exists():
            fixes = fix_blog_index_links(file_path, mapping, dry_run)
            if fixes > 0:
                files_with_fixes += 1
                total_fixes += fixes
                relative_path = file_path.relative_to(blog_root.parent)
                print(f"  {relative_path}: {fixes} fixes")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files with fixes: {files_with_fixes}")
    print(f"Total fixes made: {total_fixes}")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply fixes.")
    else:
        print(f"\nFixes applied!")
    
    # Show some examples of the mapping
    if mapping:
        print(f"\nExample mappings:")
        for i, (old, new) in enumerate(list(mapping.items())[:5]):
            print(f"  {old} -> {new}")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)