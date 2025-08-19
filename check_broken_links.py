#!/usr/bin/env python3
"""
Script to scan HTML files for broken internal links after filename cleanup.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
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
        
        # Find src attributes (for images, scripts, etc.)
        src_pattern = r'src=["\']([^"\']+)["\']'
        for match in re.finditer(src_pattern, content, re.IGNORECASE):
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
        print(f"Error normalizing path {url}: {e}")
        return None


def check_file_exists(normalized_path, site_root):
    """Check if a normalized path exists in the site."""
    try:
        full_path = site_root / normalized_path
        return full_path.exists()
    except Exception:
        return False


def main():
    site_root = Path("D:/Dropbox/Weathermakers")
    blog_root = site_root / "blog"
    
    if not site_root.exists():
        print(f"Site directory not found: {site_root}")
        return
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(site_root):
        for file in files:
            if file.endswith('.html'):
                html_files.append(Path(root) / file)
    
    print(f"Found {len(html_files)} HTML files to scan")
    
    broken_links = defaultdict(list)
    total_links_checked = 0
    
    for html_file in html_files:
        print(f"Scanning: {html_file.relative_to(site_root)}")
        
        links = extract_links_from_html(html_file)
        internal_links = [link for link in links if is_internal_link(link)]
        
        for link in internal_links:
            total_links_checked += 1
            
            # Normalize the link to a file path
            normalized_path = normalize_path(link, html_file, site_root)
            if not normalized_path:
                continue
            
            # Check if the target file exists
            if not check_file_exists(normalized_path, site_root):
                broken_links[str(html_file.relative_to(site_root))].append({
                    'original_link': link,
                    'normalized_path': normalized_path,
                    'target_should_be': site_root / normalized_path
                })
    
    # Report results
    print(f"\n{'='*80}")
    print(f"BROKEN LINKS REPORT")
    print(f"{'='*80}")
    print(f"Total HTML files scanned: {len(html_files)}")
    print(f"Total internal links checked: {total_links_checked}")
    print(f"Files with broken links: {len(broken_links)}")
    print(f"Total broken links: {sum(len(links) for links in broken_links.values())}")
    
    if broken_links:
        print(f"\nBROKEN LINKS BY FILE:")
        print(f"{'-'*80}")
        
        for file_path, links in broken_links.items():
            print(f"\nFile: {file_path} ({len(links)} broken links):")
            for link_info in links:
                print(f"  BROKEN: {link_info['original_link']}")
                print(f"     Expected: {link_info['normalized_path']}")
                print(f"     Should be: {link_info['target_should_be']}")
        
        # Generate a summary of most common broken link patterns
        all_broken = []
        for links in broken_links.values():
            all_broken.extend([link['normalized_path'] for link in links])
        
        from collections import Counter
        common_broken = Counter(all_broken).most_common(10)
        
        print(f"\nMOST COMMON BROKEN LINKS:")
        print(f"{'-'*80}")
        for path, count in common_broken:
            print(f"  {count:3d}x  {path}")
    else:
        print("\nSUCCESS: No broken internal links found!")


if __name__ == "__main__":
    main()