import pickle

with open('kmeans_nlp.pkl', 'rb') as fichier:
    kmeans_charge = pickle.load(fichier)

with open('count_vectorizer.pkl', 'rb') as fichier:
    C_V_charge = pickle.load(fichier)

with open('iso_forest_trades.pkl', 'rb') as fichier:
    clf_charge = pickle.load(fichier)

with open('scaler.pkl', 'rb') as fichier:
   scaler_charge = pickle.load(fichier)