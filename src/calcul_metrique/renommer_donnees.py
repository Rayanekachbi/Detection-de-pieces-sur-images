import os
import glob
import shutil
import json
import random

# --- 1. CONFIGURATION DES DOSSIERS SOURCES ---
# Ceci était des chemins qui n'existent plus vers les fichiers non organisés
DOSSIER_IMAGES_SOURCE = "ProjetImage/base_images" 
DOSSIER_JSON_SOURCE = "ProjetImage/BaseImageJSON"

# --- 2. CONFIGURATION DE LA DESTINATION ---
DOSSIER_DESTINATION = "Dataset_Propre"
PREFIXE_NOM = "piece_" 
RATIO_TEST = 0.5 # 50% test, 50% validation

def preparer_dossiers():
    dossiers_a_creer = ['base_images', 'json_validation', 'json_test']
    for dossier in dossiers_a_creer:
        chemin = os.path.join(DOSSIER_DESTINATION, dossier)
        os.makedirs(chemin, exist_ok=True)

def nettoyer_et_separer():
    preparer_dossiers()
    
    # 1. Lister tous les fichiers JSON du dossier source JSON
    fichiers_json = glob.glob(os.path.join(DOSSIER_JSON_SOURCE, "*.json"))
    paires_valides = []

    # 2. Trouver l'image correspondante dans le dossier source Images
    for chemin_json in fichiers_json:
        nom_base = os.path.splitext(os.path.basename(chemin_json))[0]
        
        # On cherche l'image peu importe son extension (.jpg, .jpeg, .JPG, .png)
        extensions_possibles = ['.jpg', '.jpeg', '.JPG', '.png']
        chemin_img = None
        
        for ext in extensions_possibles:
            test_img = os.path.join(DOSSIER_IMAGES_SOURCE, nom_base + ext)
            if os.path.exists(test_img):
                chemin_img = test_img
                break
                
        if chemin_img:
            paires_valides.append((chemin_img, chemin_json))
        else:
            print(f"⚠️ Image introuvable pour le JSON : {nom_base}.json")

    print(f"✅ {len(paires_valides)} paires (Image + JSON) trouvées et prêtes à être traitées.")

    # 3. Mélanger les données aléatoirement pour la séparation
    random.seed(42) # Garde le même mélange si tu relances le script
    random.shuffle(paires_valides)

    # 4. Déterminer l'index de coupure (50/50)
    index_coupure = int(len(paires_valides) * (1 - RATIO_TEST))
    
    # 5. Traiter, renommer et ranger chaque paire
    for index, (chemin_img, chemin_json) in enumerate(paires_valides):
        
        # Le nouveau nom unifié (ex: piece_042)
        nouveau_nom_base = f"{PREFIXE_NOM}{index + 1:03d}"
        ext_img = os.path.splitext(chemin_img)[1] # Récupère l'extension de l'image
        nouveau_nom_image = nouveau_nom_base + ext_img
        
        # A. Déplacer l'image dans le dossier unique "base_images"
        nouveau_chemin_img = os.path.join(DOSSIER_DESTINATION, 'base_images', nouveau_nom_image)
        shutil.copy2(chemin_img, nouveau_chemin_img)

        # B. Déterminer dans quel dossier JSON on va ranger ce fichier
        dossier_json_cible = 'json_validation' if index < index_coupure else 'json_test'
        nouveau_chemin_json = os.path.join(DOSSIER_DESTINATION, dossier_json_cible, nouveau_nom_base + ".json")

        # C. Lire le JSON, le modifier, et le sauvegarder à sa nouvelle place
        with open(chemin_json, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
        
        # MODIFICATION CRUCIALE POUR LABELME :
        # On dit au JSON de remonter d'un dossier (..) puis d'aller dans base_images
        # On utilise des doubles antislash ou des slash selon les OS, LabelMe gère bien les slash (/)
        data_json['imagePath'] = f"../base_images/{nouveau_nom_image}"
        
        with open(nouveau_chemin_json, 'w', encoding='utf-8') as f:
            json.dump(data_json, f, indent=2)

    print(f"\nTerminé ! Ton architecture est prête dans le dossier '{DOSSIER_DESTINATION}'.")
    print(f"-> {len(paires_valides)} images dans 'base_images'")
    print(f"-> {index_coupure} JSON dans 'json_validation'")
    print(f"-> {len(paires_valides) - index_coupure} JSON dans 'json_test'")

if __name__ == "__main__":
    nettoyer_et_separer()