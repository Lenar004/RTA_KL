from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI(title="Fraud Detection API")

with open("fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

class Transaction(BaseModel):
    amount: float
    hour: int
    is_electronics: int
    tx_per_day: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(tx: Transaction):
    x = np.array([[tx.amount, tx.hour, tx.is_electronics, tx.tx_per_day]])
    fraud_probability = float(model.predict_proba(x)[0][1])
    is_fraud = bool(model.predict(x)[0])

    return {
        "is_fraud": is_fraud,
        "fraud_probability": fraud_probability
    }