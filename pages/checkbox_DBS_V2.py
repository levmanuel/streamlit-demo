import streamlit as st
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN

def process_image(image, min_w, max_w, min_h, max_h):
    # Conversion en niveaux de gris
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    edges = cv.Canny(blurred, 50, 150)
    contours, * = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    checkboxes = []
    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.04 * peri, True)
        if len(approx) == 4: # Un rectangle a 4 coins
            x, y, w, h = cv.boundingRect(contour)
            # Filtrer les rectangles en fonction des tailles min/max définies par l'utilisateur
            if min_w <= w <= max_w and min_h <= h <= max_h:
                checkboxes.append((x, y, w, h))
    
    for i, checkbox in enumerate(checkboxes):
        offset = 3
        x, y, w, h = checkbox
        roi = image[y + offset : y + h - offset, x + offset : x + w - offset]
        gray_roi = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray_roi, 128, 255, cv.THRESH_BINARY)
        white_pixels = np.sum(thresh == 255)
        total_pixels = (w - 2 * offset) * (h - 2 * offset)
        if white_pixels / total_pixels < 0.9:
            # Si plus de 50% des pixels de la case sont blancs, on considère la case cochée
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) # Contour vert
        else:
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1) # Contour rouge
    return image

st.title("Détection de cases à cocher")
st.write("Chargez une image pour détecter les cases à cocher.")

threshold = st.slider("thresold", 0, 100, 50, 1) / 100
min_w = st.number_input("Largeur minimum de la case", min_value=10, max_value=200, value=20, step=1)
max_w = st.number_input("Largeur maximum de la case", min_value=10, max_value=200, value=50, step=1)
min_h = st.number_input("Hauteur minimum de la case", min_value=10, max_value=200, value=20, step=1)
max_h = st.number_input("Hauteur maximum de la case", min_value=10, max_value=200, value=50, step=1)

img_rgb = cv.imread('./assets/CHECK_TEST.png')
img_rgb = process_image(img_rgb, min_w, max_w, min_h, max_h)

img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
template = cv.imread('./assets/CHECKED_ICON.png', cv.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]
res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
loc = np.where(res >= threshold)
points = list(zip(*loc[::-1]))

# Apply DBSCAN clustering to group nearby points
db = DBSCAN(eps=3, min_samples=1)
points_array = np.array(points)
labels = db.fit_predict(points_array)
unique_labels = set(labels)

# Draw rectangles around the clustered checkboxes
for label in unique_labels:
    if label != -1:
        class_member_mask = (labels == label)
        xy = points_array[class_member_mask]
        for pt in xy:
            cv.rectangle(img_rgb, tuple(pt), (pt[0] + w, pt[1] + h), (0,0,255), 2)

st.text(f"Nb de points: {len(unique_labels)}")
st.image(img_rgb, channels="BGR", caption="Image traitée")