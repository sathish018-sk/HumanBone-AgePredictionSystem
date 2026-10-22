import cv2

# Choose a sample image from the dataset
test_image_path = r"V:/archive/boneage_dataset/boneage_dataset/5933.png"  # Change to an actual image

img = cv2.imread(test_image_path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("❌ OpenCV cannot read the image. Check the path or file format.")
else:
    print(f"✅ Image loaded successfully - Shape: {img.shape}")
    cv2.imshow("Test Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
