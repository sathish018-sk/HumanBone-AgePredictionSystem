
import pandas as pd
import numpy as np
import cv2
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf
from tensorflow.keras import layers, models


# Paths
DATASET_PATH = "V:/boneage/bonedata/image"
CSV_PATH = "V:/boneage/bonedata/boneage_dataset.csv"


# Load CSV
df = pd.read_csv(CSV_PATH)
df["id"] = df["id"].astype(str)

# Prepare Data
X, y = [], []
for _, row in df.iterrows():
    img_path = os.path.join(DATASET_PATH, row["id"] + ".png")
    if os.path.exists(img_path):
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (128, 128))
        img = img / 255.0
        X.append(img)
        y.append(row["boneage"])


X = np.array(X).reshape(-1, 128, 128, 1)
y = np.array(y)

# Build Model
model = models.Sequential([
    layers.Input(shape=(128, 128, 1)),
    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dense(1)
])

model.compile(optimizer="adam", loss="mse", metrics=["mae"])

# Train
model.fit(X, y, epochs=60, batch_size=16)

# Save
model.save("bone_age_model.h5")
print("✅ Model trained & saved successfully!")
