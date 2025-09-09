#!/usr/bin/env python3
"""
ASN-Hunter Enhanced - Advanced ASN Reconnaissance Tool with Complete Prefix Discovery
Author: Security Researcher  
Version: 2.0.0
Purpose: Bug Bounty, Penetration Testing, Red Team Operations

ENHANCED FEATURES:
- Complete prefix discovery with pagination
- Multiple data source aggregation
- CloudScraper anti-bot bypass
- Parallel processing for speed
- Advanced BGP route analysis
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import argparse
import sys
import json
import csv
import ipaddress
import subprocess
import itertools
import threading
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from urllib.parse import quote, urlparse, parse_qs
import random
import socket
import ssl

# Try importing cloudscraper for better anti-bot capabilities
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    print("[!] cloudscraper not available. Install with: pip install cloudscraper")


# Color Configuration - Matrix/Hacker Theme
class Colors:
    HEADER = "\033[38;5;46m"      # Bright Green
    SUBHEADER = "\033[38;5;51m"   # Cyan
    SUCCESS = "\033[38;5;82m"     # Light Green
    ERROR = "\033[38;5;196m"      # Red
    WARNING = "\033[38;5;226m"    # Yellow
    INFO = "\033[38;5;87m"        # Light Cyan
    BORDER = "\033[38;5;22m"      # Dark Green
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    MAGENTA = "\033[38;5;205m"    # For enhanced features


# Enhanced ASCII Banner
BANNER = f"""{Colors.HEADER}
 █████╗ ███████╗███╗   ██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██╔══██╗██╔════╝████╗  ██║    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
