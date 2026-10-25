import os
import matplotlib.pyplot as plt

# Hàm đếm số lượng ảnh trong mỗi lớp
def count_images_per_class(data_dir):
    class_counts = {}
    for class_name in sorted(os.listdir(data_dir)):
        class_path = os.path.join(data_dir, class_name)
        if os.path.isdir(class_path):
            num_images = len([
                f for f in os.listdir(class_path)
                if f.lower().endswith(('.jpg', '.png', '.jpeg'))
            ])
            class_counts[class_name] = num_images
    return class_counts

train_dir = 'data/train'
test_dir = 'data/test'

train_counts = count_images_per_class(train_dir)
test_counts = count_images_per_class(test_dir)

# Vẽ biểu đồ
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Train
axes[0].bar(train_counts.keys(), train_counts.values(), color='#1976d2')
axes[0].set_title('Số lượng ảnh theo lớp cảm xúc (Train)')
axes[0].set_xlabel('Lớp cảm xúc')
axes[0].set_ylabel('Số lượng ảnh')
axes[0].set_xticklabels(train_counts.keys(), rotation=30, ha='right')

# Test
axes[1].bar(test_counts.keys(), test_counts.values(), color='#388e3c')
axes[1].set_title('Số lượng ảnh theo lớp cảm xúc (Test)')
axes[1].set_xlabel('Lớp cảm xúc')
axes[1].set_ylabel('Số lượng ảnh')
axes[1].set_xticklabels(test_counts.keys(), rotation=30, ha='right')

plt.tight_layout()
plt.savefig('class_distribution_train_test.png', dpi=150)
plt.show()

print('Đã lưu ảnh thống kê: class_distribution_train_test.png') 