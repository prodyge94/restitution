# -*- coding: utf-8 -*-
"""
ESGI 2025-2026 - Reporting & Restitution des donnees (A. Biam)
Projet : Analyse des retards des vols aeriens domestiques US (USDOT, 2015)

ETAPE 1 du processus de restitution vu en cours :
   Collection -> Integration -> Selection -> PRETRAITEMENT (nettoyage)

Objectif du script :
  - charger flights.csv (5,8 M lignes) de maniere econome en memoire ;
  - diagnostiquer la qualite des donnees (manquantes, doublons, aberrantes) ;
  - reperer le defaut connu des "aeroports numeriques" d'octobre 2015 ;
  - transformer / creer les variables utiles (DATE, heure de depart, retard>15) ;
  - exporter un parquet propre + un rapport JSON reutilise dans la soutenance.
"""
import sys, os, json, time
sys.stdout.reconfigure(encoding="utf-8")  # evite les soucis d'encodage console (Windows cp1252)
import numpy as np
import pandas as pd

T0 = time.time()
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW  = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")
OUT  = os.path.join(BASE, "analyse", "sorties")
os.makedirs(PROC, exist_ok=True)
os.makedirs(OUT,  exist_ok=True)
report = {}

# ─────────────────────────────────────────────────────────────────────────────
# 1. COLLECTION  -  lecture econome (dtypes compacts) pour tenir en memoire
# ─────────────────────────────────────────────────────────────────────────────
dtypes = {
    "YEAR": "int16", "MONTH": "int8", "DAY": "int8", "DAY_OF_WEEK": "int8",
    "AIRLINE": "category", "FLIGHT_NUMBER": "int32",
    "ORIGIN_AIRPORT": "category", "DESTINATION_AIRPORT": "category",
    "SCHEDULED_DEPARTURE": "int16", "DEPARTURE_DELAY": "float32",
    "TAXI_OUT": "float32", "TAXI_IN": "float32",
    "SCHEDULED_TIME": "float32", "ELAPSED_TIME": "float32", "AIR_TIME": "float32",
    "DISTANCE": "int16", "ARRIVAL_DELAY": "float32",
    "DIVERTED": "int8", "CANCELLED": "int8", "CANCELLATION_REASON": "category",
    "AIR_SYSTEM_DELAY": "float32", "SECURITY_DELAY": "float32", "AIRLINE_DELAY": "float32",
    "LATE_AIRCRAFT_DELAY": "float32", "WEATHER_DELAY": "float32",
}
print("[1] Chargement de flights.csv ...")
df = pd.read_csv(os.path.join(RAW, "flights.csv"), usecols=list(dtypes), dtype=dtypes)
report["n_rows"], report["n_cols_charges"] = int(df.shape[0]), int(df.shape[1])
report["memoire_Mo"] = round(df.memory_usage(deep=True).sum() / 1e6, 1)
print(f"    {df.shape[0]:,} lignes  |  {report['memoire_Mo']} Mo en RAM")

# ─────────────────────────────────────────────────────────────────────────────
# 2. QUALITE  -  valeurs manquantes (cours : donnees manquantes / sparse)
# ─────────────────────────────────────────────────────────────────────────────
miss = df.isna().sum()
report["manquantes"] = {
    c: {"n": int(miss[c]), "pct": round(float(miss[c]) / len(df) * 100, 2)}
    for c in df.columns if miss[c] > 0
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. DOUBLONS  -  cours : pandas.DataFrame.duplicated
# ─────────────────────────────────────────────────────────────────────────────
report["doublons_ligne_complete"] = int(df.duplicated().sum())

# ─────────────────────────────────────────────────────────────────────────────
# 4. DEFAUT CONNU  -  aeroports codes en numerique (octobre 2015)
#    -> casse la jointure avec airports.csv (codes IATA). On le DOCUMENTE.
# ─────────────────────────────────────────────────────────────────────────────
orig = df["ORIGIN_AIRPORT"].astype("string")
is_num = orig.str.fullmatch(r"\d+").fillna(False).to_numpy()
df["ORIGIN_IS_NUMERIC"] = is_num
tmp = pd.DataFrame({"MONTH": df["MONTH"].to_numpy(), "num": is_num})
report["aeroports_numeriques_par_mois"] = {
    int(k): int(v) for k, v in tmp.groupby("MONTH")["num"].sum().items()
}
report["aeroports_numeriques_total"] = int(is_num.sum())

# ─────────────────────────────────────────────────────────────────────────────
# 5. ANNULATIONS / DETOURNEMENTS  -  NaN structurels (pas de vraies manquantes)
# ─────────────────────────────────────────────────────────────────────────────
report["annules_n"]   = int(df["CANCELLED"].sum())
report["annules_pct"] = round(float(df["CANCELLED"].mean()) * 100, 2)
report["detournes_n"] = int(df["DIVERTED"].sum())
report["detournes_pct"] = round(float(df["DIVERTED"].mean()) * 100, 3)
report["motif_annulation"] = {
    str(k): int(v) for k, v in df["CANCELLATION_REASON"].value_counts().items()
}  # A=compagnie, B=meteo, C=systeme national, D=securite

# ─────────────────────────────────────────────────────────────────────────────
# 6. DONNEES ABERRANTES  -  cours : decouper / filtrer / stats robustes
# ─────────────────────────────────────────────────────────────────────────────
for col in ["DEPARTURE_DELAY", "ARRIVAL_DELAY"]:
    s = df[col].dropna()
    desc = s.describe(percentiles=[.01, .05, .25, .5, .75, .95, .99])
    report[col + "_describe"] = {k: round(float(v), 2) for k, v in desc.items()}
    report[col + "_pct_sup_60min"] = round(float((s > 60).mean()) * 100, 2)
    report[col + "_pct_sup_180min"] = round(float((s > 180).mean()) * 100, 2)

# ─────────────────────────────────────────────────────────────────────────────
# 7. TRANSFORMATION / FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────
df["DATE"] = pd.to_datetime(dict(year=df.YEAR, month=df.MONTH, day=df.DAY), errors="coerce")
# SCHEDULED_DEPARTURE est au format HHMM (ex : 2354 -> 23h) ; 2400 -> 0h
df["DEP_HOUR"] = ((df["SCHEDULED_DEPARTURE"] // 100) % 24).astype("int8")
# Standard industriel : un vol est "en retard" s'il arrive 15 min ou plus apres l'heure
df["IS_DELAYED_ARR"] = (df["ARRIVAL_DELAY"] > 15)
df["IS_DELAYED_DEP"] = (df["DEPARTURE_DELAY"] > 15)
# Vol "valide" = ni annule ni detourne (base de calcul des taux de ponctualite)
df["IS_VALID"] = (df["CANCELLED"] == 0) & (df["DIVERTED"] == 0)

report["taux_retard_arr_global_pct"] = round(
    float(df.loc[df.IS_VALID, "IS_DELAYED_ARR"].mean()) * 100, 2)

# ─────────────────────────────────────────────────────────────────────────────
# 8. EXPORT  -  parquet propre (relecture en quelques secondes pour l'etape 2)
# ─────────────────────────────────────────────────────────────────────────────
out_parquet = os.path.join(PROC, "flights_clean.parquet")
df.to_parquet(out_parquet, index=False)
report["parquet"] = out_parquet
report["parquet_Mo"] = round(os.path.getsize(out_parquet) / 1e6, 1)
report["runtime_sec"] = round(time.time() - T0, 1)

with open(os.path.join(OUT, "01_nettoyage.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False, default=str)

print("[OK] Parquet + rapport ecrits en %.1fs" % report["runtime_sec"])
print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
