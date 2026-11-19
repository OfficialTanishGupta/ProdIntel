from pathlib import Path

import joblib
import pandas as pd
from app.schemas import CustomerChurnRequest, EmployeeAttritionRequest


from typing import List

from app.schemas import CustomerChurnRequest
from app.explainability import explain_prediction

from datetime import datetime


from pydantic import BaseModel, Field
import logging

from fastapi import FastAPI, HTTPException, Query
from app.database import load_portfolio_history, save_portfolio_snapshot

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "customer_churn_model.joblib"
logger = logging.getLogger(__name__)

model = joblib.load(MODEL_PATH)
EMPLOYEE_ATTRITION_MODEL_PATH = BASE_DIR / "models" / "employee_attrition_model.joblib"

employee_attrition_bundle = joblib.load(EMPLOYEE_ATTRITION_MODEL_PATH)

employee_attrition_model = employee_attrition_bundle["model"]
employee_attrition_threshold = float(employee_attrition_bundle["threshold"])


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

    try:
        prediction = model.predict(customer_data)[0]
        probability = model.predict_proba(customer_data)[0][1]
    except Exception as exc:
        logger.exception("Customer churn prediction failed.")
        raise HTTPException(
            status_code=500,
            detail="Customer churn prediction failed.",
        ) from exc

    try:
        explanation = explain_prediction(model, customer_data, top_n=5)
    except Exception:
        logger.exception("Prediction explanation generation failed.")
        explanation = {"higher_risk": [], "lower_risk": []}

    return {
        "prediction": str(prediction),
        "churn_probability": round(float(probability), 4),
        "explanation": explanation,
    }


@app.post("/predict-batch")
def predict_batch(customers: List[CustomerChurnRequest]):
    if not customers:
        return {"total_customers": 0, "results": []}

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

    try:
        predictions = model.predict(customer_data)
        probabilities = model.predict_proba(customer_data)[:, 1]
    except Exception as exc:
        logger.exception("Batch customer churn prediction failed.")
        raise HTTPException(
            status_code=500,
            detail="Batch customer churn prediction failed.",
        ) from exc

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
                "prediction": str(prediction),
                "churn_probability": round(probability, 4),
                "risk_band": risk_band,
            }
        )

    return {
        "total_customers": len(results),
        "results": results,
    }


@app.post("/predict-attrition")
def predict_employee_attrition(employee: EmployeeAttritionRequest):
    employee_data = pd.DataFrame(
        [
            {
                "Age": employee.age,
                "BusinessTravel": employee.business_travel,
                "DailyRate": employee.daily_rate,
                "Department": employee.department,
                "DistanceFromHome": employee.distance_from_home,
                "Education": employee.education,
                "EducationField": employee.education_field,
                "EnvironmentSatisfaction": employee.environment_satisfaction,
                "Gender": employee.gender,
                "HourlyRate": employee.hourly_rate,
                "JobInvolvement": employee.job_involvement,
                "JobLevel": employee.job_level,
                "JobRole": employee.job_role,
                "JobSatisfaction": employee.job_satisfaction,
                "MaritalStatus": employee.marital_status,
                "MonthlyIncome": employee.monthly_income,
                "MonthlyRate": employee.monthly_rate,
                "NumCompaniesWorked": employee.num_companies_worked,
                "OverTime": employee.overtime,
                "PercentSalaryHike": employee.percent_salary_hike,
                "PerformanceRating": employee.performance_rating,
                "RelationshipSatisfaction": employee.relationship_satisfaction,
                "StockOptionLevel": employee.stock_option_level,
                "TotalWorkingYears": employee.total_working_years,
                "TrainingTimesLastYear": employee.training_times_last_year,
                "WorkLifeBalance": employee.work_life_balance,
                "YearsAtCompany": employee.years_at_company,
                "YearsInCurrentRole": employee.years_in_current_role,
                "YearsSinceLastPromotion": employee.years_since_last_promotion,
                "YearsWithCurrManager": employee.years_with_curr_manager,
            }
        ]
    )

    try:
        probability = float(employee_attrition_model.predict_proba(employee_data)[0][1])

        prediction = "Yes" if probability >= employee_attrition_threshold else "No"

    except Exception as exc:
        logger.exception("Employee attrition prediction failed.")
        raise HTTPException(
            status_code=500,
            detail="Employee attrition prediction failed.",
        ) from exc

    return {
        "prediction": prediction,
        "attrition_probability": round(probability, 4),
        "threshold": employee_attrition_threshold,
    }


@app.get("/portfolio-history")
def get_portfolio_history(limit: int = Query(default=500, ge=1, le=5000)):
    try:
        history = load_portfolio_history(limit=limit)
        return {
            "total_snapshots": len(history),
            "history": history,
        }
    except Exception as exc:
        logger.exception("Failed to retrieve portfolio history.")
        raise HTTPException(
            status_code=503,
            detail="Portfolio history service temporarily unavailable.",
        ) from exc


@app.post("/portfolio-history")
def save_portfolio_snapshot_endpoint(snapshot: PortfolioSnapshot):
    try:
        return save_portfolio_snapshot(snapshot)
    except Exception as exc:
        logger.exception("Failed to save portfolio history.")
        raise HTTPException(
            status_code=503,
            detail="Portfolio history service temporarily unavailable.",
        ) from exc
