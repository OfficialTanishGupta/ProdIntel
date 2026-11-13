# ProdIntel — Production Intelligence Platform

[![ProdIntel CI](https://github.com/OfficialTanishGupta/ProdIntel/actions/workflows/tests.yml/badge.svg)](https://github.com/OfficialTanishGupta/ProdIntel/actions/workflows/tests.yml)

ProdIntel is a machine-learning-powered business intelligence platform that helps organizations analyze operational and customer data, predict risks, and make better decisions.

The current release delivers a complete **Customer Churn Intelligence** module: a FastAPI prediction backend, a Streamlit customer dashboard with SHAP explanations, a **Portfolio Intelligence** page for batch analysis of up to 1,000 customers, PostgreSQL-backed portfolio history, an automated regression test suite, and GitHub Actions CI.

## Current Status

| Area                                   | Status                          |
| -------------------------------------- | ------------------------------- |
| Core ML application                    | Complete                        |
| Deployment (Render)                    | Complete                        |
| PostgreSQL integration                 | Complete                        |
| Automated regression tests (21 passed) | Complete                        |
| GitHub Actions CI                      | Complete                        |
| **Code Quality & Reliability Review**  | **In progress (current phase)** |

Latest verified checkpoint: 21 tests passing locally, CI run successful on `main`.

## Current Phase — Code Quality & Reliability Review

With the core application, deployment, database persistence, tests, and CI in place, the project is now focused on reliability. Work proceeds one step at a time, and every change is tested before moving forward.

| Step | Task                                             | Status  |
| ---- | ------------------------------------------------ | ------- |
| 1    | Investigate and understand the 4 pytest warnings | Next    |
| 2    | Review FastAPI endpoints and error handling      | Pending |
| 3    | Review PostgreSQL reliability and persistence    | Pending |
| 4    | Review frontend/backend integration              | Pending |
| 5    | Identify missing regression tests                | Pending |
| 6    | Implement and test improvements                  | Pending |

**Immediate next task:** run `pytest -v -W default` from the project directory and identify all four warnings before changing any code.

**Ground rules for this phase**

- Existing working features must not break.
- Production database records are not modified without explicit approval.
- Commit and push after each completed milestone.
- ProdIntel remains a separate project from the AutoML Platform.

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
- **Persistent history:** snapshots are stored in PostgreSQL, with duplicate snapshot detection
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
                                           │  portfolio history │
                                           └───────┬─────┬──────┘
                                         joblib    │     │  Psycopg 3
                                                   ▼     ▼
                                    ┌──────────────────┐ ┌──────────────────┐
                                    │ Churn model (RF) │ │ PostgreSQL       │
                                    └──────────────────┘ │ portfolio_history│
                                                         └──────────────────┘
```

## API Endpoints

| Method     | Endpoint                    | Description                                 |
| ---------- | --------------------------- | ------------------------------------------- |
| GET        | `/`                         | Root endpoint                               |
| GET        | `/health`                   | Health check                                |
| POST       | `/predict`                  | Single customer churn prediction            |
| POST       | `/predict-batch`            | Batch predictions for multiple customers    |
| GET / POST | Portfolio history endpoints | Read and record portfolio history snapshots |

Responses include the churn prediction, churn probability, and risk classification. See the Swagger docs for exact request/response schemas.

## Tech Stack

Python · Pandas · NumPy · Scikit-learn · Matplotlib · Seaborn · Streamlit · FastAPI · PostgreSQL · Psycopg 3 · Joblib · SHAP · Requests · Pytest · GitHub Actions · Git/GitHub · Render

## Project Structure

```
ProdIntel/
├── .github/
│   └── workflows/
│       └── tests.yml                    # GitHub Actions CI
├── app/
│   ├── main.py                          # FastAPI backend
│   ├── schemas.py                       # Request/response schemas
│   ├── database.py                      # PostgreSQL connection and history storage
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
│       └── portfolio_trend_history.csv  # Legacy history (migrated to PostgreSQL)
├── tests/
│   ├── test_database.py                 # Mocked database tests
│   └── ...                              # API and batch prediction regression tests
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

## Testing

```powershell
# Run the full test suite
pytest -v

# Show all warnings (used in the current reliability phase)
pytest -v -W default
```

- The suite covers API endpoints, batch predictions, and database logic.
- Database tests are mocked and do not require production database access.
- Latest local result: `21 passed, 4 warnings`.

## Continuous Integration

GitHub Actions (`.github/workflows/tests.yml`) runs the test suite automatically:

- On every push and pull request to `main`
- On demand via manual workflow dispatch
- Runner `ubuntu-24.04`, Python `3.12`, `actions/checkout@v7`, `actions/setup-python@v7`

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
- Database: PostgreSQL for portfolio history

## Known Limitations

- Recommendations and predicted churn outcomes are decision-support signals, not guarantees.
- Model metrics are from a single public dataset and may differ on real business data.
- The test suite currently reports 4 warnings that are being investigated in the current phase.

## Roadmap

- **Phase A — Stabilize:** ✅ regression tests for API, batch prediction, and database logic; CI in place
- **Phase B — Historical analytics:** ✅ persistent PostgreSQL storage and duplicate snapshot detection; 🔜 risk-count changes between analyses, latest analysis timestamp, trend comparisons
- **Phase C — Retention intelligence:** richer priority scoring, attribute-specific recommendations, filters (risk band, contract, tenure, customer ID), better exports
- **Phase D — Professionalize (in progress):** code quality and reliability review (pytest warnings, error handling, database reliability, frontend/backend integration, missing tests), API status visibility, sample datasets, security and logging review, screenshots
- **Phase E — Expand:** employee attrition, predictive maintenance, and production-quality modules, each with independent data and modeling logic

## Screenshots

_Add screenshots here: customer prediction, SHAP explanation, portfolio overview, retention priority table, trend history._

## Author

**Tanish Gupta** — [GitHub: OfficialTanishGupta](https://github.com/OfficialTanishGupta)

---

## Employee Attrition Intelligence — Progress Summary

We've started adding **Employee Attrition Intelligence** as a separate use case within ProdIntel, alongside the existing Customer Churn Intelligence module. The existing customer churn implementation remains unchanged.

### 1. Dataset and Exploration

**Status: Completed**

- Added the IBM HR Analytics Employee Attrition dataset: `data/raw/employee_attrition.csv`
- Dataset contains 1,470 employee records and 35 columns.
- Checked missing values, duplicate records and target distribution.
- Removed three constant columns and the employee ID during preprocessing.
- Identified important attrition patterns:
  - Overtime employees have higher attrition.
  - Sales Representatives have particularly high attrition.
  - Frequent business travel is associated with higher attrition.
  - Single employees show higher attrition in this dataset.
  - Younger employees and employees with shorter company tenure show higher attrition trends.

Notebook: `notebooks/01_employee_attrition_data_exploration.ipynb`

### 2. Data Preprocessing

**Status: Completed**

Created: `notebooks/02_employee_attrition_preprocessing.ipynb`

Work completed:

- Removed irrelevant and constant columns.
- Converted Attrition target into binary values:
  - No = 0
  - Yes = 1
- Separated numerical and categorical features.
- Applied StandardScaler to numerical features.
- Applied OneHotEncoder to categorical features.
- Used stratified data splitting.

Saved cleaned dataset: `data/processed/employee_attrition_cleaned.csv`

### 3. Model Training and Comparison

**Status: Completed**

Created: `notebooks/03_employee_attrition_model_training.ipynb`

Initially trained and compared four machine learning algorithms:

1. Logistic Regression
2. Decision Tree
3. Random Forest
4. Gradient Boosting

Used accuracy, precision, recall, F1-score and ROC-AUC to evaluate performance.

Our validation results currently favor Logistic Regression.

### 4. Improved Validation Workflow

**Status: Completed**

We improved the original training workflow to avoid selecting a model threshold using the final test data.

Current split:

| Dataset    | Records | Purpose                           |
| ---------- | ------- | --------------------------------- |
| Training   | 882     | Train models                      |
| Validation | 294     | Compare models and tune threshold |
| Testing    | 294     | Final evaluation                  |

Preprocessing produces 51 encoded features.

The models now use a pipeline that fits preprocessing only on training data.

### 5. Current Best Model

**Leading candidate: Logistic Regression**

| Metric    | Validation result |
| --------- | ----------------- |
| Accuracy  | 74.83%            |
| Precision | 35.79%            |
| Recall    | 72.34%            |
| F1-score  | 47.89%            |
| ROC-AUC   | 81.75%            |

This is our current leading candidate, not yet the finalized production model.

### 6. What Remains to Be Done

Here is our roadmap from this point:

1. **Decision threshold tuning**
   Review the precision-recall graph and choose an appropriate threshold using validation data.
2. **Final model evaluation**
   Evaluate Logistic Regression on the untouched test set using the selected threshold.
3. **Model explainability**
   Identify important employee attrition factors using feature importance and SHAP where appropriate.
4. **Model saving**
   Save the trained preprocessing and prediction pipeline as a Joblib model.
5. **FastAPI integration**
   Add employee attrition prediction endpoints without disturbing customer churn endpoints.
6. **Streamlit dashboard**
   Build a separate Employee Attrition Intelligence dashboard.
7. **Testing and deployment**
   Add API tests, dashboard checks and database integration if needed, then deploy through Render.

### 7. Current Project Structure

```
ProdIntel/
│
├── app/
│   ├── main.py
│   ├── customer_ui.py
│   ├── database.py
│   └── pages/
│
├── data/
│   ├── raw/
│   │   ├── telco_customer_churn.csv
│   │   └── employee_attrition.csv
│   └── processed/
│       ├── telco_customer_churn_cleaned.csv
│       └── employee_attrition_cleaned.csv
│
├── models/
│
├── notebooks/
│   ├── 01_employee_attrition_data_exploration.ipynb
│   ├── 02_employee_attrition_preprocessing.ipynb
│   └── 03_employee_attrition_model_training.ipynb
│
```
