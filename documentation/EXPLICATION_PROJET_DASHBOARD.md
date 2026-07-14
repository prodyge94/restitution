# Explication complete du projet - Du dataset raw au dashboard

## 1. Objectif du document

Ce document explique tout le cheminement du projet : comment on part des donnees brutes, ce qu'il y a dans le dataset, quelles analyses ont ete faites, ce qu'on en a deduit, quels fichiers ont ete crees, et pourquoi le dashboard final met en avant certains graphiques plutot que d'autres.

L'objectif est qu'une personne exterieure puisse comprendre le projet sans avoir participe au travail :

- ce que contient le dataset ;
- pourquoi les retards aeriens sont analyses sous plusieurs angles ;
- pourquoi les routes aeriennes sont devenues l'axe central ;
- comment les fichiers de nettoyage, d'analyse, de restitution et de dashboard s'enchainent ;
- pourquoi le dashboard final montre ces KPI et ces graphiques precis.

---

## 2. Idee generale du projet

Le projet analyse les retards des vols domestiques americains en 2015.

Le dataset principal contient environ **5,82 millions de vols**. Chaque ligne correspond a un vol, avec des informations sur :

- la compagnie aerienne ;
- l'aeroport de depart ;
- l'aeroport d'arrivee ;
- la date et l'heure prevue ;
- l'heure reelle ;
- les retards au depart et a l'arrivee ;
- l'annulation ou le deroutement ;
- la distance ;
- les causes declarees de retard quand elles existent.

Au depart, on pouvait analyser les retards de maniere generale : par mois, par compagnie, par aeroport. Mais cette lecture restait assez large.

La nouvelle version du projet met surtout l'accent sur les **routes aeriennes**, c'est-a-dire les liaisons origine -> destination, par exemple :

- `SFO -> LAX`
- `LAX -> SFO`
- `JFK -> LAX`
- `ORD -> LGA`

Pourquoi ce choix ? Parce qu'une route est plus operationnelle qu'une moyenne globale. Un passager ou une entreprise ne subit pas "la moyenne des vols US", il subit une liaison precise. Une compagnie peut etre correcte en moyenne, mais une route particuliere peut etre beaucoup plus risquee.

---

## 3. Donnees brutes utilisees

Les donnees brutes sont dans :

```text
codex/data/raw/
```

### 3.1 `flights.csv`

C'est le fichier principal.

Il contient **5 819 079 lignes** et les informations de vol. Les colonnes importantes sont notamment :

| Type d'information | Exemples de colonnes | Utilite |
|---|---|---|
| Date | `YEAR`, `MONTH`, `DAY`, `DAY_OF_WEEK` | analyser la saisonnalite et les jours |
| Compagnie | `AIRLINE` | comparer les compagnies |
| Aeroports | `ORIGIN_AIRPORT`, `DESTINATION_AIRPORT` | construire les routes et cartes |
| Horaires | `SCHEDULED_DEPARTURE`, `DEPARTURE_TIME`, `SCHEDULED_ARRIVAL`, `ARRIVAL_TIME` | comparer prevu/reel |
| Retards | `DEPARTURE_DELAY`, `ARRIVAL_DELAY` | mesurer la ponctualite |
| Annulation | `CANCELLED`, `CANCELLATION_REASON` | mesurer les vols non effectues |
| Deroutement | `DIVERTED` | exclure ou signaler les cas particuliers |
| Distance | `DISTANCE` | contextualiser les routes |
| Causes | `AIRLINE_DELAY`, `WEATHER_DELAY`, `AIR_SYSTEM_DELAY`, `SECURITY_DELAY`, `LATE_AIRCRAFT_DELAY` | comprendre les causes declarees |

### 3.2 `airlines.csv`

Ce fichier donne le nom complet des compagnies.

Exemple :

- `AA` -> American Airlines
- `DL` -> Delta Air Lines
- `WN` -> Southwest Airlines

Il sert a rendre les analyses lisibles. Sans ce fichier, on aurait seulement des codes compagnies.

