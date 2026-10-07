from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI
from typing import List

from app.schemas import CustomerChurnRequest
from app.explainability import explain_prediction

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "customer_churn_model.joblib"


model = joblib.load(MODEL_PATH)


app = FastAPI(
    title="ProdIntel Customer Churn API",
    description="API for customer churn prediction.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "ProdIntel Customer Churn API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/predict")
def predict_churn(customer: CustomerChurnRequest):

    customer_data = pd.DataFrame(
        [
            {
                "Tenure Months": customer.tenure_months,
                "Monthly Charges": customer.monthly_charges,
                "Total Charges": customer.total_charges,
                "CLTV": customer.cltv,
                "Gender": customer.gender,
                "Senior Citizen": customer.senior_citizen,
                "Partner": customer.partner,
                "Dependents": customer.dependents,
                "Phone Service": customer.phone_service,
                "Multiple Lines": customer.multiple_lines,
                "Internet Service": customer.internet_service,
                "Online Security": customer.online_security,
                "Online Backup": customer.online_backup,
                "Device Protection": customer.device_protection,
                "Tech Support": customer.tech_support,
                "Streaming TV": customer.streaming_tv,
                "Streaming Movies": customer.streaming_movies,
                "Contract": customer.contract,
                "Paperless Billing": customer.paperless_billing,
                "Payment Method": customer.payment_method,
            }
        ]
    )

    prediction = model.predict(customer_data)[0]
    probability = model.predict_proba(customer_data)[0][1]
    
@app.post("/predict-batch")
def predict_batch(customers: List[CustomerChurnRequest]):
    customer_data = pd.DataFrame([
        {
            "Tenure Months": customer.tenure_months,
            "Monthly Charges": customer.monthly_charges,
            "Total Charges": customer.total_charges,
            "CLTV": customer.cltv,
            "Gender": customer.gender,
            "Senior Citizen": customer.senior_citizen,
            "Partner": customer.partner,
            "Dependents": customer.dependents,
            "Phone Service": customer.phone_service,
            "Multiple Lines": customer.multiple_lines,
            "Internet Service": customer.internet_service,
            "Online Security": customer.online_security,
            "Online Backup": customer.online_backup,
            "Device Protection": customer.device_protection,
            "Tech Support": customer.tech_support,
            "Streaming TV": customer.streaming_tv,
            "Streaming Movies": customer.streaming_movies,
            "Contract": customer.contract,
            "Paperless Billing": customer.paperless_billing,
            "Payment Method": customer.payment_method
        }
        for customer in customers
    ])

    predictions = model.predict(customer_data)
    probabilities = model.predict_proba(customer_data)[:, 1]

    results = []

    for prediction, probability in zip(predictions, probabilities):
        probability = float(probability)

        if probability < 0.30:
            risk_band = "Low"
        elif probability < 0.60:
            risk_band = "Moderate"
        else:
            risk_band = "High"

        results.append({
            "prediction": prediction,
            "churn_probability": round(probability, 4),
            "risk_band": risk_band
        })

    return {
        "total_customers": len(results),
        "results": results
    }

    try:
        explanation = explain_prediction(model, customer_data, top_n=5)
    except Exception:
        explanation = {"higher_risk": [], "lower_risk": []}

    return {
        "prediction": prediction,
        "churn_probability": round(float(probability), 4),
        "explanation": explanation,
    }
