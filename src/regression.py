import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import holidays
 
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    root_mean_squared_error,
    r2_score
)
 
# ─────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────
 
FEATURE_COLS = [
    'day_of_week', 'month', 'week_number', 'is_weekend', 'is_holiday',
    'temperature', 'precipitation',
    'E10', 'E85', 'GPLc', 'Gazole', 'SP95', 'SP98'
]
 
TARGET_METRO = 'frequentation_metro'
TARGET_BUS   = 'frequentation_bus'
 
PARAM_GRID = {
    'max_depth'         : [3, 5, 10, 15, None],
    'min_samples_split' : [2, 5, 10, 20],
    'min_samples_leaf'  : [1, 2, 5, 10]
}
 
 
# ─────────────────────────────────────────────
# 1. Feature engineering
# ─────────────────────────────────────────────
 
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construit les features pour le modèle de régression par arbre de décision.
 
    Features ajoutées :
    - day_of_week  : jour de la semaine (0=lundi, 6=dimanche)
    - month        : mois de l'année (1-12)
    - week_number  : numéro de semaine ISO (1-53)
    - is_weekend   : 1 si samedi ou dimanche, 0 sinon
    - is_holiday   : 1 si jour férié en France, 0 sinon
 
    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame avec une colonne 'date' de type datetime.
 
    Retourne
    --------
    pd.DataFrame
        DataFrame enrichi des features temporelles.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
 
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month']       = df['date'].dt.month
    df['week_number'] = df['date'].dt.isocalendar().week.astype(int)
    df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
 
    years = df['date'].dt.year.unique().tolist()
    fr_holidays = holidays.France(years=years)
    df['is_holiday'] = df['date'].dt.date.apply(
        lambda d: 1 if d in fr_holidays else 0
    )
 
    print("Features temporelles ajoutées :")
    print(df[['date', 'day_of_week', 'month', 'week_number',
              'is_weekend', 'is_holiday']].head(7).to_string(index=False))
 
    return df
 
 
# ─────────────────────────────────────────────
# 2. Split stratifié par mois
# ─────────────────────────────────────────────
 
