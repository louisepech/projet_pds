
from src2.agregation import aggregate_data
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
import matplotlib.dates as mdates
from src2.regression import built_model

def conso_date():
    data = aggregate_data()
    plt.figure(figsize=(10,5))
    plt.plot(data["date"], data["consommation"])
    plt.title("Consommation d'électricité dans le temps")
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.ylabel("Consommation")
    plt.show()

def conso_temp():
    data = aggregate_data()
    plt.scatter(data["temperature"], data["consommation"], alpha=0.3)
    plt.xlabel("Température")
    plt.ylabel("Consommation")
    plt.title("Consommation d'électricité en fonction de la température")
    plt.show()

def conso_precip():
    data = aggregate_data()
    plt.scatter(data["precipitation"], data["consommation"], alpha=0.3)
    plt.xlabel("Précipitations")
    plt.ylabel("Consommation")
    plt.title("Consommation en fonction des précipitations")
    plt.show()

def conso_jour():
    data = aggregate_data()
    plt.figure(figsize=(6,4))
    data.boxplot(column="consommation", by="is_non_ouvre", grid=False)
    plt.title("Consommation selon le jour")
    plt.suptitle("")
    plt.xlabel("")
    plt.xticks([1,2], ["Jour ouvré", "Jour non ouvré"])
    plt.ylabel("Consommation")
    plt.show()
    ouvre = data[data["is_non_ouvre"] == 0]["consommation"]
    non_ouvre = data[data["is_non_ouvre"] == 1]["consommation"]
    stat, p_value = mannwhitneyu(ouvre, non_ouvre, alternative="two-sided")
    print("stat:", stat)
    print("p-value:", p_value)

def predictions():
    model = built_model()
    y_test = model["y_test"]
    y_pred = model["y_pred"]
    dates_test = model["dates_test"]
    plt.figure(figsize=(12,8))
    plt.plot(dates_test, y_test.values, label="observation")
    plt.plot(dates_test, y_pred, label="prédiction")
    plt.legend()
    plt.title("Prédictions de la consommation d'électricité via forêt aléatoire")
    plt.ylabel("Consommation")
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.show()

def residus():
    model = built_model()
    dates_test = model["dates_test"]
    residus = model['résidus']
    plt.figure(figsize=(12,8))
    plt.plot(dates_test, residus, color='red')
    plt.title("Résidus du modèle")
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)
    plt.axhline(y=0, linestyle="-", color='black')
    plt.show()
