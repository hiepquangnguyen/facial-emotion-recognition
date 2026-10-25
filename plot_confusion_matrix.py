import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Đọc file confusion matrix
df = pd.read_csv('models/confusion_matrix_cnn.csv', index_col=0)

# Tính toán tỷ lệ phần trăm
df_percent = df.div(df.sum(axis=1), axis=0) * 100

# Tạo figure với 2 subplot
plt.figure(figsize=(20, 8))

# 1. Heatmap với số lượng mẫu
plt.subplot(1, 2, 1)
sns.heatmap(df, annot=True, fmt='d', cmap='YlOrRd', 
            xticklabels=df.columns, yticklabels=df.index)
plt.title('Confusion Matrix (Count)', pad=20)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')

# 2. Heatmap với tỷ lệ phần trăm
plt.subplot(1, 2, 2)
sns.heatmap(df_percent, annot=True, fmt='.1f', cmap='YlOrRd',
            xticklabels=df.columns, yticklabels=df.index)
plt.title('Confusion Matrix (Percentage)', pad=20)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')

# Điều chỉnh layout và lưu
plt.tight_layout()
plt.savefig('confusion_matrix_visualization.png', dpi=300, bbox_inches='tight')
plt.close()

print("Confusion matrix visualization has been saved to 'confusion_matrix_visualization.png'") 