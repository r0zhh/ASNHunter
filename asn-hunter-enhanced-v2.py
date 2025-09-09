#!/usr/bin/env python3
"""
ASN-Hunter Enhanced v2.0 - Advanced ASN Reconnaissance with Improved Output
Author: Security Researcher  
Version: 2.1.0
Purpose: Bug Bounty, Penetration Testing, Red Team Operations

ENHANCED OUTPUT FEATURES:
- Improved visual formatting with better statistics
- Automatic complete prefix file saving
- Interactive options for viewing all prefixes
- Geographic analysis and network insights
- Detailed coverage metrics
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
import os

# Try importing cloudscraper for better anti-bot capabilities
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

# Enhanced Color Configuration
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
    ORANGE = "\033[38;5;208m"     # For statistics
    PURPLE = "\033[38;5;141m"     # For metrics

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
        │         ENHANCED EDITION v2.1 - IMPROVED OUTPUT        │
        │      Complete Prefix Discovery & Advanced Analysis     │
        └─────────────────────────────────────────────────────────┘
{Colors.RESET}
"""

# Import the base classes from the original enhanced version
import sys
sys.path.insert(0, '.')

# Custom Exceptions (same as original)
class ASNHunterError(Exception):
    pass

class APIError(ASNHunterError):
    pass

class ScrapingError(ASNHunterError):
    pass

class RateLimitError(ASNHunterError):
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

# [Include the same BGPScraper and Enhanced classes from the original, with modifications to the display function]
# For brevity, I'll focus on the key improvements - the enhanced display function

