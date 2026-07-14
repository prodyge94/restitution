# -*- coding: utf-8 -*-
"""
ESGI 2025-2026 - Reporting & Restitution des donnees (A. Biam)
Projet : Analyse des retards des vols aeriens domestiques US (USDOT, 2015)

ETAPE 2 du processus de restitution :
   Application des ALGORITHMES -> Interpretation -> (preparation) Representation

Contenu (aligne sur le cours) :
  - Analyse UNIVARIEE : distribution, skewness & kurtosis (scipy.stats)
  - H1 (temporel)   : saisonnalite mensuelle + cycle horaire des retards
  - H2 (qualitatif) : test du CHI-2 d'independance compagnie x retard + causes
  - H3 (algorithme) : K-MEANS sur les aeroports (elbow + silhouette + standardisation)
  - Export des agregats prets pour Tableau Public (data/processed/tableau_*.csv)
  - Figures matplotlib (analyse/figures) pour le rapport / la soutenance
"""
import sys, os, json, time
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW  = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")
FIG  = os.path.join(BASE, "analyse", "figures")
OUT  = os.path.join(BASE, "analyse", "sorties")
for d in (PROC, FIG, OUT):
    os.makedirs(d, exist_ok=True)
R = {}

MOIS = {1:"01-Jan",2:"02-Fev",3:"03-Mar",4:"04-Avr",5:"05-Mai",6:"06-Juin",
        7:"07-Juil",8:"08-Aout",9:"09-Sep",10:"10-Oct",11:"11-Nov",12:"12-Dec"}
JOURS = {1:"1-Lundi",2:"2-Mardi",3:"3-Mercredi",4:"4-Jeudi",5:"5-Vendredi",6:"6-Samedi",7:"7-Dimanche"}

print("[0] Lecture du parquet nettoye ...")
df = pd.read_parquet(os.path.join(PROC, "flights_clean.parquet"))
airlines = pd.read_csv(os.path.join(RAW, "airlines.csv"))          # IATA_CODE, AIRLINE
airports = pd.read_csv(os.path.join(RAW, "airports.csv"))          # IATA_CODE, AIRPORT, CITY, STATE, LAT, LON
name_map = dict(zip(airlines.IATA_CODE, airlines.AIRLINE))
valid = df[df.IS_VALID].copy()                                     # ni annule ni deroute
print(f"    {len(df):,} vols  |  {len(valid):,} valides")

# ─────────────────────────────────────────────────────────────────────────────
# A. ANALYSE UNIVARIEE  -  skewness & kurtosis (cours, scipy.stats)
# ─────────────────────────────────────────────────────────────────────────────
R["univarie"] = {}
for col in ["ARRIVAL_DELAY", "DEPARTURE_DELAY", "DISTANCE", "TAXI_OUT"]:
    s = df[col].dropna().to_numpy(dtype="float64")
    R["univarie"][col] = {
        "moyenne": round(float(s.mean()), 2),
        "mediane": round(float(np.median(s)), 2),
        "ecart_type": round(float(s.std()), 2),
        "skewness": round(float(stats.skew(s)), 3),
        "kurtosis_excess": round(float(stats.kurtosis(s)), 3),  # 0 = normale
    }
# Figure : distribution du retard a l'arrivee (zoom lisible)
s = df["ARRIVAL_DELAY"].dropna()
plt.figure(figsize=(8, 4.5))
plt.hist(s[(s > -60) & (s < 180)], bins=120, color="#4C78A8", edgecolor="none")
plt.axvline(0, color="grey", lw=1, ls="--")
plt.axvline(15, color="#E45756", lw=1.2, ls="--", label="seuil retard = 15 min")
plt.title("Distribution du retard a l'arrivee (min) — asymetrie positive")
plt.xlabel("Retard a l'arrivee (minutes)"); plt.ylabel("Nombre de vols")
plt.legend(); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_hist_retard_arrivee.png"), dpi=110); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# H1. TEMPOREL  -  saisonnalite (mois) + cycle horaire
# ─────────────────────────────────────────────────────────────────────────────
# -- mensuel
m_valid = valid.groupby("MONTH").agg(
    n_vols=("ARRIVAL_DELAY", "size"),
    retard_moyen_arr=("ARRIVAL_DELAY", "mean"),
    taux_retard_arr=("IS_DELAYED_ARR", "mean"),
).reset_index()
m_cancel = df.groupby("MONTH")["CANCELLED"].mean().rename("taux_annulation").reset_index()
mensuel = m_valid.merge(m_cancel, on="MONTH")
mensuel["taux_retard_arr"] *= 100
mensuel["taux_annulation"] *= 100
mensuel["retard_moyen_arr"] = mensuel["retard_moyen_arr"].round(2)
mensuel["MOIS"] = mensuel["MONTH"].map(MOIS)
mensuel.round(3).to_csv(os.path.join(PROC, "tableau_mensuel.csv"), index=False)

