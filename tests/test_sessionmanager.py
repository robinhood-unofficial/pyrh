"""Test session manager"""

from unittest import mock

import pytest
import requests_mock


@pytest.fixture
def sm():
    from pyrh.sessionmanager import SessionManager

    sample_user = {
        "username": "user@example.com",
        "password": "some password",
    }

    return SessionManager(**sample_user)


def test_repr(sm):
    assert str(sm) == "SessionManager<user@example.com>"


def test_bad_challenge_type():
    from pyrh.sessionmanager import SessionManager

    with pytest.raises(ValueError) as e:
        SessionManager(challenge_type="bad")

    assert "challenge_type must be" in str(e.value)


def test_no_user_pass_oauth2(monkeypatch):
    from pyrh.sessionmanager import SessionManager
    from pyrh.exceptions import AuthenticationError

    def ret_false():
        return False

    with pytest.raises(AuthenticationError) as e:
        sm = SessionManager()
        monkeypatch.setattr(sm, "from_json", ret_false)
        sm.login_oauth2()

    assert "Username and password must be" in str(e.value)


def test_sessionmanager_autoload_userpass(monkeypatch):
    from pyrh.sessionmanager import SessionManager

    data = {
        "username": "user@example.com",
        "password": "password",
    }

    def pass_func(*args, **kwargs):
        pass

    def mock_data(*args, **kwargs):
        return data

    def empty_dict(*args, **kwargs):
        return {}

    sm = SessionManager()
    monkeypatch.setattr(sm, "post", empty_dict)
    monkeypatch.setattr(sm, "_process_auth_body", pass_func)
    monkeypatch.setattr("json.load", mock_data)
    sm.login_oauth2()

    assert sm.username == data["username"]
    assert sm.password == data["password"]


def test_login_oauth2_err(monkeypatch, sm):
    from pyrh.exceptions import AuthenticationError

    def err_dict(*args, **kwargs):
        return {"error": "Some error"}

    def none_resp(*args, **kwargs):
        return None

    monkeypatch.setattr(sm, "post", err_dict)
    with pytest.raises(AuthenticationError) as e1:
        sm.login_oauth2()

    monkeypatch.setattr(sm, "post", none_resp)
    with pytest.raises(AuthenticationError) as e2:
        sm.login_oauth2()

    assert "Unknown login error" in str(e1.value)
    assert "Unknown login error" in str(e2.value)


