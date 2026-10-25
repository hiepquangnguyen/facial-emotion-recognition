#!/usr/bin/env bash
# build.sh - Render.com build script for Emotion Recognition App

set -o errexit  # Exit on error

echo "🚀 Starting build process for Emotion Recognition App..."

# NOTE: Render's native Python runtime does not allow apt-get (no root access).
# opencv-python-headless ships its own binaries, so no system packages are needed.

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Verify critical packages
echo "✅ Verifying installations..."
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import mediapipe as mp; print(f'MediaPipe: {mp.__version__}')"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/uploads
mkdir -p models
mkdir -p plots
mkdir -p results

# Set permissions
echo "🔐 Setting permissions..."
chmod +x app.py

# Initialize database (if needed)
echo "🗄️ Initializing database..."
python -c "from database import init_db; init_db(); print('Database initialized')"

echo "✅ Build completed successfully!"
echo "🎯 Ready to deploy Emotion Recognition App!" 