### 3.3 `airports.csv`

Ce fichier decrit les aeroports.

Il contient :

- le code IATA ;
- le nom de l'aeroport ;
- la ville ;
- l'Etat ;
- la latitude ;
- la longitude.

Il sert surtout a deux choses :

- enrichir les routes avec les villes et les coordonnees ;
- afficher les routes sur une carte.

---

## 4. Nettoyage des donnees

Le nettoyage est fait dans :

```text
codex/analyse/01_nettoyage.py
```

La sortie principale est :

```text
codex/data/processed/flights_clean.parquet
```

Un rapport JSON est aussi produit :

```text
codex/analyse/sorties/01_nettoyage.json
```

### 4.1 Pourquoi nettoyer ?

Le fichier brut est trop lourd et contient des cas particuliers :

- vols annules ;
- vols deroutes ;
- valeurs manquantes ;
- causes de retard parfois absentes ;
- codes aeroports defectueux sur une partie du dataset.

Le but du nettoyage est de creer une base fiable pour les analyses.

### 4.2 Points controles

Les controles principaux montrent :

- **5 819 079 vols** dans le fichier ;
- **0 doublon complet** ;
- **89 884 vols annules**, soit **1,54 %** ;
- **15 187 vols deroutes**, soit **0,26 %** ;
- environ **486 165 codes aeroports numeriques en octobre 2015**, ce qui pose probleme pour les analyses geographiques ;
- les colonnes de causes de retard sont tres souvent vides, mais c'est normal : elles ne sont renseignees que quand un vol a un retard attribue a une cause.

### 4.3 Creation des variables utiles

Le nettoyage ajoute ou prepare des variables comme :

- `IS_DELAYED_ARR` : vrai si le vol arrive avec au moins 15 minutes de retard ;
- `IS_DELAYED_DEP` : vrai si le vol part avec au moins 15 minutes de retard ;
- `DEP_HOUR` : heure de depart prevue ;
- indicateurs pour separer les vols valides des vols annules ou deroutes ;
- detection des codes aeroports numeriques.

Le seuil de **15 minutes** est important : dans l'aerien, on considere souvent qu'un vol est en retard a partir de 15 minutes.

### 4.4 Pourquoi utiliser un fichier Parquet ?

Le fichier `flights_clean.parquet` est cree pour rendre les analyses plus rapides et plus propres.

Le CSV brut est volumineux. Le Parquet :

- prend moins de place ;
- garde les types de donnees ;
- se lit plus vite avec Python.

---

## 5. Analyses realisees

Les analyses principales sont dans :

```text
codex/analyse/02_analyse.py
```

Les resultats chiffres sont dans :

```text
codex/analyse/sorties/02_analyse.json
```

Les figures sont dans :

```text
codex/analyse/figures/
```

Les fichiers exportes pour visualisation sont dans :

```text
codex/data/processed/
```

---

## 6. Analyse globale du retard

Avant d'entrer dans les hypotheses, on regarde les indicateurs generaux.

Resultats globaux :

- **5 819 079 vols analyses** ;
- **14 compagnies** ;
- **17,91 %** des vols arrivent avec au moins 15 minutes de retard ;
- **1,54 %** des vols sont annules ;
- retard moyen a l'arrivee : **+4,41 minutes** ;
- mediane du retard a l'arrivee : **-5 minutes**.

La moyenne est positive, mais la mediane est negative. Cela veut dire que beaucoup de vols arrivent a l'heure ou en avance, mais qu'une minorite de gros retards tire la moyenne vers le haut.

C'est une information importante : il ne faut pas analyser seulement la moyenne. On utilise aussi :

- le taux de retard ;
- la mediane ;
- les percentiles ;
- les volumes de vols.

---

## 7. Hypothese H1 - Les retards dependent du temps

### Question

Est-ce que les retards varient selon le mois, le jour ou l'heure ?

### Analyses faites

On a cree plusieurs agregations :