def test_login_oauth2_detail(monkeypatch, sm):
    from pyrh.exceptions import AuthenticationError

    def invalid_jwt(*args, **kwargs):
        return {"detail": "Invalid JWT. Signature has expired"}

    monkeypatch.setattr(sm, "post", invalid_jwt)
    with pytest.raises(AuthenticationError) as e:
        sm.login_oauth2()

    assert "Invalid JWT" in str(e.value)


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_login_oauth2_challenge_valid(post_mock, monkeypatch, sm):
    monkeypatch.setattr("builtins.input", lambda: "123456")
    post_mock.side_effect = [
        {
            "detail": "Request blocked, challenge issued.",
            "challenge": {
                "id": "some_id",
                "user": "some_user",
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 3,
                "expires_at": "some_datetime",
            },
        },
        {
            "id": "some_id",
            "user": "some_user",
            "type": "email",
            "alternate_type": "sms",
            "status": "validated",
            "remaining_retries": 0,
            "remaining_attempts": 0,
            "expires_at": "some_datetime",
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
    sm.login_oauth2()

    assert post_mock.call_count == 3


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_login_oauth2_challenge_invalid(post_mock, monkeypatch, sm):
    from pyrh.exceptions import AuthenticationError

    monkeypatch.setattr("builtins.input", lambda: "123456")
    post_mock.side_effect = [
        {
            "detail": "Request blocked, challenge issued.",
            "challenge": {
                "id": "some_id",
                "user": "some_user",
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 3,
                "expires_at": "some_datetime",
            },
        },
        {
            "detail": "Challenge response is invalid.",
            "challenge": {
                "id": "some_id",
                "user": "some_user",
                "type": "email",
                "alternate_type": "sms",
                "status": "issued",
                "remaining_retries": 3,
                "remaining_attempts": 2,
                "expires_at": "some_datetime",
            },
        },
    ]
    with pytest.raises(AuthenticationError) as e:
        sm.login_oauth2()

    assert post_mock.call_count == 2
    assert "Challenge response was not accepted" in str(e.value)


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_login_oauth2_mfa_valid(post_mock, monkeypatch, sm):
    mfa_code = "123456"
    monkeypatch.setattr("builtins.input", lambda: mfa_code)
    post_mock.side_effect = [
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
    sm.login_oauth2()

    assert post_mock.call_count == 2


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_login_oauth2_mfa_invalid(post_mock, monkeypatch, sm):
    from pyrh.exceptions import AuthenticationError

    monkeypatch.setattr("builtins.input", lambda: "123456")
    post_mock.side_effect = [
        {"mfa_required": True, "mfa_type": "app"},
        {"detail": "Please enter a valid code."},
    ]
    with pytest.raises(AuthenticationError) as e:
        sm.login_oauth2()

    assert post_mock.call_count == 2
    assert "Mfa code was not accepted" in str(e.value)


def test_process_auth_body_invalid(sm):
    from pyrh.exceptions import AuthenticationError

    with pytest.raises(AuthenticationError) as e:
        sm._process_auth_body({})

    assert "missing required responses" in str(e.value)


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_refresh_oauth2_success(post_mock, sm):
    post_mock.return_value = {
        "access_token": "some_token",
        "expires_in": 86400,
        "token_type": "Bearer",
        "scope": "internal",
        "refresh_token": "some_refresh_token",
        "mfa_code": None,
        "backup_code": None,
    }

    sm.refresh_token = "some_token"
    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.refresh_oauth2()

    assert post_mock.call_count == 1


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_refresh_oauth2_failure(post_mock, sm):
    from pyrh.exceptions import AuthenticationError

    post_mock.return_value = {"error": "some_error"}

    with pytest.raises(AuthenticationError) as e1:
        sm.refresh_oauth2()

    assert "Cannot refresh login" in str(e1.value)

    sm.refresh_token = "some_token"
    sm.session.headers["Authorization"] = "Bearer some_token"

    with pytest.raises(AuthenticationError) as e2:
        sm.refresh_oauth2()

    assert "Failed to refresh" in str(e2.value)


@mock.patch("pyrh.sessionmanager.SessionManager.login_oauth2")
def test_login_init(login_mock, sm):
    sm.login()

    assert login_mock.call_count == 1


@mock.patch("pyrh.sessionmanager.SessionManager.refresh_oauth2")
def test_login_refresh_default(refresh_mock, monkeypatch, sm):
    # default expires_at is 1970
    monkeypatch.setattr(sm, "refresh_token", "some_token")
    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.login()

    assert refresh_mock.call_count == 1


@mock.patch("pyrh.sessionmanager.SessionManager.refresh_oauth2")
def test_login_refresh_force(refresh_mock, monkeypatch, sm):
    monkeypatch.setattr(sm, "refresh_token", "some_token")
    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.login(force_refresh=True)

    assert refresh_mock.call_count == 1


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_logout_success(post_mock, sm):
    post_mock.return_value = None
    sm.access_token = "some_token"
    sm.refresh_token = "some_refresh_token"
    sm.logout()
    assert sm.access_token is None
    assert sm.refresh_token is None
    assert post_mock.call_count == 1


@mock.patch("pyrh.sessionmanager.SessionManager.post")
def test_logout_failure(post_mock, sm):
    from pyrh.exceptions import AuthenticationError

    post_mock.return_value = {"error": "some_error"}
    sm.access_token = "some_token"
    sm.refresh_token = "some_refresh_token"
    with pytest.raises(AuthenticationError) as e:
        sm.logout()

    assert sm.access_token == "some_token"
    assert sm.refresh_token == "some_refresh_token"
    assert post_mock.call_count == 1
    assert "Could not log out" == str(e.value)


def test_jsonify(tmpdir, sm):
    from copy import deepcopy

    sm.access_token = "some_token"
    sm.refresh_token = "some_refresh_token"
    file = tmpdir.join("login.json")
    file.ensure(file=True)  # this will likely migrate to pathlib at some point
    assert not sm.from_json(file)

    data = deepcopy(sm.__dict__)
    data.pop("session")
    data.pop("certs")
    sm.to_json(file)

    sm.from_json(file)
    data2 = deepcopy(sm.__dict__)
    data2.pop("session")
    data2.pop("certs")

    assert data == data2


@mock.patch("pyrh.sessionmanager.datetime")
def test_authenticated(dt_mock, sm, monkeypatch):
    from datetime import datetime as dt, timedelta

    from pyrh.sessionmanager import EXPIRATION_TIME

    dt_mock.now.return_value = dt.strptime("2000", "%Y")
    assert not sm.authenticated

    expires_at_time = dt_mock.now() + timedelta(seconds=EXPIRATION_TIME)

    sm.session.headers["Authorization"] = "Bearer some_token"
    sm.expires_at = expires_at_time

    assert sm.authenticated


@mock.patch("pyrh.sessionmanager.SessionManager.login")
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


@mock.patch("pyrh.sessionmanager.SessionManager.login")
def test_post(mock_login, sm):
    import json

    from requests.exceptions import HTTPError

    adapter = requests_mock.Adapter()
    sm.session.mount("mock", adapter)
    mock_url = "mock://test.com"
    expected = [
        {"text": "", "status_code": 200, "headers": {"Content-Length": "0"}},
        {"text": '{"error": "login error"}', "status_code": 401},
        {"text": '{"test": "321"}', "status_code": 200},
        {"text": '{"error": "resource not found"}', "status_code": 404},
    ]
    adapter.register_uri("POST", mock_url, expected)

    resp1 = sm.post(mock_url)
    resp2 = sm.post(mock_url)

    with pytest.raises(HTTPError) as e:
        sm.post(mock_url)

    assert resp1 is None
    assert resp2 == json.loads(expected[2]["text"])
    assert mock_login.call_count == 1
    assert "404 Client Error" in str(e.value)
