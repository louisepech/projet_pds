import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
 
 
def impute_carburant(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute les valeurs manquantes des colonnes carburant
    par propagation de la dernière valeur connue (forward fill),
    puis backward fill pour les NaN en début de série.
 
    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes carburant avec des NaN.
 
    Retourne
    --------
    pd.DataFrame
        DataFrame avec les NaN carburant imputés.
    """
    fuel_cols = [c for c in ['E10', 'E85', 'GPLc', 'Gazole', 'SP95', 'SP98']
                 if c in df.columns]
 
    df = df.copy()
 
    print("Valeurs manquantes AVANT imputation :")
    print(df[fuel_cols].isnull().sum())
    print()
 
    df[fuel_cols] = df[fuel_cols].ffill()
 

    df[fuel_cols] = df[fuel_cols].bfill()
 
    print("Valeurs manquantes APRÈS imputation :")
    print(df[fuel_cols].isnull().sum())
 
    return df


def plot_correlation_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule et affiche la matrice de corrélations (de Pearson) entre
    les colonnes numériques du DataFrame sous forme de heatmap triangulaire.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les colonnes numériques à analyser.

    Retourne
    --------
    pd.DataFrame
        La matrice de corrélations complète.
    """
    freq_cols  = [c for c in df.columns if c.startswith('frequentation')]
    fuel_cols  = [c for c in ['E10', 'E85', 'GPLc', 'Gazole', 'SP95', 'SP98']
                  if c in df.columns]
    meteo_cols = [c for c in ['temperature', 'precipitation'] if c in df.columns]

    cols = freq_cols + meteo_cols + fuel_cols
    corr = df[cols].corr()

    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',
        vmin=-1, vmax=1, center=0,
        linewidths=0.4,
        annot_kws={'size': 9},
        ax=ax
    )
    ax.set_title('Matrice de corrélations (Pearson)', fontsize=13, pad=14)
    plt.tight_layout()
    plt.show()

    return corr


def plot_top_correlations(
    corr: pd.DataFrame,
    df: pd.DataFrame,
    target: str = None,
    top_n: int = 10
) -> None:
    """
    Affiche un bar chart des variables les plus corrélées
    avec la colonne cible, triées par r (le coefficient de corrélation de Pearson) décroissant.

    Paramètres
    ----------
    corr   : pd.DataFrame  Matrice de corrélations issue de plot_correlation_heatmap.
    df     : pd.DataFrame  DataFrame original (pour détecter freq_cols si target=None).
    target : str           Colonne cible. Si None, prend la première colonne frequentation.
    top_n  : int           Nombre de variables à afficher (défaut 10).
    """
    if target is None:
        freq_cols = [c for c in df.columns if c.startswith('frequentation')]
        target = freq_cols[0]

    top = (
        corr[target]
        .drop(index=target)
        .dropna()
        .abs()
        .sort_values(ascending=True)
        .tail(top_n)
    )

    colors = ['#2ecc71' if corr[target][i] >= 0 else '#e74c3c' for i in top.index]

    fig, ax = plt.subplots(figsize=(8, 5))
    top.plot(kind='barh', ax=ax, color=colors, edgecolor='none')
    ax.set_title(f'Top {top_n} corrélations r avec {target}', fontsize=12)
    ax.set_xlabel('r de Pearson')
    ax.axvline(0.3, color='gray', linestyle='--', linewidth=0.8, label='seuil 0.3')
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"\nValeurs complètes (avec signe) pour {target} :\n")
    print(
        corr[target]
        .drop(index=target)
        .dropna()
        .sort_values(key=abs, ascending=False)
        .head(top_n)
        .round(3)
        .to_string()
    )