import os

import pandas as pd
import requests
import streamlit as st

API_URL = (
    os.getenv(
        "PRODINTEL_API_URL",
        "http://127.0.0.1:8000",
    ).rstrip("/")
    + "/predict-batch"
)

st.set_page_config(
    page_title="ProdIntel - Portfolio Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("Portfolio Intelligence")
st.caption("Batch customer churn analysis and retention prioritization.")

REQUIRED_COLUMNS = [
    "customer_id",
    "tenure_months",
    "monthly_charges",
    "total_charges",
    "cltv",
    "gender",
    "senior_citizen",
    "partner",
    "dependents",
    "phone_service",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract",
    "paperless_billing",
    "payment_method",
]

st.info(
    "Upload a CSV containing the required customer columns. "
    "Use the exact column names shown in the sample template."
)

template = pd.DataFrame(columns=REQUIRED_COLUMNS)

st.download_button(
    "Download CSV template",
    data=template.to_csv(index=False),
    file_name="prodintel_customer_template.csv",
    mime="text/csv",
)

uploaded_files = st.file_uploader(
    "Upload customer CSV files",
    type=["csv"],
    accept_multiple_files=True,
    key="portfolio_csv_upload",
)

if uploaded_files:
    try:
        dataframes = [pd.read_csv(file) for file in uploaded_files]

        customers_df = pd.concat(
            dataframes,
            ignore_index=True,
        )

    except Exception as exc:
        st.error(f"Could not read CSV files: {exc}")
        st.stop()

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in customers_df.columns
    ]

    if missing_columns:
        st.error("Missing required columns: " + ", ".join(missing_columns))
        st.stop()

    if customers_df.empty:
        st.warning("The uploaded CSV contains no customers.")
        st.stop()

    if len(customers_df) > 1000:
        st.error("Please upload a maximum of 1,000 customers per batch.")
        st.stop()

    if customers_df["customer_id"].isna().any():
        st.error("Every customer must have a customer_id.")
        st.stop()

    if customers_df["customer_id"].astype(str).str.strip().eq("").any():
        st.error("Customer IDs cannot be blank.")
        st.stop()

    if customers_df["customer_id"].duplicated().any():
        st.error("Customer IDs must be unique.")
        st.stop()

    st.subheader("Customer Data Preview")
    st.dataframe(customers_df.head(10), use_container_width=True)

    st.write(f"**Customers loaded:** {len(customers_df):,}")

    if st.button("Analyze Customer Portfolio", type="primary"):
        payload_df = customers_df[REQUIRED_COLUMNS].copy()
        payload_df = payload_df.astype(object).where(pd.notna(payload_df), None)

        payload = payload_df.to_dict(orient="records")

        with st.spinner("Analyzing customer portfolio..."):
            try:
                response = requests.post(
                    API_URL,
                    json=payload,  # type: ignore[arg-type]
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()

            except requests.RequestException as exc:
                st.error(f"Could not connect to the prediction API: {exc}")
                st.stop()

        results_df = pd.DataFrame(result["results"])

        if len(results_df) != len(customers_df):
            st.error("The API returned an unexpected number of results.")
            st.stop()

        st.session_state["portfolio_results"] = results_df
        st.session_state["portfolio_source"] = ", ".join(
            file.name for file in uploaded_files
        )

if "portfolio_results" in st.session_state:
    results_df = st.session_state["portfolio_results"].copy()

    st.divider()
    st.subheader("Portfolio Risk Overview")

    total = len(results_df)
    high = int((results_df["risk_band"] == "High").sum())
    moderate = int((results_df["risk_band"] == "Moderate").sum())
    low = int((results_df["risk_band"] == "Low").sum())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", f"{total:,}")
    col2.metric("High Risk", f"{high:,}")
    col3.metric("Moderate Risk", f"{moderate:,}")
    col4.metric("Low Risk", f"{low:,}")

    st.subheader("Business Impact Metrics")

    # Match each prediction to its original customer record.
    business_df = customers_df[["customer_id", "monthly_charges"]].merge(
        results_df[["customer_id", "churn_probability", "risk_band"]],
        on="customer_id",
        how="inner",
        validate="one_to_one",
    )

    total_customers = len(business_df)

    predicted_churn_count = int((business_df["churn_probability"] >= 0.5).sum())

    overall_churn_rate = (
        predicted_churn_count / total_customers * 100 if total_customers else 0
    )

    high_risk_df = business_df[business_df["risk_band"] == "High"]

    monthly_revenue_at_risk = high_risk_df["monthly_charges"].sum()

    average_probability = (
        business_df["churn_probability"].mean() * 100 if total_customers else 0
    )

    st.subheader("Customer Segmentation Insights")

    segmentation_df = customers_df.merge(
        results_df[["customer_id", "risk_band"]],
        on="customer_id",
        how="inner",
        validate="one_to_one",
    )

    high_risk_customers = segmentation_df[segmentation_df["risk_band"] == "High"].copy()

    if high_risk_customers.empty:
        st.info("No high-risk customers were identified in this portfolio.")
    else:
        # Group customer tenure.
        high_risk_customers["tenure_group"] = pd.cut(
            high_risk_customers["tenure_months"],
            bins=[-1, 12, 24, float("inf")],
            labels=["0–12 months", "13–24 months", "25+ months"],
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Contract Type**")
            st.bar_chart(
                high_risk_customers["contract"].value_counts(),
                horizontal=True,
                height=220,
            )

        with col2:
            st.markdown("**Customer Tenure**")
            st.bar_chart(
                high_risk_customers["tenure_group"]
                .value_counts()
                .reindex(
                    ["0–12 months", "13–24 months", "25+ months"],
                    fill_value=0,
                ),
                horizontal=True,
                height=220,
            )

        with col3:
            st.markdown("**Internet Service**")
            st.bar_chart(
                high_risk_customers["internet_service"].value_counts(),
                horizontal=True,
                height=220,
            )

        st.caption(
            "These charts describe the uploaded high-risk segment. "
            "They show associations in this portfolio, not proof "
            "that a particular characteristic causes churn."
        )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Predicted Churn Rate",
        f"{overall_churn_rate:.1f}%",
        help="Share of customers with a predicted churn probability of at least 50%.",
    )

    metric2.metric(
        "Monthly Charges at High Risk",
        f"{monthly_revenue_at_risk:,.2f}",
        help="Sum of monthly charges for customers classified as High Risk. This is not confirmed revenue loss.",
    )

    metric3.metric(
        "Average Churn Probability",
        f"{average_probability:.1f}%",
        help="Mean predicted churn probability across all uploaded customers.",
    )

    st.subheader("Risk Distribution")

    distribution = pd.DataFrame(
        {
            "Risk Level": ["High", "Moderate", "Low"],
            "Customers": [high, moderate, low],
        }
    )

    st.bar_chart(
        distribution.set_index("Risk Level"),
        horizontal=True,
        height=220,
    )

    st.subheader("Customer Risk Results")

    st.subheader("Retention Priorities")

    priority_df = results_df.copy()

    priority_df["churn_probability_pct"] = (
        priority_df["churn_probability"] * 100
    ).round(2)

    priority_df["retention_priority"] = priority_df["risk_band"].map(
        {
            "High": 1,
            "Moderate": 2,
            "Low": 3,
        }
    )

    priority_df = priority_df.sort_values(
        ["retention_priority", "churn_probability"],
        ascending=[True, False],
    )

    high_risk_df = priority_df[priority_df["risk_band"] == "High"].copy()

    if high_risk_df.empty:
        st.success("No customers are currently classified as high risk.")
    else:
        st.warning(f"{len(high_risk_df)} customer(s) need priority retention review.")

        st.dataframe(
            high_risk_df[
                [
                    "customer_id",
                    "prediction",
                    "churn_probability_pct",
                    "risk_band",
                ]
            ].rename(
                columns={
                    "customer_id": "Customer ID",
                    "prediction": "Predicted Churn",
                    "churn_probability_pct": "Churn Probability (%)",
                    "risk_band": "Risk Level",
                }
            ),
            use_container_width=True,
        )

        st.download_button(
            "Download High-Risk Customer Report",
            data=high_risk_df.to_csv(index=False),
            file_name="prodintel_high_risk_customers.csv",
            mime="text/csv",
        )

    st.caption(
        "Priorities are based on model-estimated churn probability. "
        "They are decision-support signals, not guaranteed outcomes."
    )

    results_df["churn_probability"] = (results_df["churn_probability"] * 100).round(2)

    results_df = results_df.rename(
        columns={
            "customer_id": "Customer ID",
            "prediction": "Predicted Churn",
            "churn_probability": "Churn Probability (%)",
            "risk_band": "Risk Level",
        }
    )

    results_df = results_df.sort_values(
        "Churn Probability (%)",
        ascending=False,
    )

    st.dataframe(results_df, use_container_width=True)

    st.download_button(
        "Download Prediction Results",
        data=results_df.to_csv(index=False),
        file_name="prodintel_portfolio_predictions.csv",
        mime="text/csv",
    )

    st.caption(
        "Predictions estimate churn risk; they do not guarantee "
        "that a customer will leave."
    )
