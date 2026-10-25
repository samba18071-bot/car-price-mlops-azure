# 🚀 Production-Grade End-to-End MLOps Pipeline for Car Price Prediction

An enterprise-ready, serverless machine learning system that automatically trains, containerizes, tests, and deploys a predictive model to **Azure Container Apps** using **GitHub Actions CI/CD**.

---

## 🏛️ System Architecture
[ Developer Git Push ] ---> [ GitHub Actions CI/CD ]
│
┌───────────────────────┴───────────────────────┐
▼                                               ▼

Run Pytest Suite                    2. Download Model (GitHub Release)
│                                               │
└───────────────────────┬───────────────────────┘
▼
3. Build Docker Image Locally
│
▼
4. Push Image to Azure Container Registry (ACR)
│
▼
5. Update Live Azure Container Apps


---

## ⚙️ CI/CD Workflow & Quality Gates
Every push to the `main` branch triggers an automated pipeline defined in `.github/workflows/deploy.yml`:
1. **Automated Testing:** Runs `pytest` unit tests against the FastAPI application logic to guard against breaking changes.
2. **Artifact Management:** Fetches the serialized model (`car.pkl` > 100MB) securely from GitHub Releases during runner compilation.
3. **Containerization & Registry Push:** Compiles a production `linux/amd64` Docker image and pushes it to Azure Container Registry (`mymlregistry2026`).
4. **Serverless Deployment:** Updates the live **Azure Container App** with zero-downtime rolling updates.

---

## 🔌 API Documentation & Usage

The service exposes a RESTful API built with **FastAPI**. 

### Endpoint
`POST /predict`

### Example Request Payload
```json
{
  "features": [1.2, 2012.0, 120000, 19.7, 796.0, 46.3, 5.0, 0.0, 1.0, 0.0, 2.0, 10.0, 4.0]
}