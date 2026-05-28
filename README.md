# 🪙 Détection et Classification Automatique de Pièces de Monnaie

![Python](https://img.shields.io/badge/Language-Python-blue?style=flat-square\&logo=python)
![OpenCV](https://img.shields.io/badge/Library-OpenCV-green?style=flat-square\&logo=opencv)
![Status](https://img.shields.io/badge/Status-Completed-success?style=flat-square)

Ce projet de vision par ordinateur a pour but de localiser, segmenter et classifier des pièces de monnaie à partir d'images complexes. Il implémente et compare deux grandes approches de segmentation géométrique (**Transformée de Hough** vs **Algorithme Watershed**) avant de procéder à une classification de valeur basée sur une analyse colorimétrique avancée.

![Résultat final de la détection et classification](img/resultat_valeurs.png)

---

# 🎯 1. Constitution du Dataset & Vérité-Terrain

Afin de valider scientifiquement nos algorithmes, une méthodologie rigoureuse a été appliquée :

* **Labellisation :** Utilisation de l'outil graphique **LabelMe** pour détourer manuellement chaque pièce (*vérité-terrain*).
* **Format :** Exportation des coordonnées polygonales au format JSON.
* **Structure :** Séparation stricte entre base de tests et base de validation.

![Interface de labellisation LabelMe](img/dataset_labelme.png)

---

# ⚙️ 2. Pipeline de Traitement d'Image et Extraction

## 🔄 A. Prétraitement et Création des Masques

Pour s'affranchir :

* des variations d’éclairage,
* des ombres portées,
* des reflets métalliques,

chaque image subit plusieurs traitements successifs afin d’isoler correctement les pièces.

### Étapes appliquées

1. Extraction du **canal L** de l’espace colorimétrique **HLS**
2. Égalisation adaptative (**CLAHE**)
3. Génération d’un masque binaire
4. Isolation de la pièce sur fond noir

---

## 🪙 Exemple : pièce bicolore (1€)

![Pipeline masque pièce 1 euro](img/pipeline_masque_1euro.png)

---

## 🟠 Exemple : pièce cuivre

![Pipeline masque pièce cuivre](img/pipeline_masque_cuivre.png)

---

## 🔍 B. Inférence & Détection des contours

La détection des contours circulaires devient difficile lorsque :

* le fond est texturé,
* la pièce est tenue en main,
* ou que des reflets perturbent la binarisation.

![Limites et difficultés sur fond complexe](img/limites_fond_complexe.png)

---

### 🟠 Transformée de Hough Circulaire

Méthode basée sur :

* un accumulateur de gradients,
* la recherche géométrique de cercles.

### Avantages

* rapide
* simple à implémenter

### Inconvénients

* très sensible au bruit
* nombreux faux positifs
* multi-détections fréquentes

---

### 🔵 Algorithme Watershed

Méthode basée sur :

* une croissance de régions,
* une transformation des distances,
* un seuillage préalable.

### Avantages

* robuste sur les objets collés
* meilleure stabilité géométrique
* segmentation plus propre

### Inconvénients

* léger sous-comptage possible en faible contraste

---

# 🥊 3. Analyse Comparative & Erreurs Graves

L’évaluation a été menée sur :

* **96 images**
* **347 pièces attendues**

L’un des constats majeurs du projet concerne l’instabilité importante de la Transformée de Hough sur les textures complexes.

Dans de nombreux cas, Hough génère :

* plusieurs dizaines de cercles parasites,
* des artefacts de contours,
* un fort sur-comptage.

À l’inverse, Watershed parvient à isoler proprement les composantes connexes.

![Comparatif des détections : Hough vs Watershed](img/comparaison_hough_watershed.png)

---

# 📊 Bilan Analytique des Métriques

L’erreur quadratique moyenne (**RMSE**) obtenue avec Watershed est :

# **près de 8 fois plus faible**

que celle de la Transformée de Hough.

Cela confirme clairement la supériorité de Watershed pour cette tâche de segmentation.

![Tableau récapitulatif des métriques globales](img/tableau_metriques.png)

---

# 🎨 4. Classification et Détection de la Valeur

Une fois les pièces segmentées, la valeur est déterminée grâce à une analyse colorimétrique dans l’espace **HSV**.

---

## 🪙 Pièces bicolores (1€ / 2€)

Méthode utilisée :

* création de deux masques imbriqués :

  * cœur central
  * anneau externe

### Critère discriminant

Analyse de la :

```txt id="a7pf8x"
Saturation (S)
```

pour différencier :

* métal doré → forte saturation
* métal argenté → faible saturation

---

## 🟠 Pièces unies (Cuivre / Or nordique)

Méthode basée sur :

```txt id="9w4kcp"
Teinte (H)
```

afin de distinguer :

* les nuances rouge/brun du cuivre,
* des nuances jaunes des alliages dorés.

![Classification et analyse HSV du cuivre](img/classification_cuivre.png)

---

# 🚀 5. Installation & Exécution

## 📋 Configuration de l’environnement (Windows)

### 1. Création d’un environnement virtuel

```cmd id="e7s8zq"
python -m venv venv
```

---

### 2. Activation de l’environnement

```cmd id="n3w8fz"
venv\Scripts\activate
```

---

### 3. Installation des dépendances

```cmd id="xtd5m4"
pip install -r requirements.txt
```

---

# ▶️ Lancement des modules

Exécutez les scripts depuis la racine du projet.

---

## 🔍 Détection de formes (Hough & Watershed)

```cmd id="t0j8vn"
python -m src.main
```

---

## 🪙 Classification des valeurs

```cmd id="3k7xvw"
python -m src.detection_valeur.Detection_valeur
```

---

## 📊 Calcul des métriques

```cmd id="c2vx8n"
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

