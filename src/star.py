import pandas as pd
import os

def _convert_french_date(date_str):
    mois_map = {
        "janvier": "01", "février": "02", "mars": "03",
        "avril": "04", "mai": "05", "juin": "06",
        "juillet": "07", "août": "08", "septembre": "09",
        "octobre": "10", "novembre": "11", "décembre": "12"
    }
    
    for fr, num in mois_map.items():
        date_str = date_str.lower().replace(fr, num)
    
    return pd.to_datetime(date_str, format="%d %m %Y", errors="coerce")


def get_star_data():
    """
    Version en téléchargement CSV direct
    Nous avions initialement utilisé l’API STAR, mais face aux limitations de requêtes, 
    nous avons opté pour le téléchargement direct CSV afin d’assurer la reproductibilité.
    """
    
    file_path = "data/star.csv"
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path, parse_dates=["date"])
    
    url = "https://data.explore.star.fr/explore/dataset/tco-billettique-star-frequentation-agregee-td/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"
    
    df = pd.read_csv(url)
    
    df["Date"] = df["Date"].apply(_convert_french_date)
    df.rename(columns={"Date": "date"}, inplace=True)
    
    df_daily = df.groupby("date")["Frequentation"].sum().reset_index()
    df_daily.rename(columns={"Frequentation": "frequentation"}, inplace=True)
    
    df_daily = df_daily.sort_values("date")
    
    os.makedirs("data", exist_ok=True)
    df_daily.to_csv(file_path, index=False)
    
    
    return df_daily