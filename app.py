import os
import base64
import binascii
import json
import logging
from datetime import datetime
from functools import wraps

import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

from database import init_db, add_user, verify_user, log_emotion, get_user_emotion_history

# Load environment variables from a local .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# Secret key must be stable across restarts and shared by all gunicorn workers,
# otherwise sessions are randomly invalidated. Set SECRET_KEY in the environment.
_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    logger.warning("SECRET_KEY is not set - using a random key (sessions will not survive restarts).")
    _secret_key = os.urandom(24)
app.secret_key = _secret_key

# Limit request size (base64 webcam frames are well below this)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Load your trained model
MODEL_CANDIDATES = [
    os.path.join(BASE_DIR, 'models', 'emotion_model_cnn.h5'),
    os.path.join(BASE_DIR, 'models', 'emotion_model.h5'),
]
model = None
for _model_path in MODEL_CANDIDATES:
    if not os.path.exists(_model_path):
        continue
    try:
        model = tf.keras.models.load_model(_model_path, compile=False)
        logger.info("✅ Model loaded successfully from %s", _model_path)
        break
    except Exception as e:  # noqa: BLE001 - try next candidate
        logger.error("❌ Failed to load model %s: %s", _model_path, e)
if model is None:
    logger.error("❌ No model found! Please train the model first.")

# Initialize face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    logger.error("❌ Failed to load Haar cascade for face detection.")

# Ensure upload folder exists
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db()

# Emotion labels and colors
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
EMOTION_COLORS = {
    'angry': '#FF6B6B',
    'disgust': '#4ECDC4',
    'fear': '#45B7D1',
    'happy': '#FFA07A',
    'sad': '#98D8C8',
    'surprise': '#F7DC6F',
    'neutral': '#BB8FCE'
}


def _load_json(path, default=None):
    """Read a JSON file, returning `default` if it is missing or invalid."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default if default is not None else {}


def _count_emotions(history):
    """Count occurrences of each emotion in a user's history records."""
    emotion_counts = {}
    for record in history:
        emotion = record[1]  # emotion column
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    return emotion_counts


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this feature.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('detect'))
    return redirect(url_for('login'))


@app.route('/health')
def health():
    """Lightweight health check endpoint for hosting platforms"""
    return jsonify({'status': 'ok', 'model_loaded': model is not None}), 200


