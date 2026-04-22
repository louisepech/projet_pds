import pandas as pd
import os

def data_elec():
    """
    Construit le fichier elec.csv à partir d'un endpoint RTE
    """
    url = "https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/download/?format=csv"
    elec = pd.read_csv(url, sep=";")
    elec = elec[['date', 'consommation']]
    elec['date'] = pd.to_datetime(elec["date"])
    elec = elec.groupby('date')['consommation'].sum()
    elec = elec.reset_index(drop=False)
    #elec.to_csv("/home/ubuntu/Bureau/python pour la data/data/elec.csv", index=False)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data2")
    elec.to_csv(os.path.join(data_dir, "elec.csv"), index=False)
