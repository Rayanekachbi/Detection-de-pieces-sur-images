import cv2
import matplotlib.pyplot as plt
import os

# --- IMPORTATION DES DEUX MÉTHODES ---
from src.detection_forme.Hough import fetchNprocess as hough_process
from src.detection_forme.Watershed import fetchNprocess as watershed_process

if __name__ == "__main__":
    
    # --- LISTE DES IMAGES ---
    chemin_dossier = "Dataset_Propre/base_images/"
    
    images_test = [
        chemin_dossier + "piece_001.jpeg",
        chemin_dossier + "piece_002.jpeg",
        chemin_dossier + "piece_003.jpeg",
        chemin_dossier + "piece_004.jpg",
        chemin_dossier + "piece_005.jpeg",
        chemin_dossier + "piece_006.jpg",
        chemin_dossier + "piece_007.jpg",
        chemin_dossier + "piece_008.jpg",
        chemin_dossier + "piece_009.jpeg",
        chemin_dossier + "piece_010.jpg"
    ]

    print("Lancement de la comparaison visuelle (Fermez la fenêtre Matplotlib pour passer à l'image suivante)")

    for img_path in images_test:
        
        if not os.path.exists(img_path):
            print(f"Erreur : L'image {img_path} est introuvable.")
            continue

        print(f"Analyse de : {os.path.basename(img_path)}...")

        # 1. Calculs (sans ouvrir de fenêtres OpenCV)
        img_hough, cercles_hough = hough_process(img_path)
        img_water, cercles_water = watershed_process(img_path, show=False)

        nb_hough = len(cercles_hough) if cercles_hough else 0
        nb_water = len(cercles_water) if cercles_water else 0

        # 2. Conversion des couleurs de BGR (OpenCV) vers RGB (Matplotlib)
        if img_hough is not None:
            img_hough_rgb = cv2.cvtColor(img_hough, cv2.COLOR_BGR2RGB)
        if img_water is not None:
            img_water_rgb = cv2.cvtColor(img_water, cv2.COLOR_BGR2RGB)

        # 3. Création de l'interface Matplotlib "Jolie" (1 ligne, 2 colonnes)
        # figsize=(14, 7) donne une belle fenêtre rectangulaire
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        
        # --- Colonne 1 : HOUGH ---
        if img_hough is not None:
            ax1.imshow(img_hough_rgb)
            ax1.set_title(f"Transformée de Hough\n{nb_hough} pièce(s) détectée(s)", 
                          fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
        ax1.axis('off') # Supprime le contour et les coordonnées X/Y moches

        # --- Colonne 2 : WATERSHED ---
        if img_water is not None:
            ax2.imshow(img_water_rgb)
            ax2.set_title(f"Watershed\n{nb_water} pièce(s) détectée(s)", 
                          fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
        ax2.axis('off')

        # Titre général en haut
        nom_image = os.path.basename(img_path)
        fig.suptitle(f"Comparaison de la détection de formes sur : {nom_image}", 
                     fontsize=18, fontweight='bold', y=0.98)

        # Ajuste les marges automatiquement pour un rendu propre
        plt.tight_layout()

        # 4. Affichage
        # plt.show() bloque le code. Dès que tu fermeras la fenêtre, le script passera à l'image 2 !
        plt.show()

    print("\nToutes les images ont été traitées !")