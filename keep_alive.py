#!/usr/bin/env python3
"""
Keep Alive Script for Codespace
This script will periodically print a status message to keep the terminal active
and prevent the codespace from timing out due to inactivity.
"""

import time
import datetime
import subprocess
import os

def check_scraper_status():
    """Check if the fast scraper is still running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'fast_scraper.py'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def get_latest_progress_file():
    """Get the latest progress file to show current status"""
    try:
        files = [f for f in os.listdir('.') if f.startswith('spotify_data_fast_') and f.endswith('.csv')]
        if files:
            # Sort by the number in filename to get latest
            numbers = []
            for f in files:
                try:
                    num = int(f.replace('spotify_data_fast_', '').replace('.csv', ''))
                    numbers.append((num, f))
                except:
                    continue
            if numbers:
                numbers.sort(reverse=True)
                return numbers[0]
        
        # Also check old progress files
        old_files = [f for f in os.listdir('.') if f.startswith('spotify_data_progress_') and f.endswith('.csv')]
        if old_files:
            numbers = []
            for f in old_files:
                try:
                    num = int(f.replace('spotify_data_progress_', '').replace('.csv', ''))
                    numbers.append((num, f))
                except:
                    continue
            if numbers:
                numbers.sort(reverse=True)
                return numbers[0]
    except:
        pass
    return None, None

def main():
    print("🔄 Keep Alive Script Started")
    print("This will keep your codespace active while the scraper runs")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    
    start_time = datetime.datetime.now()
    
    while True:
        try:
            current_time = datetime.datetime.now()
            elapsed = current_time - start_time
            
            # Check scraper status
            scraper_running = check_scraper_status()
            
            # Get progress info
            latest_count, latest_file = get_latest_progress_file()
            
            # Print status
            status_msg = f"⏰ {current_time.strftime('%H:%M:%S')} | "
            status_msg += f"Uptime: {str(elapsed).split('.')[0]} | "
            status_msg += f"Scraper: {'🟢 Running' if scraper_running else '🔴 Stopped'}"
            
            if latest_count:
                status_msg += f" | Progress: {latest_count}/10000 tracks"
            
            print(status_msg)
            
            # If scraper stops, give a warning
            if not scraper_running:
                print("⚠️  WARNING: Fast scraper is not running!")
                print("   You may need to restart it: source .venv/bin/activate && python fast_scraper.py")
            
            # Wait 2 minutes before next check (keeps activity frequent enough)
            time.sleep(120)
            
        except KeyboardInterrupt:
            print("\n🛑 Keep Alive Script Stopped")
            print("Your codespace may now timeout after 30 minutes of inactivity")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()
