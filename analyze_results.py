import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score, f1_score
from datetime import datetime
from utils import plot_confusion_matrix
import shutil

def convert_to_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def analyze_training_results(history, model, X_test, y_test):
    """
    Analyze and save training results
    """
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Save model summary
    with open("results/model_summary.txt", "w", encoding='utf-8') as f:
        model.summary(print_fn=lambda x: f.write(x + '\n'))
    
    # Save training history
    history_dict = {
        'accuracy': [float(x) for x in history.history['accuracy']],
        'val_accuracy': [float(x) for x in history.history['val_accuracy']],
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']],
        'learning_rate': [float(x) for x in history.history.get('lr', [])]
    }
    
    with open("results/training_history.json", "w") as f:
        json.dump(history_dict, f, indent=4)
    
    # Generate and save plots
    plt.figure(figsize=(15, 5))
    
    # Plot accuracy
    plt.subplot(1, 3, 1)
    plt.plot(history.history['accuracy'], label='Training')
    plt.plot(history.history['val_accuracy'], label='Validation')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    # Plot loss
    plt.subplot(1, 3, 2)
    plt.plot(history.history['loss'], label='Training')
    plt.plot(history.history['val_loss'], label='Validation')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    # Plot learning rate
    if 'lr' in history.history:
        plt.subplot(1, 3, 3)
        plt.plot(history.history['lr'])
        plt.title('Learning Rate')
        plt.xlabel('Epoch')
        plt.ylabel('Learning Rate')
    
    plt.tight_layout()
    plt.savefig("results/training_plots.png")
    plt.close()
    
    # Get predictions
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
    
    # Generate and save classification report
    class_names = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
    report = classification_report(y_true_classes, y_pred_classes, target_names=class_names, output_dict=True, zero_division=0)
    
    # Convert report values to serializable types
    serializable_report = {k: convert_to_serializable(v) if isinstance(v, (np.integer, np.floating)) else v 
                         for k, v in report.items()}
    
    with open("results/classification_report.json", "w") as f:
        json.dump(serializable_report, f, indent=4)
    
    # Generate and save confusion matrix
    cm = confusion_matrix(y_true_classes, y_pred_classes)
    os.makedirs("plots", exist_ok=True)  # Đảm bảo thư mục plots tồn tại
    plot_confusion_matrix(cm, class_names, model_name="Emotion Model CNN")
    
    # Calculate and save detailed metrics
    metrics = {}
    for i, class_name in enumerate(class_names):
        metrics[class_name] = {
            'precision': convert_to_serializable(precision_score(y_true_classes == i, y_pred_classes == i, zero_division=0)),
            'recall': convert_to_serializable(recall_score(y_true_classes == i, y_pred_classes == i, zero_division=0)),
            'f1-score': convert_to_serializable(f1_score(y_true_classes == i, y_pred_classes == i, zero_division=0)),
            'support': convert_to_serializable(np.sum(y_true_classes == i))
        }
    
    with open("results/detailed_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
    
    # Plot class distribution
    plt.figure(figsize=(10, 6))
    class_dist = np.sum(y_test, axis=0)
    plt.bar(class_names, class_dist)
    plt.title('Class Distribution in Test Set')
    plt.xlabel('Emotion Class')
    plt.ylabel('Number of Samples')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("results/class_distribution.png")
    plt.close()
    
    # Lưu 20 ảnh bị nhầm lẫn điển hình
    misclassified_dir = 'results/misclassified'
    if os.path.exists(misclassified_dir):
        shutil.rmtree(misclassified_dir)
    os.makedirs(misclassified_dir, exist_ok=True)
    mis_idx = [i for i in range(len(y_true_classes)) if y_true_classes[i] != y_pred_classes[i]]
    # Chọn tối đa 20 ảnh nhầm lẫn, ưu tiên các lớp khó
    selected_idx = mis_idx[:20]
    for i in selected_idx:
        img = X_test[i].squeeze()
        plt.imsave(f'{misclassified_dir}/true_{y_true_classes[i]}_pred_{y_pred_classes[i]}_{i}.png', img, cmap='gray')
    
    return metrics 