- retard moyen par mois ;
- taux de retard par mois ;
- retard moyen par heure de depart ;
- taux de retard par heure ;
- heatmap jour x heure.

Fichiers produits :

```text
codex/data/processed/tableau_mensuel.csv
codex/data/processed/tableau_horaire.csv
codex/data/processed/tableau_heatmap_jour_heure.csv
```

Figures produites :

```text
codex/analyse/figures/fig_h1_retard_mensuel.png
codex/analyse/figures/fig_h1_retard_horaire.png
codex/analyse/figures/fig_h1_heatmap_jour_heure.png
```

### Resultats

Les resultats montrent :

- le pire mois est **juin** ;
- les retards augmentent au fil de la journee ;
- la correlation de Spearman entre l'heure et le retard moyen est positive : **0,716** ;
- a 5h, le retard moyen est plutot negatif ;
- vers 19h, le retard moyen devient beaucoup plus eleve.

### Interpretation

Les retards ne sont pas repartis au hasard.

Ils s'accumulent pendant la journee : un avion en retard sur un vol peut retarder le vol suivant. C'est ce qu'on appelle un effet de propagation ou effet cascade.

### Pourquoi c'est dans le dashboard ?

Le graphique "Le risque augmente au fil de la journee" a ete garde car il raconte une idee simple et forte :

> plus la journee avance, plus le risque de retard augmente.

C'est facile a comprendre en presentation et ca explique pourquoi les retards sont un phenomene cumulatif.

---

## 8. Hypothese H2 - La compagnie influence la ponctualite

### Question

Est-ce que certaines compagnies sont plus souvent en retard que d'autres ?

### Analyses faites

On a compare les compagnies selon :

- le nombre de vols ;
- le taux de retard ;
- le retard moyen ;
- le taux d'annulation.

On a aussi realise un test du chi-2 pour verifier si la ponctualite depend statistiquement de la compagnie.

Fichier produit :

```text
codex/data/processed/tableau_compagnies.csv
```

Figure produite :

```text
codex/analyse/figures/fig_h2_retard_compagnie.png
```

### Resultats

Le test du chi-2 rejette l'independance entre compagnie et retard.

Resultats importants :

- pire compagnie en taux de retard : **Spirit Air Lines**, environ **28,79 %** ;
- meilleure compagnie : **Hawaiian Airlines**, environ **10,53 %** ;
- Cramer's V : **0,084**.

### Interpretation

La compagnie a bien un effet, mais cet effet reste modere. Cela veut dire que la compagnie compte, mais qu'elle n'explique pas tout.

Les retards dependent aussi :

- du moment de la journee ;
- des routes ;
- des aeroports ;
- de la propagation des retards.

### Pourquoi c'est dans le dashboard ?

La comparaison des compagnies est gardee dans le dashboard, mais elle n'est pas le centre de l'analyse.

Elle sert a donner un repere :

- quelles compagnies sont les plus exposees ;
- quelles compagnies sont les plus ponctuelles ;
- pourquoi il ne faut pas reduire l'analyse a "la compagnie est mauvaise".

---

## 9. Analyse des causes declarees de retard

### Question

Quand un retard est declare, quelle est la cause principale ?

### Colonnes utilisees

Les causes de retard viennent des colonnes :

| Colonne | Signification |
|---|---|
| `AIRLINE_DELAY` | retard attribue a la compagnie |
| `WEATHER_DELAY` | retard meteo |
| `AIR_SYSTEM_DELAY` | retard lie au systeme aerien / trafic |
| `SECURITY_DELAY` | retard securite |
| `LATE_AIRCRAFT_DELAY` | retard de l'avion precedent |

Ces colonnes donnent des **minutes de retard attribuees a une cause**. Elles ne sont pas renseignees pour tous les vols, seulement quand le vol a un retard avec cause declaree.

### Fichiers produits

```text
codex/data/processed/tableau_causes_global.csv
codex/data/processed/tableau_causes_par_compagnie.csv
```

Figure produite :

