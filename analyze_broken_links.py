#!/usr/bin/env python3
"""
Analyze broken links to understand the most common patterns that need fixing.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
from collections import defaultdict, Counter


def extract_links_from_html(html_file):
    """Extract all internal links from an HTML file."""
    try:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        links = []
        
        # Find href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        for match in re.finditer(href_pattern, content, re.IGNORECASE):
            url = match.group(1)
            links.append(url)
        
        # Find src attributes (for images, scripts, etc.)
        src_pattern = r'src=["\']([^"\']+)["\']'
        for match in re.finditer(src_pattern, content, re.IGNORECASE):
            url = match.group(1)
            links.append(url)
        
        return links
    except Exception as e:
        return []


def is_internal_link(url, base_domain="weathermakerscomfort.com"):
    """Check if a URL is an internal link."""
    if url.startswith('#') or url.startswith('mailto:') or url.startswith('tel:') or url.startswith('javascript:'):
        return False
    
    # Absolute URLs
    if url.startswith('http://') or url.startswith('https://'):
        parsed = urlparse(url)
        return base_domain in parsed.netloc
    
    # Relative URLs (considered internal)
    if url.startswith('/') or not url.startswith('http'):
        return True
    
    return False


def normalize_path(url, current_file_path, site_root):
    """Convert a URL to a normalized file path for checking."""
    try:
        # Handle absolute URLs
        if url.startswith('http://') or url.startswith('https://'):
            parsed = urlparse(url)
            path = parsed.path
        else:
            path = url
        
        # Remove query parameters and fragments
        if '?' in path:
            path = path.split('?')[0]
        if '#' in path:
            path = path.split('#')[0]
        
        # Handle relative paths
        if not path.startswith('/'):
            # Relative to current file
            current_dir = current_file_path.parent
            path = str((current_dir / path).resolve().relative_to(site_root))
            path = '/' + path.replace('\\', '/')
        
        # Remove /blog/ prefix if present
        if path.startswith('/blog/'):
            path = path[6:]
        elif path.startswith('/'):
            path = path[1:]
        
        # If path is empty or just '/', it refers to index.html
        if not path or path == '/':
            return 'index.html'
        
        # If path ends with '/', append index.html
        if path.endswith('/'):
            path = path + 'index.html'
        
        # If path doesn't end with a file extension, assume it's a directory with index.html
        if '.' not in Path(path).name:
            path = path + '/index.html'
        
        return path
    except Exception as e:
        return None


def check_file_exists(normalized_path, site_root):
    """Check if a normalized path exists in the site."""
    try:
        full_path = site_root / normalized_path
        return full_path.exists()
    except Exception:
        return False


def categorize_broken_link(link):
    """Categorize broken links by type."""
    if '%3F' in link or '%3D' in link or '%3A' in link or '%2F' in link:
        return 'url_encoded'
    elif 'wp-content' in link or 'wp-includes' in link or 'wp-json' in link:
        return 'wordpress_specific'
    elif link.startswith('../../') or link.count('../') > 2:
        return 'deep_relative_path'
    elif link.endswith('.css') or link.endswith('.js'):
        return 'static_asset'
    elif 'xmlrpc.php' in link or 'rsd' in link:
        return 'wordpress_api'
    elif 'feed' in link:
        return 'rss_feed'
    else:
        return 'other'


def main():
    site_root = Path("D:/Dropbox/Weathermakers")
    
    # Sample more files for analysis
    sample_files = []
    for root, dirs, files in os.walk(site_root):
        for file in files:
            if file.endswith('.html'):
                sample_files.append(Path(root) / file)
    
    # Limit to first 50 files for analysis
    sample_files = sample_files[:50]
    
    print(f"Analyzing {len(sample_files)} HTML files for broken link patterns...")
    
    broken_links_by_category = defaultdict(list)
    all_broken_links = []
    
    for html_file in sample_files:
        links = extract_links_from_html(html_file)
        internal_links = [link for link in links if is_internal_link(link)]
        
        for link in internal_links:
            # Normalize the link to a file path
            normalized_path = normalize_path(link, html_file, site_root)
            if not normalized_path:
                continue
            
            # Check if the target file exists
            if not check_file_exists(normalized_path, site_root):
                category = categorize_broken_link(link)
                broken_links_by_category[category].append(link)
                all_broken_links.append(link)
    
    print(f"\n=== BROKEN LINK ANALYSIS ===")
    print(f"Total broken links found: {len(all_broken_links)}")
    
    print(f"\nBroken links by category:")
    for category, links in broken_links_by_category.items():
        print(f"  {category}: {len(links)} links")
    
    # Show examples for each category
    for category, links in broken_links_by_category.items():
        if links:
            print(f"\n{category.upper()} examples:")
            unique_links = list(set(links))[:5]  # Show 5 unique examples
            for link in unique_links:
                print(f"  {link}")
    
    # Most common broken links overall
    link_counts = Counter(all_broken_links)
    print(f"\nMOST COMMON BROKEN LINKS:")
    for link, count in link_counts.most_common(10):
        print(f"  {count:3d}x  {link}")


if __name__ == "__main__":
    main()