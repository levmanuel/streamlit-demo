import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import streamlit as st
import math

@dataclass
class Checkbox:
    x: int
    y: int
    w: int
    h: int
    confidence: float
    is_checked: bool
    check_confidence: float

class CheckboxDetector:
    def __init__(self, min_size: int = 15, max_size: int = 50, 
                 adaptive_threshold: bool = True):
        self.min_size = min_size
        self.max_size = max_size
        self.adaptive_threshold = adaptive_threshold
        self.reference_size = None
        self.calibrated = False
    
    def preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prétraitement amélioré avec correction d'orientation et amélioration du contraste"""
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Amélioration du contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Correction de la rotation
        angle = self._detect_rotation(gray)
        if abs(angle) > 0.5:
            gray = self._rotate_image(gray, angle)
            image = self._rotate_image(image, angle)
        
        # Création de deux versions du traitement
        if self.adaptive_threshold:
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
        else:
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Application d'opérations morphologiques pour nettoyer l'image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return gray, binary
    
    def _detect_rotation(self, gray: np.ndarray) -> float:
        """Détecte l'angle de rotation du document"""
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:, 0]:
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
            
            if angles:
                return np.median(angles)
        return 0.0
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotation de l'image avec préservation de la taille"""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rotation_matrix, (width, height), 
                            flags=cv2.INTER_CUBIC)
    
    def calibrate(self, sample_checkboxes: List[Tuple[int, int, int, int]]) -> None:
        """Calibration basée sur un échantillon de cases connues"""
        if not sample_checkboxes:
            return
        
        sizes = [(w, h) for _, _, w, h in sample_checkboxes]
        median_size = int(np.median([max(w, h) for w, h in sizes]))
        self.reference_size = median_size
        self.min_size = int(median_size * 0.7)
        self.max_size = int(median_size * 1.3)
        self.calibrated = True
    
    def detect_checkboxes(self, image: np.ndarray) -> List[Checkbox]:
        """Détection des cases avec une approche hybride"""
        gray, binary = self.preprocess_image(image)
        
        # Détection des contours avec les deux approches
        contours_binary, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, 
                                            cv2.CHAIN_APPROX_SIMPLE)
        
        edges = cv2.Canny(gray, 50, 150)
        contours_edges, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                           cv2.CHAIN_APPROX_SIMPLE)
        
        checkboxes = []
        processed_regions = np.zeros(gray.shape[:2], dtype=np.uint8)
        
        # Combiner les résultats des deux approches
        all_contours = contours_binary + contours_edges
        
        for contour in all_contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Éviter les doublons
            if processed_regions[y:y+h, x:x+w].any():
                continue
            
            confidence = self._evaluate_checkbox_confidence(contour, w, h)
            
            if confidence > 0.5:
                # Analyse du contenu
                roi = gray[y:y+h, x:x+w]
                is_checked, check_confidence = self._analyze_checkbox_content(roi)
                
                checkbox = Checkbox(x, y, w, h, confidence, is_checked, check_confidence)
                checkboxes.append(checkbox)
                
                # Marquer la région comme traitée
                processed_regions[y:y+h, x:x+w] = 255
        
        return self._remove_duplicates(checkboxes)
    
    def _evaluate_checkbox_confidence(self, contour: np.ndarray, 
                                   width: int, height: int) -> float:
        """Évalue la probabilité qu'un contour soit une case à cocher"""
        # Vérification de la taille
        if not (self.min_size <= width <= self.max_size and 
                self.min_size <= height <= self.max_size):
            return 0.0
        
        # Vérification de la forme
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
        
        # Score basé sur plusieurs critères
        scores = []
        
        # Score pour le nombre de coins
        corner_score = 1.0 if len(approx) == 4 else 0.0
        scores.append(corner_score)
        
        # Score pour le ratio d'aspect
        aspect_ratio = float(width) / height
        aspect_score = 1.0 - min(abs(aspect_ratio - 1.0), 0.5) * 2
        scores.append(aspect_score)
        
        # Score pour la taille relative
        if self.reference_size:
            size_score = 1.0 - min(abs(width - self.reference_size) / 
                                 self.reference_size, 0.5) * 2
            scores.append(size_score)
        
        return np.mean(scores)
    
    def _analyze_checkbox_content(self, roi: np.ndarray) -> Tuple[bool, float]:
        """Analyse le contenu d'une case avec plusieurs méthodes"""
        # Appliquer un seuillage adaptatif
        binary_roi = cv2.adaptiveThreshold(roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 11, 2)
        
        # Calcul du ratio de pixels noirs
        total_pixels = roi.size
        black_pixels = np.sum(binary_roi == 255)
        fill_ratio = black_pixels / total_pixels
        
        # Détection des lignes pour identifier les marques
        edges = cv2.Canny(roi, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=15, 
                              minLineLength=5, maxLineGap=3)
        
        has_lines = lines is not None and len(lines) > 0
        
        # Combiner les critères
        is_checked = fill_ratio > 0.1 or has_lines
        confidence = (fill_ratio + float(has_lines)) / 2
        
        return is_checked, confidence
    
    def _remove_duplicates(self, checkboxes: List[Checkbox]) -> List[Checkbox]:
        """Élimine les cases en double en conservant celle avec la plus grande confiance"""
        if not checkboxes:
            return []
        
        def overlap_ratio(box1: Checkbox, box2: Checkbox) -> float:
            x1 = max(box1.x, box2.x)
            y1 = max(box1.y, box2.y)
            x2 = min(box1.x + box1.w, box2.x + box2.w)
            y2 = min(box1.y + box1.h, box2.y + box2.h)
            
            if x2 <= x1 or y2 <= y1:
                return 0.0
                
            intersection = (x2 - x1) * (y2 - y1)
            area1 = box1.w * box1.h
            area2 = box2.w * box2.h
            return intersection / min(area1, area2)
        
        result = []
        checkboxes = sorted(checkboxes, key=lambda x: -x.confidence)
        
        while checkboxes:
            current = checkboxes.pop(0)
            result.append(current)
            checkboxes = [box for box in checkboxes 
                         if overlap_ratio(current, box) < 0.5]
        
        return result

