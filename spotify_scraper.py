import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import requests
from urllib.parse import urlparse
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpotifyScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        self.results = []
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        chrome_options = Options()
        
        # Essential headless options for container environment
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.66 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.66 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.66 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Additional options for performance and stealth
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use system chromedriver
        service = Service("/usr/local/bin/chromedriver")
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to hide webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def get_high_quality_image_url(self, image_urls):
        """Extract the highest quality image URL from srcset"""
        if not image_urls:
            return None
            
        # Look for the highest resolution (640w is typically the highest)
        for url in image_urls:
            if "640w" in url or "0000b273" in url:  # 0000b273 indicates 640x640
                return url.split()[0]  # Remove the width specification
        
        # Fallback to the last (usually highest quality) image
        return image_urls[-1].split()[0] if image_urls else None
    
    def extract_lyrics(self, track_id):
        """Extract lyrics from Spotify track page"""
        url = f"https://open.spotify.com/track/{track_id}"
        
        try:
            self.driver.get(url)
            self.random_delay(2, 4)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            lyrics_text = ""
            
            # Look for lyrics section
            try:
                # Find lyrics container
                lyrics_container = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='lyrics']"))
                )
                
                # Check for "Show more" button and click it
                try:
                    show_more_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Show more'], button[aria-controls*='lyrics']")
                    if show_more_btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", show_more_btn)
                        self.random_delay(1, 2)
                except:
                    pass  # No show more button or already expanded
                
                # Extract all lyric lines
                lyric_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='lyrics-line'], p[data-encore-id='text'][dir='auto']")
                
                lyrics_lines = []
                for element in lyric_elements:
                    text = element.text.strip()
                    if text and text not in lyrics_lines:  # Avoid duplicates
                        lyrics_lines.append(text)
                
                lyrics_text = "\n".join(lyrics_lines)
                
            except TimeoutException:
                logger.info(f"No lyrics found for track {track_id}")
                lyrics_text = "No lyrics available"
                
            return lyrics_text
            
        except Exception as e:
            logger.error(f"Error extracting lyrics for {track_id}: {str(e)}")
            return "Error extracting lyrics"
    
    def extract_cover_image(self, track_id):
        """Extract cover image URL from Spotify track page"""
        try:
            # Look for cover image
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='scdn.co/image']")
            
            for img in img_elements:
                src = img.get_attribute('src')
                srcset = img.get_attribute('srcset')
                
                if src and 'scdn.co/image' in src:
                    # If srcset is available, get the highest quality
                    if srcset:
                        urls = srcset.split(',')
                        high_quality_url = self.get_high_quality_image_url(urls)
                        if high_quality_url:
                            return high_quality_url
                    
                    # Fallback to src
                    return src
            
            logger.info(f"No cover image found for track {track_id}")
            return "No image available"
            
        except Exception as e:
            logger.error(f"Error extracting cover image for {track_id}: {str(e)}")
            return "Error extracting image"
    
    def scrape_track(self, track_id, track_name):
        """Scrape both lyrics and cover image for a track"""
        logger.info(f"Processing: {track_name} (ID: {track_id})")
        
        try:
            # Extract lyrics
            lyrics = self.extract_lyrics(track_id)
            
            # Extract cover image (from the same page)
            cover_image = self.extract_cover_image(track_id)
            
            result = {
                'track_id': track_id,
                'track_name': track_name,
                'spotify_url': f"https://open.spotify.com/track/{track_id}",
                'lyrics': lyrics,
                'cover_image_url': cover_image
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing track {track_id}: {str(e)}")
            return {
                'track_id': track_id,
                'track_name': track_name,
                'spotify_url': f"https://open.spotify.com/track/{track_id}",
                'lyrics': f"Error: {str(e)}",
                'cover_image_url': "Error extracting image"
            }
    
    def save_progress(self, filename="spotify_data_progress.csv"):
        """Save current progress to CSV"""
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_csv(f"/workspaces/Songs4Image/{filename}", index=False)
            logger.info(f"Progress saved: {len(self.results)} tracks completed")
    
    def scrape_all_tracks(self, csv_file_path, start_index=0, batch_size=50):
        """Scrape all tracks from CSV file with batch processing"""
        # Load track data
        df = pd.read_csv(csv_file_path)
        total_tracks = len(df)
        
        logger.info(f"Starting scraping from index {start_index}")
        logger.info(f"Total tracks to process: {total_tracks - start_index}")
        
        batch_count = 0
        
        for index, row in df.iterrows():
            if index < start_index:
                continue
                
            track_id = row['track_id']
            track_name = row['track_name']
            
            # Scrape track data
            result = self.scrape_track(track_id, track_name)
            self.results.append(result)
            
            # Random delay between requests (2-5 seconds)
            self.random_delay(2, 5)
            
            # Save progress every batch_size tracks
            if len(self.results) % batch_size == 0:
                self.save_progress()
                batch_count += 1
                
                # Longer break every few batches to avoid detection
                if batch_count % 5 == 0:
                    logger.info("Taking extended break to avoid detection...")
                    time.sleep(random.uniform(30, 60))  # 30-60 second break
                
                # Restart browser every 200 tracks to clear memory
                if len(self.results) % 200 == 0:
                    logger.info("Restarting browser to clear memory...")
                    self.driver.quit()
                    time.sleep(5)
                    self.setup_driver()
            
            # Progress update
            if (index + 1) % 10 == 0:
                progress = ((index + 1 - start_index) / (total_tracks - start_index)) * 100
                logger.info(f"Progress: {index + 1}/{total_tracks} ({progress:.1f}%)")
        
        # Final save
        self.save_progress("spotify_data_final.csv")
        logger.info("Scraping completed!")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    """Main execution function"""
    scraper = SpotifyScraper()
    
    try:
        # Load the track IDs and names CSV
        csv_file = "/workspaces/Songs4Image/track_ids_and_names.csv"
        
        # You can start from a specific index if resuming
        start_index = 0  # Change this if resuming from a specific point
        
        # Start scraping
        scraper.scrape_all_tracks(csv_file, start_index=start_index)
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        scraper.save_progress("spotify_data_interrupted.csv")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        scraper.save_progress("spotify_data_error.csv")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
