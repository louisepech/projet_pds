import requests
import pandas as pd
import os

def data_non_ouvres(): # jours fériés + weekends
    """
    Construit le fichier non_ouvres.csv à partir d'un endpoint de data.gouv
    """
    years = range(2012, 2020)
    annees = []
    for year in years:
        url = f"https://calendrier.api.gouv.fr/jours-feries/metropole/{year}.json"
        data = requests.get(url).json()
        annee = pd.DataFrame({
            "date": pd.to_datetime(list(data.keys())),
            "is_holiday": 1
        })
        annees.append(annee)
    feries = pd.concat(annees)
    feries["is_holiday"] = feries["is_holiday"].fillna(0)
    dates = pd.DataFrame({
        "date": pd.date_range(start="2012-01-01", end="2019-12-31")
    })
    dates.loc[dates["date"].dt.dayofweek >= 5, "is_weekend"] = 1
    non_ouvres = pd.merge(dates, feries, on="date", how="left")
    non_ouvres["is_holiday"] = non_ouvres["is_holiday"].fillna(0)
    non_ouvres["is_weekend"] = non_ouvres["is_weekend"].fillna(0)
    non_ouvres["is_non_ouvre"] = ((non_ouvres["is_weekend"] == 1) | (non_ouvres["is_holiday"] == 1)).astype(int)
    non_ouvres = non_ouvres[['date', 'is_non_ouvre']]
    #non_ouvres.to_csv("/home/ubuntu/Bureau/python pour la data/data/non_ouvres.csv", index=False)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data2")
    non_ouvres.to_csv(os.path.join(data_dir, "non_ouvres.csv"), index=False)
