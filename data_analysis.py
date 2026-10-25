import os
import numpy as np
import matplotlib.pyplot as plt
from utils import load_dataset
from sklearn.model_selection import StratifiedShuffleSplit

os.makedirs('results', exist_ok=True)

# Vẽ phân phối lớp cho train, val, test
def plot_class_distribution(y, class_names, title, filename):
    counts = np.sum(y, axis=0)
    plt.figure(figsize=(8, 4))
    plt.bar(class_names, counts)
    plt.title(title)
    plt.xlabel('Class')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"{title}: {dict(zip(class_names, counts))}")

# Hiển thị ảnh mẫu từng lớp
def show_sample_images(X, y, class_names, filename):
    plt.figure(figsize=(12, 6))
    for i, class_name in enumerate(class_names):
        idx = np.where(np.argmax(y, axis=1) == i)[0]
        if len(idx) > 0:
            plt.subplot(2, 4, i+1)
            plt.imshow(X[idx[0]].squeeze(), cmap='gray')
            plt.title(class_name)
            plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

if __name__ == '__main__':
    data_dir = 'data'
    class_names = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
    # Train
    X_train, y_train = load_dataset(data_dir, mode='train')
    plot_class_distribution(y_train, class_names, 'Train Set Class Distribution', 'results/train_class_dist_analysis.png')
    show_sample_images(X_train, y_train, class_names, 'results/train_samples.png')
    # Validation (tách từ train)
    y_train_labels = np.argmax(y_train, axis=1)
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    for train_idx, val_idx in sss.split(X_train, y_train_labels):
        X_val, y_val = X_train[val_idx], y_train[val_idx]
    plot_class_distribution(y_val, class_names, 'Validation Set Class Distribution', 'results/val_class_dist_analysis.png')
    show_sample_images(X_val, y_val, class_names, 'results/val_samples.png')
    # Test
    X_test, y_test = load_dataset(data_dir, mode='test')
    plot_class_distribution(y_test, class_names, 'Test Set Class Distribution', 'results/test_class_dist_analysis.png')
    show_sample_images(X_test, y_test, class_names, 'results/test_samples.png')
    # Thống kê số lượng ảnh
    print(f'Train samples: {X_train.shape[0]}, Validation samples: {X_val.shape[0]}, Test samples: {X_test.shape[0]}') 