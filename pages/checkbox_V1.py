import streamlit as st
import cv2
import numpy as np
from PIL import Image

def process_image(image, min_w, max_w, min_h, max_h):
    # Conversion en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    checkboxes = []

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        if len(approx) == 4:  # Un rectangle a 4 coins
            x, y, w, h = cv2.boundingRect(contour)
            # Filtrer les rectangles en fonction des tailles min/max définies par l'utilisateur
            if min_w <= w <= max_w and min_h <= h <= max_h:
                checkboxes.append((x, y, w, h))

    for i, checkbox in enumerate(checkboxes):
        offset = 3
        x, y, w, h = checkbox
        roi = image[y + offset : y + h - offset, x + offset : x + w - offset]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_roi, 128, 255, cv2.THRESH_BINARY)
        white_pixels = np.sum(thresh == 255)
        total_pixels = (w - 2 * offset) * (h - 2 * offset)

        if white_pixels / total_pixels < 0.9:
            # Si plus de 50% des pixels de la case sont blancs, on considère la case cochée
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Contour vert
        else:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)  # Contour rouge

    return image

st.title("Détection de cases à cocher")
st.write("Chargez une image pour détecter les cases à cocher.")

# Création des sliders pour les dimensions min/max des cases
min_w, max_w = st.slider("Largeur de la case", 10, 50, (15, 20))
min_h, max_h = min_w, max_w

# Chargement de l'image via drag and drop
uploaded_file = st.file_uploader("Choisissez une image...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Lire l'image
    image = np.array(Image.open(uploaded_file))

    # Traitement de l'image avec les valeurs de taille dynamiques
    processed_image = process_image(image, min_w, max_w, min_h, max_h)

    # Afficher l'image traitée
    st.image(processed_image, channels="BGR", caption="Image traitée")