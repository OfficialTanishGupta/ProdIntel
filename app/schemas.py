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
