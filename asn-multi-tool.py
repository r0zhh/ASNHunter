#!/usr/bin/env python3
"""
ASN-Multi-Tool: Comprehensive ASN Toolkit with All Modes
Version: 1.0.0
Purpose: All-in-one ASN reconnaissance with mode switching

AVAILABLE MODES:
- standard: Regular ASN discovery
- enhanced: Complete prefix discovery with advanced tactics
- stealth: Ultra-low profile reconnaissance  
- speed: Lightning-fast bulk processing
- monitor: Continuous monitoring mode
- compare: Compare ASN changes over time
"""

import argparse
import sys
import json
import os
from datetime import datetime
from pathlib import Path

# Import mode-specific hunters (when available)
try:
    from asn_hunter_enhanced import EnhancedASNHunter
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Multi-tool colors
class MultiColors:
    HEADER = "\033[38;5;93m"      # Purple
    SUCCESS = "\033[38;5;46m"     # Green
    ERROR = "\033[38;5;196m"      # Red
    WARNING = "\033[38;5;214m"    # Orange
    INFO = "\033[38;5;51m"        # Cyan
    RESET = "\033[0m"
    BOLD = "\033[1m"

# Multi-tool banner
MULTI_BANNER = f"""{MultiColors.HEADER}
 ╔═══════════════════════════════════════════════════════════════════════╗
 ║                          ASN-MULTI-TOOL                               ║
 ║                   Complete ASN Reconnaissance Suite                   ║
 ║                                                                       ║
 ║  Modes: standard | enhanced | stealth | speed | monitor | compare     ║
 ╚═══════════════════════════════════════════════════════════════════════╝
{MultiColors.RESET}
"""

