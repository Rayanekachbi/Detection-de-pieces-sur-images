import cv2
import numpy as np
from itertools import combinations
from src.detection_forme.Watershed import fetchNprocess

# --- Constantes de calibration (Logique Floue) ---
_H_FRONTIERE = 16.0    # Frontière Hue entre Cuivre (<16) et Or (>16)
_SIGMOID_PENTE = 1.2   # Fermeté de la transition
_S_MIN = 35            # Saturation minimale pour considérer une couleur fiable

def extraire_stats_evoluees(image, x, y, r):
    """
    Extrait les statistiques HSV en utilisant CLAHE local et pondération.
    """
    # 1. Extraction de la ROI (Region of Interest)
    y1, y2 = max(0, y-r), min(image.shape[0], y+r)
    x1, x2 = max(0, x-r), min(image.shape[1], x+r)
    roi = image[y1:y2, x1:x2].copy()
    
    if roi.size == 0: return None

    # 2. CLAHE Local (Normalisation indépendante par pièce)
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    roi_norm = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    # 3. Masquage et conversion HSV
    hsv = cv2.cvtColor(roi_norm, cv2.COLOR_BGR2HSV)
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (hsv.shape[1]//2, hsv.shape[0]//2), int(r*0.9), 255, -1)
    
    # 4. Statistiques pondérées (Teinte pondérée par Saturation)
    pixels_h = hsv[:,:,0][mask == 255]
    pixels_s = hsv[:,:,1][mask == 255]
    pixels_v = hsv[:,:,2][mask == 255]
    
    # Seuil V adaptatif
    v_med = float(np.median(pixels_v))
    v_bas = max(20.0, v_med * 0.25)
    
    # Filtre de saturation
    mask_s = pixels_s > _S_MIN
    if np.sum(mask_s) > 10:
        h_moy = np.average(pixels_h[mask_s], weights=pixels_s[mask_s])
        s_moy = np.mean(pixels_s)
    else:
        h_moy = np.mean(pixels_h)
        s_moy = np.mean(pixels_s)
        
    return {"h": h_moy, "s": s_moy, "v_med": v_med, "v_bas": v_bas, "roi_hsv": hsv}

def calculer_score_cuivre(h):
    """ Utilise Sigmoïde + Gaussienne pour différencier Cuivre (1/2/5c) vs Or (10/20/50c) """
    # Sigmoïde : plus H est bas, plus c'est probablement du cuivre (rouge/brun)
    sig = 1.0 / (1.0 + np.exp(_SIGMOID_PENTE * (h - _H_FRONTIERE)))
    # Gaussienne centrée sur le cuivre pur (Hue ~12)
    gau = float(np.exp(-0.5 * ((h - 12.0) / 5.0) ** 2))
    return 0.55 * sig + 0.45 * gau

def identifier_bicolore(stats, x, y, r):
    """ Analyse le contraste centre/bord pour 1€ et 2€ avec des masques stricts """
    hsv = stats['roi_hsv']
    h, w = hsv.shape[:2]
    center_m = np.zeros((h, w), dtype=np.uint8)
    ring_m = np.zeros((h, w), dtype=np.uint8)
    
    seuil_difference = 30    
    taille_centre = 0.30       
    debut_anneau = 0.9        
    fin_anneau = 0.95          
    
    # Création des masques
    cv2.circle(center_m, (w//2, h//2), int(r * taille_centre), 255, -1)
    cv2.circle(ring_m, (w//2, h//2), int(r * fin_anneau), 255, -1)
    cv2.circle(ring_m, (w//2, h//2), int(r * debut_anneau), 0, -1)
    
    # Calcul de la Saturation (S)
    s_center = np.mean(hsv[:,:,1][center_m == 255])
    s_ring = np.mean(hsv[:,:,1][ring_m == 255])
    
    # Différence centre - bord
    diff = s_center - s_ring
    
    is_bicolore = abs(diff) > seuil_difference
    
    if is_bicolore:
        # Si le centre est plus saturé (Or) que le bord (Argent) -> 2€
        # Sinon -> 1€
        return "2€" if diff > 0 else "1€"
        
    return None

import itertools

def resoudre_groupe_par_ratios(circles_indices, circles_data, types_possibles):
    """
    Optimisation combinatoire globale (Ton idée !) :
    Compare toutes les pièces entre elles et trouve le scénario théorique 
    qui minimise l'erreur globale des ratios.
    """
    # Diamètres réels en millimètres (constantes de pourcentage)
    ratios_reels = {
        'or': {"50c": 24.25, "20c": 22.25, "10c": 19.75},
        'cuivre': {"5c": 21.25, "2c": 18.75, "1c": 16.25}
    }
    
    diametres = ratios_reels[types_possibles]
    noms_possibles = list(diametres.keys()) # Ex: ['50c', '20c', '10c']
    
    # On récupère les (index, rayon) des pièces concernées
    pieces = [(i, circles_data[i][2]) for i in circles_indices]
    
    # S'il n'y a qu'une seule pièce, impossible de comparer (Ratio = 1/1)
    if len(pieces) == 1:
        return {pieces[0][0]: f"Individu {types_possibles}"}

    meilleur_scenario = None
    meilleure_erreur = float('inf')

    # 1. On génère TOUS les scénarios possibles (ex: 3 pièces -> 27 possibilités)
    # itertools.product génère (50c, 50c, 50c), (50c, 50c, 20c), etc.
    for scenario_labels in itertools.product(noms_possibles, repeat=len(pieces)):
        erreur_totale_scenario = 0
        
        # 2. On compare chaque pièce avec toutes les autres (Matrice des relations)
        for (idx1, r1), label1 in zip(pieces, scenario_labels):
            for (idx2, r2), label2 in zip(pieces, scenario_labels):
                if idx1 != idx2: # On ne compare pas une pièce avec elle-même
                    
                    # Le pourcentage de taille sur l'image
                    ratio_observe = r1 / r2
                    
                    # Le pourcentage de taille dans la théorie
                    ratio_theorique = diametres[label1] / diametres[label2]
                    
                    # On additionne l'erreur
                    erreur_totale_scenario += abs(ratio_observe - ratio_theorique)
        
        # 3. Si ce scénario est le plus proche de la réalité, on le sauvegarde
        if erreur_totale_scenario < meilleure_erreur:
            meilleure_erreur = erreur_totale_scenario
            meilleur_scenario = scenario_labels

    # 4. On assigne les valeurs gagnantes aux pièces
    resultats = {}
    for (idx, _), label in zip(pieces, meilleur_scenario):
        resultats[idx] = label
        
    return resultats

import cv2
import numpy as np

# --- Liste des images à tester ---
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
        chemin_dossier + "piece_140.jpg"

    ]

for img_path in images_test:
    # 1. Récupération de l'image et des cercles détectés
    image, circles = fetchNprocess(img_path, False)
    
    if image is None:
        continue

    print(f"\n--- Analyse de : {img_path} ---")

    indices_cuivre = []
    indices_or = []
    final_labels = {}
    
    # On garde une trace des couleurs pour l'affichage (facultatif)
    draw_colors = {}

    # 2. Classification individuelle (Bicolore et Score Flou)
    for i, (x, y, r) in enumerate(circles):
        stats = extraire_stats_evoluees(image, x, y, r)
        if stats is None: continue
        
        # Priorité 1 : Détection bicolore (1€ / 2€)
        label_bicolore = identifier_bicolore(stats, x, y, r)
        
        if label_bicolore:
            final_labels[i] = label_bicolore
            draw_colors[i] = (255, 200, 0) # Couleur spécifique bicolore
        else:
            # Priorité 2 : Séparation Cuivre vs Or via logique floue (Sigmoïde)
            score_cuivre = calculer_score_cuivre(stats['h'])
            if score_cuivre > 0.5:
                indices_cuivre.append(i)
                draw_colors[i] = (0, 0, 255)   # Rouge pour cuivre
            else:
                indices_or.append(i)
                draw_colors[i] = (0, 215, 255) # Jaune pour or

    # 3. Classification de groupe par ratios de taille (10c/20c/50c et 1c/2c/5c)
    if indices_cuivre:
        final_labels.update(resoudre_groupe_par_ratios(indices_cuivre, circles, 'cuivre'))
    if indices_or:
        final_labels.update(resoudre_groupe_par_ratios(indices_or, circles, 'or'))

    # 4. Affichage des résultats sur l'image
    for i, (x, y, r) in enumerate(circles):
        valeur = final_labels.get(i, "Inconnu")
        color = draw_colors.get(i, (128, 128, 128))
        
        # Dessiner le cercle et la valeur
        cv2.circle(image, (x, y), r, color, 3)
        cv2.putText(image, valeur, (x - 20, y - r - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        print(f"  Pièce {i+1}: {valeur}")

    # 5. Rendu visuel
    cv2.imshow("Detection de Valeurs Optimisee", image)
    
    # Attend une touche pour passer à l'image suivante, 'q' pour quitter
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
print("\nAnalyse terminée.")