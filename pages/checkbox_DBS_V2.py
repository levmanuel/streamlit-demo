import streamlit as st
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN

def detect_by_contours(image, min_w, max_w, min_h, max_h):
    """
    Première méthode : détection par contours
    Retourne une liste de tuples (x, y, w, h)
    """
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    edges = cv.Canny(blurred, 50, 150)
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    candidates = []
    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.04 * peri, True)
        if len(approx) == 4:  # Un rectangle a 4 coins
            x, y, w, h = cv.boundingRect(contour)
            if min_w <= w <= max_w and min_h <= h <= max_h:
                candidates.append((x, y, w, h))
    return candidates

def detect_by_template(image, template, threshold):
    """
    Deuxième méthode : détection par template matching
    Retourne une liste de tuples (x, y, w, h)
    """
    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))
    
    # Clustering des points proches
    if len(points) > 0:
        db = DBSCAN(eps=3, min_samples=1)
        points_array = np.array(points)
        labels = db.fit_predict(points_array)
        
        candidates = []
        for label in set(labels):
            if label != -1:
                class_member_mask = (labels == label)
                xy = points_array[class_member_mask]
                # Prendre le point médian du cluster
                median_point = np.median(xy, axis=0).astype(int)
                candidates.append((median_point[0], median_point[1], w, h))
        return candidates
    return []

def find_intersecting_boxes(boxes1, boxes2, iou_threshold=0.5):
    """
    Trouve les boîtes qui se chevauchent entre les deux ensembles
    en utilisant l'IoU (Intersection over Union)
    """
    def calculate_iou(box1, box2):
        # Convertir (x, y, w, h) en (x1, y1, x2, y2)
        box1_x1, box1_y1 = box1[0], box1[1]
        box1_x2, box1_y2 = box1[0] + box1[2], box1[1] + box1[3]
        box2_x1, box2_y1 = box2[0], box2[1]
        box2_x2, box2_y2 = box2[0] + box2[2], box2[1] + box2[3]
        
        # Calculer l'intersection
        x_left = max(box1_x1, box2_x1)
        y_top = max(box1_y1, box2_y1)
        x_right = min(box1_x2, box2_x2)
        y_bottom = min(box1_y2, box2_y2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
            
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculer l'union
        box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1)
        box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1)
        union_area = box1_area + box2_area - intersection_area
        
        iou = intersection_area / union_area if union_area > 0 else 0
        return iou
    
    robust_boxes = []
    for box1 in boxes1:
        for box2 in boxes2:
            if calculate_iou(box1, box2) >= iou_threshold:
                # Prendre la moyenne des deux boîtes
                x = int((box1[0] + box2[0]) / 2)
                y = int((box1[1] + box2[1]) / 2)
                w = int((box1[2] + box2[2]) / 2)
                h = int((box1[3] + box2[3]) / 2)
                robust_boxes.append((x, y, w, h))
                break
    return robust_boxes

# Interface Streamlit
st.title("Détection robuste de cases à cocher")
st.write("Utilisation de deux méthodes de détection combinées")

# Paramètres
threshold = st.slider("Seuil de template matching", 0, 100, 50, 1) / 100
min_w = st.number_input("Largeur minimum", min_value=10, max_value=200, value=20)
max_w = st.number_input("Largeur maximum", min_value=10, max_value=200, value=50)
min_h = st.number_input("Hauteur minimum", min_value=10, max_value=200, value=20)
max_h = st.number_input("Hauteur maximum", min_value=10, max_value=200, value=50)
iou_threshold = st.slider("Seuil IoU", 0, 100, 50, 1) / 100

# Chargement des images
img_rgb = cv.imread('./assets/CHECK_TEST.png')
template = cv.imread('./assets/CHECKED_ICON.png', cv.IMREAD_GRAYSCALE)

# Création d'une copie pour visualisation
debug_img = img_rgb.copy()

# Détection avec les deux méthodes
contour_boxes = detect_by_contours(img_rgb, min_w, max_w, min_h, max_h)
template_boxes = detect_by_template(img_rgb, template, threshold)

# Dessiner les boîtes de la première méthode en vert
for box in contour_boxes:
    x, y, w, h = box
    cv.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 1)

# Dessiner les boîtes de la deuxième méthode en bleu
for box in template_boxes:
    x, y, w, h = box
    cv.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 1)

# Trouver et dessiner l'intersection en rouge
robust_boxes = find_intersecting_boxes(contour_boxes, template_boxes, iou_threshold)
for box in robust_boxes:
    x, y, w, h = box
    cv.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 0, 255), 2)

# Affichage des résultats
col1, col2 = st.columns(2)
with col1:
    st.write("Debug view (vert: contours, bleu: template)")
    st.image(debug_img, channels="BGR")
    st.text(f"Contours détectés: {len(contour_boxes)}")
    st.text(f"Templates détectés: {len(template_boxes)}")

with col2:
    st.write("Détection robuste (intersection)")
    st.image(img_rgb, channels="BGR")
    st.text(f"Cases robustes: {len(robust_boxes)}")