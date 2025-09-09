#!/usr/bin/env python3
"""
Quick test of the enhanced ASN hunter with Google
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced hunter
try:
    # Read the enhanced script and simulate running it with auto selection
    print("Testing Google ASN discovery...")
    
    # For this test, let's run the speed version which has auto mode
    cmd = 'python3 asn-speed.py "Google" --auto --workers 5'
    print(f"Running: {cmd}")
    os.system(cmd)
    
except Exception as e:
    print(f"Error: {e}")
    print("Let's try the multi-tool instead...")
    os.system('python3 asn-multi-tool.py speed "Google" --auto')