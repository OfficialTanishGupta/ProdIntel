
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg

CSV_PATH = Path("data/portfolio_history/portfolio_trend_history.csv")

COLUMNS = [
    "analysis_timestamp",
    "total_customers",
    "high_risk",
    "moderate_risk",
    "low_risk",
    "average_churn_probability_pct",
]


def main():
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is not configured.")

    df = pd.read_csv(CSV_PATH)

    if list(df.columns) != COLUMNS:
        raise ValueError("CSV columns do not match the expected schema.")

    rows = []

    for record in df.to_dict(orient="records"):
        timestamp = datetime.fromisoformat(
            str(record["analysis_timestamp"])
        )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=ZoneInfo("Asia/Kolkata")
            )

        rows.append((
            timestamp,
            int(record["total_customers"]),
            int(record["high_risk"]),
            int(record["moderate_risk"]),
            int(record["low_risk"]),
            float(record["average_churn_probability_pct"]),
        ))

    inserted = 0

    with psycopg.connect(
        os.environ["DATABASE_URL"],
        connect_timeout=10,
    ) as conn:
        for row in rows:
            result = conn.execute(
                """
                INSERT INTO portfolio_history (
                    analysis_timestamp,
                    total_customers,
                    high_risk,
                    moderate_risk,
                    low_risk,
                    average_churn_probability_pct
                )
                SELECT %s, %s, %s, %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM portfolio_history
                    WHERE analysis_timestamp = %s
                      AND total_customers = %s
                      AND high_risk = %s
                      AND moderate_risk = %s
                      AND low_risk = %s
                      AND average_churn_probability_pct = %s
                )
                """,
                row + row,
            )
            inserted += result.rowcount

        total = conn.execute(
            "SELECT COUNT(*) FROM portfolio_history"
        ).fetchone()[0]

    print("CSV records:", len(rows))
    print("New records imported:", inserted)
    print("Total records in Neon:", total)


if __name__ == "__main__":
    main()
