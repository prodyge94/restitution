# Script de soutenance — US Flight Delays and Cancellations 2015

**Durée : 30 min · 4 intervenants · PowerPoint + démonstration + notebook**

Rôles : **A = Dan** = données & méthode · **B** = H1 (calendrier) · **C** = H2 (vols longs) · **D** = H3 (routes) + conclusion.
Pour B, C, D (Medy, Ahmed, Robin) : mettre sur C celui qui avait travaillé H2 à l'origine, sur B le plus à l'aise en statistiques (chi², V de Cramér), sur D le plus à l'aise en narration.
Chacun pilote l'écran pendant son passage. Tous les chiffres ci-dessous sont exacts (issus de `resume_v2.json` regénéré).

## Minutage

| Séquence | Qui | Durée |
|---|---|---|
| Slides 1-3 : titre, dataset, traitements | A | 4 min |
| Slide 4 : les 3 hypothèses | B, C, D | 1 min |
| Slide 5 + démo du dashboard en direct | B → C → D | 5 min |
| Slides 6-7 : conclusion, références | D | 2 min |
| Notebook : sections 1-5 → 6 → 7 → 8-12 | A → B → C → D | 13 min |
| Marge pour les questions | tous | 5 min |

**Avant de commencer** : dashboard.html ouvert dans un onglet (double-clic, pas besoin de serveur), notebook ouvert et déjà exécuté, PPT en mode présentation. Vérifier le vidéoprojecteur avec le dashboard : si les couleurs passent mal, augmenter la luminosité.

---

## PARTIE 1 — Le PowerPoint (~12 min)

### A — Slide 1 (titre) — 30 s

« Bonjour. Nous allons vous présenter notre projet de reporting sur les retards et annulations des vols intérieurs américains en 2015. Notre question de départ : quand, qui et où — quand les retards frappent-ils, quelles compagnies sont touchées, et où se concentrent les annulations. Je commence par les données et leur préparation, puis chacun présentera l'hypothèse qu'il a instruite, nous vous ferons visiter le dashboard, et nous terminerons par les conclusions avant de vous montrer le notebook. »

### A — Slide 2 (dataset) — 2 min

- « Le dataset vient de Kaggle, publié par le ministère américain des transports : **5 819 079 vols**, tous les vols intérieurs américains de 2015, en **31 colonnes**. »
- « Trois fichiers croisés par le code IATA : le fichier des vols (592 Mo), l'annuaire des 14 compagnies, et les 322 aéroports avec leurs coordonnées — c'est ce qui nous permet la carte du dashboard. »
- Montrer l'extrait réel : « chaque ligne est un vol programmé. Vous voyez ici quatre vols réels : un Southwest à l'heure, un Spirit arrivé avec 85 minutes de retard, un JetBlue Boston→Chicago annulé pour météo en février, et un Delta New York→Los Angeles de 2 475 miles arrivé en avance. Retenez ces quatre-là : ils annoncent déjà toute la suite. »
- Balayer les colonnes clés : « ARRIVAL_DELAY, le retard à l'arrivée en minutes — négatif signifie en avance ; CANCELLED et son motif ; DISTANCE qui nous servira à définir les vols longs. »

### A — Slide 3 (traitements) — 2 min

- « Trois étapes de traitement. D'abord **nettoyer** : l'audit a révélé 105 071 retards manquants. Ce n'est pas du bruit : ce sont exactement les 89 884 vols annulés plus les 15 187 déroutés — un vol annulé n'a pas de retard d'arrivée. Si on ne les exclut pas, ils sont comptés comme des vols à l'heure. Deuxième découverte : en octobre, les aéroports sont codés avec un autre référentiel, inexploitable — nous avons écarté ce mois uniquement pour l'analyse des routes, il ne porte que 2,7 % des annulations. »
- « Ensuite **construire** : un vol est en retard à partir de 15 minutes à l'arrivée — c'est la norme officielle du régulateur américain, pas notre choix ; un vol long fait 1 500 miles ou plus ; nous avons construit les fenêtres de vacances 2015 et les routes origine→destination. »
- « Enfin **analyser** : agrégations par jour, compagnie et route ; et surtout des comparaisons contrôlées — chaque résultat est confronté à une référence comparable et testé sur d'autres seuils. Tout est reproductible : le notebook regénère l'intégralité — tableaux, graphiques et dashboard — en moins de deux minutes. »

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