# -- horaire
horaire = valid.groupby("DEP_HOUR").agg(
    n_vols=("ARRIVAL_DELAY", "size"),
    retard_moyen_arr=("ARRIVAL_DELAY", "mean"),
    taux_retard_arr=("IS_DELAYED_ARR", "mean"),
).reset_index()
horaire["taux_retard_arr"] *= 100
horaire.round(3).to_csv(os.path.join(PROC, "tableau_horaire.csv"), index=False)

# -- heatmap jour x heure (pour Tableau)
heat = valid.groupby(["DAY_OF_WEEK", "DEP_HOUR"]).agg(
    n_vols=("ARRIVAL_DELAY", "size"),
    retard_moyen_arr=("ARRIVAL_DELAY", "mean"),
).reset_index()
heat["JOUR"] = heat["DAY_OF_WEEK"].map(JOURS)
heat.round(3).to_csv(os.path.join(PROC, "tableau_heatmap_jour_heure.csv"), index=False)

# correlation heure -> retard (Spearman, support de H1)
sp = stats.spearmanr(horaire["DEP_HOUR"], horaire["retard_moyen_arr"])
R["H1"] = {
    "pire_mois": MOIS[int(mensuel.loc[mensuel.retard_moyen_arr.idxmax(), "MONTH"])],
    "meilleur_mois": MOIS[int(mensuel.loc[mensuel.retard_moyen_arr.idxmin(), "MONTH"])],
    "retard_max_mois": float(mensuel.retard_moyen_arr.max()),
    "retard_min_mois": float(mensuel.retard_moyen_arr.min()),
    "corr_spearman_heure_retard": round(float(sp.statistic), 3),
    "corr_pvalue": float(sp.pvalue),
    "retard_5h": float(horaire.loc[horaire.DEP_HOUR == 5, "retard_moyen_arr"].mean()),
    "retard_19h": float(horaire.loc[horaire.DEP_HOUR == 19, "retard_moyen_arr"].mean()),
}
# Figures H1
plt.figure(figsize=(9, 4.2))
plt.plot(mensuel["MONTH"], mensuel["retard_moyen_arr"], "-o", color="#4C78A8")
plt.xticks(range(1, 13), [MOIS[m][3:] for m in range(1, 13)], rotation=0)
plt.title("H1 — Retard moyen a l'arrivee par mois (saisonnalite)")
plt.ylabel("Retard moyen (min)"); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h1_retard_mensuel.png"), dpi=110); plt.close()

