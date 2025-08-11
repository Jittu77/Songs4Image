#!/usr/bin/env python3
"""
Production Spotify Scraper for 10,000 songs
Optimized for 5-6 hour completion with anti-detection measures
"""

import pandas as pd
import time
import random
import os
import sys
from datetime import datetime
import logging
from spotify_scraper import SpotifyScraper

# Global logger variable
logger = None

# Enhanced logging setup
def setup_logging():
    """Setup enhanced logging with file output"""
    log_filename = f"/workspaces/Songs4Image/scraper_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

class ProductionSpotifyScraper(SpotifyScraper):
    """Enhanced scraper for production use"""
    
    def __init__(self, max_retries=3):
        super().__init__()
        self.max_retries = max_retries
        self.failed_tracks = []
        self.session_start_time = datetime.now()
        
    def scrape_track_with_retry(self, track_id, track_name, attempt=1):
        """Scrape track with retry mechanism"""
        try:
            result = self.scrape_track(track_id, track_name)
            
            # Check if scraping was successful
            if ("Error" in result['lyrics'] or "Error" in result['cover_image_url']) and attempt < self.max_retries:
                logger.warning(f"Retrying track {track_id} (attempt {attempt + 1})")
                time.sleep(random.uniform(5, 10))  # Longer delay for retry
                return self.scrape_track_with_retry(track_id, track_name, attempt + 1)
            
            return result
            
        except Exception as e:
            if attempt < self.max_retries:
                logger.warning(f"Retrying track {track_id} due to error: {str(e)} (attempt {attempt + 1})")
                time.sleep(random.uniform(5, 10))
                return self.scrape_track_with_retry(track_id, track_name, attempt + 1)
            else:
                logger.error(f"Failed to scrape {track_id} after {self.max_retries} attempts")
                self.failed_tracks.append({'track_id': track_id, 'track_name': track_name, 'error': str(e)})
                return {
                    'track_id': track_id,
                    'track_name': track_name,
                    'spotify_url': f"https://open.spotify.com/track/{track_id}",
                    'lyrics': f"Failed after {self.max_retries} attempts: {str(e)}",
                    'cover_image_url': "Failed to extract"
                }
    
    def calculate_eta(self, completed, total, start_time):
        """Calculate estimated time of arrival"""
        if completed == 0:
            return "Unknown"
        
        elapsed = datetime.now() - start_time
        rate = completed / elapsed.total_seconds()  # tracks per second
        remaining = total - completed
        eta_seconds = remaining / rate
        
        hours = int(eta_seconds // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def adaptive_delay(self, success_rate, base_delay_min=2, base_delay_max=5):
        """Adaptive delay based on success rate"""
        if success_rate < 0.8:  # If success rate is low, slow down
            delay_min = base_delay_min * 1.5
            delay_max = base_delay_max * 2
        elif success_rate > 0.95:  # If success rate is high, speed up slightly
            delay_min = base_delay_min * 0.8
            delay_max = base_delay_max * 0.8
        else:
            delay_min = base_delay_min
            delay_max = base_delay_max
        
        self.random_delay(delay_min, delay_max)
    
    def production_scrape(self, csv_file_path, start_index=0, target_time_hours=6):
        """Optimized scraping for production with time target"""
        
        # Load track data
        df = pd.read_csv(csv_file_path)
        total_tracks = len(df) - start_index
        
        logger.info(f"Starting production scrape")
        logger.info(f"Target completion time: {target_time_hours} hours")
        logger.info(f"Total tracks to process: {total_tracks}")
        logger.info(f"Starting from index: {start_index}")
        
        # Calculate target rate (tracks per second)
        target_rate = total_tracks / (target_time_hours * 3600)
        logger.info(f"Target rate: {target_rate:.4f} tracks/second ({target_rate*60:.2f} tracks/minute)")
        
        success_count = 0
        
        for index, row in df.iterrows():
            if index < start_index:
                continue
                
            track_id = row['track_id']
            track_name = row['track_name']
            
            # Scrape with retry
            result = self.scrape_track_with_retry(track_id, track_name)
            self.results.append(result)
            
            # Track success rate
            if "Error" not in result['lyrics'] and "Failed" not in result['lyrics']:
                success_count += 1
            
            completed = len(self.results)
            success_rate = success_count / completed if completed > 0 else 0
            
            # Adaptive delay based on performance
            self.adaptive_delay(success_rate)
            
            # Progress reporting and saves
            if completed % 25 == 0:  # More frequent saves
                self.save_progress(f"spotify_data_progress_{completed}.csv")
                
                eta = self.calculate_eta(completed, total_tracks, self.session_start_time)
                progress_percent = (completed / total_tracks) * 100
                
                logger.info(f"Progress: {completed}/{total_tracks} ({progress_percent:.1f}%) | "
                          f"Success rate: {success_rate:.2f} | ETA: {eta}")
            
            # Extended breaks for anti-detection
            if completed % 100 == 0:
                logger.info("Taking extended break (60-120 seconds)...")
                time.sleep(random.uniform(60, 120))
            
            # Browser restart for memory management
            if completed % 300 == 0:
                logger.info("Restarting browser...")
                self.driver.quit()
                time.sleep(10)
                self.setup_driver()
                time.sleep(5)
            
            # Check if we're on track time-wise
            elapsed_hours = (datetime.now() - self.session_start_time).total_seconds() / 3600
            if elapsed_hours > 0.5:  # After 30 minutes, check pace
                current_rate = completed / (elapsed_hours * 3600)
                if current_rate < target_rate * 0.8:  # If we're 20% behind target
                    logger.warning(f"Behind target pace. Current: {current_rate:.4f}, Target: {target_rate:.4f}")
                    # Reduce delays slightly
                    base_delay_min = max(1, 2 * 0.8)
                    base_delay_max = max(2, 5 * 0.8)
        
        # Final save and summary
        self.save_progress("spotify_data_final.csv")
        
        # Save failed tracks for retry
        if self.failed_tracks:
            failed_df = pd.DataFrame(self.failed_tracks)
            failed_df.to_csv("/workspaces/Songs4Image/failed_tracks.csv", index=False)
            logger.info(f"Saved {len(self.failed_tracks)} failed tracks for retry")
        
        # Final statistics
        total_time = datetime.now() - self.session_start_time
        final_success_rate = success_count / len(self.results) if self.results else 0
        
        logger.info(f"Scraping completed!")
        logger.info(f"Total time: {total_time}")
        logger.info(f"Total tracks processed: {len(self.results)}")
        logger.info(f"Success rate: {final_success_rate:.2f}")
        logger.info(f"Failed tracks: {len(self.failed_tracks)}")

def main():
    """Main execution function"""
    global logger
    logger = setup_logging()
    
    # Configuration
    CSV_FILE = "/workspaces/Songs4Image/track_ids_and_names.csv"
    START_INDEX = 0  # Change this to resume from a specific point
    TARGET_HOURS = 6  # Target completion time
    
    scraper = ProductionSpotifyScraper(max_retries=3)
    
    try:
        # Check if CSV file exists
        if not os.path.exists(CSV_FILE):
            logger.error(f"CSV file not found: {CSV_FILE}")
            return
        
        # Start production scraping
        scraper.production_scrape(
            csv_file_path=CSV_FILE,
            start_index=START_INDEX,
            target_time_hours=TARGET_HOURS
        )
        
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
