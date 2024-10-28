# app.py

import streamlit as st
from msg_parser import MsOxMessage
import os

# Définir le dossier de sortie pour les pièces jointes
output_folder = './attachments'
os.makedirs(output_folder, exist_ok=True)

# Fonction pour analyser un fichier .msg
def parse_msg_file(file):
    msg_obj = MsOxMessage(file)
    msg_properties_dict = msg_obj.get_properties()
    
    # Extraire les informations principales de l'email
    email_info = {
        "Subject": msg_obj.subject,
        "Created Date": msg_obj.created_date,
        "Sent Date": msg_obj.sent_date,
    }
    
    # Extraire les pièces jointes PDF
    attachments = []
    for attachment in msg_obj.attachments:
        attachment_name = attachment.Filename
        if attachment_name.endswith('.pdf'):
            attachment_path = os.path.join(output_folder, attachment_name)
            with open(attachment_path, 'wb') as f:
                f.write(attachment.data)
            attachments.append(attachment_name)
    
    email_info["Attachments"] = attachments
    return email_info

# Interface Streamlit
st.title("Analyseur de Fichiers Email (.msg)")

uploaded_file = st.file_uploader("Téléchargez un fichier .msg", type=["msg"])

if uploaded_file is not None:
    # Analyser le fichier
    email_data = parse_msg_file(uploaded_file)
    
    # Afficher les informations de l'email
    st.subheader("Informations sur l'Email")
    st.write("**Sujet:**", email_data["Subject"])
    st.write("**Date d'Envoi:**", email_data["Sent Date"])
    st.write("**Date de Création:**", email_data["Created Date"])
    
    # Afficher les pièces jointes PDF
    st.subheader("Pièces Jointes PDF")
    if email_data["Attachments"]:
        for attachment in email_data["Attachments"]:
            st.write(f"- {attachment}")
            with open(os.path.join(output_folder, attachment), "rb") as file:
                st.download_button(
                    label=f"Télécharger {attachment}",
                    data=file,
                    file_name=attachment,
                    mime="application/pdf"
                )
    else:
        st.write("Aucune pièce jointe PDF trouvée.")