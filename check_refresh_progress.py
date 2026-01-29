#!/usr/bin/env python3
"""
Quick progress checker for data refresh
Usage: python3 check_refresh_progress.py
"""

import os
import time

def check_progress():
    log_file = 'refresh_log.txt'
    
    if not os.path.exists(log_file):
        print("❌ Log file not found. Data refresh may not be running.")
        return
    
    with open(log_file, 'r') as f:
        content = f.read()
    
    # Count progress
    sectors_completed = content.count('Saved:')
    stocks_processed = content.count('✓')
    errors = content.count('✗')
    
    # Check completion
    completed = 'ALL SECTORS COMPLETED' in content
    
    # Get current sector
    lines = content.strip().split('\n')
    current_sector = "Unknown"
    for line in reversed(lines):
        if 'SECTOR:' in line:
            current_sector = line.split('SECTOR:')[1].strip().split('\n')[0]
            break
    
    # Get last line
    last_line = lines[-1] if lines else ""
    
    # Display status
    print("="*70)
    print("📊 DATA REFRESH PROGRESS")
    print("="*70)
    print(f"Sectors completed: {sectors_completed}/11")
    print(f"Stocks processed:  {stocks_processed}/205")
    print(f"Errors:            {errors}")
    print(f"Current sector:    {current_sector}")
    print(f"\nLast activity:")
    print(f"  {last_line[:70]}")
    
    if completed:
        print("\n✅ DATA REFRESH COMPLETED!")
    else:
        print(f"\n⏳ Still running... (Use Ctrl+C to stop monitoring)")
    
    print("="*70)
    
    return not completed

if __name__ == '__main__':
    print("Checking data refresh progress...\n")
    still_running = check_progress()
    
    if still_running:
        print("\nTo continue monitoring, run this script periodically.")
        print("Or check the log: tail -f refresh_log.txt")
