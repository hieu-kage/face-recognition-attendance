import os
import math
import numpy as np
import pandas as pd
from tqdm import tqdm

import matplotlib.pyplot as plt
import seaborn as sns

import cv2
from tensorflow.keras.preprocessing.image import load_img, img_to_array

import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input

try:
    from keras_facenet import FaceNet
except ImportError:
    import os
    os.system("pip install keras-facenet")
    from keras_facenet import FaceNet

from sklearn.metrics.pairwise import euclidean_distances as L2

try:
    from mtcnn import MTCNN
except ImportError:
    import os
    os.system("pip install mtcnn")
    from mtcnn import MTCNN

print("\n=== Rebuilding Model & Loading Weights ===")

try:
    print("1. Rebuilding model architecture...")
    from keras_facenet import FaceNet

    embedder_loader = FaceNet()
    rebuilt_model = embedder_loader.model

    inputs = Input(shape=(160, 160, 3))
    outputs = rebuilt_model(inputs)
    embeddings = Model(inputs, outputs)

    weights_path = "/kaggle/working/models/siamese_weights.weights.h5"

    if os.path.exists(weights_path):
        print(f"2. Loading weights from: {weights_path}")
        embeddings.load_weights(weights_path)
        print("✓ Weights loaded successfully!")
    else:
        raise FileNotFoundError(f"Weights file not found at {weights_path}")

    print(f"\nModel Status:")
    print(f"• Input shape: {embeddings.input_shape}")
    print(f"• Output shape: {embeddings.output_shape}")
    print(f"• Weights loaded from: {os.path.basename(weights_path)}")

except Exception as e:
    print(f"\n❌ Error rebuilding model: {str(e)}")
    print("Fallback: Using the model currently in memory from training session...")
    embeddings = siamese_network.layers[-1]

print("\n=== Evaluating Rebuilt Model ===")

anchor_embeddings = []
positive_embeddings = []
negative_embeddings = []

print("Generating embeddings for test set...")
for i in tqdm(range(len(test_generator))):
    batch = test_generator[i]

    anchor_batch = embeddings.predict(batch[0], verbose=0)
    pos_batch = embeddings.predict(batch[1], verbose=0)
    neg_batch = embeddings.predict(batch[2], verbose=0)

    anchor_embeddings.append(anchor_batch)
    positive_embeddings.append(pos_batch)
    negative_embeddings.append(neg_batch)

y_pred = [
    np.concatenate(anchor_embeddings, axis=0),
    np.concatenate(positive_embeddings, axis=0),
    np.concatenate(negative_embeddings, axis=0)
]

print(f"Generated embeddings shape: {y_pred[0].shape}")

print("\nCalculating distances...")
distances = []
for i in tqdm(range(len(test))):
    pos = L2(y_pred[0][i, :].reshape(1, -1), y_pred[1][i, :].reshape(1, -1))[0][0]
    neg = L2(y_pred[0][i, :].reshape(1, -1), y_pred[2][i, :].reshape(1, -1))[0][0]
    distances.append([pos, neg])

test_results = test.copy()
test_results.loc[:, ['pos_dist', 'neg_dist']] = distances

print("\n=== Distance Statistics ===")
print(test_results[['pos_dist', 'neg_dist']].describe())

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.hist(test_results['pos_dist'], bins=50, alpha=0.7, label='Positive Pairs', color='green')
plt.hist(test_results['neg_dist'], bins=50, alpha=0.7, label='Negative Pairs', color='red')
plt.xlabel('Distance')
plt.ylabel('Frequency')
plt.title('Distance Distribution (Rebuilt Model)')
plt.legend()
plt.axvline(x=1.0, color='blue', linestyle='--', label='Ref Threshold')

plt.subplot(1, 3, 2)
sns.boxplot(data=pd.melt(test_results[['pos_dist', 'neg_dist']]),
            x='variable', y='value')
plt.title('Distance Comparison')

plt.subplot(1, 3, 3)
thresholds_range = np.linspace(0.5, 3.0, 50)
accuracies = []
for thresh in thresholds_range:
    correct = len(test_results[
                      (test_results['pos_dist'] < thresh) &
                      (test_results['neg_dist'] > thresh)
                      ])
    accuracies.append(correct / len(test_results) * 100)
plt.plot(thresholds_range, accuracies)
plt.xlabel('Threshold')
plt.ylabel('Accuracy (%)')
plt.title('Accuracy vs Threshold')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('evaluation_rebuilt_model.png', dpi=300, bbox_inches='tight')
plt.show()

best_acc = 0
best_thresh = 0
for thresh in np.arange(0.5, 2.0, 0.05):
    correct = len(test_results[
                      (test_results['pos_dist'] < thresh) &
                      (test_results['neg_dist'] > thresh)
                      ])
    acc = correct / len(test_results) * 100
    if acc > best_acc:
        best_acc = acc
        best_thresh = thresh

print("-" * 50)
print(f"Rebuilt Model Evaluation Results:")
print(f"Best Threshold: {best_thresh:.2f}")
print(f"Best Accuracy: {best_acc:.2f}%")
print("-" * 50)