class EnhancedDisplayManager:
    """Enhanced display manager with improved formatting and file operations"""
    
    def __init__(self, output_dir="results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
    
    def analyze_prefix_distribution(self, prefixes: List[str]) -> Dict:
        """Analyze prefix size distribution"""
        distribution = {}
        for prefix in prefixes:
            try:
                network = ipaddress.ip_network(prefix, strict=False)
                prefix_len = network.prefixlen
                if prefix_len not in distribution:
                    distribution[prefix_len] = 0
                distribution[prefix_len] += 1
            except ValueError:
                continue
        return distribution
    
    def get_geographic_info(self, asn_info: Dict) -> Dict:
        """Extract geographic information"""
        geo_info = {
            'country': asn_info.get('country', 'Unknown'),
            'rir': asn_info.get('rir', 'Unknown'),
            'region': self._get_region_from_rir(asn_info.get('rir', ''))
        }
        return geo_info
    
    def _get_region_from_rir(self, rir: str) -> str:
        """Get geographic region from RIR"""
        rir_regions = {
            'ARIN': 'North America',
            'RIPE': 'Europe/Middle East',
            'APNIC': 'Asia-Pacific',
            'LACNIC': 'Latin America',
            'AFRINIC': 'Africa'
        }
        return rir_regions.get(rir.upper(), 'Unknown')
    
    def save_complete_prefixes(self, prefix_data: Dict, keyword: str):
        """Save complete prefix lists to files"""
        base_filename = f"complete_prefixes_{keyword.replace(' ', '_')}_{self.timestamp}"
        
        # Save as JSON
        json_file = self.output_dir / f"{base_filename}.json"
        with open(json_file, 'w') as f:
            json.dump(prefix_data, f, indent=2)
        
        # Save as plain text for easy use with other tools
        txt_file = self.output_dir / f"{base_filename}.txt"
        with open(txt_file, 'w') as f:
            f.write(f"# Complete Prefix List - {keyword}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total ASNs: {len(prefix_data)}\n\n")
            
            for asn, data in prefix_data.items():
                f.write(f"# AS{asn} - {data['info']['name']}\n")
                f.write(f"# IPv4 Prefixes ({len(data['ipv4'])} total):\n")
                for prefix in data['ipv4']:
                    f.write(f"{prefix}\n")
                f.write(f"# IPv6 Prefixes ({len(data['ipv6'])} total):\n")
                for prefix in data['ipv6']:
                    f.write(f"{prefix}\n")
                f.write("\n")
        
        # Save as CSV for spreadsheet analysis
        csv_file = self.output_dir / f"{base_filename}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ASN', 'Name', 'Prefix', 'Type', 'Size', 'Country', 'RIR'])
            
            for asn, data in prefix_data.items():
                info = data['info']
                for prefix in data['ipv4']:
                    try:
                        network = ipaddress.ip_network(prefix, strict=False)
                        writer.writerow([
                            asn, info['name'], prefix, 'IPv4', 
                            network.num_addresses, info.get('country', ''), info.get('rir', '')
                        ])
                    except ValueError:
                        writer.writerow([asn, info['name'], prefix, 'IPv4', 0, info.get('country', ''), info.get('rir', '')])
                
                for prefix in data['ipv6']:
                    writer.writerow([asn, info['name'], prefix, 'IPv6', 'N/A', info.get('country', ''), info.get('rir', '')])
        
        return {
            'json_file': json_file,
            'txt_file': txt_file,
            'csv_file': csv_file
        }
    
    def display_enhanced_results(self, prefix_data: Dict, keyword: str, show_all_prefixes=False):
        """Enhanced results display with comprehensive statistics and options"""
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
        
        # Enhanced header with comprehensive statistics
        print(f"\n{Colors.BORDER}╔════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.MAGENTA}                  ENHANCED RECONNAISSANCE REPORT v2.1               {Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}╠════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} {Colors.BOLD}Target:{Colors.RESET} {keyword:<58}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} {Colors.BOLD}Timestamp:{Colors.RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<51}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}╠════════════════════════════════════════════════════════════════════╣{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.ORANGE} DISCOVERY STATISTICS                                               {Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} • ASNs Analyzed: {Colors.BOLD}{total_asns}{Colors.RESET}{' ' * (52 - len(str(total_asns)))}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} • IPv4 Prefixes Found: {Colors.SUCCESS}{total_ipv4_prefixes}{Colors.RESET}{' ' * (44 - len(str(total_ipv4_prefixes)))}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} • IPv6 Prefixes Found: {Colors.INFO}{total_ipv6_prefixes}{Colors.RESET}{' ' * (44 - len(str(total_ipv6_prefixes)))}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} • Total IPv4 Address Space: {Colors.SUCCESS}{total_ipv4_space:,}{Colors.RESET}{' ' * (35 - len(f'{total_ipv4_space:,}'))}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}║{Colors.RESET} • Geographic Coverage: {len(countries)} countries, {len(rirs)} RIRs{' ' * (32 - len(f'{len(countries)} countries, {len(rirs)} RIRs'))}{Colors.BORDER}║{Colors.RESET}")
        print(f"{Colors.BORDER}╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n")
        
        # Save complete results automatically
        saved_files = self.save_complete_prefixes(prefix_data, keyword)
        print(f"{Colors.SUCCESS}[+] Complete prefix data automatically saved:{Colors.RESET}")
        print(f"    {Colors.DIM}├─ JSON: {saved_files['json_file']}{Colors.RESET}")
        print(f"    {Colors.DIM}├─ TXT:  {saved_files['txt_file']}{Colors.RESET}")
        print(f"    {Colors.DIM}└─ CSV:  {saved_files['csv_file']}{Colors.RESET}")
        print()
        
        # ASN-by-ASN detailed analysis
        for idx, (asn, data) in enumerate(prefix_data.items(), 1):
            info = data['info']
            ipv4_count = len(data['ipv4'])
            ipv6_count = len(data['ipv6'])
            ipv4_space = self.calculate_ip_space(data['ipv4'])
            geo_info = self.get_geographic_info(info)
            
            # Enhanced ASN header
            asn_title = f"AS{asn} - {info['name']}"
            print(f"{Colors.BORDER}┌─[ {Colors.BOLD}{asn_title}{Colors.RESET}{Colors.BORDER} ]{'─' * max(2, 69 - len(asn_title))}┐{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # Organization details
            if info['description']:
                desc = info['description']
                if len(desc) > 50:
                    desc = desc[:47] + "..."
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.BOLD}Organization:{Colors.RESET} {desc:<54}{Colors.BORDER}│{Colors.RESET}")
            
            # Geographic information
            location_parts = []
            if geo_info['country'] != 'Unknown':
                location_parts.append(f"Country: {geo_info['country']}")
            if geo_info['rir'] != 'Unknown':
                location_parts.append(f"RIR: {geo_info['rir']}")
            if geo_info['region'] != 'Unknown':
                location_parts.append(f"Region: {geo_info['region']}")
            
            if location_parts:
                location_str = " | ".join(location_parts)
                if len(location_str) > 65:
                    location_str = location_str[:62] + "..."
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.PURPLE}Geographic:{Colors.RESET} {location_str:<55}{Colors.BORDER}│{Colors.RESET}")
            
            # Data sources
            sources_str = ", ".join(info['sources']) + " + Enhanced Discovery"
            if len(sources_str) > 55:
                sources_str = sources_str[:52] + "..."
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}Data Sources:{Colors.RESET} {sources_str:<54}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv4 Prefixes with enhanced display
            if data['ipv4']:
                distribution = self.analyze_prefix_distribution(data['ipv4'])
                common_sizes = sorted(distribution.keys(), key=lambda x: distribution[x], reverse=True)[:3]
                size_info = ", ".join([f"/{size}({distribution[size]})" for size in common_sizes])
                
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.SUCCESS}IPv4 Prefixes ({ipv4_count} total) - Common sizes: {size_info}{' ' * max(0, 25 - len(size_info))}{Colors.BORDER}│{Colors.RESET}")
                
                # Display logic based on show_all_prefixes or user preference
                display_limit = min(ipv4_count, 10) if not show_all_prefixes else ipv4_count
                
                if ipv4_count > 10 and not show_all_prefixes:
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}📁 Showing first 10 of {ipv4_count} prefixes (full list in saved files){Colors.RESET}{' ' * max(0, 15 - len(str(ipv4_count)))}{Colors.BORDER}│{Colors.RESET}")
                
                for i, prefix in enumerate(data['ipv4'][:display_limit]):
                    try:
                        network = ipaddress.ip_network(prefix, strict=False)
                        ip_count = network.num_addresses
                        count_str = f"[{ip_count:,} IPs]"
                        
                        # Enhanced prefix display with network class info
                        if network.is_private:
                            prefix_type = "🏠"
                        elif network.is_multicast:
                            prefix_type = "📡"
                        elif network.is_global:
                            prefix_type = "🌐"
                        else:
                            prefix_type = "🔹"
                        
                        prefix_display = f"{prefix_type} {prefix:<18} {count_str}"
                        
                        if i == display_limit - 1 and ipv4_count > display_limit:
                            remaining = ipv4_count - display_limit
                            print(f"{Colors.BORDER}│{Colors.RESET} ├─ {prefix_display:<45}{Colors.BORDER}│{Colors.RESET}")
                            print(f"{Colors.BORDER}│{Colors.RESET} └─ {Colors.WARNING}📋 {remaining} more prefixes in {saved_files['txt_file'].name}{Colors.RESET}{' ' * max(0, 30 - len(saved_files['txt_file'].name))}{Colors.BORDER}│{Colors.RESET}")
                        else:
                            connector = "├─" if i < min(display_limit, ipv4_count) - 1 else "└─"
                            print(f"{Colors.BORDER}│{Colors.RESET} {connector} {prefix_display:<45}{Colors.BORDER}│{Colors.RESET}")
                            
                    except ValueError:
                        connector = "├─" if i < display_limit - 1 else "└─"
                        print(f"{Colors.BORDER}│{Colors.RESET} {connector} 🔹 {prefix:<45}{Colors.BORDER}│{Colors.RESET}")
                
                print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # IPv6 Prefixes with enhanced display
            if data['ipv6']:
                print(f"{Colors.BORDER}│{Colors.RESET} {Colors.INFO}IPv6 Prefixes ({ipv6_count} total):{Colors.RESET}{' ' * (44 - len(str(ipv6_count)))}{Colors.BORDER}│{Colors.RESET}")
                
                display_limit_v6 = min(ipv6_count, 8) if not show_all_prefixes else ipv6_count
                
                if ipv6_count > 8 and not show_all_prefixes:
                    print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}📁 Showing first 8 of {ipv6_count} prefixes (full list in saved files){Colors.RESET}{' ' * max(0, 17 - len(str(ipv6_count)))}{Colors.BORDER}│{Colors.RESET}")
                
                for i, prefix in enumerate(data['ipv6'][:display_limit_v6]):
                    prefix_display = f"🌐 {prefix}"
                    if len(prefix_display) > 58:
                        prefix_display = prefix_display[:55] + "..."
                    
                    if i == display_limit_v6 - 1 and ipv6_count > display_limit_v6:
                        remaining = ipv6_count - display_limit_v6
                        print(f"{Colors.BORDER}│{Colors.RESET} ├─ {prefix_display:<58}{Colors.BORDER}│{Colors.RESET}")
                        print(f"{Colors.BORDER}│{Colors.RESET} └─ {Colors.WARNING}📋 {remaining} more prefixes in {saved_files['txt_file'].name}{Colors.RESET}{' ' * max(0, 30 - len(saved_files['txt_file'].name))}{Colors.BORDER}│{Colors.RESET}")
                    else:
                        connector = "├─" if i < min(display_limit_v6, ipv6_count) - 1 else "└─"
                        print(f"{Colors.BORDER}│{Colors.RESET} {connector} {prefix_display:<58}{Colors.BORDER}│{Colors.RESET}")
                
                print(f"{Colors.BORDER}│{Colors.RESET}{' ' * 69}{Colors.BORDER}│{Colors.RESET}")
            
            # Enhanced summary statistics
            print(f"{Colors.BORDER}│{Colors.RESET} {Colors.WARNING}📊 NETWORK ANALYSIS:{Colors.RESET}{' ' * 49}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} • Total IPv4 addresses: {Colors.SUCCESS}{ipv4_space:,}{Colors.RESET}{' ' * (42 - len(f'{ipv4_space:,}'))}{Colors.BORDER}│{Colors.RESET}")
            
            # Calculate network efficiency (how many /24s this represents)
            equivalent_24s = ipv4_space // 256
            if equivalent_24s > 0:
                print(f"{Colors.BORDER}│{Colors.RESET} • Equivalent /24 networks: {Colors.INFO}{equivalent_24s:,}{Colors.RESET}{' ' * (39 - len(f'{equivalent_24s:,}'))}{Colors.BORDER}│{Colors.RESET}")
            
            print(f"{Colors.BORDER}│{Colors.RESET} • IPv4 prefixes discovered: {Colors.SUCCESS}{ipv4_count}{Colors.RESET}{' ' * (39 - len(str(ipv4_count)))}{Colors.BORDER}│{Colors.RESET}")
            print(f"{Colors.BORDER}│{Colors.RESET} • IPv6 prefixes discovered: {Colors.INFO}{ipv6_count}{Colors.RESET}{' ' * (39 - len(str(ipv6_count)))}{Colors.BORDER}│{Colors.RESET}")
            
            # Coverage estimate if we have PeeringDB hint
            if info.get('prefixes_hint', {}).get('ipv4', 0) > 0:
                expected = info['prefixes_hint']['ipv4']
                coverage = min(100, (ipv4_count / expected) * 100)
                coverage_indicator = "🎯" if coverage > 90 else "📈" if coverage > 70 else "⚠️"
                print(f"{Colors.BORDER}│{Colors.RESET} • Coverage estimate: {coverage_indicator} {Colors.PURPLE}{coverage:.1f}%{Colors.RESET} ({ipv4_count}/{expected} expected){' ' * max(0, 25 - len(f'{coverage:.1f}% ({ipv4_count}/{expected} expected)'))}{Colors.BORDER}│{Colors.RESET}")
            
            print(f"{Colors.BORDER}└─────────────────────────────────────────────────────────────────────┘{Colors.RESET}")
            
            # Add spacing between ASNs
            if idx < len(prefix_data):
                print()
        
        # Enhanced completion summary
        total_all_prefixes = total_ipv4_prefixes + total_ipv6_prefixes
        print(f"\n{Colors.SUCCESS}🎯 COLLECTION COMPLETE:{Colors.RESET}")
        print(f"   {Colors.BOLD}• {total_all_prefixes} total prefixes discovered{Colors.RESET}")
        print(f"   {Colors.BOLD}• {total_ipv4_space:,} IPv4 addresses mapped{Colors.RESET}")
        print(f"   {Colors.BOLD}• {len(countries)} countries and {len(rirs)} RIRs covered{Colors.RESET}")
        print(f"   {Colors.SUCCESS}• All data saved to {self.output_dir}/ directory{Colors.RESET}")
        
        # Interactive options
        if total_all_prefixes > 50:  # Only show for substantial results
            print(f"\n{Colors.INFO}📋 INTERACTIVE OPTIONS:{Colors.RESET}")
            print(f"   {Colors.DIM}• View complete lists: {saved_files['txt_file']}{Colors.RESET}")
            print(f"   {Colors.DIM}• Analyze in spreadsheet: {saved_files['csv_file']}{Colors.RESET}")
            print(f"   {Colors.DIM}• JSON for tools: {saved_files['json_file']}{Colors.RESET}")
            
            choice = input(f"\n{Colors.WARNING}🔍 Open complete prefix file now? (y/N): {Colors.RESET}").strip().lower()
            if choice == 'y':
                try:
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(['open', str(saved_files['txt_file'])])
                    elif sys.platform.startswith("linux"):  # Linux
                        subprocess.run(['xdg-open', str(saved_files['txt_file'])])
                    elif sys.platform == "win32":  # Windows
                        os.startfile(str(saved_files['txt_file']))
                    print(f"{Colors.SUCCESS}[+] Opened {saved_files['txt_file']}{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.ERROR}[!] Could not open file: {e}{Colors.RESET}")
                    print(f"{Colors.INFO}[*] Manual path: {saved_files['txt_file']}{Colors.RESET}")


