
import pytest
from fastapi.testclient import TestClient

import app.database as database
import app.main as main

client = TestClient(main.app)

VALID_SNAPSHOT = {
    "analysis_timestamp": "2026-11-19T10:00:00+05:30",
    "total_customers": 100,
    "high_risk": 20,
    "moderate_risk": 30,
    "low_risk": 50,
    "average_churn_probability_pct": 35.5,
}


class FakeCursor:
    def __init__(self, fetchone_result=None, fetchall_result=None):
        self.fetchone_result = fetchone_result
        self.fetchall_result = fetchall_result or []
        self.rowcount = 1
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.executed = []

    def cursor(self):
        return self.fake_cursor

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


# --------------------------------------------------
# PostgreSQL storage tests
# --------------------------------------------------

def test_initialize_database(monkeypatch):
    cursor = FakeCursor()
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        database, "get_connection", lambda: connection
    )

    database.initialize_database()

    assert len(connection.executed) == 1
    assert "CREATE TABLE IF NOT EXISTS portfolio_history" in (
        connection.executed[0][0]
    )


def test_load_portfolio_history(monkeypatch):
    expected = [
        {
            "total_customers": 100,
            "high_risk": 20,
        }
    ]

    cursor = FakeCursor(fetchall_result=expected)
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        database, "get_connection", lambda: connection
    )

    result = database.load_portfolio_history(limit=10)

    assert result == expected
    assert "ORDER BY analysis_timestamp DESC" in cursor.executed[0][0]
    assert cursor.executed[0][1] == (10,)


def test_save_portfolio_snapshot_success(monkeypatch):
    cursor = FakeCursor(fetchone_result=None)
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        database, "get_connection", lambda: connection
    )

    snapshot = main.PortfolioSnapshot(**VALID_SNAPSHOT)
    result = database.save_portfolio_snapshot(snapshot)

    assert result["saved"] is True
    assert len(cursor.executed) == 2
    assert "INSERT INTO portfolio_history" in cursor.executed[1][0]


def test_save_portfolio_snapshot_prevents_duplicates(monkeypatch):
    cursor = FakeCursor(fetchone_result={"id": 1})
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        database, "get_connection", lambda: connection
    )

    snapshot = main.PortfolioSnapshot(**VALID_SNAPSHOT)
    result = database.save_portfolio_snapshot(snapshot)

    assert result["saved"] is False
    assert len(cursor.executed) == 1


# --------------------------------------------------
# Portfolio history API tests
# --------------------------------------------------

def test_get_portfolio_history(monkeypatch):
    expected_history = [
        {
            **VALID_SNAPSHOT,
            "analysis_timestamp": "2026-11-19T10:00:00+05:30",
        }
    ]

    monkeypatch.setattr(
        main,
        "load_portfolio_history",
        lambda limit: expected_history,
    )

    response = client.get("/portfolio-history?limit=100")

    assert response.status_code == 200
    assert response.json()["total_snapshots"] == 1
    assert response.json()["history"] == expected_history


def test_save_portfolio_history_api(monkeypatch):
    monkeypatch.setattr(
        main,
        "save_portfolio_snapshot",
        lambda snapshot: {
            "saved": True,
            "message": "Portfolio snapshot saved successfully.",
        },
    )

    response = client.post("/portfolio-history", json=VALID_SNAPSHOT)

    assert response.status_code == 200
    assert response.json()["saved"] is True


def test_save_portfolio_history_invalid_snapshot():
    invalid_snapshot = {
        **VALID_SNAPSHOT,
        "total_customers": -1,
    }

    response = client.post(
        "/portfolio-history",
        json=invalid_snapshot,
    )

    assert response.status_code == 422


def test_get_portfolio_history_storage_failure(monkeypatch):
    def raise_error(limit):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        main, "load_portfolio_history", raise_error
    )

    response = client.get("/portfolio-history")

    assert response.status_code == 503


def test_save_portfolio_history_storage_failure(monkeypatch):
    def raise_error(snapshot):
        raise RuntimeError("Database unavailable")

    monkeypatch.setattr(
        main, "save_portfolio_snapshot", raise_error
    )

    response = client.post(
        "/portfolio-history",
        json=VALID_SNAPSHOT,
    )

    assert response.status_code == 503
