#!/usr/bin/env python3
"""
Lyrics Extractor for Spotify Tracks
This script adds proper lyrics extraction to existing CSV files.
Handles the "Show more" button and extracts complete lyrics.
"""

import time
import random
import pandas as pd
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

def setup_logging():
    """Setup logging for lyrics extraction"""
    log_filename = f"lyrics_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class LyricsExtractor:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver optimized for lyrics extraction"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Keep some capabilities for proper interaction
        # Don't disable JavaScript since we need to click "Show more"
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        service = Service('/usr/local/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.set_page_load_timeout(20)
        self.driver.implicitly_wait(5)
    
    def extract_full_lyrics(self, track_id, track_name):
        """Extract complete lyrics with 'Show more' handling"""
        try:
            url = f"https://open.spotify.com/track/{track_id}"
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Look for lyrics section
            try:
                lyrics_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='lyrics-line-always-visible']"))
                )
            except TimeoutException:
                return "No lyrics available"
            
            # First, collect all visible lyrics lines
            visible_lyrics = []
            visible_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='lyrics-line-always-visible']")
            
            for element in visible_elements:
                line_text = element.text.strip()
                if line_text:
                    visible_lyrics.append(line_text)
            
            # Look for "Show more" button
            show_more_clicked = False
            try:
                show_more_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Show more'], button[aria-label*='…Show more']")
                if show_more_button.is_displayed():
                    # Scroll to button and click
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
                    time.sleep(1)
                    show_more_button.click()
                    time.sleep(2)  # Wait for expansion
                    show_more_clicked = True
            except NoSuchElementException:
                # No "Show more" button found, use visible lyrics
                pass
            except Exception as e:
                logging.warning(f"Error clicking 'Show more' for {track_name}: {e}")
            
            # After clicking "Show more", collect all lyrics
            all_lyrics = []
            
            if show_more_clicked:
                # Look for all lyrics in the expanded container
                try:
                    # Try different selectors for lyrics lines
                    lyrics_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        "p[data-encore-id='text'][dir='auto'], [data-testid='lyrics-line-always-visible']")
                    
                    for element in lyrics_elements:
                        line_text = element.text.strip()
                        if line_text and line_text not in ["Lyrics", "…Show more", "Show less"]:
                            all_lyrics.append(line_text)
                
                except Exception as e:
                    logging.warning(f"Error extracting expanded lyrics for {track_name}: {e}")
                    # Fallback to visible lyrics
                    all_lyrics = visible_lyrics
            else:
                all_lyrics = visible_lyrics
            
            # Clean and format lyrics
            if all_lyrics:
                # Remove duplicates while preserving order
                seen = set()
                unique_lyrics = []
                for line in all_lyrics:
                    if line not in seen:
                        seen.add(line)
                        unique_lyrics.append(line)
                
                return " | ".join(unique_lyrics)
            else:
                return "No lyrics found"
                
        except Exception as e:
            logging.error(f"Error extracting lyrics for {track_name} ({track_id}): {e}")
            return f"Error: {str(e)}"
    
    def add_lyrics_to_csv(self, input_csv, output_csv, start_index=0, max_tracks=None):
        """Add lyrics to existing CSV file"""
        df = pd.read_csv(input_csv)
        
        if max_tracks:
            df = df.head(start_index + max_tracks)
        
        print(f"🎵 Adding lyrics to {len(df) - start_index} tracks")
        print(f"Starting from index: {start_index}")
        
        total_processed = 0
        success_count = 0
        
        for index, row in df.iterrows():
            if index < start_index:
                continue
                
            track_id = row['track_id']
            track_name = row['track_name']
            
            # Skip if lyrics already exist and are not placeholder
            if pd.notna(row.get('lyrics')) and row['lyrics'] not in ['Skipped for speed', 'No lyrics available']:
                print(f"⏭️  Skipping {track_name} (lyrics already exist)")
                continue
            
            print(f"🎵 Extracting lyrics: {track_name}")
            
            start_time = time.time()
            lyrics = self.extract_full_lyrics(track_id, track_name)
            processing_time = time.time() - start_time
            
            # Update the DataFrame
            df.at[index, 'lyrics'] = lyrics
            df.at[index, 'lyrics_processing_time'] = processing_time
            
            total_processed += 1
            if not lyrics.startswith("Error") and lyrics != "No lyrics available":
                success_count += 1
            
            print(f"✅ Completed in {processing_time:.1f}s | Success rate: {success_count/total_processed:.1%}")
            
            # Save progress every 10 tracks
            if total_processed % 10 == 0:
                df.to_csv(output_csv, index=False)
                print(f"💾 Progress saved: {total_processed} tracks processed")
            
            # Delay between requests
            time.sleep(random.uniform(1, 3))
            
            # Browser restart every 100 tracks
            if total_processed % 100 == 0:
                print("🔄 Restarting browser...")
                self.driver.quit()
                time.sleep(5)
                self.setup_driver()
        
        # Final save
        df.to_csv(output_csv, index=False)
        
        success_rate = success_count / total_processed if total_processed > 0 else 0
        print(f"\n🎉 Lyrics extraction completed!")
        print(f"Total processed: {total_processed}")
        print(f"Success rate: {success_rate:.1%}")
        
        return df

def main():
    """Main execution"""
    import glob
    
    # Find the latest fast scraper file
    fast_files = glob.glob("/workspaces/Songs4Image/spotify_data_fast_*.csv")
    if not fast_files:
        print("❌ No fast scraper files found!")
        return
    
    # Get the latest file
    latest_file = max(fast_files, key=lambda x: int(x.split('_')[-1].replace('.csv', '')))
    print(f"📁 Using file: {latest_file}")
    
    # Create output filename
    output_file = latest_file.replace('.csv', '_with_lyrics.csv')
    
    # Setup
    logger = setup_logging()
    extractor = LyricsExtractor()
    
    try:
        # Extract lyrics for a sample (first 50 tracks) to test
        extractor.add_lyrics_to_csv(latest_file, output_file, start_index=0, max_tracks=50)
    except KeyboardInterrupt:
        print("\n⏹️ Lyrics extraction interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if extractor.driver:
            extractor.driver.quit()

if __name__ == "__main__":
    main()
