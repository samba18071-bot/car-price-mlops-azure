# Car Price Prediction MLOps

An end-to-end machine learning service that predicts used-car selling prices through a validated **FastAPI** endpoint and deploys as a Docker container to **Azure Container Apps**.

[![CI/CD Pipeline](https://github.com/samba18071-bot/car-price-mlops-azure/actions/workflows/deploy.yml/badge.svg)](https://github.com/samba18071-bot/car-price-mlops-azure/actions/workflows/deploy.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Azure Container Apps](https://img.shields.io/badge/Azure-Container%20Apps-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/products/container-apps)

> **Project status:** The API and deployment workflow are implemented. The model artifact is distributed separately because `car.pkl` is larger than 100 MB.

## Contents

- [What this project does](#what-this-project-does)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [API reference](#api-reference)
- [Run locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Testing](#testing)
- [Deployment](#deployment)
- [Model artifact management](#model-artifact-management)
- [Streamlit dashboard](#streamlit-dashboard)
- [Limitations and next steps](#limitations-and-next-steps)
- [Author](#author)

## What this project does

The service:

1. Loads the serialized `car.pkl` model once when the FastAPI application starts.
2. Validates incoming car features with a typed Pydantic schema.
3. Runs inference with scikit-learn and returns a JSON prediction in lakhs.
4. Exposes a health endpoint for availability checks.
5. Tests the application in GitHub Actions before building a Docker image.
6. Pushes the image to Azure Container Registry and updates Azure Container Apps.

## Architecture

```text
                         Push to main
                              │
                              ▼
                    GitHub Actions workflow
                 ┌────────────┴────────────┐
                 ▼                         ▼
          Install dependencies       Download car.pkl
                 │                         │
                 └────────────┬────────────┘
                              ▼
                         Run pytest
                              │
                              ▼
                  Build linux/amd64 image
                              │
                              ▼
                       Push image to ACR
                              │
                              ▼
                   Update Azure Container App

 Client ──POST /predict──> FastAPI ──> car.pkl ──> Prediction
 Client ─────GET /───────> Health check
```

## Repository layout

```text
.
├── .github/workflows/deploy.yml  # CI/CD: test, build, push, deploy
├── tests/test_api.py             # API smoke tests
├── app.py                        # FastAPI service and inference logic
├── app_ui.py                     # Streamlit dashboard prototype
├── Dockerfile                    # Production API container
├── car.pkl.dvc                   # DVC pointer for the model artifact
├── register_mlflow.py             # MLflow experiment/artifact example
├── requirements.txt              # Runtime and MLOps dependencies
└── .gitignore
```

## API reference

### Base URL

The deployed service is currently available at:

`https://ml-prediction-app.politestone-56ec275d.centralindia.azurecontainerapps.io`

Interactive documentation is available at [`/docs`](https://ml-prediction-app.politestone-56ec275d.centralindia.azurecontainerapps.io/docs).

### `GET /`

Returns a liveness response when the model is loaded.

```json
{
  "status": "healthy",
  "service": "Car Price Prediction API"
}
```

If the model cannot be loaded, the endpoint returns `503 Service Unavailable`.

### `POST /predict`

Request body:

```json
{
  "present_price": 5.5,
  "year": 2012,
  "driven_kms": 120000,
  "fuel_type": 1,
  "selling_type": 0,
  "transmission": 1,
  "owner": 0
}
```

| Field | Type | Description |
| --- | --- | --- |
| `present_price` | `float` | Current showroom price, in lakhs |
| `year` | `int` | Manufacturing year |
| `driven_kms` | `int` | Total kilometers driven |
| `fuel_type` | `int` | Encoded fuel type |
| `selling_type` | `int` | Encoded seller type |
| `transmission` | `int` | Encoded transmission type |
| `owner` | `int` | Number of previous owners |

Example with `curl`:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "present_price": 5.5,
    "year": 2012,
    "driven_kms": 120000,
    "fuel_type": 1,
    "selling_type": 0,
    "transmission": 1,
    "owner": 0
  }'
```

Successful response:

```json
{
  "predicted_selling_price_lakhs": 3.45,
  "status": "success"
}
```

The exact prediction depends on the model artifact currently deployed.

## Run locally

### Prerequisites

- Python 3.11 or newer
- `pip`
- The `car.pkl` model artifact in the project root

Create an isolated environment and install dependencies:

```bash
git clone https://github.com/samba18071-bot/car-price-mlops-azure.git
cd car-price-mlops-azure

python3.11 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The CI workflow obtains the model from the GitHub Release `v.1.0.0`:

```bash
curl -L \
  "https://github.com/samba18071-bot/my_ml/releases/download/v.1.0.0/car.pkl" \
  -o car.pkl
```

Start the API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- Health check: <http://localhost:8000/>
- Swagger UI: <http://localhost:8000/docs>
- OpenAPI schema: <http://localhost:8000/openapi.json>

## Run with Docker

The Docker image expects `car.pkl` to be present before the image is built:

```bash
curl -L \
  "https://github.com/samba18071-bot/my_ml/releases/download/v.1.0.0/car.pkl" \
  -o car.pkl

docker build --platform linux/amd64 -t car-price-api .
docker run --rm -p 8000:8000 car-price-api
```

The API is then available at <http://localhost:8000/docs>.

## Testing

Install the test dependencies and run the suite:

```bash
python -m pip install pytest httpx
pytest
```

The tests support both environments where `car.pkl` is available and environments where the artifact has not yet been downloaded; the latter correctly reports the API as unavailable.

## Deployment

The workflow in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) runs on pushes to `main` or via manual dispatch. It:

1. Sets up Python 3.11.
2. Installs application and test dependencies.
3. Downloads `car.pkl` from the GitHub Release.
4. Runs `pytest`.
5. Logs in to Azure with the `AZURE_CREDENTIALS` repository secret.
6. Builds a `linux/amd64` image.
7. Pushes immutable SHA and `latest` tags to Azure Container Registry.
8. Updates the `ml-prediction-app` Azure Container App with the SHA-tagged image.

### Required GitHub configuration

The workflow requires:

- A repository secret named `AZURE_CREDENTIALS` containing an Azure service-principal credential JSON object.
- An Azure Container Registry named `mymlregistry2026`.
- A resource group named `my-ml-rg`.
- An Azure Container App named `ml-prediction-app`.
- Permission for the service principal to push to the registry and update the container app.

For production use, keep Azure resource names and deployment configuration in repository variables or environment-specific workflow configuration rather than hard-coding them in the workflow.

## Model artifact management

`car.pkl` is intentionally ignored by Git because of its size. The repository contains [`car.pkl.dvc`](car.pkl.dvc) as metadata, but the current CI/CD workflow downloads the artifact directly from the GitHub Release before testing and building.

When replacing the model:

1. Publish the new artifact through the project’s release process.
2. Update the release URL in the workflow and this README.
3. Run the test suite with the new artifact.
4. Deploy only after validating the model’s feature order and output units.

Never load an untrusted pickle file. Pickle deserialization can execute arbitrary code.

## Streamlit dashboard

[`app_ui.py`](app_ui.py) contains a Streamlit dashboard prototype. Run it with:

```bash
streamlit run app_ui.py
```

The dashboard currently constructs a 13-feature payload, while the production FastAPI schema accepts seven named fields. It therefore requires alignment with the deployed model/API contract before it should be used as the production client. The API and Swagger UI are the source of truth for the current interface.

## Limitations and next steps

- Add explicit numeric range validation for feature values.
- Align the Streamlit dashboard with the seven-field API contract.
- Add model version metadata and a reproducible training pipeline.
- Add integration tests for the deployed container and CI smoke tests for `/`.
- Store Azure resource names as configurable deployment variables.
- Add monitoring for latency, error rate, and model drift.
- Add a project license and contribution guidelines if this repository is opened for external contributions.

## Author

**Boddu Tulasi Sambasiva Naidu**

Undergraduate Engineering Student | MLOps & Systems Engineer
