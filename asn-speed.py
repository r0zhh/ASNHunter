#!/usr/bin/env python3
"""
ASN-Speed: Lightning-Fast Bulk ASN Discovery
Version: 1.0.0
Purpose: High-speed ASN enumeration with aggressive parallel processing

SPEED FEATURES:
- Concurrent API calls
- Bulk processing capabilities
- Minimal delays for maximum speed
- Streamlined output
- Cache optimization
"""

import requests
import asyncio
import aiohttp
import threading
import concurrent.futures
import time
import argparse
import sys
import json
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import quote
from queue import Queue
import re

# Speed-optimized colors
class SpeedColors:
    SPEED = "\033[38;5;226m"      # Bright Yellow
    SUCCESS = "\033[38;5;46m"     # Bright Green
    ERROR = "\033[38;5;196m"      # Red
    INFO = "\033[38;5;51m"        # Cyan
    RESET = "\033[0m"
    BOLD = "\033[1m"

# Speed Banner
SPEED_BANNER = f"""{SpeedColors.SPEED}
 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
 ▓                    ASN-SPEED MODE                         ▓
 ▓              Lightning-Fast ASN Discovery                 ▓
 ▓                   MAXIMUM VELOCITY                        ▓
 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
{SpeedColors.RESET}
"""

class SpeedScraper:
    """High-speed scraper with aggressive optimizations"""
    
    def __init__(self, max_workers=10, timeout=5):
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASN-Speed/1.0.0 (High-Performance Reconnaissance)',
            'Accept': 'application/json,text/html',
            'Connection': 'keep-alive'
        })
        # Optimize session for speed
        self.session.trust_env = False
        
        print(f"{SpeedColors.SUCCESS}[+] Speed mode initialized: {max_workers} workers, {timeout}s timeout{SpeedColors.RESET}")
    
    def speed_search_apis(self, keywords: List[str]) -> List[Dict]:
        """Parallel API searches across multiple keywords"""
        all_results = []
        
        def search_peeringdb(keyword):
            try:
                url = f"https://www.peeringdb.com/api/org?name__contains={quote(keyword)}"
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for org in data.get('data', []):
                        if org.get('asn'):
                            results.append({
                                'asn': org['asn'],
                                'name': org.get('name', ''),
                                'description': org.get('name_long', ''),
                                'source': 'PeeringDB',
                                'keyword': keyword
                            })
                    return results
            except:
                return []
            return []
        
        def search_bgpview(keyword):
            try:
                url = f"https://api.bgpview.io/search?query_term={quote(keyword)}"
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    if data.get('status') == 'ok' and 'data' in data:
                        for asn_data in data['data'].get('asns', []):
                            results.append({
                                'asn': asn_data['asn'],
                                'name': asn_data.get('name', ''),
                                'description': asn_data.get('description', ''),
                                'country': asn_data.get('country_code', ''),
                                'source': 'BGPView',
                                'keyword': keyword
                            })
                    return results
            except:
                return []
            return []
        
        # Parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all PeeringDB searches
            pdb_futures = {executor.submit(search_peeringdb, kw): kw for kw in keywords}
            
            # Submit all BGPView searches (with slight delay)
            bgpv_futures = {executor.submit(search_bgpview, kw): kw for kw in keywords}
            
            print(f"{SpeedColors.INFO}[*] Parallel API queries: {len(pdb_futures) + len(bgpv_futures)} requests{SpeedColors.RESET}")
            
            # Collect PeeringDB results
            for future in concurrent.futures.as_completed(pdb_futures):
                keyword = pdb_futures[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    if results:
                        print(f"{SpeedColors.SUCCESS}[+] PeeringDB '{keyword}': {len(results)} ASNs{SpeedColors.RESET}")
                except Exception as e:
                    print(f"{SpeedColors.ERROR}[!] PeeringDB '{keyword}': {e}{SpeedColors.RESET}")
            
            # Collect BGPView results
            for future in concurrent.futures.as_completed(bgpv_futures):
                keyword = bgpv_futures[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    if results:
                        print(f"{SpeedColors.SUCCESS}[+] BGPView '{keyword}': {len(results)} ASNs{SpeedColors.RESET}")
                except Exception as e:
                    print(f"{SpeedColors.ERROR}[!] BGPView '{keyword}': {e}{SpeedColors.RESET}")
        
        return all_results
    
    def speed_scrape_prefixes(self, asns: List[str]) -> Dict:
        """High-speed prefix scraping with parallel processing"""
        results = {}
        
        def scrape_asn_prefixes(asn):
            asn_results = {'ipv4': [], 'ipv6': []}
            
            # Speed scrape IPv4
            try:
                url = f"https://bgp.he.net/AS{asn}#_prefixes"
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    # Fast regex extraction
                    ipv4_pattern = r'href="/net/([\d\.]+/\d+)"'
                    matches = re.findall(ipv4_pattern, response.text)
                    asn_results['ipv4'] = list(set(matches))  # Deduplicate
            except:
                pass
            
            # Speed scrape IPv6 
            try:
                url = f"https://bgp.he.net/AS{asn}#_prefixes6"
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    # Fast regex extraction
                    ipv6_pattern = r'href="/net/([\da-fA-F:]+/\d+)"'
                    matches = re.findall(ipv6_pattern, response.text)
                    asn_results['ipv6'] = list(set(matches))  # Deduplicate
            except:
                pass
            
            return asn, asn_results
        
        print(f"{SpeedColors.INFO}[*] High-speed prefix scraping: {len(asns)} ASNs{SpeedColors.RESET}")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_asn = {executor.submit(scrape_asn_prefixes, asn): asn for asn in asns}
            
            for future in concurrent.futures.as_completed(future_to_asn):
                asn = future_to_asn[future]
                try:
                    asn_key, asn_data = future.result()
                    results[asn_key] = asn_data
                    total_prefixes = len(asn_data['ipv4']) + len(asn_data['ipv6'])
                    print(f"{SpeedColors.SUCCESS}[+] AS{asn}: {total_prefixes} prefixes{SpeedColors.RESET}")
                except Exception as e:
                    print(f"{SpeedColors.ERROR}[!] AS{asn}: {e}{SpeedColors.RESET}")
                    results[asn] = {'ipv4': [], 'ipv6': []}
        
        elapsed = time.time() - start_time
        print(f"{SpeedColors.SPEED}[⚡] Prefix scraping completed in {elapsed:.1f}s{SpeedColors.RESET}")
        
        return results


class SpeedASNHunter:
    """High-speed ASN hunter for bulk operations"""
    
    def __init__(self, max_workers=10, timeout=5, output_file=None):
        self.scraper = SpeedScraper(max_workers, timeout)
        self.output_file = output_file
        self.results = {}
        self.start_time = None
    
    def parse_keywords(self, keyword_input: str) -> List[str]:
        """Parse keyword input for bulk processing"""
        if ',' in keyword_input:
            # Multiple keywords separated by commas
            keywords = [kw.strip() for kw in keyword_input.split(',')]
        elif keyword_input.startswith('@'):
            # Keywords from file
            filename = keyword_input[1:]
            try:
                with open(filename, 'r') as f:
                    keywords = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"{SpeedColors.ERROR}[!] File not found: {filename}{SpeedColors.RESET}")
                return []
        else:
            # Single keyword
            keywords = [keyword_input]
        
        print(f"{SpeedColors.INFO}[*] Processing {len(keywords)} keywords: {keywords}{SpeedColors.RESET}")
        return keywords
    
    def deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Fast deduplication by ASN"""
        seen_asns = set()
        unique_results = []
        
        for result in results:
            asn = result['asn']
            if asn not in seen_asns:
                seen_asns.add(asn)
                unique_results.append(result)
        
        print(f"{SpeedColors.INFO}[*] Deduplicated: {len(results)} -> {len(unique_results)} unique ASNs{SpeedColors.RESET}")
        return unique_results
    
    def speed_display_results(self, asn_info: List[Dict], prefix_data: Dict):
        """Fast, streamlined results display"""
        total_asns = len(asn_info)
        total_ipv4_prefixes = sum(len(data['ipv4']) for data in prefix_data.values())
        total_ipv6_prefixes = sum(len(data['ipv6']) for data in prefix_data.values())
        total_time = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n{SpeedColors.SPEED}▓▓▓ SPEED RESULTS ▓▓▓{SpeedColors.RESET}")
        print(f"{SpeedColors.BOLD}Total Time: {total_time:.1f}s{SpeedColors.RESET}")
        print(f"{SpeedColors.BOLD}ASNs Found: {total_asns}{SpeedColors.RESET}")
        print(f"{SpeedColors.BOLD}IPv4 Prefixes: {total_ipv4_prefixes}{SpeedColors.RESET}")
        print(f"{SpeedColors.BOLD}IPv6 Prefixes: {total_ipv6_prefixes}{SpeedColors.RESET}")
        print(f"{SpeedColors.BOLD}Speed: {(total_ipv4_prefixes + total_ipv6_prefixes) / max(total_time, 0.1):.1f} prefixes/sec{SpeedColors.RESET}")
        
        print(f"\n{SpeedColors.INFO}ASN SUMMARY:{SpeedColors.RESET}")
        for asn_data in asn_info:
            asn = str(asn_data['asn'])
            if asn in prefix_data:
                ipv4_count = len(prefix_data[asn]['ipv4'])
                ipv6_count = len(prefix_data[asn]['ipv6'])
                total_prefixes = ipv4_count + ipv6_count
                
                print(f"{SpeedColors.SUCCESS}AS{asn}{SpeedColors.RESET} - {asn_data['name'][:30]:<30} | "
                      f"IPv4: {ipv4_count:>3} | IPv6: {ipv6_count:>3} | Total: {total_prefixes:>3}")
    
    def speed_export(self, asn_info: List[Dict], prefix_data: Dict):
        """Fast export with minimal processing"""
        if not self.output_file:
            return
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'speed',
            'processing_time': time.time() - self.start_time if self.start_time else 0,
            'asns': {}
        }
        
        for asn_data in asn_info:
            asn = str(asn_data['asn'])
            export_data['asns'][asn] = {
                'info': asn_data,
                'ipv4_prefixes': prefix_data.get(asn, {}).get('ipv4', []),
                'ipv6_prefixes': prefix_data.get(asn, {}).get('ipv6', [])
            }
        
        with open(self.output_file, 'w') as f:
            json.dump(export_data, f, separators=(',', ':'))  # Compact JSON
        
        print(f"{SpeedColors.SUCCESS}[⚡] Results exported to {self.output_file}{SpeedColors.RESET}")
    
    def run(self, keyword_input: str, auto_select=False):
        """Main speed execution"""
        self.start_time = time.time()
        
        print(SPEED_BANNER)
        print(f"{SpeedColors.SPEED}[⚡] Maximum speed mode activated{SpeedColors.RESET}")
        
        # Phase 1: Parse keywords
        keywords = self.parse_keywords(keyword_input)
        if not keywords:
            return
        
        # Phase 2: High-speed API searches
        print(f"\n{SpeedColors.INFO}[⚡] Phase 1: High-speed API discovery{SpeedColors.RESET}")
        all_results = self.scraper.speed_search_apis(keywords)
        
        # Phase 3: Deduplication
        unique_results = self.deduplicate_results(all_results)
        
        if not unique_results:
            print(f"{SpeedColors.ERROR}[!] No ASNs found. Speed run aborted.{SpeedColors.RESET}")
            return
        
        # Phase 4: ASN selection (auto or manual)
        if auto_select:
            selected_asns = unique_results
            print(f"{SpeedColors.SPEED}[⚡] Auto-selected all {len(selected_asns)} ASNs{SpeedColors.RESET}")
        else:
            # Quick selection interface
            print(f"\n{SpeedColors.INFO}FOUND ASNs:{SpeedColors.RESET}")
            for idx, result in enumerate(unique_results[:20], 1):  # Limit display for speed
                print(f"{idx:>2}. AS{result['asn']} - {result['name'][:50]}")
            
            if len(unique_results) > 20:
                print(f"... and {len(unique_results) - 20} more ASNs")
            
            selection = input(f"\n{SpeedColors.SPEED}[⚡] Quick select (1,2,3 or 'all' or 'top10'): {SpeedColors.RESET}").strip()
            
            if selection.lower() == 'all':
                selected_asns = unique_results
            elif selection.lower() == 'top10':
                selected_asns = unique_results[:10]
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    selected_asns = [unique_results[i] for i in indices if 0 <= i < len(unique_results)]
                except:
                    print(f"{SpeedColors.ERROR}[!] Invalid selection. Using top 5.{SpeedColors.RESET}")
                    selected_asns = unique_results[:5]
        
        # Phase 5: High-speed prefix collection
        print(f"\n{SpeedColors.INFO}[⚡] Phase 2: High-speed prefix collection{SpeedColors.RESET}")
        asn_list = [str(asn_data['asn']) for asn_data in selected_asns]
        prefix_data = self.scraper.speed_scrape_prefixes(asn_list)
        
        # Phase 6: Speed results
        print(f"\n{SpeedColors.INFO}[⚡] Phase 3: Results compilation{SpeedColors.RESET}")
        self.speed_display_results(selected_asns, prefix_data)
        
        # Phase 7: Export
        self.speed_export(selected_asns, prefix_data)
        
        total_time = time.time() - self.start_time
        print(f"\n{SpeedColors.SPEED}[⚡] SPEED RUN COMPLETE: {total_time:.1f} seconds{SpeedColors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description='ASN-Speed - Lightning-Fast Bulk ASN Discovery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Speed Examples:
  python3 asn-speed.py "tesla,google,amazon" --auto
  python3 asn-speed.py "@targets.txt" --workers 20 --timeout 3
  python3 asn-speed.py "cloudflare" --workers 15 -o speed_results.json
  
Keywords Input:
  Single: python3 asn-speed.py "tesla"
  Multiple: python3 asn-speed.py "tesla,google,amazon"
  From file: python3 asn-speed.py "@keywords.txt"
        """
    )
    
    parser.add_argument('keywords', help='Keywords (single, comma-separated, or @file)')
    parser.add_argument('--workers', type=int, default=10, help='Max concurrent workers (default: 10)')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout in seconds (default: 5)')
    parser.add_argument('--auto', action='store_true', help='Auto-select all found ASNs')
    parser.add_argument('-o', '--output', help='Output file for speed results')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    args = parser.parse_args()
    
    if args.no_color:
        for attr in dir(SpeedColors):
            if not attr.startswith('_'):
                setattr(SpeedColors, attr, '')
    
    try:
        hunter = SpeedASNHunter(
            max_workers=args.workers,
            timeout=args.timeout,
            output_file=args.output
        )
        hunter.run(args.keywords, auto_select=args.auto)
    except KeyboardInterrupt:
        print(f"\n{SpeedColors.ERROR}[!] Speed run interrupted.{SpeedColors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{SpeedColors.ERROR}[!] Speed run failed: {e}{SpeedColors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()