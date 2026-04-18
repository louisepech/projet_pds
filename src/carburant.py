import requests
import pandas as pd
import zipfile
import io
import xml.etree.ElementTree as ET

def get_carburant_data():
    """
    Récupère le prix quotidien moyen par type de carburant à Rennes pour 2025.
    Colonnes : date, gazole, sp95, sp98, e10, e85, gplc
    """

    url = "https://donnees.roulez-eco.fr/opendata/annee/2025"

    print("Téléchargement des données carburant 2025...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        xml_filename = [f for f in z.namelist() if f.endswith(".xml")][0]
        with z.open(xml_filename) as f:
            tree = ET.parse(f)

    root = tree.getroot()
    records = []

    RENNES_CP = {"35000", "35200", "35700"}

    for pdv in root.findall("pdv"):
        cp = pdv.get("cp", "").strip()
        if cp not in RENNES_CP:
            continue

        ville_node = pdv.find("ville")
        ville = ville_node.text.strip().upper() if ville_node is not None and ville_node.text else ""
        if "RENNES" not in ville:
            continue

        for prix_tag in pdv.findall("prix"):
            nom    = prix_tag.get("nom", "").strip()
            valeur = prix_tag.get("valeur")
            maj    = prix_tag.get("maj")

            if valeur and maj and nom:
                try:
                    records.append({
                        "date":      pd.to_datetime(maj, errors="coerce"),
                        "carburant": nom,
                        "prix":      float(valeur)
                    })
                except ValueError:
                    continue

    if not records:
        raise ValueError("Aucune donnée trouvée pour Rennes dans le fichier 2025")

    df = pd.DataFrame(records)

    
    if df["prix"].mean() > 100:
        df["prix"] = df["prix"] / 1000

    nom_mapping = {
        "Gazole":  "Gazole",
        "SP95":    "SP95",
        "SP98":    "SP98",
        "E10":     "E10",
        "E85":     "E85",
        "GPLc":    "GPLc",
    }
    df["carburant"] = df["carburant"].map(nom_mapping)
    df = df.dropna(subset=["carburant"])  

    df["date"] = df["date"].dt.normalize()
    df = df[df["date"].dt.year == 2025]

    df_daily = (
        df.groupby(["date", "carburant"])["prix"]
        .mean()
        .unstack(level="carburant")   
        .reset_index()
    )

    df_daily.columns.name = None
    df_daily["date"] = pd.to_datetime(df_daily["date"])
    df_daily = df_daily.sort_values("date").reset_index(drop=True)

    print(f"Série quotidienne : {len(df_daily)} jours couverts")
    print(f"Carburants disponibles : {[c for c in df_daily.columns if c != 'date']}")
    return df_daily