plt.figure(figsize=(9, 4.2))
plt.plot(horaire["DEP_HOUR"], horaire["retard_moyen_arr"], "-o", color="#F58518")
plt.title("H1 — Retard moyen a l'arrivee par heure de depart programmee")
plt.xlabel("Heure de depart (0-23)"); plt.ylabel("Retard moyen (min)")
plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h1_retard_horaire.png"), dpi=110); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# H2. COMPAGNIE  -  test du CHI-2 d'independance + classement + causes
# ─────────────────────────────────────────────────────────────────────────────
ct = pd.crosstab(valid["AIRLINE"], valid["IS_DELAYED_ARR"])
chi2, p, dof, _ = chi2_contingency(ct)
n = ct.to_numpy().sum()
cramers_v = float(np.sqrt(chi2 / n))     # k=2 -> min(r,c)-1 = 1
R["H2"] = {
    "chi2": round(float(chi2), 1), "p_value": float(p), "dof": int(dof),
    "cramers_v": round(cramers_v, 3), "n": int(n),
    "independance_rejetee": bool(p < 0.05),
}
comp = valid.groupby("AIRLINE").agg(
    n_vols=("ARRIVAL_DELAY", "size"),
    retard_moyen_arr=("ARRIVAL_DELAY", "mean"),
    taux_retard_arr=("IS_DELAYED_ARR", "mean"),
).reset_index()
comp_cancel = df.groupby("AIRLINE")["CANCELLED"].mean().rename("taux_annulation").reset_index()
comp = comp.merge(comp_cancel, on="AIRLINE")
comp["compagnie"] = comp["AIRLINE"].map(name_map)
comp["taux_retard_arr"] *= 100
comp["taux_annulation"] *= 100
comp = comp.sort_values("taux_retard_arr", ascending=False)
comp.round(3).to_csv(os.path.join(PROC, "tableau_compagnies.csv"), index=False)
R["H2"]["pire_compagnie"] = comp.iloc[0]["compagnie"]
R["H2"]["meilleure_compagnie"] = comp.iloc[-1]["compagnie"]
R["H2"]["taux_retard_max"] = round(float(comp.taux_retard_arr.max()), 2)
R["H2"]["taux_retard_min"] = round(float(comp.taux_retard_arr.min()), 2)

# Causes de retard (minutes attribuees) - global + par compagnie
causes = ["AIR_SYSTEM_DELAY", "SECURITY_DELAY", "AIRLINE_DELAY", "LATE_AIRCRAFT_DELAY", "WEATHER_DELAY"]
causes_fr = {"AIR_SYSTEM_DELAY":"Systeme aerien","SECURITY_DELAY":"Securite",
             "AIRLINE_DELAY":"Compagnie","LATE_AIRCRAFT_DELAY":"Avion en retard","WEATHER_DELAY":"Meteo"}
tot = df[causes].sum()
g = pd.DataFrame({"cause": [causes_fr[c] for c in causes],
                  "minutes_totales": tot.values,
                  "part_pct": (tot.values / tot.values.sum() * 100).round(2)})
g.sort_values("minutes_totales", ascending=False).to_csv(
    os.path.join(PROC, "tableau_causes_global.csv"), index=False)
R["H2"]["cause_principale"] = g.sort_values("minutes_totales", ascending=False).iloc[0]["cause"]

# causes par compagnie (part en %)
cc = df.groupby("AIRLINE")[causes].sum()
cc_pct = cc.div(cc.sum(axis=1), axis=0) * 100
cc_pct = cc_pct.rename(columns=causes_fr).reset_index()
cc_pct["compagnie"] = cc_pct["AIRLINE"].map(name_map)
cc_pct.round(2).to_csv(os.path.join(PROC, "tableau_causes_par_compagnie.csv"), index=False)

# Figures H2
plt.figure(figsize=(9, 5))
plt.barh(comp["compagnie"], comp["taux_retard_arr"], color="#4C78A8")
plt.gca().invert_yaxis()
plt.title("H2 — Taux de vols en retard (>15 min) par compagnie")
plt.xlabel("% de vols en retard a l'arrivee"); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h2_retard_compagnie.png"), dpi=110); plt.close()

