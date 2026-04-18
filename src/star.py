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
    Lecture du fichier, en local téléchargé
    """
    
    raw_path = "data/star_raw.csv"
    clean_path = "data/star.csv"

    if os.path.exists(clean_path):
        return pd.read_csv(clean_path, parse_dates=["date"])

    df = pd.read_csv(raw_path, sep=";")

    df["date"] = pd.to_datetime(df["date"])

    df_daily = df.groupby("date")["Frequentation"].sum().reset_index()
    df_daily.rename(columns={"Frequentation": "frequentation"}, inplace=True)

    df_daily = df_daily.sort_values("date")

    os.makedirs("data", exist_ok=True)
    df_daily.to_csv(clean_path, index=False)

    return df_daily