```text
codex/analyse/figures/fig_h2_causes.png
```

### Resultats

La cause principale est :

```text
LATE_AIRCRAFT_DELAY = avion precedent arrive en retard
```

Dans le dashboard :

- avion en retard : environ **39,8 %** des minutes de retard ;
- compagnie : environ **32,2 %** ;
- systeme aerien : environ **22,9 %** ;
- meteo : environ **5,0 %** ;
- securite : environ **0,1 %**.

### Interpretation

La meteo n'est pas la cause principale.

Le retard vient surtout :

- de la propagation des retards entre vols ;
- de facteurs attribues a la compagnie ;
- du systeme aerien.

Important : on ne peut pas dire que **LAX est la cause principale**. On peut dire que LAX apparait souvent dans les routes sensibles, mais la cause declaree principale dans le dataset est l'avion precedent en retard.

### Pourquoi c'est dans le dashboard ?

Ce graphique est garde parce qu'il repond a la question "pourquoi les retards arrivent ?".

Il permet aussi d'eviter une conclusion trop simple du type :

> Les retards viennent surtout de la meteo.

En realite, le dataset montre surtout un phenomene de propagation.

---

## 10. Hypothese H3 - Les routes aeriennes concentrent les retards

### Question

Quelles liaisons origine -> destination concentrent le plus de risque ?

### Pourquoi les routes sont devenues l'axe central

Une route est une liaison precise :

```text
ORIGIN_AIRPORT -> DESTINATION_AIRPORT
```

Exemple :

```text
SFO -> LAX
```

Cette approche est plus concrete qu'une analyse globale.

Une compagnie peut avoir une moyenne correcte, mais une route particuliere peut etre problematique. Un aeroport peut etre charge, mais ce qui interesse un passager, c'est aussi la liaison qu'il prend.

### Variables calculees par route

Pour chaque route, on calcule :

- `n_vols` : nombre de vols ;
- `retard_moyen_arr` : retard moyen a l'arrivee ;
- `retard_median_arr` : retard median ;
- `taux_retard_arr` : pourcentage de vols arrives avec au moins 15 minutes de retard ;
- `taux_annulation` : taux d'annulation ;
- `distance` : distance de la route ;
- coordonnees de l'aeroport d'origine ;
- coordonnees de l'aeroport de destination ;
- `score_sensibilite` : volume x taux de retard.

Fichier produit :

```text
codex/data/processed/tableau_routes.csv
```

Figures produites :

```text
codex/analyse/figures/fig_h3_routes_sensibles.png
codex/analyse/figures/fig_h3_routes_volume_retard.png
```

### Pourquoi creer un score de sensibilite ?

Le score utilise :

```text
score_sensibilite = nombre de vols x taux de retard
```

Ce score a ete choisi parce qu'une route peut etre importante de deux manieres :

1. Elle peut avoir un taux de retard tres eleve.
2. Elle peut avoir un volume enorme, donc toucher beaucoup de vols meme si le taux n'est pas le pire.

Une petite route avec 50 % de retard peut etre interessante, mais elle concerne peu de vols. Une grosse route avec 25 % de retard peut avoir un impact beaucoup plus fort sur le reseau.

### Resultats

La route la plus sensible est :

```text
SFO -> LAX
```

Chiffres :

- **13 400 vols** ;
- **26,23 %** d'arrivees en retard ;
- **+11,44 minutes** de retard moyen ;
- route aussi la plus frequentee dans les routes analysees.

Autres routes visibles dans le dashboard :

- `LAX -> SFO`
- `LAS -> LAX`
- `ORD -> LGA`
- `JFK -> LAX`
- `LAX -> LAS`
- `LAX -> JFK`
- `ORD -> LAX`

### Interpretation

Les routes sensibles ne sont pas seulement des trajets en retard. Ce sont des trajets qui combinent :

- beaucoup de vols ;
- un taux de retard eleve ;
- une exposition importante pour les passagers ;
- parfois des hubs importants.