plt.figure(figsize=(7, 4.5))
gs = g.sort_values("minutes_totales", ascending=True)
plt.barh(gs["cause"], gs["minutes_totales"] / 1e6, color="#72B7B2")
plt.title("H2 — Causes de retard (millions de minutes cumulees, 2015)")
plt.xlabel("Millions de minutes"); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h2_causes.png"), dpi=110); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# H3. K-MEANS  -  segmentation des aeroports (elbow + silhouette + standardisation)
# ─────────────────────────────────────────────────────────────────────────────
nonnum = valid[~valid["ORIGIN_IS_NUMERIC"]].copy()
nonnum["ORIGIN_AIRPORT"] = nonnum["ORIGIN_AIRPORT"].astype("string")
ap = nonnum.groupby("ORIGIN_AIRPORT").agg(
    n_dep=("DEPARTURE_DELAY", "size"),
    retard_moyen_dep=("DEPARTURE_DELAY", "mean"),
    taux_retard_dep=("IS_DELAYED_DEP", "mean"),
    taxi_out_moyen=("TAXI_OUT", "mean"),
).reset_index()
ap_cancel = df[~df["ORIGIN_IS_NUMERIC"]].copy()
ap_cancel["ORIGIN_AIRPORT"] = ap_cancel["ORIGIN_AIRPORT"].astype("string")
ap_cancel = ap_cancel.groupby("ORIGIN_AIRPORT")["CANCELLED"].mean().rename("taux_annulation").reset_index()
ap = ap.merge(ap_cancel, on="ORIGIN_AIRPORT")
ap = ap[ap["n_dep"] >= 365]                      # aeroports avec >= ~1 vol/jour (stats stables)
ap = ap.merge(airports, left_on="ORIGIN_AIRPORT", right_on="IATA_CODE", how="left")
ap = ap.dropna(subset=["LATITUDE", "LONGITUDE"])  # garde ceux geolocalisables
R["H3"] = {"n_aeroports_clusterises": int(len(ap))}

feat_cols = ["log_volume", "retard_moyen_dep", "taux_retard_dep", "taux_annulation", "taxi_out_moyen"]
ap["log_volume"] = np.log10(ap["n_dep"])          # volume tres asymetrique -> log (transformation cours)
X = StandardScaler().fit_transform(ap[feat_cols])  # standardisation (eviter biais d'echelle)

inerties, silhouettes = {}, {}
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    inerties[k] = round(float(km.inertia_), 2)
    silhouettes[k] = round(float(silhouette_score(X, km.labels_)), 3)
R["H3"]["inerties"] = inerties
R["H3"]["silhouettes"] = silhouettes
k_opt = max(silhouettes, key=silhouettes.get)
R["H3"]["k_silhouette_optimal"] = int(k_opt)

K = max(3, min(4, R["H3"]["k_silhouette_optimal"]))   # k optimal (silhouette), borne a [3;4]
km = KMeans(n_clusters=K, n_init=10, random_state=42).fit(X)
ap["cluster"] = km.labels_
R["H3"]["k_retenu"] = int(K)
R["H3"]["silhouette_k_retenu"] = silhouettes[K]

# Profil moyen (centroides en valeurs reelles) de chaque cluster
prof = ap.groupby("cluster").agg(
    n=("IATA_CODE", "size"),
    volume_moyen=("n_dep", "mean"),
    log_volume=("log_volume", "mean"),
    retard_moyen_dep=("retard_moyen_dep", "mean"),
    taux_retard_dep=("taux_retard_dep", "mean"),
    taux_annulation=("taux_annulation", "mean"),
    taxi_out_moyen=("taxi_out_moyen", "mean"),
)
# Nommage par SIGNATURE OPERATIONNELLE (retard / annulation), pas par la taille :
# le volume n'est pas le facteur discriminant principal -> c'est un resultat en soi.
if K == 3:
    c_cancel = prof["taux_annulation"].idxmax()                           # annulations elevees
    c_delay  = prof.drop(index=c_cancel)["retard_moyen_dep"].idxmax()     # retards eleves
    c_fiable = [i for i in prof.index if i not in (c_cancel, c_delay)][0] # ponctuel & fiable
    noms = {c_fiable: "Aeroports ponctuels et fiables",
            c_delay:  "Aeroports congestionnes (retards eleves)",
            c_cancel: "Aeroports instables (annulations elevees)"}
else:
    rang = prof["retard_moyen_dep"].rank().astype(int)
    noms = {i: f"Cluster {i} (retard rang {rang[i]}/{K})" for i in prof.index}
prof["nom"] = prof.index.map(noms)
ap["cluster_nom"] = ap["cluster"].map(prof["nom"])
prof.round(2).reset_index().to_csv(os.path.join(PROC, "tableau_clusters_profil.csv"), index=False)
R["H3"]["profils"] = {int(i): {"nom": prof.loc[i, "nom"], "n_aeroports": int(prof.loc[i, "n"]),
        "volume_moyen": round(float(prof.loc[i, "volume_moyen"]), 0),
        "retard_moyen_dep": round(float(prof.loc[i, "retard_moyen_dep"]), 2),
        "taux_retard_dep_pct": round(float(prof.loc[i, "taux_retard_dep"]) * 100, 1)} for i in prof.index}

