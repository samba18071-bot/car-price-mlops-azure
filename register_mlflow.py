import mlflow
import mlflow.sklearn
import pickle
from sklearn.ensemble import RandomForestRegressor  # Example model

# Start an MLflow run
with mlflow.start_run(run_name="car_price_v1"):
    # 1. Train your model (example parameters)
    n_estimators = 100
    max_depth = 10
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
    # model.fit(X_train, y_train)

    # 2. Log parameters and evaluation metrics
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("max_depth", max_depth)
    # mlflow.log_metric("rmse", rmse_value)

    # 3. Save and log the model artifact (car.pkl)
    with open("car.pkl", "wb") as f:
        pickle.dump(model, f)
    
    mlflow.log_artifact("car.pkl")
    print("Model logged successfully to MLflow tracking store!")