@app.route('/detect')
@login_required
def detect():
    """Main emotion detection page - login required"""
    username = session.get('username', 'User')
    return render_template('index.html',
                           emotions=EMOTIONS,
                           colors=EMOTION_COLORS,
                           username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('detect'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user_id = verify_user(username, password) if username and password else None
        if user_id:
            session.clear()
            session['user_id'] = user_id
            session['username'] = username
            flash('Login successful! Welcome back!', 'success')
            return redirect(url_for('detect'))
        flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('detect'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
        elif not email or '@' not in email:
            flash('Please enter a valid email address.', 'error')
        elif add_user(username, password, email):
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists. Please try different credentials.', 'error')
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye {username}! You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    username = session.get('username', 'User')
    history = get_user_emotion_history(user_id)

    # Calculate emotion statistics
    emotion_counts = _count_emotions(history)
    total_detections = len(history)
    emotion_stats = {
        emotion: {
            'count': count,
            'percentage': round((count / total_detections) * 100, 1)
        }
        for emotion, count in emotion_counts.items()
    } if total_detections else {}

    return render_template('dashboard.html',
                           username=username,
                           history=history,
                           emotion_stats=emotion_stats,
                           total_detections=total_detections,
                           colors=EMOTION_COLORS)


@app.route('/analyze', methods=['POST'])
@login_required
def analyze_image():
    """Analyze emotion from uploaded image - login required"""
    if model is None:
        return jsonify({'error': 'Model not loaded. Please contact administrator.'}), 500

    # Get image data from request
    payload = request.get_json(silent=True) or {}
    image_data = payload.get('image')
    if not image_data or not isinstance(image_data, str):
        return jsonify({'error': 'No image data provided'}), 400

    # Base64 image from webcam (accepts both data URLs and raw base64)
    if ',' in image_data:
        image_data = image_data.split(',', 1)[1]
    try:
        image_bytes = base64.b64decode(image_data)
    except (binascii.Error, ValueError):
        return jsonify({'error': 'Invalid image encoding'}), 400

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Failed to decode image'}), 400

    try:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            return jsonify({'error': 'No face detected. Please ensure your face is clearly visible and well-lit.'}), 400

        # Process the largest face
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face

        # Extract and preprocess face region
        face_img = gray[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (48, 48))
        face_img = face_img.astype('float32') / 255.0
        face_img = np.expand_dims(face_img, axis=[0, -1])

        # Get prediction
        prediction = model.predict(face_img, verbose=0)
        predicted_idx = int(np.argmax(prediction[0]))
        predicted_emotion = EMOTIONS[predicted_idx]
        confidence = float(prediction[0][predicted_idx])

        # Log the emotion to user's history
        log_emotion(session['user_id'], predicted_emotion, confidence)

        # Prepare all emotion probabilities
        emotion_probabilities = [
            {
                'emotion': emotion,
                'probability': float(prediction[0][i]),
                'percentage': round(float(prediction[0][i]) * 100, 1),
                'color': EMOTION_COLORS[emotion]
            }
            for i, emotion in enumerate(EMOTIONS)
        ]

        # Sort by probability (highest first)
        emotion_probabilities.sort(key=lambda item: item['probability'], reverse=True)

        result = {
            'success': True,
            'predicted_emotion': predicted_emotion,
            'confidence': confidence,
            'confidence_percentage': round(confidence * 100, 1),
            'emotion_probabilities': emotion_probabilities,
            'face_coordinates': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
            'color': EMOTION_COLORS[predicted_emotion],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': session.get('username', 'User')
        }

        return jsonify(result)

    except Exception:  # noqa: BLE001 - log full traceback, return generic message
        app.logger.exception("Error in analyze_image")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500


@app.route('/api/model-info')
@login_required
def model_info():
    """Get information about the loaded model - login required"""
    if model is None:
        return jsonify({'error': 'No model loaded'}), 500

    # Load model stats
    try:
        with open(os.path.join(BASE_DIR, 'models', 'classification_report_cnn.txt'), 'r', encoding='utf-8') as f:
            report_text = f.read()
    except OSError:
        report_text = "Model report not available"

    dataset_info = _load_json(os.path.join(BASE_DIR, 'results', 'dataset_info.json'))
    cnn_results = _load_json(os.path.join(BASE_DIR, 'models', 'cnn_results.json'))

    test_accuracy = cnn_results.get('test_accuracy')
    accuracy = f"{test_accuracy * 100:.2f}%" if isinstance(test_accuracy, (int, float)) else 'N/A'

    return jsonify({
        'model_loaded': True,
        'emotions': EMOTIONS,
        'total_parameters': int(model.count_params()),
        'dataset_info': dataset_info or cnn_results.get('dataset_info', {}),
        'accuracy': accuracy,
        'report': report_text,
        'user': session.get('username', 'User')
    })


@app.route('/api/user-stats')
@login_required
def user_stats():
    """Get current user's emotion statistics"""
    user_id = session['user_id']
    history = get_user_emotion_history(user_id)

    if not history:
        return jsonify({'total': 0, 'emotions': {}})

    return jsonify({
        'total': len(history),
        'emotions': _count_emotions(history),
        'user': session.get('username', 'User')
    })


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify({'error': 'Image is too large.'}), 413


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting Emotion Recognition Web App...")
    print("🔐 Login required for all features")
    print("📊 Model status:", "✅ Loaded" if model is not None else "❌ Not loaded")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)