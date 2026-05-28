----------------------------------------
INSTALLATION
----------------------------------------
(commandes pour Windows)
Créer un environnement virtuel :
    python -m venv venv

Activer l’environnement (Windows) :
    venv\Scripts\activate

Installer les dépendances :
    pip install -r requirements.txt


----------------------------------------
EXECUTION
----------------------------------------
Depuis la racine du projet :

1) Lancer les deux algorithmes de detection de forme :
    python -m src.main   

2) Tester détection de valeur :
    python -m src.detection_valeur.Detection_valeur

3) Tester les métriques :
    python -m src.calcul_metrique.metrique

----------------------------------------
ARBORESCENCE
----------------------------------------

.
├── README.txt
├── requirements.txt
├── Hough_rapport_evaluation.txt
├── Watershed_rapport_evaluation.txt
|
├── Dataset_Propre/
│   ├── base_images/
│   │   ├── piece_001.jpeg
│   │   ├── piece_002.jpeg
│   │   ├── piece_003.jpeg
│   │   └── ...
│   ├── json_test/
│   │   ├── piece_097.json
│   │   ├── piece_098.json
│   │   ├── piece_099.json
│   │   └── ...
│   └── json_validation/
│       ├── piece_001.json
│       ├── piece_002.json
│       ├── piece_003.json
│       └── ...
└── src/
    ├── main.py
    ├── calcul_metrique/
    │   ├── metrique.py
    │   └── renommer_donnees.py
    ├── detection_forme/
    │   ├── Hough.py
    │   └── Watershed.py
    └── detection_valeur/
        └── Detection_valeur.py