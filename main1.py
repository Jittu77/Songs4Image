import os
import io
import asyncio
import json
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import torch
from torchvision import models, transforms
from deepface import DeepFace
from colorthief import ColorThief
from ultralytics import YOLO
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib
from typing import List
import requests
try:
    from youtubesearchpython import VideosSearch
except ImportError:
    try:
        from youtube_search import YoutubeSearch
        VideosSearch = None
    except ImportError:
        VideosSearch = None
        YoutubeSearch = None

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("MoviePy not available. Video creation features will be disabled.")

from pydantic import BaseModel, Field
import google.generativeai as genai
import tempfile

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("yt-dlp not available. Audio download features will be disabled.")

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# -----------------------------
# API Keys Setup
# -----------------------------
GEMINI_API_KEY = "AIzaSyAZJZPbnEddSiRCbnzp_DQRFkSDK-GXF6Q"
os.environ['GOOGLE_API_KEY'] = GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

# -----------------------------
# Spotify Setup
# -----------------------------
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id='1f61472fe65f48a29febcfc9fcbe814d',
    client_secret='e447472fc69b477da6145176f5ee3e05'
))

# -----------------------------
# Gemini Models Setup
# -----------------------------
class Song(BaseModel):
    song: str = Field(description="Name of the song")
    singer: str = Field(description="Singer or artist of the song")

class MusicList(BaseModel):
    songs: List[Song] = Field(description="List of recommended songs with their singers")

llm = genai.GenerativeModel("gemini-2.0-flash-exp")

# -----------------------------
# Scene Detection Setup (Same as main.py)
# -----------------------------
categories_url = 'https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt'
categories_file = 'categories_places365.txt'
if not os.path.exists(categories_file):
    urllib.request.urlretrieve(categories_url, categories_file)
with open(categories_file) as f:
    classes = [line.strip().split(' ')[0][3:] for line in f]

model = models.resnet18(num_classes=365)
model_file = 'resnet18_places365.pth.tar'
if not os.path.exists(model_file):
    model_url = 'http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar'
    urllib.request.urlretrieve(model_url, model_file)
checkpoint = torch.load(model_file, map_location=torch.device('cpu'))
state_dict = {str.replace(k,'module.',''): v for k,v in checkpoint['state_dict'].items()}
model.load_state_dict(state_dict)
model.eval()

scene_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

yolo_model = YOLO("yolov8n.pt")

# -----------------------------
# Helper Functions (Same as main.py)
# -----------------------------
def predict_scene(image_path):
    img = Image.open(image_path).convert('RGB')
    input_img = scene_transform(img).unsqueeze(0)
    with torch.no_grad():
        output = model(input_img)
        _, pred = output.topk(3)
        scene_labels = [classes[idx] for idx in pred[0]]
    return scene_labels

def detect_objects(image_path):
    results = yolo_model(image_path)
    labels = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            labels.append(r.names[cls_id])
    return list(set(labels))

def analyze_emotion(image_path):
    try:
        analysis = DeepFace.analyze(img_path=image_path, actions=["emotion"], enforce_detection=False)
        if isinstance(analysis, list):
            return analysis[0]['dominant_emotion']
        return analysis['dominant_emotion']
    except:
        return "neutral"

def extract_dominant_color(image_path):
    color_thief = ColorThief(image_path)
    return color_thief.get_color(quality=1)

# -----------------------------
# Gemini AI Functions
# -----------------------------
async def get_gemini_song_recommendations(image_path, scene, objects, mood, color):
    """Get song recommendations from Gemini AI based on image analysis"""
    
    prompt = f"""
    You are a psychological Indian music recommender.  
    Analyze the given image and the following detected attributes to recommend suitable songs.
    
    Detected Attributes:
    - Scene: {', '.join(scene)}
    - Objects: {', '.join(objects)}
    - Mood/Emotion: {mood}
    - Dominant Color: RGB{color}
    
    Based on this analysis, recommend a list of suitable songs.  

    Guidelines:
    - Focus mainly on **Indian music** (Bollywood, classical, indie, devotional, regional).  
    - You may include **global tracks** if they strongly fit the mood.  
    - Consider the scene, objects, and mood to create a cohesive recommendation.
    - Output must be in JSON format that matches this schema:
        {{
          "songs": [
            {{"song": "Song Name", "singer": "Singer Name"}},
            ...
          ]
        }}
    - Provide 8-10 song recommendations.
    - Do not include explanations or extra commentary.
    """

    try:
        img = Image.open(image_path)
        response = llm.generate_content(
            [prompt, img],
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.7
            }
        )

        try:
            raw_text = response.text
        except AttributeError:
            raw_text = response.candidates[0].content.parts[0].text

        result = json.loads(raw_text)
        return result.get('songs', [])
    
    except Exception as e:
        print(f"Error getting Gemini recommendations: {e}")
        return []

