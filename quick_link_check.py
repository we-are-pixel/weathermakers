#!/usr/bin/env python3
"""
Quick link checker to sample a few files and see what kind of broken links we have.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict


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
        
        return links
    except Exception as e:
        print(f"Error reading {html_file}: {e}")
        return []


def is_internal_link(url, base_domain="weathermakerscomfort.com"):
    """Check if a URL is an internal link."""
    if url.startswith('#'):  # Fragment only
        return False
    if url.startswith('mailto:'):  # Email links
        return False
    if url.startswith('tel:'):  # Phone links
        return False
    if url.startswith('javascript:'):  # JavaScript links
        return False
    
    # Absolute URLs
    if url.startswith('http://') or url.startswith('https://'):
        parsed = urlparse(url)
        return base_domain in parsed.netloc
    
    # Relative URLs (considered internal)
    if url.startswith('/') or not url.startswith('http'):
        return True
    
    return False


def main():
    site_root = Path("D:/Dropbox/Weathermakers")
    
    # Sample a few key files
    sample_files = [
        site_root / "blog" / "index.html",
        site_root / "index.html",
        site_root / "blog" / "air-conditioning-service" / "5-signs-it-might-be-time-to-retire-your-ac" / "index.html"
    ]
    
    print("=== QUICK LINK CHECK SAMPLE ===")
    
    for html_file in sample_files:
        if not html_file.exists():
            print(f"SKIP: {html_file.relative_to(site_root)} (doesn't exist)")
            continue
            
        print(f"\nChecking: {html_file.relative_to(site_root)}")
        
        links = extract_links_from_html(html_file)
        internal_links = [link for link in links if is_internal_link(link)]
        
        print(f"  Total links: {len(links)}")
        print(f"  Internal links: {len(internal_links)}")
        
        # Show first few internal links as examples
        print("  Sample internal links:")
        for i, link in enumerate(internal_links[:10]):
            print(f"    {i+1:2d}. {link}")
        
        if len(internal_links) > 10:
            print(f"    ... and {len(internal_links) - 10} more")
    
    print(f"\n=== SUMMARY ===")
    print("This shows the types of links we're dealing with.")
    print("Many may be broken due to the site being downloaded/converted.")


if __name__ == "__main__":
    main()