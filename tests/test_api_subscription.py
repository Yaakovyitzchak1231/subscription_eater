
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime

from backend.app import app, get_db
from backend.models import Subscription

client = TestClient(app)

# Global mock for the DB session
mock_db_session = MagicMock()

def override_get_db():
    try:
        yield mock_db_session
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def reset_mock():
    mock_db_session.reset_mock()
    # Reset return values
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None

def _create_mock_subscription():
    mock_sub = MagicMock(spec=Subscription)
    mock_sub.id = 1
    mock_sub.service_name = "Test Service"
    mock_sub.cost = 10.0
    mock_sub.status = "active"
    mock_sub.currency = "USD"
    mock_sub.billing_cycle = "monthly"
    mock_sub.category = "Software"
    mock_sub.renewal_date = datetime(2023, 1, 1)
    mock_sub.confidence_score = 0.9
    mock_sub.is_confirmed = True

    mock_sub.account = MagicMock(email="test@example.com")
    mock_sub.source_email = None

    return mock_sub

def test_update_subscription_success():
    # Setup mock
    mock_sub = _create_mock_subscription()
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = mock_sub

    payload = {
        "cost": 15.0,
        "status": "cancelled",
        "currency": "usd"
    }

    response = client.put("/api/subscriptions/1", json=payload)

    assert response.status_code == 200, response.text
    assert mock_sub.cost == 15.0
    assert mock_sub.status == "cancelled"
    assert mock_sub.currency == "USD"

def test_update_subscription_not_found():
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = None

    response = client.put("/api/subscriptions/999", json={"cost": 10.0})
    assert response.status_code == 404

def test_update_subscription_invalid_cost():
    mock_sub = _create_mock_subscription()
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = mock_sub

    response = client.put("/api/subscriptions/1", json={"cost": -5.0})
    assert response.status_code == 400
    assert "negative" in response.json()["detail"].lower()

def test_update_subscription_invalid_currency():
    mock_sub = _create_mock_subscription()
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = mock_sub

    response = client.put("/api/subscriptions/1", json={"currency": "US Dollar"})
    assert response.status_code == 400
    assert "3-letter" in response.json()["detail"]

def test_update_subscription_invalid_status():
    mock_sub = _create_mock_subscription()
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = mock_sub

    response = client.put("/api/subscriptions/1", json={"status": "weird"})
    assert response.status_code == 400

def test_update_subscription_invalid_date():
    mock_sub = _create_mock_subscription()
    mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = mock_sub

    response = client.put("/api/subscriptions/1", json={"renewal_date": "not-a-date"})
    assert response.status_code == 400
    assert "ISO 8601" in response.json()["detail"]
