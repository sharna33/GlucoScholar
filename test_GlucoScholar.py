from GlucoScholar import randomForest, ploting_charts, ImageProcessor, InformationFetcher
import os
import matplotlib.pyplot as plt
import pytesseract

# Define local storage paths
LOCAL_DATA_DIR = "d:/GlucoScholar/data"
LOCAL_IMAGES_DIR = os.path.join(LOCAL_DATA_DIR, "images")
LOCAL_IMAGE_PATH = os.path.join(LOCAL_IMAGES_DIR, "Image-1.png")

# Create directories if they don't exist
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
os.makedirs(LOCAL_IMAGES_DIR, exist_ok=True)

# Initialize and run Random Forest model
radFor = randomForest()
predict = radFor.bulkPrediction("https://gist.githubusercontent.com/sharna33/218183b8151378720081809c92b92235/raw/f949bf5752e27a99a44f34b685568801e57dbfe0/diabetes_prediction_dataset.csv", 100)

# Plot predictions
plotObj = ploting_charts()
diabetics = {"Yes": 0, "No": 0}

for _ in predict:
    if _ == 1:
        diabetics["Yes"] += 1
    else:
        diabetics["No"] += 1

print(diabetics.items())
plotObj.pieChart(diabetics.values(), diabetics.keys(), "Diabetes Prediction")

# Test OCR/Info modules with local image
image_processor = ImageProcessor()
info_fetcher = InformationFetcher()

# Use local image path - update this path to your actual image location
image_path = os.path.join(LOCAL_IMAGE_PATH)
extracted_text = image_processor.extract_text(image_path)
print(f"Extracted Text: {extracted_text}")

google_results = info_fetcher.google_search(extracted_text)
print(f"Google Search Results:\n", google_results)
