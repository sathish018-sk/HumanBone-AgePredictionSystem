import joblib
import cv2
import numpy as np

model = joblib.load("model.pkl")

def predict_bone_age(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (224, 224))
    img = img.flatten().reshape(1, -1)
    return model.predict(img)[0]

# Example
predicted = predict_bone_age(r"V:/archive/boneage_dataset/boneage_dataset/5933.png")
print(f"📢 Predicted Bone Age: {predicted:.2f}")
