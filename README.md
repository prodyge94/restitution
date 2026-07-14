# Restitution - Retards des vols US 2015

Ce depot contient les fichiers utiles pour comprendre et presenter le projet de visualisation sur les retards des vols domestiques americains en 2015.

## Contenu

```text
.
├── scripts/
│   ├── 01_nettoyage.py
│   └── 02_analyse.py
├── dashboard/
│   └── index.html
├── documentation/
│   ├── EXPLICATION_PROJET_DASHBOARD.md
│   ├── RAPPORT.md
│   └── GUIDE_TABLEAU.md
└── rendu/
    └── rendu visualisation.pptx
```

## Fichiers importants

- `scripts/01_nettoyage.py` : nettoyage du dataset brut, controle qualite, creation du fichier propre.
- `scripts/02_analyse.py` : analyses principales, KPI, routes aeriennes, compagnies, causes, aeroports.
- `dashboard/index.html` : dashboard final interactif.
- `documentation/EXPLICATION_PROJET_DASHBOARD.md` : explication complete du chemin raw data -> dashboard.
- `rendu/rendu visualisation.pptx` : rendu final PowerPoint.

## Donnees

Les fichiers raw complets ne sont pas inclus dans ce depot pour eviter de pousser un projet trop lourd.

Dataset utilise : Kaggle / USDOT, `2015 Flight Delays and Cancellations`.

Les scripts attendent une structure de type :

```text
data/
├── raw/
│   ├── flights.csv
│   ├── airlines.csv
│   └── airports.csv
└── processed/
```

## Lancer le dashboard

Depuis le dossier `dashboard/` :

```bash
python -m http.server 8765
```

Puis ouvrir :

```text
http://127.0.0.1:8765/
```

## Message principal

Le projet montre que les retards ne sont pas seulement lies aux compagnies ou a la meteo. Certaines routes aeriennes concentrent davantage le risque. La route `SFO -> LAX` ressort comme route prioritaire car elle combine un volume eleve et un taux de retard important.
