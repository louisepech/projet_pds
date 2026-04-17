import requests
import pandas as pd
import os


def _convert_french_date(date_str):
    """
    Convertit une date du type chaine de caractères '1 janvier 2025' en datetime
    """
    
    mois_map = {
        "janvier": "01", "février": "02", "mars": "03",
        "avril": "04", "mai": "05", "juin": "06",
        "juillet": "07", "août": "08", "septembre": "09",
        "octobre": "10", "novembre": "11", "décembre": "12"
    }
    
    for fr, num in mois_map.items():
        date_str = date_str.lower().replace(fr, num)
    
    return pd.to_datetime(date_str, format="%d %m %Y", errors="coerce")


def get_star_data(start_date="2025-01-01", end_date="2025-12-31"):
    """
    Récupère via API les données de fréquentation STAR (réseau de transports à Rennes)
    et retourne les fréquentations journalières
    """
    
    file_path = "data/star.csv"
    
    # Chargement si déjà téléchargé via api
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=["date"])
        return df

    # si le fichier n'existe pas : téléchargement via l'api 
    #ou si premiere utilisation
    url = "https://data.explore.star.fr/api/explore/v2.1/catalog/datasets/tco-billettique-star-frequentation-agregee-td/records"
    
    params = {
        "limit": 10000,
        "refine": f"date>='{start_date}' AND date<='{end_date}'"
    }

    response = requests.get(url, params=params)
    data = response.json()["results"]
    
    df = pd.DataFrame(data)
    
    df["date"] = df["date"].apply(_convert_french_date)
    
    if df["date"].isna().sum() > 0:
        print("Attention : certaines dates-textes n'ont pas été converties au format date")
    
    df_daily = df.groupby("date")["frequentation"].sum().reset_index()
    
    df_daily = df_daily.sort_values("date")

    #sauvegarde
    os.makedirs("data", exist_ok=True)
    df_daily.to_csv(file_path, index=False)

    return df_daily