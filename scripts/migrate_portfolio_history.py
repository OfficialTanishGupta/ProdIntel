import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import get_connection

CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "portfolio_history"
    / "portfolio_trend_history.csv"
)

COLUMNS = (
    "analysis_timestamp",
    "total_customers",
    "high_risk",
    "moderate_risk",
    "low_risk",
    "average_churn_probability_pct",
)


def parse_timestamp(value: str) -> datetime:
    timestamp = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp.astimezone(timezone.utc)


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        print("No historical records found. Nothing to migrate.")
        return

    migrated = 0
    skipped = 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for row in rows:
                timestamp = parse_timestamp(row["analysis_timestamp"])
                total = int(row["total_customers"])
                high = int(row["high_risk"])
                moderate = int(row["moderate_risk"])
                low = int(row["low_risk"])
                average = float(row["average_churn_probability_pct"])

                if min(total, high, moderate, low) < 0:
                    raise ValueError(f"Negative customer count in row: {row}")

                if high + moderate + low != total:
                    raise ValueError(f"Risk counts do not equal total customers: {row}")

                if not 0 <= average <= 100:
                    raise ValueError(f"Invalid average churn probability: {row}")

                values = (
                    timestamp,
                    total,
                    high,
                    moderate,
                    low,
                    average,
                )

                cursor.execute(
                    """
                    SELECT id
                    FROM portfolio_history
                    WHERE analysis_timestamp = %s
                      AND total_customers = %s
                      AND high_risk = %s
                      AND moderate_risk = %s
                      AND low_risk = %s
                      AND average_churn_probability_pct = %s
                    LIMIT 1
                    """,
                    values,
                )

                if cursor.fetchone():
                    skipped += 1
                    continue

                cursor.execute(
                    """
                    INSERT INTO portfolio_history (
                        analysis_timestamp,
                        total_customers,
                        high_risk,
                        moderate_risk,
                        low_risk,
                        average_churn_probability_pct
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    values,
                )

                migrated += 1

    print(f"CSV records found: {len(rows)}")
    print(f"New records migrated: {migrated}")
    print(f"Existing matching records skipped: {skipped}")
    print("Migration completed successfully.")


if __name__ == "__main__":
    main()
