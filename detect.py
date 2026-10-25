import cv2
import numpy as np
try:
    import mediapipe as mp
    USE_MEDIAPIPE = True
except ImportError:
    print("MediaPipe not found, falling back to OpenCV's Haar Cascade")
    USE_MEDIAPIPE = False
from model import load_model
from utils import draw_emotion, get_emotion_color

import argparse

# Thêm phần phân tích tham số khi chạy
parser = argparse.ArgumentParser()
parser.add_argument('--use_haar', action='store_true', help='Chỉ dùng Haar Cascade dù MediaPipe có sẵn')
args = parser.parse_args()

# Design: nếu dùng --use_haar, ép USE_MEDIAPIPE=False
USE_MEDIAPIPE = not args.use_haar and USE_MEDIAPIPE

class EmotionDetector:
    def __init__(self, model_path):
        # Load model
        self.model = load_model(model_path)
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        if USE_MEDIAPIPE:
            # Initialize MediaPipe Face Detection
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                min_detection_confidence=0.5
            )
        else:
            # Initialize Haar Cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize counters
        self.happy_count = 0
        self.emotion_counts = {emotion: 0 for emotion in self.emotions}
    
    def preprocess_face(self, face_img):
        """Preprocess face image for model input"""
        if len(face_img.shape) == 3:  # If color image
            face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_img = cv2.resize(face_img, (48, 48))
        face_img = face_img.astype('float32') / 255.0
        face_img = np.expand_dims(face_img, axis=[0, -1])
        return face_img
    
    def detect_emotion(self, frame):
        """Detect emotions in the frame"""
        if USE_MEDIAPIPE:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)
            
            if results.detections:
                for detection in results.detections:
                    # Get face bounding box
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    # Process detected face
                    self._process_face(frame, x, y, width, height)
        else:
            # Use Haar Cascade
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            for (x, y, width, height) in faces:
                # Process detected face
                self._process_face(frame, x, y, width, height)
        
        # Display emotion counts
        y_offset = 30
        for emotion, count in self.emotion_counts.items():
            text = f"{emotion}: {count}"
            cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, get_emotion_color(emotion), 2)
            y_offset += 25
        
        return frame
    
    def _process_face(self, frame, x, y, width, height):
        """Process a detected face"""
        # Ensure coordinates are within frame bounds
        h, w = frame.shape[:2]
        x = max(0, x)
        y = max(0, y)
        width = min(width, w - x)
        height = min(height, h - y)
        
        # Extract and preprocess face
        face_img = frame[y:y+height, x:x+width]
        if face_img.size == 0:
            return
            
        face_processed = self.preprocess_face(face_img)
        
        # Predict emotion
        predictions = self.model.predict(face_processed, verbose=0)[0]
        emotion_idx = np.argmax(predictions)
        emotion = self.emotions[emotion_idx]
        confidence = predictions[emotion_idx]
        
        # Update counters
        self.emotion_counts[emotion] += 1
        if emotion == 'happy':
            self.happy_count += 1
        
        # Draw results
        color = get_emotion_color(emotion)
        cv2.rectangle(frame, (x, y), (x+width, y+height), color, 2)
        label = f"{emotion}: {confidence:.2f}"
        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    def reset_counts(self):
        """Reset emotion counters"""
        self.happy_count = 0
        self.emotion_counts = {emotion: 0 for emotion in self.emotions}

def try_camera_index(index, backend=None):
    """Try to open and test a camera with given index and backend"""
    if backend:
        cap = cv2.VideoCapture(index, backend)
    else:
        cap = cv2.VideoCapture(index)
        
    if not cap.isOpened():
        return None
        
    # Try to read a frame
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0:
        cap.release()
        return None
        
    return cap

def main():
    print("Initializing emotion detector...")
    # Initialize detector with CNN model
    detector = EmotionDetector("models/emotion_model_cnn.h5")
    
    print("Testing available cameras...")
    cap = None
    backends = [None, cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    # Try different camera indices with different backends
    for index in range(2):  # Try first two indices
        print(f"\nTrying camera index {index}:")
        for backend in backends:
            backend_name = str(backend) if backend else "default"
            print(f"  Testing with backend {backend_name}...")
            
            cap = try_camera_index(index, backend)
            if cap is not None:
                print(f"Success! Found working camera with index {index} and backend {backend_name}")
                break
        if cap is not None:
            break
    
    if cap is None:
        print("Error: Could not find any working camera")
        return
    
    # Set camera properties
    print("\nConfiguring camera...")
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Original resolution: {original_width}x{original_height}")
    
    # Try to set resolution only if it's different
    target_width, target_height = 640, 480
    if original_width != target_width or original_height != target_height:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, target_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_height)
        
        # Verify if resolution was set
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Actual resolution: {actual_width}x{actual_height}")
    
    # Create window
    win_name = 'Emotion Detection (Press Q to quit, R to reset counters)'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 900, 700)
    
    print("\nStarting detection loop... Press 'Q' to quit")
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("Warning: Failed to read frame, retrying...")
            continue
        
        # Print frame info occasionally
        if cv2.getTickCount() % (cv2.getTickFrequency() * 5) == 0:  # Every ~5 seconds
            print(f"Frame shape: {frame.shape}, dtype: {frame.dtype}")
        
        # Flip the frame horizontally for selfie view
        frame = cv2.flip(frame, 1)
        
        try:
            # Detect emotions and show processed frame
            processed_frame = detector.detect_emotion(frame.copy())
            if processed_frame is not None:
                cv2.imshow(win_name, processed_frame)
            
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting...")
            break
        elif key == ord('r'):
            print("Resetting emotion counters...")
            detector.reset_counts()
    
    print("Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()