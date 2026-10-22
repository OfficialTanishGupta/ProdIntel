from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI
from typing import List

from app.schemas import CustomerChurnRequest
from app.explainability import explain_prediction

from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, Field

from app.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "customer_churn_model.joblib"


model = joblib.load(MODEL_PATH)


class PortfolioSnapshot(BaseModel):
    analysis_timestamp: datetime
    total_customers: int = Field(ge=0)
    high_risk: int = Field(ge=0)
    moderate_risk: int = Field(ge=0)
    low_risk: int = Field(ge=0)
    average_churn_probability_pct: float = Field(ge=0, le=100)


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

    try:
        explanation = explain_prediction(model, customer_data, top_n=5)
    except Exception:
        explanation = {"higher_risk": [], "lower_risk": []}

    return {
        "prediction": str(prediction),
        "churn_probability": round(float(probability), 4),
        "explanation": explanation,
    }


@app.post("/predict-batch")
def predict_batch(customers: List[CustomerChurnRequest]):
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
            for customer in customers
        ]
    )


@app.get("/portfolio-history")
def get_portfolio_history(limit: int = Query(default=500, ge=1, le=5000)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    analysis_timestamp,
                    total_customers,
                    high_risk,
                    moderate_risk,
                    low_risk,
                    average_churn_probability_pct
                FROM portfolio_history
                ORDER BY analysis_timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            history = cursor.fetchall()

    return {
        "total_snapshots": len(history),
        "history": history,
    }


@app.post("/portfolio-history")
def save_portfolio_snapshot(snapshot: PortfolioSnapshot):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # Avoid saving an identical snapshot twice.
            cursor.execute(
                """
                SELECT id
                FROM portfolio_history
                WHERE analysis_timestamp = %s
                  AND total_customers = %s
                  AND high_risk = %s
                  AND moderate_risk = %s
                  AND low_risk = %s
                  AND average_churn_probability_pct = %s
                LIMIT 1
                """,
                (
                    snapshot.analysis_timestamp,
                    snapshot.total_customers,
                    snapshot.high_risk,
                    snapshot.moderate_risk,
                    snapshot.low_risk,
                    snapshot.average_churn_probability_pct,
                ),
            )

            existing = cursor.fetchone()

            if existing:
                return {
                    "message": "Snapshot already exists",
                    "saved": False,
                }

            cursor.execute(
                """
                INSERT INTO portfolio_history (
                    analysis_timestamp,
                    total_customers,
                    high_risk,
                    moderate_risk,
                    low_risk,
                    average_churn_probability_pct
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    snapshot.analysis_timestamp,
                    snapshot.total_customers,
                    snapshot.high_risk,
                    snapshot.moderate_risk,
                    snapshot.low_risk,
                    snapshot.average_churn_probability_pct,
                ),
            )

    return {
        "message": "Portfolio snapshot saved successfully",
        "saved": True,
    }

    predictions = model.predict(customer_data)
    probabilities = model.predict_proba(customer_data)[:, 1]

    results = []

    for customer, prediction, probability in zip(customers, predictions, probabilities):
        probability = float(probability)

        if probability < 0.30:
            risk_band = "Low"
        elif probability < 0.60:
            risk_band = "Moderate"
        else:
            risk_band = "High"

        results.append(
            {
                "customer_id": customer.customer_id,
                "prediction": prediction,
                "churn_probability": round(probability, 4),
                "risk_band": risk_band,
            }
        )

    return {"total_customers": len(results), "results": results}

    try:
        explanation = explain_prediction(model, customer_data, top_n=5)
    except Exception:
        explanation = {"higher_risk": [], "lower_risk": []}

    return {
        "prediction": prediction,
        "churn_probability": round(float(probability), 4),
        "explanation": explanation,
    }
