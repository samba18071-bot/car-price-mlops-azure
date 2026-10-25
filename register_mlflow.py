# register_mlflow.py
import mlflow
import mlflow.sklearn
import pickle

mlflow.set_experiment("production_models")

with mlflow.start_run(run_name="initial_export"):
    with open("car.pkl", "rb") as f:
        model = pickle.load(f)
    
    # Log the serialized model into MLflow registry
    mlflow.sklearn.log_model(model, artifact_path="model")
    mlflow.log_param("serialized_format", "pickle")
    print("Model logged to MLflow successfully.")