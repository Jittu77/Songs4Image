# Spotify Scraper Usage Guide

## Files Created:

1. **spotify_scraper.py** - Main scraper class with anti-detection measures
2. **production_scraper.py** - Optimized for 10,000 songs in 5-6 hours
3. **test_scraper.py** - Test script for verification
4. **requirements.txt** - Required Python packages

## Setup Instructions:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Chrome browser** (if not already installed):
   ```bash
   # Ubuntu/Debian
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
   sudo apt update
   sudo apt install google-chrome-stable
   ```

## Usage:

### Test Run (Recommended First):
```bash
python test_scraper.py
```
This will test the first 5 tracks to ensure everything works.

### Production Run:
```bash
python production_scraper.py
```

## Features:

### Anti-Detection Measures:
- Random user agents
- Random delays (2-5 seconds between requests)
- Extended breaks every 100 tracks (60-120 seconds)
- Browser restarts every 300 tracks
- Stealth options to avoid bot detection

### Performance Optimizations:
- Adaptive delay based on success rate
- Automatic retry mechanism (up to 3 attempts)
- Progress saving every 25 tracks
- ETA calculation and progress monitoring
- Memory management with browser restarts

### Time Management:
- Target: 10,000 songs in 6 hours
- Rate: ~0.46 tracks/second (~28 tracks/minute)
- Automatic pace adjustment if behind schedule

### Output Files:
- **spotify_data_progress_X.csv** - Periodic progress saves
- **spotify_data_final.csv** - Final complete dataset
- **failed_tracks.csv** - Tracks that failed after retries
- **scraper_log_TIMESTAMP.log** - Detailed execution log

### Resume Capability:
If the scraper stops, you can resume by:
1. Opening `production_scraper.py`
2. Changing `START_INDEX` to the last completed track number
3. Running the script again

## Expected Output Format:

| track_id | track_name | spotify_url | lyrics | cover_image_url |
|----------|------------|-------------|---------|-----------------|
| 4iV5W9uYEdYUVa79Axb7Rh | Song Name | https://open.spotify.com/track/... | Full lyrics text | https://i.scdn.co/image/... |

## Safety Features:

1. **Rate Limiting**: Prevents overwhelming Spotify's servers
2. **Error Handling**: Graceful handling of network issues
3. **Progress Saving**: No data loss if interrupted
4. **Success Monitoring**: Tracks success rate and adjusts accordingly
5. **Detailed Logging**: Complete audit trail of operations

## Monitoring:

Watch the console output or log file for:
- Progress updates every 25 tracks
- Success rate monitoring
- ETA calculations
- Error notifications
- Break announcements

## Tips:

1. **Run during off-peak hours** for better performance
2. **Monitor the log file** for any issues
3. **Keep the terminal window active** to see progress
4. **Don't interrupt** during extended breaks (they're important for anti-detection)
5. **Check failed_tracks.csv** after completion for any tracks that need manual review

## Troubleshooting:

- **Chrome driver issues**: The script auto-downloads the correct driver
- **Memory issues**: Browser restarts every 300 tracks prevent this
- **Rate limiting**: Extended breaks and random delays handle this
- **Network issues**: Automatic retry mechanism with exponential backoff