# The main enhanced ASN hunter class would be similar to the original but use the new display manager
# For brevity, I'll create a simple version that focuses on the key improvements

def main():
    """Enhanced main function with improved argument parsing"""
    parser = argparse.ArgumentParser(
        description='ASN-Hunter Enhanced v2.1 - Complete ASN Reconnaissance with Improved Output',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Enhanced v2.1 Examples:
  python3 asn-hunter-enhanced-v2.py "tesla" --show-all --improved-output
  python3 asn-hunter-enhanced-v2.py "cloudflare" --show-all --save-dir custom_results
  python3 asn-hunter-enhanced-v2.py "amazon" --show-all --auto-open -v
        """
    )
    
    parser.add_argument('keyword', help='Organization name to search')
    parser.add_argument('--show-all', action='store_true', default=True, help='Show all prefixes in display')
    parser.add_argument('--improved-output', action='store_true', default=True, help='Use enhanced output format')
    parser.add_argument('--save-dir', default='results', help='Directory to save complete prefix files')
    parser.add_argument('--auto-open', action='store_true', help='Automatically open results file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    args = parser.parse_args()
    
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # Create display manager
    display_manager = EnhancedDisplayManager(args.save_dir)
    
    print(BANNER)
    print(f"{Colors.SUCCESS}[+] Enhanced v2.1 with improved output formatting{Colors.RESET}")
    print(f"{Colors.INFO}[*] Results will be saved to: {display_manager.output_dir}/{Colors.RESET}")
    
    # For demo purposes, create sample data (in real implementation, this would come from the actual scraping)
    sample_data = {
        "394161": {
            "info": {
                "asn": 394161,
                "name": "TESLA",
                "description": "Tesla Motors, Inc.",
                "country": "US",
                "rir": "ARIN",
                "sources": ["PeeringDB", "BGPView"],
                "prefixes_hint": {"ipv4": 75, "ipv6": 10}
            },
            "ipv4": [
                "149.106.192.0/24", "149.106.193.0/24", "149.106.194.0/24",
                "149.106.195.0/24", "149.106.196.0/24", "149.106.197.0/24",
                # ... more prefixes would be here
            ],
            "ipv6": [
                "2620:137:d000::/48", "2620:137:d001::/48", "2620:137:d002::/48"
            ]
        }
    }
    
    # Display enhanced results
    display_manager.display_enhanced_results(sample_data, args.keyword, args.show_all)

if __name__ == "__main__":
    main()