# -----------------------------
# YouTube and Spotify Functions
# -----------------------------
def search_youtube_songs(songs):
    """Search for songs on YouTube and return video links"""
    youtube_results = []
    
    for song in songs:
        try:
            query = f"{song['song']} {song['singer']}"
            
            if VideosSearch:
                # Using youtubesearchpython
                videos_search = VideosSearch(query, limit=1)
                results = videos_search.result()['result']
                
                if results:
                    video = results[0]
                    youtube_results.append({
                        'song': song['song'],
                        'singer': song['singer'],
                        'youtube_id': video['id'],
                        'youtube_url': video['link'],
                        'thumbnail': video['thumbnails'][0]['url'] if video['thumbnails'] else '',
                        'duration': video.get('duration', 'Unknown')
                    })
            elif YoutubeSearch:
                # Using youtube-search-python
                results = YoutubeSearch(query, max_results=1).to_dict()
                
                if results:
                    video = results[0]
                    youtube_results.append({
                        'song': song['song'],
                        'singer': song['singer'],
                        'youtube_id': video['id'],
                        'youtube_url': f"https://www.youtube.com/watch?v={video['id']}",
                        'thumbnail': video['thumbnails'][0] if video['thumbnails'] else '',
                        'duration': video.get('duration', 'Unknown')
                    })
            else:
                # Fallback: create a search URL
                search_query = query.replace(' ', '+')
                youtube_results.append({
                    'song': song['song'],
                    'singer': song['singer'],
                    'youtube_id': 'unknown',
                    'youtube_url': f"https://www.youtube.com/results?search_query={search_query}",
                    'thumbnail': '',
                    'duration': 'Unknown'
                })
                
        except Exception as e:
            print(f"Error searching YouTube for {song['song']}: {e}")
            continue
    
    return youtube_results

def search_spotify_songs(songs):
    """Search for songs on Spotify and return details"""
    spotify_results = []
    
    for song in songs:
        try:
            query = f"track:{song['song']} artist:{song['singer']}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                spotify_results.append({
                    'song': song['song'],
                    'singer': song['singer'],
                    'name': track['name'],
                    'artist': ", ".join([a['name'] for a in track['artists']]),
                    'image': track['album']['images'][0]['url'] if track['album']['images'] else '',
                    'url': track['external_urls']['spotify'],
                    'preview_url': track.get('preview_url')
                })
        except Exception as e:
            print(f"Error searching Spotify for {song['song']}: {e}")
            continue
    
    return spotify_results

def download_youtube_audio(youtube_url, output_path):
    """Download audio from YouTube video"""
    if not YT_DLP_AVAILABLE:
        print("yt-dlp not available for audio download")
        return False
        
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return True
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return False

def create_video_with_music(image_path, audio_path, output_path, duration=30):
    """Create a video combining image and audio"""
    if not MOVIEPY_AVAILABLE:
        print("MoviePy not available for video creation")
        return False
        
    try:
        # Create image clip
        image_clip = mp.ImageClip(image_path, duration=duration)
        
        # Load audio clip
        audio_clip = mp.AudioFileClip(audio_path)
        
        # Trim audio to match duration
        if audio_clip.duration > duration:
            audio_clip = audio_clip.subclip(0, duration)
        
        # Combine image and audio
        final_video = image_clip.set_audio(audio_clip)
        final_video.write_videofile(output_path, fps=1, codec='libx264', audio_codec='aac')
        
        # Close clips to free memory
        image_clip.close()
        audio_clip.close()
        final_video.close()
        
        return True
    except Exception as e:
        print(f"Error creating video: {e}")
        return False

