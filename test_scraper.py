#!/usr/bin/env python3
"""
Test script to verify the Spotify scraper setup and test with a few tracks
"""

import pandas as pd
from spotify_scraper import SpotifyScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_scraper():
    """Test the scraper with a few tracks"""
    
    # Load the track data
    try:
        df = pd.read_csv("/workspaces/Songs4Image/track_ids_and_names.csv")
        logger.info(f"Loaded {len(df)} tracks from CSV")
        
        # Test with first 5 tracks
        test_tracks = df.head(5)
        
        scraper = SpotifyScraper()
        
        for index, row in test_tracks.iterrows():
            track_id = row['track_id']
            track_name = row['track_name']
            
            logger.info(f"Testing track: {track_name} (ID: {track_id})")
            
            result = scraper.scrape_track(track_id, track_name)
            
            # Print results
            print(f"\n{'='*60}")
            print(f"Track: {result['track_name']}")
            print(f"ID: {result['track_id']}")
            print(f"URL: {result['spotify_url']}")
            print(f"Cover Image: {result['cover_image_url'][:100]}...")
            print(f"Lyrics (first 200 chars): {result['lyrics'][:200]}...")
            print(f"{'='*60}\n")
            
            # Save individual result for verification
            test_df = pd.DataFrame([result])
            test_df.to_csv(f"/workspaces/Songs4Image/test_result_{index}.csv", index=False)
        
        scraper.close()
        logger.info("Test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    test_scraper()
