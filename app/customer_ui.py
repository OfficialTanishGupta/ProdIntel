import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="ProdIntel - Customer Intelligence",
    page_icon="📊",  # Added a default icon
    layout="wide",
)

st.title("ProdIntel - Customer Intelligence")
st.subheader("Customer Churn Prediction")
st.write("Enter customer information to estimate the probability of customer churn.")

with st.form("customer_churn_form"):
    st.subheader("Customer Information")
    col1, col2 = st.columns(2)

    with col1:
        tenure_months = st.number_input("Tenure Months", min_value=0, value=12, step=1)
        monthly_charges = st.number_input(
            "Monthly Charges", min_value=0.0, value=70.0, step=1.0
        )
        total_charges = st.number_input(
            "Total Charges", min_value=0.0, value=840.0, step=10.0
        )
        cltv = st.number_input("CLTV", min_value=0.0, value=5000.0, step=100.0)
        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior Citizen", [0, 1])
        partner = st.selectbox("Partner", ["Yes", "No"])
        dependents = st.selectbox("Dependents", ["Yes", "No"])
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox(
            "Multiple Lines", ["Yes", "No", "No phone service"]
        )

    with col2:
        internet_service = st.selectbox(
            "Internet Service", ["DSL", "Fiber optic", "No"]
        )
        online_security = st.selectbox(
            "Online Security", ["Yes", "No", "No internet service"]
        )
        online_backup = st.selectbox(
            "Online Backup", ["Yes", "No", "No internet service"]
        )
        device_protection = st.selectbox(
            "Device Protection", ["Yes", "No", "No internet service"]
        )
        tech_support = st.selectbox(
            "Tech Support", ["Yes", "No", "No internet service"]
        )
        streaming_tv = st.selectbox(
            "Streaming TV", ["Yes", "No", "No internet service"]
        )
        streaming_movies = st.selectbox(
            "Streaming Movies", ["Yes", "No", "No internet service"]
        )
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment_method = st.selectbox(
            "Payment Method",
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
        )

    submitted = st.form_submit_button("Predict Customer Churn")

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

    # Added a spinner context manager for better UX
    with st.spinner("Connecting to API and calculating prediction..."):
        try:
            response = requests.post(API_URL, json=customer_data, timeout=10)
            response.raise_for_status()
            result = response.json()

            # Moved rendering code safely inside the successful block
            prediction = result["prediction"]
            probability = result["churn_probability"]

            st.divider()
            st.subheader("Prediction Result")
            st.metric("Churn Probability", f"{probability * 100:.2f}%")
            st.write(f"Model prediction: **{prediction}**")
            st.progress(probability)

            if prediction == "Yes":
                st.warning(
                    "The model predicts that this customer belongs to the churn class."
                )
            else:
                st.success(
                    "The model predicts that this customer belongs to the non-churn class."
                )

        except requests.exceptions.RequestException as error:
            st.error("Unable to connect to the Customer Churn API.")
            st.code(str(error))


st.divider()

st.caption("ProdIntel Customer Intelligence | " "ML-powered customer churn prediction")