# -----------------------------
# Flask Routes
# -----------------------------
@app.route('/')
def home():
    return render_template('advanced_index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save uploaded file
        os.makedirs('static/uploads', exist_ok=True)
        filepath = os.path.join('static/uploads', file.filename)
        file.save(filepath)

        # Basic analysis (same as main.py)
        scene = predict_scene(filepath)
        objects = detect_objects(filepath)
        mood = analyze_emotion(filepath)
        color = extract_dominant_color(filepath)

        analysis_result = {
            'scene': scene,
            'objects': objects,
            'mood': mood,
            'color': color
        }

        # Get recommendations from Gemini AI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        gemini_songs = loop.run_until_complete(
            get_gemini_song_recommendations(filepath, scene, objects, mood, color)
        )

        # Search YouTube and Spotify
        youtube_songs = search_youtube_songs(gemini_songs)
        spotify_songs = search_spotify_songs(gemini_songs)

        return render_template('advanced_index.html', 
                             analysis=analysis_result,
                             youtube_songs=youtube_songs,
                             spotify_songs=spotify_songs,
                             image_filename=file.filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-video', methods=['POST'])
def create_video_api():
    """API endpoint to create and download video with image and selected song"""
    try:
        data = request.json
        image_filename = data.get('image_filename')
        youtube_url = data.get('youtube_url')
        song_name = data.get('song_name', 'video')
        
        if not image_filename or not youtube_url:
            return jsonify({'error': 'Missing required parameters'}), 400

        image_path = os.path.join('static/uploads', image_filename)
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image file not found'}), 404

        # Create temp directory for audio
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, 'audio.mp3')
        
        # Download audio from YouTube
        if not download_youtube_audio(youtube_url, audio_path):
            return jsonify({'error': 'Failed to download audio'}), 500

        # Create output video
        os.makedirs('static/videos', exist_ok=True)
        output_filename = f"output_{song_name.replace(' ', '_')}.mp4"
        output_path = os.path.join('static/videos', output_filename)
        
        if create_video_with_music(image_path, audio_path, output_path):
            return jsonify({
                'success': True, 
                'video_url': f'/download-video/{output_filename}',
                'video_path': output_path
            })
        else:
            return jsonify({'error': 'Failed to create video'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-video/<filename>')
def download_video(filename):
    """Download generated video"""
    try:
        video_path = os.path.join('static/videos', filename)
        if os.path.exists(video_path):
            return send_file(video_path, as_attachment=True)
        else:
            return jsonify({'error': 'Video file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/crop-audio', methods=['POST'])
def crop_audio():
    """API endpoint to crop audio and create custom video"""
    try:
        data = request.json
        youtube_url = data.get('youtube_url')
        start_time = data.get('start_time', 0)
        end_time = data.get('end_time', 30)
        image_filename = data.get('image_filename')
        
        if not all([youtube_url, image_filename]):
            return jsonify({'error': 'Missing required parameters'}), 400

        image_path = os.path.join('static/uploads', image_filename)
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, 'audio.mp3')
        
        # Download and crop audio
        if download_youtube_audio(youtube_url, audio_path):
            # Crop audio using moviepy
            if MOVIEPY_AVAILABLE:
                audio_clip = mp.AudioFileClip(audio_path)
                cropped_audio = audio_clip.subclip(start_time, end_time)
                
                cropped_path = os.path.join(temp_dir, 'cropped_audio.mp3')
                cropped_audio.write_audiofile(cropped_path)
                
                # Create video with cropped audio
                output_filename = f"cropped_video_{start_time}_{end_time}.mp4"
                output_path = os.path.join('static/videos', output_filename)
                
                if create_video_with_music(image_path, cropped_path, output_path, end_time - start_time):
                    return jsonify({
                        'success': True,
                        'video_url': f'/download-video/{output_filename}'
                    })
            else:
                return jsonify({'error': 'MoviePy not available for audio processing'}), 500
        
        return jsonify({'error': 'Failed to process audio'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/videos', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, port=8001)
