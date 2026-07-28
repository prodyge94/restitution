# Script de soutenance — US Flight Delays and Cancellations 2015

**Durée : 30 min · 4 intervenants · PowerPoint + démonstration + notebook**

Rôles : **A = Dan** = données & méthode · **B** = H1 (calendrier) · **C** = H2 (vols longs) · **D** = H3 (routes) + conclusion.
Pour B, C, D (Medy, Ahmed, Robin) : mettre sur C celui qui avait travaillé H2 à l'origine, sur B le plus à l'aise en statistiques (chi², V de Cramér), sur D le plus à l'aise en narration.
Chacun pilote l'écran pendant son passage. Tous les chiffres ci-dessous sont exacts (issus de `resume_v2.json` regénéré).

## Minutage

| Séquence | Qui | Durée |
|---|---|---|
| Slides 1-3 : titre, dataset, traitements | A | 5 min |
| Slide 4 : les 3 hypothèses | B, C, D | 1 min |
| Slide 5 + démo du dashboard en direct | B → C → D | 5 min |
| Slides 6-7 : conclusion, références | D | 2 min |
| Notebook : sections 1-5 → 6 → 7 → 8-12 | A → B → C → D | 13 min |
| Marge pour les questions | tous | 4 min |

**Avant de commencer** : dashboard.html ouvert dans un onglet (double-clic, pas besoin de serveur), notebook ouvert et déjà exécuté, PPT en mode présentation. Vérifier le vidéoprojecteur avec le dashboard : si les couleurs passent mal, augmenter la luminosité.

---

## PARTIE 1 — Le PowerPoint (~12 min)

### A — Slide 1 (titre) — 30 s

« Bonjour. Nous allons vous présenter notre projet de reporting sur les retards et annulations des vols intérieurs américains en 2015. Notre question de départ : quand, qui et où — quand les retards frappent-ils, quelles compagnies sont touchées, et où se concentrent les annulations. Je commence par les données et leur préparation, puis chacun présentera l'hypothèse qu'il a instruite, nous vous ferons visiter le dashboard, et nous terminerons par les conclusions avant de vous montrer le notebook. »

### A — Slide 2 (dataset) — 2 min à 2 min 30

**La source et le choix (~30 s).** « Le dataset s'appelle *2015 Flight Delays and Cancellations*. Il est distribué sur Kaggle mais publié à l'origine par le Département américain des Transports, le régulateur fédéral — c'est une source officielle. Nous l'avons choisi, et fait valider, parce qu'il coche trois cases : il est massif — 5 819 079 vols, l'intégralité du trafic intérieur américain de 2015 —, il est riche — 31 colonnes par vol —, et il permet d'interroger le phénomène sous nos trois angles : le temps, les compagnies, le réseau. »

**Les trois fichiers (~20 s).** « Il est livré en trois fichiers qui se joignent par le code IATA, le code à trois lettres de l'aviation civile. Le fichier des vols : 592 Mo, une ligne par vol programmé. L'annuaire des compagnies : 14 lignes, le code et le nom commercial — WN c'est Southwest, DL c'est Delta. Et les aéroports : 322 lignes avec code, nom, ville, État et coordonnées GPS — ce sont ces coordonnées qui nous permettront la carte du dashboard. »

**L'extrait réel (~30 s).** « Chaque ligne est un vol programmé. Vous en voyez quatre vrais : un Southwest Atlanta→Chicago arrivé 4 minutes en avance ; un Spirit Chicago→New York arrivé avec 85 minutes de retard ; un JetBlue Boston→Chicago annulé — motif B, la météo, un 2 février ; et un Delta New York→Los Angeles, 2 475 miles, arrivé 10 minutes en avance. Retenez ces quatre-là : le low-cost en retard, l'annulation météo du Nord-Est en hiver, le très long vol ponctuel — ils annoncent déjà nos trois hypothèses. »

