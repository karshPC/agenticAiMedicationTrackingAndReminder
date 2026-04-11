import pytesseract
import cv2
import numpy as np


def preprocess(image_path):
    img = cv2.imread(image_path)

    # 🔥 resize (VERY IMPORTANT)
    img = cv2.resize(img, None, fx=2, fy=2)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 🔥 remove noise
    gray = cv2.medianBlur(gray, 3)

    # 🔥 edge enhancement
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharp = cv2.filter2D(gray, -1, kernel)

    # 🔥 threshold
    thresh = cv2.adaptiveThreshold(
        sharp,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh


def extract_text(image_path):
    img = preprocess(image_path)

    config = "--oem 3 --psm 6"

    text = pytesseract.image_to_string(img, config=config)

    return text