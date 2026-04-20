import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def _moving_avg(series, window=7):
    return series.rolling(window, center=True, min_periods=1).mean()

def _carburant_index(df):
    """Moyenne normalisée des 6 carburants 
    indice 100 au 1er janvier
    """
    cols = ['E10', 'E85', 'GPLc', 'Gazole', 'SP95', 'SP98']
    avg = df[cols].mean(axis=1)
    return avg / avg.iloc[0] * 100



def plot_dashboard(df):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
    fig.suptitle("Dashboard transport · météo · carburants – 2025", fontsize=13, fontweight='bold')

    df.plot(x='date', y='frequentation_metro', kind='line', ax=ax1, color='steelblue', label='Métro')
    df.plot(x='date', y='frequentation_bus',   kind='line', ax=ax1, color='tomato',    label='Bus')
    ax1.set_ylabel("Fréquentation"); ax1.legend(); ax1.set_xlabel("")

    df.plot(x='date', y='temperature',   kind='line', ax=ax2, color='steelblue', label='Température (°C)')
    df.plot(x='date', y='precipitation', kind='line', ax=ax2, color='tomato',    label='Précipitations (mm)')
    ax2.set_ylabel("Météo"); ax2.legend(); ax2.set_xlabel("")

    colors = ['tomato','steelblue','seagreen','purple','orange','black']
    for col, c in zip(['E10','E85','GPLc','Gazole','SP95','SP98'], colors):
        df.plot(x='date', y=col, kind='line', ax=ax3, color=c, alpha=0.4, label=col)
    ax3.set_ylabel("Prix carburants (€)"); ax3.legend(ncol=3, fontsize=8)

    plt.tight_layout()
    plt.show()



def plot_deseasonalized(df):
    """
    Graphique de la fréquentation désaisonalisé de l'effet semaine
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
    fig.suptitle("Fréquentation : brut vs tendance (MA 7j)", fontsize=13, fontweight='bold')

    for ax, col, color, label in [
        (ax1, 'frequentation_metro', 'steelblue', 'Métro'),
        (ax2, 'frequentation_bus',   'tomato',    'Bus'),
    ]:
        raw   = df[col]
        trend = _moving_avg(raw, 7)
        ax.plot(df['date'], raw,   color=color, alpha=0.25, linewidth=0.8, label=f'{label} brut')
        ax.plot(df['date'], trend, color=color, linewidth=2,               label=f'{label} tendance 7j')
        ax.set_ylabel(label); ax.legend()

    plt.tight_layout()
    plt.show()



def plot_carburant_index(df):
    fig, ax = plt.subplots(figsize=(14, 4))
    fig.suptitle("Indice carburant moyen (base 100) + tendance 30j", fontsize=13, fontweight='bold')

    idx   = _carburant_index(df)
    trend = _moving_avg(idx, 30)

    ax.plot(df['date'], idx,   color='gray',       alpha=0.35, linewidth=0.8, label='Indice brut')
    ax.plot(df['date'], trend, color='darkorange',  linewidth=2.5,            label='Tendance 30j')
    ax.axhline(100, color='black', linewidth=0.8, linestyle='--', alpha=0.4)
    ax.set_ylabel("Indice (base 100 = 1er jan)"); ax.legend()

    plt.tight_layout()
    plt.show()


def plot_correlation_overview(df):
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("Fréquentation totale vs variables explicatives (normalisées)", fontsize=13, fontweight='bold')

    freq_total = df['frequentation_metro'] + df['frequentation_bus']
    freq_norm  = (freq_total - freq_total.mean()) / freq_total.std()

    for ax, col, label, color in [
        (axes[0], 'temperature',   'Température (°C)',    'steelblue'),
        (axes[1], 'precipitation', 'Précipitations (mm)', 'tomato'),
    ]:
        v_norm = (df[col] - df[col].mean()) / df[col].std()
        ax.fill_between(df['date'], freq_norm, alpha=0.15, color='gray')
        ax.plot(df['date'], freq_norm, color='gray',  linewidth=1,   alpha=0.5, label='Fréquentation (normalisée)')
        ax.plot(df['date'], v_norm,    color=color,   linewidth=1.5, label=f'{label} (normalisée)')
        ax.set_ylabel("Écart-type"); ax.legend(fontsize=9)

    idx      = _carburant_index(df)
    idx_norm = (idx - idx.mean()) / idx.std()
    axes[2].fill_between(df['date'], freq_norm, alpha=0.15, color='gray')
    axes[2].plot(df['date'], freq_norm, color='gray',       linewidth=1,   alpha=0.5, label='Fréquentation (normalisée)')
    axes[2].plot(df['date'], idx_norm,  color='darkorange', linewidth=1.5, label='Indice carburant (normalisé)')
    axes[2].set_ylabel("Écart-type"); axes[2].legend(fontsize=9)

    plt.tight_layout()
    plt.show()