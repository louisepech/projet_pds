import requests
import pandas as pd

def get_carburant_data():
    """
    Récupère le prix quotidien moyen des différents carburants pour la ville de Rennes
    """
    
    url = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records"
    
    params = {
        "limit": 10000,
        "refine": "ville:RENNES"
    }
    
    response = requests.get(url, params=params)
    data = response.json()["results"]
    
    df = pd.DataFrame(data)
    
    
    df["date"] = pd.to_datetime(df["date"])
    
    
    df = df[["date", "prix"]]
    
    
    df_daily = df.groupby(df["date"].dt.date)["prix"].mean().reset_index()
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    
    df_daily.rename(columns={"prix": "fuel_price"}, inplace=True)
    
    return df_daily