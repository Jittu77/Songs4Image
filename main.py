import os
from flask import Flask, render_template, request, jsonify
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

# Import secure configuration
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, FLASK_DEBUG, FLASK_PORT

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# -----------------------------
# Spotify Setup
# -----------------------------
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# -----------------------------
# Scene Detection Setup
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

# -----------------------------
# YOLO Object Detection Setup
# -----------------------------
yolo_model = YOLO("yolov8n.pt")

# -----------------------------
# Helper Functions
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

def get_song_recommendations(query):
    results = sp.search(q=query, type='track', limit=5)
    songs = []
    for item in results['tracks']['items']:
        songs.append({
            'name': item['name'],
            'artist': ", ".join([a['name'] for a in item['artists']]),
            'image': item['album']['images'][0]['url'],
            'url': item['external_urls']['spotify']
        })
    return songs

# -----------------------------
# Flask Routes
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    songs = []
    analysis_result = {}
    if request.method == 'POST':
        file = request.files['image']
        if file:
            # Create uploads directory if it doesn't exist
            os.makedirs('static/uploads', exist_ok=True)
            filepath = os.path.join('static/uploads', file.filename)
            file.save(filepath)

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

            query = f"{mood} {' '.join(scene[:1])}"
            songs = get_song_recommendations(query)

    return render_template('index.html', songs=songs, analysis=analysis_result)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for React frontend"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Create uploads directory if it doesn't exist
        os.makedirs('static/uploads', exist_ok=True)
        filepath = os.path.join('static/uploads', file.filename)
        file.save(filepath)

        # Perform analysis
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

        # Get song recommendations
        query = f"{mood} {' '.join(scene[:1])}"
        songs = get_song_recommendations(query)

        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'songs': songs,
            'image_url': f'/static/uploads/{file.filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)