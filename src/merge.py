from src.star import get_star_data
from src.meteo import get_meteo_data
from src.carburant import get_carburant_data

def build_dataset():
    """
    Construction de notre dataset final en fusionnant cex de star, météo et carburant
    """
    
    star = get_star_data()
    meteo = get_meteo_data()
    carburant = get_carburant_data()
    
    
    df = star.merge(meteo, on="date", how="inner")
    df = df.merge(carburant, on="date", how="left")
    
    
    df = df.sort_values("date")
    
    return df