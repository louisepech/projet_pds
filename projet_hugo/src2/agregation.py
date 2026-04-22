import pandas as pd
import os

def aggregate_data():
    """
    Agrège en un fichier data.csv les trois fichiers
    """
    #elec = pd.read_csv("/home/ubuntu/Bureau/python pour la data/data/elec.csv")
    #meteo = pd.read_csv("/home/ubuntu/Bureau/python pour la data/data/meteo.csv")
    #non_ouvres = pd.read_csv("/home/ubuntu/Bureau/python pour la data/data/non_ouvres.csv")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data2")
    elec = pd.read_csv(os.path.join(data_dir, "elec.csv"))
    meteo = pd.read_csv(os.path.join(data_dir, "meteo.csv"))
    non_ouvres = pd.read_csv(os.path.join(data_dir, "non_ouvres.csv"))
    data = pd.merge(elec, meteo, on="date", how="inner")
    data = pd.merge(data, non_ouvres, on="date", how="left")
    data["date"] = pd.to_datetime(data["date"])
    #data.to_csv("/home/ubuntu/Bureau/python pour la data/data/data.csv", index=False)
    data.to_csv(os.path.join(data_dir, "data.csv"), index=False)
    return data
