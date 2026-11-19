import pandas as pd
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


# --------------------------------------------------
# CSV storage tests
# --------------------------------------------------


def test_load_portfolio_history_missing_file(tmp_path, monkeypatch):
    history_file = tmp_path / "portfolio_history.csv"
    monkeypatch.setattr(database, "HISTORY_FILE", history_file)

    assert database.load_portfolio_history() == []


def test_save_portfolio_snapshot_creates_csv(tmp_path, monkeypatch):
    history_file = tmp_path / "portfolio_history.csv"
    monkeypatch.setattr(database, "HISTORY_FILE", history_file)

    snapshot = main.PortfolioSnapshot(**VALID_SNAPSHOT)

    result = database.save_portfolio_snapshot(snapshot)

    assert result["saved"] is True
    assert history_file.exists()

    history_df = pd.read_csv(history_file)

    assert len(history_df) == 1
    assert history_df.iloc[0]["total_customers"] == 100
    assert history_df.iloc[0]["high_risk"] == 20


def test_save_portfolio_snapshot_prevents_duplicates(tmp_path, monkeypatch):
    history_file = tmp_path / "portfolio_history.csv"
    monkeypatch.setattr(database, "HISTORY_FILE", history_file)

    snapshot = main.PortfolioSnapshot(**VALID_SNAPSHOT)

    first_result = database.save_portfolio_snapshot(snapshot)
    second_result = database.save_portfolio_snapshot(snapshot)

    assert first_result["saved"] is True
    assert second_result["saved"] is False

    history_df = pd.read_csv(history_file)
    assert len(history_df) == 1


def test_load_portfolio_history_respects_limit(tmp_path, monkeypatch):
    history_file = tmp_path / "portfolio_history.csv"
    monkeypatch.setattr(database, "HISTORY_FILE", history_file)

    records = [
        {
            **VALID_SNAPSHOT,
            "analysis_timestamp": f"2026-11-19T10:{minute:02d}:00+05:30",
        }
        for minute in range(3)
    ]

    pd.DataFrame(records).to_csv(history_file, index=False)

    history = database.load_portfolio_history(limit=2)

    assert len(history) == 2


# --------------------------------------------------
# Portfolio history API tests
# --------------------------------------------------


def test_get_portfolio_history(monkeypatch):
    expected_history = [
        {
            "analysis_timestamp": "2026-11-19T10:00:00+05:30",
            "total_customers": 100,
            "high_risk": 20,
            "moderate_risk": 30,
            "low_risk": 50,
            "average_churn_probability_pct": 35.5,
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

    response = client.post(
        "/portfolio-history",
        json=VALID_SNAPSHOT,
    )

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
        raise OSError("CSV storage unavailable")

    monkeypatch.setattr(
        main,
        "load_portfolio_history",
        raise_error,
    )

    response = client.get("/portfolio-history")

    assert response.status_code == 503


def test_save_portfolio_history_storage_failure(monkeypatch):
    def raise_error(snapshot):
        raise OSError("CSV storage unavailable")

    monkeypatch.setattr(
        main,
        "save_portfolio_snapshot",
        raise_error,
    )

    response = client.post(
        "/portfolio-history",
        json=VALID_SNAPSHOT,
    )

    assert response.status_code == 503
