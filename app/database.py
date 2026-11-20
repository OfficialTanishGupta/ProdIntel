
import os
from typing import Any, cast

import psycopg
from psycopg.rows import dict_row


def get_database_url() -> str:
    """Read and normalize the database URL."""
    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    return database_url


def get_connection() -> psycopg.Connection[Any]:
    """Create a PostgreSQL database connection."""
    return psycopg.connect(
        get_database_url(),
        row_factory=cast(Any, dict_row),
        connect_timeout=10,
    )


def initialize_database() -> None:
    """Create the portfolio history table if it does not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_history (
                id BIGSERIAL PRIMARY KEY,
                analysis_timestamp TIMESTAMPTZ NOT NULL,
                total_customers INTEGER NOT NULL,
                high_risk INTEGER NOT NULL,
                moderate_risk INTEGER NOT NULL,
                low_risk INTEGER NOT NULL,
                average_churn_probability_pct DOUBLE PRECISION NOT NULL
            )
        """)


def load_portfolio_history(limit: int = 500) -> list[dict[str, Any]]:
    """Load portfolio snapshots from PostgreSQL."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    analysis_timestamp,
                    total_customers,
                    high_risk,
                    moderate_risk,
                    low_risk,
                    average_churn_probability_pct
                FROM portfolio_history
                ORDER BY analysis_timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()


def save_portfolio_snapshot(snapshot: Any) -> dict[str, Any]:
    """Save a portfolio snapshot, avoiding exact duplicates."""
    values = (
        snapshot.analysis_timestamp,
        snapshot.total_customers,
        snapshot.high_risk,
        snapshot.moderate_risk,
        snapshot.low_risk,
        snapshot.average_churn_probability_pct,
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
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
                return {
                    "saved": False,
                    "message": "Portfolio snapshot already exists.",
                }

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

    return {
        "saved": True,
        "message": "Portfolio snapshot saved successfully.",
    }
