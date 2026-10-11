import streamlit as st
import cv2 as cv
import numpy as np
from sklearn.cluster import DBSCAN


def detect_by_contours(image, min_w, max_w, min_h, max_h):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    edges = cv.Canny(blurred, 50, 150)
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    candidates = []
    for contour in contours:
        peri = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.04 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv.boundingRect(contour)
            if min_w <= w <= max_w and min_h <= h <= max_h:
                candidates.append((x, y, w, h))
    return candidates


def detect_by_template(image, template, threshold):
    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    h, w = template.shape[:2]
    res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    points = list(zip(*loc[::-1]))

    if not points:
        return []

    db = DBSCAN(eps=3, min_samples=1)
    points_array = np.array(points)
    labels = db.fit_predict(points_array)

    candidates = []
    for label in set(labels):
        if label != -1:
            xy = points_array[labels == label]
            median_point = np.median(xy, axis=0).astype(int)
            candidates.append((median_point[0], median_point[1], w, h))
    return candidates


def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[0] + box1[2], box2[0] + box2[2])
    y2 = min(box1[1] + box1[3], box2[1] + box2[3])
    if x2 < x1 or y2 < y1:
        return 0.0
    inter = (x2 - x1) * (y2 - y1)
    union = box1[2] * box1[3] + box2[2] * box2[3] - inter
    return inter / union if union > 0 else 0.0


def find_intersecting_boxes(boxes1, boxes2, iou_threshold):
    robust = []
    for b1 in boxes1:
        for b2 in boxes2:
            if calculate_iou(b1, b2) >= iou_threshold:
                robust.append((
                    int((b1[0] + b2[0]) / 2),
                    int((b1[1] + b2[1]) / 2),
                    int((b1[2] + b2[2]) / 2),
                    int((b1[3] + b2[3]) / 2),
                ))
                break
    return robust


def load_image_from_upload(upload, flags=cv.IMREAD_COLOR):
    arr = np.frombuffer(upload.read(), np.uint8)
    return cv.imdecode(arr, flags)


def load_image_from_path(path, flags=cv.IMREAD_COLOR):
    img = cv.imread(path, flags)
    return img


# --- UI ---
st.title("Détection robuste de cases à cocher")
st.write("Combine détection par contours et template matching, filtrée par IoU.")

# --- Chargement des images ---
st.sidebar.header("Images")
with st.sidebar.expander("📄 Image principale", expanded=True):
    upload_main = st.file_uploader("Charger une image", type=["png", "jpg", "jpeg"], key="main")
    st.caption("Laissez vide pour utiliser l'image de démonstration.")

with st.sidebar.expander("🔲 Template (case à cocher)", expanded=True):
    upload_tmpl = st.file_uploader("Charger un template", type=["png", "jpg", "jpeg"], key="tmpl")
    st.caption("Laissez vide pour utiliser le template de démonstration.")

if upload_main:
    img_rgb = load_image_from_upload(upload_main)
else:
    img_rgb = load_image_from_path("./assets/CHECK_TEST.png")

if upload_tmpl:
    template = load_image_from_upload(upload_tmpl, cv.IMREAD_GRAYSCALE)
else:
    template = load_image_from_path("./assets/CHECKED_ICON.png", cv.IMREAD_GRAYSCALE)

if img_rgb is None:
    st.error("Image principale introuvable. Chargez une image via la sidebar.")
    st.stop()

if template is None:
    st.error("Template introuvable. Chargez un template via la sidebar.")
    st.stop()

# --- Paramètres ---
st.sidebar.header("Paramètres")
threshold = st.sidebar.slider("Seuil template matching", 0, 100, 50) / 100
min_w, max_w = st.sidebar.slider("Largeur des cases (px)", 0, 200, (25, 75))
min_h, max_h = st.sidebar.slider("Hauteur des cases (px)", 0, 200, (25, 75))
iou_threshold = st.sidebar.slider("Seuil IoU", 0, 100, 50) / 100

# --- Détection ---
contour_boxes = detect_by_contours(img_rgb, min_w, max_w, min_h, max_h)
template_boxes = detect_by_template(img_rgb, template, threshold)
robust_boxes = find_intersecting_boxes(contour_boxes, template_boxes, iou_threshold)

# --- Visualisation ---
debug_img = img_rgb.copy()
result_img = img_rgb.copy()

for x, y, w, h in contour_boxes:
    cv.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
for x, y, w, h in template_boxes:
    cv.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 1)
for x, y, w, h in robust_boxes:
    cv.rectangle(result_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Vue debug")
    st.caption("🟢 Contours   🔵 Template matching")
    st.image(debug_img, channels="BGR", use_container_width=True)
    st.metric("Contours détectés", len(contour_boxes))
    st.metric("Templates détectés", len(template_boxes))

with col2:
    st.subheader("Détection robuste (IoU)")
    st.caption("🔴 Cases confirmées par les deux méthodes")
    st.image(result_img, channels="BGR", use_container_width=True)
    st.metric("Cases robustes", len(robust_boxes))
