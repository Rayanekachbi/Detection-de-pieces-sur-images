# 🪙 Détection et Classification Automatique de Pièces de Monnaie

![Python](https://img.shields.io/badge/Language-Python-blue?style=flat-square\&logo=python)
![OpenCV](https://img.shields.io/badge/Library-OpenCV-green?style=flat-square\&logo=opencv)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

---

# 🏗️ Architecture et Résultat Final

Ce projet de vision par ordinateur a pour objectif de :

* localiser automatiquement des pièces de monnaie,
* segmenter précisément leurs contours,
* classifier leur valeur à partir de caractéristiques colorimétriques avancées.

Le projet compare deux approches majeures de segmentation géométrique :

* **Transformée de Hough**
* **Algorithme Watershed**

avant d’effectuer une classification basée sur l’analyse des couleurs dans l’espace HSV.

![Résultat final de détection](img/resultat_final.png)

---

# 🎯 1. Constitution du Dataset & Vérité-Terrain

Afin de valider scientifiquement les algorithmes, une méthodologie rigoureuse a été appliquée.

## 📌 Labellisation des données

* Utilisation de l’outil graphique **LabelMe**
* Détourage manuel de chaque pièce
* Création d’une vérité-terrain (*ground truth*)

## 📂 Format des annotations

Les annotations sont exportées au format :

```txt id="f5c73x"
JSON
```

avec les coordonnées polygonales de chaque pièce.

## 🧪 Séparation du dataset

Le dataset est séparé en :

* une base de test
* une base de validation

afin d’éviter toute fuite d’apprentissage.

![Interface de labellisation LabelMe](img/dataset_labelme.png)

---

# ⚙️ 2. Pipeline de Traitement d'Image

## 🔄 A. Prétraitement commun

Pour limiter :

* les variations d’éclairage,
* les ombres,
* les reflets métalliques,

les images passent par plusieurs étapes de prétraitement.

### Étapes appliquées

1. **Redimensionnement**

   * standardisation des calculs

2. Extraction du **canal L** de l’espace colorimétrique **HLS**

3. **CLAHE**

   * égalisation d’histogramme adaptative
   * amélioration des contrastes locaux

4. Double filtrage :

   * flou médian
   * flou gaussien

afin de supprimer le bruit haute fréquence.

![Pipeline de prétraitement](img/pipeline_pretraitement.png)

---

## 🔍 B. Inférence & Détection des contours

### 🟠 Transformée de Hough Circulaire

Approche basée sur :

* un accumulateur de gradients,
* la recherche géométrique directe de cercles.

### Avantages

* très rapide
* simple à implémenter

### Inconvénients

* extrêmement sensible au bruit
* nombreuses multi-détections

---

### 🔵 Algorithme Watershed

Approche fondée sur :

* la croissance de régions,
* une transformation des distances,
* un seuillage préalable.

### Avantages

* excellente séparation des objets collés
* segmentation stable
* meilleure robustesse géométrique

### Inconvénients

* léger sous-comptage possible en faible contraste

---

# 📊 3. Analyse Comparative & Erreurs Graves

L’évaluation a été réalisée sur :

* **96 images**
* **347 pièces attendues**

---

## ❌ Le problème de sur-comptage de Hough

La transformée de Hough génère de nombreux artefacts sur les textures complexes.

Exemple critique :

* **142 cercles détectés**
* pour une seule pièce réelle
* sur l’image `piece_093`

![Artefacts de multi-détection avec Hough](img/hough_multidetection.png)

---

## ✅ Watershed : stabilité et précision

L’algorithme Watershed conserve :

* une vraie cohérence géométrique,
* une séparation propre des composantes connexes,
* une forte stabilité sur les scènes complexes.

![Segmentation propre via Watershed](img/watershed_segmentation.png)

---

# 📈 Bilan Analytique des Métriques

| Métrique                             | Transformée de Hough | Watershed ✅ |
| ------------------------------------ | -------------------: | ----------: |
| **Total pièces détectées sur 347**           |           728 pièces |  256 pièces |
| **MAE** *(Erreur Absolue Moyenne)*   |                 6.53 |    **0.95** |
| **RMSE** *(Root Mean Squared Error)* |                20.09 |    **2.56** |

---

## 🧠 Conclusion expérimentale

L’erreur quadratique moyenne (**RMSE**) de Watershed est :

# **7,8 fois plus faible**

que celle obtenue avec la transformée de Hough.

Cela confirme clairement la supériorité de Watershed pour ce problème de segmentation.

![Graphique comparatif des performances](img/bilan_metriques.png)

---

# 🎨 4. Classification et Détection de la Valeur

Une fois les pièces segmentées, leur valeur est estimée via une analyse dans l’espace colorimétrique **HSV**.

---

## 🪙 Pièces bicolores (1€ / 2€)

Méthode utilisée :

* génération de deux masques imbriqués :

  * cœur central
  * anneau externe

### Critère discriminant

Analyse de la :

```txt id="0c5qvw"
Saturation (S)
```

afin de distinguer :

* métal doré → forte saturation
* métal argenté → faible saturation

---

## 🟠 Pièces unies (Cuivre / Or nordique)

Analyse basée sur :

```txt id="xvwf3x"
Teinte (H)
```

pour différencier :

* les nuances rouge/brun du cuivre,
* des nuances jaunes des alliages dorés.

![Analyse colorimétrique HSV](img/classification_hsv.png)

---

# 🚀 5. Installation & Exécution

## 📋 Configuration de l’environnement (Windows)

### 1. Création d’un environnement virtuel

```cmd id="s6o5gq"
python -m venv venv
```

---

### 2. Activation de l’environnement

```cmd id="0ryx7v"
venv\Scripts\activate
```

---

### 3. Installation des dépendances

```cmd id="n6cvx7"
pip install -r requirements.txt
```

---

# ▶️ Lancement des modules

Les scripts doivent être exécutés depuis la racine du projet.

---

## 🔍 Détection globale

```cmd id="qf1cwe"
python -m src.main
```

---

## 🪙 Classification des valeurs

```cmd id="n0txna"
python -m src.detection_valeur.Detection_valeur
```

---

## 📊 Calcul des métriques

```cmd id="fr3p4x"
python -m src.calcul_metrique.metrique
```

---

# 👥 Équipe Projet

Développé par :

* Louis Chen
* Michel Lin
* Rayane Kachbi

Projet UE Image — 2025/2026.

---
