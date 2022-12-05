"""Test session manager"""

from unittest import mock

import pytest
import requests_mock
from freezegun import freeze_time

MOCK_URL = "mock://test.com"


# TODO: refactor this to remove internal method testing and only test the public methods


@pytest.fixture
def sm():
    from pyrh.models import SessionManager

    sample_user = {
        "username": "user@example.com",
        "password": "some password",
    }

    return SessionManager(**sample_user)


@pytest.fixture
def sm_mfa():
    from pyrh.models import SessionManager

    sample_mfa_user = {
        "username": "user@example.com",
        "password": "some password",
        "mfa": "1234567890111213",
    }

    return SessionManager(**sample_mfa_user)


@pytest.fixture
def sm_adap(monkeypatch):
    from pyrh.models import SessionManager

    sample_user = {
        "username": "user@example.com",
        "password": "some password",
    }

    monkeypatch.setattr("pyrh.urls.OAUTH", MOCK_URL)
    monkeypatch.setattr("pyrh.urls.OAUTH_REVOKE", MOCK_URL)
    monkeypatch.setattr("pyrh.urls.build_challenge", lambda x: MOCK_URL)

    session_manager = SessionManager(**sample_user)
    adapter = requests_mock.Adapter()
    session_manager.session.mount("mock", adapter)

    return session_manager, adapter


def test_repr(sm):
    assert str(sm) == "SessionManager<user@example.com>"


def test_bad_challenge_type(sm):
    from pyrh.models import SessionManager

    sample_user = {
        "username": "user@example.com",
        "password": "some password",
    }

    with pytest.raises(ValueError) as e:
        SessionManager(challenge_type="bad", **sample_user)

    assert "challenge_type must be" in str(e.value)


def test_login_oauth2_errors(monkeypatch, sm_adap):
    from pyrh.exceptions import AuthenticationError

    sm, adapter = sm_adap

    # Note it is not possible to get invalid results to replace
    # oauth from the mfa approaches as those individual functions will error
    # out themselves

    adapter.register_uri(
        "POST", MOCK_URL, text='{"error": "Some error"}', status_code=400
    )
    with pytest.raises(AuthenticationError) as e:
        sm._login_oauth2()

    assert "Some error" in str(e.value)


@freeze_time("2005-01-01")
def test_login_oauth2_challenge_valid(monkeypatch, sm_adap):
    import uuid
    from datetime import datetime

    import pytz

    from pyrh.models.oauth import OAuthSchema

    monkeypatch.setattr("builtins.input", lambda: "123456")
    expiry = datetime.strptime("2010", "%Y").replace(tzinfo=pytz.UTC)
    responses = [
        {
            "detail": "Request blocked, challenge issued.",
            "challenge": {
                "id": str(uuid.uuid4()),
                "user": str(uuid.uuid4()),
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 3,
                "expires_at": expiry,
            },
        },
        {
            "id": str(uuid.uuid4()),
            "user": str(uuid.uuid4()),
            "type": "email",
            "alternate_type": "sms",
            "status": "validated",
            "remaining_retries": 0,
            "remaining_attempts": 0,
            "expires_at": expiry,
        },
        {
            "access_token": "some_token",
            "expires_in": 876880,
            "token_type": "Bearer",
            "scope": "internal",
            "refresh_token": "some_refresh_token",
            "mfa_code": None,
            "backup_code": None,
        },
    ]
    expected = [
        {"text": OAuthSchema().dumps(responses[0]), "status_code": 401},
        {"text": OAuthSchema().dumps(responses[1]), "status_code": 200},
        {"text": OAuthSchema().dumps(responses[2]), "status_code": 200},
    ]
    sm, adapter = sm_adap
    adapter.register_uri("POST", MOCK_URL, expected)
    sm._login_oauth2()

    assert sm.oauth.is_valid


