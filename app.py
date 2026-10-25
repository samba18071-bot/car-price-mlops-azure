# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import numpy as np

# 1. Initialize FastAPI instance
app = FastAPI(title="ML Prediction Service", version="1.0.0")

# 2. Load model binary
try:
    with open("car.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    model = None

# 3. Define schema for input validation
class InferenceRequest(BaseModel):
    features: list[float]

# 4. Root / Health-check endpoint
@app.get("/")
def health_check():
    if model is None:
        raise HTTPException(status_code=500, detail="Model file not found")
    return {"status": "healthy", "service": "ML Inference API"}

# 5. Prediction endpoint
@app.post("/predict")
def predict(payload: InferenceRequest):
    # your prediction code here
    if model is None:
        raise HTTPException(status_code=500, detail="Model artifact unavailable")
    
    try:
        # Reshape flat list into a 2D array: shape (1, num_features)
        input_data = np.array([payload.features])
        raw_prediction = model.predict(input_data)
        
        # Extract scalar value
        result = int(raw_prediction[0]) if hasattr(raw_prediction[0], "item") else raw_prediction[0]
        
        return {
            "prediction": result,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference error: {str(e)}")