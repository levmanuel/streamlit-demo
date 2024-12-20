import streamlit as st
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

st.title("Détection de cases à cocher")
st.write("Chargez une image pour détecter les cases à cocher.")

threshold = st.slider("thresold", 0, 100, 50, 1) / 100
img_rgb = cv.imread('./assets/CHECK_TEST.png')
img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
template = cv.imread('./assets/CHECKED_ICON.png', cv.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]
res = cv.matchTemplate(img_gray,template,cv.TM_CCOEFF_NORMED)
loc = np.where( res >= threshold)
points = list(zip(*loc[::-1]))
tot = len(points)
st.text(f"Nb de points: {tot}")
for pt in points:
    st.text(pt)
    cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

st.image(img_rgb, channels="BGR", caption="Image traitée")