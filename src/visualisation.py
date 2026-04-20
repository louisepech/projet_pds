import matplotlib.pyplot as plt


def plot_dashboard(df):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 8), sharex=True)

    df.plot(x='date', y='frequentation_metro', kind='line', ax=ax1, color='blue', label='Métro')
    df.plot(x='date', y='frequentation_bus',   kind='line', ax=ax1, color='red',  label='Bus')
    ax1.set_ylabel("Fréquentation")
    ax1.legend()

    df.plot(x='date', y='temperature',   kind='line', ax=ax2, color='blue', label='Température')
    df.plot(x='date', y='precipitation', kind='line', ax=ax2, color='red',  label='Précipitations')
    ax2.set_ylabel("Météo")
    ax2.legend()

    df.plot(x='date', y='E10',    kind='line', ax=ax3, color='red',    label='E10')
    df.plot(x='date', y='E85',    kind='line', ax=ax3, color='blue',   label='E85')
    df.plot(x='date', y='GPLc',   kind='line', ax=ax3, color='green',  label='GPLc')
    df.plot(x='date', y='Gazole', kind='line', ax=ax3, color='purple', label='Gazole')
    df.plot(x='date', y='SP95',   kind='line', ax=ax3, color='orange', label='SP95')
    df.plot(x='date', y='SP98',   kind='line', ax=ax3, color='black',  label='SP98')
    ax3.set_ylabel("Prix carburants")
    ax3.legend()

    plt.tight_layout()
    plt.show()