from src2.agregation import aggregate_data
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import pandas as pd

def built_model():
    """
    Construction de la forêt aléatoire
    """
    data = aggregate_data()
    data["date"] = pd.to_datetime(data["date"])
    X = data[["temperature", "precipitation", "is_non_ouvre"]]
    y = data["consommation"]
    X_train = X.iloc[:int(0.8*len(X))]
    X_test  = X.iloc[int(0.8*len(X)):]
    dates_test = data["date"].iloc[int(0.8*len(data)):]
    y_train = y.iloc[:int(0.8*len(y))]
    y_test = y.iloc[int(0.8*len(y)):]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    residus = y_test-y_pred
    importance = pd.Series(model.feature_importances_, index=X.columns)
    return {"model": model,
            "X_train": X_train,
            "y_test": y_test,
            "y_pred": y_pred,
            "importance": importance,
            "R2": r2_score(y_test, y_pred),
            "résidus": residus,
            "dates_test": dates_test}
