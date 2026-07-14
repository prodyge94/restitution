# Rapport - Analyse des retards des vols aeriens US 2015
**ESGI 2025-2026 - Reporting et Restitution des donnees - A. Biam**

---

## 1. Resume

Nous analysons **5 819 079 vols interieurs americains en 2015**, issus du dataset USDOT/Kaggle. Le projet cherche a expliquer les retards selon quatre angles : le temps, les compagnies, les routes aeriennes et les aeroports.

Globalement, **17,9 %** des vols arrivent en retard d'au moins 15 minutes, **1,5 %** sont annules, et le retard moyen a l'arrivee est de **+4,4 minutes**. La mediane est negative (**-5 minutes**), ce qui montre que beaucoup de vols arrivent a l'heure ou en avance, mais qu'une minorite de gros retards tire la moyenne vers le haut.

Le nouvel axe central est l'analyse des **routes aeriennes**. Une compagnie ou un aeroport peut avoir une moyenne correcte, mais certaines liaisons precises peuvent concentrer beaucoup de retards. C'est donc un angle plus operationnel.

---

## 2. Donnees et methode

Les donnees brutes sont :

- `flights.csv` : 5,8 millions de vols, horaires, retards, annulations, distances et causes de retard.
- `airlines.csv` : noms des compagnies.
- `airports.csv` : informations geographiques des aeroports.

Le pipeline suit le cours :

> Collection -> Integration -> Selection -> Pretraitement -> Transformation -> Algorithmes -> Interpretation -> Representation.

Le nettoyage a permis de verifier :

- **0 doublon** sur les vols.
- Les valeurs manquantes sont surtout **structurelles** : les causes de retard ne sont renseignees que quand un vol est effectivement en retard.
- En octobre 2015, environ **486 000 codes aeroports** sont mal codes en numerique. Ils sont exclus des analyses geographiques.
- Les retards sont tres asymetriques : on utilise donc la moyenne, mais aussi la mediane, les taux et les percentiles.

---

## 3. H1 - Les retards dependent du moment

**Question :** les retards changent-ils selon le mois et l'heure ?

Les resultats montrent un effet clair :

- pic de retard en **juin** et **fevrier** ;
- fevrier a aussi un fort taux d'annulation ;
- les vols du matin sont souvent plus ponctuels ;
- le retard augmente au fil de la journee, surtout en fin d'apres-midi et le soir.

**Conclusion :** H1 est validee. Les retards ne sont pas aleatoires : ils s'accumulent dans le temps, notamment par effet de cascade quand un avion deja en retard enchaine plusieurs vols.

---

## 4. H2 - La compagnie influence la ponctualite

**Question :** certaines compagnies sont-elles plus souvent en retard ?

Le test du chi-2 montre que la ponctualite n'est pas independante de la compagnie. Les compagnies les plus en retard sont notamment **Spirit** et **Frontier**, tandis que **Hawaiian**, **Alaska** et **Delta** sont plus ponctuelles.

Mais le Cramer's V reste faible/modere : la compagnie compte, mais elle n'explique pas tout.

Les causes de retard montrent aussi que la premiere cause est souvent **l'avion precedent en retard**, devant la meteo. Cela relie H2 a H1 : les retards se propagent.

**Conclusion :** H2 est validee, mais avec nuance. La compagnie influence le retard, mais le moment, les routes et les aeroports jouent aussi un role important.

---

## 5. H3 - Les routes aeriennes concentrent les retards

**Question :** quelles liaisons origine -> destination sont les plus problematiques ?

Cette nouvelle version donne une place centrale aux routes aeriennes. Pour chaque route, on calcule :

- le nombre de vols ;
- le retard moyen a l'arrivee ;
- le retard median ;
- le taux de vols en retard ;
- le taux d'annulation ;
- la distance ;
- un **score de sensibilite** : volume de vols x taux de retard.

Ce score est important car une route peut etre problematique de deux manieres :

- soit elle a un retard moyen tres eleve ;
- soit elle a un volume enorme, donc meme un taux de retard moyen touche beaucoup de passagers.

Dans les resultats, **SFO -> LAX** ressort comme une route tres sensible : beaucoup de vols, un taux de retard eleve, et un retard moyen d'environ **11,4 minutes**. D'autres routes comme **LAX -> SFO** ou certaines routes depuis de grands hubs montrent aussi une forte exposition au retard.

**Conclusion :** H3 devient un axe majeur. L'analyse par route permet de passer d'une vision globale a une vision operationnelle : on identifie les trajets qui concentrent le plus de risque pour les passagers.

---

## 6. H4 - Les aeroports ont des profils differents

L'analyse des aeroports reste utile en complement. Avec K-means, les aeroports sont regroupes selon leur volume, retard moyen, taux de retard, annulation et taxi-out.

On obtient trois profils :

- aeroports congestionnes avec retards eleves ;
- aeroports instables avec annulations elevees ;
- aeroports ponctuels et fiables.

**Conclusion :** cette analyse explique en partie pourquoi certaines routes sont plus sensibles : elles passent souvent par des hubs congestionnes.

---

## 7. Limites

- Donnees limitees a l'annee 2015.
- Les codes aeroports defectueux d'octobre limitent l'analyse geographique.
- Les routes sont analysees avec des agregats, pas avec les correspondances passagers.
- Le score de sensibilite est simple et interpretable, mais il ne mesure pas directement le cout economique ou l'impact client.

---

## 8. Conclusion generale

Le retard aerien est un phenomene cumulatif. Il depend du moment, de la compagnie, des aeroports, mais surtout certaines **routes aeriennes** concentrent fortement le probleme.

La nouvelle version du projet met donc en avant une lecture plus concrete : **quelles liaisons posent le plus de risque de retard ?** C'est plus utile pour comprendre l'experience passager et pour proposer des recommandations operationnelles.
