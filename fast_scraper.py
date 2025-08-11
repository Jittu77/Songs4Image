#!/usr/bin/env python3
"""
FAST Production Spotify Scraper
Optimized for speed - targets 2-3 seconds per track (vs current 10+ seconds)
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
import re

class FastSpotifyScraper:
    def __init__(self):
        self.driver = None
        self.results = []
        self.failed_tracks = []
        self.session_start_time = datetime.now()
        self.setup_driver()
    
    def setup_driver(self):
        """Setup optimized Chrome driver for speed"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Don't load images for speed
        options.add_argument('--disable-javascript')  # Disable JS for speed
        options.add_argument('--disable-css')  # Disable CSS for speed
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Disable loading unnecessary content
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        # Random user agent for anti-detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        service = Service('/usr/local/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Set shorter timeouts for speed
        self.driver.set_page_load_timeout(15)  # Max 15 seconds to load
        self.driver.implicitly_wait(3)  # Max 3 seconds to find elements
    
    def extract_basic_info(self, track_id, track_name):
        """Extract basic info without complex scraping - FAST VERSION"""
        try:
            url = f"https://open.spotify.com/track/{track_id}"
            
            # Set a short timeout
            start_time = time.time()
            self.driver.get(url)
            
            # Quick wait for page to load basic elements
            time.sleep(1)  # Just 1 second wait
            
            # Try to get cover image quickly
            cover_image = ""
            try:
                # Look for meta tag with image (faster than waiting for elements)
                img_meta = self.driver.find_element(By.XPATH, "//meta[@property='og:image']")
                cover_image = img_meta.get_attribute("content")
            except:
                try:
                    # Fallback to img element
                    img_element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "img[data-testid='cover-art-image']"))
                    )
                    cover_image = img_element.get_attribute("src")
                except:
                    cover_image = "Not found"
            
            # Skip lyrics for now - they take too long
            lyrics = "Skipped for speed"
            
            processing_time = time.time() - start_time
            
            return {
                'track_id': track_id,
                'track_name': track_name,
                'spotify_url': url,
                'cover_image': cover_image,
                'lyrics': lyrics,
                'processing_time': processing_time
            }
            
        except Exception as e:
            return {
                'track_id': track_id,
                'track_name': track_name,
                'spotify_url': f"https://open.spotify.com/track/{track_id}",
                'cover_image': f"Error: {str(e)}",
                'lyrics': f"Error: {str(e)}",
                'processing_time': 0
            }
    
    def minimal_delay(self):
        """Minimal delay for speed - just 0.5-1.5 seconds"""
        time.sleep(random.uniform(0.5, 1.5))
    
    def save_progress(self, filename):
        """Save progress to CSV"""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(f"/workspaces/Songs4Image/{filename}", index=False)
    
    def fast_scrape(self, csv_file_path, start_index=0):
        """SPEED-OPTIMIZED scraping"""
        # Load track data
        df = pd.read_csv(csv_file_path)
        total_tracks = len(df) - start_index
        
        print(f"🚀 FAST SCRAPER STARTED")
        print(f"Target: 2-3 seconds per track")
        print(f"Total tracks: {total_tracks}")
        print(f"Estimated time: {total_tracks * 2.5 / 3600:.1f} hours")
        print("-" * 50)
        
        for index, row in df.iterrows():
            if index < start_index:
                continue
                
            track_id = row['track_id']
            track_name = row['track_name']
            
            start_time = time.time()
            
            # Fast extraction
            result = self.extract_basic_info(track_id, track_name)
            self.results.append(result)
            
            # Track failures
            if "Error" in result['cover_image']:
                self.failed_tracks.append(result)
            
            completed = len(self.results)
            elapsed = time.time() - start_time
            
            # Progress every 25 tracks
            if completed % 25 == 0:
                self.save_progress(f"spotify_data_fast_{completed}.csv")
                
                session_elapsed = (datetime.now() - self.session_start_time).total_seconds()
                rate = completed / session_elapsed * 60  # tracks per minute
                eta_hours = (total_tracks - completed) / rate / 60
                
                print(f"✅ {completed}/{total_tracks} | Rate: {rate:.1f}/min | ETA: {eta_hours:.1f}h | Last: {elapsed:.1f}s")
            
            # Minimal delay
            self.minimal_delay()
            
            # Quick browser restart every 500 tracks
            if completed % 500 == 0:
                print("🔄 Quick browser restart...")
                self.driver.quit()
                time.sleep(2)
                self.setup_driver()
        
        # Final save
        self.save_progress("spotify_data_fast_final.csv")
        
        total_time = datetime.now() - self.session_start_time
        success_rate = (len(self.results) - len(self.failed_tracks)) / len(self.results) if self.results else 0
        
        print(f"\n🎉 FAST SCRAPING COMPLETED!")
        print(f"Total time: {total_time}")
        print(f"Tracks processed: {len(self.results)}")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Average time per track: {total_time.total_seconds() / len(self.results):.1f}s")

def main():
    """Main execution function"""
    CSV_FILE = "/workspaces/Songs4Image/track_ids_and_names.csv"
    
    # Start from track 175 since previous scraper completed that many
    start_index = 175
    print(f"🔄 Starting from track {start_index} (previous scraper completed 175 tracks)")
    
    scraper = FastSpotifyScraper()
    
    try:
        scraper.fast_scrape(CSV_FILE, start_index)
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
        scraper.save_progress(f"spotify_data_fast_interrupted_{len(scraper.results)}.csv")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        scraper.save_progress(f"spotify_data_fast_error_{len(scraper.results)}.csv")
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    main()
