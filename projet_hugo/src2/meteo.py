import requests
import pandas as pd
import time
import os

def data_meteo():
    """
    Construit le fichier meteo.csv à partir de l'API Open-Meteo
    """
    villes = {
        "paris": (48.85, 2.35),
        "lille": (50.63, 3.06),
        "strasbourg": (48.58, 7.75),
        "lyon": (45.76, 4.84),
        "bordeaux": (44.84, -0.58),
        "nantes": (47.22, -1.55),
        "toulouse": (43.60, 1.44),
        "marseille": (43.30, 5.37),
        "nice": (43.70, 7.26),
        "rennes": (48.11, -1.68),
        "montpellier": (43.61, 3.87),
        "grenoble": (45.18, 5.72),
        "dijon": (47.32, 5.04),
        "angers": (47.48, -0.55),
        "reims": (49.26, 4.03),
        "le_havre": (49.49, 0.10),
        "clermont": (45.78, 3.08),
        "saint_etienne": (45.44, 4.39),
        "tours": (47.39, 0.69),
        "amiens": (49.89, 2.30),
        "metz": (49.12, 6.17),
        "perpignan": (42.70, 2.89),
        "bayonne": (43.49, -1.47),
        "poitiers": (46.58, 0.34),
        "caen": (49.18, -0.37),
        "limoges": (45.83, 1.26),
        "besancon": (47.24, 6.02),
        "orleans": (47.90, 1.90),
        "avignon": (43.95, 4.81),
        "pau": (43.30, -0.37)
    }
    meteos = []
    url = "https://archive-api.open-meteo.com/v1/archive"
    for ville, (lat, lon) in villes.items():  # une requête pour chaque ville
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2012-01-01",
            "end_date": "2019-12-31",
            "daily": "temperature_2m_mean,precipitation_sum",
            "timezone": "Europe/Paris"
        }
        response = requests.get(url, params=params).json()
        time.sleep(10) # éviter blocage API
        meteo = pd.DataFrame({
            "date": pd.to_datetime(response["daily"]["time"]),
            f"temp_{ville}": response["daily"]["temperature_2m_mean"],
            f"precip_{ville}": response["daily"]["precipitation_sum"]
        })
        meteos.append(meteo)
    m = meteos[0]
    for meteo in meteos[1:]: # jointures
        m = pd.merge(m, meteo, on="date")
    temperatures = [colonne for colonne in m.columns if "temp" in colonne]
    precipitations = [colonne for colonne in m.columns if "precip" in colonne]
    m["temperature"] = m[temperatures].mean(axis=1)
    m["precipitation"] = m[precipitations].mean(axis=1)
    m['date'] = pd.to_datetime(m["date"])
    m = m[["date", "temperature", "precipitation"]]
    #m.to_csv("/home/ubuntu/Bureau/python pour la data/data/meteo.csv", index=False)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data2")
    m.to_csv(os.path.join(data_dir, "meteo.csv"), index=False)
