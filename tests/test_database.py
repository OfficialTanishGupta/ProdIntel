from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import app.database as database
import app.main as main

client = TestClient(main.app)


# --------------------------------------------------
# Database configuration tests
# --------------------------------------------------


def test_get_database_url_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        database.get_database_url()


def test_get_database_url_normalizes_postgres(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://user:password@localhost:5432/prodintel",
    )

    result = database.get_database_url()

    assert result.startswith("postgresql://")


def test_get_connection_uses_configured_database(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/prodintel",
    )

    mock_connect = MagicMock()
    monkeypatch.setattr(database.psycopg, "connect", mock_connect)

    database.get_connection()

    mock_connect.assert_called_once()

    args, kwargs = mock_connect.call_args

    assert args[0].startswith("postgresql://")
    assert kwargs["connect_timeout"] == 10
    assert "row_factory" in kwargs


def test_initialize_database_creates_table(monkeypatch):
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        database,
        "get_connection",
        lambda: connection,
    )

    database.initialize_database()

    executed_query = cursor.execute.call_args[0][0]

    assert "CREATE TABLE IF NOT EXISTS portfolio_history" in executed_query


# --------------------------------------------------
# Portfolio history API tests
# --------------------------------------------------


def create_mock_connection():
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    return connection, cursor


def test_get_portfolio_history(monkeypatch):
    connection, cursor = create_mock_connection()

    cursor.fetchall.return_value = [
        {
            "analysis_timestamp": "2026-10-30T10:00:00Z",
            "total_customers": 100,
            "high_risk": 20,
            "moderate_risk": 30,
            "low_risk": 50,
            "average_churn_probability_pct": 35.5,
        }
    ]

    monkeypatch.setattr(
        main,
        "get_connection",
        lambda: connection,
    )

    response = client.get("/portfolio-history")

    assert response.status_code == 200

    data = response.json()

    assert data["total_snapshots"] == 1
    assert len(data["history"]) == 1
    assert data["history"][0]["total_customers"] == 100


def test_get_portfolio_history_respects_limit(monkeypatch):
    connection, cursor = create_mock_connection()
    cursor.fetchall.return_value = []

    monkeypatch.setattr(
        main,
        "get_connection",
        lambda: connection,
    )

    response = client.get("/portfolio-history?limit=10")

    assert response.status_code == 200

    executed_query = cursor.execute.call_args[0][0]
    query_parameters = cursor.execute.call_args[0][1]

    assert "LIMIT %s" in executed_query
    assert query_parameters == (10,)


def test_save_portfolio_snapshot(monkeypatch):
    connection, cursor = create_mock_connection()

    # No existing duplicate snapshot.
    cursor.fetchone.return_value = None

    monkeypatch.setattr(
        main,
        "get_connection",
        lambda: connection,
    )

    snapshot = {
        "analysis_timestamp": "2026-10-30T10:00:00Z",
        "total_customers": 100,
        "high_risk": 20,
        "moderate_risk": 30,
        "low_risk": 50,
        "average_churn_probability_pct": 35.5,
    }

    response = client.post("/portfolio-history", json=snapshot)

    assert response.status_code == 200
    assert response.json()["saved"] is True

    executed_query = cursor.execute.call_args[0][0]

    assert "INSERT INTO portfolio_history" in executed_query


def test_save_duplicate_portfolio_snapshot(monkeypatch):
    connection, cursor = create_mock_connection()

    # Simulate an existing matching snapshot.
    cursor.fetchone.return_value = {"id": 1}

    monkeypatch.setattr(
        main,
        "get_connection",
        lambda: connection,
    )

    snapshot = {
        "analysis_timestamp": "2026-10-30T10:00:00Z",
        "total_customers": 100,
        "high_risk": 20,
        "moderate_risk": 30,
        "low_risk": 50,
        "average_churn_probability_pct": 35.5,
    }

    response = client.post("/portfolio-history", json=snapshot)

    assert response.status_code == 200
    assert response.json()["saved"] is False

    # Only the SELECT query should have executed.
    assert cursor.execute.call_count == 1


def test_save_invalid_portfolio_snapshot():
    invalid_snapshot = {
        "analysis_timestamp": "2026-10-30T10:00:00Z",
        "total_customers": -10,
        "high_risk": 20,
        "moderate_risk": 30,
        "low_risk": 50,
        "average_churn_probability_pct": 35.5,
    }

    response = client.post(
        "/portfolio-history",
        json=invalid_snapshot,
    )

    assert response.status_code == 422
