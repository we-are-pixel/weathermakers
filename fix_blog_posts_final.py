#!/usr/bin/env python3
"""
Fix remaining blog issues:
1. Fix H2 title links in blog index to point to correct posts
2. Fix CSS/asset paths in individual blog posts to work from subdirectories
"""

import os
import re
from pathlib import Path


def create_blog_post_mapping():
    """Create a mapping from post IDs to their paths."""
    return {
        '1086': 'heating-service/what-does-a-furnace-tune-up-include/',
        '1090': 'heating-service/types-of-heating-systems-for-alberta-homes-and-buildings/',
        '1203': 'heating-service/why-does-my-furnace-smell/',
        '1206': 'heating-service/when-should-i-repair-vs-replace-my-furnace/',
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


def extract_title_from_h2(h2_content):
    """Extract title from H2 content."""
    # Remove HTML tags to get just the text
    title = re.sub(r'<[^>]+>', '', h2_content)
    return title.strip()


def find_post_path_by_title(title, post_mapping):
    """Find the post path that matches the title."""
    # This is a simplified approach - we'll try to match titles to known posts
    title_lower = title.lower()
    
    # Create a reverse mapping from likely titles to paths
    title_mappings = {
        'why is my water heater leaking? what you should do now': '3030',
        'what are common plumbing issues for businesses?': '3019', 
        'is a tankless water heater right for your home?': '3007',
        'what to do when your water heater starts leaking': '3081',
        'how to choose the right hvac system for your commercial space': '3042',
        'simple ways to keep your family safe from carbon monoxide': '3053',
        'inverter acs are better to beat the summer heat and here&#8217;s why': '3067',
        'inverter acs are better to beat the summer heat and heres why': '3067',
        'is it an emergency? know when to call a plumber right away': '2992',
        'new furnace install: what to expect': '2983',
        'spread the love: upgrade your hvac system': '2972',
        'how to spot signs you need boiler repair': '2953',
        'top 5 benefits of ductless heating systems': '2856',  # This might be in ductless category
        'furnace maintenance: essential for an edmonton winter': '2937',
        'big tips for big jobs: considerations for commercial plumbing': '2930',
        'the air filter: a component you can&#8217;t afford to forget this year': '2924',
        'the air filter: a component you cant afford to forget this year': '2924',
        'choosing the right heating system for your home this winter': '2920',
        'duct cleaning: a good choice for the fall': '2915',
        'are drain cleaning chemicals really that bad?': '2910',
        'customer questions: why does a problem impact a system efficiency?': '2905',
        'customer questions: why does a problem impact a systems efficiency?': '2905',
        'the unique pros and cons of ductless hvac': '2899',
    }
    
    for known_title, post_id in title_mappings.items():
        if known_title in title_lower:
            return post_mapping.get(post_id, '')
    
    return ''


def fix_blog_index_h2_links(file_path, post_mapping, dry_run=True):
    """Fix H2 title links in blog index files."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Find H2 links that point to /blog/ and fix them
        h2_pattern = r'<h2><a href="/blog/" rel="bookmark" title="Permanent Link to ([^"]+)">([^<]+)</a></h2>'
        
        def fix_h2_link(match):
            title = match.group(1)
            link_text = match.group(2)
            
            # Find the correct post path
            post_path = find_post_path_by_title(title, post_mapping)
            if post_path:
                return f'<h2><a href="{post_path}index.html" rel="bookmark" title="Permanent Link to {title}">{link_text}</a></h2>'
            else:
                # If we can't find the post, leave it as is but log it
                print(f"    Could not find post path for: {title}")
                return match.group(0)
        
        old_content = content
        content = re.sub(h2_pattern, fix_h2_link, content)
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


def calculate_relative_depth(blog_post_path, blog_root):
    """Calculate how many levels deep a blog post is from the blog root."""
    try:
        relative_path = blog_post_path.relative_to(blog_root)
        return len(relative_path.parts) - 1  # -1 because the last part is index.html
    except ValueError:
        return 0


def fix_blog_post_css_paths(file_path, blog_root, dry_run=True):
    """Fix CSS and asset paths in individual blog posts."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_made = 0
        
        # Calculate how deep this post is
        depth = calculate_relative_depth(file_path, blog_root)
        
        if depth > 0:
            # Create the relative path prefix
            relative_prefix = '../' * depth
            
            # Fix asset paths that start with /assets/
            asset_patterns = [
                (r'href="/assets/', f'href="{relative_prefix}assets/'),
                (r'src="/assets/', f'src="{relative_prefix}assets/'),
                (r'href="/apple-touch-icon', f'href="{relative_prefix}apple-touch-icon'),
                (r'href="/favicon', f'href="{relative_prefix}favicon'),
            ]
            
            for pattern, replacement in asset_patterns:
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
    
    post_mapping = create_blog_post_mapping()
    
    # Part 1: Fix H2 title links in blog index files
    print("=== FIXING H2 TITLE LINKS ===")
    
    index_files = [
        blog_root / "index.html",
        blog_root / "page" / "2" / "index.html",
    ]
    
    h2_fixes = 0
    for file_path in index_files:
        if file_path.exists():
            fixes = fix_blog_index_h2_links(file_path, post_mapping, dry_run)
            if fixes > 0:
                relative_path = file_path.relative_to(blog_root.parent)
                print(f"  {relative_path}: {fixes} H2 links fixed")
                h2_fixes += fixes
    
    # Part 2: Fix CSS paths in individual blog posts
    print("\n=== FIXING CSS PATHS IN BLOG POSTS ===")
    
    # Find all blog post index.html files in subdirectories
    blog_posts = []
    for root, dirs, files in os.walk(blog_root):
        for file in files:
            if file == 'index.html':
                file_path = Path(root) / file
                # Skip the main blog index
                if file_path != blog_root / 'index.html':
                    blog_posts.append(file_path)
    
    css_fixes = 0
    css_files_fixed = 0
    
    for blog_post in blog_posts:
        fixes = fix_blog_post_css_paths(blog_post, blog_root, dry_run)
        if fixes > 0:
            css_files_fixed += 1
            css_fixes += fixes
            relative_path = blog_post.relative_to(blog_root.parent)
            print(f"  {relative_path}: {fixes} CSS path fixes")
    
    print(f"\n=== SUMMARY ===")
    print(f"H2 title link fixes: {h2_fixes}")
    print(f"CSS path fixes: {css_fixes} across {css_files_fixed} files")
    
    if dry_run:
        print(f"\nDRY RUN: No files were actually modified.")
        print(f"Use --execute to apply fixes.")
    else:
        print(f"\nFixes applied!")


if __name__ == "__main__":
    import sys
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "--execute"
    main(dry_run=dry_run)