**Les colonnes clés, une par une (~40 s à l'oral, le reste en réserve pour les questions).**
- `YEAR / MONTH / DAY` : « la date du vol en trois colonnes — nous les recomposons en vraie date. »
- `AIRLINE` : « le code IATA de la compagnie qui opère le vol, 14 valeurs distinctes. »
- `ORIGIN_AIRPORT / DESTINATION_AIRPORT` : « les aéroports de départ et d'arrivée, en code IATA — LAX, JFK... C'est sur ces colonnes que nous découvrirons l'anomalie d'octobre, j'y reviens. »
- `SCHEDULED_DEPARTURE` : « l'heure de départ prévue, au format hhmm — 1730 se lit 17 h 30. »
- `DISTANCE` : « la distance du vol en miles — un mile vaut 1,6 km ; les 2 475 miles du New York–Los Angeles font environ 4 000 km. C'est elle qui définira le vol long. »
- `DEPARTURE_DELAY / ARRIVAL_DELAY` : « les minutes de retard au départ et à l'arrivée — négatif signifie en avance. Toute notre analyse des retards repose sur l'arrivée : c'est ce que vit le passager. L'écart entre les deux mesure ce que le vol rattrape en l'air — il servira dans H2. »
- `CANCELLED` et `CANCELLATION_REASON` : « vol annulé oui/non, et le motif en un code : A la compagnie, B la météo, C le contrôle aérien, D la sûreté. »
- `DIVERTED` : « vol dérouté vers un autre aéroport que prévu — rare, 15 187 cas. »
- `AIR_SYSTEM / SECURITY / AIRLINE / LATE_AIRCRAFT / WEATHER_DELAY` : « cinq colonnes qui ne sont renseignées que pour les vols en retard d'au moins 15 minutes : elles ventilent les minutes de retard par responsabilité — le contrôle aérien, la sûreté, la compagnie, l'avion précédent arrivé en retard, la météo. »

**Si le prof demande les colonnes restantes** (non montrées sur la slide) : `FLIGHT_NUMBER` le numéro de vol, `TAIL_NUMBER` l'immatriculation de l'appareil, `TAXI_OUT / TAXI_IN` les minutes de roulage au sol, `WHEELS_OFF / WHEELS_ON` les heures réelles de décollage et d'atterrissage, `SCHEDULED_TIME / ELAPSED_TIME / AIR_TIME` les durées prévue, réelle et en vol, `SCHEDULED_ARRIVAL / ARRIVAL_TIME / DEPARTURE_TIME` les horaires prévus et réels. « Nous ne chargeons que 19 colonnes sur 31 : le détail opérationnel du roulage et des heures réelles ne sert aucune de nos hypothèses, et l'écarter allège d'autant la mémoire. »

**Les fichiers annexes (~10 s).** « En bas de slide : airlines.csv fait la correspondance code → nom de compagnie, airports.csv apporte ville, État et coordonnées — tous deux joints au fichier des vols par le code IATA. »

### A — Slide 3 (traitements) — 2 min à 2 min 30

**Étape 1 — Nettoyer (~50 s).** « Premier réflexe avant toute analyse : l'audit des valeurs manquantes et des incohérences. Deux découvertes ont structuré la suite.
La première : `ARRIVAL_DELAY` manque pour 105 071 vols. Plutôt que de supprimer ou d'imputer à l'aveugle, nous avons cherché *pourquoi* — et le croisement le prouve : ce sont exactement les 89 884 vols annulés plus les 15 187 déroutés. Un vol qui n'a jamais atterri comme prévu n'a pas de retard d'arrivée : c'est un manquant structurel, pas accidentel. La décision qui en découle : les exclure du périmètre des retards. Si on ne le fait pas, le test "retard ≥ 15 minutes" renvoie faux pour eux et ils sont silencieusement comptés comme des vols à l'heure — le taux serait artificiellement abaissé.
La seconde : les colonnes aéroports contiennent normalement des codes à trois lettres, mais une partie des lignes porte des identifiants numériques — et 100 % de ces lignes sont en octobre. Ce mois utilise un autre référentiel, impossible à joindre à notre table des aéroports : une même liaison y apparaîtrait sous deux noms. Le dataset ne fournit pas de table de conversion ; nous avons donc écarté octobre — mais uniquement de l'analyse des routes, et après avoir chiffré le coût : octobre pèse 8,4 % des vols mais seulement 2,7 % des annulations, c'est le mois le plus calme de l'année — 0,50 % d'annulations contre 1,54 % en moyenne. Les hypothèses 1 et 2 conservent les douze mois. »

**Étape 2 — Construire (~40 s).** « Ensuite, les variables d'analyse — chacune définie explicitement pour être discutable et reproductible.
Le retard : arrivée à 15 minutes ou plus — ce n'est pas notre choix, c'est la norme du régulateur américain. Et nous raisonnons en *taux de vols en retard*, pas en moyenne : le retard médian du pays est de −5 minutes quand la moyenne est à +4,4 — la majorité des vols arrivent en avance, une minorité très en retard tire la moyenne : elle serait trompeuse.
Le vol long : 1 500 miles ou plus, la distance d'un vol qui traverse une bonne partie du pays — et nous testerons la sensibilité à 1 000 et 2 000 miles.
Les fenêtres de vacances 2015, bornées date à date : l'été du 1er juin au 31 août, le Nouvel An du 1er au 5 janvier, Thanksgiving du 20 au 30 novembre, Noël du 18 au 31 décembre. C'est un proxy assumé — le dataset n'a pas de colonne vacances — borné explicitement pour être critiquable.
Et les routes : le couple orienté origine→destination — Boston→LaGuardia est distinct de LaGuardia→Boston, car rien ne dit que les deux sens se comportent pareil ; nous vérifierons aussi en non orienté. »

**Étape 3 — Analyser (~30 s).** « Enfin les traitements analytiques : des agrégations par jour et par mois pour les séries temporelles, par compagnie — quatorze — pour l'hypothèse 2, par route — 4 693 — pour l'hypothèse 3. Et trois principes transverses : mesurer des *parts* — quelle part des retards vient des vols longs ; comparer à une *référence comparable* — chaque période de vacances face au reste de son propre mois, pour neutraliser la saison ; et rapporter toute concentration à celle du trafic — sinon on mesure la taille des routes, pas leur fragilité. Chaque résultat est ensuite retesté sur d'autres seuils et périmètres. »

**La chute (~10 s).** « Le tout tient dans un pipeline reproductible : les 592 Mo sont chargés en types compacts — environ 350 Mo en mémoire — et la chaîne complète s'exécute en une centaine de secondes. Aucun chiffre n'est écrit à la main : tableaux, graphiques et dashboard sont régénérés à chaque exécution du notebook. »

### B, C, D — Slide 4 (hypothèses) — 1 min

Chacun lit la sienne, sans commentaire (le prof ne veut pas de paragraphes sous les hypothèses) :
- **B** : « Première hypothèse, le calendrier : il y a plus de vols en retard pendant les vacances que le reste de l'année. »
- **C** : « Deuxième hypothèse, les vols longs : les longs courriers composent la plus grande majorité des retards. »
- **D** : « Troisième hypothèse, le réseau : une petite minorité de liaisons concentre la majorité des annulations. »

### B → C → D — Slide 5 puis dashboard en direct — 5 min

*Basculer du PPT vers l'onglet dashboard.html. Phrase de transition (celui qui a la main, B) :* « Voici notre écran de résumé — il est interactif, généré automatiquement par notre notebook, et conçu pour un lecteur non technique. En haut, les repères : 5,82 millions de vols, 18,6 % en retard, 1,5 % annulés. »

**B — cartes H1 (~1 min 30)** : « La courbe hebdomadaire montre le rythme de l'année : le pic de retards culmine à 35 % des vols la semaine du Nouvel An, et les annulations culminent à 6,5 % en mars — retards et annulations ne vivent pas au même rythme, premier enseignement. Le classement des périodes le confirme : Nouvel an 36,2 %, Noël 28,8 %, été 21 %, contre 16,9 % hors vacances. »

**C — cartes H2 (~1 min 30)** : « Pour les vols longs, réponse directe à l'hypothèse : ils ne portent que 13 % des retards — et la barre de gauche montre pourquoi ce n'est pas un hasard : c'est exactement leur part du trafic. Même en minutes de retard cumulées, 13 %. Et le nuage de points élimine l'hypothèse de repli : chaque bulle est une compagnie, si les vols longs pénalisaient les compagnies qui en font beaucoup, le nuage monterait vers la droite — il est plat. Les plus en retard sont Spirit et Frontier, des low-cost court-courrier ; les plus ponctuelles, Delta, Alaska, Hawaiian, ont des profils opposés. »

**D — carte géo et tables (~1 min 30)** : « Les annulations, elles, ont une géographie : le Nord-Est. La liaison la plus risquée relie Norfolk à LaGuardia : 15,2 % de vols annulés. Les 455 routes qui portent la moitié des annulations du réseau sont annulées 2,6 fois plus que les autres à volume comparable, et 51,7 % de leurs annulations tombent entre janvier et mars — l'hiver. La météo est d'ailleurs le premier motif d'annulation du pays : 54 % des cas. »

### D — Slides 6-7 (conclusion, références) — 2 min

- « H1 est confirmée, mais pas pour la raison attendue : ce ne sont pas "les vacances", ce sont les pics de fin d'année — +18 points au Nouvel An, +15 à Noël, quand Thanksgiving, le plus gros week-end de déplacement du pays, n'a aucun effet. »
- « H2 est réfutée : 13 % des retards, très loin d'une majorité — et c'est un vrai résultat, pas un échec : la distance ne dégrade pas la fiabilité, les vols longs rattrapent même leur retard en vol. »
- « H3 est confirmée, à condition de la mesurer honnêtement : la concentration brute est en partie mécanique, le résultat solide est le sur-risque ×2,6 des navettes du Nord-Est en hiver. »
- « Le fil conducteur : **les retards suivent le calendrier, les annulations suivent la météo et le réseau** — deux phénomènes différents, à piloter séparément. »
- Références : une phrase — « nos sources et outils : le dataset officiel du DOT via Kaggle, la norme des 15 minutes, et Python — pandas, NumPy, SciPy, Matplotlib. Nous passons au notebook. »

---

## PARTIE 2 — Le notebook (~13 min)

*Règle générale : scroller lentement, s'arrêter seulement sur les cellules citées, ne jamais relire le code ligne à ligne. Le prof veut vérifier qu'on sait ce que fait chaque section.*

### A — Sections 1 à 5 (~3 min 30)

- **Sommaire** : « le notebook exécute toute la chaîne : chargement, audit, préparation, les trois hypothèses, exports. »
- **Section 2** : « 592 Mo chargés en types compacts — int8, float32, category — pour tenir en ~350 Mo de mémoire. Des contrôles d'intégrité vérifient qu'on a bien les 5 819 079 vols attendus. »
- **Section 3.1** (s'arrêter sur le tableau croisé) : « la preuve que les retards manquants sont structurels : annulés + déroutés = exactement les 105 071 manquants, zéro inexpliqué. »
- **Section 3.2** : « la détection d'octobre : 100 % des codes numériques concentrés sur ce mois. On quantifie ce que coûte son exclusion — 2,7 % des annulations — avant de décider. »
- **Section 4** : « chaque variable construite est documentée dans un dictionnaire : définitions, types, à quelle hypothèse elle sert. »
- **Section 5** : « le panorama pose un piège classique : le retard **médian** est de −5 minutes — la majorité des vols arrivent en avance — quand la moyenne est à +4,4. C'est pour ça que tout le notebook raisonne en taux de vols en retard, pas en moyenne, qui serait trompeuse. »

### B — Section 6, H1 (~3 min)

- « Nous avons volontairement procédé en trois temps. Le **test naïf** d'abord : 21,9 % de retards pendant les vacances contre 16,9 % hors vacances, +5 points. Significatif ? Attention : sur 5,7 millions de lignes, tout est significatif — la p-value ne prouve plus rien. Nous reportons donc le **V de Cramér** : 0,06, une association réelle mais faible. »
- « La **décomposition** montre pourquoi : l'agrégat "vacances" est composé à 77 % de l'été, et il cache des comportements opposés — Thanksgiving est en dessous de la référence. »
- « D'où le **test contrôlé** : comparer décembre à la moyenne annuelle, c'est mesurer l'hiver, pas les vacances. Chaque fenêtre est donc comparée au reste de son propre mois. Résultat : Nouvel An **+18,3 points**, Noël **+14,8**, l'été +4,1 seulement, et Thanksgiving **−0,8** — aucun effet. La conclusion s'inverse presque : ce ne sont pas les vacances, ce sont les pics courts de fin d'année. »

### C — Section 7, H2 (~3 min)

- « L'hypothèse validée est une affirmation de **composition** : les vols longs porteraient la majorité des retards. Test direct, section 7.1 : ils portent **13,5 % des vols en retard** et **13,1 % des minutes de retard**, pour 13,6 % du trafic. On a testé la sensibilité au seuil : même en appelant "long" tout vol dès 1 000 miles, on plafonne à 29 %. Réfutée sous tous les angles. »
- « Le mécanisme, 7.2 : le taux de retard est quasi plat selon la distance — 18,2 % en dessous de 500 miles, 18,4 % au-delà de 2 000. Et les vols longs **rattrapent** près de 9 minutes en vol : leurs horaires intègrent des marges. La distance ne crée pas de sur-risque. »
- « Restait l'hypothèse indirecte, 7.3 : les compagnies spécialisées en vols longs seraient-elles plus en retard ? Point de méthode : la question porte sur les compagnies, donc l'unité d'analyse est la compagnie — il y en a 14. Tester sur 5,7 millions de vols serait de la pseudo-réplication : les vols d'une même compagnie ne sont pas indépendants. Sur les 14 compagnies : corrélation de −0,18, p = 0,54, R² de 3 % — aucun lien, et même de signe contraire à l'hypothèse. »

### D — Sections 8 à 12, H3 et synthèse (~3 min 30)

- « Le piège de H3 : elle est presque vraie par construction, le trafic lui-même est concentré. Il faut donc comparer la concentration des annulations à celle du trafic : les 10 % de routes en tête portent 50,9 % des annulations… mais déjà 38,7 % des vols. Les indices de Gini résument l'écart : 0,68 contre 0,56. »
- « Le résultat qui résiste, 8.2 : à volume comparable, les 455 routes prioritaires sont annulées à 2,9 % contre 1,1 % ailleurs — un sur-risque de **×2,6**. Et il a un visage : la navette du Nord-Est en hiver — 51,7 % de leurs annulations au premier trimestre, LaGuardia à 4,6 % d'annulations quand Atlanta, premier aéroport mondial, est à 0,7 %. »
- « Robustesse, 8.3 : le résultat ne dépend ni de l'exclusion d'octobre, ni du sens des routes. »
- Sections 9-12, en 30 secondes : « les figures, les exports — 14 CSV, un résumé JSON — et les données du dashboard : tout ce que vous avez vu à l'écran sort d'ici, aucun chiffre n'est écrit à la main, la synthèse finale est générée depuis les variables calculées. »

---

## PARTIE 3 — Questions probables et réponses

**[A] Pourquoi 2015 ? Est-ce généralisable ?** → C'est le dataset de référence publié par le DOT, année complète et propre. Les mécanismes mis en évidence (marges horaires, météo hivernale, modèle low-cost) sont structurels, mais on ne prétend pas extrapoler les chiffres exacts à d'autres années.

**[A] Pourquoi exclure octobre plutôt que convertir les codes ?** → La table de correspondance DOT↔IATA n'est pas dans le dataset. Convertir avec une source externe ajoutait un risque d'erreur ; exclure coûte 2,7 % des annulations et on a vérifié que le résultat H3 n'en dépend pas.

**[A] Pourquoi analyser le retard à l'arrivée plutôt qu'au départ ?** → C'est le retard vécu à destination qui compte pour le passager ; et l'écart entre départ et arrivée mesure le rattrapage en vol, exploité dans H2.

**[A] Que contiennent les colonnes que vous n'avez pas chargées ?** → Le détail opérationnel : roulage (TAXI_OUT/IN), heures réelles de décollage et d'atterrissage (WHEELS_OFF/ON), durées (SCHEDULED_TIME, ELAPSED_TIME, AIR_TIME), immatriculation (TAIL_NUMBER). Rien qui serve nos trois hypothèses — et 12 colonnes de moins, c'est autant de mémoire économisée.

**[A] Comment fonctionnent les 5 colonnes de causes de retard ?** → Elles ne sont renseignées que pour les vols arrivés avec 15 minutes ou plus de retard, et ventilent les minutes par responsabilité. Leur agrégation donne le panorama : l'avion précédent en retard est la première source de minutes de retard ; la météo est le premier motif d'annulation (54 %).

**[A] Médiane négative, comment l'expliquer ?** → La distribution des retards est asymétrique : beaucoup de petites avances, une minorité de gros retards qui tirent la moyenne. C'est exactement le cas d'école moyenne/médiane du cours.

**[B] C'est quoi le V de Cramér ?** → La force d'une association entre deux variables qualitatives, de 0 à 1, dérivée du chi². On l'utilise parce qu'avec 5,7 millions d'observations, la p-value du chi² est toujours minuscule — elle dit qu'un effet existe, pas qu'il compte.

**[B] Pourquoi comparer au "reste du même mois" ?** → Pour neutraliser la saison : décembre contre la moyenne annuelle mesure l'hiver + les vacances ; décembre-fêtes contre décembre-hors-fêtes isole l'effet fêtes.

**[B] Le dashboard montre les taux bruts, le notebook l'effet net — pourquoi ?** → Le dashboard vise un public non technique : les taux bruts sont lisibles et vont dans le même sens. L'analyse rigoureuse est dans le notebook, et le classement affiché reste factuellement exact.

**[C] Pourquoi 1 500 miles ?** → Seuil au-delà duquel un vol traverse une bonne partie du pays. Et la conclusion ne dépend pas du choix : testée à 1 000 et 2 000 miles.

**[C] Pourquoi tester sur 14 compagnies plutôt que 5,7 M de vols ?** → Les vols d'une même compagnie partagent réseau, flotte et règles : ce ne sont pas des observations indépendantes. Les traiter comme telles fabrique de la significativité artificielle — c'est la pseudo-réplication. D'ailleurs le test au niveau vol donne p < 0,001 pour un écart de 0,3 point sans aucune portée pratique : l'exemple parfait.

**[C] L'axe Y du nuage commence à 8 %, pas à 0 — pourquoi ?** → Choix assumé de lisibilité : sur un nuage de points, la position encode la valeur, pas une longueur depuis zéro — tronquer est admis (contrairement aux barres). Aucune compagnie n'est sous 11 %.

**[D] La courbe de Lorenz, c'est quoi ?** → On classe les routes de la plus à la moins annulée ; la courbe donne la part cumulée des annulations. Superposée à la même courbe pour le trafic, l'écart entre les deux est la vraie information. Le Gini résume chaque courbe en un chiffre : 0 = uniforme, 1 = tout concentré.

**[D] Pourquoi un minimum de 365 vols pour les routes risquées ?** → Environ un vol par jour : sans ce seuil, une route à 4 vols dont 1 annulé sortirait en tête avec 25 %. Le seuil est celui du notebook, le dashboard affiche la même liste.

**[A ou C] Pourquoi pas de K-means ou d'ACP, vus en cours ?** → Les hypothèses ont dicté les méthodes : aucune des trois n'est une question de segmentation ni de réduction de dimension. Plaquer un algorithme pour cocher une case aurait été précisément le triturage de données contre lequel le cours met en garde.

**[D, relais C] La carte, comment est-elle faite ?** → C'est la projection standard des États-Unis (Albers, qui préserve les surfaces), recalculée en Python à l'export pour que le dashboard fonctionne hors ligne, sans librairie externe ni connexion. C'est de l'outillage, pas une analyse — le code est commenté ligne à ligne. *(Si le prof insiste sur le code : Dan — personne A — reprend.)*

**[tous] Qu'est-ce qui vous a le plus surpris ?** → Réponse libre — bons candidats : Thanksgiving sans effet, les vols longs qui arrivent plus en avance que les courts, Atlanta 6 fois plus fiable que LaGuardia.

---

## Coordination

- **Tronc commun** (les 4 doivent le savoir par cœur) : les 3 hypothèses mot pour mot, leurs verdicts (confirmée à préciser / réfutée / confirmée à nuancer), et les 4 KPI du bandeau (5,82 M · 18,6 % · 1,5 % · 9,7 %).
- Une seule règle de relais : question de code sur la carte → Dan. Tout le reste : celui dont c'est le territoire répond, les autres n'interrompent pas.
- Si une démo plante : le PPT contient la capture du dashboard en slide 5 — continuer sur la capture sans s'excuser plus d'une phrase.
- Dernière phrase (D) : « Merci — nous pouvons maintenant détailler n'importe quelle partie du notebook. »
