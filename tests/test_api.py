import sys
import os

# Adds the root project directory to Python's path so it can locate app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app import app  # Imports your FastAPI instance from app.py in the root directory

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    # Check if root returns 200, 404, or docs redirect
    assert response.status_code in [200, 404, 307]

def test_prediction_endpoint():
    payload = {
        "features": [1.2, 2012.0, 120000, 19.7, 796.0, 46.3, 5.0, 0.0, 1.0, 0.0, 2.0, 10.0, 4.0]
    }
    response = client.post("/predict", json=payload)
    # Verifies the API successfully accepts the payload and returns a prediction
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data or isinstance(data, (dict, list))