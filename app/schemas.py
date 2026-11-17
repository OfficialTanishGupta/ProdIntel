from typing import Literal

from pydantic import BaseModel, Field


class CustomerChurnRequest(BaseModel):

    customer_id: str | None = None

    tenure_months: int = Field(ge=0)
    monthly_charges: float = Field(ge=0)
    total_charges: float = Field(ge=0)
    cltv: float = Field(ge=0)

    gender: Literal["Male", "Female"]

    senior_citizen: Literal[0, 1]

    partner: Literal["Yes", "No"]
    dependents: Literal["Yes", "No"]

    phone_service: Literal["Yes", "No"]

    multiple_lines: Literal["Yes", "No", "No phone service"]

    internet_service: Literal["DSL", "Fiber optic", "No"]

    online_security: Literal["Yes", "No", "No internet service"]

    online_backup: Literal["Yes", "No", "No internet service"]

    device_protection: Literal["Yes", "No", "No internet service"]

    tech_support: Literal["Yes", "No", "No internet service"]

    streaming_tv: Literal["Yes", "No", "No internet service"]

    streaming_movies: Literal["Yes", "No", "No internet service"]

    contract: Literal["Month-to-month", "One year", "Two year"]

    paperless_billing: Literal["Yes", "No"]

    payment_method: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]


class EmployeeAttritionRequest(BaseModel):
    age: int = Field(ge=18, le=100)
    business_travel: Literal["Non-Travel", "Travel_Frequently", "Travel_Rarely"]
    daily_rate: int = Field(ge=0)
    department: Literal["Human Resources", "Research & Development", "Sales"]
    distance_from_home: int = Field(ge=0)
    education: int = Field(ge=1, le=5)
    education_field: Literal[
        "Human Resources",
        "Life Sciences",
        "Marketing",
        "Medical",
        "Other",
        "Technical Degree",
    ]
    environment_satisfaction: int = Field(ge=1, le=4)
    gender: Literal["Female", "Male"]
    hourly_rate: int = Field(ge=0)
    job_involvement: int = Field(ge=1, le=4)
    job_level: int = Field(ge=1, le=5)
    job_role: Literal[
        "Healthcare Representative",
        "Human Resources",
        "Laboratory Technician",
        "Manager",
        "Manufacturing Director",
        "Research Director",
        "Research Scientist",
        "Sales Executive",
        "Sales Representative",
    ]
    job_satisfaction: int = Field(ge=1, le=4)
    marital_status: Literal["Divorced", "Married", "Single"]
    monthly_income: int = Field(ge=0)
    monthly_rate: int = Field(ge=0)
    num_companies_worked: int = Field(ge=0)
    overtime: Literal["No", "Yes"]
    percent_salary_hike: int = Field(ge=0, le=100)
    performance_rating: int = Field(ge=1, le=4)
    relationship_satisfaction: int = Field(ge=1, le=4)
    stock_option_level: int = Field(ge=0, le=3)
    total_working_years: int = Field(ge=0)
    training_times_last_year: int = Field(ge=0)
    work_life_balance: int = Field(ge=1, le=4)
    years_at_company: int = Field(ge=0)
    years_in_current_role: int = Field(ge=0)
    years_since_last_promotion: int = Field(ge=0)
    years_with_curr_manager: int = Field(ge=0)
