import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.utils import Sequence
from tensorflow.keras.preprocessing.image import ImageDataGenerator

class EmotionDataGenerator(Sequence):
    def __init__(self, data_dir, mode='train', batch_size=64, target_size=(48, 48), shuffle=True, augment=False):
        self.data_dir = data_dir
        self.mode = mode
        self.batch_size = batch_size
        self.target_size = target_size
        self.shuffle = shuffle
        self.augment = augment
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.num_classes = len(self.emotions)
        self.image_paths = []
        self.labels = []
        for emotion_idx, emotion in enumerate(self.emotions):
            emotion_dir = os.path.join(data_dir, mode, emotion)
            if not os.path.exists(emotion_dir):
                print(f"Warning: Directory {emotion_dir} does not exist")
                continue
            for img_name in os.listdir(emotion_dir):
                img_path = os.path.join(emotion_dir, img_name)
                self.image_paths.append(img_path)
                self.labels.append(emotion_idx)
        self.labels = np.array(self.labels)
        self.on_epoch_end()
        if self.augment and self.mode == 'train':
            self.datagen = ImageDataGenerator(
                rotation_range=15,
                width_shift_range=0.1,
                height_shift_range=0.1,
                zoom_range=0.1,
                horizontal_flip=True,
                brightness_range=[0.8, 1.2],
                fill_mode='nearest'
            )
        else:
            self.datagen = ImageDataGenerator()
        print(f"Loaded {len(self.image_paths)} {mode} images")

    def __len__(self):
        return int(np.ceil(len(self.image_paths) / self.batch_size))

    def __getitem__(self, idx):
        batch_indexes = self.indexes[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_paths = [self.image_paths[i] for i in batch_indexes]
        batch_labels = self.labels[batch_indexes]
        X = np.zeros((len(batch_paths), *self.target_size, 1), dtype=np.float32)
        y = tf.keras.utils.to_categorical(batch_labels, num_classes=self.num_classes)
        for i, img_path in enumerate(batch_paths):
            img = tf.keras.preprocessing.image.load_img(img_path, color_mode='grayscale', target_size=self.target_size)
            img = tf.keras.preprocessing.image.img_to_array(img)
            img = img.astype('float32') / 255.0
            X[i] = img
        if self.augment and self.mode == 'train':
            X, y = next(self.datagen.flow(X, y, batch_size=self.batch_size, shuffle=False))
        return X, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.image_paths))
        if self.shuffle:
            np.random.shuffle(self.indexes) 