███████║███████╗██╔██╗ ██║    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██║╚════██║██║╚██╗██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║███████║██║ ╚████║    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{Colors.MAGENTA}
        ┌─────────────────────────────────────────────────────────┐
        │           ENHANCED EDITION v2.0 - SHOW ALL             │
        │    Complete Prefix Discovery & Advanced Scraping       │
        └─────────────────────────────────────────────────────────┘
{Colors.RESET}
"""


# Custom Exceptions
class ASNHunterError(Exception):
    """Base exception for ASN-Hunter"""
    pass

class APIError(ASNHunterError):
    """API request failed"""
    pass

class ScrapingError(ASNHunterError):
    """Web scraping failed"""
    pass

class RateLimitError(ASNHunterError):
    """Rate limit exceeded"""
    pass


def handle_errors(func):
    """Enhanced error handler with retry logic"""
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                if attempt == max_retries - 1:
                    print(f"{Colors.ERROR}[!] Connection failed after {max_retries} attempts{Colors.RESET}")
                    return None
                time.sleep(2 ** attempt)
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    print(f"{Colors.WARNING}[!] Request timeout after {max_retries} attempts{Colors.RESET}")
                    return None
                time.sleep(2 ** attempt)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"{Colors.ERROR}[!] Access forbidden (403). Trying CloudScraper...{Colors.RESET}")
                    return None
                elif e.response.status_code == 429:
                    wait_time = 60 + (attempt * 30)
                    print(f"{Colors.WARNING}[!] Rate limited. Waiting {wait_time}s...{Colors.RESET}")
                    time.sleep(wait_time)
                else:
                    print(f"{Colors.ERROR}[!] HTTP Error {e.response.status_code}{Colors.RESET}")
                    return None
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"{Colors.ERROR}[!] Unexpected error in {func.__name__}: {e}{Colors.RESET}")
                    return None
                time.sleep(1)
    return wrapper


class EnhancedBGPScraper:
    """Enhanced BGP scraper with multiple tactics and complete prefix discovery"""
    
    def __init__(self, delay=1, use_cloudscraper=True, parallel_requests=False):
        self.delay = delay
        self.parallel_requests = parallel_requests
        self.use_cloudscraper = use_cloudscraper and CLOUDSCRAPER_AVAILABLE
        
        # User agents rotation for stealth
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
        
        # Initialize sessions
        if self.use_cloudscraper:
            print(f"{Colors.SUCCESS}[+] CloudScraper enabled for enhanced anti-bot bypass{Colors.RESET}")
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            self.session = self.scraper
        else:
            self.session = requests.Session()
            self._setup_session()
    
    def _setup_session(self):
        """Setup session with rotating headers and SSL configuration"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,de;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        # SSL context for better compatibility
        self.session.verify = True
        self.session.timeout = 20
    
    def _get_random_headers(self):
        """Get randomized headers for each request"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
    
    @handle_errors
    def get_complete_prefixes(self, asn: str, prefix_type='ipv4') -> List[str]:
        """
        Enhanced method to get ALL prefixes with pagination support
        Uses multiple tactics to discover complete prefix lists
        """
        print(f"{Colors.INFO}[*] Getting ALL {prefix_type.upper()} prefixes for AS{asn}...{Colors.RESET}")
        
        all_prefixes = set()  # Use set to avoid duplicates
        
        # Tactic 1: Standard BGP.HE.NET scraping with pagination
        prefixes = self._scrape_bgp_he_paginated(asn, prefix_type)
        if prefixes:
            all_prefixes.update(prefixes)
            print(f"{Colors.SUCCESS}  └─ BGP.HE.NET: Found {len(prefixes)} {prefix_type.upper()} prefixes{Colors.RESET}")
        
        # Tactic 2: Alternative BGP.HE.NET endpoints
        prefixes = self._scrape_bgp_he_alternative(asn, prefix_type)
        if prefixes:
            new_prefixes = set(prefixes) - all_prefixes
            all_prefixes.update(new_prefixes)
            print(f"{Colors.SUCCESS}  └─ Alternative endpoint: Found {len(new_prefixes)} additional prefixes{Colors.RESET}")
        
        # Tactic 3: RipeSTAT API (for European ASNs)
        prefixes = self._get_ripestat_prefixes(asn, prefix_type)
        if prefixes:
            new_prefixes = set(prefixes) - all_prefixes
            all_prefixes.update(new_prefixes)
            print(f"{Colors.SUCCESS}  └─ RipeSTAT API: Found {len(new_prefixes)} additional prefixes{Colors.RESET}")
        
        # Tactic 4: BGPView API prefixes
        prefixes = self._get_bgpview_prefixes(asn, prefix_type)
        if prefixes:
            new_prefixes = set(prefixes) - all_prefixes
            all_prefixes.update(new_prefixes)
            print(f"{Colors.SUCCESS}  └─ BGPView API: Found {len(new_prefixes)} additional prefixes{Colors.RESET}")
        
        # Tactic 5: WHOIS route objects
        prefixes = self._get_whois_routes(asn, prefix_type)
        if prefixes:
            new_prefixes = set(prefixes) - all_prefixes
            all_prefixes.update(new_prefixes)
            print(f"{Colors.SUCCESS}  └─ WHOIS routes: Found {len(new_prefixes)} additional prefixes{Colors.RESET}")
        
        # Tactic 6: BGP looking glass queries
        prefixes = self._query_looking_glass(asn, prefix_type)
        if prefixes:
            new_prefixes = set(prefixes) - all_prefixes
            all_prefixes.update(new_prefixes)
            print(f"{Colors.SUCCESS}  └─ Looking Glass: Found {len(new_prefixes)} additional prefixes{Colors.RESET}")
        
        final_prefixes = list(all_prefixes)
        print(f"{Colors.BOLD}[+] TOTAL {prefix_type.upper()} PREFIXES for AS{asn}: {len(final_prefixes)}{Colors.RESET}")
        
        return sorted(final_prefixes)
    
    @handle_errors
    def _scrape_bgp_he_paginated(self, asn: str, prefix_type: str) -> List[str]:
        """Enhanced BGP.HE.NET scraping with pagination support"""
        prefixes = []
        page = 1
        
        while True:
            # Construct URL with pagination
            if prefix_type == 'ipv4':
                url = f"https://bgp.he.net/AS{asn}#_prefixes"
                if page > 1:
                    url += f"?p={page}"
                table_id = 'table_prefixes4'
            else:
                url = f"https://bgp.he.net/AS{asn}#_prefixes6"
                if page > 1:
                    url += f"?p={page}"
                table_id = 'table_prefixes6'
            
            # Add randomized delay
            time.sleep(self.delay + random.uniform(0.5, 1.5))
            
            # Rotate headers for each request
            if not self.use_cloudscraper:
                self.session.headers.update(self._get_random_headers())
            
            try:
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the table
                table = soup.find('table', {'id': table_id})
                if not table:
                    # Try alternative selectors
                    tables = soup.find_all('table')
                    for t in tables:
                        if 'prefix' in str(t).lower():
                            table = t
                            break
                
                if not table:
                    break
                
                page_prefixes = []
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all('td')
                    if cells and len(cells) > 0:
                        prefix_cell = cells[0]
                        prefix_link = prefix_cell.find('a')
                        
                        if prefix_link:
                            href = prefix_link.get('href', '')
                            # Extract from href="/net/192.0.2.0/24"
                            if prefix_type == 'ipv4':
                                match = re.search(r'/net/([\d\.]+/\d+)', href)
                            else:
                                match = re.search(r'/net/([\da-fA-F:]+/\d+)', href)
                            
                            if match:
                                page_prefixes.append(match.group(1))
                            else:
                                # Fallback to text content
                                prefix_text = prefix_link.get_text(strip=True)
                                if '/' in prefix_text:
                                    if prefix_type == 'ipv4' and re.match(r'^\d+\.\d+\.\d+\.\d+/\d+$', prefix_text):
                                        page_prefixes.append(prefix_text)
                                    elif prefix_type == 'ipv6' and ':' in prefix_text:
                                        page_prefixes.append(prefix_text)
                
                if not page_prefixes:
                    break
                
                prefixes.extend(page_prefixes)
                print(f"{Colors.INFO}    └─ Page {page}: {len(page_prefixes)} prefixes{Colors.RESET}")
                
                # Check if there's a next page
                next_link = soup.find('a', string=re.compile(r'next|more|›|→', re.I))
                if not next_link:
                    # Check for numbered pagination
                    pagination = soup.find_all('a', href=re.compile(r'p=\d+'))
                    if not any(int(re.search(r'p=(\d+)', a.get('href')).group(1)) > page for a in pagination):
                        break
                
                page += 1
                
                # Safety limit
                if page > 50:
                    print(f"{Colors.WARNING}[!] Stopping pagination at page 50 for safety{Colors.RESET}")
                    break
                    
            except Exception as e:
                print(f"{Colors.ERROR}[!] Error on page {page}: {e}{Colors.RESET}")
                break
        
        return prefixes
    
    @handle_errors
    def _scrape_bgp_he_alternative(self, asn: str, prefix_type: str) -> List[str]:
        """Try alternative BGP.HE.NET endpoints and formats"""
        prefixes = []
        
        # Alternative endpoints to try
        alt_urls = [
            f"https://bgp.he.net/AS{asn}/data",
            f"https://bgp.he.net/AS{asn}/prefixes",
            f"https://bgp.he.net/AS{asn}/routes",
        ]
        
        for url in alt_urls:
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    # Try to extract prefixes from different formats
                    text = response.text
                    
                    if prefix_type == 'ipv4':
                        # Look for IPv4 CIDR patterns
                        pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})\b'
                    else:
                        # Look for IPv6 CIDR patterns
                        pattern = r'\b((?:[a-fA-F0-9]{1,4}:)+[a-fA-F0-9]{1,4}/\d{1,3})\b'
                    
                    found = re.findall(pattern, text)
                    if found:
                        prefixes.extend(found)
                        break
                        
            except:
                continue
        
        return list(set(prefixes))  # Remove duplicates
    
    @handle_errors
    def _get_ripestat_prefixes(self, asn: str, prefix_type: str) -> List[str]:
        """Query RipeSTAT API for prefix information"""
        prefixes = []
        
        # RipeSTAT announced prefixes API
        url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{asn}"
        
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok' and 'data' in data:
                for prefix_data in data['data'].get('prefixes', []):
                    prefix = prefix_data.get('prefix', '')
                    if prefix:
                        if prefix_type == 'ipv4' and '.' in prefix and ':' not in prefix:
                            prefixes.append(prefix)
                        elif prefix_type == 'ipv6' and ':' in prefix:
                            prefixes.append(prefix)
                            
        except Exception as e:
            if "stat.ripe.net" in str(e):
                pass  # RIPE STAT might not be accessible
            
        return prefixes
    
    @handle_errors
    def _get_bgpview_prefixes(self, asn: str, prefix_type: str) -> List[str]:
        """Get prefixes from BGPView API"""
        prefixes = []
        
        url = f"https://api.bgpview.io/asn/{asn}/prefixes"
        
        try:
            time.sleep(self.delay * 2)  # BGPView is more aggressive
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok' and 'data' in data:
                prefix_key = f"{prefix_type}_prefixes"
                for prefix_data in data['data'].get(prefix_key, []):
                    prefix = prefix_data.get('prefix', '')
                    if prefix:
                        prefixes.append(prefix)
                        
        except:
            pass  # BGPView might be rate limiting
            
        return prefixes
    
    @handle_errors
    def _get_whois_routes(self, asn: str, prefix_type: str) -> List[str]:
        """Query WHOIS databases for route objects"""
        prefixes = []
        
        whois_servers = [
            'whois.radb.net',
            'whois.ripe.net',
            'whois.apnic.net',
            'whois.arin.net',
        ]
        
        for server in whois_servers:
            try:
                result = subprocess.run(
                    ['whois', '-h', server, f'AS{asn}'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if prefix_type == 'ipv4' and line.startswith('route:'):
                            prefix = line.split(':', 1)[1].strip()
                            if '/' in prefix and '.' in prefix and ':' not in prefix:
                                prefixes.append(prefix)
                        elif prefix_type == 'ipv6' and line.startswith('route6:'):
                            prefix = line.split(':', 1)[1].strip()
                            if '/' in prefix and ':' in prefix:
                                prefixes.append(prefix)
                                
            except:
                continue
        
        return list(set(prefixes))
    
    @handle_errors
    def _query_looking_glass(self, asn: str, prefix_type: str) -> List[str]:
        """Query public looking glass servers for BGP routes"""
        prefixes = []
        
        # Some public looking glass servers
        lg_servers = [
            'https://lg.he.net/',
            'https://www.lookglass.org/',
        ]
        
        # This is a simplified implementation
        # In practice, each looking glass has different APIs
        for server in lg_servers:
            try:
                # This would need specific implementation for each LG
                # For now, just return empty to avoid complexity
                pass
            except:
                continue
        
        return prefixes


class EnhancedASNHunter:
    """Enhanced ASN-Hunter with parallel processing and advanced features"""
    
    def __init__(self, verbose=False, output_file=None, delay=1, show_all=True, use_parallel=True):
        self.verbose = verbose
        self.output_file = output_file
        self.delay = delay
        self.show_all = show_all
        self.use_parallel = use_parallel
        self.results = []
        
        # Initialize enhanced scraper
        self.scraper = EnhancedBGPScraper(
            delay=delay, 
            use_cloudscraper=CLOUDSCRAPER_AVAILABLE,
            parallel_requests=use_parallel
        )
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASN-Hunter-Enhanced/2.0.0 (+https://github.com/security-tools/asn-hunter)'
        })
    
    @handle_errors
    def search_peeringdb(self, keyword: str) -> List[Dict]:
        """Enhanced PeeringDB search with additional fields"""
        url = f"https://www.peeringdb.com/api/org?name__contains={quote(keyword)}"
        
        if self.verbose:
            print(f"{Colors.INFO}[*] Querying PeeringDB: {url}{Colors.RESET}")
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for org in data.get('data', []):
            if org.get('asn'):
                results.append({
                    'asn': org['asn'],
                    'name': org.get('name', ''),
                    'aka': org.get('aka', ''),
                    'name_long': org.get('name_long', ''),
                    'website': org.get('website', ''),
                    'info_type': org.get('info_type', ''),
                    'info_prefixes4': org.get('info_prefixes4', 0),
                    'info_prefixes6': org.get('info_prefixes6', 0),
                    'source': 'PeeringDB'
                })
        
        return results
    
    @handle_errors
    def search_bgpview(self, keyword: str) -> List[Dict]:
        """Enhanced BGPView search"""
        url = f"https://api.bgpview.io/search?query_term={quote(keyword)}"
        
        if self.verbose:
            print(f"{Colors.INFO}[*] Querying BGPView: {url}{Colors.RESET}")
        
        time.sleep(self.delay)
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        if data.get('status') == 'ok' and 'data' in data:
            for asn_data in data['data'].get('asns', []):
                results.append({
                    'asn': asn_data['asn'],
                    'name': asn_data.get('name', ''),
                    'description': asn_data.get('description', ''),
                    'country_code': asn_data.get('country_code', ''),
                    'rir_name': asn_data.get('rir_name', ''),
                    'email_contacts': asn_data.get('email_contacts', []),
                    'abuse_contacts': asn_data.get('abuse_contacts', []),
                    'source': 'BGPView'
                })
        
        return results
    
    def merge_results(self, peeringdb_results: List, bgpview_results: List) -> List[Dict]:
        """Enhanced result merging with better deduplication"""
        merged = {}
        
        # Process PeeringDB results
        for result in peeringdb_results:
            asn = result['asn']
            merged[asn] = {
                'asn': asn,
                'name': result.get('name', ''),
                'description': result.get('name_long', result.get('name', '')),
                'aka': result.get('aka', ''),
                'website': result.get('website', ''),
                'country': '',
                'rir': '',
                'info_type': result.get('info_type', ''),
                'prefixes_hint': {
                    'ipv4': result.get('info_prefixes4', 0),
                    'ipv6': result.get('info_prefixes6', 0)
                },
                'contacts': [],
                'sources': ['PeeringDB']
            }
        
        # Process BGPView results
        for result in bgpview_results:
            asn = result['asn']
            if asn in merged:
                # Merge with existing
                merged[asn]['sources'].append('BGPView')
                if not merged[asn]['description'] and result.get('description'):
                    merged[asn]['description'] = result['description']
                merged[asn]['country'] = result.get('country_code', '')
                merged[asn]['rir'] = result.get('rir_name', '')
                merged[asn]['contacts'] = result.get('email_contacts', [])
            else:
                # New entry
                merged[asn] = {
                    'asn': asn,
                    'name': result.get('name', ''),
                    'description': result.get('description', ''),
                    'aka': '',
                    'website': '',
                    'country': result.get('country_code', ''),
                    'rir': result.get('rir_name', ''),
                    'info_type': '',
                    'prefixes_hint': {'ipv4': 0, 'ipv6': 0},
                    'contacts': result.get('email_contacts', []),
                    'sources': ['BGPView']
                }
        
        # Convert to list and sort
        results = list(merged.values())
        results.sort(key=lambda x: x['name'].lower())
        
        return results
    
    def interactive_selection(self, results: List[Dict]) -> List[Dict]:
        """Enhanced interactive selection with filtering"""
        if not results:
            return []
        
        current_results = results.copy()
        
        while True:
            # Display header
            print(f"\n{Colors.BORDER}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"{Colors.BORDER}║{Colors.MAGENTA}                ENHANCED ASN SEARCH RESULTS                   {Colors.BORDER}║{Colors.RESET}")
            print(f"{Colors.BORDER}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
            
            # Display results
            for idx, result in enumerate(current_results, 1):
                prefix_info = ""
                if result['prefixes_hint']['ipv4'] or result['prefixes_hint']['ipv6']:
                    hints = []
                    if result['prefixes_hint']['ipv4']:
                        hints.append(f"~{result['prefixes_hint']['ipv4']} IPv4")
                    if result['prefixes_hint']['ipv6']:
                        hints.append(f"~{result['prefixes_hint']['ipv6']} IPv6")
                    prefix_info = f" ({', '.join(hints)})"
                
                print(f"{Colors.SUCCESS}[{idx}]{Colors.RESET} {Colors.BOLD}AS{result['asn']}{Colors.RESET} - {result['name']}{prefix_info}")
                if result['description']:
                    print(f"    {Colors.DIM}└─ Description:{Colors.RESET} {result['description']}")
                
                location_info = []
                if result['country']:
                    location_info.append(f"Country: {result['country']}")
                if result['rir']:
                    location_info.append(f"RIR: {result['rir']}")
                if location_info:
                    print(f"    {Colors.DIM}└─{Colors.RESET} {' | '.join(location_info)}")
                
                print(f"    {Colors.DIM}└─ Sources:{Colors.RESET} {', '.join(result['sources'])}")
                print()
            
            # Enhanced selection prompt
            print(f"{Colors.MAGENTA}Enhanced Selection Options:{Colors.RESET}")
            print(f"  • Enter numbers: 1,3,5 or ranges: 1-5")
            print(f"  • 'all' - select all ASNs")
            print(f"  • 'filter <term>' - filter results by keyword")
            print(f"  • 'reset' - reset filters")
            print(f"  • 'info <num>' - detailed info for ASN")
            print(f"  • 'q' - quit")
            print()
            
            selection = input(f"{Colors.SUBHEADER}[?] Your selection: {Colors.RESET}").strip()
            
            if selection.lower() == 'q':
                return []
            
            if selection.lower() == 'all':
                return current_results
            
            if selection.lower() == 'reset':
                current_results = results.copy()
                continue
            
            if selection.lower().startswith('filter '):
                filter_term = selection[7:].lower()
                current_results = [
                    r for r in results 
                    if filter_term in r['name'].lower() or 
                       filter_term in r['description'].lower() or
                       filter_term in str(r['asn'])
                ]
                print(f"{Colors.INFO}[*] Filtered to {len(current_results)} results{Colors.RESET}")
                continue
            
            if selection.lower().startswith('info '):
                try:
                    info_idx = int(selection[5:]) - 1
                    if 0 <= info_idx < len(current_results):
                        self._show_detailed_info(current_results[info_idx])
                    else:
                        print(f"{Colors.ERROR}[!] Invalid selection number{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.ERROR}[!] Invalid info command{Colors.RESET}")
                continue
            
            selected_indices = self.parse_selection(selection, len(current_results))
            if selected_indices:
                return [current_results[i-1] for i in selected_indices]
            else:
                print(f"{Colors.ERROR}[!] Invalid selection. Please try again.{Colors.RESET}")
    
    def _show_detailed_info(self, asn_data: Dict):
        """Show detailed information about an ASN"""
        print(f"\n{Colors.BORDER}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.HEADER}                    DETAILED ASN INFO                       {Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        
        print(f"{Colors.BOLD}ASN:{Colors.RESET} AS{asn_data['asn']}")
        print(f"{Colors.BOLD}Name:{Colors.RESET} {asn_data['name']}")
        if asn_data['description']:
            print(f"{Colors.BOLD}Description:{Colors.RESET} {asn_data['description']}")
        if asn_data['aka']:
            print(f"{Colors.BOLD}Also Known As:{Colors.RESET} {asn_data['aka']}")
        if asn_data['website']:
            print(f"{Colors.BOLD}Website:{Colors.RESET} {asn_data['website']}")
        if asn_data['country']:
            print(f"{Colors.BOLD}Country:{Colors.RESET} {asn_data['country']}")
        if asn_data['rir']:
            print(f"{Colors.BOLD}RIR:{Colors.RESET} {asn_data['rir']}")
        if asn_data['contacts']:
            print(f"{Colors.BOLD}Contacts:{Colors.RESET} {', '.join(asn_data['contacts'])}")
        
        print(f"{Colors.BOLD}Sources:{Colors.RESET} {', '.join(asn_data['sources'])}")
        
        if asn_data['prefixes_hint']['ipv4'] or asn_data['prefixes_hint']['ipv6']:
            print(f"{Colors.BOLD}Estimated Prefixes:{Colors.RESET}")
            if asn_data['prefixes_hint']['ipv4']:
                print(f"  • IPv4: ~{asn_data['prefixes_hint']['ipv4']} prefixes")
            if asn_data['prefixes_hint']['ipv6']:
                print(f"  • IPv6: ~{asn_data['prefixes_hint']['ipv6']} prefixes")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def parse_selection(self, input_str: str, max_num: int) -> List[int]:
        """Enhanced selection parsing"""
        selected = []
        
        if '-' in input_str and ',' not in input_str:
            # Range selection
            parts = input_str.split('-')
            if len(parts) == 2:
                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    return list(range(start, min(end + 1, max_num + 1)))
                except ValueError:
                    return []
        
        # Comma-separated selection
        for part in input_str.split(','):
            try:
                num = int(part.strip())
                if 1 <= num <= max_num:
                    selected.append(num)
            except ValueError:
                continue
        
        return selected
    
    def calculate_ip_space(self, prefixes: List[str]) -> int:
        """Enhanced IP space calculation"""
        total = 0
        for prefix in prefixes:
            try:
                network = ipaddress.ip_network(prefix, strict=False)
                total += network.num_addresses
            except ValueError:
                continue
        return total
    
    def save_complete_prefixes(self, prefix_data: Dict, keyword: str):
        """Save complete prefix lists to files automatically"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        base_filename = f"complete_prefixes_{keyword.replace(' ', '_')}_{timestamp}"
        
        # Save as TXT file for easy viewing and tool integration
        txt_file = results_dir / f"{base_filename}.txt"
        with open(txt_file, 'w') as f:
            f.write(f"# Complete Prefix List - {keyword}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total ASNs: {len(prefix_data)}\n")
            f.write(f"# Tool: ASN-Hunter Enhanced v2.0\n\n")
            
            total_prefixes = 0
            for asn, data in prefix_data.items():
                f.write(f"# ═══════════════════════════════════════════════════\n")
                f.write(f"# AS{asn} - {data['info']['name']}\n")
                f.write(f"# Organization: {data['info'].get('description', 'N/A')}\n")
                f.write(f"# Country: {data['info'].get('country', 'N/A')} | RIR: {data['info'].get('rir', 'N/A')}\n")
                f.write(f"# IPv4: {len(data['ipv4'])} prefixes | IPv6: {len(data['ipv6'])} prefixes\n")
                f.write(f"# ═══════════════════════════════════════════════════\n\n")
                
                if data['ipv4']:
                    f.write(f"# IPv4 Prefixes for AS{asn} ({len(data['ipv4'])} total):\n")
                    for prefix in data['ipv4']:
                        f.write(f"{prefix}\n")
                        total_prefixes += 1
                    f.write("\n")
                
                if data['ipv6']:
                    f.write(f"# IPv6 Prefixes for AS{asn} ({len(data['ipv6'])} total):\n")
                    for prefix in data['ipv6']:
                        f.write(f"{prefix}\n")
                        total_prefixes += 1
                    f.write("\n")
            
            f.write(f"# Total prefixes across all ASNs: {total_prefixes}\n")
        
        # Save as JSON for programmatic use
        json_file = results_dir / f"{base_filename}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'keyword': keyword,
                'version': '2.0',
                'asns': prefix_data
            }, f, indent=2)
        
        return {'txt_file': txt_file, 'json_file': json_file}

    def display_enhanced_results(self, prefix_data: Dict, keyword: str = "target"):
        """Enhanced results display with improved formatting and auto-save"""
        total_asns = len(prefix_data)
        total_ipv4_space = 0
        total_ipv6_space = 0
        total_ipv4_prefixes = 0
        total_ipv6_prefixes = 0
        countries = set()
        rirs = set()
        
        # Calculate comprehensive statistics
        for asn, data in prefix_data.items():
            total_ipv4_space += self.calculate_ip_space(data['ipv4'])
            total_ipv6_space += len(data['ipv6'])
            total_ipv4_prefixes += len(data['ipv4'])
            total_ipv6_prefixes += len(data['ipv6'])
            
            if data['info'].get('country'):
                countries.add(data['info']['country'])
            if data['info'].get('rir'):
                rirs.add(data['info']['rir'])
        
        # Save complete results first
        saved_files = self.save_complete_prefixes(prefix_data, keyword)
        
        # Clean professional header - no emojis, perfect alignment
        box_width = 80
        
        print(f"\n{Colors.HEADER}╔{'═' * (box_width - 2)}╗{Colors.RESET}")
        
        # Properly center the main title
        main_title = "ASN RECONNAISSANCE REPORT v2.0"
        title_padding = (box_width - 2 - len(main_title)) // 2
        title_line = f"{' ' * title_padding}{Colors.BOLD}{main_title}{Colors.RESET}{' ' * (box_width - 2 - len(main_title) - title_padding)}"
        print(f"{Colors.HEADER}║{title_line}{Colors.HEADER}║{Colors.RESET}")
        
        print(f"{Colors.HEADER}╠{'═' * (box_width - 2)}╣{Colors.RESET}")
        
        # Target and timestamp with dots for professional look
        target_text = f"Target Organization"
        target_value = keyword
        target_dots = box_width - 6 - len(target_text) - len(target_value)
        print(f"{Colors.HEADER}║{Colors.RESET} {target_text} {'.' * target_dots} {target_value} {Colors.HEADER}║{Colors.RESET}")
        
        timestamp_text = f"Report Generated"
        timestamp_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp_dots = box_width - 6 - len(timestamp_text) - len(timestamp_value)
        print(f"{Colors.HEADER}║{Colors.RESET} {timestamp_text} {'.' * timestamp_dots} {timestamp_value} {Colors.HEADER}║{Colors.RESET}")
        
        print(f"{Colors.HEADER}╠{'═' * (box_width - 2)}╣{Colors.RESET}")
        
        # Properly center the statistics title
        stats_title = "SUMMARY STATISTICS"
        stats_padding = (box_width - 2 - len(stats_title)) // 2
        stats_line = f"{' ' * stats_padding}{Colors.BOLD}{stats_title}{Colors.RESET}{' ' * (box_width - 2 - len(stats_title) - stats_padding)}"
        print(f"{Colors.HEADER}║{stats_line}{Colors.HEADER}║{Colors.RESET}")
        print(f"{Colors.HEADER}╠{'═' * (box_width - 2)}╣{Colors.RESET}")
        
        # Statistics with clean text indicators and proper alignment
        stats = [
            ("ASNs Analyzed", str(total_asns)),
            ("IPv4 Prefixes Found", str(total_ipv4_prefixes)),
            ("IPv6 Prefixes Found", str(total_ipv6_prefixes)),
            ("Total IPv4 Address Space", f"{total_ipv4_space:,}"),
            ("Geographic Coverage", f"{len(countries)} countries, {len(rirs)} RIRs")
        ]
        
        for label, value in stats:
            dots_count = box_width - 6 - len(label) - len(value)
            print(f"{Colors.HEADER}║{Colors.RESET} {label} {'.' * dots_count} {Colors.SUCCESS}{value}{Colors.RESET} {Colors.HEADER}║{Colors.RESET}")
        
        print(f"{Colors.HEADER}╚{'═' * (box_width - 2)}╝{Colors.RESET}")
        print()
        
        # Clean file save notification
        print(f"\n{Colors.SUCCESS}COMPLETE PREFIX DATA AUTOMATICALLY SAVED:{Colors.RESET}")
        print(f"   ├─ Complete list: {saved_files['txt_file']}")
        print(f"   └─ JSON format:   {saved_files['json_file']}")
        print()
        
        # ASN-by-ASN detailed analysis with improved display
        for idx, (asn, data) in enumerate(prefix_data.items(), 1):
            info = data['info']
            ipv4_count = len(data['ipv4'])
            ipv6_count = len(data['ipv6'])
            ipv4_space = self.calculate_ip_space(data['ipv4'])
            
            # Clean ASN header without emojis - perfectly calculated width
            box_width = 92
            asn_title = f"AS{asn} - {info['name']}"
            # Ensure title fits within available space
            max_title_length = box_width - 8  # Account for "┌─[ " and " ]" and border chars
            if len(asn_title) > max_title_length:
                asn_title = asn_title[:max_title_length - 3] + "..."
            
            # Calculate exact padding for perfect alignment
            title_section_length = 4 + len(asn_title) + 2  # "┌─[ " + title + " ]"
            padding = box_width - title_section_length - 1  # -1 for closing "┐"
            print(f"{Colors.BORDER}┌─[ {Colors.BOLD}{asn_title}{Colors.RESET}{Colors.BORDER} ]{'─' * max(0, padding)}┐{Colors.RESET}")
            print(f"{Colors.BORDER}│{' ' * (box_width - 2)}{Colors.BORDER}│{Colors.RESET}")
            
            # Organization details with clean formatting  
            if info['description']:
                desc = info['description']
                max_desc_length = box_width - len(" Organization.....: ") - 2  # -2 for borders
                if len(desc) > max_desc_length:
                    desc = desc[:max_desc_length - 3] + "..."
                org_line = f" Organization.....: {Colors.BOLD}{desc}{Colors.RESET}"
                padding = box_width - len(f" Organization.....: {desc}") - 2
                print(f"{Colors.BORDER}│{org_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # Geographic information with region mapping
            location_parts = []
            if info.get('country'):
                location_parts.append(f"Country: {info['country']}")
            if info.get('rir'):
                location_parts.append(f"RIR: {info['rir']}")
                # Add region info based on RIR
                region_map = {
                    'ARIN': 'North America', 'RIPE': 'Europe/Middle East', 
                    'APNIC': 'Asia-Pacific', 'LACNIC': 'Latin America', 'AFRINIC': 'Africa'
                }
                region = region_map.get(info['rir'], '')
                if region:
                    location_parts.append(f"Region: {region}")
            
            if location_parts:
                location_str = " | ".join(location_parts)
                max_geo_length = box_width - len(" Geographic.......: ") - 2  # -2 for borders
                if len(location_str) > max_geo_length:
                    location_str = location_str[:max_geo_length - 3] + "..."
                geo_line = f" Geographic.......: {Colors.MAGENTA}{location_str}{Colors.RESET}"
                padding = box_width - len(f" Geographic.......: {location_str}") - 2
                print(f"{Colors.BORDER}│{geo_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # Data sources
            sources_str = ", ".join(info['sources']) + " + Enhanced Discovery"
            max_sources_length = box_width - len(" Data Sources.....: ") - 2  # -2 for borders
            if len(sources_str) > max_sources_length:
                sources_str = sources_str[:max_sources_length - 3] + "..."
            sources_line = f" Data Sources.....: {Colors.INFO}{sources_str}{Colors.RESET}"
            padding = box_width - len(f" Data Sources.....: {sources_str}") - 2
            print(f"{Colors.BORDER}│{sources_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{' ' * (box_width - 2)}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv4 Prefixes with clean display
            if data['ipv4']:
                display_limit = min(ipv4_count, 10)
                ipv4_header_line = f" IPv4 Prefixes....: {Colors.SUCCESS}{ipv4_count} total{Colors.RESET}"
                padding = box_width - len(f" IPv4 Prefixes....: {ipv4_count} total") - 2
                print(f"{Colors.BORDER}│{ipv4_header_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                if ipv4_count > 10:
                    display_info = f" Display..........: First 10, complete list saved to file"
                    padding = box_width - len(display_info) - 2
                    print(f"{Colors.BORDER}│{display_info}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                for i, prefix in enumerate(data['ipv4'][:display_limit]):
                    try:
                        network = ipaddress.ip_network(prefix, strict=False)
                        ip_count = network.num_addresses
                        
                        # Network type indicators (text-based)
                        if network.is_private:
                            net_type = "Private"
                        elif network.is_global:
                            net_type = "Global"
                        else:
                            net_type = "Other"
                        
                        count_str = f"[{ip_count:,} IPs]"
                        prefix_display = f"{prefix:<22} {count_str:<12} ({net_type})"
                        
                        # Calculate max length for network display
                        connector = "├─" if i < display_limit - 1 else "└─"
                        prefix_label = f" {connector} Network.......: "
                        max_prefix_length = box_width - len(prefix_label) - 2  # -2 for borders
                        
                        if len(prefix_display) > max_prefix_length:
                            prefix_display = prefix_display[:max_prefix_length - 3] + "..."
                        
                        prefix_line = f"{prefix_label}{Colors.INFO}{prefix_display}{Colors.RESET}"
                        padding = box_width - len(f"{prefix_label}{prefix_display}") - 2
                        print(f"{Colors.BORDER}│{prefix_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                        
                    except ValueError:
                        connector = "├─" if i < display_limit - 1 else "└─"
                        prefix_label = f" {connector} Network.......: "
                        max_prefix_length = box_width - len(prefix_label) - 2  # -2 for borders
                        
                        prefix_display = prefix
                        if len(prefix_display) > max_prefix_length:
                            prefix_display = prefix_display[:max_prefix_length - 3] + "..."
                        
                        prefix_line = f"{prefix_label}{Colors.INFO}{prefix_display}{Colors.RESET}"
                        padding = box_width - len(f"{prefix_label}{prefix_display}") - 2
                        print(f"{Colors.BORDER}│{prefix_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                if ipv4_count > display_limit:
                    remaining = ipv4_count - display_limit
                    remaining_line = f"    + {remaining} more prefixes in saved files"
                    padding = box_width - len(remaining_line) - 2
                    print(f"{Colors.BORDER}│{remaining_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                print(f"{Colors.BORDER}│{' ' * (box_width - 2)}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv6 Prefixes with clean display
            if data['ipv6']:
                display_limit_v6 = min(ipv6_count, 8)
                ipv6_header_line = f" IPv6 Prefixes....: {Colors.INFO}{ipv6_count} total{Colors.RESET}"
                padding = box_width - len(f" IPv6 Prefixes....: {ipv6_count} total") - 2
                print(f"{Colors.BORDER}│{ipv6_header_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                if ipv6_count > 8:
                    display_info = f" Display..........: First 8, complete list saved to file"
                    padding = box_width - len(display_info) - 2
                    print(f"{Colors.BORDER}│{display_info}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                for i, prefix in enumerate(data['ipv6'][:display_limit_v6]):
                    connector = "├─" if i < display_limit_v6 - 1 else "└─"
                    prefix_label = f" {connector} Network.......: "
                    max_prefix_length = box_width - len(prefix_label) - 2  # -2 for borders
                    
                    prefix_display = prefix
                    if len(prefix_display) > max_prefix_length:
                        prefix_display = prefix_display[:max_prefix_length - 3] + "..."
                    
                    prefix_line = f"{prefix_label}{Colors.INFO}{prefix_display}{Colors.RESET}"
                    padding = box_width - len(f"{prefix_label}{prefix_display}") - 2
                    print(f"{Colors.BORDER}│{prefix_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                if ipv6_count > display_limit_v6:
                    remaining_v6 = ipv6_count - display_limit_v6
                    remaining_line = f"    + {remaining_v6} more prefixes in saved files"
                    padding = box_width - len(remaining_line) - 2
                    print(f"{Colors.BORDER}│{remaining_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
                
                print(f"{Colors.BORDER}│{' ' * (box_width - 2)}{Colors.BORDER}│{Colors.RESET}")
            
            # Network Analysis with clean formatting
            analysis_header = f" NETWORK ANALYSIS.:"
            padding = box_width - len(analysis_header) - 2
            print(f"{Colors.BORDER}│{analysis_header}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # Total IPv4 addresses
            addr_line = f" • Total IPv4 addresses.......: {Colors.SUCCESS}{ipv4_space:,}{Colors.RESET}"
            padding = box_width - len(f" • Total IPv4 addresses.......: {ipv4_space:,}") - 2
            print(f"{Colors.BORDER}│{addr_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # Calculate /24 equivalent for context
            equivalent_24s = ipv4_space // 256
            if equivalent_24s > 0:
                nets_line = f" • Equivalent /24 networks....: {Colors.INFO}{equivalent_24s:,}{Colors.RESET}"
                padding = box_width - len(f" • Equivalent /24 networks....: {equivalent_24s:,}") - 2
                print(f"{Colors.BORDER}│{nets_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv4 prefixes discovered
            ipv4_line = f" • IPv4 prefixes discovered...: {Colors.SUCCESS}{ipv4_count}{Colors.RESET}"
            padding = box_width - len(f" • IPv4 prefixes discovered...: {ipv4_count}") - 2
            print(f"{Colors.BORDER}│{ipv4_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv6 prefixes discovered
            ipv6_line = f" • IPv6 prefixes discovered...: {Colors.INFO}{ipv6_count}{Colors.RESET}"
            padding = box_width - len(f" • IPv6 prefixes discovered...: {ipv6_count}") - 2
            print(f"{Colors.BORDER}│{ipv6_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            # Coverage estimate with text indicator
            if info.get('prefixes_hint', {}).get('ipv4', 0) > 0:
                expected = info['prefixes_hint']['ipv4']
                coverage = min(100, (ipv4_count / expected) * 100)
                if coverage > 90:
                    indicator = "EXCELLENT"
                elif coverage > 70:
                    indicator = "GOOD"
                else:
                    indicator = "PARTIAL"
                coverage_line = f" • Coverage estimate..........: {Colors.MAGENTA}{coverage:.1f}% ({indicator}){Colors.RESET}"
                padding = box_width - len(f" • Coverage estimate..........: {coverage:.1f}% ({indicator})") - 2
                print(f"{Colors.BORDER}│{coverage_line}{' ' * max(0, padding)}{Colors.BORDER}│{Colors.RESET}")
            
            print(f"{Colors.BORDER}└{'─' * (box_width - 2)}┘{Colors.RESET}")
            
            # Add spacing between ASNs except for the last one
            if idx < len(prefix_data):
                print()
        
        # Clean completion summary with consistent formatting
        total_all_prefixes = total_ipv4_prefixes + total_ipv6_prefixes
        print(f"\n{Colors.SUCCESS}RECONNAISSANCE COMPLETE:{Colors.RESET}")
        print(f"   • {total_all_prefixes} total prefixes discovered across {total_asns} ASNs")
        print(f"   • {total_ipv4_space:,} IPv4 addresses mapped")
        print(f"   • Geographic coverage: {len(countries)} countries, {len(rirs)} RIRs")
        print(f"   • Complete data saved: {saved_files['txt_file'].name}")
        
        # Interactive file opening option
        if total_all_prefixes > 25:  # Only show for substantial results
            choice = input(f"\n{Colors.WARNING}Open complete prefix file? (y/N): {Colors.RESET}").strip().lower()
            if choice == 'y':
                try:
                    import os
                    if sys.platform == "darwin":  # macOS
                        os.system(f'open "{saved_files["txt_file"]}"')
                    elif sys.platform.startswith("linux"):  # Linux
                        os.system(f'xdg-open "{saved_files["txt_file"]}" 2>/dev/null &')
                    elif sys.platform == "win32":  # Windows
                        os.startfile(str(saved_files['txt_file']))
                    print(f"{Colors.SUCCESS}[+] Opened complete prefix file{Colors.RESET}")
                except Exception:
                    print(f"{Colors.INFO}[*] File location: {saved_files['txt_file']}{Colors.RESET}")
        
        print()
    
    def run_parallel_prefix_collection(self, selected_asns: List[Dict]) -> Dict:
        """Collect prefixes in parallel for speed"""
        prefix_data = {}
        
        def collect_asn_prefixes(asn_info):
            asn = str(asn_info['asn'])
            try:
                # Get IPv4 prefixes
                ipv4_prefixes = self.scraper.get_complete_prefixes(asn, 'ipv4')
                
                # Get IPv6 prefixes
                ipv6_prefixes = self.scraper.get_complete_prefixes(asn, 'ipv6')
                
                return {
                    asn: {
                        'info': asn_info,
                        'ipv4': ipv4_prefixes,
                        'ipv6': ipv6_prefixes
                    }
                }
            except Exception as e:
                print(f"{Colors.ERROR}[!] Error processing AS{asn}: {e}{Colors.RESET}")
                return {asn: {'info': asn_info, 'ipv4': [], 'ipv6': []}}
        
        if self.use_parallel and len(selected_asns) > 1:
            print(f"{Colors.MAGENTA}[*] Using parallel processing for {len(selected_asns)} ASNs...{Colors.RESET}")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(collect_asn_prefixes, asn_info): asn_info for asn_info in selected_asns}
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    prefix_data.update(result)
        else:
            # Sequential processing
            for idx, asn_info in enumerate(selected_asns, 1):
                print(f"{Colors.INFO}[*] [{idx}/{len(selected_asns)}] Processing AS{asn_info['asn']}...{Colors.RESET}")
                result = collect_asn_prefixes(asn_info)
                prefix_data.update(result)
        
        return prefix_data
    
    def export_enhanced_results(self, prefix_data: Dict, format_type='json'):
        """Enhanced export with additional metadata"""
        if not self.output_file:
            return
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'total_asns': len(prefix_data),
            'collection_method': 'enhanced_multi_source',
            'sources_used': [
                'BGP.HE.NET', 'PeeringDB', 'BGPView', 'RipeSTAT', 
                'WHOIS', 'Looking Glass'
            ],
            'asns': {}
        }
        
        total_ipv4_space = 0
        total_prefixes = 0
        
        for asn, data in prefix_data.items():
            ipv4_space = self.calculate_ip_space(data['ipv4'])
            total_ipv4_space += ipv4_space
            total_prefixes += len(data['ipv4']) + len(data['ipv6'])
            
            export_data['asns'][asn] = {
                'info': data['info'],
                'ipv4_prefixes': data['ipv4'],
                'ipv6_prefixes': data['ipv6'],
                'ipv4_count': len(data['ipv4']),
                'ipv6_count': len(data['ipv6']),
                'total_ipv4_addresses': ipv4_space,
                'collection_completeness': 'enhanced'
            }
        
        export_data['summary'] = {
            'total_ipv4_addresses': total_ipv4_space,
            'total_prefixes': total_prefixes,
            'collection_timestamp': datetime.now().isoformat()
        }
        
        if format_type == 'json':
            with open(self.output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif format_type == 'csv':
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ASN', 'Name', 'Description', 'Country', 'RIR',
                    'IPv4_Count', 'IPv6_Count', 'Total_IPv4_IPs',
                    'IPv4_Prefixes', 'IPv6_Prefixes', 'Sources'
                ])
                for asn, data in prefix_data.items():
                    info = data['info']
                    writer.writerow([
                        asn, info['name'], info['description'], 
                        info['country'], info['rir'],
                        len(data['ipv4']), len(data['ipv6']),
                        self.calculate_ip_space(data['ipv4']),
                        ';'.join(data['ipv4']), ';'.join(data['ipv6']),
                        ','.join(info['sources'])
                    ])
    
    def run(self, keyword: str):
        """Enhanced main execution flow"""
        
        # Display enhanced banner
        print(BANNER)
        
        if CLOUDSCRAPER_AVAILABLE:
            print(f"{Colors.SUCCESS}[+] CloudScraper enabled for enhanced scraping{Colors.RESET}")
        if self.use_parallel:
            print(f"{Colors.SUCCESS}[+] Parallel processing enabled{Colors.RESET}")
        if self.show_all:
            print(f"{Colors.MAGENTA}[+] SHOW ALL mode: Complete prefix discovery enabled{Colors.RESET}")
        
        # Step 1: Enhanced organization search
        print(f"\n{Colors.INFO}[*] Searching for organizations matching '{keyword}'...{Colors.RESET}")
        
        peeringdb_results = self.search_peeringdb(keyword)
        if peeringdb_results:
            print(f"{Colors.SUCCESS}[+] Found {len(peeringdb_results)} results from PeeringDB{Colors.RESET}")
        
        bgpview_results = self.search_bgpview(keyword)
        if bgpview_results:
            print(f"{Colors.SUCCESS}[+] Found {len(bgpview_results)} results from BGPView{Colors.RESET}")
        
        # Step 2: Enhanced merging
        all_results = self.merge_results(peeringdb_results or [], bgpview_results or [])
        print(f"{Colors.INFO}[*] Total unique ASNs found: {len(all_results)}{Colors.RESET}")
        
        if not all_results:
            print(f"{Colors.ERROR}[!] No organizations found for '{keyword}'{Colors.RESET}")
            return
        
        # Step 3: Enhanced interactive selection
        selected = self.interactive_selection(all_results)
        
        if not selected:
            print(f"{Colors.WARNING}[!] No ASNs selected. Exiting.{Colors.RESET}")
            return
        
        print(f"{Colors.MAGENTA}[*] Collecting COMPLETE prefix data for {len(selected)} ASN(s)...{Colors.RESET}")
        print(f"{Colors.INFO}[*] This may take longer due to comprehensive discovery{Colors.RESET}")
        
        # Step 4: Enhanced prefix collection
        prefix_data = self.run_parallel_prefix_collection(selected)
        
        # Step 5: Enhanced results display
        self.display_enhanced_results(prefix_data, keyword)
        
        # Step 6: Enhanced export
        if self.output_file:
            format_type = 'json'
            if self.output_file.endswith('.csv'):
                format_type = 'csv'
            
            self.export_enhanced_results(prefix_data, format_type)
            print(f"{Colors.SUCCESS}[+] Enhanced results exported to {self.output_file}{Colors.RESET}")
        
        # Display collection summary
        total_prefixes = sum(len(data['ipv4']) + len(data['ipv6']) for data in prefix_data.values())
        print(f"\n{Colors.MAGENTA}[+] COLLECTION COMPLETE: {total_prefixes} total prefixes discovered{Colors.RESET}")


def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(
        description='ASN-Hunter Enhanced - Complete ASN Reconnaissance with Advanced Tactics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Enhanced Examples:
  python3 asn-hunter-enhanced.py tesla --show-all
  python3 asn-hunter-enhanced.py "cloudflare" -v --parallel
  python3 asn-hunter-enhanced.py amazon -o complete_results.json --show-all
  python3 asn-hunter-enhanced.py meta --no-parallel --delay 3
        """
    )
    
    parser.add_argument('keyword', help='Organization name to search')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file (json/csv)')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--delay', type=int, default=1, help='Delay between requests (seconds)')
    parser.add_argument('--show-all', action='store_true', default=True, help='Show all prefixes (default: True)')
    parser.add_argument('--no-show-all', action='store_true', help='Limit prefix display')
    parser.add_argument('--parallel', action='store_true', default=True, help='Use parallel processing (default: True)')
    parser.add_argument('--no-parallel', action='store_true', help='Disable parallel processing')
    
    args = parser.parse_args()
    
    if args.no_color:
        # Disable colors
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    show_all = args.show_all and not args.no_show_all
    use_parallel = args.parallel and not args.no_parallel
    
    try:
        hunter = EnhancedASNHunter(
            verbose=args.verbose, 
            output_file=args.output, 
            delay=args.delay,
            show_all=show_all,
            use_parallel=use_parallel
        )
        hunter.run(args.keyword)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Interrupted by user. Exiting...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.ERROR}[!] Fatal error: {e}{Colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()