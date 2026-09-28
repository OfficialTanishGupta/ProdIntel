from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {"message": "ProdIntel Customer Churn API is running"}


def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


VALID_CUSTOMER = {
    "tenure_months": 5,
    "monthly_charges": 85.5,
    "total_charges": 430.0,
    "cltv": 5500.0,
    "gender": "Male",
    "senior_citizen": 0,
    "partner": "No",
    "dependents": "No",
    "phone_service": "Yes",
    "multiple_lines": "No",
    "internet_service": "Fiber optic",
    "online_security": "No",
    "online_backup": "No",
    "device_protection": "No",
    "tech_support": "No",
    "streaming_tv": "Yes",
    "streaming_movies": "Yes",
    "contract": "Month-to-month",
    "paperless_billing": "Yes",
    "payment_method": "Electronic check",
}


def test_prediction_endpoint():

    response = client.post("/predict", json=VALID_CUSTOMER)

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "churn_probability" in data

    assert data["prediction"] in ["Yes", "No"]

    assert 0 <= data["churn_probability"] <= 1


def test_missing_required_field():

    invalid_customer = VALID_CUSTOMER.copy()

    del invalid_customer["tenure_months"]

    response = client.post("/predict", json=invalid_customer)

    assert response.status_code == 422


def test_invalid_data_type():

    invalid_customer = VALID_CUSTOMER.copy()

    invalid_customer["monthly_charges"] = "not-a-number"

    response = client.post("/predict", json=invalid_customer)

    assert response.status_code == 422


def test_invalid_categorical_value():

    invalid_customer = VALID_CUSTOMER.copy()

    invalid_customer["contract"] = "Invalid Contract"

    response = client.post("/predict", json=invalid_customer)

    assert response.status_code == 422


def test_negative_numeric_value():

    invalid_customer = VALID_CUSTOMER.copy()

    invalid_customer["tenure_months"] = -1

    response = client.post("/predict", json=invalid_customer)

    assert response.status_code == 422

