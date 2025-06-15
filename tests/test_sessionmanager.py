import pytest
from freezegun import freeze_time

from pyrh.exceptions import AuthenticationError
from pyrh.models.sessionmanager import SessionManager

MOCK_URL = "https://api.robinhood.com/oauth2/token/"


@pytest.fixture
def sm_adap(requests_mock):
    sm = SessionManager(username="user", password="pass")
    return sm, requests_mock


def test_login_oauth2_errors(monkeypatch, sm_adap):
    sm, adapter = sm_adap
    adapter.register_uri(
        "POST", MOCK_URL, [{"json": {"error": "Some error"}, "status_code": 400}]
    )
    monkeypatch.setattr(
        "pyrh.models.sessionmanager.verify_workflow", lambda *a, **k: None
    )
    with pytest.raises(AuthenticationError) as e:
        sm._login_oauth2()
    assert "Failed to login, no verification workflow found" in str(e.value)


@freeze_time("2005-01-01")
def test_login_oauth2_workflow(monkeypatch, sm_adap):
    sm, adapter = sm_adap
    # Simulate workflow required
    adapter.register_uri(
        "POST",
        MOCK_URL,
        [
            {
                "json": {"verification_workflow": {"id": "workflow123"}},
                "status_code": 200,
            },
            {
                "json": {
                    "access_token": "token",
                    "expires_in": 1000,
                    "refresh_token": "refresh",
                    "token_type": "Bearer",
                    "scope": "internal",
                },
                "status_code": 200,
            },
        ],
    )
    # Patch workflow to do nothing (simulate success)
    monkeypatch.setattr(
        "pyrh.models.sessionmanager.verify_workflow", lambda **kwargs: None
    )
    sm._login_oauth2()
    assert sm.oauth.access_token == "token"


def test_login_oauth2_workflow_failure(monkeypatch, sm_adap):
    sm, adapter = sm_adap
    # Simulate workflow required, but no follow-up token
    adapter.register_uri(
        "POST",
        MOCK_URL,
        [
            {"json": {"verification_workflow": None}, "status_code": 200},
            {"json": {"error": "Some error"}, "status_code": 400},
        ],
    )
    # Patch workflow to do nothing (simulate success)
    monkeypatch.setattr(
        "pyrh.models.sessionmanager.verify_workflow", lambda **kwargs: None
    )
    with pytest.raises(AuthenticationError) as e:
        sm._login_oauth2()
    assert "Failed to login, no verification workflow found" in str(e.value)


def test_login_oauth2_no_workflow(monkeypatch, sm_adap):
    sm, adapter = sm_adap
    # Simulate no workflow, no token
    adapter.register_uri("POST", MOCK_URL, [{"json": {}, "status_code": 200}])
    with pytest.raises(AuthenticationError) as e:
        sm._login_oauth2()
    assert "Failed to login, no verification workflow found" in str(e.value)


def test_refresh_oauth2_success(sm_adap):
    sm, adapter = sm_adap
    sm.oauth = type("OAuth", (), {"refresh_token": "refresh", "is_valid": True})()
    adapter.register_uri(
        "POST",
        MOCK_URL,
        [
            {
                "json": {
                    "access_token": "token",
                    "expires_in": 1000,
                    "refresh_token": "refresh",
                    "token_type": "Bearer",
                    "scope": "internal",
                },
                "status_code": 200,
            }
        ],
    )
    sm._refresh_oauth2()
    assert sm.oauth.access_token == "token"


def test_refresh_oauth2_failure(sm_adap):
    sm, adapter = sm_adap
    sm.oauth = type("OAuth", (), {"refresh_token": "refresh", "is_valid": True})()
    adapter.register_uri(
        "POST", MOCK_URL, [{"json": {"error": "invalid_grant"}, "status_code": 400}]
    )
    with pytest.raises(AuthenticationError):
        sm._refresh_oauth2()
