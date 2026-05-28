# 🪙 Détection et Classification Automatique de Pièces de Monnaie

![Python](https://img.shields.io/badge/Language-Python-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/Library-OpenCV-green?style=flat-square&logo=opencv)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

Ce projet de vision par ordinateur a pour but de localiser et segmenter des pièces de monnaie à partir d'images complexes, avant d'en déduire leur valeur. 
L'intégralité du pipeline, de la détection géométrique jusqu'à la classification finale, repose exclusivement sur des **algorithmes non supervisés** (traitement du signal classique, sans apprentissage profond).

---

## 📊 1. Bilan Quantitatif des Détections

Le défi principal résidant dans la détection géométrique parfaite des pièces, voici les résultats de notre évaluation menée sur un jeu de **96 images** (comportant **347 pièces** attendues). Nous avons comparé deux algorithmes non supervisés majeurs : la Transformée de Hough et l'algorithme Watershed.

![Tableau récapitulatif des métriques globales](img/tableau_metriques.png)

L'erreur quadratique (RMSE) de **Watershed** se révèle être **près de 8 fois plus faible** que celle de Hough. Il limite considérablement le sur-comptage et s'impose comme l'algorithme le plus fiable pour la suite du traitement.

---

## ⚙️ 2. Détection de Pièces : De la donnée aux algorithmes

### A. Constitution du Dataset & Vérité-Terrain
Pour pouvoir calculer les métriques présentées ci-dessus, une méthodologie rigoureuse a été appliquée :
* **Labellisation :** Utilisation de l'outil graphique **LabelMe** pour détourer manuellement chaque pièce.
* **Format :** Exportation des coordonnées des polygones au format JSON.
* **Structure :** Séparation étanche du dataset en une base de tests et une base de validation.

![Interface de labellisation LabelMe](img/dataset_labelme.png)

### B. Comparaison des Algorithmes (Hough vs Watershed)
Détecter des pièces sur des fonds complexes (comme la peau humaine) génère énormément de bruit lors de la binarisation :

![Limites et difficultés sur fond complexe](img/limites_fond_complexe.png)

Face à ce défi, nos deux approches non supervisées ont réagi très différemment :
* **Transformée de Hough Circulaire :** Très rapide mais ultra-sensible au bruit de texture. L'accumulateur de gradients s'affole sur les fonds complexes, créant de sévères artefacts de multi-détection.
* **Algorithme Watershed (Ligne de partage des eaux) :** Approche par croissance de régions initiée par une transformation des distances. Extrêmement robuste, il réussit à isoler proprement une pièce unique même lorsque les contours sont flous.

![Comparatif des détections : Hough vs Watershed](img/comparaison_hough_watershed.png)

---

## 🎨 3. Détection de la Valeur (Classification Non Supervisée)

Une fois la phase critique de détection validée (via Watershed) et les pièces isolées, le projet procède à une classification de leur valeur. Cette étape non supervisée s'appuie sur une analyse colorimétrique poussée (espaces **HLS** et **HSV**).

### Création des Masques d'Analyse
Pour s'affranchir des variations d'éclairage et analyser précisément les métaux, un pipeline de filtres (CLAHE, lissage) génère des masques spécifiques. 

**Exemple d'extraction des régions sur une pièce bicolore (1€) :**
![Pipeline masque pièce 1 euro](img/pipeline_masque_1euro.png)

**Exemple d'extraction sur une pièce unie (Cuivre) :**
![Pipeline masque pièce cuivre](img/pipeline_masque_cuivre.png)

### Analyse Colorimétrique
* **Pièces bicolores (1€, 2€) :** L'analyse de la **saturation (S)** sur les différents masques (cœur vs anneau) différencie le métal doré (forte saturation) du métal argenté (faible saturation).
* **Pièces unies (Cuivre vs Or) :** L'analyse de la **teinte (H)** permet de discriminer finement les nuances de rouge/brun du cuivre des nuances jaunes des alliages d'or nordique.

![Classification et analyse de la teinte d'un individu en cuivre](img/classification_cuivre.png)

### Résultat Final
Grâce à ce pipeline complet, l'algorithme parvient à encercler la pièce et à afficher sa valeur estimée directement sur l'image source :

![Résultat final de la détection et classification](img/resultat_valeurs.png)

---

## 🚀 4. Installation & Exécution

### Configuration de l'environnement (Windows)
1. Créez un environnement virtuel Python :
   ```cmd
   python -m venv venv

```

2. Activez l'environnement :
```cmd
venv\Scripts\activate

```


3. Installez les dépendances requises :
```cmd
pip install -r requirements.txt

```



### Lancement des modules

Exécutez les scripts depuis la racine du projet :

* **Lancement de la détection de forme (Hough et Watershed) :**
```cmd
python -m src.main

```


* **Test de la classification de valeur :**
```cmd
python -m src.detection_valeur.Detection_valeur

```


* **Calcul des métriques d'évaluation :**
```cmd
python -m src.calcul_metrique.metrique

```



---

*Développé par Louis Chen, Michel Lin et Rayane Kachbi - Projet UE Image 2025/2026.*

```
