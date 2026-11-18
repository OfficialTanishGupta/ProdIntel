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
    + "/predict-attrition"
)

st.set_page_config(
    page_title="ProdIntel - Employee Intelligence",
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

    .stApp {
        background: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 16px;
        background: linear-gradient(
            135deg, #0f172a 0%, #1e293b 60%, #334155 100%
        );
        margin-bottom: 1.6rem;
    }

    .hero-eyebrow {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .hero-title {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.4rem 0;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
    }

    .section-title {
        color: #0f172a;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }

    .section-desc {
        color: #64748b;
        font-size: 0.82rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }

    label, label p, div[data-testid="stWidgetLabel"] p {
        color: #334155 !important;
        font-size: 0.83rem !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background: #ffffff;
        border-color: #cbd5e1;
        border-radius: 9px;
    }

    div[data-baseweb="select"] *,
    div[data-baseweb="input"] input,
    .stNumberInput input {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: #0f172a;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #1e293b;
        color: #ffffff;
    }

    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .probability {
        font-size: 2.4rem;
        font-weight: 700;
        color: #0f172a;
    }

    .result-label {
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }

    .footer-note {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 2rem;
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


def section_header(title, description):
    st.markdown(
        f'<div class="section-title">{title}</div>'
        f'<div class="section-desc">{description}</div>',
        unsafe_allow_html=True,
    )


def number_field(label, minimum, maximum=None, default=0):
    return st.number_input(
        label,
        min_value=minimum,
        max_value=maximum,
        value=default,
        step=1,
    )


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">ProdIntel</div>
        <div class="hero-title">Employee Intelligence</div>
        <div class="hero-subtitle">
            ML-powered employee attrition prediction and workforce intelligence
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Employee Input Form
# --------------------------------------------------

with st.form("employee_attrition_form", border=False):

    # Employee profile
    with st.container(border=True):
        section_header(
            "Employee Profile",
            "Basic demographic and employment information",
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            age = number_field("Age", 18, 100, 35)
            gender = st.selectbox("Gender", ["Male", "Female"])

        with c2:
            marital_status = st.selectbox(
                "Marital Status",
                ["Married", "Single", "Divorced"],
            )
            distance_from_home = number_field("Distance From Home", 0, default=7)

        with c3:
            education = number_field("Education (1-5)", 1, 5, 3)
            education_field = st.selectbox(
                "Education Field",
                [
                    "Life Sciences",
                    "Medical",
                    "Marketing",
                    "Technical Degree",
                    "Human Resources",
                    "Other",
                ],
            )

        with c4:
            business_travel = st.selectbox(
                "Business Travel",
                [
                    "Travel_Rarely",
                    "Travel_Frequently",
                    "Non-Travel",
                ],
            )
            num_companies_worked = number_field("Previous Companies", 0, default=2)

    # Job details
    with st.container(border=True):
        section_header(
            "Job & Department",
            "Current organizational role and work experience",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            department = st.selectbox(
                "Department",
                [
                    "Research & Development",
                    "Sales",
                    "Human Resources",
                ],
            )
            job_role = st.selectbox(
                "Job Role",
                [
                    "Research Scientist",
                    "Laboratory Technician",
                    "Sales Executive",
                    "Sales Representative",
                    "Healthcare Representative",
                    "Manufacturing Director",
                    "Manager",
                    "Research Director",
                    "Human Resources",
                ],
            )

        with c2:
            job_level = number_field("Job Level (1-5)", 1, 5, 2)
            total_working_years = number_field("Total Working Years", 0, default=10)

        with c3:
            years_at_company = number_field("Years At Company", 0, default=5)
            years_in_current_role = number_field("Years In Current Role", 0, default=3)

        c1, c2, c3 = st.columns(3)

        with c1:
            years_since_last_promotion = number_field(
                "Years Since Last Promotion", 0, default=1
            )

        with c2:
            years_with_curr_manager = number_field(
                "Years With Current Manager", 0, default=3
            )

        with c3:
            training_times_last_year = number_field(
                "Training Times Last Year", 0, default=3
            )

    # Satisfaction and work environment
    with st.container(border=True):
        section_header(
            "Satisfaction & Work Environment",
            "Employee engagement, satisfaction and work-life balance",
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            environment_satisfaction = number_field(
                "Environment Satisfaction (1-4)", 1, 4, 3
            )
            job_satisfaction = number_field("Job Satisfaction (1-4)", 1, 4, 3)

        with c2:
            job_involvement = number_field("Job Involvement (1-4)", 1, 4, 3)
            relationship_satisfaction = number_field(
                "Relationship Satisfaction (1-4)", 1, 4, 3
            )

        with c3:
            work_life_balance = number_field("Work-Life Balance (1-4)", 1, 4, 3)
            overtime = st.selectbox("OverTime", ["No", "Yes"])

        with c4:
            stock_option_level = number_field("Stock Option Level (0-3)", 0, 3, 1)

    # Compensation and performance
    with st.container(border=True):
        section_header(
            "Compensation & Performance",
            "Salary, working rates and performance indicators",
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            daily_rate = number_field("Daily Rate", 0, default=800)
            hourly_rate = number_field("Hourly Rate", 0, default=65)

        with c2:
            monthly_income = number_field("Monthly Income", 0, default=5000)
            monthly_rate = number_field("Monthly Rate", 0, default=15000)

        with c3:
            percent_salary_hike = number_field("Percent Salary Hike", 0, 100, 15)
            performance_rating = number_field("Performance Rating (1-4)", 1, 4, 3)

    submitted = st.form_submit_button(
        "Predict Employee Attrition",
        use_container_width=True,
    )


# --------------------------------------------------
# Prediction
# --------------------------------------------------

if submitted:

    employee_data = {
        "age": age,
        "business_travel": business_travel,
        "daily_rate": daily_rate,
        "department": department,
        "distance_from_home": distance_from_home,
        "education": education,
        "education_field": education_field,
        "environment_satisfaction": environment_satisfaction,
        "gender": gender,
        "hourly_rate": hourly_rate,
        "job_involvement": job_involvement,
        "job_level": job_level,
        "job_role": job_role,
        "job_satisfaction": job_satisfaction,
        "marital_status": marital_status,
        "monthly_income": monthly_income,
        "monthly_rate": monthly_rate,
        "num_companies_worked": num_companies_worked,
        "overtime": overtime,
        "percent_salary_hike": percent_salary_hike,
        "performance_rating": performance_rating,
        "relationship_satisfaction": relationship_satisfaction,
        "stock_option_level": stock_option_level,
        "total_working_years": total_working_years,
        "training_times_last_year": training_times_last_year,
        "work_life_balance": work_life_balance,
        "years_at_company": years_at_company,
        "years_in_current_role": years_in_current_role,
        "years_since_last_promotion": years_since_last_promotion,
        "years_with_curr_manager": years_with_curr_manager,
    }

    with st.spinner("Analyzing employee information..."):

        try:
            response = requests.post(
                API_URL,
                json=employee_data,
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

        except requests.exceptions.ConnectionError:
            st.error("Employee Intelligence API is unavailable.")
            st.info("Verify that the ProdIntel API service is running.")

        except requests.exceptions.Timeout:
            st.error("The prediction request timed out.")

        except requests.exceptions.HTTPError:
            st.error("The API rejected the prediction request.")
            st.code(response.text)

        except requests.exceptions.RequestException as error:
            st.error("An unexpected API error occurred.")
            st.code(str(error))

        else:
            prediction = result["prediction"]
            probability = float(result["attrition_probability"])
            threshold = float(result["threshold"])

            probability_percent = probability * 100
            threshold_percent = threshold * 100

            if prediction == "Yes":
                heading = "Likely to Leave"
                color = "#b91c1c"
                message = (
                    "The model predicts that this employee belongs "
                    "to the attrition class."
                )
            else:
                heading = "Likely to Stay"
                color = "#15803d"
                message = (
                    "The model predicts that this employee belongs "
                    "to the non-attrition class."
                )

            st.markdown("---")
            st.subheader("Employee Attrition Prediction")

            with st.container(border=True):
                left, right = st.columns(
                    [1, 2],
                    vertical_alignment="center",
                )

                with left:
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div class="probability"
                                 style="color:{color};">
                                {probability_percent:.2f}%
                            </div>
                            <div style="color:#64748b;">
                                Attrition Probability
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with right:
                    st.markdown(
                        f"""
                        <div class="result-label"
                             style="color:{color};">
                            {heading}
                        </div>
                        <p>{message}</p>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.progress(min(max(probability, 0.0), 1.0))

                    st.caption(f"Model decision threshold: {threshold_percent:.0f}%")

                st.divider()

                st.markdown("**Prediction Details**")

                c1, c2, c3 = st.columns(3)

                c1.metric("Prediction", prediction)
                c2.metric(
                    "Attrition Probability",
                    f"{probability_percent:.2f}%",
                )
                c3.metric(
                    "Decision Threshold",
                    f"{threshold_percent:.0f}%",
                )

            st.caption(
                "This prediction is a model-based estimate, "
                "not a definitive assessment of an employee."
            )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    """
    <div class="footer-note">
        ProdIntel Employee Intelligence ·
        ML-powered employee attrition prediction
    </div>
    """,
    unsafe_allow_html=True,
)
