import pytesseract
import cv2
import numpy as np


def preprocess_image(image_path):
    img = cv2.imread(image_path)

    # Resize (VERY IMPORTANT)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Noise removal
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive threshold (better than simple threshold)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        15,
        3
    )

    return thresh


def extract_text(image_path):

    processed = preprocess_image(image_path)

    custom_config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(processed, config=custom_config)

    return text