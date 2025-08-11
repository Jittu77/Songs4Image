# Songs4Image - Spotify Data Scraper

A comprehensive Spotify web scraping project designed to extract track information, cover images, and lyrics from 10,000+ songs. This project features multiple scraping strategies optimized for different use cases and includes anti-detection measures.

## 🎯 Project Overview

This project successfully scraped **10,000 Spotify tracks** with the following data:
- Track IDs and names
- Spotify URLs
- Cover image URLs
- Song lyrics (with full text extraction)

## 🚀 Features

### Multi-Strategy Scraping
- **Fast Scraper**: Optimized for speed (2-3 seconds per track)
- **Production Scraper**: Detailed extraction with comprehensive logging
- **Lyrics Extractor**: Specialized tool for complete lyrics extraction

### Anti-Detection Measures
- Random user agents and delays
- Browser restart cycles
- Headless Chrome optimization
- Rate limiting and adaptive delays

### Utility Tools
- **Keep Alive**: Prevents codespace timeout during long operations
- **Progress Tracking**: Automatic progress saves every 25 tracks
- **Error Handling**: Robust retry mechanisms and failure tracking

## 📁 Project Structure

```
Songs4Image/
├── scrapers/
│   ├── fast_scraper.py          # Speed-optimized scraper (primary)
│   ├── production_scraper.py    # Detailed scraper with full logging
│   ├── spotify_scraper.py       # Base scraper class
│   └── lyrics_extractor.py      # Specialized lyrics extraction
├── utilities/
│   ├── keep_alive.py           # Codespace timeout prevention
│   └── test_scraper.py         # Testing and validation
├── data/
│   ├── track_ids_and_names.csv        # Input dataset (10K tracks)
│   ├── spotify_songs_dataset.csv      # Source dataset
│   ├── spotify_data_progress_175.csv  # Milestone: First 175 tracks
│   └── spotify_data_fast_9000.csv     # Milestone: 9K tracks completed
├── docs/
│   └── README_SCRAPER.md       # Detailed scraper documentation
├── requirements.txt            # Python dependencies
└── main.py                    # Main execution script
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google Chrome browser
- ChromeDriver

### Installation
```bash
# Clone the repository
git clone https://github.com/Jittu77/Songs4Image.git
cd Songs4Image

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### ChromeDriver Setup
```bash
# For Ubuntu/Debian (Codespaces)
sudo apt-get update
sudo apt-get install -y google-chrome-stable
sudo apt-get install -y chromium-chromedriver

# Or download manually
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# Download appropriate version for your Chrome
```

## 🚀 Usage

### Quick Start - Fast Scraper
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the optimized fast scraper
python fast_scraper.py
```

### Production Scraper (Detailed)
```bash
# For comprehensive logging and detailed extraction
python production_scraper.py
```

### Lyrics Extraction
```bash
# Add lyrics to existing CSV files
python lyrics_extractor.py
```

### Keep Codespace Active
```bash
# Prevent timeout during long scraping sessions
python keep_alive.py
```

## 📊 Performance Metrics

### Fast Scraper Performance
- **Speed**: 2-3 seconds per track
- **Rate**: ~14.7 tracks/minute
- **Total Time**: ~10 hours for 10,000 tracks
- **Success Rate**: >95%

### Production Scraper Performance  
- **Speed**: 8-12 seconds per track
- **Rate**: ~5.8 tracks/minute
- **Total Time**: ~29 hours for 10,000 tracks
- **Success Rate**: >98% (more detailed extraction)

## 📈 Data Output

### CSV Structure
Each output file contains:
```csv
track_id,track_name,spotify_url,cover_image,lyrics,processing_time
1J2tfINpEHRhCP8CUS15lE,The Message,https://open.spotify.com/track/1J2tfINpEHRhCP8CUS15lE,https://i.scdn.co/image/...,Some people live for the fortune...,3.05
```

### Key Fields
- **track_id**: Spotify track identifier
- **track_name**: Song title
- **spotify_url**: Direct Spotify link
- **cover_image**: Album cover image URL
- **lyrics**: Complete song lyrics (with "Show more" expansion)
- **processing_time**: Time taken to scrape this track

## 🛡️ Anti-Detection Features

- **Random User Agents**: Rotates between different browser signatures
- **Adaptive Delays**: Dynamic timing based on success rates
- **Browser Restarts**: Periodic driver restarts to avoid memory issues
- **Headless Operation**: Runs without visible browser window
- **Progress Checkpoints**: Automatic saves prevent data loss

## 📋 Dataset Information

### Source Dataset
- **Original**: 170,000+ tracks from Kaggle Spotify dataset
- **Processed**: 10,000 unique track IDs
- **Format**: Clean track IDs (removed "spotify:track:" prefix)

### Output Datasets
- **spotify_data_progress_175.csv**: First 175 tracks (detailed)
- **spotify_data_fast_9000.csv**: 9,000 tracks (fast scraper)
- **Final output**: Complete 10,000 track dataset

## ⚙️ Configuration

### Environment Variables
```bash
# Optional: Set custom delays
export SCRAPER_MIN_DELAY=1
export SCRAPER_MAX_DELAY=3

# Optional: Set batch size
export PROGRESS_SAVE_INTERVAL=25
```

### Scraper Options
- Modify delays in `fast_scraper.py` line 89-92
- Adjust browser restart frequency (default: every 500 tracks)
- Configure timeout settings in driver setup

## 🔧 Troubleshooting

### Common Issues

**ChromeDriver not found**
```bash
# Check ChromeDriver location
which chromedriver
# Should return: /usr/local/bin/chromedriver
```

**Memory issues**
- Browser restarts automatically every 500 tracks
- Increase restart frequency for low-memory environments

**Rate limiting**
- Scraper includes adaptive delays
- Modify delay ranges in scraper configuration

**Codespace timeout**
- Use `keep_alive.py` for long scraping sessions
- Default timeout: 30 minutes without activity

## 📝 Logging

All scrapers include comprehensive logging:
- **INFO**: Progress updates and milestones
- **WARNING**: Retry attempts and minor issues
- **ERROR**: Failed extractions and critical errors

Log files are automatically generated with timestamps.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect Spotify's terms of service and rate limits.

## 🎯 Use Cases

- **Music Analysis**: Large-scale song data analysis
- **Machine Learning**: Training datasets for music recommendation
- **Research**: Academic research on music trends
- **Development**: Building music-related applications

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review `README_SCRAPER.md` for detailed documentation
3. Open an issue on GitHub

---

**Note**: This scraper is designed for educational and research purposes. Always comply with website terms of service and implement appropriate rate limiting.