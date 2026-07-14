# Guide Tableau - Version routes aeriennes

Ce guide sert a construire les visualisations de la nouvelle version du projet, avec les **routes aeriennes** comme axe important.

Toutes les donnees sont dans `data/processed/`.

---

## 1. Connexion

Dans Tableau Public :

1. Connexion -> fichier texte.
2. Charger les CSV depuis `data/processed/`.
3. Utiliser chaque CSV comme source separee.

---

## 2. Visualisations conseillees

### F1 - Retard par mois

- Source : `tableau_mensuel.csv`
- Type : courbe
- Colonnes : `MOIS`
- Lignes : `retard_moyen_arr`
- Lecture : montrer les pics de juin et fevrier.

### F2 - Heatmap jour x heure

- Source : `tableau_heatmap_jour_heure.csv`
- Type : carre / heatmap
- Colonnes : `DEP_HOUR`
- Lignes : `JOUR`
- Couleur : `retard_moyen_arr`
- Lecture : les retards augmentent au fil de la journee.

### F3 - Classement des compagnies

- Source : `tableau_compagnies.csv`
- Type : barres triees
- Lignes : `compagnie`
- Colonnes : `taux_retard_arr`
- Lecture : comparer les compagnies les plus et les moins ponctuelles.

### F4 - Causes de retard

- Source : `tableau_causes_global.csv`
- Type : barres ou camembert
- Couleur : `cause`
- Valeur : `minutes_totales`
- Lecture : montrer que l'avion precedent en retard domine plus que la meteo.

### F5 - Routes les plus sensibles

- Source : `tableau_routes.csv`
- Type : barres triees
- Lignes : `route`
- Colonnes : `score_sensibilite`
- Couleur : `taux_retard_arr`
- Info-bulle : `n_vols`, `retard_moyen_arr`, `taux_retard_arr`, `taux_annulation`, `distance`
- Lecture : identifier les liaisons qui combinent gros volume et fort retard.

### F6 - Routes : volume vs retard

- Source : `tableau_routes.csv`
- Type : nuage de points
- Colonnes : `n_vols`
- Lignes : `retard_moyen_arr`
- Taille : `taux_retard_arr`
- Couleur : `score_sensibilite`
- Etiquette : `route` pour les points les plus importants
- Lecture : distinguer les routes tres frequentees des routes vraiment tres en retard.

### F7 - Carte des routes

- Source : `tableau_routes.csv`
- Utiliser les coordonnees :
  - origine : `origin_lat`, `origin_lon`
  - destination : `dest_lat`, `dest_lon`
- Si Tableau ne trace pas automatiquement des lignes, faire une carte simple des origines ou destinations les plus sensibles.
- Taille : `n_vols`
- Couleur : `score_sensibilite`
- Lecture : montrer la concentration geographique des routes sensibles.

### F8 - Carte des aeroports

- Source : `tableau_aeroports.csv`
- Colonnes : `LONGITUDE`
- Lignes : `LATITUDE`
- Couleur : `cluster_nom`
- Taille : `n_dep`
- Lecture : les aeroports expliquent en partie pourquoi certaines routes sont sensibles.

---

## 3. Dashboard resume

Le dashboard doit montrer :

- KPI : total vols, taux de retard, taux d'annulation, retard moyen.
- Heatmap jour x heure.
- Classement compagnies.
- Top routes sensibles.
- Carte ou scatter des routes.

Le message principal du dashboard :

> Les retards dependent du temps et des compagnies, mais certaines routes concentrent beaucoup plus le risque. L'analyse par route donne la vision la plus operationnelle.

---

## 4. Dictionnaire rapide

| Fichier | Usage |
|---------|-------|
| `tableau_mensuel.csv` | saisonnalite |
| `tableau_horaire.csv` | retard par heure |
| `tableau_heatmap_jour_heure.csv` | heatmap temps |
| `tableau_compagnies.csv` | comparaison compagnies |
| `tableau_causes_global.csv` | causes globales |
| `tableau_routes.csv` | routes aeriennes sensibles |
| `tableau_aeroports.csv` | carte / clusters aeroports |

---

## 5. Phrase a retenir

Les routes aeriennes permettent de passer d'une analyse generale a une analyse concrete : une liaison precise peut etre beaucoup plus risquee qu'une autre, meme si la compagnie ou l'aeroport semblent corrects en moyenne.
