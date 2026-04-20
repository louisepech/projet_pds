import requests
import pandas as pd

def get_meteo_data(start_date="2025-01-01", end_date="2025-12-31"):
    """
    Récupère les données météo pour Rennes (température + précipitations)
    en passant par les données heure par heure puis agrégation journalière
    """
    
    # coordonnées gps de Rennes
    lat, lon = 48.1173, -1.6778
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,precipitation",
        "timezone": "Europe/Paris"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise ValueError(f"Erreur API météo : {response.status_code}")
    
    json_data = response.json()
    
    if "hourly" not in json_data:
        print("Réponse API météo :", json_data)
        raise ValueError("Pas de données 'hourly' dans la réponse")
    
    data = json_data["hourly"]
    
    df = pd.DataFrame({
        "datetime": pd.to_datetime(data["time"]),
        "temperature": data["temperature_2m"],
        "precipitation": data["precipitation"]
    })
    
    df["date"] = df["datetime"].dt.date
    
    df_daily = df.groupby("date").agg({
        "temperature": "mean",
        "precipitation": "sum"
    }).reset_index()
    
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    
    return df_daily