export_cols = ["IATA_CODE","AIRPORT","CITY","STATE","LATITUDE","LONGITUDE",
               "n_dep","retard_moyen_dep","taux_retard_dep","taux_annulation",
               "taxi_out_moyen","cluster","cluster_nom"]
ap_out = ap[export_cols].copy()
ap_out["taux_retard_dep"] *= 100
ap_out["taux_annulation"] *= 100
ap_out.round(3).to_csv(os.path.join(PROC, "tableau_aeroports.csv"), index=False)

# Figures H3
plt.figure(figsize=(7, 4.2))
ks = list(inerties)
plt.plot(ks, [inerties[k] for k in ks], "-o", label="Inertie (elbow)", color="#4C78A8")
plt.twinx().plot(ks, [silhouettes[k] for k in ks], "-s", color="#E45756", label="Silhouette")
plt.title("H3 — Choix de k : methode du coude + silhouette")
plt.xlabel("Nombre de clusters k"); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h3_elbow_silhouette.png"), dpi=110); plt.close()

palette = {0:"#4C78A8",1:"#F58518",2:"#54A24B",3:"#E45756"}
plt.figure(figsize=(7.5, 5))
for c in sorted(ap["cluster"].unique()):
    sub = ap[ap.cluster == c]
    plt.scatter(sub["n_dep"], sub["retard_moyen_dep"], s=18, alpha=.7,
                color=palette.get(c, "#888"), label=prof.loc[c, "nom"])
plt.xscale("log"); plt.xlabel("Volume de departs (log)"); plt.ylabel("Retard moyen au depart (min)")
plt.title("H3 — Archetypes d'aeroports (K-means)"); plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h3_clusters_scatter.png"), dpi=110); plt.close()

plt.figure(figsize=(9, 5.2))
for c in sorted(ap["cluster"].unique()):
    sub = ap[(ap.cluster == c) & (ap.LONGITUDE > -130) & (ap.LONGITUDE < -65)]  # zoom USA continental
    plt.scatter(sub["LONGITUDE"], sub["LATITUDE"], s=sub["n_dep"]/1500+5, alpha=.7,
                color=palette.get(c, "#888"), label=prof.loc[c, "nom"])
plt.title("H3 — Carte des archetypes d'aeroports (taille = volume)")
plt.xlabel("Longitude"); plt.ylabel("Latitude"); plt.legend(fontsize=8); plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h3_clusters_carte.png"), dpi=110); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# B. ROUTES + ECHANTILLON (pour viz ad-hoc Tableau)
# ─────────────────────────────────────────────────────────────────────────────
rt = nonnum.copy()
rt["DESTINATION_AIRPORT"] = rt["DESTINATION_AIRPORT"].astype("string")
airport_info = airports.rename(columns={
    "IATA_CODE": "code",
    "AIRPORT": "nom",
    "CITY": "ville",
    "STATE": "etat",
    "LATITUDE": "lat",
    "LONGITUDE": "lon",
})
routes = rt.groupby(["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"]).agg(
    n_vols=("ARRIVAL_DELAY", "size"),
    retard_moyen_arr=("ARRIVAL_DELAY", "mean"),
    retard_median_arr=("ARRIVAL_DELAY", "median"),
    taux_retard_arr=("IS_DELAYED_ARR", "mean"),
    distance=("DISTANCE", "first"),
).reset_index()
route_cancel = df[~df["ORIGIN_IS_NUMERIC"]].copy()
route_cancel["ORIGIN_AIRPORT"] = route_cancel["ORIGIN_AIRPORT"].astype("string")
route_cancel["DESTINATION_AIRPORT"] = route_cancel["DESTINATION_AIRPORT"].astype("string")
route_cancel = route_cancel.groupby(["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"])["CANCELLED"].mean().rename("taux_annulation").reset_index()
routes = routes.merge(route_cancel, on=["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"], how="left")
routes = routes[routes["n_vols"] >= 365].copy()
routes["taux_retard_arr"] *= 100
routes["taux_annulation"] *= 100
routes["route"] = routes["ORIGIN_AIRPORT"].astype(str) + " -> " + routes["DESTINATION_AIRPORT"].astype(str)
routes["score_sensibilite"] = routes["n_vols"] * routes["taux_retard_arr"] / 100
routes = routes.merge(airport_info.add_prefix("origin_"), left_on="ORIGIN_AIRPORT", right_on="origin_code", how="left")
routes = routes.merge(airport_info.add_prefix("dest_"), left_on="DESTINATION_AIRPORT", right_on="dest_code", how="left")
routes = routes.sort_values(["score_sensibilite", "n_vols"], ascending=False).head(300)
routes.round(3).to_csv(os.path.join(PROC, "tableau_routes.csv"), index=False)

