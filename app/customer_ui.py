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

RISK_STYLES = {
    "Low": {"color": "#15803d", "bg": "#f0fdf4", "border": "#bbf7d0"},
    "Moderate": {"color": "#b45309", "bg": "#fffbeb", "border": "#fde68a"},
    "High": {"color": "#b91c1c", "bg": "#fef2f2", "border": "#fecaca"},
}


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="ProdIntel - Customer Intelligence",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root { color-scheme: light; }

html, body, [class*="css"], .stApp, button, input, select, textarea {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stApp {
    background: #f8fafc;
    color: #0f172a;
}

.stApp p, .stApp span, .stApp li {
    color: inherit;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1180px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

/* Hero */
.hero {
    padding: 2rem 2.2rem;
    border-radius: 16px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #334155 100%);
    margin-bottom: 1.6rem;
}
.hero-eyebrow {
    color: #94a3b8 !important;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    color: #f8fafc !important;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0;
}
.hero-subtitle {
    color: #cbd5e1 !important;
    font-size: 0.98rem;
    margin-top: 0.4rem;
    font-weight: 400;
}

/* Section headings */
.section-title {
    color: #0f172a;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 0.1rem;
}
.section-desc {
    color: #64748b;
    font-size: 0.82rem;
    margin-bottom: 0.8rem;
}

/* Card containers (keyed containers + fallback for bordered wrapper) */
[class*="st-key-card"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}
[class*="st-key-card"] { padding: 1.2rem 1.3rem; }

/* Nested wrappers should not double-draw borders */
[class*="st-key-card"] div[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* Form wrapper: no extra frame */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

/* Widget labels */
label, label p, div[data-testid="stWidgetLabel"] p {
    color: #334155 !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
}

/* Inputs & selects: force light appearance */
div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background-color: #0f172a !important;
    border-color: #cbd5e1 !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] > div:hover,
div[data-baseweb="input"]:hover {
    border-color: #94a3b8 !important;
}
div[data-baseweb="select"] *,
div[data-baseweb="input"] input,
.stNumberInput input {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    background-color: transparent !important;
}
div[data-baseweb="select"] svg { fill: #64748b !important; }
.stNumberInput button {
    background: #f1f5f9 !important;
    color: #334155 !important;
    border-color: #e2e8f0 !important;
}
.stNumberInput button svg { fill: #334155 !important; }

/* Dropdown menu */
div[data-baseweb="popover"] div[data-baseweb="menu"],
div[data-baseweb="popover"] ul {
    background: #ffffff !important;
}
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] li * {
    color: #0f172a !important;
    background: transparent;
}
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] li[aria-selected="true"] {
    background: #f1f5f9 !important;
}

/* Submit button */
div[data-testid="stFormSubmitButton"] button {
    background: #0f172a;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.01em;
    transition: all 0.2s ease;
}
div[data-testid="stFormSubmitButton"] button:hover {
    background: #1e293b;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.25);
    color: #ffffff;
}
div[data-testid="stFormSubmitButton"] button p { color: #ffffff !important; }

/* Result */
.gauge-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
}
.gauge {
    width: 170px;
    height: 170px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.gauge-inner {
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.gauge-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.gauge-label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.15rem;
}
.badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    border: 1px solid;
}
.result-heading {
    font-size: 1.35rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0.7rem 0 0.3rem 0;
}
.result-text {
    color: #475569;
    font-size: 0.92rem;
    line-height: 1.55;
}

/* Stat tiles */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.8rem;
    margin-top: 0.4rem;
}
.stat-tile {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.9rem 1rem;
}
.stat-label {
    color: #64748b;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}
.stat-value {
    color: #0f172a;
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 0.25rem;
}

/* Recommendations */
.reco {
    display: flex;
    gap: 0.7rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
    font-size: 0.9rem;
    line-height: 1.5;
}
.reco:last-child { border-bottom: none; }
.reco-dot {
    flex: 0 0 8px;
    height: 8px;
    border-radius: 50%;
    background: #0f172a;
    margin-top: 0.5rem;
}

.recommendation-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.footer-note {
    text-align: center;
    color: #475569;
    font-size: 0.8rem;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #e2e8f0;
}
</style>
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------


def section_header(title: str, description: str) -> None:
    st.markdown(
        f'<div class="section-title">{title}</div>'
        f'<div class="section-desc">{description}</div>',
        unsafe_allow_html=True,
    )


def stat_tile(label: str, value: str) -> str:
    return (
        '<div class="stat-tile">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div>'
        "</div>"
    )


def build_recommendations(data, risk_band):
    recommendations = []

    if risk_band == "High":
        recommendations.append(
            "Prioritize this customer for proactive retention outreach."
        )

    elif risk_band == "Moderate":
        recommendations.append(
            "Monitor this customer closely and consider a targeted retention offer."
        )

    else:
        recommendations.append("No immediate retention intervention is required.")

    if data["contract"] == "Month-to-month":
        recommendations.append(
            "Consider offering an incentive to move the customer to a longer-term contract."
        )

    if data["internet_service"] == "Fiber optic" and data["tech_support"] == "No":
        recommendations.append(
            "Consider offering Tech Support as part of a service bundle."
        )

    if data["internet_service"] != "No" and data["online_security"] == "No":
        recommendations.append(
            "Promote Online Security to strengthen the customer's service package."
        )

    if data["payment_method"] == "Electronic check":
        recommendations.append(
            "Encourage automatic payment methods to improve payment continuity."
        )

    if data["tenure_months"] < 12:
        recommendations.append(
            "Provide additional onboarding and early-lifecycle engagement."
        )

    return recommendations[:4]


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="hero">'
    '<div class="hero-eyebrow">ProdIntel</div>'
    '<div class="hero-title">Customer Intelligence</div>'
    '<div class="hero-subtitle">'
    "ML-powered customer churn analysis and business intelligence"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Customer Input Form
# --------------------------------------------------

with st.form("customer_churn_form", border=False):

    top_left, top_right = st.columns(2, gap="medium")

    with top_left:
        with st.container(border=True, key="card_account"):
            section_header(
                "Account & Billing",
                "Tenure and financial value of the customer",
            )

            a1, a2 = st.columns(2)

            with a1:
                tenure_months = st.number_input(
                    "Tenure Months",
                    min_value=0,
                    value=12,
                    step=1,
                )
                total_charges = st.number_input(
                    "Total Charges",
                    min_value=0.0,
                    value=840.0,
                    step=10.0,
                )

            with a2:
                monthly_charges = st.number_input(
                    "Monthly Charges",
                    min_value=0.0,
                    value=70.0,
                    step=1.0,
                )
                cltv = st.number_input(
                    "CLTV",
                    min_value=0.0,
                    value=5000.0,
                    step=100.0,
                )

    with top_right:
        with st.container(border=True, key="card_contract"):
            section_header(
                "Contract & Payment",
                "Commitment level and billing preferences",
            )

            c1, c2 = st.columns(2)

            with c1:
                contract = st.selectbox(
                    "Contract",
                    ["Month-to-month", "One year", "Two year"],
                )
                paperless_billing = st.selectbox(
                    "Paperless Billing",
                    ["Yes", "No"],
                )

            with c2:
                payment_method = st.selectbox(
                    "Payment Method",
                    [
                        "Electronic check",
                        "Mailed check",
                        "Bank transfer (automatic)",
                        "Credit card (automatic)",
                    ],
                )

    with st.container(border=True, key="card_demographics"):
        section_header(
            "Demographics",
            "Basic customer profile",
        )

        d1, d2, d3, d4 = st.columns(4)

        with d1:
            gender = st.selectbox("Gender", ["Male", "Female"])
        with d2:
            senior_citizen = st.selectbox("Senior Citizen", [0, 1])
        with d3:
            partner = st.selectbox("Partner", ["Yes", "No"])
        with d4:
            dependents = st.selectbox("Dependents", ["Yes", "No"])

    with st.container(border=True, key="card_services"):
        section_header(
            "Services",
            "Phone and internet services subscribed by the customer",
        )

        s1, s2, s3 = st.columns(3)

        with s1:
            phone_service = st.selectbox("Phone Service", ["Yes", "No"])
            multiple_lines = st.selectbox(
                "Multiple Lines",
                ["Yes", "No", "No phone service"],
            )
            internet_service = st.selectbox(
                "Internet Service",
                ["DSL", "Fiber optic", "No"],
            )

        with s2:
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

        with s3:
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
    explanation = result.get("explanation", {})
    higher_risk = explanation.get("higher_risk", [])
    lower_risk = explanation.get("lower_risk", [])

    probability_clamped = min(max(probability, 0.0), 1.0)
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

    style = RISK_STYLES[risk_band]

    if prediction == "Yes":
        prediction_heading = "Likely to churn"
        prediction_text = (
            "The model predicts that this customer belongs to the churn class. "
            "The customer may require additional retention analysis or engagement."
        )
    else:
        prediction_heading = "Likely to stay"
        prediction_text = (
            "The model predicts that this customer belongs to the non-churn class."
        )

    if risk_band == "High":
        risk_summary = "This customer shows a high likelihood of churn and should receive proactive retention attention."
    elif risk_band == "Moderate":
        risk_summary = "This customer shows moderate churn risk and may benefit from targeted retention actions."
    else:
        risk_summary = "This customer currently shows low churn risk and does not require immediate intervention."

    st.markdown(
        f"""
    <div class="recommendation-card">
        <strong>Business Risk Summary</strong>
        <div style="margin-top:8px;">
            {risk_summary}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    gauge_html = (
        '<div class="gauge-wrap">'
        f'<div class="gauge" style="background: conic-gradient('
        f'{style["color"]} {probability_clamped * 360:.1f}deg, #e2e8f0 0deg);">'
        '<div class="gauge-inner">'
        f'<div class="gauge-value">{probability_percent:.1f}%</div>'
        '<div class="gauge-label">Churn Risk</div>'
        "</div></div></div>"
    )

    summary_html = (
        f'<span class="badge" style="color:{style["color"]};'
        f'background:{style["bg"]};border-color:{style["border"]};">'
        f"{risk_band} Risk</span>"
        f'<div class="result-heading">{prediction_heading}</div>'
        f'<div class="result-text">{risk_message}<br>{prediction_text}</div>'
    )

    with st.container(border=True, key="card_result"):
        res_left, res_right = st.columns(
            [1, 2], gap="large", vertical_alignment="center"
        )

        with res_left:
            st.markdown(gauge_html, unsafe_allow_html=True)

        with res_right:
            st.markdown(summary_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # Why this prediction? (Indented correctly inside `if submitted:`)
    # -----------------------------

    section_header(
        "Why this prediction?", "Key factors influencing the model's churn assessment."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Factors increasing churn risk")

        if higher_risk:
            for item in higher_risk:
                feature = item["feature"]
                impact = item["impact"]

                feature = feature.replace("_", " — ")

                st.markdown(
                    f"""
                    <div class="recommendation-card">
                        <strong>{feature}</strong>
                        <div style="margin-top:6px;">
                            Contribution to higher churn risk: <b>{impact:.4f}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No strong risk-increasing factors identified.")

    with col2:
        st.markdown("### Factors reducing churn risk")

        if lower_risk:
            for item in lower_risk:
                feature = item["feature"]
                impact = item["impact"]

                feature = feature.replace("_", " — ")

                st.markdown(
                    f"""
                    <div class="recommendation-card">
                        <strong>{feature}</strong>
                        <div style="margin-top:6px;">
                            Contribution to lower churn risk: <b>{abs(impact):.4f}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No strong risk-reducing factors identified.")

    # --------------------------------------------------
    # Snapshot + Recommendations
    # --------------------------------------------------

    snap_col, reco_col = st.columns([3, 2], gap="medium")

    with snap_col:
        with st.container(border=True, key="card_snapshot"):
            section_header(
                "Customer Snapshot",
                "Key indicators submitted for this prediction",
            )

            tiles = "".join(
                [
                    stat_tile("Tenure", f"{tenure_months} months"),
                    stat_tile("Monthly Charges", f"{monthly_charges:,.2f}"),
                    stat_tile("Total Charges", f"{total_charges:,.2f}"),
                    stat_tile("Contract", contract),
                    stat_tile("Internet Service", internet_service),
                    stat_tile("Payment Method", payment_method),
                ]
            )

            st.markdown(
                f'<div class="stat-grid">{tiles}</div>',
                unsafe_allow_html=True,
            )

    with reco_col:
        with st.container(border=True, key="card_reco"):
            section_header(
                "Retention Considerations",
                "Suggested actions based on the customer profile",
            )

            recos = "".join(
                f'<div class="reco"><div class="reco-dot"></div><div>{tip}</div></div>'
                for tip in build_recommendations(customer_data, risk_band)
            )

            st.markdown(recos, unsafe_allow_html=True)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    '<div class="footer-note">'
    "ProdIntel Customer Intelligence · ML-powered customer churn prediction"
    "</div>",
    unsafe_allow_html=True,
)
