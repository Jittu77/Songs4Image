# Songs4Image - AI-Powered Music Recommendation System

An intelligent music recommendation system that analyzes images to suggest matching songs. This project combines computer vision, emotion analysis, and music recommendation algorithms to bridge the gap between visual content and auditory experiences. Additionally includes a comprehensive Spotify data scraping toolkit for building music datasets.

## 🎯 Project Overview

### 🎵 AI Music Recommendation Web Application
This project features an intelligent Flask web application that analyzes uploaded images to recommend matching music:
- **Image Analysis**: Scene detection, object recognition, emotion analysis, and color extraction
- **Music Matching**: AI-powered song recommendations based on visual characteristics
- **Modern Web Interface**: Responsive design with drag-and-drop image upload
- **Real-time Processing**: Instant analysis and recommendations
- **API Support**: RESTful API for integration with other applications

### 📊 Spotify Data Scraping Toolkit
Successfully scraped **10,000 Spotify tracks** with comprehensive data extraction:
- Track IDs and names
- Spotify URLs  
- Cover image URLs
- Song lyrics (with full text extraction)

## 🚀 Features

### 🎵 AI Music Recommendation System
- **Advanced Image Analysis**:
  - Scene detection using ResNet18 with Places365 dataset
  - Object detection using YOLOv8
  - Emotion analysis using DeepFace
  - Dominant color extraction using ColorThief
- **Intelligent Music Matching**:
  - Spotify API integration for real-time music recommendations
  - Context-aware song suggestions based on visual analysis
  - Support for multiple music moods and genres
- **Modern Web Interface**:
  - Responsive HTML5 design with drag-and-drop upload
  - Real-time image preview and analysis results
  - Beautiful gradient UI with FontAwesome icons
- **Dual API Support**:
  - Web interface route for direct user interaction
  - RESTful API endpoint for frontend integration

### 📊 Spotify Data Scraping Toolkit Multi-Strategy Scraping
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
├── 🎵 Web Application/
│   ├── main.py                      # Flask app with image analysis & music recommendation (formerly main1.py)
│   ├── templates/
│   │   ├── index.html               # Modern web interface with image upload
│   │   └── advanced_index.html      # Advanced template variant
│   └── static/
│       ├── uploads/                 # User uploaded images storage
│       └── *.jpg, *.jpeg            # Sample/test images
├── 📊 scrapper/                     # Data Scraping Tools
│   ├── fast_scraper.py              # Speed-optimized scraper (primary)
│   ├── production_scraper.py        # Detailed scraper with full logging
│   ├── spotify_scraper.py           # Base scraper class
│   ├── lyrics_extractor.py          # Specialized lyrics extraction
│   └── test_scraper.py              # Testing and validation
├── 📁 datasets/                     # Data & Analysis
│   ├── track_ids_and_names.csv      # Input dataset (10K tracks)
│   ├── spotify_songs_dataset.csv    # Source dataset
│   ├── spotify_data_progress_175.csv # Milestone: First 175 tracks
│   ├── spotify_data_fast_9000.csv   # Milestone: 9K tracks completed
│   └── dataset.csv                  # Original dataset
├── 🔧 Utilities/
│   └── keep_alive.py                # Codespace timeout prevention
├── 📓 Analysis Notebooks/
│   ├── ML_Analysis.ipynb            # Machine learning analysis and clustering
│   └── project_report.ipynb         # Comprehensive project documentation
├── 📚 Documentation/
│   └── README_SCRAPER.md            # Detailed scraper documentation
├── requirements.txt                 # Python dependencies
└── .gitignore                      # Git ignore configuration
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google Chrome browser (for scraping features)
- Spotify API credentials (for music recommendations)

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

# Additional dependencies for web application
pip install flask torch spotipy deepface colorthief ultralytics flask-cors Pillow torchvision
```

### Spotify API Setup (Required for Music Recommendations)
1. Create a Spotify Developer account at https://developer.spotify.com/
2. Create a new app and get your Client ID and Client Secret
3. Update the credentials in `main.py`:
```python
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id='your_client_id_here',
    client_secret='your_client_secret_here'
))
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

### 🎵 AI Music Recommendation Web App

#### Quick Start
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the web application (enhanced version with Gemini AI integration)
python main.py
```
The application will be available at `http://localhost:8001`

#### Features:
- **Web Interface**: Upload images via drag-and-drop or file browser
- **Real-time Analysis**: Instant scene detection, object recognition, and emotion analysis
- **Music Recommendations**: AI-generated song suggestions based on image characteristics
- **API Access**: Use `/api/analyze` endpoint for programmatic access

