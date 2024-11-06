import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing import image # type: ignore
import numpy as np
from PIL import Image
import json

# Chemin du modèle et du fichier JSON de correspondance des noms
model_path = "./models/latest_checkpoint.h5"
class_mapping_path = "./models/class_mapping.json"  # Chemin vers le fichier de correspondance des indices
species_names_path = "./models/noms_francais.json"  # Chemin vers le fichier avec noms latins et français

# Charger le modèle
model = tf.keras.models.load_model(model_path)

# Charger la correspondance des classes
with open(class_mapping_path, "r") as f:
    class_mapping = json.load(f)

# Charger les noms scientifiques et français
with open(species_names_path, "r") as f:
    species_names = json.load(f)

# Taille de l'image pour la prédiction
image_size = (224, 224)

def predict_species(img, model, class_mapping, species_names):
    # Prétraiter l'image
    img = img.resize(image_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Prédire les probabilités
    predictions = model.predict(img_array)[0]
    
    # Récupérer les 3 classes avec les probabilités les plus élevées
    top_3_indices = np.argsort(predictions)[-3:][::-1]
    top_3_species = [
        {
            "latin_name": class_mapping[str(i)],  # Nom latin
            "french_name": species_names.get(class_mapping[str(i)], "Nom non trouvé"),  # Nom français
            "probability": predictions[i]
        }
        for i in top_3_indices
    ]
    
    return top_3_species

# Interface Streamlit
st.title("Prédiction d'espèce d'arbre")

# Charger une image
uploaded_file = st.file_uploader("Choisissez une image d'arbre...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Afficher l'image chargée en taille réduite
    img = Image.open(uploaded_file)
    st.image(img, caption="Image chargée", width=300)

    # Prédire les 3 meilleures probabilités
    with st.spinner("Prédiction en cours..."):
        top_3_species = predict_species(img, model, class_mapping, species_names)
    
    st.success("Résultats de la prédiction :")
    for species in top_3_species:
        st.write(f"- Nom latin : {species['latin_name']} ({species['french_name']}) : {species['probability']:.2%}")