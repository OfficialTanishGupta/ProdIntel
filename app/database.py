import os
from typing import Any, cast

import psycopg
from psycopg.rows import dict_row


def get_database_url():
    """Read the database connection URL from the environment."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not configured.")

    # Render PostgreSQL URLs may use postgres:// or postgresql://.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def get_connection() -> psycopg.Connection[Any]:
    return psycopg.connect(
        get_database_url(),
        row_factory=cast(Any, dict_row),
        connect_timeout=10,
    )


def initialize_database():
    """Create the portfolio history table if it does not exist."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_history (
                    id BIGSERIAL PRIMARY KEY,
                    analysis_timestamp TIMESTAMPTZ NOT NULL,
                    total_customers INTEGER NOT NULL,
                    high_risk INTEGER NOT NULL,
                    moderate_risk INTEGER NOT NULL,
                    low_risk INTEGER NOT NULL,
                    average_churn_probability_pct DOUBLE PRECISION NOT NULL
                );
                """)
