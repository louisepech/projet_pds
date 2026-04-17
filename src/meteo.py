import requests
import pandas as pd

def get_meteo_data(start_date="2025-01-01", end_date="2025-12-31"):
    """
    Récupère les données météo pour la ville de Rennes 
    En particulier les données de température et métriques de précipitations
    """
    
    # coordonnées géographiques Rennes
    lat, lon = 48.1173, -1.6778
    
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_mean,precipitation_sum",
        "timezone": "Europe/Paris"
    }
    
    response = requests.get(url, params=params)
    data = response.json()["daily"]
    
    df = pd.DataFrame({
        "date": pd.to_datetime(data["time"]),
        "temperature": data["temperature_2m_mean"],
        "precipitation": data["precipitation_sum"]
    })
    
    return df