LAX apparait souvent dans les routes sensibles. On peut donc dire que LAX est un point de concentration important. Mais il ne faut pas dire que LAX est "la cause principale" des retards. C'est plutot un hub present dans plusieurs routes a risque.

### Pourquoi c'est dans le dashboard ?

C'est le coeur du dashboard.

Le dashboard met une carte et un classement de routes parce que le message principal est :

> les retards ne sont pas seulement un probleme global ; certaines liaisons concentrent beaucoup plus le risque.

La carte permet de comprendre visuellement ou se trouvent les routes. Le top 8 permet de les classer clairement.

---

## 11. Hypothese H4 - Les aeroports expliquent une partie des routes

### Question

Les aeroports peuvent-ils etre regroupes selon leur profil de performance ?

### Analyse faite

On a cree une table par aeroport avec :

- volume de departs ;
- retard moyen au depart ;
- taux de retard au depart ;
- taux d'annulation ;
- taxi-out moyen.

Puis on a applique un K-means pour regrouper les aeroports en profils.

Fichiers produits :

```text
codex/data/processed/tableau_aeroports.csv
codex/data/processed/tableau_clusters_profil.csv
```

Figures produites :

```text
codex/analyse/figures/fig_h3_elbow_silhouette.png
codex/analyse/figures/fig_h3_clusters_scatter.png
codex/analyse/figures/fig_h3_clusters_carte.png
```

### Resultats

Le nombre de clusters retenu est **3**.

Profils :

1. Aeroports ponctuels et fiables.
2. Aeroports congestionnes avec retards eleves.
3. Aeroports instables avec annulations elevees.

### Interpretation

Les aeroports ne remplacent pas l'analyse des routes. Ils l'expliquent en partie.

Une route qui passe par un hub congestionne peut etre plus exposee. Mais le dashboard final ne met pas les clusters au centre parce que le sujet principal choisi est devenu la route aerienne.

### Pourquoi ce n'est pas le graphique principal du dashboard ?

Les clusters aeroport sont utiles, mais moins directement lisibles pour un public non technique.

Un professeur ou un decisionnaire comprend plus vite :

```text
SFO -> LAX est une route prioritaire
```

que :

```text
tel aeroport appartient au cluster 1 selon K-means
```

Donc les aeroports restent dans l'analyse et le rapport, mais le dashboard final privilegie les routes.

---

## 12. Fichiers crees et role de chacun

### 12.1 Dossier `data/raw`

```text
codex/data/raw/flights.csv
codex/data/raw/airlines.csv
codex/data/raw/airports.csv
```

Role : stocker les donnees brutes originales.

Ces fichiers ne doivent pas etre modifies. Ils servent de point de depart.

### 12.2 Dossier `data/processed`

```text
codex/data/processed/flights_clean.parquet
```

Base nettoyee et optimisee pour Python.

```text
codex/data/processed/tableau_mensuel.csv
codex/data/processed/tableau_horaire.csv
codex/data/processed/tableau_heatmap_jour_heure.csv
```

Fichiers pour l'analyse temporelle.

```text
codex/data/processed/tableau_compagnies.csv
codex/data/processed/tableau_causes_global.csv
codex/data/processed/tableau_causes_par_compagnie.csv
```

Fichiers pour l'analyse compagnies et causes.

```text
codex/data/processed/tableau_routes.csv
```

Fichier central pour l'analyse des routes aeriennes.

```text
codex/data/processed/tableau_aeroports.csv
codex/data/processed/tableau_clusters_profil.csv
```

Fichiers pour l'analyse des aeroports et clusters.

```text
codex/data/processed/tableau_echantillon.csv
```

Petit echantillon de vols pour exploration ou verification rapide.

### 12.3 Dossier `analyse`

```text
codex/analyse/01_nettoyage.py
```

Script de nettoyage. Il charge les donnees brutes, controle la qualite, cree les variables utiles et exporte le Parquet propre.

```text
codex/analyse/02_analyse.py
```

