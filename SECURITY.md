# Security Configuration Guide

## 🔒 Security Setup for Songs4Image

### Quick Setup
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual API credentials:
   ```bash
   # Required for AI recommendations (main1.py)
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   
   # Required for music recommendations (both main.py and main1.py)
   SPOTIFY_CLIENT_ID=your_actual_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_actual_spotify_client_secret
   ```

### Getting API Credentials

#### Spotify API
1. Visit https://developer.spotify.com/
2. Log in with your Spotify account
3. Create a new app
4. Copy the Client ID and Client Secret to your `.env` file

#### Gemini AI API  
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the API key to your `.env` file

### Security Best Practices
- ✅ Never commit `.env` files to version control
- ✅ Use different API keys for development and production
- ✅ Regularly rotate your API keys
- ✅ Limit API key permissions to required scopes
- ✅ Monitor API usage for unusual activity

### Troubleshooting
If you see credential-related errors:
1. Ensure `.env` file exists in the project root
2. Check that all required variables are set in `.env`
3. Verify API keys are valid and active
4. Restart the application after changing credentials

### Environment Variables Reference
- `GEMINI_API_KEY`: Google Gemini AI API key (required for main1.py)
- `SPOTIFY_CLIENT_ID`: Spotify app client ID (required for both apps)
- `SPOTIFY_CLIENT_SECRET`: Spotify app client secret (required for both apps)
- `FLASK_DEBUG`: Enable/disable debug mode (optional, default: False)
- `FLASK_PORT`: Port to run Flask app (optional, default: 8000)