def visualize_results(image: np.ndarray, checkboxes: List[Checkbox]) -> np.ndarray:
    """Visualisation des résultats avec informations détaillées"""
    result = image.copy()
    
    for checkbox in checkboxes:
        # Couleur basée sur la confiance et l'état
        confidence_color = int(255 * checkbox.confidence)
        if checkbox.is_checked:
            color = (0, confidence_color, 0)  # Vert
        else:
            color = (0, 0, confidence_color)  # Rouge
            
        # Dessiner le rectangle
        cv2.rectangle(result, (checkbox.x, checkbox.y), 
                     (checkbox.x + checkbox.w, checkbox.y + checkbox.h), 
                     color, 2)
        
        # Afficher les scores
        text = f"{checkbox.confidence:.2f}/{checkbox.check_confidence:.2f}"
        cv2.putText(result, text, (checkbox.x, checkbox.y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result

# Déclaration de l'interface Streamlit
st.title("Détection de cases à cocher dans une image")
st.write("Téléchargez une image et ajustez les paramètres pour détecter les cases à cocher.")

# Téléchargement de l'image
uploaded_file = st.file_uploader("Choisir une image...", type=["jpg", "jpeg", "png"])

# Configuration des paramètres de détection
min_size = st.slider("Taille minimale des cases", 10, 100, 15)
max_size = st.slider("Taille maximale des cases", 20, 150, 50)
adaptive_threshold = st.checkbox("Seuillage adaptatif", True)

# Initialiser le détecteur avec les paramètres de l'utilisateur
detector = CheckboxDetector(min_size=min_size, max_size=max_size, adaptive_threshold=adaptive_threshold)

if uploaded_file is not None:
    # Lecture de l'image en utilisant OpenCV
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    # Détection des cases à cocher
    checkboxes = detector.detect_checkboxes(image)
    result_image = visualize_results(image, checkboxes)
    
    # Afficher les résultats
    st.image(result_image, channels="BGR", caption="Résultats de la détection")
    st.write(f"Nombre de cases détectées : {len(checkboxes)}")

    # Afficher les détails des cases détectées
    if checkboxes:
        st.write("Détails des cases détectées :")
        for i, checkbox in enumerate(checkboxes):
            st.write(f"Case {i + 1} : Position = ({checkbox.x}, {checkbox.y}), "
                     f"Taille = ({checkbox.w}x{checkbox.h}), "
                     f"Confiance = {checkbox.confidence:.2f}, "
                     f"Coché = {'Oui' if checkbox.is_checked else 'Non'}, "
                     f"Confiance de marquage = {checkbox.check_confidence:.2f}")