Script principal d'analyse. Il calcule les KPI, teste les hypotheses, cree les agregations et exporte les CSV pour visualisation.

```text
codex/analyse/sorties/01_nettoyage.json
codex/analyse/sorties/02_analyse.json
```

Fichiers de resultats chiffres. Ils servent a tracer les conclusions et a verifier les valeurs utilisees dans le rapport/dashboard.

```text
codex/analyse/figures/
```

Graphiques statiques produits par Python.

### 12.4 Dossier `dashboard`

```text
codex/dashboard/index.html
```

Dashboard interactif en HTML/CSS/JavaScript.

Il affiche :

- le titre du dataset ;
- les KPI globaux ;
- la route prioritaire ;
- une carte des routes sensibles ;
- un top 8 des routes ;
- le risque de retard par heure ;
- les causes declarees ;
- la comparaison des compagnies.

Le dashboard utilise D3.js pour les visualisations et une carte US via TopoJSON.

### 12.5 Dossier `rapport`

```text
codex/rapport/RAPPORT.md
```

Rapport analytique qui explique les donnees, les hypotheses, les resultats et les limites.

```text
codex/rapport/SCRIPT_SOUTENANCE.md
```

Script court pour expliquer le projet a l'oral.

### 12.6 Dossier `tableau`

```text
codex/tableau/GUIDE_TABLEAU.md
```

Guide pour refaire ou comprendre les visualisations Tableau possibles.

### 12.7 Dossier `outputs`

```text
codex/outputs/Rendu_retards_vols_US_2015_ESGI.pptx
```

PowerPoint complet de restitution.

```text
codex/outputs/dashboard_routes_hypotheses.pptx
```

PowerPoint court avec :

- slide 1 : hypotheses de depart ;
- slide 2 : dashboard final.

```text
codex/outputs/dashboard_browser_capture.png
codex/outputs/dashboard_browser_capture_centered.png
```

Captures du dashboard depuis le navigateur.

---

## 13. Pourquoi le dashboard montre ces elements

Le dashboard n'affiche pas tout ce qui a ete analyse. Il affiche les elements les plus utiles pour comprendre rapidement le sujet.

### 13.1 Titre du dataset

Le titre est :

```text
US Flight Delays and Cancellations 2015
```

Pourquoi ? Pour qu'au premier coup d'oeil, on sache :

- le sujet ;
- le pays ;
- l'annee ;
- le type d'evenement analyse.

### 13.2 KPI globaux

KPI affiches :

- nombre de vols ;
- taux de retard ;
- retard moyen ;
- taux d'annulation.

Pourquoi ces KPI ?

Ils donnent le contexte avant d'aller dans le detail. Sans eux, on ne sait pas si le probleme concerne 10 000 vols ou 5,8 millions.

### 13.3 Bandeau "priorite reseau"

Le bandeau met en avant :

```text
SFO -> LAX
```

Pourquoi ?

Parce que cette route combine :

- le plus gros volume ;
- un taux de retard eleve ;
- un impact important.

Ce bandeau transforme l'analyse en message decisionnel.

### 13.4 Carte des routes

La carte montre les routes les plus sensibles.

Pourquoi une carte ?

Parce qu'une route est une information geographique. La carte aide a voir rapidement que plusieurs routes prioritaires tournent autour de grands hubs comme LAX, SFO, LAS, ORD, LGA ou JFK.

### 13.5 Top 8 des routes

Le classement donne une lecture precise.

Pourquoi ne pas afficher toutes les routes ?

Parce qu'il y en a beaucoup. Afficher toutes les routes rendrait le dashboard illisible. On affiche donc les routes les plus prioritaires, c'est-a-dire celles qui ont le meilleur score de sensibilite.

### 13.6 Courbe du risque par heure

Elle montre que le risque augmente au fil de la journee.

Pourquoi la garder ?

Parce qu'elle explique le mecanisme de propagation des retards. Ce graphique repond a la question "quand les retards apparaissent-ils ?".

### 13.7 Causes de retard

