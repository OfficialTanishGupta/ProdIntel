import os

import requests
import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

API_URL = (
    os.getenv(
        "PRODINTEL_API_URL",
        "http://127.0.0.1:8000",
    ).rstrip("/")
    + "/predict"
)


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ProdIntel - Customer Intelligence",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# Custom Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #666666;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.8rem;
        }

        .result-card {
            padding: 1.2rem;
            border-radius: 10px;
            border: 1px solid #dddddd;
            margin-top: 1rem;
        }

        .small-label {
            color: #666666;
            font-size: 0.85rem;
        }

        .big-value {
            font-size: 1.8rem;
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">ProdIntel - Customer Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "ML-powered customer churn analysis and business intelligence"
    "</div>",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Customer Input Form
# --------------------------------------------------

with st.form("customer_churn_form"):

    st.markdown(
        '<div class="section-title">Customer Information</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        tenure_months = st.number_input(
            "Tenure Months",
            min_value=0,
            value=12,
            step=1,
        )

        monthly_charges = st.number_input(
            "Monthly Charges",
            min_value=0.0,
            value=70.0,
            step=1.0,
        )

        total_charges = st.number_input(
            "Total Charges",
            min_value=0.0,
            value=840.0,
            step=10.0,
        )

        cltv = st.number_input(
            "CLTV",
            min_value=0.0,
            value=5000.0,
            step=100.0,
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female"],
        )

        senior_citizen = st.selectbox(
            "Senior Citizen",
            [0, 1],
        )

        partner = st.selectbox(
            "Partner",
            ["Yes", "No"],
        )

        dependents = st.selectbox(
            "Dependents",
            ["Yes", "No"],
        )

        phone_service = st.selectbox(
            "Phone Service",
            ["Yes", "No"],
        )

        multiple_lines = st.selectbox(
            "Multiple Lines",
            ["Yes", "No", "No phone service"],
        )

    with col2:

        internet_service = st.selectbox(
            "Internet Service",
            ["DSL", "Fiber optic", "No"],
        )

        online_security = st.selectbox(
            "Online Security",
            ["Yes", "No", "No internet service"],
        )

        online_backup = st.selectbox(
            "Online Backup",
            ["Yes", "No", "No internet service"],
        )

        device_protection = st.selectbox(
            "Device Protection",
            ["Yes", "No", "No internet service"],
        )

        tech_support = st.selectbox(
            "Tech Support",
            ["Yes", "No", "No internet service"],
        )

        streaming_tv = st.selectbox(
            "Streaming TV",
            ["Yes", "No", "No internet service"],
        )

        streaming_movies = st.selectbox(
            "Streaming Movies",
            ["Yes", "No", "No internet service"],
        )

        contract = st.selectbox(
            "Contract",
            ["Month-to-month", "One year", "Two year"],
        )

        paperless_billing = st.selectbox(
            "Paperless Billing",
            ["Yes", "No"],
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
        )

    submitted = st.form_submit_button(
        "Predict Customer Churn",
        use_container_width=True,
    )


# --------------------------------------------------
# Prediction
# --------------------------------------------------

if submitted:

    customer_data = {
        "tenure_months": tenure_months,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "cltv": cltv,
        "gender": gender,
        "senior_citizen": senior_citizen,
        "partner": partner,
        "dependents": dependents,
        "phone_service": phone_service,
        "multiple_lines": multiple_lines,
        "internet_service": internet_service,
        "online_security": online_security,
        "online_backup": online_backup,
        "device_protection": device_protection,
        "tech_support": tech_support,
        "streaming_tv": streaming_tv,
        "streaming_movies": streaming_movies,
        "contract": contract,
        "paperless_billing": paperless_billing,
        "payment_method": payment_method,
    }

    with st.spinner("Analyzing customer information..."):

        try:

            response = requests.post(
                API_URL,
                json=customer_data,
                timeout=30,
            )

            response.raise_for_status()

            result = response.json()

        except requests.exceptions.ConnectionError:

            st.error("The Customer Intelligence API is currently unavailable.")
            st.info("Please verify that the ProdIntel API service is running.")
            st.stop()

        except requests.exceptions.Timeout:

            st.error("The prediction request timed out.")
            st.info("Please try again in a few moments.")
            st.stop()

        except requests.exceptions.HTTPError as error:

            st.error("The API rejected the prediction request.")
            st.code(str(error))
            st.stop()

        except requests.exceptions.RequestException as error:

            st.error("An unexpected API error occurred.")
            st.code(str(error))
            st.stop()

    prediction = result["prediction"]
    probability = float(result["churn_probability"])

    probability_percent = probability * 100

    # --------------------------------------------------
    # Risk Band
    # --------------------------------------------------

    if probability < 0.30:
        risk_band = "Low"
        risk_message = "The estimated churn probability is relatively low."

    elif probability < 0.60:
        risk_band = "Moderate"
        risk_message = "The customer shows a moderate estimated churn probability."

    else:
        risk_band = "High"
        risk_message = (
            "The customer shows a relatively high estimated churn probability."
        )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    st.divider()

    st.subheader("Prediction Result")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Churn Probability",
            f"{probability_percent:.2f}%",
        )

    with metric2:
        st.metric(
            "Model Prediction",
            prediction,
        )

    with metric3:
        st.metric(
            "Risk Band",
            risk_band,
        )

    st.progress(min(max(probability, 0.0), 1.0))

    # --------------------------------------------------
    # Business Interpretation
    # --------------------------------------------------

    st.subheader("Business Insight")

    st.write(risk_message)

    if prediction == "Yes":

        st.warning(
            "The model predicts that this customer belongs to "
            "the churn class. The customer may require additional "
            "retention analysis or engagement."
        )

    else:

        st.success(
            "The model predicts that this customer belongs to " "the non-churn class."
        )

    # --------------------------------------------------
    # Customer Indicators
    # --------------------------------------------------

    st.subheader("Customer Indicators")

    indicator1, indicator2, indicator3, indicator4 = st.columns(4)

    with indicator1:
        st.metric(
            "Tenure",
            f"{tenure_months} months",
        )

    with indicator2:
        st.metric(
            "Monthly Charges",
            f"{monthly_charges:.2f}",
        )

    with indicator3:
        st.metric(
            "Contract",
            contract,
        )

    with indicator4:
        st.metric(
            "Internet Service",
            internet_service,
        )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption("ProdIntel Customer Intelligence | " "ML-powered customer churn prediction")
