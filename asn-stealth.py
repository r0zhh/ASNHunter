#!/usr/bin/env python3
"""
ASN-Stealth: Ultra-Stealthy ASN Reconnaissance with Maximum Evasion
Version: 1.0.0
Purpose: Stealth-focused ASN discovery with advanced anti-detection

STEALTH FEATURES:
- Random delays and jitter
- TOR proxy support
- User-Agent rotation
- Request timing obfuscation  
- Distributed collection across multiple sessions
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
import argparse
import sys
import json
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote
import threading
from queue import Queue

# Stealth Colors (Darker theme)
class StealthColors:
    STEALTH = "\033[38;5;8m"      # Dark Gray
    SUCCESS = "\033[38;5;34m"     # Dark Green
    ERROR = "\033[38;5;88m"       # Dark Red
    WARNING = "\033[38;5;130m"    # Dark Orange
    INFO = "\033[38;5;24m"        # Dark Blue
    RESET = "\033[0m"
    DIM = "\033[2m"

# Stealth Banner
STEALTH_BANNER = f"""{StealthColors.STEALTH}
 ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
 █                 ASN-STEALTH MODE                          █
 █           Ultra-Low Profile ASN Reconnaissance           █
 █                    STAY UNDETECTED                       █
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
{StealthColors.RESET}
"""

class StealthScraper:
    """Ultra-stealthy scraper with maximum evasion techniques"""
    
    def __init__(self, min_delay=3, max_delay=8, use_tor=False):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.use_tor = use_tor
        self.session_pool = []
        self.current_session = 0
        
        # Extensive User-Agent pool
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/118.0.2088.76',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        # Initialize session pool
        self._create_session_pool()
        
        print(f"{StealthColors.SUCCESS}[+] Stealth mode initialized{StealthColors.RESET}")
        print(f"{StealthColors.DIM}[*] Session pool: {len(self.session_pool)} sessions{StealthColors.RESET}")
        print(f"{StealthColors.DIM}[*] Delay range: {min_delay}-{max_delay}s{StealthColors.RESET}")
        if use_tor:
            print(f"{StealthColors.INFO}[*] TOR proxy enabled{StealthColors.RESET}")
    
    def _create_session_pool(self):
        """Create multiple sessions with different configurations"""
        for i in range(5):  # 5 different sessions
            session = requests.Session()
            
            # Randomize session configuration
            session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': random.choice([
                    'en-US,en;q=0.9', 'en-US,en;q=0.8', 'en-GB,en;q=0.9'
                ]),
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'DNT': '1',
            })
            
            # TOR proxy configuration
            if self.use_tor:
                session.proxies = {
                    'http': 'socks5://127.0.0.1:9050',
                    'https': 'socks5://127.0.0.1:9050'
                }
            
            # Random timeout
            session.timeout = random.uniform(15, 25)
            
            self.session_pool.append(session)
    
    def _get_stealth_session(self):
        """Get a session with rotated configuration"""
        session = self.session_pool[self.current_session]
        self.current_session = (self.current_session + 1) % len(self.session_pool)
        
        # Rotate User-Agent
        session.headers['User-Agent'] = random.choice(self.user_agents)
        
        return session
    
    def _stealth_delay(self):
        """Apply randomized stealth delay with jitter"""
        base_delay = random.uniform(self.min_delay, self.max_delay)
        jitter = random.uniform(-0.5, 0.5)
        total_delay = max(1.0, base_delay + jitter)
        
        print(f"{StealthColors.DIM}[*] Stealth delay: {total_delay:.1f}s{StealthColors.RESET}")
        time.sleep(total_delay)
    
    def stealth_get(self, url: str, retries=2):
        """Perform stealthy GET request with multiple fallback strategies"""
        for attempt in range(retries + 1):
            try:
                # Apply stealth delay before each request
                if attempt > 0:
                    print(f"{StealthColors.WARNING}[!] Retry attempt {attempt}{StealthColors.RESET}")
                
                self._stealth_delay()
                
                # Get rotated session
                session = self._get_stealth_session()
                
                # Add random headers
                extra_headers = {}
                if random.random() < 0.3:  # 30% chance
                    extra_headers['Cache-Control'] = 'no-cache'
                if random.random() < 0.2:  # 20% chance  
                    extra_headers['Pragma'] = 'no-cache'
                
                response = session.get(url, headers=extra_headers)
                
                if response.status_code == 200:
                    print(f"{StealthColors.SUCCESS}[+] Success: {response.status_code}{StealthColors.RESET}")
                    return response
                elif response.status_code == 403:
                    print(f"{StealthColors.WARNING}[!] Access denied (403), trying different session...{StealthColors.RESET}")
                    continue
                elif response.status_code == 429:
                    extended_delay = random.uniform(60, 120)
                    print(f"{StealthColors.WARNING}[!] Rate limited. Extended delay: {extended_delay:.1f}s{StealthColors.RESET}")
                    time.sleep(extended_delay)
                    continue
                else:
                    print(f"{StealthColors.WARNING}[!] HTTP {response.status_code}{StealthColors.RESET}")
                    
            except requests.exceptions.RequestException as e:
                print(f"{StealthColors.ERROR}[!] Request failed: {e}{StealthColors.RESET}")
                if attempt < retries:
                    time.sleep(random.uniform(5, 10))
                    continue
        
        return None
    
    def stealth_search_peeringdb(self, keyword: str) -> List[Dict]:
        """Stealthy PeeringDB search"""
        url = f"https://www.peeringdb.com/api/org?name__contains={quote(keyword)}"
        print(f"{StealthColors.INFO}[*] Stealth PeeringDB query...{StealthColors.RESET}")
        
        response = self.stealth_get(url)
        if not response:
            return []
        
        try:
            data = response.json()
            results = []
            
            for org in data.get('data', []):
                if org.get('asn'):
                    results.append({
                        'asn': org['asn'],
                        'name': org.get('name', ''),
                        'description': org.get('name_long', ''),
                        'source': 'PeeringDB-Stealth'
                    })
            
            print(f"{StealthColors.SUCCESS}[+] PeeringDB: {len(results)} results (stealth){StealthColors.RESET}")
            return results
            
        except json.JSONDecodeError:
            print(f"{StealthColors.ERROR}[!] PeeringDB: Invalid JSON response{StealthColors.RESET}")
            return []
    
    def stealth_search_bgpview(self, keyword: str) -> List[Dict]:
        """Stealthy BGPView search with extended delays"""
        url = f"https://api.bgpview.io/search?query_term={quote(keyword)}"
        print(f"{StealthColors.INFO}[*] Stealth BGPView query...{StealthColors.RESET}")
        
        # Extra delay for BGPView (they're aggressive)
        time.sleep(random.uniform(2, 4))
        
        response = self.stealth_get(url)
        if not response:
            return []
        
        try:
            data = response.json()
            results = []
            
            if data.get('status') == 'ok' and 'data' in data:
                for asn_data in data['data'].get('asns', []):
                    results.append({
                        'asn': asn_data['asn'],
                        'name': asn_data.get('name', ''),
                        'description': asn_data.get('description', ''),
                        'country': asn_data.get('country_code', ''),
                        'source': 'BGPView-Stealth'
                    })
            
            print(f"{StealthColors.SUCCESS}[+] BGPView: {len(results)} results (stealth){StealthColors.RESET}")
            return results
            
        except json.JSONDecodeError:
            print(f"{StealthColors.ERROR}[!] BGPView: Invalid JSON response{StealthColors.RESET}")
            return []
    
    def stealth_scrape_bgp_he(self, asn: str, prefix_type: str) -> List[str]:
        """Ultra-stealthy BGP.HE.NET scraping"""
        print(f"{StealthColors.INFO}[*] Stealth BGP.HE.NET scraping AS{asn} ({prefix_type})...{StealthColors.RESET}")
        
        if prefix_type == 'ipv4':
            url = f"https://bgp.he.net/AS{asn}#_prefixes"
            table_id = 'table_prefixes4'
            pattern = r'/net/([\d\.]+/\d+)'
        else:
            url = f"https://bgp.he.net/AS{asn}#_prefixes6" 
            table_id = 'table_prefixes6'
            pattern = r'/net/([\da-fA-F:]+/\d+)'
        
        response = self.stealth_get(url, retries=3)
        if not response:
            print(f"{StealthColors.ERROR}[!] Failed to access BGP.HE.NET{StealthColors.RESET}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        prefixes = []
        
        # Find table with multiple strategies
        table = soup.find('table', {'id': table_id})
        if not table:
            # Alternative: find any table containing prefixes
            tables = soup.find_all('table')
            for t in tables:
                if 'prefix' in str(t).lower():
                    table = t
                    break
        
        if table:
            for row in table.find_all('tr')[1:]:  # Skip header
                cells = row.find_all('td')
                if cells and cells[0].find('a'):
                    prefix_link = cells[0].find('a')
                    href = prefix_link.get('href', '')
                    match = re.search(pattern, href)
                    if match:
                        prefixes.append(match.group(1))
                    else:
                        # Fallback to text extraction
                        prefix_text = prefix_link.get_text(strip=True)
                        if '/' in prefix_text:
                            if prefix_type == 'ipv4' and re.match(r'^\d+\.\d+\.\d+\.\d+/\d+$', prefix_text):
                                prefixes.append(prefix_text)
                            elif prefix_type == 'ipv6' and ':' in prefix_text:
                                prefixes.append(prefix_text)
        
        print(f"{StealthColors.SUCCESS}[+] BGP.HE.NET: {len(prefixes)} {prefix_type} prefixes (stealth){StealthColors.RESET}")
        return prefixes


class StealthASNHunter:
    """Main stealth ASN hunter with ultra-low profile"""
    
    def __init__(self, min_delay=3, max_delay=8, use_tor=False, output_file=None):
        self.scraper = StealthScraper(min_delay, max_delay, use_tor)
        self.output_file = output_file
        self.results = {}
    
    def stealth_search(self, keyword: str) -> List[Dict]:
        """Perform stealthy ASN search"""
        print(f"{StealthColors.INFO}[*] Initiating stealth reconnaissance for: '{keyword}'{StealthColors.RESET}")
        
        all_results = []
        
        # Staggered searches with random order
        search_order = ['peeringdb', 'bgpview']
        random.shuffle(search_order)
        
        for search_type in search_order:
            if search_type == 'peeringdb':
                results = self.scraper.stealth_search_peeringdb(keyword)
                all_results.extend(results)
                
                # Random break between searches
                if search_order.index(search_type) < len(search_order) - 1:
                    break_time = random.uniform(10, 20)
                    print(f"{StealthColors.DIM}[*] Inter-search delay: {break_time:.1f}s{StealthColors.RESET}")
                    time.sleep(break_time)
                    
            elif search_type == 'bgpview':
                results = self.scraper.stealth_search_bgpview(keyword)
                all_results.extend(results)
        
        # Deduplicate results
        seen_asns = set()
        unique_results = []
        for result in all_results:
            if result['asn'] not in seen_asns:
                seen_asns.add(result['asn'])
                unique_results.append(result)
        
        return unique_results
    
    def stealth_select_asn(self, results: List[Dict]) -> List[Dict]:
        """Stealth-mode ASN selection (simplified for speed)"""
        if not results:
            return []
        
        print(f"\n{StealthColors.STEALTH}═══ STEALTH TARGET SELECTION ═══{StealthColors.RESET}")
        
        for idx, result in enumerate(results, 1):
            print(f"{StealthColors.SUCCESS}[{idx}]{StealthColors.RESET} AS{result['asn']} - {result['name']}")
            if result.get('description'):
                print(f"    {StealthColors.DIM}└─ {result['description'][:60]}...{StealthColors.RESET}")
        
        print(f"\n{StealthColors.WARNING}Stealth Mode: Quick selection required{StealthColors.RESET}")
        selection = input(f"{StealthColors.DIM}[?] Select ASNs (e.g., 1,2,3 or 'all'): {StealthColors.RESET}").strip()
        
        if selection.lower() == 'all':
            return results
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            return [results[i] for i in indices if 0 <= i < len(results)]
        except:
            print(f"{StealthColors.ERROR}[!] Invalid selection. Taking first ASN.{StealthColors.RESET}")
            return [results[0]] if results else []
    
    def stealth_collect_prefixes(self, selected_asns: List[Dict]):
        """Collect prefixes in stealth mode"""
        print(f"\n{StealthColors.INFO}[*] Initiating stealth prefix collection...{StealthColors.RESET}")
        
        for idx, asn_info in enumerate(selected_asns, 1):
            asn = str(asn_info['asn'])
            print(f"\n{StealthColors.INFO}[*] [{idx}/{len(selected_asns)}] Target: AS{asn}{StealthColors.RESET}")
            
            # Random delay between ASNs
            if idx > 1:
                inter_asn_delay = random.uniform(15, 30)
                print(f"{StealthColors.DIM}[*] Inter-target delay: {inter_asn_delay:.1f}s{StealthColors.RESET}")
                time.sleep(inter_asn_delay)
            
            # Collect IPv4 prefixes
            ipv4_prefixes = self.scraper.stealth_scrape_bgp_he(asn, 'ipv4')
            
            # Random delay between IPv4 and IPv6
            time.sleep(random.uniform(5, 10))
            
            # Collect IPv6 prefixes
            ipv6_prefixes = self.scraper.stealth_scrape_bgp_he(asn, 'ipv6')
            
            self.results[asn] = {
                'info': asn_info,
                'ipv4': ipv4_prefixes,
                'ipv6': ipv6_prefixes
            }
    
    def stealth_display_results(self):
        """Display results in stealth format"""
        print(f"\n{StealthColors.STEALTH}═══ STEALTH RECONNAISSANCE COMPLETE ═══{StealthColors.RESET}")
        
        total_prefixes = 0
        for asn, data in self.results.items():
            total_prefixes += len(data['ipv4']) + len(data['ipv6'])
        
        print(f"{StealthColors.SUCCESS}[+] Total prefixes discovered: {total_prefixes}{StealthColors.RESET}")
        
        for asn, data in self.results.items():
            info = data['info']
            ipv4_count = len(data['ipv4'])
            ipv6_count = len(data['ipv6'])
            
            print(f"\n{StealthColors.SUCCESS}┌─[ AS{asn} - {info['name']} ]{StealthColors.RESET}")
            print(f"{StealthColors.DIM}│{StealthColors.RESET}")
            print(f"{StealthColors.DIM}├─ IPv4 prefixes: {ipv4_count}{StealthColors.RESET}")
            
            # Show first few prefixes
            for prefix in data['ipv4'][:3]:
                print(f"{StealthColors.DIM}│  ├─ {prefix}{StealthColors.RESET}")
            if ipv4_count > 3:
                print(f"{StealthColors.DIM}│  └─ ... {ipv4_count - 3} more{StealthColors.RESET}")
            
            print(f"{StealthColors.DIM}├─ IPv6 prefixes: {ipv6_count}{StealthColors.RESET}")
            for prefix in data['ipv6'][:2]:
                print(f"{StealthColors.DIM}│  ├─ {prefix}{StealthColors.RESET}")
            if ipv6_count > 2:
                print(f"{StealthColors.DIM}│  └─ ... {ipv6_count - 2} more{StealthColors.RESET}")
            
            print(f"{StealthColors.DIM}└─{StealthColors.RESET}")
    
    def stealth_export(self):
        """Export results quietly"""
        if not self.output_file:
            return
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'stealth',
            'asns': {}
        }
        
        for asn, data in self.results.items():
            export_data['asns'][asn] = {
                'info': data['info'],
                'ipv4_prefixes': data['ipv4'],
                'ipv6_prefixes': data['ipv6']
            }
        
        with open(self.output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"{StealthColors.SUCCESS}[+] Results exported quietly to {self.output_file}{StealthColors.RESET}")
    
    def run(self, keyword: str):
        """Main stealth execution"""
        print(STEALTH_BANNER)
        
        # Phase 1: Stealth search
        results = self.stealth_search(keyword)
        if not results:
            print(f"{StealthColors.ERROR}[!] No targets found. Mission aborted.{StealthColors.RESET}")
            return
        
        # Phase 2: Target selection
        selected = self.stealth_select_asn(results)
        if not selected:
            print(f"{StealthColors.ERROR}[!] No targets selected. Mission aborted.{StealthColors.RESET}")
            return
        
        # Phase 3: Stealth collection
        self.stealth_collect_prefixes(selected)
        
        # Phase 4: Results
        self.stealth_display_results()
        
        # Phase 5: Export
        self.stealth_export()
        
        print(f"\n{StealthColors.SUCCESS}[+] Stealth mission complete. Stay undetected.{StealthColors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description='ASN-Stealth - Ultra-Low Profile ASN Reconnaissance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Stealth Examples:
  python3 asn-stealth.py "tesla" --min-delay 5 --max-delay 10
  python3 asn-stealth.py "cloudflare" --tor -o stealth_results.json
  python3 asn-stealth.py "target" --min-delay 10 --max-delay 20 --tor
        """
    )
    
    parser.add_argument('keyword', help='Target organization name')
    parser.add_argument('--min-delay', type=int, default=3, help='Minimum delay between requests (default: 3s)')
    parser.add_argument('--max-delay', type=int, default=8, help='Maximum delay between requests (default: 8s)')
    parser.add_argument('--tor', action='store_true', help='Use TOR proxy (requires TOR running on 9050)')
    parser.add_argument('-o', '--output', help='Output file for stealth results')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    args = parser.parse_args()
    
    if args.no_color:
        for attr in dir(StealthColors):
            if not attr.startswith('_'):
                setattr(StealthColors, attr, '')
    
    try:
        hunter = StealthASNHunter(
            min_delay=args.min_delay,
            max_delay=args.max_delay, 
            use_tor=args.tor,
            output_file=args.output
        )
        hunter.run(args.keyword)
    except KeyboardInterrupt:
        print(f"\n{StealthColors.ERROR}[!] Mission aborted by user.{StealthColors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{StealthColors.ERROR}[!] Mission failed: {e}{StealthColors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()