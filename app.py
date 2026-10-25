from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pickle
import numpy as np
from contextlib import asynccontextmanager

# Global dictionary to hold our model in memory across requests
ml_context = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model ONCE on startup to maximize performance
    try:
        with open("car.pkl", "rb") as f:
            ml_context["model"] = pickle.load(f)
        print("Model 'car.pkl' loaded successfully into memory.")
    except Exception as e:
        print(f"Failed to load model on startup: {e}")
        ml_context["model"] = None
    
    yield
    
    # Cleanup memory on shutdown
    ml_context.clear()

app = FastAPI(
    title="Car Price Prediction API", 
    version="1.0.0",
    lifespan=lifespan
)

# Define clear, named schema for incoming feature payload
class CarFeatures(BaseModel):
    present_price: float = Field(..., description="Present showroom price of the car (in lakhs)")
    year: int = Field(..., description="Manufacturing year of the car")
    driven_kms: int = Field(..., description="Total kilometers driven")
    fuel_type: int = Field(..., description="Fuel type encoded (e.g., Petrol/Diesel/CNG)")
    selling_type: int = Field(..., description="Selling type encoded (Dealer/Individual)")
    transmission: int = Field(..., description="Transmission type (Manual/Automatic)")
    owner: int = Field(..., description="Number of previous owners")

@app.get("/")
def health_check():
    """Liveness probe to ensure the service and model are active."""
    if ml_context.get("model") is None:
        raise HTTPException(status_code=503, detail="Model artifact not initialized.")
    return {"status": "healthy", "service": "Car Price Prediction API"}

@app.post("/predict")
def predict(data: CarFeatures):
    model = ml_context.get("model")
    if model is None:
        raise HTTPException(status_code=503, detail="Model unavailable in memory.")
        
    try:
        # Extract features into the 2D array expected by the model pipeline
        features_array = np.array([[
            data.present_price,
            data.year,
            data.driven_kms,
            data.fuel_type,
            data.selling_type,
            data.transmission,
            data.owner
        ]])
            
        prediction = model.predict(features_array)
        
        # Safely convert numpy scalar to python float
        predicted_price = float(prediction[0].item() if hasattr(prediction[0], "item") else prediction[0])
        
        return {
            "predicted_selling_price_lakhs": predicted_price,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference computation error: {str(e)}")