R["H3_routes"] = {
    "n_routes_analysees": int(len(routes)),
    "route_plus_sensible": str(routes.iloc[0]["route"]),
    "volume_route_plus_sensible": int(routes.iloc[0]["n_vols"]),
    "taux_retard_route_plus_sensible": round(float(routes.iloc[0]["taux_retard_arr"]), 2),
    "retard_moyen_route_plus_sensible": round(float(routes.iloc[0]["retard_moyen_arr"]), 2),
    "route_plus_frequentee": str(routes.sort_values("n_vols", ascending=False).iloc[0]["route"]),
    "route_retard_moyen_max": str(routes.sort_values("retard_moyen_arr", ascending=False).iloc[0]["route"]),
}

top_routes = routes.sort_values("score_sensibilite", ascending=True).tail(15)
plt.figure(figsize=(9, 5.5))
plt.barh(top_routes["route"], top_routes["score_sensibilite"], color="#E45756")
plt.title("H3 - Routes aeriennes les plus sensibles (volume x taux de retard)")
plt.xlabel("Score de sensibilite: vols x taux de retard")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h3_routes_sensibles.png"), dpi=110); plt.close()

plt.figure(figsize=(8, 5))
plt.scatter(routes["n_vols"], routes["retard_moyen_arr"],
            s=np.clip(routes["taux_retard_arr"], 5, 40) * 3,
            alpha=.55, color="#F58518")
plt.xlabel("Volume annuel de vols")
plt.ylabel("Retard moyen arrivee (min)")
plt.title("H3 - Routes: volume vs retard moyen")
plt.grid(alpha=.25)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig_h3_routes_volume_retard.png"), dpi=110); plt.close()

ech = valid.sample(min(250000, len(valid)), random_state=42)[
    ["DATE","MONTH","DAY_OF_WEEK","DEP_HOUR","AIRLINE","ORIGIN_AIRPORT","DESTINATION_AIRPORT",
     "DEPARTURE_DELAY","ARRIVAL_DELAY","DISTANCE","IS_DELAYED_ARR"]].copy()
ech["compagnie"] = ech["AIRLINE"].map(name_map)
ech.to_csv(os.path.join(PROC, "tableau_echantillon.csv"), index=False)

# ─────────────────────────────────────────────────────────────────────────────
# C. KPI de l'ECRAN DE RESUME
# ─────────────────────────────────────────────────────────────────────────────
R["kpi_resume"] = {
    "total_vols": int(len(df)),
    "total_compagnies": int(df["AIRLINE"].nunique()),
    "total_aeroports_origine": int(df["ORIGIN_AIRPORT"].nunique()),
    "taux_retard_arr_pct": round(float(valid["IS_DELAYED_ARR"].mean()) * 100, 2),
    "taux_annulation_pct": round(float(df["CANCELLED"].mean()) * 100, 2),
    "retard_moyen_arr_min": round(float(valid["ARRIVAL_DELAY"].mean()), 2),
}
R["runtime_sec"] = round(time.time() - T0, 1)
with open(os.path.join(OUT, "02_analyse.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, indent=2, ensure_ascii=False, default=str)

print("[OK] Analyse terminee en %.1fs" % R["runtime_sec"])
print(json.dumps(R, indent=2, ensure_ascii=False, default=str))