class ASNMultiTool:
    """Main multi-tool coordinator"""
    
    def __init__(self):
        self.available_modes = self._check_available_modes()
        print(f"{MultiColors.INFO}[*] Available modes: {', '.join(self.available_modes)}{MultiColors.RESET}")
    
    def _check_available_modes(self):
        """Check which modes are available based on dependencies"""
        modes = ['standard']  # Always available
        
        # Check for enhanced mode
        if ENHANCED_AVAILABLE:
            modes.append('enhanced')
        
        # Check for other mode files
        script_dir = Path(__file__).parent
        
        if (script_dir / 'asn-stealth.py').exists():
            modes.append('stealth')
        
        if (script_dir / 'asn-speed.py').exists():
            modes.append('speed')
        
        # Advanced modes (if implemented)
        modes.extend(['monitor', 'compare'])
        
        return modes
    
    def run_standard_mode(self, args):
        """Run standard ASN discovery"""
        print(f"{MultiColors.INFO}[*] Running STANDARD mode{MultiColors.RESET}")
        
        # Import and run standard hunter
        try:
            import subprocess
            cmd = [
                sys.executable, 'asn-hunter.py', args.keyword
            ]
            if args.verbose:
                cmd.append('-v')
            if args.output:
                cmd.extend(['-o', args.output])
            
            subprocess.run(cmd)
        except Exception as e:
            print(f"{MultiColors.ERROR}[!] Standard mode failed: {e}{MultiColors.RESET}")
    
    def run_enhanced_mode(self, args):
        """Run enhanced ASN discovery with complete prefix collection"""
        print(f"{MultiColors.SUCCESS}[*] Running ENHANCED mode - Complete Discovery{MultiColors.RESET}")
        
        try:
            import subprocess
            cmd = [
                sys.executable, 'asn-hunter-enhanced.py', args.keyword,
                '--show-all'
            ]
            if args.verbose:
                cmd.append('-v')
            if args.output:
                cmd.extend(['-o', args.output])
            if hasattr(args, 'parallel') and args.parallel:
                cmd.append('--parallel')
            if hasattr(args, 'delay') and args.delay:
                cmd.extend(['--delay', str(args.delay)])
            
            subprocess.run(cmd)
        except Exception as e:
            print(f"{MultiColors.ERROR}[!] Enhanced mode failed: {e}{MultiColors.RESET}")
    
    def run_stealth_mode(self, args):
        """Run stealth reconnaissance"""
        print(f"{MultiColors.WARNING}[*] Running STEALTH mode - Ultra-Low Profile{MultiColors.RESET}")
        
        try:
            import subprocess
            cmd = [
                sys.executable, 'asn-stealth.py', args.keyword
            ]
            if hasattr(args, 'min_delay'):
                cmd.extend(['--min-delay', str(args.min_delay)])
            if hasattr(args, 'max_delay'):
                cmd.extend(['--max-delay', str(args.max_delay)])
            if hasattr(args, 'tor') and args.tor:
                cmd.append('--tor')
            if args.output:
                cmd.extend(['-o', args.output])
            
            subprocess.run(cmd)
        except Exception as e:
            print(f"{MultiColors.ERROR}[!] Stealth mode failed: {e}{MultiColors.RESET}")
    
    def run_speed_mode(self, args):
        """Run high-speed bulk processing"""
        print(f"{MultiColors.INFO}[*] Running SPEED mode - Lightning Fast{MultiColors.RESET}")
        
        try:
            import subprocess
            cmd = [
                sys.executable, 'asn-speed.py', args.keyword
            ]
            if hasattr(args, 'workers'):
                cmd.extend(['--workers', str(args.workers)])
            if hasattr(args, 'timeout'):
                cmd.extend(['--timeout', str(args.timeout)])
            if hasattr(args, 'auto') and args.auto:
                cmd.append('--auto')
            if args.output:
                cmd.extend(['-o', args.output])
            
            subprocess.run(cmd)
        except Exception as e:
            print(f"{MultiColors.ERROR}[!] Speed mode failed: {e}{MultiColors.RESET}")
    
    def run_monitor_mode(self, args):
        """Run continuous monitoring mode"""
        print(f"{MultiColors.INFO}[*] Running MONITOR mode - Continuous Surveillance{MultiColors.RESET}")
        
        # Simple monitoring implementation
        import time
        
        interval = getattr(args, 'interval', 3600)  # Default 1 hour
        output_dir = Path(args.output) if args.output else Path('monitor_results')
        output_dir.mkdir(exist_ok=True)
        
        print(f"{MultiColors.INFO}[*] Monitoring '{args.keyword}' every {interval}s{MultiColors.RESET}")
        print(f"{MultiColors.INFO}[*] Results stored in: {output_dir}{MultiColors.RESET}")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = output_dir / f"monitor_{timestamp}_{iteration:03d}.json"
                
                print(f"\n{MultiColors.SUCCESS}[+] Monitor iteration {iteration} at {timestamp}{MultiColors.RESET}")
                
                # Run enhanced mode for monitoring
                try:
                    import subprocess
                    cmd = [
                        sys.executable, 'asn-hunter-enhanced.py', args.keyword,
                        '--show-all', '-o', str(output_file)
                    ]
                    if args.verbose:
                        cmd.append('-v')
                    
                    subprocess.run(cmd, capture_output=not args.verbose)
                    print(f"{MultiColors.SUCCESS}[+] Results saved to {output_file}{MultiColors.RESET}")
                except Exception as e:
                    print(f"{MultiColors.ERROR}[!] Monitor iteration {iteration} failed: {e}{MultiColors.RESET}")
                
                print(f"{MultiColors.INFO}[*] Waiting {interval}s for next iteration...{MultiColors.RESET}")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n{MultiColors.WARNING}[!] Monitoring stopped by user after {iteration} iterations{MultiColors.RESET}")
    
    def run_compare_mode(self, args):
        """Compare ASN data across different time periods"""
        print(f"{MultiColors.INFO}[*] Running COMPARE mode - Change Detection{MultiColors.RESET}")
        
        if not args.compare_files or len(args.compare_files) < 2:
            print(f"{MultiColors.ERROR}[!] Compare mode requires at least 2 files{MultiColors.RESET}")
            return
        
        try:
            # Load comparison files
            datasets = []
            for file_path in args.compare_files:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    datasets.append({
                        'file': file_path,
                        'timestamp': data.get('timestamp', 'unknown'),
                        'data': data
                    })
            
            print(f"{MultiColors.INFO}[*] Comparing {len(datasets)} datasets{MultiColors.RESET}")
            
            # Simple comparison logic
            self._perform_comparison(datasets)
            
        except Exception as e:
            print(f"{MultiColors.ERROR}[!] Compare mode failed: {e}{MultiColors.RESET}")
    
    def _perform_comparison(self, datasets):
        """Perform detailed comparison between datasets"""
        if len(datasets) < 2:
            return
        
        baseline = datasets[0]
        current = datasets[-1]
        
        print(f"\n{MultiColors.HEADER}COMPARISON RESULTS:{MultiColors.RESET}")
        print(f"Baseline: {baseline['file']} ({baseline['timestamp']})")
        print(f"Current:  {current['file']} ({current['timestamp']})")
        
        # Extract ASNs and prefixes
        baseline_asns = set(baseline['data'].get('asns', {}).keys())
        current_asns = set(current['data'].get('asns', {}).keys())
        
        new_asns = current_asns - baseline_asns
        removed_asns = baseline_asns - current_asns
        common_asns = baseline_asns & current_asns
        
        print(f"\n{MultiColors.SUCCESS}ASN CHANGES:{MultiColors.RESET}")
        print(f"  New ASNs: {len(new_asns)}")
        if new_asns:
            for asn in sorted(new_asns):
                print(f"    + AS{asn}")
        
        print(f"  Removed ASNs: {len(removed_asns)}")
        if removed_asns:
            for asn in sorted(removed_asns):
                print(f"    - AS{asn}")
        
        # Compare prefixes for common ASNs
        print(f"\n{MultiColors.INFO}PREFIX CHANGES:{MultiColors.RESET}")
        for asn in sorted(common_asns):
            baseline_prefixes = set(
                baseline['data']['asns'][asn].get('ipv4_prefixes', []) +
                baseline['data']['asns'][asn].get('ipv6_prefixes', [])
            )
            current_prefixes = set(
                current['data']['asns'][asn].get('ipv4_prefixes', []) +
                current['data']['asns'][asn].get('ipv6_prefixes', [])
            )
            
            new_prefixes = current_prefixes - baseline_prefixes
            removed_prefixes = baseline_prefixes - current_prefixes
            
            if new_prefixes or removed_prefixes:
                print(f"  AS{asn}:")
                if new_prefixes:
                    print(f"    + {len(new_prefixes)} new prefixes")
                    for prefix in sorted(list(new_prefixes)[:5]):  # Show first 5
                        print(f"      + {prefix}")
                    if len(new_prefixes) > 5:
                        print(f"      ... and {len(new_prefixes) - 5} more")
                
                if removed_prefixes:
                    print(f"    - {len(removed_prefixes)} removed prefixes")
                    for prefix in sorted(list(removed_prefixes)[:5]):  # Show first 5
                        print(f"      - {prefix}")
                    if len(removed_prefixes) > 5:
                        print(f"      ... and {len(removed_prefixes) - 5} more")
    
    def show_help(self):
        """Show comprehensive help for all modes"""
        print(MULTI_BANNER)
        print(f"{MultiColors.HEADER}AVAILABLE MODES:{MultiColors.RESET}")
        
        modes_help = {
            'standard': 'Regular ASN discovery with basic prefix collection',
            'enhanced': 'Complete prefix discovery with 6 advanced tactics',
            'stealth': 'Ultra-low profile reconnaissance with anti-detection',
            'speed': 'Lightning-fast bulk processing with parallel execution',
            'monitor': 'Continuous monitoring with periodic data collection',
            'compare': 'Compare ASN datasets to detect changes over time'
        }
        
        for mode, description in modes_help.items():
            available = "✓" if mode in self.available_modes else "✗"
            print(f"  {available} {mode:10} - {description}")
        
        print(f"\n{MultiColors.INFO}USAGE EXAMPLES:{MultiColors.RESET}")
        print(f"  Standard:  python3 asn-multi-tool.py standard \"tesla\"")
        print(f"  Enhanced:  python3 asn-multi-tool.py enhanced \"tesla\" --show-all")
        print(f"  Stealth:   python3 asn-multi-tool.py stealth \"tesla\" --tor --min-delay 5")
        print(f"  Speed:     python3 asn-multi-tool.py speed \"tesla,google,amazon\" --auto")
        print(f"  Monitor:   python3 asn-multi-tool.py monitor \"tesla\" --interval 3600")
        print(f"  Compare:   python3 asn-multi-tool.py compare --files old.json new.json")
        
        print(f"\n{MultiColors.WARNING}For mode-specific help:{MultiColors.RESET}")
        print(f"  python3 asn-multi-tool.py MODE --help")
    
    def run(self, args):
        """Main execution dispatcher"""
        if args.command == 'help' or not hasattr(args, 'command') or not args.command:
            self.show_help()
            return
        
        if args.command not in self.available_modes:
            print(f"{MultiColors.ERROR}[!] Mode '{args.command}' not available{MultiColors.RESET}")
            print(f"{MultiColors.INFO}[*] Available modes: {', '.join(self.available_modes)}{MultiColors.RESET}")
            return
        
        print(MULTI_BANNER)
        
        # Dispatch to appropriate mode
        mode_map = {
            'standard': self.run_standard_mode,
            'enhanced': self.run_enhanced_mode,
            'stealth': self.run_stealth_mode,
            'speed': self.run_speed_mode,
            'monitor': self.run_monitor_mode,
            'compare': self.run_compare_mode
        }
        
        mode_function = mode_map.get(args.command)
        if mode_function:
            mode_function(args)
        else:
            print(f"{MultiColors.ERROR}[!] Mode '{args.command}' not implemented{MultiColors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description='ASN-Multi-Tool - Complete ASN Reconnaissance Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available modes')
    
    # Standard mode
    standard_parser = subparsers.add_parser('standard', help='Regular ASN discovery')
    standard_parser.add_argument('keyword', help='Organization name to search')
    standard_parser.add_argument('-v', '--verbose', action='store_true')
    standard_parser.add_argument('-o', '--output', help='Output file')
    
    # Enhanced mode
    enhanced_parser = subparsers.add_parser('enhanced', help='Complete prefix discovery')
    enhanced_parser.add_argument('keyword', help='Organization name to search')
    enhanced_parser.add_argument('-v', '--verbose', action='store_true')
    enhanced_parser.add_argument('-o', '--output', help='Output file')
    enhanced_parser.add_argument('--show-all', action='store_true', default=True)
    enhanced_parser.add_argument('--parallel', action='store_true')
    enhanced_parser.add_argument('--delay', type=int, default=1)
    
    # Stealth mode
    stealth_parser = subparsers.add_parser('stealth', help='Ultra-low profile reconnaissance')
    stealth_parser.add_argument('keyword', help='Target organization')
    stealth_parser.add_argument('--min-delay', type=int, default=3)
    stealth_parser.add_argument('--max-delay', type=int, default=8)
    stealth_parser.add_argument('--tor', action='store_true')
    stealth_parser.add_argument('-o', '--output', help='Output file')
    
    # Speed mode
    speed_parser = subparsers.add_parser('speed', help='Lightning-fast bulk processing')
    speed_parser.add_argument('keyword', help='Keywords (single, comma-separated, or @file)')
    speed_parser.add_argument('--workers', type=int, default=10)
    speed_parser.add_argument('--timeout', type=int, default=5)
    speed_parser.add_argument('--auto', action='store_true')
    speed_parser.add_argument('-o', '--output', help='Output file')
    
    # Monitor mode
    monitor_parser = subparsers.add_parser('monitor', help='Continuous monitoring')
    monitor_parser.add_argument('keyword', help='Organization to monitor')
    monitor_parser.add_argument('--interval', type=int, default=3600, help='Check interval in seconds')
    monitor_parser.add_argument('-v', '--verbose', action='store_true')
    monitor_parser.add_argument('-o', '--output', help='Output directory')
    
    # Compare mode
    compare_parser = subparsers.add_parser('compare', help='Compare datasets')
    compare_parser.add_argument('--files', dest='compare_files', nargs='+', required=True, 
                                help='JSON files to compare')
    
    # Help command
    subparsers.add_parser('help', help='Show detailed help')
    
    args = parser.parse_args()
    
    multi_tool = ASNMultiTool()
    
    try:
        multi_tool.run(args)
    except KeyboardInterrupt:
        print(f"\n{MultiColors.WARNING}[!] Multi-tool interrupted by user{MultiColors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{MultiColors.ERROR}[!] Multi-tool failed: {e}{MultiColors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()