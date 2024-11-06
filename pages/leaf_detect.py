import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image # type: ignore
import numpy as np
from PIL import Image
import json
import os

model_path = "./models/latest_checkpoint.h5"
class_mapping_path = "./models/class_mapping.json"
species_names_path = "./models/noms_francais.json" 
test_image_path = "./assets/test_image.jpg"

model = tf.keras.models.load_model(model_path)
with open(class_mapping_path, "r") as f:
    class_mapping = json.load(f)

with open(species_names_path, "r") as f:
    species_names = json.load(f)

image_size = (224, 224)

def predict_species(img, model, class_mapping, species_names):
    img = img.resize(image_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    predictions = model.predict(img_array)[0]
    top_3_indices = np.argsort(predictions)[-3:][::-1]
    top_3_species = [
        {
            "latin_name": class_mapping[str(i)],
            "french_name": species_names.get(class_mapping[str(i)], "Nom non trouvé"),
            "probability": predictions[i]
        }
        for i in top_3_indices
    ]
    
    return top_3_species

st.title("Prédiction d'espèce d'arbre")
uploaded_file = st.file_uploader("Choisissez une image d'arbre...", type=["jpg", "jpeg", "png"])
use_test_image = st.button("Utiliser une image d'essai")

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption="Image chargée", width=300)
elif use_test_image and os.path.exists(test_image_path):
    img = Image.open(test_image_path)
    st.image(img, caption="Image d'essai", width=300)
else:
    st.warning("Veuillez télécharger une image ou utiliser l'image d'essai.")

if 'img' in locals():
    with st.spinner("Prédiction en cours..."):
        top_3_species = predict_species(img, model, class_mapping, species_names)
    
    st.success("Résultats de la prédiction :")
    for species in top_3_species:
        st.write(f"- Nom latin : {species['latin_name']} ({species['french_name']}) : {species['probability']:.2%}")