#!/usr/bin/env python3
"""
ASN-Hunter - Advanced ASN Reconnaissance Tool
Author: Security Researcher
Version: 1.0.0
Purpose: Bug Bounty, Penetration Testing, Red Team Operations
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
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from urllib.parse import quote


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


# ASCII Banner
BANNER = f"""{Colors.HEADER}
 █████╗ ███████╗███╗   ██╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██╔══██╗██╔════╝████╗  ██║    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
███████║███████╗██╔██╗ ██║    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██║╚════██║██║╚██╗██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║███████║██║ ╚████║    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{Colors.SUBHEADER}
        ┌─────────────────────────────────────────────────────────┐
        │  Advanced ASN Reconnaissance & Network Mapping Tool    │
        │           For Bug Bounty & Penetration Testing         │
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
    """Decorator for comprehensive error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            print(f"{Colors.ERROR}[!] Connection failed. Check your internet connection.{Colors.RESET}")
            return None
        except requests.exceptions.Timeout:
            print(f"{Colors.WARNING}[!] Request timeout. Retrying...{Colors.RESET}")
            time.sleep(2)
            try:
                return func(*args, **kwargs)
            except:
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"{Colors.ERROR}[!] Access forbidden. May need to update User-Agent.{Colors.RESET}")
            elif e.response.status_code == 429:
                print(f"{Colors.WARNING}[!] Rate limited. Waiting 60 seconds...{Colors.RESET}")
                time.sleep(60)
                try:
                    return func(*args, **kwargs)
                except:
                    return None
            else:
                print(f"{Colors.ERROR}[!] HTTP Error {e.response.status_code}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.ERROR}[!] Unexpected error in {func.__name__}: {e}{Colors.RESET}")
            return None
    return wrapper


class BGPHEScraper:
    """BGP.HE.NET web scraper with anti-bot measures"""
    
    def __init__(self, delay=1):
        self.delay = delay
        self.session = requests.Session()
        # CRITICAL: Set headers to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    @handle_errors
    def get_ipv4_prefixes(self, asn: str) -> List[str]:
        """Scrape IPv4 prefixes from bgp.he.net"""
        url = f"https://bgp.he.net/AS{asn}#_prefixes"
        
        # Add delay to avoid rate limiting
        time.sleep(self.delay)
        
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prefixes = []
        
        # Method 1: Find by table id
        table = soup.find('table', {'id': 'table_prefixes4'})
        if not table:
            # Method 2: Find by section header
            header = soup.find('div', {'id': 'prefixes'})
            if header:
                table = header.find_next('table')
        
        if table:
            for row in table.find_all('tr')[1:]:  # Skip header row
                cells = row.find_all('td')
                if cells and cells[0].find('a'):
                    prefix_link = cells[0].find('a')
                    # Extract prefix from href="/net/192.0.2.0/24"
                    href = prefix_link.get('href', '')
                    match = re.search(r'/net/([\d\.]+/\d+)', href)
                    if match:
                        prefixes.append(match.group(1))
                    else:
                        # Fallback: get text content
                        prefix_text = prefix_link.get_text(strip=True)
                        if '/' in prefix_text and re.match(r'^\d+\.\d+\.\d+\.\d+/\d+$', prefix_text):
                            prefixes.append(prefix_text)
        
        return prefixes
    
    @handle_errors
    def get_ipv6_prefixes(self, asn: str) -> List[str]:
        """Scrape IPv6 prefixes from bgp.he.net"""
        url = f"https://bgp.he.net/AS{asn}#_prefixes6"
        
        time.sleep(self.delay)
        
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prefixes = []
        
        # Find IPv6 table
        table = soup.find('table', {'id': 'table_prefixes6'})
        if not table:
            # Alternative: look for the prefixes6 section
            header = soup.find('div', {'id': 'prefixes6'})
            if header:
                table = header.find_next('table')
        
        if table:
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if cells and cells[0].find('a'):
                    prefix_link = cells[0].find('a')
                    href = prefix_link.get('href', '')
                    # Extract IPv6 prefix from href="/net/2001:db8::/32"
                    match = re.search(r'/net/([\da-fA-F:]+/\d+)', href)
                    if match:
                        prefixes.append(match.group(1))
                    else:
                        prefix_text = prefix_link.get_text(strip=True)
                        if '/' in prefix_text and ':' in prefix_text:
                            prefixes.append(prefix_text)
        
        return prefixes
    
    @handle_errors
    def get_asn_details(self, asn: str) -> Dict:
        """Scrape general ASN information from main page"""
        url = f"https://bgp.he.net/AS{asn}"
        
        response = self.session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            "asn": asn,
            "name": "",
            "organization": "",
            "country": ""
        }
        
        # Extract AS name from page title or header
        title = soup.find('title')
        if title:
            # Format: "AS13335 - CLOUDFLARENET - Cloudflare, Inc."
            match = re.search(r'AS\d+ - ([\w-]+) - (.+)', title.text)
            if match:
                details["name"] = match.group(1)
                details["organization"] = match.group(2)
        
        return details


class ASNHunter:
    """Main ASN-Hunter application class"""
    
    def __init__(self, verbose=False, output_file=None, delay=1):
        self.verbose = verbose
        self.output_file = output_file
        self.delay = delay
        self.results = []
        self.scraper = BGPHEScraper(delay=delay)
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASN-Hunter/1.0.0 (+https://github.com/security-tools/asn-hunter)'
        })
    
    @handle_errors
    def search_peeringdb(self, keyword: str) -> List[Dict]:
        """Query PeeringDB API for organizations"""
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
        """Query BGPView API for ASNs"""
        url = f"https://api.bgpview.io/search?query_term={quote(keyword)}"
        
        if self.verbose:
            print(f"{Colors.INFO}[*] Querying BGPView: {url}{Colors.RESET}")
        
        # BGPView is more aggressive with rate limiting
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
        """Merge and deduplicate results from both sources"""
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
        
        # Sort by relevance (exact matches first, then partial matches)
        def sort_key(item):
            name = item['name'].lower()
            desc = item['description'].lower()
            keyword = keyword.lower() if 'keyword' in locals() else ''
            
            if keyword in name:
                return (0, name)
            elif keyword in desc:
                return (1, name)
            else:
                return (2, name)
        
        try:
            results.sort(key=sort_key)
        except:
            # Fallback sort by name
            results.sort(key=lambda x: x['name'].lower())
        
        return results
    
    def interactive_selection(self, results: List[Dict]) -> List[Dict]:
        """Interactive selection interface with multiple input methods"""
        if not results:
            return []
        
        while True:
            # Display header
            print(f"\n{Colors.BORDER}╔═══════════════════════════════════════════════════════════════╗{Colors.RESET}")
            print(f"{Colors.BORDER}║{Colors.HEADER}                    ASN SEARCH RESULTS                         {Colors.BORDER}║{Colors.RESET}")
            print(f"{Colors.BORDER}╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
            
            # Display results
            for idx, result in enumerate(results, 1):
                print(f"{Colors.SUCCESS}[{idx}]{Colors.RESET} {Colors.BOLD}AS{result['asn']}{Colors.RESET} - {result['name']}")
                if result['description']:
                    print(f"    {Colors.DIM}└─ Description:{Colors.RESET} {result['description']}")
                
                country_rir = []
                if result['country']:
                    country_rir.append(f"Country: {result['country']}")
                if result['rir']:
                    country_rir.append(f"RIR: {result['rir']}")
                if country_rir:
                    print(f"    {Colors.DIM}└─{Colors.RESET} {' | '.join(country_rir)}")
                
                print(f"    {Colors.DIM}└─ Sources:{Colors.RESET} {', '.join(result['sources'])}")
                
                if result['prefixes_hint']['ipv4'] or result['prefixes_hint']['ipv6']:
                    hints = []
                    if result['prefixes_hint']['ipv4']:
                        hints.append(f"~{result['prefixes_hint']['ipv4']} IPv4")
                    if result['prefixes_hint']['ipv6']:
                        hints.append(f"~{result['prefixes_hint']['ipv6']} IPv6")
                    print(f"    {Colors.DIM}└─ Prefix Hints:{Colors.RESET} {', '.join(hints)}")
                
                print()
            
            # Selection prompt
            print(f"{Colors.INFO}Selection Options:{Colors.RESET}")
            print(f"  • Enter numbers separated by commas (e.g., 1,3,5)")
            print(f"  • Enter range (e.g., 1-5)")
            print(f"  • Enter 'all' to select all")
            print(f"  • Enter 'q' to quit")
            print()
            
            selection = input(f"{Colors.SUBHEADER}[?] Your selection: {Colors.RESET}").strip()
            
            if selection.lower() == 'q':
                return []
            
            if selection.lower() == 'all':
                return results
            
            selected_indices = self.parse_selection(selection, len(results))
            if selected_indices:
                return [results[i-1] for i in selected_indices]
            else:
                print(f"{Colors.ERROR}[!] Invalid selection. Please try again.{Colors.RESET}")
    
    def parse_selection(self, input_str: str, max_num: int) -> List[int]:
        """Parse user input for selection"""
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
        """Calculate total IP address space from CIDR prefixes"""
        total = 0
        for prefix in prefixes:
            try:
                network = ipaddress.ip_network(prefix, strict=False)
                total += network.num_addresses
            except ValueError:
                continue
        return total
    
    def display_results(self, prefix_data: Dict):
        """Display final reconnaissance report"""
        total_asns = len(prefix_data)
        total_ipv4_space = 0
        total_ipv6_space = 0
        
        # Calculate totals
        for asn, data in prefix_data.items():
            total_ipv4_space += self.calculate_ip_space(data['ipv4'])
            total_ipv6_space += len(data['ipv6'])  # Count of /64 subnets approximation
        
        # Header
        print(f"\n{Colors.BORDER}╔════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.HEADER}                         RECONNAISSANCE REPORT                      {Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}╠════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} ASNs Analyzed: {total_asns:<53}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} Total IPv4 Space: {total_ipv4_space:,} addresses{' ' * (37 - len(f'{total_ipv4_space:,}'))}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} Total IPv6 Prefixes: {total_ipv6_space:<42}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
        
        # Details for each ASN
        for asn, data in prefix_data.items():
            info = data['info']
            ipv4_count = len(data['ipv4'])
            ipv6_count = len(data['ipv6'])
            ipv4_space = self.calculate_ip_space(data['ipv4'])
            
            print(f"{Colors.BORDER}┌─[ {Colors.BOLD}AS{asn}{Colors.RESET}{Colors.BORDER} - {info['name']} ]{'─' * (50 - len(asn) - len(info['name']))}┐{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            if info['description']:
                print(f"{Colors.BORDER}│{Colors.RESET} Organization: {info['description']:<54}{Colors.BORDER}│{Colors.RESET}")
            
            location_info = []
            if info['country']:
                location_info.append(f"Country: {info['country']}")
            if info['rir']:
                location_info.append(f"RIR: {info['rir']}")
            if location_info:
                print(f"{Colors.BORDER}│{Colors.RESET} {' | '.join(location_info):<66}{Colors.BORDER}│{Colors.RESET}")
            
            print(f"{Colors.BORDER}│{Colors.RESET} Data Sources: {', '.join(info['sources'])}, bgp.he.net{' ' * (38 - len(', '.join(info['sources'])))}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv4 prefixes
            if data['ipv4']:
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}IPv4 Prefixes ({ipv4_count} total):{Colors.RESET}{' ' * (44 - len(str(ipv4_count)))}{Colors.BORDER}│{Colors.RESET}")
                for i, prefix in enumerate(data['ipv4'][:5]):  # Show first 5
                    try:
                        network = ipaddress.ip_network(prefix, strict=False)
                        ip_count = network.num_addresses
                        print(f"{Colors.BORDER}│{Colors.RESET} ├─ {prefix:<20} [{ip_count:,} IPs]{' ' * (25 - len(f'{ip_count:,}'))}{Colors.BORDER}│{Colors.RESET}")
                    except ValueError:
                        print(f"{Colors.BORDER}│{Colors.RESET} ├─ {prefix:<49}{Colors.BORDER}│{Colors.RESET}")
                
                if ipv4_count > 5:
                    print(f"{Colors.BORDER}│{Colors.RESET} └─ ... {ipv4_count - 5} more prefixes{' ' * (37 - len(str(ipv4_count - 5)))}{Colors.BORDER}│{Colors.RESET}")
                print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv6 prefixes
            if data['ipv6']:
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}IPv6 Prefixes ({ipv6_count} total):{Colors.RESET}{' ' * (44 - len(str(ipv6_count)))}{Colors.BORDER}│{Colors.RESET}")
                for prefix in data['ipv6'][:3]:  # Show first 3
                    print(f"{Colors.BORDER}│{Colors.RESET} ├─ {prefix:<58}{Colors.BORDER}│{Colors.RESET}")
                
                if ipv6_count > 3:
                    print(f"{Colors.BORDER}│{Colors.RESET} └─ ... {ipv6_count - 3} more prefixes{' ' * (37 - len(str(ipv6_count - 3)))}{Colors.BORDER}│{Colors.RESET}")
                print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # Summary
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}Summary Statistics:{Colors.RESET}{' ' * 50}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} • Total IPv4 addresses: {ipv4_space:,}{' ' * (42 - len(f'{ipv4_space:,}'))}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} • IPv6 prefixes: {ipv6_count}{' ' * (53 - len(str(ipv6_count)))}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}└─────────────────────────────────────────────────────────────────────┘{Colors.RESET}\n")
    
    def export_results(self, prefix_data: Dict, format_type='json'):
        """Export results to file"""
        if not self.output_file:
            return
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_asns': len(prefix_data),
            'asns': {}
        }
        
        for asn, data in prefix_data.items():
            export_data['asns'][asn] = {
                'info': data['info'],
                'ipv4_prefixes': data['ipv4'],
                'ipv6_prefixes': data['ipv6'],
                'ipv4_count': len(data['ipv4']),
                'ipv6_count': len(data['ipv6']),
                'total_ipv4_addresses': self.calculate_ip_space(data['ipv4'])
            }
        
        if format_type == 'json':
            with open(self.output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
        elif format_type == 'csv':
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ASN', 'Name', 'Description', 'Country', 'IPv4_Prefixes', 'IPv6_Prefixes', 'Total_IPv4_IPs'])
                for asn, data in prefix_data.items():
                    info = data['info']
                    writer.writerow([
                        asn, info['name'], info['description'], info['country'],
                        ';'.join(data['ipv4']), ';'.join(data['ipv6']),
                        self.calculate_ip_space(data['ipv4'])
                    ])
    
    def whois_fallback(self, asn: str) -> List[str]:
        """Fallback method using whois if web scraping fails"""
        try:
            result = subprocess.run(
                ['whois', '-h', 'whois.radb.net', f'AS{asn}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            prefixes = []
            for line in lines:
                if line.startswith('route:') or line.startswith('route6:'):
                    prefix = line.split(':', 1)[1].strip()
                    prefixes.append(prefix)
            return prefixes
        except:
            return []
    
    def run(self, keyword: str):
        """Main execution flow"""
        
        # Display banner
        print(BANNER)
        
        # Step 1: Search for organizations
        print(f"{Colors.INFO}[*] Searching for organizations matching '{keyword}'...{Colors.RESET}")
        
        peeringdb_results = self.search_peeringdb(keyword)
        if peeringdb_results:
            print(f"{Colors.SUCCESS}[+] Found {len(peeringdb_results)} results from PeeringDB{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}[!] No results from PeeringDB{Colors.RESET}")
            peeringdb_results = []
        
        bgpview_results = self.search_bgpview(keyword)
        if bgpview_results:
            print(f"{Colors.SUCCESS}[+] Found {len(bgpview_results)} results from BGPView{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}[!] No results from BGPView{Colors.RESET}")
            bgpview_results = []
        
        # Step 2: Merge and deduplicate
        all_results = self.merge_results(peeringdb_results, bgpview_results)
        print(f"{Colors.INFO}[*] Total unique ASNs found: {len(all_results)}{Colors.RESET}")
        
        if not all_results:
            print(f"{Colors.ERROR}[!] No organizations found for '{keyword}'{Colors.RESET}")
            print(f"{Colors.INFO}[*] Try a broader search term or check your internet connection{Colors.RESET}")
            return
        
        # Step 3: Interactive selection
        selected = self.interactive_selection(all_results)
        
        if not selected:
            print(f"{Colors.WARNING}[!] No ASNs selected. Exiting.{Colors.RESET}")
            return
        
        print(f"{Colors.INFO}[*] Fetching prefix data for {len(selected)} ASN(s)...{Colors.RESET}")
        
        # Step 4: Fetch prefix data
        prefix_data = {}
        for idx, asn_info in enumerate(selected, 1):
            asn = str(asn_info['asn'])
            print(f"{Colors.INFO}[*] [{idx}/{len(selected)}] Processing AS{asn}...{Colors.RESET}")
            
            # Fetch IPv4 prefixes
            ipv4_prefixes = self.scraper.get_ipv4_prefixes(asn)
            if ipv4_prefixes:
                print(f"{Colors.SUCCESS}  └─ Found {len(ipv4_prefixes)} IPv4 prefixes{Colors.RESET}")
            else:
                print(f"{Colors.WARNING}  └─ No IPv4 prefixes found, trying whois fallback...{Colors.RESET}")
                fallback_prefixes = self.whois_fallback(asn)
                ipv4_prefixes = [p for p in fallback_prefixes if ':' not in p]
                if ipv4_prefixes:
                    print(f"{Colors.SUCCESS}  └─ Whois fallback found {len(ipv4_prefixes)} IPv4 prefixes{Colors.RESET}")
            
            # Fetch IPv6 prefixes
            ipv6_prefixes = self.scraper.get_ipv6_prefixes(asn)
            if ipv6_prefixes:
                print(f"{Colors.SUCCESS}  └─ Found {len(ipv6_prefixes)} IPv6 prefixes{Colors.RESET}")
            else:
                # Try whois fallback for IPv6
                fallback_prefixes = self.whois_fallback(asn)
                ipv6_prefixes = [p for p in fallback_prefixes if ':' in p]
                if ipv6_prefixes:
                    print(f"{Colors.SUCCESS}  └─ Whois fallback found {len(ipv6_prefixes)} IPv6 prefixes{Colors.RESET}")
            
            prefix_data[asn] = {
                'info': asn_info,
                'ipv4': ipv4_prefixes,
                'ipv6': ipv6_prefixes
            }
        
        # Step 5: Display results
        self.display_results(prefix_data)
        
        # Step 6: Export if requested
        if self.output_file:
            format_type = 'json'
            if self.output_file.endswith('.csv'):
                format_type = 'csv'
            
            self.export_results(prefix_data, format_type)
            print(f"{Colors.SUCCESS}[+] Results exported to {self.output_file}{Colors.RESET}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ASN-Hunter - Advanced ASN Reconnaissance Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 asn-hunter.py tesla
  python3 asn-hunter.py "tesla motors" -v
  python3 asn-hunter.py cloudflare -o results.json
  python3 asn-hunter.py amazon --format csv -o asn_report.csv
        """
    )
    
    parser.add_argument('keyword', help='Organization name to search')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-o', '--output', help='Output file (json/csv)')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json', help='Output format')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--delay', type=int, default=1, help='Delay between requests (seconds)')
    
    args = parser.parse_args()
    
    if args.no_color:
        # Disable colors
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    try:
        hunter = ASNHunter(verbose=args.verbose, output_file=args.output, delay=args.delay)
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