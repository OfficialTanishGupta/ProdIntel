import os
import pandas as pd
import requests
import streamlit as st
from datetime import datetime
from pathlib import Path

API_BASE_URL = os.getenv(
    "PRODINTEL_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

PREDICT_BATCH_URL = f"{API_BASE_URL}/predict-batch"
PORTFOLIO_HISTORY_URL = f"{API_BASE_URL}/portfolio-history"


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


def load_portfolio_history():
    """Load historical portfolio snapshots from the backend."""
    response = requests.get(
        PORTFOLIO_HISTORY_URL,
        params={"limit": 5000},
        timeout=30,
    )
    response.raise_for_status()

    history = response.json().get("history", [])
    return pd.DataFrame(history)


def save_portfolio_snapshot(snapshot):
    """Save a portfolio snapshot through the backend API."""
    response = requests.post(
        PORTFOLIO_HISTORY_URL,
        json=snapshot,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


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
        customers_df = pd.concat(dataframes, ignore_index=True)
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
        payload = [
            {str(k): v for k, v in record.items()}
            for record in payload_df.to_dict(orient="records")
        ]

        with st.spinner("Analyzing customer portfolio..."):
            try:
                response = requests.post(
                    PREDICT_BATCH_URL,
                    json=payload,
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

        st.session_state["portfolio_results"] = results_df.copy()
        st.session_state["portfolio_customers"] = customers_df.copy()
        st.session_state["portfolio_source"] = ", ".join(
            file.name for file in uploaded_files
        )

        history_dir = Path("data/portfolio_history")
        history_dir.mkdir(parents=True, exist_ok=True)

        snapshot = {
            "analysis_timestamp": datetime.now()
            .astimezone()
            .isoformat(timespec="seconds"),
            "total_customers": len(results_df),
            "high_risk": int((results_df["risk_band"] == "High").sum()),
            "moderate_risk": int((results_df["risk_band"] == "Moderate").sum()),
            "low_risk": int((results_df["risk_band"] == "Low").sum()),
            "average_churn_probability_pct": round(
                results_df["churn_probability"].mean() * 100, 2
            ),
        }

        try:
            save_result = save_portfolio_snapshot(snapshot)

            if save_result.get("saved"):
                st.success("Portfolio snapshot saved to PostgreSQL.")
            else:
                st.info("This portfolio snapshot already exists in PostgreSQL.")

        except requests.RequestException as exc:
            st.warning(
                "Predictions completed, but the historical snapshot could not "
                f"be saved to PostgreSQL: {exc}"
            )

    if (
        "portfolio_results" in st.session_state
        and "portfolio_customers" in st.session_state
    ):
        results_df = st.session_state["portfolio_results"].copy()
        customers_df = st.session_state["portfolio_customers"].copy()

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

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric(
            "Predicted Churn Rate",
            f"{overall_churn_rate:.1f}%",
            help="Share of customers with a predicted churn probability of at least 50%.",
        )
        metric2.metric(
            "Monthly Charges at High Risk",
            f"{monthly_revenue_at_risk:,.2f}",
            help="Sum of monthly charges for customers classified as High Risk.",
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
        st.bar_chart(distribution.set_index("Risk Level"), horizontal=True, height=220)

        st.subheader("Customer Segmentation Insights")
        segmentation_df = customers_df.merge(
            results_df[["customer_id", "risk_band"]],
            on="customer_id",
            how="inner",
            validate="one_to_one",
        )

        high_risk_customers = segmentation_df[
            segmentation_df["risk_band"] == "High"
        ].copy()

        if high_risk_customers.empty:
            st.info("No high-risk customers were identified in this portfolio.")
        else:
            high_risk_customers["tenure_group"] = pd.cut(
                high_risk_customers["tenure_months"],
                bins=[-1, 12, 24, float("inf")],
                labels=["0–12 months", "13–24 months", "25+ months"],
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Contract Type**")
                st.bar_chart(
                    high_risk_customers["contract"].value_counts(),
                    horizontal=True,
                    height=220,
                )
            with c2:
                st.markdown("**Customer Tenure**")
                st.bar_chart(
                    high_risk_customers["tenure_group"]
                    .value_counts()
                    .reindex(
                        ["0–12 months", "13–24 months", "25+ months"], fill_value=0
                    ),
                    horizontal=True,
                    height=220,
                )
            with c3:
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

        st.subheader("Customer Risk Results")
        priority_df = results_df.copy()
        priority_df["churn_probability_pct"] = (
            priority_df["churn_probability"] * 100
        ).round(2)
        priority_df["retention_priority"] = priority_df["risk_band"].map(
            {"High": 1, "Moderate": 2, "Low": 3}
        )
        priority_df = priority_df.sort_values(
            ["retention_priority", "churn_probability"], ascending=[True, False]
        )
        high_risk_df = priority_df[priority_df["risk_band"] == "High"].copy()

        st.subheader("Recommended Retention Actions")

        def recommend_retention_actions(customer):
            actions = []
            if str(customer.get("contract", "")).strip().lower() == "month-to-month":
                actions.append(
                    "Offer an incentive to switch to a longer-term contract."
                )
            try:
                if float(customer.get("tenure_months", 0)) < 12:
                    actions.append(
                        "Provide onboarding support and a proactive check-in."
                    )
            except (TypeError, ValueError):
                pass
            if str(customer.get("tech_support", "")).strip().lower() == "no":
                actions.append("Review eligibility for a technical-support offer.")
            if str(customer.get("online_security", "")).strip().lower() == "no":
                actions.append("Explain available online-security options.")
            if "electronic check" in str(customer.get("payment_method", "")).lower():
                actions.append("Encourage convenient automatic payment options.")
            if not actions:
                actions.append(
                    "Arrange proactive customer outreach and review feedback."
                )
            return " ".join(actions)

        if high_risk_df.empty:
            st.info("No high-risk customers currently require targeted actions.")
            st.success("No customers are currently classified as high risk.")
        else:
            st.warning(
                f"{len(high_risk_df)} customer(s) need priority retention review."
            )
            recommendation_df = customers_df.merge(
                high_risk_df[["customer_id", "churn_probability", "risk_band"]],
                on="customer_id",
                how="inner",
            )
            recommendation_df["Recommended Actions"] = recommendation_df.apply(
                recommend_retention_actions, axis=1
            )
            recommendation_df["Priority Score"] = (
                recommendation_df["churn_probability"] * 100
            ).round(1)

            def get_next_action(customer):
                actions = str(customer.get("Recommended Actions", ""))
                if "longer-term contract" in actions:
                    return "Contact customer about contract options"
                if "onboarding support" in actions:
                    return "Schedule proactive customer check-in"
                if "technical-support offer" in actions:
                    return "Review technical-support offer"
                if "online-security options" in actions:
                    return "Discuss online-security options"
                if "automatic payment options" in actions:
                    return "Discuss automatic payment options"
                return "Arrange proactive retention outreach"

            recommendation_df["Suggested Next Step"] = recommendation_df.apply(
                get_next_action, axis=1
            )

            st.subheader("Retention Strategy Insights")
            contract_risk = (
                recommendation_df["contract"]
                .astype(str)
                .str.lower()
                .eq("month-to-month")
                .sum()
            )
            short_tenure_risk = (
                pd.to_numeric(recommendation_df["tenure_months"], errors="coerce")
                .lt(12)
                .sum()
            )
            service_support_risk = (
                recommendation_df["tech_support"].astype(str).str.lower().eq("no").sum()
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Month-to-Month Customers", int(contract_risk))
            m2.metric("Customers Under 12 Months", int(short_tenure_risk))
            m3.metric("Customers Without Tech Support", int(service_support_risk))

            st.caption(
                "These counts describe the high-risk customers in the analyzed portfolio. "
                "They indicate potential retention opportunities, not proven causes of churn."
            )

            display_df = recommendation_df[
                [
                    "customer_id",
                    "churn_probability",
                    "Priority Score",
                    "Suggested Next Step",
                    "Recommended Actions",
                ]
            ].copy()
            display_df["churn_probability"] = (
                display_df["churn_probability"] * 100
            ).round(2).astype(str) + "%"

            st.dataframe(
                display_df.sort_values("Priority Score", ascending=False),
                hide_index=True,
                use_container_width=True,
            )

            st.download_button(
                "Download Retention Action Plan",
                data=recommendation_df[
                    [
                        "customer_id",
                        "risk_band",
                        "churn_probability",
                        "Priority Score",
                        "Suggested Next Step",
                        "Recommended Actions",
                    ]
                ].to_csv(index=False),
                file_name="prodintel_retention_action_plan.csv",
                mime="text/csv",
            )

            st.dataframe(
                high_risk_df[
                    ["customer_id", "prediction", "churn_probability_pct", "risk_band"]
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

        display_results_df = results_df.copy()
        display_results_df["churn_probability"] = (
            display_results_df["churn_probability"] * 100
        ).round(2)
        display_results_df = display_results_df.rename(
            columns={
                "customer_id": "Customer ID",
                "prediction": "Predicted Churn",
                "churn_probability": "Churn Probability (%)",
                "risk_band": "Risk Level",
            }
        ).sort_values("Churn Probability (%)", ascending=False)

        st.dataframe(display_results_df, use_container_width=True)

        st.download_button(
            "Download Prediction Results",
            data=display_results_df.to_csv(index=False),
            file_name="prodintel_portfolio_predictions.csv",
            mime="text/csv",
        )

        st.divider()
        st.subheader("Executive Portfolio Summary")

        summary_df = pd.DataFrame(
            [
                {"Metric": "Total Customers Analyzed", "Value": total},
                {"Metric": "High-Risk Customers", "Value": high},
                {"Metric": "Moderate-Risk Customers", "Value": moderate},
                {"Metric": "Low-Risk Customers", "Value": low},
                {
                    "Metric": "Predicted Churn Rate (%)",
                    "Value": round(overall_churn_rate, 2),
                },
                {
                    "Metric": "Average Churn Probability (%)",
                    "Value": round(average_probability, 2),
                },
                {
                    "Metric": "Monthly Charges Associated with High-Risk Customers",
                    "Value": round(float(monthly_revenue_at_risk), 2),
                },
            ]
        )

        st.dataframe(summary_df, hide_index=True, use_container_width=True)

        st.download_button(
            "Download Executive Summary",
            data=summary_df.to_csv(index=False),
            file_name="prodintel_executive_summary.csv",
            mime="text/csv",
        )


st.divider()
st.subheader("Portfolio Risk Trends")

try:
    history_df = load_portfolio_history()

except requests.RequestException as exc:
    st.error(f"Could not load portfolio history from the API: {exc}")
    history_df = pd.DataFrame()

if not history_df.empty:
    history_df["analysis_timestamp"] = pd.to_datetime(
        history_df["analysis_timestamp"],
        errors="coerce",
    )

    history_df = (
        history_df.dropna(subset=["analysis_timestamp"])
        .sort_values("analysis_timestamp")
        .reset_index(drop=True)
    )

    if not history_df.empty:
        required_columns = [
            "total_customers",
            "high_risk",
            "moderate_risk",
            "low_risk",
            "average_churn_probability_pct",
        ]

        missing_columns = [
            column for column in required_columns if column not in history_df.columns
        ]

        if missing_columns:
            st.error(
                "Portfolio history is missing required columns: "
                + ", ".join(missing_columns)
            )
        else:
            latest = history_df.iloc[-1]
            previous = history_df.iloc[-2] if len(history_df) > 1 else None

            latest_timestamp = latest["analysis_timestamp"]
            latest_timestamp_text = latest_timestamp.strftime("%d %b %Y, %I:%M:%S %p")

            st.caption(
                "Historical comparisons use consecutive analysis snapshots. "
                "Customer populations may differ between analyses."
            )

            # Analysis metadata
            st.markdown("#### Analysis Overview")

            meta1, meta2 = st.columns(2)

            with meta1:
                st.metric(
                    "Recorded Analyses",
                    f"{len(history_df):,}",
                )

            with meta2:
                st.metric(
                    "Latest Analysis",
                    latest_timestamp_text,
                )

            # Latest portfolio metrics
            st.markdown("#### Latest Portfolio Snapshot")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric(
                "Total Customers",
                f"{int(latest['total_customers']):,}",
            )

            col2.metric(
                "High Risk",
                f"{int(latest['high_risk']):,}",
            )

            col3.metric(
                "Moderate Risk",
                f"{int(latest['moderate_risk']):,}",
            )

            col4.metric(
                "Low Risk",
                f"{int(latest['low_risk']):,}",
            )

            col5.metric(
                "Average Churn Probability",
                f"{latest['average_churn_probability_pct']:.2f}%",
            )

            # Compare the latest snapshot with the previous one
            if previous is not None:
                st.markdown("#### Change Since Previous Analysis")

                risk1, risk2, risk3, risk4 = st.columns(4)

                high_delta = int(latest["high_risk"] - previous["high_risk"])
                moderate_delta = int(
                    latest["moderate_risk"] - previous["moderate_risk"]
                )
                low_delta = int(latest["low_risk"] - previous["low_risk"])
                customer_delta = int(
                    latest["total_customers"] - previous["total_customers"]
                )

                probability_delta = (
                    latest["average_churn_probability_pct"]
                    - previous["average_churn_probability_pct"]
                )

                risk1.metric(
                    "High-Risk Count Change",
                    f"{high_delta:+d}",
                    delta_color="off",
                )

                risk2.metric(
                    "Moderate-Risk Count Change",
                    f"{moderate_delta:+d}",
                    delta_color="off",
                )

                risk3.metric(
                    "Low-Risk Count Change",
                    f"{low_delta:+d}",
                    delta_color="off",
                )

                risk4.metric(
                    "Customer Count Change",
                    f"{customer_delta:+d}",
                    delta_color="off",
                )

                st.metric(
                    "Average Churn Probability Change",
                    f"{probability_delta:+.2f} percentage points",
                    delta_color="off",
                )

                st.caption(
                    "Positive changes indicate increases; negative changes "
                    "indicate decreases. These are differences between "
                    "snapshots, not necessarily changes in the same customers."
                )

                # Business-friendly interpretation
                if high_delta > 0:
                    st.warning(
                        f"High-risk customer count increased by "
                        f"{high_delta}. Review the latest high-risk "
                        "customer list and prioritize appropriate retention actions."
                    )
                elif high_delta < 0:
                    st.info(
                        f"High-risk customer count decreased by "
                        f"{abs(high_delta)} compared with the previous analysis. "
                        "Validate the customer populations before concluding "
                        "that retention risk has improved."
                    )
                else:
                    st.info(
                        "High-risk customer count is unchanged "
                        "from the previous analysis."
                    )

            else:
                st.info(
                    "A previous snapshot is needed to calculate historical "
                    "changes. Comparisons will appear after another successful "
                    "portfolio analysis."
                )

            # Historical risk chart
            st.markdown("#### Risk Distribution Over Time")

            st.line_chart(
                history_df.set_index("analysis_timestamp")[
                    ["high_risk", "moderate_risk", "low_risk"]
                ]
            )

            # Full historical data
            with st.expander("View Historical Analysis Records"):
                st.dataframe(
                    history_df,
                    hide_index=True,
                    use_container_width=True,
                )

            # Download does not append a history snapshot
            st.download_button(
                "Download Portfolio Trend History",
                data=history_df.to_csv(index=False),
                file_name="prodintel_portfolio_trends.csv",
                mime="text/csv",
                key="download_portfolio_trend_history",
            )

    else:
        st.info("No valid portfolio history is available yet.")

else:
    st.info("Run a successful portfolio analysis to start building trend history.")