@freeze_time("2005-01-01")
def test_login_oauth2_challenge_invalid(monkeypatch, sm_adap):
    import uuid
    from datetime import datetime

    import pytz

    from pyrh.exceptions import AuthenticationError
    from pyrh.models.oauth import OAuthSchema

    monkeypatch.setattr("builtins.input", lambda: "123456")
    expiry = datetime.strptime("2010", "%Y").replace(tzinfo=pytz.UTC)
    responses = [
        {
            "detail": "Request blocked, challenge issued.",
            "challenge": {
                "id": str(uuid.uuid4()),
                "user": str(uuid.uuid4()),
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 3,
                "expires_at": expiry,
            },
        },
        {
            "detail": "Challenge response is invalid.",
            "challenge": {
                "id": str(uuid.uuid4()),
                "user": str(uuid.uuid4()),
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 2,
                "expires_at": expiry,
            },
        },
        {
            "detail": "Challenge response is invalid.",
            "challenge": {
                "id": str(uuid.uuid4()),
                "user": str(uuid.uuid4()),
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 1,
                "expires_at": expiry,
            },
        },
        {
            "detail": "Some message.",
            "challenge": {
                "id": str(uuid.uuid4()),
                "user": str(uuid.uuid4()),
                "type": "email",
                "alternate_type": "sms",
                "status": "failed",
                "remaining_retries": 3,
                "remaining_attempts": 0,
                "expires_at": expiry,
            },
        },
    ]
    expected = [
        {"text": OAuthSchema().dumps(responses[0]), "status_code": 401},
        {"text": OAuthSchema().dumps(responses[1]), "status_code": 401},
        {"text": OAuthSchema().dumps(responses[2]), "status_code": 401},
        {"text": OAuthSchema().dumps(responses[3]), "status_code": 401},
    ]
    sm, adapter = sm_adap
    adapter.register_uri("POST", MOCK_URL, expected)
    with pytest.raises(AuthenticationError) as e:
        sm._login_oauth2()

    assert "Exceeded available" in str(e.value)


def test_login_oauth2_mfa_valid(monkeypatch, sm_adap):
    from pyrh.models.oauth import OAuthSchema

    mfa_code = "123456"
    monkeypatch.setattr("builtins.input", lambda: mfa_code)
    responses = [
        {"mfa_required": True, "mfa_type": "app"},
        {
            "access_token": "some_token",
            "expires_in": 876880,
            "token_type": "Bearer",
            "scope": "internal",
            "refresh_token": "some_refresh_token",
            "mfa_code": mfa_code,
            "backup_code": None,
        },
    ]
    expected = [
        {"text": OAuthSchema().dumps(responses[0]), "status_code": 200},
        {"text": OAuthSchema().dumps(responses[1]), "status_code": 200},
    ]
    sm, adapter = sm_adap
    adapter.register_uri("POST", MOCK_URL, expected)
    sm._login_oauth2()

    assert sm.oauth.is_valid


def test_login_oauth2_mfa_invalid(monkeypatch, sm_adap):
    from pyrh.exceptions import AuthenticationError
    from pyrh.models.oauth import OAuthSchema

    monkeypatch.setattr("builtins.input", lambda: "123456")
    responses = [
        {"mfa_required": True, "mfa_type": "app"},
        {"detail": "Please enter a valid code"},
        {"detail": "Please enter a valid code"},
        {"detail": "Please enter a valid code"},
    ]
    expected = [
        {"text": OAuthSchema().dumps(responses[0]), "status_code": 200},
        {"text": OAuthSchema().dumps(responses[1]), "status_code": 401},
        {"text": OAuthSchema().dumps(responses[2]), "status_code": 401},
        {"text": OAuthSchema().dumps(responses[3]), "status_code": 401},
    ]
    sm, adapter = sm_adap
    adapter.register_uri("POST", MOCK_URL, expected)
    with pytest.raises(AuthenticationError) as e:
        sm._login_oauth2()

    assert "Too many incorrect" in str(e.value)


def test_refresh_oauth2_success(sm_adap):
    from pyrh.models.oauth import OAuthSchema

    response = {
        "access_token": "some_token",
        "expires_in": 86400,
        "token_type": "Bearer",
        "scope": "internal",
        "refresh_token": "some_refresh_token",
        "mfa_code": None,
        "backup_code": None,
    }
    sm, adapter = sm_adap
    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    adapter.register_uri(
        "POST", MOCK_URL, text=OAuthSchema().dumps(response), status_code=200
    )

    sm.refresh_token = "some_token"
    sm.session.headers["Authorization"] = "Bearer some_token"
    sm._refresh_oauth2()

    assert sm.oauth.is_valid


def test_refresh_oauth2_failure(sm_adap):
    from pyrh.exceptions import AuthenticationError
    from pyrh.models.oauth import OAuthSchema

    response = {"error": "some_error"}
    sm, adapter = sm_adap
    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    adapter.register_uri(
        "POST", MOCK_URL, text=OAuthSchema().dumps(response), status_code=401
    )

    sm.refresh_token = "some_token"
    sm.session.headers["Authorization"] = "Bearer some_token"
    with pytest.raises(AuthenticationError) as e:
        sm._refresh_oauth2()

    assert "Failed to refresh" in str(e.value)


@mock.patch("pyrh.models.SessionManager._login_oauth2")
def test_login_init(login_mock, sm):
    sm.login()

    assert login_mock.call_count == 1


