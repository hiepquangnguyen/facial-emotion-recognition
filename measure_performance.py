import tensorflow as tf
import time
import numpy as np
from tensorflow.keras.models import load_model
import cv2
import psutil
import os

def measure_inference_speed(model_path, num_runs=100, input_shape=(48, 48, 1)):
    """
    Đo tốc độ suy luận của mô hình
    """
    print("Loading model...")
    model = load_model(model_path)
    
    # Tạo dữ liệu giả lập
    dummy_input = np.random.random((1, *input_shape))
    
    # Warm-up
    print("Warming up...")
    for _ in range(10):
        model.predict(dummy_input, verbose=0)
    
    # Đo thời gian
    print(f"Measuring inference speed over {num_runs} runs...")
    times = []
    for _ in range(num_runs):
        start_time = time.time()
        model.predict(dummy_input, verbose=0)
        end_time = time.time()
        times.append(end_time - start_time)
    
    # Tính toán metrics
    avg_time = np.mean(times)
    std_time = np.std(times)
    fps = 1.0 / avg_time
    
    return {
        'average_inference_time': avg_time * 1000,  # Convert to ms
        'std_inference_time': std_time * 1000,      # Convert to ms
        'fps': fps,
        'min_fps': 1.0 / (avg_time + std_time),
        'max_fps': 1.0 / (avg_time - std_time)
    }

def measure_memory_usage(model_path):
    """
    Đo lượng bộ nhớ sử dụng
    """
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Load model
    model = load_model(model_path)
    
    # Đo bộ nhớ sau khi load model
    model_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Tạo dữ liệu giả lập và đo bộ nhớ khi inference
    dummy_input = np.random.random((1, 48, 48, 1))
    model.predict(dummy_input, verbose=0)
    inference_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    return {
        'initial_memory_mb': initial_memory,
        'model_memory_mb': model_memory - initial_memory,
        'inference_memory_mb': inference_memory - model_memory
    }

def measure_camera_fps():
    """
    Đo FPS thực tế khi xử lý camera
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None
    
    # Đọc vài frame để khởi động camera
    for _ in range(10):
        cap.read()
    
    # Đo FPS
    num_frames = 100
    start_time = time.time()
    
    for _ in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            break
    
    end_time = time.time()
    cap.release()
    
    total_time = end_time - start_time
    fps = num_frames / total_time
    
    return {
        'camera_fps': fps,
        'frame_time_ms': (total_time / num_frames) * 1000
    }

def main():
    model_path = 'models/emotion_model_cnn.h5'
    
    print("\n=== Model Performance Metrics ===")
    
    # Đo tốc độ suy luận
    inference_metrics = measure_inference_speed(model_path)
    print("\nInference Speed:")
    print(f"Average inference time: {inference_metrics['average_inference_time']:.2f} ms")
    print(f"Standard deviation: {inference_metrics['std_inference_time']:.2f} ms")
    print(f"FPS: {inference_metrics['fps']:.2f}")
    print(f"FPS range: {inference_metrics['min_fps']:.2f} - {inference_metrics['max_fps']:.2f}")
    
    # Đo bộ nhớ
    memory_metrics = measure_memory_usage(model_path)
    print("\nMemory Usage:")
    print(f"Model size: {memory_metrics['model_memory_mb']:.2f} MB")
    print(f"Additional memory during inference: {memory_metrics['inference_memory_mb']:.2f} MB")
    
    # Đo FPS camera
    camera_metrics = measure_camera_fps()
    if camera_metrics:
        print("\nCamera Performance:")
        print(f"Camera FPS: {camera_metrics['camera_fps']:.2f}")
        print(f"Frame processing time: {camera_metrics['frame_time_ms']:.2f} ms")
    
    # Tính toán độ trễ tổng thể
    total_latency = inference_metrics['average_inference_time'] + (1000 / camera_metrics['camera_fps'])
    print(f"\nTotal system latency: {total_latency:.2f} ms")

if __name__ == "__main__":
    main() 