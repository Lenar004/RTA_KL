from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI(title="Fraud Detection API — Isolation Forest")

with open("fraud_model_if.pkl", "rb") as f:
    model = pickle.load(f)

class Transaction(BaseModel):
    amount: float
    is_electronics: int
    tx_per_minute: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/model-info")
def model_info():
    return {
        "type": "isolation_forest",
        "n_estimators": model.n_estimators,
        "contamination": model.contamination
    }

@app.post("/score")
def score(tx: Transaction):
    X = np.array([[tx.amount, tx.is_electronics, tx.tx_per_minute]])
    prediction = model.predict(X)[0]
    anomaly_score = model.decision_function(X)[0]
    fraud_probability = float(np.clip(0.5 - anomaly_score, 0.0, 1.0))

    return {
        "is_fraud": bool(prediction == -1),
        "fraud_probability": round(fraud_probability, 4),
        "model": "isolation_forest"
    }