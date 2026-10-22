import os
import pandas as pd
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

DATASET_PATH = r"V:/boneage/bonedata"
IMAGE_PATH = r"V:/boneage/bonedata/image"

def load_data():
    df = pd.read_csv(f"{DATASET_PATH}/boneage_dataset.csv")
    df["id"] = df["id"].astype(str)
    
    X = []
    y = []
    
    for idx, row in df.iterrows():
        img_path = os.path.join(IMAGE_PATH, f"{row['id']}.png")
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (224, 224))
            img = img.flatten()
            X.append(img)
            y.append(row['boneage'])
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Loaded {len(X)} images and {len(y)} labels.")  # sanity check
    
    return train_test_split(X, y, test_size=0.2, random_state=42)