@mock.patch("pyrh.models.SessionManager._refresh_oauth2")
def test_login_refresh_default(refresh_mock, sm):
    # default expires_at is 1970
    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.login()

    assert refresh_mock.call_count == 1


@mock.patch("pyrh.models.SessionManager._refresh_oauth2")
def test_login_refresh_force(refresh_mock, sm):
    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.login(force_refresh=True)

    assert refresh_mock.call_count == 1


@mock.patch("pyrh.models.SessionManager.post")
def test_logout_success(post_mock, sm):
    post_mock.return_value = {}
    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    sm.logout()
    assert post_mock.call_count == 1


@mock.patch("pyrh.models.SessionManager.post")
def test_logout_failure(post_mock, sm):
    from requests.exceptions import HTTPError

    from pyrh.exceptions import AuthenticationError

    def raise_error(*args, **kwargs):
        raise HTTPError

    post_mock.side_effect = raise_error
    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    with pytest.raises(AuthenticationError) as e:
        sm.logout()

    assert sm.oauth.access_token == "some_token"
    assert sm.oauth.refresh_token == "some_refresh_token"
    assert post_mock.call_count == 1
    assert "Could not log out" == str(e.value)


def test_jsonify(tmpdir, sm):
    from pyrh import dump_session, load_session
    from pyrh.exceptions import InvalidCacheFile

    sm.oauth.access_token = "some_token"
    sm.oauth.refresh_token = "some_refresh_token"
    file = tmpdir.join("login.json")
    file.ensure(file=True)  # this will likely migrate to pathlib at some point

    with pytest.raises(InvalidCacheFile) as e:
        load_session(file)

    assert "The cache file at" in str(e.value)

    dump_session(sm, file)
    sm1 = load_session(file)

    # TODO: make this test a bit more robust
    assert sm.oauth == sm1.oauth


@freeze_time("2000-01-01")
def test_authenticated(sm, monkeypatch):
    from datetime import datetime as dt
    from datetime import timedelta

    import pytz

    from pyrh.models.sessionmanager import EXPIRATION_TIME

    assert not sm.authenticated

    expires_at_time = dt.now().replace(tzinfo=pytz.UTC) + timedelta(
        seconds=EXPIRATION_TIME
    )

    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.expires_at = expires_at_time

    assert sm.authenticated


@mock.patch("pyrh.models.SessionManager.login")
def test_get(mock_login, sm):
    import json

    from requests.exceptions import HTTPError

    adapter = requests_mock.Adapter()
    sm.session.mount("mock", adapter)
    mock_url = "mock://test.com"
    expected = [
        {"text": '{"test": "123"}', "status_code": 200},
        {"text": '{"error": "login error"}', "status_code": 401},
        {"text": '{"test": "321"}', "status_code": 200},
        {"text": '{"error": "resource not found"}', "status_code": 404},
    ]
    adapter.register_uri("GET", mock_url, expected)

    resp1 = sm.get(mock_url)
    resp2 = sm.get(mock_url)

    with pytest.raises(HTTPError) as e:
        sm.get(mock_url)

    assert resp1 == json.loads(expected[0]["text"])
    assert resp2 == json.loads(expected[2]["text"])
    assert mock_login.call_count == 1
    assert "404 Client Error" in str(e.value)


@mock.patch("pyrh.models.SessionManager.login")
def test_post(mock_login, sm):
    import json

    from requests.exceptions import HTTPError

    adapter = requests_mock.Adapter()
    sm.session.mount("mock", adapter)
    mock_url = "mock://test.com"
    expected = [
        {"text": '{"error": "login error"}', "status_code": 401},
        {"text": '{"test": "321"}', "status_code": 200},
        {"text": '{"error": "resource not found"}', "status_code": 404},
    ]
    adapter.register_uri("POST", mock_url, expected)

    resp1 = sm.post(mock_url)

    with pytest.raises(HTTPError) as e:
        sm.post(mock_url)

    assert resp1 == json.loads(expected[1]["text"])
    assert mock_login.call_count == 1
    assert "404 Client Error" in str(e.value)


@freeze_time("2020-01-01")
def test_token_expired(sm):
    from datetime import datetime

    import pytz

    # Assumes default token expired is set to 1970
    assert sm.token_expired

    sm.expires_at = datetime.strptime("2020-01-03", "%Y-%m-%d").replace(tzinfo=pytz.UTC)

    assert not sm.token_expired


def test_login_set(sm):
    assert sm.login_set

    sm.username = None
    sm.password = None

    assert not sm.login_set
