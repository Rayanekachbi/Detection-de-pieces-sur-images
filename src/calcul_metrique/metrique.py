import numpy as np
import os
import math
import cv2
import json

from src.detection_forme.Watershed import fetchNprocess

def charger_rayons_depuis_json(chemin_json, scale):
    """
    Lit le fichier JSON LabelMe, extrait les formes et convertit leurs coordonnées.
    Accepte les cercles ET les polygones pour ne fausser aucun comptage.
    """
    rayons_gt = []
    
    if not os.path.exists(chemin_json):
        print(f"Fichier JSON introuvable : {chemin_json}")
        return None

    with open(chemin_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Vérification optionnelle / Affichage du champ imagePath pour débogage
    image_path_json = data.get("imagePath", "")
    
    for shape in data.get("shapes", []):
        type_forme = shape.get("shape_type")
        points = shape.get("points", [])
        
        if type_forme == "circle" and len(points) == 2:
            # LabelMe stocke 2 points pour un cercle : [centre, point_sur_le_bord]
            p1 = points[0]
            p2 = points[1]
            rayon_original = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            rayon_ajuste = rayon_original * scale
            rayons_gt.append(rayon_ajuste)
        else:
            # C'est un polygone (ou autre chose). On l'ajoute à la liste avec 
            # une valeur de 0.0 pour qu'il soit bien compté dans le total des pièces !
            rayons_gt.append(0.0)
                
    return rayons_gt, image_path_json

def executer_evaluation_metrique(chemin_image, chemin_json, fichier_txt):
    """
    Effectue l'évaluation (comptage + rayons) et écrit simultanément 
    dans la console et dans le fichier TXT.
    Retourne (nb_reel, nb_detecte) pour alimenter les statistiques globales.
    """

    log_image = ""

    print(f"\n---------------------------------------------------")
    print(f"\n===================================================")
    print(f"Analyse de l'image : {os.path.basename(chemin_image)}")
    
    log_image += f"\n---------------------------------------------------\n"
    log_image += f"\n===================================================\n"
    log_image += f"Analyse de l'image : {os.path.basename(chemin_image)}\n"

    # 1. Appel de votre fonction de détection robuste
    image_traitee, coordonnees_cercles = fetchNprocess(chemin_image)
    

    if image_traitee is None:
        msg_error = f"Erreur : Impossible de charger l'image {chemin_image}\n"
        print(msg_error, end="")
        fichier_txt.write(log_image + msg_error)
        return 0, 0

    # Recalcul manuel du scale appliqué par fetchNprocess pour ajuster le JSON
    # fetchNprocess utilise norm = 500 et redimensionne selon la largeur d'origine
    image_originale_brute = cv2.imread(chemin_image)
    if image_originale_brute is not None:
        scale = 500.0 / image_originale_brute.shape[1]
    else:
        msg_error = f"Erreur lors de la lecture brute de l'image pour l'échelle.\n"
        print(msg_error, end="")
        fichier_txt.write(log_image + msg_error)
        return 0, 0


    # 2. Chargement et vérification du fichier JSON de vérité terrain
    donnees_json = charger_rayons_depuis_json(chemin_json, scale)
    if donnees_json is None:
        msg_error = "Évaluation annulée pour cette image (JSON manquant ou incorrect).\n"
        print(msg_error, end="")
        fichier_txt.write(log_image + msg_error)
        return 0, 0
            
    rayons_verite_terrain, image_path_json = donnees_json
    
    # Vérification : est-ce que le nom de fichier dans 'imagePath' correspond à l'image testée ?
    nom_image_attendu = os.path.splitext(os.path.basename(chemin_image))[0]
    nom_image_json = os.path.splitext(os.path.basename(image_path_json.replace("\\", "/")))[0] # Nettoyage des antislashs Windows
    
    if nom_image_attendu.lower() != nom_image_json.lower():
        log_image += f"ATTENTION : Incohérence détectée ! \n   -> Fichier analysé : {nom_image_attendu} \n   -> Lié dans le JSON : {nom_image_json}\n"
        print(f"ATTENTION : Incohérence détectée !")
        print(f"   -> Fichier analysé : {nom_image_attendu}")
        print(f"   -> Lié dans le JSON : {nom_image_json}")
    else:
        log_image += f"Cohérence fichier OK (Correspondance validée avec imagePath).\n"
        print(f"Cohérence fichier OK (Correspondance validée avec imagePath).")

    
    # 3. Extraction des rayons prédits (r)
    rayons_predits = []
    
    # Comme fetchNprocess renvoie une simple liste de tuples [(x,y,r), ...], 
    # une simple boucle suffit !
    if coordonnees_cercles is not None:
        for cercle in coordonnees_cercles:
            if len(cercle) >= 3:
                rayons_predits.append(float(cercle[2])) # Le rayon est l'index 2
    else: 
        # Si l'image n'a pas pu être chargée
        msg_error = "Erreur : Impossible de récupérer les données de détection.\n"
        print(msg_error, end="")
        fichier_txt.write(log_image + msg_error)
        return len(rayons_verite_terrain), 0
            
    nb_reels = len(rayons_verite_terrain)
    nb_detectes = len(rayons_predits)


    etats_metriq = (
        f"-> Pièces réelles (Vérité Terrain JSON) : {len(rayons_verite_terrain)}\n"
        f"-> Pièces détectées par l'algorithme : {len(rayons_predits)}\n"
        f"-> Écart (Erreur de comptage)         : {nb_detectes - nb_reels:+d}\n"
    )
    print(etats_metriq, end="")
    log_image += etats_metriq
    


    # Écriture définitive dans le fichier texte pour cette image
    fichier_txt.write(log_image)
    return nb_reels, nb_detectes



# --- Zone de Test Automatique sur tout le dossier ---
if __name__ == "__main__":
    # Dossier contenant votre base d'images
    # dossier_test = "Test"
    # dossier_test_json = "testValidationJson"
    dossier_test = "Dataset_Propre/base_images"
    dossier_test_json = "Dataset_Propre/json_validation"

    nom_fichier_rapport = "rapport_evaluation_Classific_test.txt"

    if not os.path.exists(dossier_test):
        print(f"Erreur : Le dossier '{dossier_test}' n'existe pas.")
    else:
        # Liste de toutes les extensions d'images acceptées
        extensions_images = ('.jpg', '.jpeg', '.png')
        
        # Récupérer tous les fichiers du dossier Test
        fichiers = os.listdir(dossier_test)
        fichiers_images = [f for f in fichiers if f.lower().endswith(extensions_images)]
        
        print(f"Début de l'évaluation globale sur le dossier '{dossier_test}'")
        print(f"{len(fichiers_images)} image(s) trouvée(s).")
        print(f"Les résultats seront sauvegardés dans : {nom_fichier_rapport}")
        
        # Listes pour stocker les comptes de chaque image afin d'appliquer la formule globale
        liste_verites = []
        liste_predictions = []
        images_evaluees = 0

        # Ouverture du fichier TXT avec encodage UTF-8
        with open(nom_fichier_rapport, "w", encoding="utf-8") as fichier_txt:
            # En-tête du fichier texte
            fichier_txt.write("==================================================\n")
            fichier_txt.write("      RAPPORT D'ÉVALUATION DE LA MÉTRIQUE         \n")
            fichier_txt.write("==================================================\n")
            fichier_txt.write(f"Nombre total d'images traitées : {len(fichiers_images)}\n")


            for fichier_img in fichiers_images:
                chemin_img_complet = os.path.join(dossier_test, fichier_img)
                
                # Déduction automatique du nom du fichier JSON correspondant
                nom_sans_ext, _ = os.path.splitext(fichier_img)
                fichier_json = nom_sans_ext + ".json"
                chemin_json_complet = os.path.join(dossier_test_json, fichier_json)
                
                # Gestion automatique des doublons "bis" : 
                # ex: "imagebis.jpg" -> cherche "imagebis.json"
                if os.path.exists(chemin_json_complet):
                    nb_r, nb_d = executer_evaluation_metrique(chemin_img_complet, chemin_json_complet, fichier_txt)
                    
                    # On stocke les résultats pour le calcul final global
                    liste_verites.append(nb_r)
                    liste_predictions.append(nb_d)
                    images_evaluees += 1
                else:
                    msg_saute_img = f"\nImage sautée : {fichier_img} (Aucun fichier JSON '{fichier_json}' associé trouvé).\n"
                    print(msg_saute_img, end="")
                    fichier_txt.write(msg_saute_img)

            # --- Section Bilan Global (Idéal pour vos Slides !) ---
            # --- SECTION BILAN GLOBAL (Calculs basés sur le cours YouTube à 10:02) ---
            if images_evaluees > 0:
                y = np.array(liste_predictions)      # Tableau des prédictions [y1, y2, ..., yN]
                y_chapeau = np.array(liste_verites)  # Tableau des vérités terrains [ŷ1, ŷ2, ..., ŷN]
                
                # Calcul de la MAE, MSE et RMSE globales (par rapport au nombre d'images N)
                mae_globale = np.mean(np.abs(y - y_chapeau))
                mse_globale = np.mean((y - y_chapeau) ** 2)
                rmse_globale = np.sqrt(mse_globale)
                
                total_reelles = int(np.sum(y_chapeau))
                total_detectees = int(np.sum(y))

                bilan_global = (
                    f"\n===================================================\n"
                    f"         BILAN GLOBAL        \n"
                    f"===================================================\n"
                    f"Nombre d'images évaluées (N)   : {images_evaluees}\n"
                    f"Total pièces attendues          : {total_reelles}\n"
                    f"Total pièces détectées par Watershed: {total_detectees}\n"
                    f"---------------------------------------------------\n"
                    f"MAE  (Erreur Absolue Moyenne)   : {mae_globale:.2f} pièces/image\n"
                    f"MSE  (Erreur Quadratique Moyenne): {mse_globale:.2f} (pièces)^2\n"
                    f"RMSE (Root Mean Squared Error)  : {rmse_globale:.2f} pièces/image\n"
                    f"===================================================\n"
                )
                print(bilan_global)
                fichier_txt.write(bilan_global)
            else:
                print("\nAucune image n'a pu être évaluée avec son fichier JSON.")
        
        print(f"\nEvaluation terminée ! \nLe fichier '{nom_fichier_rapport}' a été généré et enregistrer avec succès. \n")