#### API Usage Example:
```bash
curl -X POST -F "image=@your_image.jpg" http://localhost:8000/api/analyze
```

### 📊 Spotify Data Scraping

#### Quick Start - Fast Scraper
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the optimized fast scraper
cd scrapper
python fast_scraper.py
```

### Production Scraper (Detailed)
```bash
# For comprehensive logging and detailed extraction
cd scrapper
python production_scraper.py
```

### Lyrics Extraction
```bash
# Add lyrics to existing CSV files
cd scrapper
python lyrics_extractor.py
```

### Keep Codespace Active
```bash
# Prevent timeout during long scraping sessions
python keep_alive.py
```

## 🤖 Technical Implementation

### Image Analysis Pipeline
1. **Scene Detection**: Uses ResNet18 trained on Places365 dataset to identify scene types (beach, forest, city, etc.)
2. **Object Recognition**: Employs YOLOv8 for real-time object detection and labeling
3. **Emotion Analysis**: Leverages DeepFace library for facial emotion recognition in images
4. **Color Analysis**: Extracts dominant colors using ColorThief algorithm

### Music Recommendation Algorithm
1. **Context Generation**: Combines scene, emotion, and object data to create search context
2. **Spotify Integration**: Queries Spotify API with generated context for relevant tracks
3. **Result Filtering**: Returns curated list of songs with metadata (artist, album art, Spotify URL)
4. **Real-time Processing**: Optimized for fast response times under 3 seconds

### Web Application Architecture
- **Backend**: Flask framework with CORS support for API access
- **Frontend**: Modern HTML5 with responsive CSS and JavaScript
- **File Handling**: Secure image upload with validation and storage
- **API Design**: RESTful endpoints for both web and programmatic access

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
All datasets are stored in the `datasets/` folder. Each output file contains:
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
All datasets are stored in the `datasets/` folder:
- **track_ids_and_names.csv**: Input dataset with 10,000 track IDs
- **spotify_data_progress_175.csv**: First 175 tracks (detailed)
- **spotify_data_fast_9000.csv**: 9,000 tracks (fast scraper)
- **spotify_songs_dataset.csv**: Source dataset
- **dataset.csv**: Original dataset
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

### 🎵 Music Recommendation System
- **Social Media Integration**: Automatically suggest music for photo posts
- **Content Creation**: Find background music for videos based on scenes
- **Personal Music Discovery**: Explore new songs that match your visual preferences
- **Event Planning**: Generate playlists based on venue/event photos
- **Mood-based Recommendations**: Get music suggestions that match your current visual environment

### 📊 Data Research & Analysis

- **Music Analysis**: Large-scale song data analysis
- **Machine Learning**: Training datasets for music recommendation
- **Research**: Academic research on music trends
- **Development**: Building music-related applications

## 🚀 Quick Demo

### Web Application Demo
1. **Start the Application**:
   ```bash
   python main.py
   ```
   Navigate to `http://localhost:8000`

   > **Note**: If you encounter dependency issues with model downloads, use the demo version:
   > ```bash
   > python demo_main.py  # Runs with mock AI analysis for testing
   > ```

2. **Upload an Image**: 
   - Drag and drop any image file, or click to browse
   - Supported formats: JPG, PNG, GIF (up to 10MB)

3. **View Results**:
   - Scene detection (e.g., "beach", "forest", "urban")
   - Objects detected (e.g., "person", "car", "tree")
   - Emotion analysis (e.g., "happy", "calm", "energetic")
   - Dominant color extraction
   - Curated music recommendations from Spotify

### API Demo
```bash
# Test the API endpoint
curl -X POST -F "image=@sample_image.jpg" http://localhost:8000/api/analyze

# Example response:
{
  "success": true,
  "analysis": {
    "scene": ["beach", "outdoor", "water"],
    "objects": ["person", "surfboard"],
    "mood": "happy",
    "color": [135, 206, 235]
  },
  "songs": [
    {
      "name": "Good Vibrations",
      "artist": "The Beach Boys",
      "image": "https://i.scdn.co/image/...",
      "url": "https://open.spotify.com/track/..."
    }
  ]
}
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review `README_SCRAPER.md` for detailed documentation
3. Open an issue on GitHub

---

**Note**: This scraper is designed for educational and research purposes. Always comply with website terms of service and implement appropriate rate limiting.