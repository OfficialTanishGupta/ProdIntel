from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

HISTORY_FILE = BASE_DIR / "data" / "portfolio_history" / "portfolio_trend_history.csv"

HISTORY_COLUMNS = [
    "analysis_timestamp",
    "total_customers",
    "high_risk",
    "moderate_risk",
    "low_risk",
    "average_churn_probability_pct",
]


def load_portfolio_history(limit: int = 500):
    """Load portfolio snapshots from local CSV storage."""
    if not HISTORY_FILE.exists():
        return []

    history_df = pd.read_csv(HISTORY_FILE)

    if history_df.empty:
        return []

    history_df = history_df[HISTORY_COLUMNS]
    history_df = history_df.tail(limit)

    return history_df.to_dict(orient="records")


def save_portfolio_snapshot(snapshot):
    """Save a portfolio snapshot to local CSV storage."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = snapshot.analysis_timestamp.isoformat()

    record = {
        "analysis_timestamp": timestamp,
        "total_customers": snapshot.total_customers,
        "high_risk": snapshot.high_risk,
        "moderate_risk": snapshot.moderate_risk,
        "low_risk": snapshot.low_risk,
        "average_churn_probability_pct": (snapshot.average_churn_probability_pct),
    }

    if HISTORY_FILE.exists():
        history_df = pd.read_csv(HISTORY_FILE)
    else:
        history_df = pd.DataFrame(columns=HISTORY_COLUMNS)

    if not history_df.empty:
        duplicate = (
            (history_df["analysis_timestamp"].astype(str) == timestamp)
            & (history_df["total_customers"] == record["total_customers"])
            & (history_df["high_risk"] == record["high_risk"])
            & (history_df["moderate_risk"] == record["moderate_risk"])
            & (history_df["low_risk"] == record["low_risk"])
            & (
                history_df["average_churn_probability_pct"]
                == record["average_churn_probability_pct"]
            )
        ).any()

        if duplicate:
            return {
                "saved": False,
                "message": "Portfolio snapshot already exists.",
            }

    history_df = pd.concat(
        [history_df, pd.DataFrame([record])],
        ignore_index=True,
    )

    history_df.to_csv(HISTORY_FILE, index=False)

    return {
        "saved": True,
        "message": "Portfolio snapshot saved successfully.",
    }