Le graphique des causes montre que l'avion precedent en retard est la cause dominante.

Pourquoi la garder ?

Parce qu'il explique "pourquoi" les retards arrivent. Il montre aussi que la meteo n'est pas la cause principale.

### 13.8 Comparaison des compagnies

Ce graphique montre les compagnies les plus et les moins exposees au retard.

Pourquoi la garder ?

Parce que la compagnie reste un facteur important, meme si elle n'est pas l'axe central.

---

## 14. Pourquoi certains elements ne sont pas au centre du dashboard

### 14.1 Pourquoi pas uniquement les compagnies ?

Parce que la compagnie ne suffit pas a expliquer les retards.

Le test statistique montre un lien, mais l'effet reste modere. Une compagnie peut etre correcte en moyenne tout en ayant certaines routes sensibles.

### 14.2 Pourquoi pas uniquement les aeroports ?

Parce qu'un aeroport donne une information de lieu, mais pas directement l'experience d'une liaison.

Un passager ne prend pas "LAX" tout seul : il prend une route comme `SFO -> LAX` ou `LAX -> JFK`.

### 14.3 Pourquoi pas seulement les causes ?

Parce que les causes expliquent les minutes de retard, mais elles ne disent pas quelles routes sont prioritaires.

### 14.4 Pourquoi pas une heatmap jour x heure dans le dashboard final ?

La heatmap est utile en analyse, mais elle est plus dense. Pour un dashboard de presentation, une courbe horaire est plus directe et plus lisible.

### 14.5 Pourquoi pas tous les graphiques Python ?

Un dashboard doit etre comprehensible rapidement. Il faut choisir les graphiques qui racontent le mieux l'histoire.

Ici, l'histoire est :

1. le dataset est massif ;
2. les retards existent mais ne touchent pas tous les vols ;
3. le risque augmente dans la journee ;
4. les causes montrent un effet de propagation ;
5. les routes aeriennes permettent d'identifier les liaisons prioritaires.

---

## 15. Message final a retenir

Le projet montre que les retards aeriens ne sont pas seulement un phenomene global.

Ils dependent :

- du temps ;
- de la compagnie ;
- des causes declarees ;
- des aeroports ;
- mais surtout de certaines routes qui concentrent le risque.

Le dashboard final met donc les **routes aeriennes** au centre, car c'est la lecture la plus concrete et la plus operationnelle.

La conclusion principale est :

> SFO -> LAX est la route la plus prioritaire dans l'analyse, car elle combine un tres gros volume de vols et un taux de retard eleve.

Mais il faut ajouter une nuance importante :

> LAX apparait comme un point important dans plusieurs routes sensibles, mais la cause declaree principale des retards reste l'arrivee tardive de l'avion precedent.

---

## 16. Comment reproduire le projet

Depuis le dossier :

```text
codex/
```

Lancer :

```bash
python analyse/01_nettoyage.py
python analyse/02_analyse.py
```

Puis ouvrir le dashboard :

```bash
cd dashboard
python -m http.server 8765
```

Et aller sur :

```text
http://127.0.0.1:8765/
```

---

## 17. Resume ultra-court pour expliquer a l'oral

On part d'un dataset de 5,82 millions de vols domestiques US en 2015. On nettoie les donnees, on retire les cas qui posent probleme pour les analyses geographiques, puis on cree des variables de retard a 15 minutes. Ensuite, on analyse les retards selon le temps, les compagnies, les causes, les aeroports et surtout les routes aeriennes.

Les resultats montrent que les retards augmentent au fil de la journee, que la compagnie a un effet mais ne suffit pas a tout expliquer, et que la cause principale declaree est l'avion precedent arrive en retard. L'analyse la plus operationnelle est celle des routes, car elle montre directement quelles liaisons concentrent le plus de risque.

C'est pour cela que le dashboard final met en avant les KPI globaux, la carte des routes, le top 8 des routes prioritaires, l'evolution horaire, les causes de retard et la comparaison des compagnies.