def stratified_split(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Découpe le DataFrame en train/test en stratifiant par mois,
    garantissant que chaque mois est représenté dans les deux jeux.
 
    Paramètres
    ----------
    df           : DataFrame avec les features déjà construites.
    test_size    : Proportion des données pour le test (défaut 0.2).
    random_state : Graine aléatoire pour la reproductibilité (défaut 42).
 
    Retourne
    --------
    X_train, X_test, y_train_metro, y_test_metro,
    y_train_bus, y_test_bus, df_test
    """
    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Features manquantes dans le DataFrame : {missing}")
 
    X       = df[FEATURE_COLS]
    y_metro = df[TARGET_METRO]
    y_bus   = df[TARGET_BUS]
 
    # Premier split stratifié sur metro (même indices pour bus grâce au même random_state)
    X_train, X_test, y_train_metro, y_test_metro = train_test_split(
        X, y_metro,
        test_size=test_size,
        random_state=random_state,
        stratify=df['month']
    )
 
    # On réutilise exactement les mêmes indices pour bus
    y_train_bus = y_bus.loc[X_train.index]
    y_test_bus  = y_bus.loc[X_test.index]
 
    # df_test pour les graphiques (trié par date pour la lisibilité)
    df_test = df.loc[X_test.index].sort_values('date').copy()
    X_test  = X_test.loc[df_test.index]
    y_test_metro = y_test_metro.loc[df_test.index]
    y_test_bus   = y_test_bus.loc[df_test.index]
 
    n_train, n_test = len(X_train), len(X_test)
    print(f"Split stratifié par mois : {n_train} jours train / {n_test} jours test")
    print(f"  Mois représentés dans le test : "
          f"{sorted(df_test['month'].unique().tolist())}")
 
    return X_train, X_test, y_train_metro, y_test_metro, y_train_bus, y_test_bus, df_test
 
 
# ─────────────────────────────────────────────
# 3. Grid search avec TimeSeriesSplit
# ─────────────────────────────────────────────
 
def run_grid_search(X_train: pd.DataFrame, y_train: pd.Series,
                    target_name: str) -> GridSearchCV:
    """
    Lance un GridSearchCV sur un DecisionTreeRegressor
    avec validation croisée temporelle (TimeSeriesSplit).
 
    Paramètres
    ----------
    X_train     : Features d'entraînement.
    y_train     : Cible d'entraînement.
    target_name : Nom de la cible (pour l'affichage).
 
    Retourne
    --------
    GridSearchCV fitté.
    """
    tscv = TimeSeriesSplit(n_splits=5)
 
    gs = GridSearchCV(
        estimator=DecisionTreeRegressor(random_state=42),
        param_grid=PARAM_GRID,
        cv=tscv,
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        verbose=1
    )
 
    print(f"\nGrid search pour : {target_name}")
    gs.fit(X_train, y_train)
 
    print(f"  Meilleurs paramètres : {gs.best_params_}")
    print(f"  MAE CV (train)       : {-gs.best_score_:,.0f} voyageurs")
 
    return gs
 
 
# ─────────────────────────────────────────────
# 4. Évaluation
# ─────────────────────────────────────────────
 
def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series,
                   target_name: str, df_test: pd.DataFrame) -> dict:
    """
    Calcule MAE, RMSE et R² sur le jeu de test,
    puis trace le graphique prédictions vs réelles et l'importance des features.
 
    Paramètres
    ----------
    model       : Modèle fitté (GridSearchCV ou estimator).
    X_test      : Features de test.
    y_test      : Vraies valeurs de la cible.
    target_name : Nom de la cible (pour les titres).
    df_test     : DataFrame de test avec la colonne 'date'.
 
    Retourne
    --------
    dict avec les métriques {MAE, RMSE, R2}.
    """
    y_pred = model.predict(X_test)
 
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)
 
    print(f"\n── Évaluation {target_name} ──────────────────")
    print(f"  MAE  : {mae:>12,.0f} voyageurs")
    print(f"  RMSE : {rmse:>12,.0f} voyageurs")
    print(f"  R²   : {r2:>12.4f}")
 
    # Prédictions vs réelles
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df_test['date'].values, y_test.values,
            label='Réel', color='steelblue', linewidth=1.2)
    ax.plot(df_test['date'].values, y_pred,
            label='Prédit', color='tomato', linewidth=1.2, linestyle='--')
    ax.set_title(f'{target_name} — Réel vs Prédit (jeu de test)')
    ax.set_xlabel('')
    ax.legend()
    plt.tight_layout()
    plt.show()
 
    # Importance des features
    best_estimator = model.best_estimator_ if hasattr(model, 'best_estimator_') else model
    importances = pd.Series(
        best_estimator.feature_importances_, index=FEATURE_COLS
    ).sort_values(ascending=True)
 
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    importances.plot(kind='barh', ax=ax2, color='steelblue', edgecolor='none')
    ax2.set_title(f'Importance des features — {target_name}')
    ax2.set_xlabel('Importance (Gini)')
    plt.tight_layout()
    plt.show()
 
    return {'MAE': mae, 'RMSE': rmse, 'R2': r2}
 
 
# ─────────────────────────────────────────────
# 5. Comparaison des métriques
# ─────────────────────────────────────────────
 
def compare_metrics(metrics_metro: dict, metrics_bus: dict) -> None:
    """Affiche un tableau récapitulatif des métriques pour les deux modèles."""
    summary = pd.DataFrame(
        [metrics_metro, metrics_bus],
        index=['Metro', 'Bus']
    ).round({'MAE': 0, 'RMSE': 0, 'R2': 4})
 
    print("\n── Récapitulatif des métriques ───────────────")
    print(summary.to_string())
 
 
# ─────────────────────────────────────────────
# 6. Prédiction
# ─────────────────────────────────────────────
 
def predict_frequentation(
    date,
    temperature: float,
    precipitation: float,
    E10: float,
    E85: float,
    GPLc: float,
    Gazole: float,
    SP95: float,
    SP98: float,
    ligne: str = 'metro',
    model_metro=None,
    model_bus=None
) -> float:
    """
    Prédit la fréquentation d'une ligne de transport pour un jour donné.
 
    Paramètres
    ----------
    date          : str ou datetime (ex: '2025-03-15')
    temperature   : Température moyenne du jour (°C)
    precipitation : Précipitations du jour (mm)
    E10           : Prix E10 (€/L)
    E85           : Prix E85 (€/L)
    GPLc          : Prix GPLc (€/L)
    Gazole        : Prix Gazole (€/L)
    SP95          : Prix SP95 (€/L)
    SP98          : Prix SP98 (€/L)
    ligne         : 'metro' ou 'bus'
    model_metro   : Modèle entraîné pour le métro (GridSearchCV)
    model_bus     : Modèle entraîné pour le bus (GridSearchCV)
 
    Retourne
    --------
    float : Fréquentation prédite (nombre de voyageurs)
    """
    if ligne not in ('metro', 'bus'):
        raise ValueError("Le paramètre 'ligne' doit être 'metro' ou 'bus'.")
    if ligne == 'metro' and model_metro is None:
        raise ValueError("model_metro est requis pour ligne='metro'.")
    if ligne == 'bus' and model_bus is None:
        raise ValueError("model_bus est requis pour ligne='bus'.")
 
    d = pd.to_datetime(date)
    fr_holidays = holidays.France(years=[d.year])
    is_holiday  = 1 if d.date() in fr_holidays else 0
 
    row = pd.DataFrame([{
        'day_of_week'  : d.dayofweek,
        'month'        : d.month,
        'week_number'  : d.isocalendar()[1],
        'is_weekend'   : int(d.dayofweek >= 5),
        'is_holiday'   : is_holiday,
        'temperature'  : temperature,
        'precipitation': precipitation,
        'E10'          : E10,
        'E85'          : E85,
        'GPLc'         : GPLc,
        'Gazole'       : Gazole,
        'SP95'         : SP95,
        'SP98'         : SP98,
    }])[FEATURE_COLS]
 
    model  = model_metro if ligne == 'metro' else model_bus
    result = model.predict(row)[0]
 
    print(f"\nPrédiction fréquentation {ligne} le {d.date()} :")
    print(f"  Jour férié : {'oui' if is_holiday else 'non'} | "
          f"Week-end : {'oui' if d.dayofweek >= 5 else 'non'}")
    print(f"  → {result:,.0f} voyageurs estimés")
 
    return result