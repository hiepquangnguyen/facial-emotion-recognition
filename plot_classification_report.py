import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data from classification report
data = {
    'class': ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'],
    'precision': [0.5020, 0.5641, 0.5276, 0.8287, 0.5080, 0.7430, 0.4628],
    'recall': [0.5261, 0.1982, 0.2520, 0.8484, 0.4082, 0.7377, 0.7518],
    'f1-score': [0.5138, 0.2933, 0.3410, 0.8384, 0.4526, 0.7403, 0.5729],
    'support': [958, 111, 1024, 1774, 1247, 831, 1233]
}

df = pd.DataFrame(data)

# Create figure with subplots
plt.style.use('default')  # Use default matplotlib style
fig = plt.figure(figsize=(20, 15))

# 1. Bar plot for metrics
ax1 = plt.subplot(2, 2, 1)
x = np.arange(len(df['class']))
width = 0.25

ax1.bar(x - width, df['precision'], width, label='Precision', color='skyblue')
ax1.bar(x, df['recall'], width, label='Recall', color='lightgreen')
ax1.bar(x + width, df['f1-score'], width, label='F1-score', color='salmon')

ax1.set_ylabel('Score')
ax1.set_title('Metrics by Class')
ax1.set_xticks(x)
ax1.set_xticklabels(df['class'], rotation=45)
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Bar plot for support
ax2 = plt.subplot(2, 2, 2)
ax2.bar(df['class'], df['support'], color='lightblue')
ax2.set_ylabel('Number of Samples')
ax2.set_title('Support by Class')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3)

# 3. Radar plot
ax3 = plt.subplot(2, 2, 3, polar=True)

# Number of variables
categories = df['class']
N = len(categories)

# Compute angle for each axis
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

# Plot precision
values = df['precision'].values
values = np.concatenate((values, [values[0]]))
ax3.plot(angles, values, linewidth=2, linestyle='solid', label='Precision')
ax3.fill(angles, values, alpha=0.1)

# Plot recall
values = df['recall'].values
values = np.concatenate((values, [values[0]]))
ax3.plot(angles, values, linewidth=2, linestyle='solid', label='Recall')
ax3.fill(angles, values, alpha=0.1)

# Plot f1-score
values = df['f1-score'].values
values = np.concatenate((values, [values[0]]))
ax3.plot(angles, values, linewidth=2, linestyle='solid', label='F1-score')
ax3.fill(angles, values, alpha=0.1)

# Set labels
plt.xticks(angles[:-1], categories)
ax3.set_ylim(0, 1)
ax3.legend(loc='upper right', bbox_to_anchor=(0.3, 0.3))
ax3.set_title('Metrics Radar Plot')

# 4. Heatmap of metrics
ax4 = plt.subplot(2, 2, 4)
metrics = df[['precision', 'recall', 'f1-score']].values
im = ax4.imshow(metrics, cmap='YlOrRd')

# Add colorbar
cbar = ax4.figure.colorbar(im, ax=ax4)
cbar.ax.set_ylabel('Score', rotation=-90, va="bottom")

# Add labels
ax4.set_xticks(np.arange(3))
ax4.set_yticks(np.arange(len(df['class'])))
ax4.set_xticklabels(['Precision', 'Recall', 'F1-score'])
ax4.set_yticklabels(df['class'])

# Rotate the tick labels and set their alignment
plt.setp(ax4.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

# Add text annotations
for i in range(len(df['class'])):
    for j in range(3):
        text = ax4.text(j, i, f"{metrics[i, j]:.3f}",
                       ha="center", va="center", color="black")

ax4.set_title("Metrics Heatmap")

# Adjust layout and save
plt.tight_layout()
plt.savefig('classification_report_plots.png', dpi=300, bbox_inches='tight')
plt.close() 