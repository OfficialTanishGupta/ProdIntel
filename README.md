# ProdIntel — Production Intelligence Platform

ProdIntel is a machine-learning-powered business intelligence platform that helps organizations analyze operational and customer data, predict risks, and make better decisions.

The current release delivers a complete **Customer Churn Intelligence** module: a FastAPI prediction backend, a Streamlit customer dashboard with SHAP explanations, and a **Portfolio Intelligence** page for batch analysis of up to 1,000 customers.

## Live Demo

| Component                         | Link                                                 |
| --------------------------------- | ---------------------------------------------------- |
| Customer Intelligence (Streamlit) | https://prodintel-customer-intelligence.onrender.com |
| Prediction API (FastAPI)          | https://prodintel-ltus.onrender.com                  |
| API Docs (Swagger)                | https://prodintel-ltus.onrender.com/docs             |

## Features

### Customer Intelligence

- Single-customer churn prediction with account, billing, contract, demographic, and service inputs
- Churn probability and risk classification (Low / Moderate / High)
- Risk visualization
- Business-oriented retention recommendations
- SHAP-based explanation of each prediction

### Portfolio Intelligence

- Downloadable CSV input template
- Multiple CSV file uploads
- Validation: required columns, empty data, maximum rows, and missing/blank/duplicate customer IDs
- Customer data preview before analysis
- Batch prediction via the FastAPI `/predict-batch` endpoint
- Portfolio risk overview: total, high-, moderate-, and low-risk customers
- Business impact metrics: predicted churn rate, monthly charges of high-risk customers, average churn probability
- Segmentation charts: contract type, tenure, internet service
- Risk distribution chart
- Retention priority table with Priority Score and Suggested Next Step
- Customer-specific retention recommendations
- Retention strategy insights (month-to-month customers, short-tenure customers, customers without technical support)
- Downloads: high-risk customer report, prediction results, retention action plan, executive portfolio summary
- Portfolio risk trend history with chart, data table, and CSV download
- Results stored in `st.session_state`, so downloads and reruns do not lose data or trigger duplicate predictions

## Risk Definitions

| Band     | Churn probability |
| -------- | ----------------- |
| Low      | below 30%         |
| Moderate | 30% to below 60%  |
| High     | 60% or above      |

- **Predicted churn rate** counts customers with churn probability of at least 50%. This is intentionally different from the risk bands.
- **Monthly charges of high-risk customers** is an exposure indicator, not confirmed revenue loss.

## Model

- Algorithm: Random Forest classification pipeline (numerical and categorical preprocessing)
- Dataset: Telco Customer Churn (7,043 records)
- Artifact: `models/customer_churn_model.joblib`
- Notebook: `notebooks/11_customer_churn_final_model.ipynb`

| Metric    | Value   |
| --------- | ------- |
| Accuracy  | ~80.34% |
| ROC-AUC   | ~85.16% |
| F1 score  | ~59.68% |
| Precision | ~65.50% |
| Recall    | ~54.81% |

> These are recorded evaluation results on held-out data, not a guarantee of production performance.

## Architecture

```
┌────────────────────┐   HTTP (requests)   ┌────────────────────┐
│  Streamlit UI      │ ──────────────────► │  FastAPI backend   │
│  - Customer page   │                     │  /  /health        │
│  - Portfolio page  │ ◄────────────────── │  /predict          │
└────────────────────┘   JSON predictions  │  /predict-batch    │
                                           └─────────┬──────────┘
                                                     │ joblib
                                                     ▼
                                           ┌────────────────────┐
                                           │ Churn model (RF)   │
                                           └────────────────────┘
```

## API Endpoints

| Method | Endpoint         | Description                              |
| ------ | ---------------- | ---------------------------------------- |
| GET    | `/`              | Root endpoint                            |
| GET    | `/health`        | Health check                             |
| POST   | `/predict`       | Single customer churn prediction         |
| POST   | `/predict-batch` | Batch predictions for multiple customers |

Responses include the churn prediction, churn probability, and risk classification.

## Tech Stack

Python · Pandas · NumPy · Scikit-learn · Matplotlib · Seaborn · Streamlit · FastAPI · Joblib · SHAP · Requests · Git/GitHub · Render

## Project Structure

```
ProdIntel/
├── app/
│   ├── main.py                          # FastAPI backend
│   ├── schemas.py                       # Request/response schemas
│   ├── customer_ui.py                   # Customer Intelligence frontend
│   ├── explainability.py                # SHAP explanations
│   └── pages/
│       └── portfolio_intelligence.py    # Portfolio Intelligence page
├── models/
│   └── customer_churn_model.joblib
├── notebooks/
│   └── 11_customer_churn_final_model.ipynb
├── data/
│   └── portfolio_history/
│       └── portfolio_trend_history.csv
├── requirements.txt
└── README.md
```

## Local Setup

```powershell
# 1. Clone
git clone https://github.com/OfficialTanishGupta/ProdIntel.git
cd ProdIntel

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the backend (terminal 1)
uvicorn app.main:app --reload

# 5. Run the frontend (terminal 2)
streamlit run app/customer_ui.py
```

By default the frontend should point to the deployed API. To use a local backend, update the API base URL in the frontend to `http://127.0.0.1:8000`.

## Using Portfolio Intelligence

1. Open **Portfolio Intelligence** from the Streamlit sidebar.
2. Download the CSV template and fill in customer data (up to 1,000 customers per batch).
3. Upload one or more CSV files and review the data preview.
4. Click **Analyze Customer Portfolio**.
5. Review risk metrics, segmentation, retention priorities, and the executive summary.
6. Download the reports you need.
7. Each successful analysis records one snapshot in the trend history.

## Deployment

Both services are deployed on Render:

- Backend: FastAPI web service
- Frontend: Streamlit web service

## Known Limitations

- **Trend history storage:** history is saved to a local CSV (`data/portfolio_history/portfolio_trend_history.csv`). Render's local filesystem may not persist across restarts or deployments, so persistent storage (e.g., a database) is needed for durable history.
- Recommendations and predicted churn outcomes are decision-support signals, not guarantees.
- Model metrics are from a single public dataset and may differ on real business data.

## Roadmap

- **Phase A — Stabilize:** regression test multi-file uploads, all downloads, and trend recording; confirm no duplicate snapshots
- **Phase B — Historical analytics:** risk-count changes between analyses, latest analysis timestamp, trend comparisons, persistent storage
- **Phase C — Retention intelligence:** richer priority scoring, attribute-specific recommendations, filters (risk band, contract, tenure, customer ID), better exports
- **Phase D — Professionalize:** error handling, API status visibility, sample datasets, automated tests, security and logging review, screenshots
- **Phase E — Expand:** employee attrition, predictive maintenance, and production-quality modules, each with independent data and modeling logic

## Screenshots

_Add screenshots here: customer prediction, SHAP explanation, portfolio overview, retention priority table, trend history._

## Author

**Tanish Gupta** — [GitHub: OfficialTanishGupta](https://github.com/OfficialTanishGupta)
