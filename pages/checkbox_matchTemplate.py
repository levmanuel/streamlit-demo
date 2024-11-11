import streamlit as st
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

st.title("Détection de cases à cocher")
st.write("Chargez une image pour détecter les cases à cocher.")

threshold = st.slider("thresold", 0, 100, 40, 2) / 100
img_rgb = cv.imread('./assets/CHECK_TEST.png')
img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
template = cv.imread('./assets/CHECKED_ICON.png', cv.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]
res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
loc = np.where( res >= threshold)
points = zip(*loc[::-1])
st.text(len(points))
for pt in points:
    cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

st.image(img_rgb, channels="BGR", caption="Image traitée")

# # Chargement de l'image via drag and drop
# uploaded_file = st.file_uploader("Choisissez une image...", type=["png", "jpg", "jpeg"])

# if uploaded_file is not None:
#     # Lire l'image
#     image = np.array(Image.open(uploaded_file))

#     # Traitement de l'image avec les valeurs de taille dynamiques
#     processed_image = process_image(image, min_w, max_w, min_h, max_h)

#     # Afficher l'image traitée
#     st.image(processed_image, channels="BGR", caption="Image traitée")