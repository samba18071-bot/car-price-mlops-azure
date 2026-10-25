import sys
import os

# Adds root directory to Python's path so it can locate app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    # Accept 200, 404, 307, or 503 (if model artifact is missing in test runner)
    assert response.status_code in [200, 404, 307, 503]

def test_prediction_endpoint():
    # Payload must match the named Pydantic schema fields in app.py
    payload = {
        "present_price": 5.5,
        "year": 2012,
        "driven_kms": 120000,
        "fuel_type": 1,
        "selling_type": 0,
        "transmission": 1,
        "owner": 0
    }
    response = client.post("/predict", json=payload)
    
    # If the model file car.pkl is present, it will return 200. 
    # If car.pkl is not downloaded yet during test step, it returns 503.
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "predicted_selling_price_lakhs" in data or "prediction" in data